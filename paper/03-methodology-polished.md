# 3. Methodology (Polished)

## 3.1 Problem Definition

**Definition 1 (Microservice Root Cause Analysis Problem)**: Given a microservice system $S = \{s_1, s_2, ..., s_n\}$ and a fault instance $F$, the goal of Root Cause Analysis (RCA) is to identify the root cause service $s_{root} \in S$ and its causal propagation path $P = (s_{root}, ..., s_{affected})$.

**Input**:
- Static service dependency graph $G_{dep} = (V, E_{dep})$, where $V$ is the set of services and $E_{dep}$ represents call relationships
- Runtime monitoring data $M = \{M_t\}_{t=1}^T$, including metrics, logs, and traces
- Fault detection timestamp $t_{anomaly}$

**Output**:
- Root cause service $s_{root}$
- Confidence score $c \in [0, 1]$
- Causal propagation path $P$
- Reasoning explanation $R$

**Challenges**:
1. **Large Search Space**: Microservice systems typically contain dozens to hundreds of services, making exhaustive search infeasible.
2. **Causal Confusion**: Faults propagate along dependency chains, causing multiple services to exhibit anomalies simultaneously.
3. **Heterogeneous Data**: Metrics, logs, and traces have different formats and require unified analysis.
4. **Real-time Requirements**: Operational scenarios require fast localization (within minutes).

## 3.2 CE-MARCA Framework Overview

We propose **CE-MARCA** (Causal-Enhanced Multi-Agent Root Cause Analysis), a framework that addresses the above challenges through causal enhancement and multi-agent collaboration.

**Core Ideas**:
1. **Structural Constraints**: Leverage system topological knowledge (dependency graphs) and runtime causal relationships (causal graphs) to constrain the search space.
2. **Specialized Division of Labor**: Multiple agents separately process metrics, logs, and traces, avoiding cognitive overload of single agents.
3. **Dynamic Adaptation**: Automatically adjust reasoning strategies based on fault patterns to improve efficiency.

**Architectural Components**:
- **Dual-Layer Graph Engine**: Static dependency graph + Dynamic causal graph
- **Multi-Agent System**: Coordinator + Specialized agents (metrics, logs, traces)
- **Strategy Module**: Fault classifier + Strategy selector

**Figure 1** illustrates the overall architecture of CE-MARCA (see `results/figures/fig1_architecture.png`).

## 3.3 Dual-Layer Graph Structure

### 3.3.1 Static Dependency Graph

The static dependency graph $G_{dep} = (V, E_{dep})$ encodes service call relationships, derived from:
- Service registries (e.g., Consul, Eureka)
- Configuration files (e.g., Kubernetes YAML)
- Historical trace data statistics

**Construction Method**:
$$E_{dep} = \{(s_i, s_j) | s_i \text{ calls } s_j \text{ with frequency} > \theta\}$$

where $\theta$ is a frequency threshold used to filter occasional calls.

**Uses**:
- Prune candidate causal pairs: Only compute Granger causality for service pairs with direct call relationships
- Constrain search space: Root causes can only be in upstream dependencies of anomalous services

### 3.3.2 Dynamic Causal Graph

The dynamic causal graph $G_{causal} = (V, E_{causal})$ encodes runtime causal relationships, learned from time-series data through Granger causality tests.

**Definition 2 (Granger Causality)**: For two time series $X$ and $Y$, if using past values of $X$ significantly improves the prediction accuracy of $Y$, then $X$ is said to Granger-cause $Y$.

**Computation Method**:
For a service pair $(s_i, s_j)$, compare the following two models:

1. **Restricted Model** (using only past values of $s_j$):
   $$Y_t = \alpha + \sum_{k=1}^{p} \beta_k Y_{t-k} + \epsilon_t$$

2. **Unrestricted Model** (using past values of both $s_i$ and $s_j$):
   $$Y_t = \alpha + \sum_{k=1}^{p} \beta_k Y_{t-k} + \sum_{k=1}^{p} \gamma_k X_{t-k} + \epsilon_t$$

where $p$ is the lag order, $X$ is the metric series of $s_i$, and $Y$ is the metric series of $s_j$.

**F-test**:
$$F = \frac{(RSS_{restricted} - RSS_{unrestricted}) / p}{RSS_{unrestricted} / (T - 2p - 1)}$$

