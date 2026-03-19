"""
追踪智能体

分析调用链延迟和瓶颈
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentRole, Hypothesis


class TracesAgent(BaseAgent):
    """追踪智能体"""
    
    def __init__(self):
        super().__init__(AgentRole.TRACES)
        self.latency_threshold_ms = 500
    
    def analyze(
        self,
        data: Dict[str, Any],
        causal_graph,
        strategy: Dict[str, Any]
    ) -> Hypothesis:
        """分析追踪数据并生成假设"""
        traces = data.get("traces", [])
        
        if not traces:
            return self._create_no_anomaly_hypothesis()
        
        # Step 1: 分析调用链
        service_latencies = self._extract_service_latencies(traces)
        
        # Step 2: 识别延迟瓶颈
        bottlenecks = []
        for service_id, latency_stats in service_latencies.items():
            if latency_stats["p99"] > self.latency_threshold_ms:
                bottlenecks.append({
                    "service": service_id,
                    "latency_p50": latency_stats["p50"],
                    "latency_p99": latency_stats["p99"],
                    "span_count": latency_stats["count"],
                    "self_time_ratio": latency_stats.get("self_time_ratio", 0)
                })
        
        if not bottlenecks:
            return self._create_no_anomaly_hypothesis()
        
        # Step 3: 按延迟排序
        bottlenecks.sort(key=lambda x: x["latency_p99"], reverse=True)
        top_bottleneck = bottlenecks[0]
        
        # Step 4: 生成假设
        confidence = min(0.65 + (top_bottleneck["latency_p99"] / 2000) * 0.35, 1.0)
        
        evidence = [{
            "type": "latency_bottleneck",
            "service": top_bottleneck["service"],
            "latency_p50": top_bottleneck["latency_p50"],
            "latency_p99": top_bottleneck["latency_p99"],
            "span_count": top_bottleneck["span_count"]
        }]
        
        causal_path = []
        if causal_graph:
            causal_path = causal_graph.extract_causal_path(
                top_bottleneck["service"],
                top_bottleneck["service"]
            )
        
        return Hypothesis(
            service=top_bottleneck["service"],
            confidence=confidence,
            evidence=evidence,
            source_agent=AgentRole.TRACES,
            reasoning=self._generate_reasoning(top_bottleneck),
            causal_path=causal_path
        )
    
    def _extract_service_latencies(
        self,
        traces: List[Dict[str, Any]]
    ) -> Dict[str, Dict]:
        """从调用链提取服务延迟统计"""
        service_latencies = {}
        
        for trace in traces:
            spans = trace.get("spans", [])
            for span in spans:
                service_id = span.get("service", "unknown")
                duration = span.get("duration_ms", 0)
                
                if service_id not in service_latencies:
                    service_latencies[service_id] = {
                        "latencies": [],
                        "count": 0
                    }
                
                service_latencies[service_id]["latencies"].append(duration)
                service_latencies[service_id]["count"] += 1
        
        # 计算统计值
        result = {}
        for service_id, data in service_latencies.items():
            latencies = sorted(data["latencies"])
            n = len(latencies)
            
            result[service_id] = {
                "p50": latencies[n // 2] if n > 0 else 0,
                "p99": latencies[int(n * 0.99)] if n > 0 else 0,
                "count": data["count"],
                "self_time_ratio": 0.5  # TODO: 计算自身时间占比
            }
        
        return result
    
    def _generate_reasoning(self, bottleneck: Dict) -> str:
        """生成推理解释"""
        return (
            f"服务 {bottleneck['service']} 是延迟瓶颈：\n"
            f"  P50 延迟：{bottleneck['latency_p50']:.2f}ms\n"
            f"  P99 延迟：{bottleneck['latency_p99']:.2f}ms\n"
            f"  调用次数：{bottleneck['span_count']}"
        )
    
    def _create_no_anomaly_hypothesis(self) -> Hypothesis:
        """创建无异常假设"""
        return Hypothesis(
            service="unknown",
            confidence=0.0,
            evidence=[],
            source_agent=AgentRole.TRACES,
            reasoning="未检测到调用链异常",
            causal_path=[]
        )
