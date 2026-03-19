#!/usr/bin/env python3
"""
合成数据生成器

生成模拟的 MicroRCA 数据集用于演示和测试
"""

import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta


class SyntheticDataGenerator:
    """合成故障数据生成器"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        
        # 定义 3 种架构
        self.architectures = {
            "BookInfo": {
                "services": ["api-gateway", "product-page", "details", "reviews", "ratings", "mongodb"],
                "dependencies": [
                    ("api-gateway", "product-page"),
                    ("product-page", "details"),
                    ("product-page", "reviews"),
                    ("reviews", "ratings"),
                    ("ratings", "mongodb")
                ]
            },
            "SockShop": {
                "services": ["front-end", "catalogue", "orders", "payment", "shipping", "user", "cart", "mongodb"],
                "dependencies": [
                    ("front-end", "catalogue"),
                    ("front-end", "orders"),
                    ("orders", "payment"),
                    ("orders", "shipping"),
                    ("front-end", "user"),
                    ("front-end", "cart")
                ]
            },
            "OnlineBoutique": {
                "services": ["frontend", "product-catalog", "recommendation", "cart", "checkout", "payment", "shipping", "currency", "redis"],
                "dependencies": [
                    ("frontend", "product-catalog"),
                    ("frontend", "recommendation"),
                    ("frontend", "cart"),
                    ("cart", "checkout"),
                    ("checkout", "payment"),
                    ("checkout", "shipping"),
                    ("product-catalog", "redis")
                ]
            }
        }
        
        # 故障类型
        self.fault_types = [
            "cpu_hog",
            "memory_leak",
            "network_latency",
            "service_error",
            "cascade_failure"
        ]
    
    def generate_time_series(
        self,
        length: int = 100,
        baseline: float = 50.0,
        anomaly_start: int = 70,
        anomaly_magnitude: float = 40.0,
        noise: float = 5.0
    ) -> List[float]:
        """生成带异常的时间序列"""
        series = []
        for t in range(length):
            if t < anomaly_start:
                # 正常阶段
                value = baseline + np.random.randn() * noise
            else:
                # 异常阶段
                value = baseline + anomaly_magnitude + np.random.randn() * noise
            series.append(max(0, min(100, value)))  # 限制在 0-100
        return series
    
    def generate_metrics(
        self,
        services: List[str],
        root_cause: str,
        fault_type: str,
        length: int = 100
    ) -> Dict[str, Dict[str, List[float]]]:
        """生成指标数据"""
        metrics = {}
        
        for service in services:
            # 基础值
            base_cpu = 30 + random.random() * 20
            base_memory = 40 + random.random() * 20
            base_latency = 100 + random.random() * 50
            base_error_rate = 0.1 + random.random() * 0.2
            
            # 判断是否受影响（根因或服务下游）
            is_affected = (service == root_cause)
            
            # 默认值
            cpu_delta = 5
            memory_delta = 5
            latency_delta = 20
            error_delta = 0.1
            
            # 如果是根因服务，异常更明显
            if is_affected:
                if fault_type == "cpu_hog":
                    cpu_delta = 50
                    latency_delta = 200
                elif fault_type == "memory_leak":
                    cpu_delta = 20
                    memory_delta = 40
                    latency_delta = 150
                elif fault_type == "network_latency":
                    cpu_delta = 10
                    latency_delta = 400
                elif fault_type == "service_error":
                    error_delta = 10
                    latency_delta = 100
                else:  # cascade_failure
                    cpu_delta = 40
                    memory_delta = 30
                    latency_delta = 300
            
            metrics[service] = {
                "cpu_usage": self.generate_time_series(
                    length, base_cpu, 70, cpu_delta if is_affected or fault_type == "cpu_hog" else 5
                ),
                "memory_usage": self.generate_time_series(
                    length, base_memory, 70, memory_delta if 'memory_delta' in dir() else 10
                ),
                "latency_p99": self.generate_time_series(
                    length, base_latency, 70, latency_delta, noise=20
                ),
                "error_rate": self.generate_time_series(
                    length, base_error_rate, 70, error_delta if 'error_delta' in dir() else 0.1, noise=0.05
                )
            }
        
        return metrics
    
    def generate_logs(
        self,
        services: List[str],
        root_cause: str,
        fault_type: str,
        num_logs: int = 50
    ) -> Dict[str, List[Dict[str, Any]]]:
        """生成日志数据"""
        logs = {}
        
        error_messages = {
            "cpu_hog": ["CPU usage critical", "Processing slow", "Timeout waiting for response"],
            "memory_leak": ["Out of memory", "GC overhead limit exceeded", "Heap space exhausted"],
            "network_latency": ["Connection timeout", "Network unreachable", "Request timed out"],
            "service_error": ["Internal server error", "Service unavailable", "Exception thrown"],
            "cascade_failure": ["Downstream service failed", "Circuit breaker open", "Fallback triggered"]
        }
        
        for service in services:
            service_logs = []
            is_root = (service == root_cause)
            
            # 生成日志
            for i in range(num_logs):
                if is_root and random.random() < 0.3:
                    # 根因服务有更多错误日志
                    level = random.choice(["error", "error", "warn", "info"])
                    message = random.choice(error_messages.get(fault_type, ["Error occurred"]))
                else:
                    level = random.choice(["info", "info", "info", "warn"])
                    message = "Request processed successfully"
                
                service_logs.append({
                    "timestamp": (datetime.now() - timedelta(minutes=num_logs-i)).isoformat(),
                    "level": level,
                    "message": message,
                    "service": service
                })
            
            logs[service] = service_logs
        
        return logs
    
    def generate_traces(
        self,
        services: List[str],
        dependencies: List[tuple],
        root_cause: str,
        fault_type: str,
        num_traces: int = 20
    ) -> List[Dict[str, Any]]:
        """生成追踪数据"""
        traces = []
        
        for i in range(num_traces):
            trace_id = f"trace_{i:04d}"
            spans = []
            
            # 构建调用链
            current_services = [services[0]]  # 从入口服务开始
            visited = set()
            
            for step in range(min(5, len(services))):
                current = current_services[-1]
                if current in visited:
                    break
                visited.add(current)
                
                # 基础延迟
                if current == root_cause:
                    if fault_type == "network_latency":
                        duration = 1500 + random.random() * 1000
                    elif fault_type == "cpu_hog":
                        duration = 800 + random.random() * 500
                    else:
                        duration = 500 + random.random() * 300
                else:
                    duration = 50 + random.random() * 100
                
                spans.append({
                    "trace_id": trace_id,
                    "span_id": f"span_{step}",
                    "service": current,
                    "operation": f"{current}/handle",
                    "duration_ms": duration,
                    "timestamp": (datetime.now() - timedelta(seconds=num_traces-i)).isoformat()
                })
                
                # 找到下游服务
                downstream = [t[1] for t in dependencies if t[0] == current]
                if downstream:
                    current_services.append(random.choice(downstream))
                else:
                    break
            
            traces.append({
                "trace_id": trace_id,
                "spans": spans
            })
        
        return traces
    
    def generate_fault(
        self,
        arch_name: str,
        fault_id: int
    ) -> Dict[str, Any]:
        """生成单个故障实例"""
        arch = self.architectures[arch_name]
        services = arch["services"]
        dependencies = arch["dependencies"]
        
        # 随机选择根因和故障类型
        root_cause = random.choice(services)
        fault_type = random.choice(self.fault_types)
        
        # 生成数据
        metrics = self.generate_metrics(services, root_cause, fault_type)
        logs = self.generate_logs(services, root_cause, fault_type)
        traces = self.generate_traces(services, dependencies, root_cause, fault_type)
        
        # 构建故障实例
        fault = {
            "fault_id": f"{arch_name.lower().replace(' ', '')}_{fault_id:03d}",
            "architecture": arch_name,
            "fault_type": fault_type,
            "root_cause_service": root_cause,
            "root_cause_type": fault_type,
            "timestamp_start": (datetime.now() - timedelta(hours=1)).isoformat(),
            "timestamp_end": datetime.now().isoformat(),
            "metrics": metrics,
            "logs": logs,
            "traces": traces,
            "ground_truth": {
                "root_cause": root_cause,
                "fault_type": fault_type,
                "affected_services": [root_cause]  # 简化
            }
        }
        
        return fault
    
    def generate_dataset(
        self,
        faults_per_arch: int = 40,
        output_dir: str = "data/processed"
    ):
        """生成完整数据集"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        all_faults = []
        
        print("Generating synthetic faults...")
        for arch_name in self.architectures.keys():
            print(f"  {arch_name}: {faults_per_arch} faults")
            for i in range(faults_per_arch):
                fault = self.generate_fault(arch_name, i)
                all_faults.append(fault)
        
        # 保存所有故障
        with open(output_path / "all_faults.json", 'w') as f:
            json.dump(all_faults, f, indent=2)
        
        # 划分数据集
        random.shuffle(all_faults)
        n = len(all_faults)
        train_end = int(n * 0.7)
        val_end = int(n * 0.85)
        
        splits = {
            "train": all_faults[:train_end],
            "val": all_faults[train_end:val_end],
            "test": all_faults[val_end:]
        }
        
        for split_name, split_data in splits.items():
            with open(output_path / f"{split_name}.json", 'w') as f:
                json.dump(split_data, f, indent=2)
        
        # 生成依赖图
        dep_graph = {
            "services": [],
            "dependencies": []
        }
        for arch in self.architectures.values():
            dep_graph["services"].extend(arch["services"])
            dep_graph["dependencies"].extend(arch["dependencies"])
        
        dep_graph["services"] = list(set(dep_graph["services"]))
        
        with open(output_path / "dependency_graph.json", 'w') as f:
            json.dump(dep_graph, f, indent=2)
        
        # 保存统计信息
        stats = {
            "total_faults": len(all_faults),
            "train_faults": len(splits["train"]),
            "val_faults": len(splits["val"]),
            "test_faults": len(splits["test"]),
            "architectures": list(self.architectures.keys()),
            "fault_types": self.fault_types
        }
        
        with open(output_path / "statistics.json", 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\nGenerated {len(all_faults)} synthetic faults")
        print(f"Saved to {output_dir}")
        print(f"Statistics: {json.dumps(stats, indent=2)}")


def main():
    print("=" * 60)
    print("Synthetic Data Generator for CE-MARCA")
    print("=" * 60)
    
    generator = SyntheticDataGenerator(seed=42)
    generator.generate_dataset(
        faults_per_arch=40,
        output_dir="data/processed"
    )
    
    print("\n" + "=" * 60)
    print("Data generation completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
