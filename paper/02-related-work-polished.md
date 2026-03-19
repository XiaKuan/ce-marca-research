# 2. Related Work (Polished)

## 2.1 Microservice Root Cause Analysis

Microservice root cause analysis (RCA) is a core problem in the AIOps domain. Existing methods can be categorized into three types:

**Rule-Based Methods**:
Early RCA systems primarily relied on predefined rules and thresholds [1]. For example, setting CPU usage >80% triggers alerts. Such methods are straightforward but struggle with complex fault patterns and incur high rule maintenance costs.

**Machine Learning-Based Methods**:
With the development of machine learning technology, researchers have proposed various supervised and unsupervised methods. Wang et al. [2] proposed using Random Forest for fault type classification. Chen et al. [3] used LSTM for learning time series patterns. However, these methods require large amounts of labeled data and have limited generalization capability.

**Graph-Based Methods**:
In recent years, graph-based methods have gained attention. MicroRCA [4] utilizes service dependency graphs for root cause localization. GraphRCA [5] combines call chain graphs with Bayesian networks. These methods leverage system topological knowledge but have limited reasoning capabilities.

**Recent Advances**:
Zhang et al. [6] proposed mABC, using multi-agent collaboration for RCA. However, this method does not fully leverage causal relationships and has a simple inter-agent coordination mechanism.

## 2.2 LLM Applications in Software Engineering

Large Language Models (LLMs) have rapidly developed in software engineering applications [7].

**Code Generation and Debugging**:
Chen et al. [8] found LLMs perform excellently in code generation tasks. Li et al. [9] proposed using LLMs for automated debugging.

**Log Analysis**:
LogLLM [10] uses LLMs for log anomaly detection. However, this method only processes log data, not combining metrics and traces.

**Fault Diagnosis**:
Wang et al. [11] explored LLM applications in fault diagnosis. Research found that unconstrained LLMs are prone to hallucination, generating incorrect causal explanations.

**Limitations**:
The main limitation of existing LLM methods is the lack of structural constraints [12]. Treating system telemetry data as unstructured text leads to inefficient and unreliable reasoning.

## 2.3 Causal Discovery and Inference

Causal discovery aims to learn causal relationships from data [13].

**Traditional Methods**:
- **Granger Causality** [14]: Based on time series prediction, suitable for linear relationships
- **PC Algorithm** [15]: Based on conditional independence tests
- **NOTEARS** [16]: Transforms DAG constraints into continuous optimization problems

**Neural Causal Discovery**:
Neural Granger [17] uses neural networks for modeling nonlinear causal relationships. However, computational complexity is high.

**Causal and LLM Combination**:
Recent research explores combining causal discovery with LLMs. Liu et al. [18] proposed using causal constraints to reduce LLM hallucination. Wan et al. [19] surveyed LLM applications in causal discovery.

**Research Gap**:
Existing work primarily focuses on causal reasoning in text domains, with less attention to structured scenarios like microservice systems.

## 2.4 Multi-Agent Systems

Multi-agent systems demonstrate advantages in complex tasks [20].

**Collaboration Frameworks**:
Park et al. [21] proposed Generative Agents, simulating human behavior. Zhang et al. [6] applied multi-agent systems to RCA.

**Communication Protocols**:
Inter-agent communication protocols are central to multi-agent systems [22]. Existing protocols include blackboard models, message passing, etc.

**AIOps Applications**:
In the AIOps domain, multi-agent systems are used for monitoring [23], alert correlation [24], and other tasks. However, existing work does not fully leverage causal relationships for agent coordination.

## 2.5 Research Gaps

Through analysis of existing work, we identify the following research gaps:

**Gap 1: Causal Enhancement + Multi-Agent Collaboration**:
Existing work either uses causal discovery [17, 18] or multi-agent systems [6, 21], but research combining both is limited. Particularly in microservice RCA scenarios, how to leverage causal graphs for multi-agent coordination remains unexplored.

**Gap 2: Dynamic Reasoning Strategies**:
Existing methods mostly use fixed reasoning processes [4, 5], lacking the ability to dynamically adjust based on fault patterns.

**Gap 3: Dual-Layer Graph Fusion**:
Research on fusing static dependency graphs with dynamic causal graphs is insufficient. Existing work either uses only dependency graphs [4] or only causal graphs [17].

**Our Positioning**:
Addressing the above gaps, we propose the CE-MARCA framework, the first to combine causal enhancement with multi-agent collaboration, achieving dynamic adaptive microservice root cause analysis.

---

**润色说明**：
1. 增强文献分类清晰度
2. 优化批判性分析
3. 明确研究空白表述
4. 规范引用格式
5. 增强逻辑连贯性
6. 添加明确的方法定位
