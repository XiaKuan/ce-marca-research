# Phase 3：实验设计

创建时间：2026-03-19 10:45
状态：进行中

---

## 3.1 实验环境搭建方案

### 硬件环境

| 组件 | 配置 | 说明 |
|------|------|------|
| **CPU** | 当前环境 | CPU-only，限制因果发现算法选择 |
| **内存** | ≥16GB 推荐 | 处理大规模时间序列数据 |
| **存储** | ≥100GB SSD | 数据集 + 日志存储 |
| **GPU** | 无（当前） | 如有可升级 Neural Granger |

### 软件环境

```yaml
# environment.yml
name: causal-marca
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy>=1.24
  - pandas>=2.0
  - networkx>=3.0
  - scikit-learn>=1.3
  - statsmodels>=0.14  # Granger 因果检验
  - pytest>=7.0
  
  # LLM 推理
  - transformers>=4.35
  - accelerate>=0.24
  - bitsandbytes>=0.41  # 量化（CPU 友好）
  
  # 多智能体框架
  - langchain>=0.1
  - pydantic>=2.0
  
  # 可视化
  - matplotlib>=3.7
  - seaborn>=0.12
  - plotly>=5.18
  
  # 开发工具
  - jupyterlab>=4.0
  - black>=23.0
  - mypy>=1.0
  - pip
  - pip:
      - causalinference>=0.1.2  # 因果推断库
```

### 项目结构

```
causal-marca/
├── README.md
├── pyproject.toml
├── environment.yml
│
├── data/
│   ├── raw/                    # 原始数据集
│   │   ├── microrca/
│   │   └── aiops_challenge/
│   ├── processed/              # 预处理后数据
│   └── synthetic/              # 合成数据生成器
│
├── src/
│   ├── __init__.py
│   │
│   ├── graph/                  # 图模块
│   │   ├── __init__.py
│   │   ├── dependency_graph.py # 静态依赖图
│   │   ├── causal_graph.py     # 动态因果图
│   │   └── dual_layer.py       # 双层图结构
│   │
│   ├── causal/                 # 因果发现模块
│   │   ├── __init__.py
│   │   ├── granger.py          # Granger 因果检验
│   │   ├── neural_granger.py   # Neural Granger (GPU)
│   │   └── notears.py          # NOTEARS (备选)
│   │
│   ├── agents/                 # 多智能体模块
│   │   ├── __init__.py
│   │   ├── base_agent.py       # 智能体基类
│   │   ├── coordinator.py      # 协调智能体
│   │   ├── metrics_agent.py    # 监控智能体
│   │   ├── logs_agent.py       # 日志智能体
│   │   ├── traces_agent.py     # 追踪智能体
│   │   └── cahp_protocol.py    # CAHP 协作协议
│   │
│   ├── strategy/               # 推理策略模块
│   │   ├── __init__.py
│   │   ├── fault_classifier.py # 故障模式分类
│   │   ├── strategy_selector.py# 策略选择器
│   │   └── dynamic_adjust.py   # 动态调整器
│   │
│   ├── evaluation/             # 评估模块
│   │   ├── __init__.py
│   │   ├── metrics.py          # 评估指标
│   │   ├── baselines.py        # 基线方法
│   │   └── ablation.py         # 消融实验
│   │
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── data_loader.py      # 数据加载
│       └── visualization.py    # 可视化
│
├── experiments/                # 实验配置
│   ├── config.yaml             # 主配置
│   ├── microrca_experiment.yaml
│   └── ablation_experiments.yaml
│
├── notebooks/                  # Jupyter  notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_causal_graph_demo.ipynb
│   ├── 03_agent_collaboration_demo.ipynb
│   └── 04_results_analysis.ipynb
│
├── results/                    # 实验结果
│   ├── logs/                   # 运行日志
│   ├── metrics/                # 评估指标
│   ├── figures/                # 图表
│   └── reports/                # 报告
│
└── tests/                      # 单元测试
    ├── test_graph.py
    ├── test_causal.py
    ├── test_agents.py
    └── test_strategy.py
```

---

## 3.2 数据集准备计划

### MicroRCA 数据集

**来源**: https://github.com/NetManAIOps/MicroRCA

**数据规模**:
- 100+ 故障实例
- 3 种微服务架构（BookInfo、SockShop、Online Boutique）
- 故障类型：性能下降、错误率上升、级联故障

**数据格式**:
```python
# 每个故障实例
{
    "fault_id": "fault_001",
    "architecture": "bookinfo",
    "fault_type": "cpu_hog",
    "root_cause_service": "product-page",
    "root_cause_type": "resource_exhaustion",
    "timestamp_start": "2024-01-01T10:00:00Z",
    "timestamp_end": "2024-01-01T10:30:00Z",
    "metrics": {...},      # 时间序列指标
    "logs": [...],         # 日志列表
    "traces": [...]        # 调用链数据
}
```

**准备步骤**:
1. [ ] 克隆 MicroRCA 仓库
2. [ ] 下载预处理数据
3. [ ] 编写数据加载器（`src/utils/data_loader.py`）
4. [ ] 数据探索性分析（notebook 01）
5. [ ] 划分训练/验证/测试集（70/15/15）

### AIOps Challenge 2023

**来源**: https://www.aiops-challenge.com/

**数据规模**:
- 50+ 故障实例
- 真实生产环境数据
- 多样化故障模式

**注意**: 需要注册并同意数据使用协议

### 合成数据生成器

