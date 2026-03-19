# CE-MARCA: Causal-Enhanced Multi-Agent Root Cause Analysis

基于因果增强多智能体协作的动态微服务根因推理方法

## 安装

```bash
# 创建 conda 环境
conda env create -f environment.yml
conda activate causal-marca

# 或者使用 pip
pip install -e .
```

## 快速开始

```python
from causal_marca import CEMARCA

# 初始化
marca = CEMARCA(
    dependency_graph_path="data/dependency_graph.json",
    llm_model="Qwen/Qwen2.5-7B-Instruct"
)

# 运行根因分析
report = marca.analyze(
    anomaly_timestamp="2024-01-01T10:00:00Z",
    metrics_window="30min",
    logs_window="30min",
    traces_window="30min"
)

# 查看结果
print(f"根因服务：{report.root_cause_service}")
print(f"置信度：{report.confidence}")
print(f"因果路径：{report.causal_path}")
```

## 项目结构

```
causal-marca/
├── src/
│   ├── graph/           # 图模块（依赖图、因果图）
│   ├── causal/          # 因果发现（Granger、Neural Granger）
│   ├── agents/          # 多智能体（协调器、监控、日志、追踪）
│   ├── strategy/        # 推理策略（故障分类、策略选择）
│   ├── evaluation/      # 评估（指标、基线、消融实验）
│   └── utils/           # 工具（数据加载、可视化）
├── data/                # 数据集
├── experiments/         # 实验配置
├── notebooks/           # Jupyter notebooks
├── results/             # 实验结果
└── tests/               # 单元测试
```

## 核心组件

### 1. 双层图结构

- **静态依赖图**：服务调用关系（架构知识）
- **动态因果图**：Granger 因果关系（运行时学习）

### 2. 多智能体协作（CAHP 协议）

- **协调智能体**：全局协调、策略选择、结果聚合
- **监控智能体**：指标异常分析
- **日志智能体**：日志模式分析
- **追踪智能体**：调用链延迟分析

### 3. 动态推理策略

根据故障模式（性能下降、错误率上升、资源耗尽、级联故障、间歇性故障）自动调整推理策略。

## 实验

### 主实验

```bash
python -m experiments.run_main_experiment
```

### 消融实验

```bash
python -m experiments.run_ablation_study
```

## 许可证

MIT License
