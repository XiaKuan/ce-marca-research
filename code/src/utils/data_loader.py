"""
数据加载器：加载 MicroRCA 等数据集
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class FaultInstance:
    """故障实例"""
    fault_id: str
    architecture: str
    fault_type: str
    root_cause_service: str
    root_cause_type: str
    timestamp_start: str
    timestamp_end: str
    metrics: Dict[str, Any]
    logs: List[Dict[str, Any]]
    traces: List[Dict[str, Any]]
    ground_truth: Dict[str, Any]


class MicroRCALoader:
    """MicroRCA 数据集加载器"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
    def load_fault(self, fault_id: str) -> FaultInstance:
        """加载单个故障实例"""
        fault_path = self.data_dir / f"{fault_id}.json"
        
        if not fault_path.exists():
            raise FileNotFoundError(f"Fault {fault_id} not found")
        
        with open(fault_path, 'r') as f:
            data = json.load(f)
        
        return FaultInstance(
            fault_id=data["fault_id"],
            architecture=data.get("architecture", "unknown"),
            fault_type=data.get("fault_type", "unknown"),
            root_cause_service=data["root_cause_service"],
            root_cause_type=data.get("root_cause_type", "unknown"),
            timestamp_start=data["timestamp_start"],
            timestamp_end=data["timestamp_end"],
            metrics=data.get("metrics", {}),
            logs=data.get("logs", []),
            traces=data.get("traces", []),
            ground_truth=data.get("ground_truth", {})
        )
    
    def list_faults(self) -> List[str]:
        """列出所有故障 ID"""
        return [f.stem for f in self.data_dir.glob("*.json")]
    
    def load_all(self) -> List[FaultInstance]:
        """加载所有故障实例"""
        faults = []
        for fault_id in self.list_faults():
            try:
                faults.append(self.load_fault(fault_id))
            except Exception as e:
                print(f"Failed to load {fault_id}: {e}")
        return faults
    
    def get_faults_by_type(self, fault_type: str) -> List[FaultInstance]:
        """按故障类型筛选"""
        all_faults = self.load_all()
        return [f for f in all_faults if f.fault_type == fault_type]
    
    def get_faults_by_architecture(self, architecture: str) -> List[FaultInstance]:
        """按架构筛选"""
        all_faults = self.load_all()
        return [f for f in all_faults if f.architecture == architecture]
    
    def split_dataset(
        self,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42
    ):
        """划分训练/验证/测试集"""
        import random
        
        all_faults = self.load_all()
        random.seed(seed)
        random.shuffle(all_faults)
        
        n = len(all_faults)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        return {
            "train": all_faults[:train_end],
            "val": all_faults[train_end:val_end],
            "test": all_faults[val_end:]
        }


class MetricsDataLoader:
    """指标数据加载器"""
    
    @staticmethod
    def load_from_csv(csv_path: str) -> pd.DataFrame:
        """从 CSV 加载指标数据"""
        df = pd.read_csv(csv_path)
        
        # 确保必要的列存在
        required_cols = ["timestamp", "service_id", "metric_name", "value"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        return df
    
    @staticmethod
    def to_service_dict(df: pd.DataFrame, metric_column: str = "value") -> Dict[str, Dict]:
        """
        转换为服务字典格式
        
        Returns:
            {
                "service_id": {
                    "metric_name": [values...],
                    ...
                },
                ...
            }
        """
        services = {}
        
        for service_id in df["service_id"].unique():
            service_data = df[df["service_id"] == service_id]
            services[service_id] = {}
            
            for metric_name in service_data["metric_name"].unique():
                metric_data = service_data[service_data["metric_name"] == metric_name]
                services[service_id][metric_name] = metric_data[metric_column].tolist()
        
        return services


class LogsDataLoader:
    """日志数据加载器"""
    
    @staticmethod
    def load_from_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
        """从 JSONL 加载日志"""
        logs = []
        with open(jsonl_path, 'r') as f:
            for line in f:
                logs.append(json.loads(line))
        return logs
    
    @staticmethod
    def filter_by_service(logs: List[Dict], service_id: str) -> List[Dict]:
        """按服务筛选日志"""
        return [log for log in logs if log.get("service") == service_id]
    
    @staticmethod
    def filter_by_level(logs: List[Dict], level: str) -> List[Dict]:
        """按日志级别筛选"""
        return [log for log in logs if log.get("level") == level]


class TracesDataLoader:
    """追踪数据加载器"""
    
    @staticmethod
    def load_from_json(json_path: str) -> List[Dict[str, Any]]:
        """从 JSON 加载追踪数据"""
        with open(json_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def extract_spans(traces: List[Dict]) -> List[Dict]:
        """提取所有 spans"""
        spans = []
        for trace in traces:
            spans.extend(trace.get("spans", []))
        return spans
    
    @staticmethod
    def group_by_service(spans: List[Dict]) -> Dict[str, List[Dict]]:
        """按服务分组 spans"""
        grouped = {}
        for span in spans:
            service = span.get("service", "unknown")
            if service not in grouped:
                grouped[service] = []
            grouped[service].append(span)
        return grouped


def load_dependency_graph(graph_path: str) -> Dict[str, Any]:
    """加载依赖图"""
    with open(graph_path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    # 示例用法
    # loader = MicroRCALoader("data/raw/microrca")
    # faults = loader.load_all()
    # print(f"Loaded {len(faults)} faults")
    pass