**目的**: 生成可控变量的测试数据，用于消融实验

**设计**:
```python
class SyntheticDataGenerator:
    """合成故障数据生成器"""
    
    def __init__(self, architecture_config):
        self.arch = architecture_config
        self.dependency_graph = self._build_dependency_graph()
        
    def generate_fault(
        self, 
        fault_type: str,
        root_cause_service: str,
        severity: float,
        duration_min: int
    ) -> FaultInstance:
        """
        生成单个故障实例
        
        Args:
            fault_type: 故障类型 (cpu/memory/latency/error)
            root_cause_service: 根因服务
            severity: 严重程度 (0-1)
            duration_min: 持续时间 (分钟)
        
        Returns:
            FaultInstance: 包含指标、日志、追踪的故障实例
        """
        # 1. 注入故障到根因服务
        # 2. 根据依赖图传播故障
        # 3. 生成观测数据（指标 + 日志 + 追踪）
        # 4. 添加噪声
        pass
    
    def generate_dataset(
        self, 
        num_faults: int,
        fault_type_distribution: Dict[str, float]
    ) -> List[FaultInstance]:
        """生成故障数据集"""
        pass
```

---

## 3.3 基线方法复现计划

### 基线 1: Standard RAG

**实现**: 使用 LangChain 默认 RAG 流程

```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFacePipeline

def baseline_standard_rag(query, context_data):
    # 1. 将所有日志/指标转为文本
    # 2. 构建向量索引
    # 3. 检索相关上下文
    # 4. LLM 生成答案
    pass
```

**预期性能**: Top-1 Accuracy ~50-60%

### 基线 2: Graph-RAG（前期研究）

**实现**: 基于前期研究的图约束单智能体方法

```python
def baseline_graph_rag(query, context_data, dependency_graph):
    # 1. 使用依赖图剪枝检索空间
    # 2. 检索相关上下文
    # 3. 单智能体 LLM 推理
    pass
```

**预期性能**: Top-1 Accuracy ~65-70%

### 基线 3: mABC（复现）

**来源**: Zhang et al. (2024) arXiv:2404.xxxxx

**实现要点**:
- 多智能体架构
- 区块链启发式共识机制
- 无因果增强

**预期性能**: Top-1 Accuracy ~70-75%

### 基线 4: Random Forest

**实现**: sklearn 传统 ML 分类器

```python
from sklearn.ensemble import RandomForestClassifier

def baseline_random_forest(features, labels):
    # 1. 手工特征工程
    # 2. 训练 Random Forest
    # 3. 预测根因服务
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(features, labels)
    return clf
```

**预期性能**: Top-1 Accuracy ~60-65%

---

## 3.4 实验流程

### 主实验：性能对比

```python
def main_experiment():
    """主实验：对比所有方法"""
    
    # 1. 加载数据集
    test_data = load_dataset("microrca", split="test")
    
    # 2. 定义方法
    methods = {
        "Standard RAG": baseline_standard_rag,
        "Graph-RAG": baseline_graph_rag,
        "mABC": baseline_mabc,
        "Random Forest": baseline_rf,
        "CE-MARCA (Ours)": ce_marca_full
    }
    
    # 3. 运行实验
    results = {}
    for name, method in methods.items():
        print(f"Running {name}...")
        predictions = []
        for instance in test_data:
            pred = method(instance.query, instance.context)
            predictions.append(pred)
        
        # 4. 评估
        metrics = evaluate(predictions, test_data.ground_truth)
        results[name] = metrics
    
    # 5. 输出结果
    print_results_table(results)
    plot_comparison_chart(results)
    
    return results
```

### 消融实验

```python
def ablation_study():
    """消融实验：验证各组件贡献"""
    
    ablations = {
        "Full": ce_marca_full,
        "-Causal": ce_marca_without_causal,
        "-MultiAgent": ce_marca_single_agent,
        "-Dynamic": ce_marca_fixed_strategy,
        "-Diversity": ce_marca_no_diversity_bonus
    }
    
    results = {}
    for name, method in ablations.items():
        print(f"Running ablation: {name}...")
        # 运行实验...
        results[name] = metrics
    
    return results
```

### 案例研究

选择 3-5 个典型故障案例，详细分析：
1. **成功案例**：CE-MARCA 正确定位，基线失败
2. **失败案例**：CE-MARCA 也失败的案例，分析原因
3. **因果约束价值**：展示因果图如何避免幻觉

---

## 3.5 时间规划

| 任务 | 预计时间 | 状态 |
|------|----------|------|
| 环境搭建 | 0.5 天 | 🔄 进行中 |
| MicroRCA 数据准备 | 0.5 天 | ⏳ 待开始 |
| 合成数据生成器 | 1 天 | ⏳ 待开始 |
| 基线方法实现 | 1.5 天 | ⏳ 待开始 |
| CE-MARCA 实现 | 2 天 | ⏳ 待开始 |
| 主实验运行 | 0.5 天 | ⏳ 待开始 |
| 消融实验运行 | 0.5 天 | ⏳ 待开始 |
| 结果分析与可视化 | 1 天 | ⏳ 待开始 |

**Phase 3 总计**: 约 7 天

---

## Phase 3 检查清单

- [x] 3.1 实验环境搭建方案
- [x] 3.2 数据集准备计划
- [x] 3.3 基线方法复现计划
- [x] 3.4 实验流程设计
- [x] 3.5 时间规划

**下一步**: Phase 4 - 实现与验证
