"""
协调智能体

负责全局协调、策略选择、假设仲裁和结果聚合
"""

from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent, AgentRole, AgentMessage, MessageType, Hypothesis
import numpy as np


class CoordinatorAgent(BaseAgent):
    """协调智能体"""
    
    def __init__(self):
        super().__init__(AgentRole.COORDINATOR)
        self.hypotheses_buffer: List[Hypothesis] = []
        
    def analyze(
        self,
        data: Dict[str, Any],
        causal_graph,
        strategy: Dict[str, Any]
    ) -> Hypothesis:
        """
        协调智能体不直接分析数据，而是聚合其他智能体的假设
        
        此方法用于接口一致性，实际使用 aggregate_hypotheses
        """
        raise NotImplementedError("Coordinator aggregates, not analyzes directly")
    
    def collect_hypotheses(
        self,
        metrics_hypothesis: Hypothesis,
        logs_hypothesis: Hypothesis,
        traces_hypothesis: Hypothesis
    ):
        """收集各智能体的假设"""
        self.hypotheses_buffer = [
            metrics_hypothesis,
            logs_hypothesis,
            traces_hypothesis
        ]
    
    def arbitrate_hypotheses(
        self,
        causal_graph,
        min_agreement: float = 0.6
    ) -> Hypothesis:
        """
        仲裁假设：综合多个智能体的假设，生成最终假设
        
        Args:
            causal_graph: 因果图（用于一致性检查）
            min_agreement: 最小一致同意阈值
        
        Returns:
            final_hypothesis: 最终假设
        """
        # Step 1: 按服务分组假设
        service_hypotheses: Dict[str, List[Hypothesis]] = {}
        for hyp in self.hypotheses_buffer:
            if hyp.service not in service_hypotheses:
                service_hypotheses[hyp.service] = []
            service_hypotheses[hyp.service].append(hyp)
        
        # Step 2: 计算每个服务的综合置信度
        service_scores: Dict[str, float] = {}
        arbitration_log = []
        
        for service, hyps in service_hypotheses.items():
            # 基础分数：置信度平均
            base_score = np.mean([h.confidence for h in hyps])
            
            # 多样性加分：多个智能体独立提出同一假设
            diversity_bonus = len(set([h.source_agent for h in hyps])) * 0.1
            
            # 因果一致性加分：假设在因果图上有支持路径
            causal_bonus = self._check_causal_consistency(service, causal_graph) * 0.2
            
            # 最终分数（上限 1.0）
            final_score = min(base_score + diversity_bonus + causal_bonus, 1.0)
            
            service_scores[service] = final_score
            arbitration_log.append({
                "service": service,
                "base_score": base_score,
                "diversity_bonus": diversity_bonus,
                "causal_bonus": causal_bonus,
                "final_score": final_score
            })
        
        # Step 3: 选择最高分服务
        if not service_scores:
            return self._create_empty_hypothesis()
        
        root_cause_service = max(service_scores, key=service_scores.get)
        final_confidence = service_scores[root_cause_service]
        
        # Step 4: 生成最终假设
        supporting_hyps = [h for h in self.hypotheses_buffer 
                          if h.service == root_cause_service]
        
        final_hypothesis = Hypothesis(
            service=root_cause_service,
            confidence=final_confidence,
            evidence=[e for h in supporting_hyps for e in h.evidence],
            source_agent=AgentRole.COORDINATOR,
            reasoning=self._generate_reasoning(supporting_hyps, arbitration_log),
            causal_path=causal_graph.extract_causal_path(
                root_cause_service, 
                supporting_hyps[0].causal_path[-1] if supporting_hyps[0].causal_path else root_cause_service
            ) if causal_graph else []
        )
        
        return final_hypothesis
    
    def _check_causal_consistency(self, service: str, causal_graph) -> float:
        """
        检查假设的因果一致性
        
        Returns:
            0.0-1.0 的一致性分数
        """
        if causal_graph is None or causal_graph.graph is None:
            return 0.0
        
        # 检查该服务是否有显著的入边（被其他服务因果影响）
        incoming_edges = list(causal_graph.graph.in_edges(service, data=True))
        
        if not incoming_edges:
            return 0.0
        
        # 计算平均因果强度
        avg_strength = np.mean([data['strength'] for _, _, data in incoming_edges])
        
        # 归一化到 0-1
        # 假设 F 统计量 > 10 为强因果
        consistency = min(avg_strength / 10.0, 1.0)
        
        return consistency
    
    def _generate_reasoning(
        self,
        supporting_hyps: List[Hypothesis],
        arbitration_log: List[Dict]
    ) -> str:
        """生成推理解释"""
        agents_involved = set([h.source_agent.value for h in supporting_hyps])
        
        reasoning_parts = [
            f"基于 {len(agents_involved)} 个智能体的协作分析：",
        ]
        
        # 添加各智能体的证据摘要
        for hyp in supporting_hyps:
            reasoning_parts.append(
                f"- {hyp.source_agent.value}: {hyp.reasoning} "
                f"(置信度：{hyp.confidence:.2f})"
            )
        
        # 添加仲裁信息
        service_log = next(
            (log for log in arbitration_log if log["service"] == supporting_hyps[0].service),
            None
        )
        if service_log:
            reasoning_parts.append(
                f"\n仲裁评分：基础={service_log['base_score']:.2f}, "
                f"多样性 +{service_log['diversity_bonus']:.2f}, "
                f"因果 +{service_log['causal_bonus']:.2f}"
            )
        
        return "\n".join(reasoning_parts)
    
    def _create_empty_hypothesis(self) -> Hypothesis:
        """创建空假设（当无法确定根因时）"""
        return Hypothesis(
            service="unknown",
            confidence=0.0,
            evidence=[],
            source_agent=AgentRole.COORDINATOR,
            reasoning="无法确定根因：证据不足或冲突",
            causal_path=[]
        )
    
    def generate_report(
        self,
        final_hypothesis: Hypothesis,
        fault_pattern: str,
        total_time_sec: float,
        total_tokens_used: int
    ) -> Dict[str, Any]:
        """生成根因分析报告"""
        return {
            "root_cause_service": final_hypothesis.service,
            "confidence": final_hypothesis.confidence,
            "fault_pattern": fault_pattern,
            "causal_path": final_hypothesis.causal_path,
            "evidence_summary": {
                h.source_agent.value: h.evidence
                for h in self.hypotheses_buffer
            },
            "reasoning_steps": final_hypothesis.reasoning.split("\n"),
            "recommendations": self._generate_recommendations(final_hypothesis),
            "generated_at": final_hypothesis.timestamp,
            "total_time_sec": total_time_sec,
            "total_tokens_used": total_tokens_used
        }
    
    def _generate_recommendations(self, hypothesis: Hypothesis) -> List[str]:
        """生成建议措施"""
        recommendations = []
        
        # 根据置信度生成不同级别的建议
        if hypothesis.confidence > 0.85:
            recommendations.append(
                f"🔴 高置信度根因：{hypothesis.service}，建议立即检查该服务"
            )
        elif hypothesis.confidence > 0.6:
            recommendations.append(
                f"🟡 中等置信度根因：{hypothesis.service}，建议结合人工经验进一步确认"
            )
        else:
            recommendations.append(
                f"🟢 低置信度根因：{hypothesis.service}，建议扩大调查范围"
            )
        
        # 根据因果路径生成建议
        if hypothesis.causal_path:
            path_str = " → ".join(hypothesis.causal_path)
            recommendations.append(f"因果传播路径：{path_str}")
        
        # 通用建议
        recommendations.append("建议查看该服务的监控指标、日志和调用链详情")
        
        return recommendations
    
    def clear_buffer(self):
        """清空假设缓冲区"""
        self.hypotheses_buffer = []
