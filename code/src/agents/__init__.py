"""
智能体模块：多智能体协作框架
"""

from .base_agent import BaseAgent, AgentMessage, MessageType
from .coordinator import CoordinatorAgent
from .metrics_agent import MetricsAgent
from .logs_agent import LogsAgent
from .traces_agent import TracesAgent
from .cahp_protocol import CAHPProtocol

__all__ = [
    "BaseAgent",
    "AgentMessage",
    "MessageType",
    "CoordinatorAgent",
    "MetricsAgent",
    "LogsAgent",
    "TracesAgent",
    "CAHPProtocol",
]
