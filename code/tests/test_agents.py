"""
单元测试：智能体模块
"""

import pytest
from src.agents.base_agent import AgentRole, MessageType, AgentMessage, Hypothesis
from src.agents.metrics_agent import MetricsAgent
from src.agents.logs_agent import LogsAgent
from src.agents.traces_agent import TracesAgent
from src.agents.coordinator import CoordinatorAgent
from src.agents.cahp_protocol import CAHPProtocol


class TestAgentMessage:
    """测试智能体消息"""
    
    def test_create_message(self):
        """测试创建消息"""
        msg = AgentMessage(
            sender=AgentRole.METRICS,
            receiver=AgentRole.COORDINATOR,
            message_type=MessageType.HYPOTHESIS,
            content={"service": "payment-service"}
        )
        
        assert msg.sender == AgentRole.METRICS
        assert msg.receiver == AgentRole.COORDINATOR
        assert msg.message_type == MessageType.HYPOTHESIS
    
    def test_message_to_dict(self):
        """测试消息序列化"""
        msg = AgentMessage(
            sender=AgentRole.LOGS,
            receiver=AgentRole.COORDINATOR,
            message_type=MessageType.DATA_RESPONSE,
            content={"error_count": 5}
        )
        
        msg_dict = msg.to_dict()
        
        assert msg_dict["sender"] == "logs"
        assert msg_dict["message_type"] == "data_response"
        assert msg_dict["content"]["error_count"] == 5
    
    def test_message_from_dict(self):
        """测试消息反序列化"""
        msg_dict = {
            "sender": "traces",
            "receiver": "coordinator",
            "message_type": "hypothesis",
            "content": {"service": "api-gateway"}
        }
        
        msg = AgentMessage.from_dict(msg_dict)
        
        assert msg.sender == AgentRole.TRACES
        assert msg.message_type == MessageType.HYPOTHESIS


class TestHypothesis:
    """测试假设"""
    
    def test_create_hypothesis(self):
        """测试创建假设"""
        hyp = Hypothesis(
            service="payment-service",
            confidence=0.85,
            evidence=[{"type": "metric", "metric": "cpu", "value": 95}],
            source_agent=AgentRole.METRICS,
            reasoning="CPU 使用率异常高",
            causal_path=["api-gateway", "order-service", "payment-service"]
        )
        
        assert hyp.service == "payment-service"
        assert hyp.confidence == 0.85
        assert len(hyp.evidence) == 1
        assert len(hyp.causal_path) == 3
    
    def test_hypothesis_to_dict(self):
        """测试假设序列化"""
        hyp = Hypothesis(
            service="order-service",
            confidence=0.75,
            evidence=[],
            source_agent=AgentRole.LOGS,
            reasoning="检测到错误日志"
        )
        
        hyp_dict = hyp.to_dict()
        
        assert hyp_dict["service"] == "order-service"
        assert hyp_dict["source_agent"] == "logs"


class TestMetricsAgent:
    """测试监控智能体"""
    
    def test_detect_anomalies(self):
        """测试异常检测"""
        agent = MetricsAgent(thresholds={"cpu_usage": 80.0})
        
        metrics = {
            "cpu_usage": [50, 55, 60, 95, 98],  # 最后两个值异常
            "memory_usage": [60, 62, 65, 68, 70]
        }
        
        anomalies = agent._detect_anomalies(metrics)
        
        # 应该检测到 CPU 异常
        assert len(anomalies) > 0
        assert any(a["metric"] == "cpu_usage" for a in anomalies)
    
    def test_analyze_no_anomaly(self):
        """测试无异常分析"""
        agent = MetricsAgent()
        
        data = {
            "services": {
                "service-a": {
                    "cpu_usage": [50, 52, 51, 53],
                    "memory_usage": [60, 61, 60, 62]
                }
            }
        }
        
        hypothesis = agent.analyze(data, None, {})
        
        assert hypothesis.service == "unknown"
        assert hypothesis.confidence == 0.0
    
    def test_analyze_with_anomaly(self):
        """测试有异常分析"""
        agent = MetricsAgent()
        
        data = {
            "services": {
                "service-a": {
                    "cpu_usage": [50, 52, 95, 98],  # CPU 突增
                    "memory_usage": [60, 61, 62, 63]
                }
            }
        }
        
        hypothesis = agent.analyze(data, None, {})
        
        assert hypothesis.service == "service-a"
        assert hypothesis.confidence > 0.5


