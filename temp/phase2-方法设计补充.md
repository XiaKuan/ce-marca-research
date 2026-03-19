# Phase 2 补充：实现细节

创建时间：2026-03-19 10:40

---

## 2.5 核心算法伪代码

### 算法 1：因果增强多智能体根因分析（CE-MARCA）

```python
Algorithm 1: CE-MARCA - Causal-Enhanced Multi-Agent Root Cause Analysis

Input:
    - anomaly_timestamp: 故障发生时间
    - services: 微服务列表
    - dependency_graph: 静态依赖图 G_dep
    - metrics_window: 监控数据窗口 W_m
    - logs_window: 日志数据窗口 W_l
    - traces_window: 追踪数据窗口 W_t
    - max_rounds: 最大推理轮数 R_max

Output:
    - root_cause_report: 根因分析报告

1:  // ========== Phase 1: 故障模式识别 ==========
2:  anomaly_signature ← ExtractAnomalySignature(W_m, W_l, W_t)
3:  fault_pattern ← ClassifyFaultPattern(anomaly_signature)
4:  
5:  // ========== Phase 2: 策略选择 ==========
6:  reasoning_strategy ← SelectStrategy(fault_pattern, G_dep)
7:  // reasoning_strategy = {priority, time_window, causal_depth}
8:  
9:  // ========== Phase 3: 因果图构建 ==========
10: causal_graph ← BuildCausalGraph(W_m, G_dep)
11: // 使用 Granger 因果，只检查 G_dep 中存在的边
12: 
13: // ========== Phase 4: 多智能体协作推理 ==========
14: hypotheses ← []
15: for round r = 1 to R_max do
16:     // 4.1 并行数据收集
17:     metrics_evidence ← MetricsAgent.Analyze(W_m, causal_graph, reasoning_strategy)
18:     logs_evidence ← LogsAgent.Analyze(W_l, causal_graph, reasoning_strategy)
19:     traces_evidence ← TracesAgent.Analyze(W_t, causal_graph, reasoning_strategy)
20:     
21:     // 4.2 假设生成
22:     h_metrics ← GenerateHypothesis(metrics_evidence, confidence_threshold=0.7)
23:     h_logs ← GenerateHypothesis(logs_evidence, confidence_threshold=0.7)
24:     h_traces ← GenerateHypothesis(traces_evidence, confidence_threshold=0.7)
25:     
26:     // 4.3 假设聚合
27:     hypotheses ← hypotheses ∪ {h_metrics, h_logs, h_traces}
28:     
29:     // 4.4 收敛检查
30:     if Converged(hypotheses, min_confidence=0.85) then
31:         break
32:     end if
33:     
34:     // 4.5 策略调整（如果未收敛）
35:     reasoning_strategy ← AdjustStrategy(reasoning_strategy, hypotheses)
36:     // 扩大时间窗口、增加因果深度等
37: end for
38: 
39: // ========== Phase 5: 仲裁与报告 ==========
40: final_hypothesis ← ArbitrateHypotheses(hypotheses, causal_graph)
41: root_cause_report ← GenerateReport(final_hypothesis, evidence=hypotheses)
42: 
43: return root_cause_report
```

### 算法 2：Granger 因果强度计算

```python
Algorithm 2: GrangerCausalStrength - 计算两服务间的 Granger 因果强度

Input:
    - X: 源服务指标时间序列 (长度 T)
    - Y: 目标服务指标时间序列 (长度 T)
    - max_lag: 最大滞后阶数 L
    - significance_level: 显著性水平 α (默认 0.05)

Output:
    - causal_strength: 因果强度 (F 统计量)
    - p_value: 显著性 p 值
    - is_causal: 是否存在因果关系 (布尔值)

1:  // Step 1: 构建受限模型 (Restricted Model)
2:  // Y_t = α + Σ β_i * Y_{t-i} + ε_t
3:  model_restricted ← FitAR(Y, order=max_lag)
4:  rss_restricted ← SumSquaredResiduals(model_restricted)
5:  
6:  // Step 2: 构建非受限模型 (Unrestricted Model)
7:  // Y_t = α + Σ β_i * Y_{t-i} + Σ γ_i * X_{t-i} + ε_t
8:  model_unrestricted ← FitVAR([Y, X], order=max_lag)
9:  rss_unrestricted ← SumSquaredResiduals(model_unrestricted)
10: 
11: // Step 3: F 检验
12: df1 ← max_lag  // 分子自由度
13: df2 ← T - 2*max_lag - 1  // 分母自由度
14: 
15: F_statistic ← ((rss_restricted - rss_unrestricted) / df1) / 
16:               (rss_unrestricted / df2)
17: 
18: p_value ← F_Distribution_CDF(F_statistic, df1, df2)
19: 
20: // Step 4: 判断因果性
21: if p_value < significance_level then
22:     is_causal ← True
23:     causal_strength ← F_statistic
24: else
25:     is_causal ← False
26:     causal_strength ← 0
27: end if
28: 
29: return (causal_strength, p_value, is_causal)
```

