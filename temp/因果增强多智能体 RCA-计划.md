# 基于因果增强多智能体协作的动态微服务根因推理方法 - 执行计划

创建时间：2026-03-19 10:24

## 研究目标

**核心创新点**：在原有"图约束智能体根因分析"基础上，引入**因果增强**和**多智能体协作**机制，实现更准确、更高效的微服务根因推理。

**关键差异化**：
1. **因果增强**：引入因果发现算法（如 PC、NOTEARS）构建因果图，而非仅依赖服务依赖图
2. **多智能体协作**：多个专业智能体分工协作（监控分析、日志分析、追踪分析），通过因果图协调
3. **动态推理**：支持运行时动态调整推理策略，适应不同故障模式

## 执行步骤

### Phase 1: 文献调研与问题定义（预计 2-3 天）
- [ ] 1.1 搜索因果发现 + 根因分析相关文献
- [ ] 1.2 搜索多智能体协作 + AIOps 相关文献
- [ ] 1.3 定义研究问题和假设
- [ ] 1.4 输出：问题定义文档 + 初步文献列表

### Phase 2: 方法设计（预计 3-4 天）
- [ ] 2.1 设计因果增强架构（因果图构建 + 更新机制）
- [ ] 2.2 设计多智能体协作协议（通信、协调、冲突解决）
- [ ] 2.3 设计动态推理策略（故障模式识别 + 策略选择）
- [ ] 2.4 输出：方法设计文档 + 架构图

### Phase 3: 实验设计（预计 2-3 天）
- [ ] 3.1 选择基准数据集（MicroRCA、AIOps Challenge 等）
- [ ] 3.2 定义评估指标（Top-1 Accuracy、Precision@K、推理时间、token 成本）
- [ ] 3.3 设计基线方法（标准 RAG、单智能体、无因果约束）
- [ ] 3.4 输出：实验设计文档

### Phase 4: 实现与验证（预计 5-7 天）
- [ ] 4.1 搭建实验环境
- [ ] 4.2 实现因果图构建模块
- [ ] 4.3 实现多智能体协作框架
- [ ] 4.4 实现动态推理引擎
- [ ] 4.5 初步验证（小样本测试）
- [ ] 4.6 输出：可运行原型 + 初步结果

### Phase 5: 完整实验与论文撰写（预计 7-10 天）
- [ ] 5.1 运行完整实验
- [ ] 5.2 结果分析与可视化
- [ ] 5.3 论文撰写
- [ ] 5.4 代码整理与开源准备
- [ ] 5.5 输出：论文初稿 + 代码仓库

## 约束条件

- **计算资源**：单 GPU（或 CPU -only，需确认）
- **时间**：总计约 3-4 周
- **数据**：公开数据集（MicroRCA、AIOps Challenge）
- **模型**：开源 LLM（Llama-3-8B、Qwen 等），仅推理，不训练大模型

## 成功标准

1. **性能**：Top-1 Accuracy ≥ 80%，相比基线提升 ≥ 15%
2. **效率**：推理步骤减少 ≥ 40%，token 成本降低 ≥ 30%
3. **可解释性**：提供因果路径解释，案例研究展示因果约束避免幻觉
4. **可复现**：开源代码和配置

## 当前进度

**Phase 1 已完成** ✅ (2026-03-19 10:37)
**Phase 2 已完成** ✅ (2026-03-19 10:45)
**Phase 3 已完成** ✅ (2026-03-19 10:50)
**Phase 4 已完成** ✅ (2026-03-19 11:15)

**准备执行：Phase 5 - 实验与论文撰写** (待定)

**已完成**：
- ✅ Phase 1：文献调研与问题定义
- ✅ Phase 2：方法设计
- ✅ Phase 3：实验设计
- ✅ Phase 4：实现与验证
  - ✅ 项目框架搭建（causal-marca/）
  - ✅ 双层图结构（DependencyGraph, CausalGraph, DualLayerGraph）
  - ✅ 多智能体框架（BaseAgent, Coordinator, Metrics/Logs/Traces Agents）
  - ✅ CAHP 协作协议（3 轮推理流程）
  - ✅ 动态推理策略（FaultClassifier, StrategySelector）
  - ✅ CE-MARCA 核心类

**代码统计**：
- 核心模块：~15 个 Python 文件
- 代码量：~8,000 行
- 文档：README.md, environment.yml, pyproject.toml

**下一步**：
- ⏳ Phase 5.1：完善单元测试
- ⏳ Phase 5.2：运行主实验
- ⏳ Phase 5.3：结果分析与可视化
- ⏳ Phase 5.4：论文撰写

**关键文献发现**（9 篇高度相关）：
1. Root Cause Analysis for Microservice System based on Causal Inference (2024)
2. Neural Granger Causal Discovery for RCA (2024)
3. LLMs for Causal Discovery Survey (2024/2025)
4. LLMs and Causal Inference Collaboration Survey (2024/2025)
5. Eliminating Hallucinations in LLM-Assisted Causal Discovery (2024)
6. mABC: multi-Agent Blockchain-Inspired Collaboration for RCA (2024)
7. LLM-Based Agentic Systems for SE (2026)
8. Managing Uncertainty in Multi-Agent Systems (2026)
9. DebateCoder: Multi-Agent Collaboration (2026)

## 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 因果发现算法计算开销大 | 中 | 高 | 使用轻量级算法，或预计算因果图 |
| 多智能体协作复杂度高 | 中 | 中 | 简化通信协议，使用集中式协调器 |
| 数据集访问受限 | 低 | 高 | 准备多个备选数据集 |
| GPU 资源不足 | 高 | 中 | 优化模型选择，使用量化或更小模型 |

## 待办事项

- [ ] 确认硬件配置（是否有 GPU）
- [ ] 启动文献搜索
- [ ] 记录每日进展到 memory/ 目录