class TestLogsAgent:
    """测试日志智能体"""
    
    def test_analyze_error_logs(self):
        """测试错误日志分析"""
        agent = LogsAgent()
        
        data = {
            "services": {
                "payment-service": {
                    "logs": [
                        {"level": "info", "message": "Request processed"},
                        {"level": "error", "message": "Connection timeout"},
                        {"level": "error", "message": "Database connection failed"},
                        {"level": "fatal", "message": "Service crash"}
                    ]
                }
            }
        }
        
        hypothesis = agent.analyze(data, None, {})
        
        assert hypothesis.service == "payment-service"
        assert hypothesis.confidence > 0.5


class TestTracesAgent:
    """测试追踪智能体"""
    
    def test_analyze_latency_bottleneck(self):
        """测试延迟瓶颈分析"""
        agent = TracesAgent()
        
        data = {
            "traces": [
                {
                    "trace_id": "trace-001",
                    "spans": [
                        {"service": "api-gateway", "duration_ms": 50},
                        {"service": "order-service", "duration_ms": 200},
                        {"service": "payment-service", "duration_ms": 1500}  # 延迟瓶颈
                    ]
                }
            ]
        }
        
        hypothesis = agent.analyze(data, None, {})
        
        assert hypothesis.service == "payment-service"


class TestCoordinatorAgent:
    """测试协调智能体"""
    
    def test_arbitrate_hypotheses(self):
        """测试假设仲裁"""
        coordinator = CoordinatorAgent()
        
        # 创建多个智能体的假设
        metrics_hyp = Hypothesis(
            service="payment-service",
            confidence=0.8,
            evidence=[{"type": "cpu", "value": 95}],
            source_agent=AgentRole.METRICS,
            reasoning="CPU 异常"
        )
        
        logs_hyp = Hypothesis(
            service="payment-service",  # 同一服务
            confidence=0.7,
            evidence=[{"type": "error", "count": 5}],
            source_agent=AgentRole.LOGS,
            reasoning="错误日志"
        )
        
        traces_hyp = Hypothesis(
            service="order-service",  # 不同服务
            confidence=0.6,
            evidence=[{"type": "latency", "value": 500}],
            source_agent=AgentRole.TRACES,
            reasoning="延迟高"
        )
        
        coordinator.collect_hypotheses(metrics_hyp, logs_hyp, traces_hyp)
        
        # 仲裁（无因果图）
        final = coordinator.arbitrate_hypotheses(causal_graph=None)
        
        # 应该选择 payment-service（多个智能体支持）
        assert final.service == "payment-service"
        # 置信度应该因多样性加分而提高
        assert final.confidence > 0.8


class TestCAHPProtocol:
    """测试 CAHP 协议"""
    
    def test_start_session(self):
        """测试开始会话"""
        coordinator = CoordinatorAgent()
        protocol = CAHPProtocol(
            coordinator,
            MetricsAgent(),
            LogsAgent(),
            TracesAgent()
        )
        
        session = protocol.start_session("test-session-001", max_rounds=3)
        
        assert session.session_id == "test-session-001"
        assert session.max_rounds == 3
        assert session.round_number == 0
    
    def test_run_round(self):
        """测试运行一轮"""
        coordinator = CoordinatorAgent()
        protocol = CAHPProtocol(
            coordinator,
            MetricsAgent(),
            LogsAgent(),
            TracesAgent()
        )
        
        protocol.start_session("test-001")
        
        data = {
            "services": {
                "service-a": {
                    "cpu_usage": [50, 55, 95, 98],
                    "memory_usage": [60, 62, 65, 68]
                }
            },
            "traces": []
        }
        
        hypotheses = protocol.run_round(
            "test-001",
            data,
            causal_graph=None,
            strategy={"confidence_threshold": 0.85}
        )
        
        assert "metrics" in hypotheses
        assert "logs" in hypotheses
        assert "traces" in hypotheses
    
    def test_should_continue(self):
        """测试是否继续"""
        coordinator = CoordinatorAgent()
        protocol = CAHPProtocol(
            coordinator,
            MetricsAgent(),
            LogsAgent(),
            TracesAgent()
        )
        
        protocol.start_session("test-002", max_rounds=3)
        
        # 第 1 轮后应该继续
        protocol.run_round("test-002", {"services": {}, "traces": []}, None, {})
        assert protocol.should_continue("test-002") == True
        
        # 第 2 轮后应该继续
        protocol.run_round("test-002", {"services": {}, "traces": []}, None, {})
        assert protocol.should_continue("test-002") == True
        
        # 第 3 轮后应该停止
        protocol.run_round("test-002", {"services": {}, "traces": []}, None, {})
        assert protocol.should_continue("test-002") == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