### 算法 3：智能体假设仲裁

```python
Algorithm 3: HypothesisArbitration - 多智能体假设仲裁

Input:
    - hypotheses: 假设列表 [{service, confidence, evidence, source_agent}]
    - causal_graph: 因果图
    - min_agreement: 最小一致同意阈值 (默认 0.6)

Output:
    - final_hypothesis: 最终假设
    - arbitration_log: 仲裁日志

1:  arbitration_log ← []
2:  
3:  // Step 1: 按服务分组假设
4:  service_hypotheses ← GroupByService(hypotheses)
5:  
6:  // Step 2: 计算每个服务的综合置信度
7:  service_scores ← {}
8:  for each service, hyps in service_hypotheses do
9:      // 加权平均：考虑证据多样性和因果一致性
10:     base_score ← Mean([h.confidence for h in hyps])
11:     
12:     // 多样性加分：多个智能体独立提出同一假设
13:     diversity_bonus ← len(set([h.source_agent for h in hyps])) * 0.1
14:     
15:     // 因果一致性加分：假设在因果图上有支持路径
16:     causal_bonus ← CheckCausalConsistency(service, causal_graph) * 0.2
17:     
18:     service_scores[service] ← min(base_score + diversity_bonus + causal_bonus, 1.0)
19:     
20:     arbitration_log.append({
21:         "service": service,
22:         "base_score": base_score,
23:         "diversity_bonus": diversity_bonus,
24:         "causal_bonus": causal_bonus,
25:         "final_score": service_scores[service]
26:     })
27: end for
28: 
29: // Step 3: 选择最高分服务
30: root_cause_service ← ArgMax(service_scores)
31: final_confidence ← service_scores[root_cause_service]
32: 
33: // Step 4: 生成最终假设
34: final_hypothesis ← {
35:     "service": root_cause_service,
36:     "confidence": final_confidence,
37:     "supporting_agents": [h.source_agent for h in hypotheses 
38:                            if h.service == root_cause_service],
39:     "evidence": [h.evidence for h in hypotheses 
40:                  if h.service == root_cause_service],
41:     "causal_path": ExtractCausalPath(root_cause_service, causal_graph)
42: }
43: 
44: return (final_hypothesis, arbitration_log)
```

---

## 2.6 数据结构定义

### 核心数据类

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import numpy as np

class FaultPattern(Enum):
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ERROR_RATE_SPIKE = "error_rate_spike"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CASCADE_FAILURE = "cascade_failure"
    INTERMITTENT_FAULT = "intermittent_fault"

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    METRICS = "metrics"
    LOGS = "logs"
    TRACES = "traces"

@dataclass
class AnomalySignature:
    """故障特征向量"""
    timestamp: str
    latency_p99_delta: float  # 延迟变化倍数
    error_rate_delta: float   # 错误率变化倍数
    cpu_delta: float          # CPU 使用率变化
    memory_delta: float       # 内存使用率变化
    throughput_delta: float   # 吞吐量变化
    num_anomalous_services: int
    affected_services: List[str]

@dataclass
class ReasoningStrategy:
    """推理策略配置"""
    priority: List[AgentRole]  # 智能体优先级
    time_window: str           # 时间窗口 (e.g., "30min")
    causal_depth: int          # 因果图搜索深度
    max_rounds: int = 3        # 最大推理轮数
    confidence_threshold: float = 0.85

@dataclass
class CausalEdge:
    """因果边"""
    source: str
    target: str
    strength: float           # F 统计量
    p_value: float
    is_significant: bool
    lag: int                  # 最优滞后阶数

@dataclass
class Hypothesis:
    """根因假设"""
    service: str
    confidence: float
    evidence: List[Dict]
    source_agent: AgentRole
    reasoning: str
    causal_path: List[str]
    timestamp: str

@dataclass
class RootCauseReport:
    """根因分析报告"""
    root_cause_service: str
    confidence: float
    fault_pattern: FaultPattern
    causal_path: List[str]
    evidence_summary: Dict[AgentRole, List[Dict]]
    reasoning_steps: List[str]
    recommendations: List[str]
    generated_at: str
    total_time_sec: float
    total_tokens_used: int
```

### 图结构定义

```python
import networkx as nx

