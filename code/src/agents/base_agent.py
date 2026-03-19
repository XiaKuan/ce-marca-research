"""
智能体基类

定义所有智能体的通用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
from datetime import datetime


class AgentRole(Enum):
    """智能体角色"""
    COORDINATOR = "coordinator"
    METRICS = "metrics"
    LOGS = "logs"
    TRACES = "traces"


class MessageType(Enum):
    """消息类型"""
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    HYPOTHESIS = "hypothesis"
    HYPOTHESIS_AGGREGATION = "hypothesis_aggregation"
    STRATEGY_UPDATE = "strategy_update"
    FINAL_REPORT = "final_report"


@dataclass
class AgentMessage:
    """智能体间通信消息"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    round_id: str = ""
    sender: AgentRole = AgentRole.COORDINATOR
    receiver: AgentRole = AgentRole.COORDINATOR
    message_type: MessageType = MessageType.DATA_REQUEST
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "round_id": self.round_id,
            "sender": self.sender.value,
            "receiver": self.receiver.value,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentMessage":
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            round_id=data.get("round_id", ""),
            sender=AgentRole(data.get("sender", "coordinator")),
            receiver=AgentRole(data.get("receiver", "coordinator")),
            message_type=MessageType(data.get("message_type", "data_request")),
            content=data.get("content", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat())
        )


@dataclass
class Hypothesis:
    """根因假设"""
    service: str
    confidence: float
    evidence: List[Dict[str, Any]]
    source_agent: AgentRole
    reasoning: str
    causal_path: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "service": self.service,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "source_agent": self.source_agent.value,
            "reasoning": self.reasoning,
            "causal_path": self.causal_path,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.message_history: List[AgentMessage] = []
        
    @abstractmethod
    def analyze(
        self,
        data: Dict[str, Any],
        causal_graph,
        strategy: Dict[str, Any]
    ) -> Hypothesis:
        """
        分析数据并生成假设
        
        Args:
            data: 监控/日志/追踪数据
            causal_graph: 因果图
            strategy: 推理策略配置
        
        Returns:
            Hypothesis: 根因假设
        """
        pass
    
    def receive_message(self, message: AgentMessage):
        """接收消息"""
        self.message_history.append(message)
    
    def send_message(
        self,
        receiver: AgentRole,
        message_type: MessageType,
        content: Dict[str, Any]
    ) -> AgentMessage:
        """发送消息"""
        message = AgentMessage(
            sender=self.role,
            receiver=receiver,
            message_type=message_type,
            content=content
        )
        self.message_history.append(message)
        return message
    
    def get_recent_messages(self, limit: int = 10) -> List[AgentMessage]:
        """获取最近的消息"""
        return self.message_history[-limit:]
    
    def clear_history(self):
        """清空消息历史"""
        self.message_history = []
    
    def __repr__(self):
        return f"{self.role.value}_agent"
