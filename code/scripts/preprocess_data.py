#!/usr/bin/env python3
"""
数据预处理脚本

将 MicroRCA 原始数据转换为 CE-MARCA 可用格式
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import random


def load_raw_faults(data_dir: str) -> List[Dict[str, Any]]:
    """加载原始故障数据"""
    faults = []
    data_path = Path(data_dir)
    
    for arch_dir in data_path.iterdir():
        if not arch_dir.is_dir():
            continue
        
        architecture = arch_dir.name
        print(f"Processing {architecture}...")
        
        for fault_file in arch_dir.glob("*.json"):
            with open(fault_file, 'r') as f:
                fault_data = json.load(f)
            
            fault_data['architecture'] = architecture
            faults.append(fault_data)
    
    print(f"Loaded {len(faults)} fault instances")
    return faults


def extract_dependency_graph(faults: List[Dict]) -> Dict[str, Any]:
    """从故障数据中提取依赖图"""
    services = set()
    dependencies = set()
    
    for fault in faults:
        metrics = fault.get('metrics', {})
        for service_id in metrics.keys():
            services.add(service_id)
        
        # 从追踪数据中提取依赖关系
        traces = fault.get('traces', [])
        for trace in traces:
            spans = trace.get('spans', [])
            for i in range(len(spans) - 1):
                caller = spans[i].get('service')
                callee = spans[i + 1].get('service')
                if caller and callee:
                    dependencies.add((caller, callee))
    
    graph = {
        "services": list(services),
        "dependencies": [
            {"source": s, "target": t}
            for s, t in dependencies
        ]
    }
    
    print(f"Extracted dependency graph: {len(services)} services, {len(dependencies)} dependencies")
    return graph


def split_dataset(faults: List[Dict], seed: int = 42) -> Dict[str, List[Dict]]:
    """划分数据集"""
    random.seed(seed)
    random.shuffle(faults)
    
    n = len(faults)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)
    
    return {
        "train": faults[:train_end],
        "val": faults[train_end:val_end],
        "test": faults[val_end:]
    }


def save_processed_data(
    faults: List[Dict],
    dep_graph: Dict,
    splits: Dict[str, List[Dict]],
    output_dir: str
):
    """保存处理后的数据"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存依赖图
    with open(output_path / "dependency_graph.json", 'w') as f:
        json.dump(dep_graph, f, indent=2)
    
    # 保存各数据集
    for split_name, split_data in splits.items():
        with open(output_path / f"{split_name}.json", 'w') as f:
            json.dump(split_data, f, indent=2)
    
    # 保存统计信息
    stats = {
        "total_faults": len(faults),
        "train_faults": len(splits["train"]),
        "val_faults": len(splits["val"]),
        "test_faults": len(splits["test"]),
        "num_services": len(dep_graph["services"]),
        "num_dependencies": len(dep_graph["dependencies"]),
        "architectures": list(set(f["architecture"] for f in faults))
    }
    
    with open(output_path / "statistics.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Saved processed data to {output_dir}")
    print(f"Statistics: {json.dumps(stats, indent=2)}")


def main():
    """主函数"""
    print("=" * 60)
    print("MicroRCA Data Preprocessing")
    print("=" * 60)
    
    raw_data_dir = "data/raw/MicroRCA"
    processed_data_dir = "data/processed"
    
    if not os.path.exists(raw_data_dir):
        print(f"Error: Raw data directory not found: {raw_data_dir}")
        print("Please download MicroRCA dataset first.")
        print("See: scripts/DATA_DOWNLOAD.md")
        return
    
    # Step 1: 加载原始数据
    print("\n[1/4] Loading raw faults...")
    faults = load_raw_faults(raw_data_dir)
    
    # Step 2: 提取依赖图
    print("\n[2/4] Extracting dependency graph...")
    dep_graph = extract_dependency_graph(faults)
    
    # Step 3: 划分数据集
    print("\n[3/4] Splitting dataset...")
    splits = split_dataset(faults)
    print(f"Train: {len(splits['train'])}, Val: {len(splits['val'])}, Test: {len(splits['test'])}")
    
    # Step 4: 保存处理后的数据
    print("\n[4/4] Saving processed data...")
    save_processed_data(faults, dep_graph, splits, processed_data_dir)
    
    print("\n" + "=" * 60)
    print("Preprocessing completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
