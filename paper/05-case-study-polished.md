# 5. Case Study (Polished)

## 5.1 Success Case: Cascade Failure Localization

### 5.1.1 Case Description

**Fault Scenario**: In the Online Boutique architecture, the payment-service experienced database connection pool exhaustion, causing response latency. The fault propagated upstream through the call chain, affecting order-service and api-gateway.

**Fault Characteristics**:
- 3 services simultaneously exhibited elevated latency
- Error rate increased from 0.1% to 8%
- P99 latency increased from 200ms to 2500ms

**Ground Truth**: payment-service (database connection pool exhaustion)

### 5.1.2 CE-MARCA Reasoning Process

**Round 1: Parallel Data Collection**

| Agent | Detection Results | Preliminary Hypothesis | Confidence |
|-------|-------------------|------------------------|------------|
| Metrics | payment-service CPU 95%, memory 88% | payment-service | 0.75 |
| Logs | payment-service shows "Connection pool exhausted" errors | payment-service | 0.80 |
| Traces | payment-service latency 2500ms, order-service 500ms | payment-service | 0.70 |

**Round 2: Causal-Constrained Reasoning**

The coordinator constructs the causal graph:
```
api-gateway → order-service → payment-service
     │              │              │
  (15.2)        (18.7)         (root)
```

Numbers represent Granger causal strength (F-statistic).

Agents adjust priorities based on the causal graph and re-analyze:
- **Metrics Agent**: Confirms payment-service metrics anomaly appeared earliest
- **Logs Agent**: Discovers payment-service error logs have earliest timestamps
- **Traces Agent**: Confirms latency propagation starts from payment-service

**Round 3: Hypothesis Arbitration**

The coordinator collects hypotheses and performs arbitration:

**Payment Service Score Calculation**:
- Base Score: (0.75 + 0.80 + 0.70) / 3 = 0.75
- Diversity Bonus: 0.1 × 3 (3 agents agree) = 0.30
- Causal Consistency: 0.2 × 0.85 (strong incoming edges in causal graph) = 0.17
- **Final Score**: 0.75 + 0.30 + 0.17 = 1.22 (normalized to 0.92)

**Final Report**:
```
Root Cause Service: payment-service
Confidence: 92%
Causal Path: payment-service → order-service → api-gateway
Reasoning:
  - metrics: CPU 95%, memory 88% (confidence: 0.75)
  - logs: "Connection pool exhausted" errors (confidence: 0.80)
  - traces: Latency 2500ms, propagating from payment-service (confidence: 0.70)
Recommendations:
  🔴 High confidence root cause: payment-service, recommend immediate check of database connection pool configuration
```

### 5.1.3 Value of Causal Graph Analysis

**Comparative Experiment**: We compared performance with and without the causal graph.

**Without Causal Graph**:
- Standard RAG incorrectly identified api-gateway as root cause (because its latency was most visible)
- Reason: LLM was misled by surface symptoms, failing to identify causal propagation direction

**With Causal Graph**:
- CE-MARCA correctly identified payment-service as root cause
- Causal graph shows: payment-service → order-service → api-gateway propagation path
- Granger causality test confirms: payment-service changes precede other services

**Key Insight**: The causal graph helps distinguish "cause" from "effect" through temporal ordering and statistical significance, avoiding being misled by surface symptoms.

## 5.2 Failure Case: Intermittent Fault

### 5.2.1 Case Description

**Fault Scenario**: In the BookInfo architecture, the product-page service experienced intermittent memory leaks, occurring every 10-15 minutes and lasting 2-3 minutes before automatic recovery.

**Fault Characteristics**:
- Memory usage fluctuated periodically (60% → 90% → 60%)
- No obvious error logs
- Slight latency increase (200ms → 400ms)

**Ground Truth**: product-page (memory leak)

### 5.2.2 CE-MARCA Reasoning Process

**Round 1**:
- Metrics Agent: Detected memory fluctuation, but low confidence (0.55)
- Logs Agent: No obvious errors detected (confidence 0.30)
- Traces Agent: Latency change not significant (confidence 0.45)

**Round 2**:
Coordinator expanded time window (30min → 1h) and re-analyzed:
- Metrics Agent: Discovered periodic pattern, confidence increased to 0.65
- Logs Agent: Still no obvious errors
- Traces Agent: Latency change still not significant

**Round 3**:
Arbitration results:
- product-page score: 0.58 (below threshold 0.75)
- Final output: Unable to determine root cause (unknown)

### 5.2.3 Failure Analysis

**1. Insufficient Fault Pattern Recognition**:
- Intermittent fault characteristics were not obvious
- Fault classifier failed to accurately identify the pattern
- Periodic patterns require longer time windows (>2h) for detection

**2. Missing Log Evidence**:
- Memory leak did not produce obvious error logs
- Logs Agent could not provide effective evidence

**3. Limited Causal Graph Quality**:
- Intermittent faults caused non-stationary time series
- Granger causality test assumes stationarity, performance degraded

### 5.2.4 Improvement Directions

**1. Enhanced Fault Pattern Recognition**:
- Introduce frequency domain analysis (Fourier transform) for periodicity detection
- Use change point detection algorithms for intermittent faults

**2. Improved Log Analysis**:
- Use more sensitive anomaly detection (e.g., Isolation Forest)
- Combine log semantic analysis to identify potential warnings

**3. Non-Stationary Causal Discovery**:
- Use causal discovery methods suitable for non-stationary time series
- Consider segmented causal analysis

## 5.3 User Study (Preliminary)

We invited 3 operations engineers to evaluate CE-MARCA's interpretability.

**Evaluation Task**:
- Read RCA reports for 10 faults
- Rating: Interpretability (1-5), Trustworthiness (1-5), Practicality (1-5)

**Results**:

| Engineer | Interpretability | Trustworthiness | Practicality | Feedback |
|----------|-----------------|-----------------|--------------|----------|
| Engineer A (5 yrs exp) | 4.5 | 4.0 | 4.5 | "Causal path is clear, helps understand fault propagation" |
| Engineer B (3 yrs exp) | 4.0 | 4.5 | 4.0 | "Confidence score helps me know when human intervention is needed" |
| Engineer C (8 yrs exp) | 4.0 | 3.5 | 4.5 | "Recommendations are practical, but want to see more context" |

**Average Rating**: Interpretability 4.2 / Trustworthiness 4.0 / Practicality 4.3

**Qualitative Feedback**:
- **Strengths**: Causal path visualization, multi-agent evidence aggregation, confidence scoring
- **Improvement Suggestions**: Add historical fault comparison, provide more detailed timelines

## 5.4 Chapter Summary

Through case studies, we gained in-depth insights into CE-MARCA's reasoning process:
1. **Success Case**: Causal graphs help distinguish causal propagation direction, avoiding being misled by surface symptoms
2. **Failure Case**: Intermittent fault detection remains challenging, requiring improved fault pattern recognition
3. **User Feedback**: Interpretability and practicality are well-received, trustworthiness needs further improvement

The next chapter discusses the method's limitations and future work.

---

**润色说明**：
1. 增强案例故事性
2. 优化表格格式
3. 突出关键洞察
4. 添加明确的改进方向
5. 规范用户研究呈现
6. 添加章节小结
