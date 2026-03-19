"""
推理策略选择器
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from .fault_classifier import FaultPattern


@dataclass
class ReasoningStrategy:
    """推理策略配置"""
    priority: List[str]  # 智能体优先级 ["metrics", "logs", "traces"]
    time_window: str  # 时间窗口 "30min", "1h"
    causal_depth: int  # 因果图搜索深度
    max_rounds: int = 3  # 最大推理轮数
    confidence_threshold: float = 0.85  # 置信度阈值


class ReasoningStrategySelector:
    """推理策略选择器"""
    
    def __init__(self):
        # 默认策略
        self.default_strategy = ReasoningStrategy(
            priority=["metrics", "logs", "traces"],
            time_window="30min",
            causal_depth=2,
            max_rounds=3,
            confidence_threshold=0.85
        )
        
        # 故障模式到策略的映射
        self.pattern_strategies = {
            FaultPattern.PERFORMANCE_DEGRADATION: ReasoningStrategy(
                priority=["traces", "metrics", "logs"],
                time_window="30min",
                causal_depth=3,
                max_rounds=3,
                confidence_threshold=0.85
            ),
            FaultPattern.ERROR_RATE_SPIKE: ReasoningStrategy(
                priority=["logs", "traces", "metrics"],
                time_window="15min",
                causal_depth=2,
                max_rounds=3,
                confidence_threshold=0.85
            ),
            FaultPattern.RESOURCE_EXHAUSTION: ReasoningStrategy(
                priority=["metrics", "logs", "traces"],
                time_window="1h",
                causal_depth=2,
                max_rounds=3,
                confidence_threshold=0.80
            ),
            FaultPattern.CASCADE_FAILURE: ReasoningStrategy(
                priority=["metrics", "traces", "logs"],
                time_window="1h",
                causal_depth=5,
                max_rounds=3,
                confidence_threshold=0.75
            ),
            FaultPattern.INTERMITTENT_FAULT: ReasoningStrategy(
                priority=["metrics", "logs", "traces"],
                time_window="2h",
                causal_depth=3,
                max_rounds=5,  # 更多轮次
                confidence_threshold=0.70
            )
        }
    
    def select(
        self,
        fault_pattern: FaultPattern,
        custom_overrides: Dict[str, Any] = None
    ) -> ReasoningStrategy:
        """
        根据故障模式选择策略
        
        Args:
            fault_pattern: 故障模式
            custom_overrides: 自定义覆盖配置
        
        Returns:
            ReasoningStrategy: 推理策略
        """
        # 获取对应策略
        strategy = self.pattern_strategies.get(
            fault_pattern,
            self.default_strategy
        )
        
        # 应用自定义覆盖
        if custom_overrides:
            strategy = ReasoningStrategy(
                priority=custom_overrides.get("priority", strategy.priority),
                time_window=custom_overrides.get("time_window", strategy.time_window),
                causal_depth=custom_overrides.get("causal_depth", strategy.causal_depth),
                max_rounds=custom_overrides.get("max_rounds", strategy.max_rounds),
                confidence_threshold=custom_overrides.get(
                    "confidence_threshold",
                    strategy.confidence_threshold
                )
            )
        
        return strategy
    
    def to_dict(self, strategy: ReasoningStrategy) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "priority": strategy.priority,
            "time_window": strategy.time_window,
            "causal_depth": strategy.causal_depth,
            "max_rounds": strategy.max_rounds,
            "confidence_threshold": strategy.confidence_threshold
        }
