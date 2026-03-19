"""
静态依赖图模块

从服务注册表、配置文件或历史追踪数据加载服务调用关系
"""

import json
import networkx as nx
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class DependencyGraph:
    """静态服务依赖图"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_service(self, service_id: str, metadata: Optional[Dict] = None):
        """添加服务节点"""
        self.graph.add_node(service_id, **(metadata or {}))
        
    def add_dependency(
        self, 
        source: str, 
        target: str,
        call_frequency: Optional[float] = None,
        protocol: Optional[str] = None
    ):
        """
        添加服务依赖边（source 调用 target）
        
        Args:
            source: 调用方服务
            target: 被调用方服务
            call_frequency: 调用频率（次/秒）
            protocol: 通信协议（HTTP/gRPC 等）
        """
        self.graph.add_edge(
            source, target,
            call_frequency=call_frequency,
            protocol=protocol
        )
        
    def load_from_json(self, path: str):
        """从 JSON 文件加载依赖图"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        # 添加节点
        for service in data.get("services", []):
            self.add_service(service["id"], service.get("metadata"))
        
        # 添加边
        for dep in data.get("dependencies", []):
            self.add_dependency(
                dep["source"],
                dep["target"],
                dep.get("call_frequency"),
                dep.get("protocol")
            )
            
        return self
    
    def load_from_microservices_config(self, config_path: str):
        """从微服务配置文件加载"""
        # 实现根据具体配置格式调整
        pass
        
    def get_upstream_services(self, service_id: str) -> List[str]:
        """获取上游服务（调用该服务的服务）"""
        return list(self.graph.predecessors(service_id))
    
    def get_downstream_services(self, service_id: str) -> List[str]:
        """获取下游服务（该服务调用的服务）"""
        return list(self.graph.successors(service_id))
    
    def get_all_services(self) -> List[str]:
        """获取所有服务"""
        return list(self.graph.nodes())
    
    def get_candidate_causal_pairs(self) -> List[Tuple[str, str]]:
        """
        获取候选因果对
        
        基于依赖图剪枝：只考虑有直接调用关系的服务对
        这可以显著减少 Granger 因果检验的计算量
        """
        return list(self.graph.edges())
    
    def has_path(self, source: str, target: str) -> bool:
        """检查是否存在从 source 到 target 的路径"""
        return nx.has_path(self.graph, source, target)
    
    def get_shortest_path(self, source: str, target: str) -> List[str]:
        """获取最短调用路径"""
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return []
    
    def to_dict(self) -> Dict:
        """导出为字典"""
        return {
            "services": list(self.graph.nodes()),
            "dependencies": [
                {"source": u, "target": v, **data}
                for u, v, data in self.graph.edges(data=True)
            ]
        }
    
    def save_to_json(self, path: str):
        """保存到 JSON 文件"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @property
    def num_services(self) -> int:
        """服务数量"""
        return self.graph.number_of_nodes()
    
    @property
    def num_dependencies(self) -> int:
        """依赖关系数量"""
        return self.graph.number_of_edges()
    
    def __repr__(self):
        return f"DependencyGraph(services={self.num_services}, dependencies={self.num_dependencies})"