where $RSS$ is the residual sum of squares, and $T$ is the time series length.

If the p-value $< \alpha$ (default 0.05), we reject the null hypothesis and conclude that a causal relationship exists.

**Causal Edge Weight**:
$$w_{ij} = F_{statistic}(s_i \to s_j)$$

**Update Mechanism**:
- Sliding window: Recompute causal graph every $\Delta t$ time
- Incremental update: Only recompute edges with significant changes

### 3.3.3 Dual-Layer Graph Fusion

**Constrained Search Space**:
For an anomalous service $s_{anomalous}$, the candidate root cause set is:
$$C(s_{anomalous}) = \{s | (s, s_{anomalous}) \in E_{dep} \land (s, s_{anomalous}) \in E_{causal}\}$$

That is, services that simultaneously satisfy:
1. Are upstream services in the dependency graph
2. Have significant causal edges in the causal graph

**Advantages**:
- Compared to using only dependency graphs: Reduces false positives (excludes upstream services without causal relationships)
- Compared to using only causal graphs: Reduces computation (prunes service pairs without dependency relationships)

## 3.4 Multi-Agent Collaboration (CAHP Protocol)

We propose the **CAHP** (Causal-Enhanced Agent Handshake Protocol) protocol to coordinate multiple agents for collaborative reasoning.

### 3.4.1 Agent Roles

**Table 1: Agent Roles and Responsibilities**

| Role | Responsibilities | Input | Output |
|------|------------------|-------|--------|
| Coordinator | Global coordination, hypothesis arbitration, result aggregation | All agent hypotheses | Final root cause report |
| Metrics Agent | Analyze metric anomalies (CPU, memory, latency) | Metrics data, causal graph | Hypothesis + metric evidence |
| Logs Agent | Analyze log patterns (errors, warnings) | Logs data, causal graph | Hypothesis + log evidence |
| Traces Agent | Analyze call chain latency | Traces data, causal graph | Hypothesis + trace evidence |

### 3.4.2 3-Round Reasoning Process

**Round 1: Parallel Data Collection**

Agents collect and analyze data in parallel:
$$H_i^{(1)} = \text{Agent}_i.\text{analyze}(D_i, G_{causal}, \pi)$$

where $H_i^{(1)}$ is the hypothesis from agent $i$, $D_i$ is the corresponding data, and $\pi$ is the reasoning strategy.

**Round 2: Causal-Constrained Reasoning**

The coordinator adjusts search priorities for each agent based on the causal graph:
$$\text{priority}(s) = \sum_{s' \in \text{upstream}(s)} w_{s's}$$

Agents re-analyze based on priorities and generate updated hypotheses $H_i^{(2)}$.

**Round 3: Hypothesis Arbitration and Verification**

The coordinator collects all hypotheses and performs arbitration:

**Definition 3 (Hypothesis Confidence Score)**:
$$\text{score}(s) = \underbrace{\frac{1}{|A_s|}\sum_{i \in A_s} c_i}_{\text{Base Score}} + \underbrace{0.1 \cdot |A_s|}_{\text{Diversity Bonus}} + \underbrace{0.2 \cdot \text{causal\_consistency}(s)}_{\text{Causal Consistency}}$$

where $A_s$ is the set of agents proposing service $s$ as root cause, and $c_i$ is the confidence from agent $i$.

**Diversity Bonus**: Multiple agents independently proposing the same hypothesis increases confidence.