class DualLayerGraph:
    """双层图结构"""
    
    def __init__(self):
        # Layer 1: 静态依赖图
        self.dependency_graph = nx.DiGraph()
        
        # Layer 2: 动态因果图
        self.causal_graph = nx.DiGraph()
        
    def add_dependency(self, source: str, target: str, 
                       call_frequency: float = None):
        """添加静态依赖边"""
        self.dependency_graph.add_edge(
            source, target, 
            call_frequency=call_frequency
        )
        
    def add_causal_edge(self, edge: CausalEdge):
        """添加动态因果边"""
        if edge.is_significant:
            self.causal_graph.add_edge(
                edge.source, edge.target,
                strength=edge.strength,
                p_value=edge.p_value,
                lag=edge.lag
            )
    
    def get_candidate_pairs(self) -> List[tuple]:
        """获取候选因果对（基于依赖图剪枝）"""
        return list(self.dependency_graph.edges())
    
    def get_causal_neighbors(self, service: str, 
                             depth: int = 1) -> List[str]:
        """获取因果邻居（指定深度内）"""
        neighbors = set()
        current_level = {service}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # 上游邻居（可能的根因）
                predecessors = self.causal_graph.predecessors(node)
                next_level.update(predecessors)
            neighbors.update(next_level)
            current_level = next_level
            
        return list(neighbors)
    
    def extract_causal_path(self, source: str, target: str) -> List[str]:
        """提取因果路径"""
        try:
            path = nx.shortest_path(
                self.causal_graph, 
                source=source, 
                target=target,
                weight=lambda u, v, d: -d.get('strength', 1)  # 强度越大，权重越小
            )
            return path
        except nx.NetworkXNoPath:
            return []
```

---

## 2.7 评估方案细化

### 数据集

| 数据集 | 规模 | 故障类型 | 标注 | 使用方式 |
|--------|------|----------|------|----------|
| **MicroRCA** | 100+ 故障 | 性能、错误、级联 | 根因服务 + 路径 | 主要评估 |
| **AIOps Challenge 2023** | 50+ 故障 | 多样 | 根因服务 | 补充评估 |
| **Synthetic (自生成)** | 200+ 故障 | 可控变量 | 完整标注 | 消融实验 |

### 基线方法

| 方法 | 描述 | 实现来源 |
|------|------|----------|
| **Standard RAG** | 检索增强生成，无图约束 | LangChain 默认 |
| **Graph-RAG** | 图约束检索，单智能体 | 前期研究 |
| **mABC** | 多智能体区块链协作 | 复现 (Zhang et al., 2024) |
| **Random Forest** | 传统 ML 分类器 | sklearn |
| **MicroRCA-SOTA** | MicroRCA 论文最佳方法 | 官方实现 |

### 评估指标计算

```python
def evaluate(root_cause_reports, ground_truth):
    """
    评估根因分析性能
    
    Args:
        root_cause_reports: 预测结果列表
        ground_truth: 真实标注列表
    
    Returns:
        metrics: 评估指标字典
    """
    # Top-1 Accuracy
    top1_correct = sum(
        1 for pred, truth in zip(root_cause_reports, ground_truth)
        if pred.root_cause_service == truth.root_cause_service
    )
    top1_accuracy = top1_correct / len(ground_truth)
    
    # Precision@K
    def precision_at_k(pred, truth, k=3):
        # 检查根因是否在前 K 个候选中
        # 这里简化为检查因果路径前 K 个节点
        causal_path = pred.causal_path[:k]
        return 1 if truth.root_cause_service in causal_path else 0
    
    precision_at_3 = np.mean([
        precision_at_k(pred, truth, k=3) 
        for pred, truth in zip(root_cause_reports, ground_truth)
    ])
    
    # 推理步骤数（智能体查询次数）
    avg_reasoning_steps = np.mean([
        len(pred.reasoning_steps) for pred in root_cause_reports
    ])
    
    # Token 成本
    avg_tokens = np.mean([
        pred.total_tokens_used for pred in root_cause_reports
    ])
    
    # 推理时间
    avg_time = np.mean([
        pred.total_time_sec for pred in root_cause_reports
    ])
    
    return {
        "top1_accuracy": top1_accuracy,
        "precision_at_3": precision_at_3,
        "avg_reasoning_steps": avg_reasoning_steps,
        "avg_tokens": avg_tokens,
        "avg_time_sec": avg_time
    }
```

### 消融实验设计

| 实验组 | 配置 | 目的 |
|--------|------|------|
| **Full** | 因果增强 + 多智能体 + 动态策略 | 完整方法 |
| **-Causal** | 无因果图，仅依赖图 | 验证因果增强效果 |
| **-MultiAgent** | 单智能体（协调器直接分析） | 验证多智能体效果 |
| **-Dynamic** | 固定策略（不动态调整） | 验证动态策略效果 |
| **-Diversity** | 仲裁时不加多样性加分 | 验证多样性奖励效果 |

---

## Phase 2 完成检查清单

- [x] 2.1 因果增强架构设计
- [x] 2.2 多智能体协作协议设计
- [x] 2.3 动态推理策略设计
- [x] 2.4 系统架构图
- [x] 2.5 伪代码实现细节
- [x] 2.6 数据结构定义
- [x] 2.7 评估方案细化

**Phase 2 状态**: ✅ 完成 (10:45)

**下一步**: Phase 3 - 实验设计
