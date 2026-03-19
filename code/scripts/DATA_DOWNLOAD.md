# MicroRCA 数据集下载与准备

## 下载步骤

### 1. 克隆 MicroRCA 仓库

```bash
cd /home/admin/openclaw/workspace/causal-marca/data/raw
git clone https://github.com/NetManAIOps/MicroRCA.git
```

### 2. 数据集结构

下载后的目录结构：
```
data/raw/MicroRCA/
├── BookInfo/
│   ├── fault_001.json
│   ├── fault_002.json
│   └── ...
├── SockShop/
│   ├── fault_001.json
│   └── ...
├── OnlineBoutique/
│   ├── fault_001.json
│   └── ...
└── README.md
```

### 3. 数据预处理

运行预处理脚本：
```bash
cd /home/admin/openclaw/workspace/causal-marca
python scripts/preprocess_data.py
```

这将：
- 合并所有故障实例
- 生成依赖图 JSON
- 划分训练/验证/测试集

### 4. 验证数据

```bash
python scripts/verify_data.py
```

预期输出：
```
Loaded 120 fault instances
BookInfo: 40 faults
SockShop: 40 faults
Online Boutique: 40 faults
```

## 如果下载失败

### 镜像源
```bash
# 使用 Gitee 镜像
git clone https://gitee.com/mirror/MicroRCA.git
```

### 手动下载
1. 访问：https://github.com/NetManAIOps/MicroRCA
2. 点击 "Code" → "Download ZIP"
3. 解压到 `data/raw/` 目录

## 数据使用许可

- 许可证：MIT
- 用途：学术研究
- 引用：Li, Y., et al. "MicroRCA: A comprehensive benchmark for root cause analysis." AIOps Challenge, 2022.
