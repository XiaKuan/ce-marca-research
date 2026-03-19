"""
监控智能体

分析指标异常（CPU、内存、延迟、吞吐量等）
"""

from typing import Dict, List, Any, Optional
import numpy as np
from .base_agent import BaseAgent, AgentRole, Hypothesis


class MetricsAgent(BaseAgent):
    """监控智能体"""
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        super().__init__(AgentRole.METRICS)
        # 默认阈值
        self.thresholds = thresholds or {
            "cpu_usage": 80.0,  # %
            "memory_usage": 85.0,  # %
            "latency_p99": 500.0,  # ms
            "error_rate": 5.0,  # %
            "throughput_drop": 30.0  # % 下降
        }
    
    def analyze(
        self,
        data: Dict[str, Any],
        causal_graph,
        strategy: Dict[str, Any]
    ) -> Hypothesis:
        """
        分析指标数据并生成假设
        
        Args:
            data: 指标数据
                {
                    "services": {
                        "service_id": {
                            "cpu_usage": [...],
                            "memory_usage": [...],
                            "latency_p99": [...],
                            "error_rate": [...],
                            "throughput": [...]
                        }
                    }
                }
            causal_graph: 因果图
            strategy: 推理策略配置
        
        Returns:
            Hypothesis: 根因假设
        """
        services_data = data.get("services", {})
        
        # Step 1: 检测每个服务的异常
        anomalous_services = []
        for service_id, metrics in services_data.items():
            anomalies = self._detect_anomalies(metrics)
            if anomalies:
                anomalous_services.append({
                    "service": service_id,
                    "anomalies": anomalies,
                    "severity": self._calculate_severity(anomalies)
                })
        
        if not anomalous_services:
            return self._create_no_anomaly_hypothesis()
        
        # Step 2: 按严重程度排序
        anomalous_services.sort(key=lambda x: x["severity"], reverse=True)
        
        # Step 3: 生成假设（最严重的服务为根因候选）
        top_candidate = anomalous_services[0]
        
        # Step 4: 使用因果图调整置信度
        confidence = self._adjust_confidence_with_causal_graph(
            top_candidate["service"],
            causal_graph,
            base_confidence=0.7 + top_candidate["severity"] * 0.3
        )
        
        # Step 5: 构建证据
        evidence = []
        for anomaly in top_candidate["anomalies"]:
            evidence.append({
                "type": "metric_anomaly",
                "metric": anomaly["metric"],
                "value": anomaly["value"],
                "threshold": anomaly["threshold"],
                "delta": anomaly["delta"]
            })
        
        # Step 6: 获取因果路径
        causal_path = []
        if causal_graph:
            causal_path = causal_graph.extract_causal_path(
                top_candidate["service"],
                top_candidate["service"]
            )
        
        hypothesis = Hypothesis(
            service=top_candidate["service"],
            confidence=confidence,
            evidence=evidence,
            source_agent=AgentRole.METRICS,
            reasoning=self._generate_reasoning(top_candidate),
            causal_path=causal_path
        )
        
        return hypothesis
    
    def _detect_anomalies(self, metrics: Dict[str, List[float]]) -> List[Dict]:
        """检测指标异常"""
        anomalies = []
        
        for metric_name, values in metrics.items():
            if not values:
                continue
            
            # 获取阈值
            threshold = self.thresholds.get(metric_name)
            if threshold is None:
                continue
            
            # 计算当前值（最近一段时间的平均）
            recent_values = values[-10:] if len(values) >= 10 else values
            current_value = np.mean(recent_values)
            
            # 计算基线（较早一段时间的平均）
            if len(values) >= 20:
                baseline_values = values[-30:-10]
                baseline = np.mean(baseline_values)
            else:
                baseline = threshold * 0.5  # 假设基线为阈值的一半
            
            # 计算变化
            delta = current_value - baseline
            delta_percent = (delta / baseline * 100) if baseline > 0 else 0
            
            # 判断是否异常
            is_anomaly = False
            if metric_name in ["cpu_usage", "memory_usage", "latency_p99", "error_rate"]:
                is_anomaly = current_value > threshold or delta_percent > 50
            elif metric_name == "throughput":
                is_anomaly = delta_percent < -self.thresholds["throughput_drop"]
            
            if is_anomaly:
                anomalies.append({
                    "metric": metric_name,
                    "value": current_value,
                    "threshold": threshold,
                    "baseline": baseline,
                    "delta": delta,
                    "delta_percent": delta_percent
                })
        
        return anomalies
    
    def _calculate_severity(self, anomalies: List[Dict]) -> float:
        """计算异常严重程度（0-1）"""
        if not anomalies:
            return 0.0
        
        # 基于异常数量和严重程度计算
        severity_scores = []
        for anomaly in anomalies:
            # 计算超出阈值的程度
            if anomaly["threshold"] > 0:
                exceed_ratio = anomaly["value"] / anomaly["threshold"]
            else:
                exceed_ratio = 1.0
            
            # 归一化到 0-1
            score = min(exceed_ratio - 1, 1.0)
            severity_scores.append(score)
        
        # 平均严重程度 + 数量惩罚
        avg_severity = np.mean(severity_scores)
        count_bonus = min(len(anomalies) * 0.1, 0.3)
        
        return min(avg_severity + count_bonus, 1.0)
    
    def _adjust_confidence_with_causal_graph(
        self,
        service: str,
        causal_graph,
        base_confidence: float
    ) -> float:
        """使用因果图调整置信度"""
        if causal_graph is None or causal_graph.graph is None:
            return base_confidence
        
        # 检查该服务是否有显著的入边
        incoming_edges = list(causal_graph.graph.in_edges(service, data=True))
        
        if not incoming_edges:
            # 没有因果入边，降低置信度（可能是自身问题）
            return base_confidence * 0.9
        
        # 有因果入边，提高置信度（可能是上游影响）
        max_strength = max([data['strength'] for _, _, data in incoming_edges])
        
        # 强度越大，置信度提升越多
        boost = min(max_strength / 20.0, 0.15)
        
        return min(base_confidence + boost, 1.0)
    
    def _generate_reasoning(self, candidate: Dict) -> str:
        """生成推理解释"""
        anomaly_strs = []
        for anomaly in candidate["anomalies"]:
            anomaly_strs.append(
                f"{anomaly['metric']}: {anomaly['value']:.2f} "
                f"(阈值：{anomaly['threshold']}, "
                f"变化：{anomaly['delta_percent']:+.1f}%)"
            )
        
        return (
            f"服务 {candidate['service']} 检测到 {len(candidate['anomalies'])} 项异常：\n"
            + "\n".join([f"  - {s}" for s in anomaly_strs])
        )
    
    def _create_no_anomaly_hypothesis(self) -> Hypothesis:
        """创建无异常假设"""
        return Hypothesis(
            service="unknown",
            confidence=0.0,
            evidence=[],
            source_agent=AgentRole.METRICS,
            reasoning="未检测到指标异常",
            causal_path=[]
        )
