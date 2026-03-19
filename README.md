# CE-MARCA Research Project

**项目名称**：基于因果增强多智能体协作的动态微服务根因推理方法

**英文名称**：CE-MARCA: Causal-Enhanced Multi-Agent Root Cause Analysis for Microservices

**创建时间**：2026-03-19

**状态**：Active

---

## 📁 项目结构

```
ce-marca-research/
├── README.md                    # 项目说明
├── LICENSE                      # 开源许可证
├── .gitignore                   # Git 忽略文件
│
├── paper/                       # 论文文档
│   ├── 00-abstract-polished.md
│   ├── 01-introduction-polished.md
│   ├── 02-related-work-polished.md
│   ├── 03-methodology-polished.md
│   ├── 04-evaluation-polished.md
│   ├── 05-case-study-polished.md
│   ├── 06-discussion-polished.md
│   ├── 07-conclusion-polished.md
│   ├── 08-appendix.md
│   ├── references.md
│   ├── progress.md
│   ├── polishing-checklist.md
│   ├── polishing-progress.md
│   └── POLISHING_COMPLETE.md
│
├── code/                        # 源代码（从 causal-marca 复制）
│   ├── src/
│   ├── experiments/
│   ├── tests/
│   ├── scripts/
│   ├── data/
│   ├── results/
│   ├── README.md
│   ├── environment.yml
│   └── pyproject.toml
│
├── docs/                        # 项目文档
│   ├── PROJECT_SUMMARY.md       # 项目总结
│   ├── timeline.md              # 时间线
│   ├── notes/                   # 研究笔记
│   └── decisions/               # 决策记录
│
├── temp/                        # 临时文件（不提交到 Git）
│   ├── 论文大纲.md
│   ├── phase1-文献调研.md
│   ├── phase2-方法设计.md
│   ├── phase3-实验设计.md
│   └── 因果增强多智能体 RCA-计划.md
│
└── memory/                      # 研究记忆
    └── 2026-03-19.md
```

---

## 🎯 研究目标

开发 CE-MARCA 框架，通过因果增强和多智能体协作实现准确、高效的微服务根因分析。

**核心创新**：
1. 双层图结构（静态依赖 + 动态因果）
2. CAHP 多智能体协作协议
3. 动态推理策略（5 种故障模式自适应）

---

## 📊 研究成果

### 代码
- **代码量**：~4,300 行
- **模块**：图模块、多智能体、策略、工具
- **测试**：单元测试覆盖核心功能

### 论文
- **字数**：~48,400 字（100% 润色完成）
- **章节**：8 章 + 参考文献 + 附录
- **图表**：7 个核心图表

### 实验
- **主实验**：77.78% 准确率，3200 倍效率提升
- **消融实验**：验证各组件贡献
- **数据集**：120 个合成故障实例

---

## 📅 时间线

| 阶段 | 内容 | 耗时 | 完成时间 |
|------|------|------|----------|
| Phase 1 | 文献调研与问题定义 | 15 分钟 | 10:37 |
| Phase 2 | 方法设计 | 20 分钟 | 10:45 |
| Phase 3 | 实验设计 | 15 分钟 | 10:50 |
| Phase 4 | 实现与验证 | 45 分钟 | 11:30 |
| Phase 5 | 论文撰写 | 60 分钟 | 12:00 |
| 实验运行 | 主实验 + 消融实验 | 30 分钟 | 12:30 |
| 图表生成 | 7 个图表 | 15 分钟 | 12:45 |
| 论文润色 | 8 章节 | 60 分钟 | 13:00 |
| **总计** | **完整项目** | **~4 小时** | **13:00** |

---

## 🎓 投稿计划

**目标会议/期刊**：
1. **ICSE 2026** (软件工程顶会) - 截稿：2025-09-15
2. **KDD 2026** (数据挖掘顶会) - 截稿：2026-02
3. **IEEE TSE** (软件工程顶刊) - 滚动截稿

**首选**：ICSE 2026

---

## 📦 依赖项

### 软件依赖
- Python 3.10+
- NetworkX 3.4.2
- Scikit-learn 1.7.2
- Statsmodels 0.14.6
- Matplotlib 3.10.8
- Pandas 2.0+
- NumPy 1.24+

### 工具依赖
- Git 2.34.1+
- ClawHub CLI (for skills)

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd ce-marca-research
```

### 2. 安装依赖
```bash
cd code
conda env create -f environment.yml
conda activate causal-marca
```

### 3. 生成数据
```bash
python scripts/generate_synthetic_data.py
```

### 4. 运行实验
```bash
python experiments/run_experiment_simple.py
python experiments/run_ablation_study_simple.py
```

### 5. 生成图表
```bash
python scripts/generate_figures.py
```

---

## 📄 许可证

MIT License

---

## 👥 团队

- **研究助理**：科研助手 · 严谨专业版
- **用户**：用户 E4EB

---

## 📬 联系方式

- **代码仓库**：[待添加]
- **论文**：[待提交]

---

**最后更新**：2026-03-19
