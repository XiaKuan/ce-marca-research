# 6. Discussion (Polished)

## 6.1 Method Advantages

**1. Structural Constraints Reduce Hallucination**:
Compared to unconstrained LLM methods, CE-MARCA constrains the search space to causally related services through the dual-layer graph structure. Experiments show this reduces hallucination rate from 35% to 12%.

**2. Multi-Agent Collaboration Improves Reliability**:
Single-agent methods are susceptible to noise from individual data sources. Multi-agent collaboration improves decision reliability through evidence cross-validation. Ablation studies show that removing multi-agent collaboration reduces accuracy by 11.11%.

**3. Dynamic Strategies Adapt to Different Scenarios**:
Fixed strategies cannot adapt to diverse fault patterns. The dynamic strategy selector automatically adjusts reasoning configurations based on 5 fault patterns, maintaining high performance (75-88%) across all types.

**4. Strong Interpretability**:
CE-MARCA generates reports containing causal paths, multi-agent evidence, and confidence scores, helping operations personnel understand the reasoning process. User study rating: 4.2/5.0.

## 6.2 Limitations

**1. Computational Overhead**:
Granger causality test has computational complexity of $O(|E_{dep}| \cdot T \cdot p^2)$. For large systems (100+ services), causal graph construction may take 5-10 minutes. Although it can be pre-computed offline, real-time performance is still limited.

**Mitigation**:
- Use incremental updates, recomputing only significantly changed edges
- Employ approximate algorithms (e.g., sampling) to accelerate computation
- Leverage GPU acceleration for Neural Granger

**2. Data Dependency**:
CE-MARCA relies on complete monitoring data (metrics, logs, traces). If data is missing or of poor quality, performance degrades.

**Mitigation**:
- Implement data quality checks to detect missing and anomalous data
- Support partial data modes (e.g., metrics-only)
- Provide data completion suggestions

**3. Fault Pattern Coverage**:
Currently supports 5 fault patterns, but real-world scenarios may have more complex composite faults (e.g., simultaneous resource exhaustion and network partition).

**Mitigation**:
- Extend fault classifier to support composite faults
- Introduce meta-learning for rapid adaptation to new fault types
- Collect more real-world fault cases

**4. Cold Start Problem**:
When new systems lack historical data, causal graph quality is low, affecting reasoning accuracy.

**Mitigation**:
- Use default dependency graphs as initial constraints
- Transfer learning: transfer causal knowledge from similar systems
- Active learning: annotate small samples for rapid adaptation

**5. Causal Discovery Assumptions**:
Granger causality test assumes stationary time series, but real monitoring data may be non-stationary (e.g., periodicity, trends).

**Mitigation**:
- Use differencing or detrending preprocessing
- Employ methods suitable for non-stationary series (e.g., time-varying Granger)
- Incorporate domain knowledge to constrain causal direction

## 6.3 External Validity

**Threat 1: Dataset Representativeness**:
Experiments primarily used the MicroRCA dataset, which includes 3 architectures but all are open-source example systems, potentially differing from real production systems.

**Mitigation**: We plan to collaborate with industry partners to collect real production environment data for evaluation.

**Threat 2: Baseline Implementation**:
Some baseline methods (e.g., mABC) are reproduced implementations, potentially differing from original implementations.

**Mitigation**: We use official code (when available) or contact authors to confirm implementation details.

**Threat 3: Hyperparameter Tuning**:
Hyperparameters were tuned on the validation set, potentially overfitting to the test set.

**Mitigation**: We use cross-validation and report average results across multiple random seeds.

## 6.4 Ethical Considerations

**1. Automated Decision Risks**:
Root cause analysis results may influence operational decisions (e.g., service restart, traffic switching). Incorrect root cause localization may lead to unnecessary service disruptions.

**Mitigation**:
- Provide confidence scores, recommending human intervention for low confidence
- Record complete reasoning process, supporting post-hoc audit
- Clearly state method limitations

**2. Data Privacy**:
Logs and traces may contain sensitive information (e.g., user IDs, IP addresses).

**Mitigation**:
- Data anonymization processing
- On-premise deployment, data stays within domain
- Compliance with data protection regulations (e.g., GDPR)

**3. Responsibility Attribution**:
If automated root cause analysis leads to incorrect decisions, responsibility attribution is unclear.

**Mitigation**:
- Clearly state the system is an auxiliary tool, final decisions remain with humans
- Provide detailed reasoning reports, supporting responsibility tracing

## 6.5 Deployment Recommendations

**1. Progressive Deployment**:
- **Phase 1**: Offline analysis of historical faults to validate accuracy
- **Phase 2**: Parallel operation, comparing with manual analysis
- **Phase 3**: Gradually take over simple faults, complex faults still handled by humans

**2. Monitoring and Feedback**:
- Record accuracy and user feedback for each analysis
- Regularly update causal graphs and fault classifiers
- Establish feedback loops for continuous improvement

**3. Personnel Training**:
- Train operations personnel to understand and use the system
- Establish human-machine collaboration workflows
- Define escalation mechanisms (when to transfer to humans)

## 6.6 Chapter Summary

This chapter discussed CE-MARCA's advantages, limitations, external validity threats, ethical considerations, and deployment recommendations. Although the method has limitations, through appropriate mitigations and progressive deployment, it can be safely and effectively applied in practical scenarios.

---

**Open Questions**:
1. How to balance automation and human intervention?
2. How to evaluate the long-term value of root cause analysis systems?
3. How to design better human-machine collaboration interfaces?

These questions require further exploration in future research.

---

**润色说明**：
1. 增强批判性分析
2. 优化缓解措施呈现
3. 规范伦理考虑讨论
4. 添加明确的部署建议
5. 强化开放问题提出
6. 添加章节小结
