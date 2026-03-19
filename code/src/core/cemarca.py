"""
CE-MARCA 核心类

Causal-Enhanced Multi-Agent Root Cause Analysis
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path

from .graph.dual_layer import DualLayerGraph
from .graph.causal_graph import CausalGraph
from .agents.coordinator import CoordinatorAgent
from .agents.metrics_agent import MetricsAgent
from .agents.logs_agent import LogsAgent
from .agents.traces_agent import TracesAgent
from .agents.cahp_protocol import CAHPProtocol
from .strategy.fault_classifier import FaultClassifier, AnomalySignature
from .strategy.strategy_selector import ReasoningStrategySelector


class CEMARCA:
    """
    CE-MARCA: Causal-Enhanced Multi-Agent Root Cause Analysis
    
    基于因果增强多智能体协作的动态微服务根因推理方法
    """
    
    def __init__(
        self,
        dependency_graph_path: Optional[str] = None,
        llm_model: str = "Qwen/Qwen2.5-7B-Instruct",
        significance_level: float = 0.05,
        max_lag: int = 5
    ):
        """
        初始化 CE-MARCA
        
        Args:
            dependency_graph_path: 静态依赖图路径
            llm_model: LLM 模型名称
            significance_level: Granger 因果显著性水平
            max_lag: Granger 因果最大滞后阶数
        """
        # 双层图结构
        self.dual_graph = DualLayerGraph()
        if dependency_graph_path:
            self.dual_graph.load_dependency_graph(dependency_graph_path)
        
        # 智能体
        self.coordinator = CoordinatorAgent()
        self.metrics_agent = MetricsAgent()
        self.logs_agent = LogsAgent()
        self.traces_agent = TracesAgent()
        
        # CAHP 协议
        self.cahp = CAHPProtocol(
            self.coordinator,
            self.metrics_agent,
            self.logs_agent,
            self.traces_agent
        )
        
        # 策略模块
        self.fault_classifier = FaultClassifier()
        self.strategy_selector = ReasoningStrategySelector()
        
        # 配置
        self.llm_model = llm_model
        self.significance_level = significance_level
        self.max_lag = max_lag
        
        # 统计
        self.total_queries = 0
        self.total_tokens = 0
    
    def analyze(
        self,
        anomaly_timestamp: str,
        metrics_data: Dict[str, Any],
        logs_data: Dict[str, Any],
        traces_data: Dict[str, Any],
        baseline_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        执行根因分析
        
        Args:
            anomaly_timestamp: 故障发生时间
            metrics_data: 指标数据
            logs_data: 日志数据
            traces_data: 追踪数据
            baseline_metrics: 基线指标（用于计算变化）
        
        Returns:
            root_cause_report: 根因分析报告
        """
        start_time = time.time()
        
        # Step 1: 故障模式识别
        fault_pattern = self._identify_fault_pattern(
            metrics_data, baseline_metrics
        )
        
        # Step 2: 策略选择
        strategy = self.strategy_selector.select(fault_pattern)
        
        # Step 3: 构建因果图
        self._build_causal_graph(metrics_data)
        
        # Step 4: 启动 CAHP 会话
        session_id = f"session_{anomaly_timestamp}"
        self.cahp.start_session(session_id, max_rounds=strategy.max_rounds)
        
        # Step 5: 多轮推理
        data = {
            "services": self._merge_service_data(
                metrics_data, logs_data, traces_data
            ),
            "traces": traces_data.get("traces", [])
        }
        
        round_num = 0
        while self.cahp.should_continue(session_id):
            round_num += 1
            
            # 运行一轮
            hypotheses = self.cahp.run_round(
                session_id,
                data,
                self.dual_graph.causal_graph,
                self.strategy_selector.to_dict(strategy)
            )
            
            # 如果未收敛，调整策略
            if not self.cahp.sessions[session_id].converged:
                strategy = self.cahp.adjust_strategy(session_id, strategy)
        
        # Step 6: 生成报告
        total_time = time.time() - start_time
        
        report = self.cahp.get_final_report(
            session_id,
            fault_pattern=fault_pattern.value,
            total_time_sec=total_time,
            total_tokens_used=self.total_tokens
        )
        
        if report is None:
            report = self._create_error_report(
                "未能收敛到足够置信度的根因",
                fault_pattern.value,
                total_time
            )
        
        return report
    
    def _identify_fault_pattern(
        self,
        metrics_data: Dict[str, Any],
        baseline_metrics: Optional[Dict[str, float]]
    ):
        """识别故障模式"""
        # 简化实现：从指标数据提取特征
        # 实际实现需要更复杂的特征提取
        
        current = {}
        baseline = baseline_metrics or {}
        
        # 提取当前指标（简化：取所有服务的平均）
        services = metrics_data.get("services", {})
        if services:
            first_service = list(services.values())[0]
            current = {
                "latency_p99": first_service.get("latency_p99", [0])[-1],
                "error_rate": first_service.get("error_rate", [0])[-1],
                "cpu_usage": first_service.get("cpu_usage", [0])[-1],
                "memory_usage": first_service.get("memory_usage", [0])[-1],
                "throughput": first_service.get("throughput", [0])[-1]
            }
        
        return self.fault_classifier.classify_from_metrics(
            current,
            baseline,
            num_anomalous_services=len(services)
        )
    
    def _build_causal_graph(self, metrics_data: Dict[str, Any]):
        """构建因果图"""
        # 简化实现
        # 实际实现需要从时间序列数据计算 Granger 因果
        pass
    
    def _merge_service_data(
        self,
        metrics_data: Dict[str, Any],
        logs_data: Dict[str, Any],
        traces_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并各服务的数据"""
        merged = {}
        
        # 合并指标
        for service_id, metrics in metrics_data.get("services", {}).items():
            if service_id not in merged:
                merged[service_id] = {}
            merged[service_id]["metrics"] = metrics
        
        # 合并日志
        for service_id, logs in logs_data.get("services", {}).items():
            if service_id not in merged:
                merged[service_id] = {}
            merged[service_id]["logs"] = logs
        
        return merged
    
    def _create_error_report(
        self,
        error_message: str,
        fault_pattern: str,
        total_time: float
    ) -> Dict[str, Any]:
        """创建错误报告"""
        return {
            "root_cause_service": "unknown",
            "confidence": 0.0,
            "fault_pattern": fault_pattern,
            "causal_path": [],
            "evidence_summary": {},
            "reasoning_steps": [f"错误：{error_message}"],
            "recommendations": ["建议检查监控数据完整性"],
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_time_sec": total_time,
            "total_tokens_used": self.total_tokens
        }
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """获取图统计信息"""
        return self.dual_graph.get_graph_statistics()
