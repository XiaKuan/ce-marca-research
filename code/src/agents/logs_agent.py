"""
日志智能体

分析日志模式（错误、警告、异常堆栈）
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentRole, Hypothesis


class LogsAgent(BaseAgent):
    """日志智能体"""
    
    def __init__(self):
        super().__init__(AgentRole.LOGS)
        self.error_keywords = [
            "error", "exception", "failed", "failure", "crash",
            "timeout", "connection refused", "out of memory"
        ]
        self.warning_keywords = [
            "warn", "warning", "slow", "retry", "degraded"
        ]
    
    def analyze(
        self,
        data: Dict[str, Any],
        causal_graph,
        strategy: Dict[str, Any]
    ) -> Hypothesis:
        """分析日志数据并生成假设"""
        services_logs = data.get("services", {})
        
        # Step 1: 分析每个服务的日志
        service_scores = []
        for service_id, logs in services_logs.items():
            score, anomalies = self._analyze_service_logs(service_id, logs)
            if score > 0:
                service_scores.append({
                    "service": service_id,
                    "score": score,
                    "anomalies": anomalies
                })
        
        if not service_scores:
            return self._create_no_anomaly_hypothesis()
        
        # Step 2: 按分数排序
        service_scores.sort(key=lambda x: x["score"], reverse=True)
        top_candidate = service_scores[0]
        
        # Step 3: 生成假设
        confidence = min(0.6 + top_candidate["score"] * 0.4, 1.0)
        
        evidence = [
            {"type": "log_pattern", **anomaly}
            for anomaly in top_candidate["anomalies"][:5]
        ]
        
        causal_path = []
        if causal_graph:
            causal_path = causal_graph.extract_causal_path(
                top_candidate["service"],
                top_candidate["service"]
            )
        
        return Hypothesis(
            service=top_candidate["service"],
            confidence=confidence,
            evidence=evidence,
            source_agent=AgentRole.LOGS,
            reasoning=self._generate_reasoning(top_candidate),
            causal_path=causal_path
        )
    
    def _analyze_service_logs(
        self,
        service_id: str,
        logs: List[Dict[str, Any]]
    ) -> tuple:
        """分析单个服务的日志"""
        anomalies = []
        score = 0.0
        
        error_count = 0
        warning_count = 0
        
        for log in logs:
            message = log.get("message", "").lower()
            level = log.get("level", "info").lower()
            
            # 统计错误和警告
            if level in ["error", "fatal", "critical"]:
                error_count += 1
                anomalies.append({
                    "level": level,
                    "message": log.get("message", "")[:200],
                    "timestamp": log.get("timestamp", "")
                })
            elif level == "warn":
                warning_count += 1
            
            # 检查关键词
            for keyword in self.error_keywords:
                if keyword in message:
                    score += 2.0
                    break
            
            for keyword in self.warning_keywords:
                if keyword in message:
                    score += 0.5
                    break
        
        # 基于错误数量计算分数
        score += error_count * 1.5
        score += warning_count * 0.2
        
        # 归一化
        score = min(score / 10.0, 1.0)
        
        return score, anomalies
    
    def _generate_reasoning(self, candidate: Dict) -> str:
        """生成推理解释"""
        error_count = len([a for a in candidate["anomalies"] 
                          if a.get("level") in ["error", "fatal", "critical"]])
        
        return (
            f"服务 {candidate['service']} 检测到 {error_count} 个错误日志，"
            f"异常模式分数：{candidate['score']:.2f}"
        )
    
    def _create_no_anomaly_hypothesis(self) -> Hypothesis:
        """创建无异常假设"""
        return Hypothesis(
            service="unknown",
            confidence=0.0,
            evidence=[],
            source_agent=AgentRole.LOGS,
            reasoning="未检测到日志异常",
            causal_path=[]
        )
