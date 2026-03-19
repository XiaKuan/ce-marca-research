# Phase 1 文献调研记录

创建时间：2026-03-19

## 关键文献发现

### 因果发现 + 根因分析

1. **Root Cause Analysis for Microservice System based on Causal Inference: How Far Are We?** (2024)
   - arXiv:2408.xxxxx (Submitted Aug 2024)
   - 关键贡献：系统性评估因果推理在微服务 RCA 中的应用进展
   - 相关性：⭐⭐⭐⭐⭐ 直接相关，提供领域现状分析

2. **Root Cause Analysis In Microservice Using Neural Granger Causal Discovery** (2024)
   - Authors: Cheng-Ming Lin et al.
   - arXiv:2402.xxxxx (Submitted Feb 2024)
   - 关键贡献：使用 Neural Granger 因果发现进行微服务根因分析
   - 相关性：⭐⭐⭐⭐⭐ 直接相关，提供因果发现方法

3. **Large Language Models for Causal Discovery: Current Landscape and Future Directions** (2024/2025)
   - Authors: Guangya Wan et al.
   - arXiv:2402.xxxxx (Submitted Feb 2024, revised Feb 2025)
   - 关键贡献：LLM 用于因果发现的综述
   - 相关性：⭐⭐⭐⭐⭐ 提供 LLM+ 因果发现的系统框架

4. **Large Language Models and Causal Inference in Collaboration: A Survey** (2024/2025)
   - Authors: Xiaoyu Liu et al.
   - arXiv:2403.xxxxx (Submitted Mar 2024, revised Mar 2025)
   - 关键贡献：LLM 与因果推理协作的综述
   - 相关性：⭐⭐⭐⭐ 提供方法论基础

5. **A Novel Approach to Eliminating Hallucinations in Large Language Model-Assisted Causal Discovery** (2024)
   - arXiv:2411.xxxxx (Submitted Nov 2024)
   - 关键贡献：消除 LLM 辅助因果发现中的幻觉
   - 相关性：⭐⭐⭐⭐⭐ 直接解决我们关注的幻觉问题

### 多智能体协作 + RCA

6. **mABC: multi-Agent Blockchain-Inspired Collaboration for root cause analysis in micro-services architecture** (2024)
   - Authors: Wei Zhang et al.
   - arXiv:2404.xxxxx (Submitted Apr 2024, revised Dec 2024)
   - 关键贡献：多智能体协作 + 区块链启发式方法用于 RCA
   - 相关性：⭐⭐⭐⭐⭐ 直接相关，提供多智能体协作框架

### 多智能体协作 + 软件工程

7. **LLM-Based Agentic Systems for Software Engineering: Challenges and Opportunities** (2026)
   - Authors: Yongjian Tang, Thomas Runkler
   - arXiv:2601.xxxxx (Submitted Jan 2026)
   - 关键贡献：LLM 智能体系统在 SE 中的挑战与机遇
   - 相关性：⭐⭐⭐⭐ 提供智能体系统设计洞察

8. **Managing Uncertainty in LLM-based Multi-Agent System Operation** (2026)
   - arXiv:2602.xxxxx (Submitted Feb 2026)
   - 关键贡献：管理多智能体系统中的不确定性
   - 相关性：⭐⭐⭐⭐ 对动态推理策略有启发

9. **DebateCoder: Multi-Agent Collaboration for Code Generation** (2026)
   - Authors: Haoji Zhang et al.
   - arXiv:2601.xxxxx (Submitted Jan 2026)
   - 关键贡献：辩论式多智能体协作代码生成
   - 相关性：⭐⭐⭐ 协作机制可借鉴

### 已有研究基础（从之前运行继承）

4. **Graph-Constrained Agentic Root Cause Analysis** (前期研究)
   - 关键贡献：图约束智能体推理框架
   - 相关性：⭐⭐⭐⭐ 作为基线方法

## 研究空白分析

基于以上文献，识别以下研究空白：

1. **因果增强 + 多智能体协作的结合**：现有工作要么使用因果发现，要么使用多智能体，但两者结合的研究较少
   - mABC 使用多智能体但未深入因果发现
   - Neural Granger 使用因果发现但是单模型方法
   - **我们的机会**：结合两者优势

2. **动态推理策略**：大多数方法使用固定推理流程，缺乏根据故障模式动态调整的能力
   - 现有工作多为静态分析流程
   - **我们的机会**：引入故障模式识别 + 策略选择机制

3. **因果图与依赖图的融合**：如何将静态服务依赖图与动态因果图有效结合仍是开放问题
   - 依赖图：静态架构信息
   - 因果图：动态运行时关系
   - **我们的机会**：双层图结构，静态 + 动态融合

4. **LLM 幻觉问题**：LLM 辅助因果发现中存在幻觉风险
   - 最新研究 (2024.11) 专门讨论此问题
   - **我们的机会**：使用因果约束减少幻觉

## 研究方法初步设计

基于文献调研，初步设计如下：

### 核心架构

```
┌─────────────────────────────────────────────┐
│          协调智能体 (Coordinator)            │
│  - 故障模式识别                              │
│  - 推理策略选择                              │
│  - 结果聚合与验证                            │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│ 监控智能体 │ │ 日志智能体 │ │ 追踪智能体 │
│ (Metrics) │ │  (Logs)   │ │  (Traces) │
└───────────┘ └───────────┘ └───────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
        ┌───────────────────────┐
        │   因果图引擎          │
        │  - 静态依赖图 (已知)   │
        │  - 动态因果图 (学习)   │
        │  - Granger/NOTEARS    │
        └───────────────────────┘
```

### 关键创新点

1. **因果增强**：使用 Neural Granger 或 NOTEARS 构建因果图，约束智能体搜索空间
2. **多智能体协作**：专业分工 + 协调器，避免单智能体认知过载
3. **动态推理**：根据故障模式（性能下降、错误率上升、延迟增加）选择不同推理策略

## 下一步搜索关键词

- "causal graph neural network microservices"
- "multi-agent reinforcement learning AIOps"
- "dynamic root cause analysis"
- "causal discovery survey 2024"
- "LLM agent collaboration software engineering"

## 待获取的文献全文

- [ ] 获取文献 1 的 PDF 全文
- [ ] 获取文献 2 的 PDF 全文
- [ ] 获取文献 3 的 PDF 全文
- [ ] 搜索引用这些文献的相关工作
