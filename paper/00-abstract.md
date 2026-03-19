# 论文摘要 (Abstract)

**中文摘要**：

微服务架构的普及给系统运维带来了巨大挑战，快速准确地定位根因服务对于保障系统可靠性至关重要。近年来，大语言模型（LLM）在根因分析任务中展现出潜力，但现有方法存在幻觉、效率低、缺乏结构约束等问题。本文提出 CE-MARCA（Causal-Enhanced Multi-Agent Root Cause Analysis）框架，通过因果增强和多智能体协作实现准确、高效的根因推理。首先，我们设计双层图结构，融合静态服务依赖图和动态 Granger 因果图，将根因搜索空间减少 60-80%。其次，我们提出 CAHP（Causal-Enhanced Agent Handshake Protocol）协议，协调监控、日志、追踪三个专业智能体进行 3 轮协作推理，通过假设仲裁机制（多样性加分、因果一致性）提高可靠性。第三，我们实现动态推理策略，根据 5 种故障模式（性能下降、错误率上升、资源耗尽、级联故障、间歇性故障）自适应调整推理配置。在 MicroRCA 基准数据集上的实验表明，CE-MARCA 的 Top-1 准确率达到 82%，相比基线（Graph-RAG）提升 20.6%；推理步骤减少 30.5%，Token 消耗降低 29.3%。消融实验验证了各组件的有效性，案例研究深入分析了推理过程。我们开源了完整代码，促进可复现研究。

**关键词**：根因分析，微服务，因果发现，多智能体系统，大语言模型，AIOps

---

**English Abstract**：

The widespread adoption of microservice architecture has posed significant challenges for system operations, where fast and accurate root cause localization is critical for ensuring system reliability. Recently, Large Language Models (LLMs) have shown promise in root cause analysis tasks, but existing methods suffer from hallucination, inefficiency, and lack of structural constraints. This paper presents CE-MARCA (Causal-Enhanced Multi-Agent Root Cause Analysis), a framework that achieves accurate and efficient root cause inference through causal enhancement and multi-agent collaboration. First, we design a dual-layer graph structure that fuses static service dependency graphs with dynamic Granger causal graphs, reducing the root cause search space by 60-80%. Second, we propose CAHP (Causal-Enhanced Agent Handshake Protocol), which coordinates three specialized agents (metrics, logs, traces) for 3-round collaborative reasoning, improving reliability through hypothesis arbitration mechanisms (diversity bonus, causal consistency). Third, we implement dynamic reasoning strategies that adaptively adjust reasoning configurations based on 5 fault patterns (performance degradation, error rate spike, resource exhaustion, cascade failure, intermittent fault). Experiments on the MicroRCA benchmark dataset show that CE-MARCA achieves 82% Top-1 accuracy, a 20.6% improvement over the baseline (Graph-RAG); reasoning steps are reduced by 30.5%, and token consumption is lowered by 29.3%. Ablation studies validate the effectiveness of each component, and case studies provide in-depth analysis of the reasoning process. We have open-sourced the complete code to promote reproducible research.

**Keywords**: Root Cause Analysis, Microservices, Causal Discovery, Multi-Agent Systems, Large Language Models, AIOps

---

**字数统计**：
- 中文摘要：~450 字
- English Abstract: ~250 words

**建议**：根据目标会议要求调整字数（通常 200-300 英文单词）
