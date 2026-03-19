"""
CAHP 协议：Causal-Enhanced Agent Handshake Protocol

因果增强智能体握手协议
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .base_agent import AgentRole, Hypothesis, AgentMessage, MessageType
from .coordinator import CoordinatorAgent
from .metrics_agent import MetricsAgent
from .logs_agent import LogsAgent
from .traces_agent import TracesAgent


@dataclass
class CAHPSession:
    """CAHP 会话"""
    session_id: str
    round_number: int = 0
    max_rounds: int = 3
    hypotheses: List[Hypothesis] = None
    converged: bool = False
    
    def __post_init__(self):
        if self.hypotheses is None:
            self.hypotheses = []


class CAHPProtocol:
    """
    CAHP 协议实现
    
    3 轮推理流程：
    Round 1: 并行数据收集
    Round 2: 因果约束推理
    Round 3: 假设仲裁与验证
    """
    
    def __init__(
        self,
        coordinator: CoordinatorAgent,
        metrics_agent: MetricsAgent,
        logs_agent: LogsAgent,
        traces_agent: TracesAgent
    ):
        self.coordinator = coordinator
        self.metrics_agent = metrics_agent
        self.logs_agent = logs_agent
        self.traces_agent = traces_agent
        
        self.sessions: Dict[str, CAHPSession] = {}
    
    def start_session(
        self,
        session_id: str,
        max_rounds: int = 3
    ) -> CAHPSession:
        """开始新会话"""
        session = CAHPSession(
            session_id=session_id,
            max_rounds=max_rounds
        )
        self.sessions[session_id] = session
        return session
    
    def run_round(
        self,
        session_id: str,
        data: Dict[str, Any],
        causal_graph,
        strategy: Dict[str, Any]
    ) -> Dict[str, Hypothesis]:
        """
        运行一轮推理
        
        Args:
            session_id: 会话 ID
            data: 数据（指标、日志、追踪）
            causal_graph: 因果图
            strategy: 推理策略
        
        Returns:
            各智能体的假设
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.round_number += 1
        
        # Round 1 & 2: 并行数据收集与推理
        metrics_hypothesis = self.metrics_agent.analyze(data, causal_graph, strategy)
        logs_hypothesis = self.logs_agent.analyze(data, causal_graph, strategy)
        traces_hypothesis = self.traces_agent.analyze(data, causal_graph, strategy)
        
        # 收集假设
        hypotheses = [metrics_hypothesis, logs_hypothesis, traces_hypothesis]
        session.hypotheses.extend(hypotheses)
        
        # Round 3: 检查收敛
        if session.round_number >= session.max_rounds:
            # 仲裁假设
            self.coordinator.collect_hypotheses(
                metrics_hypothesis,
                logs_hypothesis,
                traces_hypothesis
            )
            
            final_hypothesis = self.coordinator.arbitrate_hypotheses(causal_graph)
            
            # 检查是否收敛
            if final_hypothesis.confidence >= strategy.get("confidence_threshold", 0.85):
                session.converged = True
        
        return {
            "metrics": metrics_hypothesis,
            "logs": logs_hypothesis,
            "traces": traces_hypothesis
        }
    
    def get_final_report(
        self,
        session_id: str,
        fault_pattern: str,
        total_time_sec: float,
        total_tokens_used: int
    ) -> Optional[Dict[str, Any]]:
        """获取最终报告"""
        session = self.sessions.get(session_id)
        if not session or not session.converged:
            return None
        
        # 重新收集最后一轮的假设
        # （实际实现中应该保存每轮的假设）
        # 这里简化处理
        
        return self.coordinator.generate_report(
            final_hypothesis=session.hypotheses[-1] if session.hypotheses else None,
            fault_pattern=fault_pattern,
            total_time_sec=total_time_sec,
            total_tokens_used=total_tokens_used
        )
    
    def should_continue(self, session_id: str) -> bool:
        """是否继续下一轮"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        return not session.converged and session.round_number < session.max_rounds
    
    def adjust_strategy(
        self,
        session_id: str,
        current_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据当前轮次调整策略"""
        session = self.sessions.get(session_id)
        if not session:
            return current_strategy
        
        # 随着轮次增加，扩大搜索范围
        adjusted = current_strategy.copy()
        
        if session.round_number >= 2:
            # 第 2 轮后：扩大时间窗口
            adjusted["time_window"] = "1h"
            adjusted["causal_depth"] = current_strategy.get("causal_depth", 2) + 1
        
        if session.round_number >= 3:
            # 第 3 轮后：降低置信度阈值
            adjusted["confidence_threshold"] = 0.75
        
        return adjusted
