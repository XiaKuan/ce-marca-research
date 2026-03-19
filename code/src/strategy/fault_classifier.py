"""
故障模式分类器
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class FaultPattern(Enum):
    """故障模式"""
    PERFORMANCE_DEGRADATION = "performance_degradation"  # 性能下降
    ERROR_RATE_SPIKE = "error_rate_spike"  # 错误率上升
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # 资源耗尽
    CASCADE_FAILURE = "cascade_failure"  # 级联故障
    INTERMITTENT_FAULT = "intermittent_fault"  # 间歇性故障


@dataclass
class AnomalySignature:
    """故障特征向量"""
    latency_p99_delta: float  # 延迟变化倍数
    error_rate_delta: float  # 错误率变化倍数
    cpu_delta: float  # CPU 变化
    memory_delta: float  # 内存变化
    throughput_delta: float  # 吞吐量变化
    num_anomalous_services: int  # 异常服务数量


class FaultClassifier:
    """故障模式分类器"""
    
    def __init__(self):
        # 规则阈值
        self.thresholds = {
            "latency_spike": 2.0,  # 延迟翻倍
            "error_spike": 0.5,  # 错误率增加 50%
            "cpu_high": 0.3,  # CPU 增加 30%
            "memory_high": 0.3,  # 内存增加 30%
            "throughput_drop": 0.3,  # 吞吐量下降 30%
            "cascade_threshold": 3  # 级联故障：3 个以上服务异常
        }
    
    def classify(self, signature: AnomalySignature) -> FaultPattern:
        """
        根据故障特征分类故障模式
        
        使用规则分类（简单、可解释）
        后续可升级为 ML 分类器
        """
        scores = {pattern: 0.0 for pattern in FaultPattern}
        
        # 规则 1: 错误率突增 → 错误率上升
        if signature.error_rate_delta > self.thresholds["error_spike"]:
            scores[FaultPattern.ERROR_RATE_SPIKE] += 0.8
        
        # 规则 2: 延迟增加 → 性能下降
        if signature.latency_p99_delta > self.thresholds["latency_spike"]:
            scores[FaultPattern.PERFORMANCE_DEGRADATION] += 0.7
        
        # 规则 3: 资源使用率增加 → 资源耗尽
        if signature.cpu_delta > self.thresholds["cpu_high"]:
            scores[FaultPattern.RESOURCE_EXHAUSTION] += 0.6
        if signature.memory_delta > self.thresholds["memory_high"]:
            scores[FaultPattern.RESOURCE_EXHAUSTION] += 0.6
        
        # 规则 4: 多服务异常 → 级联故障
        if signature.num_anomalous_services > self.thresholds["cascade_threshold"]:
            scores[FaultPattern.CASCADE_FAILURE] += 0.9
        
        # 规则 5: 吞吐量下降 → 性能下降或资源耗尽
        if signature.throughput_delta < -self.thresholds["throughput_drop"]:
            scores[FaultPattern.PERFORMANCE_DEGRADATION] += 0.4
        
        # 选择最高分模式
        best_pattern = max(scores, key=scores.get)
        
        # 如果没有明显模式，默认性能下降
        if scores[best_pattern] < 0.5:
            return FaultPattern.PERFORMANCE_DEGRADATION
        
        return best_pattern
    
    def classify_from_metrics(
        self,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float],
        num_anomalous_services: int = 1
    ) -> FaultPattern:
        """
        从指标数据直接分类
        
        Args:
            current_metrics: 当前指标
            baseline_metrics: 基线指标
            num_anomalous_services: 异常服务数量
        """
        def safe_delta(current, baseline):
            if baseline == 0:
                return 0.0
            return (current - baseline) / baseline
        
        signature = AnomalySignature(
            latency_p99_delta=safe_delta(
                current_metrics.get("latency_p99", 0),
                baseline_metrics.get("latency_p99", 0)
            ),
            error_rate_delta=safe_delta(
                current_metrics.get("error_rate", 0),
                baseline_metrics.get("error_rate", 0)
            ),
            cpu_delta=safe_delta(
                current_metrics.get("cpu_usage", 0),
                baseline_metrics.get("cpu_usage", 0)
            ),
            memory_delta=safe_delta(
                current_metrics.get("memory_usage", 0),
                baseline_metrics.get("memory_usage", 0)
            ),
            throughput_delta=safe_delta(
                current_metrics.get("throughput", 0),
                baseline_metrics.get("throughput", 0)
            ),
            num_anomalous_services=num_anomalous_services
        )
        
        return self.classify(signature)