**Causal Consistency**:
$$\text{causal\_consistency}(s) = \frac{1}{|\text{in\_edges}(s)|} \sum_{(s', s) \in E_{causal}} w_{s's}$$

The service with the highest $\text{score}(s)$ is selected as the root cause.

### 3.4.3 Convergence Conditions

Reasoning terminates under the following conditions:
1. **Confidence Threshold**: $\max_s \text{score}(s) \geq \tau$ (default 0.85)
2. **Maximum Rounds**: Reach preset maximum rounds (default 3)

## 3.5 Dynamic Reasoning Strategies

### 3.5.1 Fault Pattern Classification

**Definition 4 (Fault Feature Vector)**:
$$\mathbf{f} = [\Delta_{latency}, \Delta_{error}, \Delta_{cpu}, \Delta_{memory}, \Delta_{throughput}, n_{services}]$$

where $\Delta$ represents the rate of change in metrics, and $n_{services}$ is the number of anomalous services.

**Table 2: Fault Patterns and Rules**

| Fault Pattern | Rule | Reasoning Strategy |
|---------------|------|-------------------|
| Performance Degradation | $\Delta_{latency} > 2.0$ | Traces-first, depth=3 |
| Error Rate Spike | $\Delta_{error} > 0.5$ | Logs-first, window=15min |
| Resource Exhaustion | $\Delta_{cpu} > 0.3 \lor \Delta_{memory} > 0.3$ | Metrics-first, window=1h |
| Cascade Failure | $n_{services} > 3$ | Causal-graph-first, depth=5 |
| Intermittent Fault | High variance, low mean change | Multi-round, window=2h |

### 3.5.2 Strategy Selector

The strategy selector $\Pi$ maps fault patterns to strategy configurations:
$$\pi = \Pi(fault\_pattern) = (\text{priority}, \text{time\_window}, \text{causal\_depth}, \text{max\_rounds})$$

**Table 3: Strategy Configuration Examples**

| Fault Pattern | Agent Priority | Time Window | Causal Depth | Max Rounds |
|---------------|----------------|-------------|--------------|------------|
| Performance Degradation | [traces, metrics, logs] | 30min | 3 | 3 |
| Error Rate Spike | [logs, traces, metrics] | 15min | 2 | 3 |
| Resource Exhaustion | [metrics, logs, traces] | 1h | 2 | 3 |
| Cascade Failure | [metrics, traces, logs] | 1h | 5 | 3 |

### 3.5.3 Dynamic Adjustment

If first-round reasoning does not converge, adjust the strategy:
- **Expand time window**: 30min → 1h → 2h
- **Increase causal depth**: 2 → 3 → 5
- **Lower confidence threshold**: 0.85 → 0.75 → 0.65

## 3.6 Complexity Analysis

### 3.6.1 Time Complexity

**Causal Graph Construction**:
- Number of candidate pairs: $O(|E_{dep}|)$ (after dependency graph pruning)
- Single-pair Granger test: $O(T \cdot p^2)$, where $T$ is time series length and $p$ is lag order
- Total complexity: $O(|E_{dep}| \cdot T \cdot p^2)$

**Multi-Agent Reasoning**:
- Single-round analysis: $O(n \cdot d)$, where $n$ is number of services and $d$ is data dimension
- Maximum rounds: $R_{max}$ (default 3)
- Total complexity: $O(R_{max} \cdot n \cdot d)$

**Overall**:
$$O(|E_{dep}| \cdot T \cdot p^2 + R_{max} \cdot n \cdot d)$$

For typical microservice systems ($n \approx 100$, $|E_{dep}| \approx 300$), single analysis can be completed within minutes.

### 3.6.2 Space Complexity

- Dependency graph: $O(n + |E_{dep}|)$
- Causal graph: $O(n + |E_{causal}|)$
- Monitoring data: $O(n \cdot T)$
- Total complexity: $O(n \cdot T + |E_{dep}| + |E_{causal}|)$

### 3.6.3 Token Cost Analysis

Compared to unconstrained LLM methods, CE-MARCA reduces token consumption by constraining the search space through causal graphs:

**Unconstrained Method**:
$$\text{tokens}_{baseline} \approx n \cdot \text{tokens\_per\_service}$$

**CE-MARCA**:
$$\text{tokens}_{ours} \approx |C(s_{anomalous})| \cdot \text{tokens\_per\_service}$$

where $|C(s_{anomalous})| \ll n$ (typically 60-80% reduction).

---

**Chapter Summary**:

This chapter detailed the design of the CE-MARCA framework:
1. Dual-layer graph structure fuses static dependencies and dynamic causal relationships
2. CAHP protocol coordinates multi-agent collaborative reasoning through 3 rounds
3. Dynamic strategies adapt to 5 fault patterns
4. Complexity analysis demonstrates feasibility in practical scenarios

The next chapter presents the experimental evaluation.

---

**润色说明**：
1. 优化数学公式格式
2. 增强段落过渡
3. 统一术语使用
4. 规范表格和图表引用
5. 添加章节小结
6. 提高可读性和逻辑连贯性
