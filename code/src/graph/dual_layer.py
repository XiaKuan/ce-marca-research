"""
双层图结构

融合静态依赖图和动态因果图
"""

import json
from typing import Dict, List, Optional, Tuple
from .dependency_graph import DependencyGraph
from .causal_graph import CausalGraph, CausalEdge


class DualLayerGraph:
    """
    双层图结构
    
    Layer 1: 静态依赖图（服务调用关系）
    Layer 2: 动态因果图（Granger 因果关系）
    """
    
    def __init__(
        self,
        dependency_graph: Optional[DependencyGraph] = None,
        causal_graph: Optional[CausalGraph] = None
    ):
        self.dependency_graph = dependency_graph or DependencyGraph()
        self.causal_graph = causal_graph or CausalGraph()
        
    def load_dependency_graph(self, path: str):
        """加载静态依赖图"""
        self.dependency_graph.load_from_json(path)
        return self
    
    def build_causal_graph(
        self,
        metrics_data,
        metric_column: str = "latency_p99"
    ):
        """构建动态因果图"""
        import pandas as pd
        
        if isinstance(metrics_data, str):
            # 从文件加载
            metrics_data = pd.read_csv(metrics_data)
        
        self.causal_graph.build_from_metrics(
            metrics_data,
            self.dependency_graph,
            metric_column
        )
        return self
    
    def get_constrained_search_space(self, target_service: str) -> List[str]:
        """
        获取约束搜索空间
        
        基于依赖图和因果图的交集，减少根因搜索范围
        
        Args:
            target_service: 目标服务（出现异常的服务）
        
        Returns:
            候选根因服务列表
        """
        # 1. 从依赖图获取上游服务
        dep_upstream = set(self.dependency_graph.get_upstream_services(target_service))
        
        # 2. 从因果图获取因果邻居
        causal_upstream = set(self.causal_graph.get_causal_neighbors(target_service))
        
        # 3. 取交集（既在依赖图上游，又有因果关系的）
        # 这可以显著减少搜索空间
        constrained_candidates = dep_upstream.intersection(causal_upstream)
        
        # 4. 如果交集为空，回退到依赖图上游
        if not constrained_candidates:
            constrained_candidates = dep_upstream
        
        return list(constrained_candidates)
    
    def get_causal_strength(self, source: str, target: str) -> float:
        """获取因果强度"""
        if self.causal_graph.graph.has_edge(source, target):
            return self.causal_graph.graph.edges[source, target]['strength']
        return 0.0
    
    def is_dependency_exists(self, source: str, target: str) -> bool:
        """检查依赖关系是否存在"""
        return self.dependency_graph.graph.has_edge(source, target)
    
    def validate_causal_edge(self, source: str, target: str) -> bool:
        """
        验证因果边的有效性
        
        有效的因果边应该：
        1. 在因果图中显著
        2. 在依赖图中有路径支持（可选，但推荐）
        """
        # 检查因果图
        if not self.causal_graph.graph.has_edge(source, target):
            return False
        
        # 检查依赖图（可选约束）
        # 有些因果关系可能跨越多个服务跳数
        if not self.dependency_graph.has_path(source, target):
            # 如果没有直接依赖，但有因果关系，可能是间接影响
            pass
        
        return True
    
    def extract_full_causal_path(
        self,
        root_cause: str,
        affected_service: str
    ) -> List[Dict]:
        """
        提取完整因果路径（包含依赖和因果信息）
        
        Returns:
            路径列表，每项包含服务信息和因果强度
        """
        # 获取因果路径
        causal_path = self.causal_graph.extract_causal_path(root_cause, affected_service)
        
        if not causal_path:
            return []
        
        # 构建详细路径
        detailed_path = []
        for i, service in enumerate(causal_path):
            node_info = {
                "service": service,
                "order": i,
                "is_root_cause": (i == 0),
                "is_affected": (i == len(causal_path) - 1)
            }
            
            # 添加与前一个节点的因果强度
            if i > 0:
                prev_service = causal_path[i - 1]
                node_info["causal_strength"] = self.get_causal_strength(
                    prev_service, service
                )
                node_info["has_dependency"] = self.is_dependency_exists(
                    prev_service, service
                )
            
            detailed_path.append(node_info)
        
        return detailed_path
    
    def get_graph_statistics(self) -> Dict:
        """获取图统计信息"""
        return {
            "num_services": self.dependency_graph.num_services,
            "num_dependencies": self.dependency_graph.num_dependencies,
            "num_causal_edges": self.causal_graph.num_edges,
            "causal_graph_density": self.causal_graph.density,
            "dependency_graph_density": self.dependency_graph.graph.density()
        }
    
    def to_dict(self) -> Dict:
        """导出为字典"""
        return {
            "dependency_graph": self.dependency_graph.to_dict(),
            "causal_graph": self.causal_graph.to_dict(),
            "statistics": self.get_graph_statistics()
        }
    
    def save_to_json(self, path: str):
        """保存到 JSON 文件"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_json(cls, path: str) -> "DualLayerGraph":
        """从 JSON 文件加载"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        instance = cls()
        
        # 重建依赖图
        dep_data = data["dependency_graph"]
        for service in dep_data["services"]:
            instance.dependency_graph.add_service(service)
        for dep in dep_data["dependencies"]:
            instance.dependency_graph.add_dependency(
                dep["source"], dep["target"],
                dep.get("call_frequency"),
                dep.get("protocol")
            )
        
        # 重建因果图
        causal_data = data["causal_graph"]
        instance.causal_graph.significance_level = causal_data.get("significance_level", 0.05)
        instance.causal_graph.max_lag = causal_data.get("max_lag", 5)
        for edge_data in causal_data["edges"]:
            edge = CausalEdge(
                source=edge_data["source"],
                target=edge_data["target"],
                strength=edge_data["strength"],
                p_value=edge_data["p_value"],
                is_significant=edge_data["is_significant"],
                lag=edge_data.get("lag", 5)
            )
            instance.causal_graph.add_edge(edge)
        
        return instance
    
    def __repr__(self):
        return (
            f"DualLayerGraph("
            f"dep_services={self.dependency_graph.num_services}, "
            f"dep_edges={self.dependency_graph.num_dependencies}, "
            f"causal_edges={self.causal_graph.num_edges})"
        )
