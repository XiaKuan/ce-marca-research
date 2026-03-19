"""
动态因果图模块

基于 Granger 因果检验从时间序列数据中学习因果关系
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import networkx as nx
from statsmodels.tsa.stattools import grangercausalitytests


@dataclass
class CausalEdge:
    """因果边"""
    source: str
    target: str
    strength: float  # F 统计量
    p_value: float
    is_significant: bool
    lag: int  # 最优滞后阶数
    
    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "strength": self.strength,
            "p_value": self.p_value,
            "is_significant": self.is_significant,
            "lag": self.lag
        }


class CausalGraph:
    """动态因果图"""
    
    def __init__(self, significance_level: float = 0.05, max_lag: int = 5):
        self.graph = nx.DiGraph()
        self.significance_level = significance_level
        self.max_lag = max_lag
        
    def add_edge(self, edge: CausalEdge):
        """添加因果边"""
        if edge.is_significant:
            self.graph.add_edge(
                edge.source, edge.target,
                strength=edge.strength,
                p_value=edge.p_value,
                lag=edge.lag
            )
    
    def compute_granger_causality(
        self,
        source_series: np.ndarray,
        target_series: np.ndarray,
        max_lag: Optional[int] = None
    ) -> Tuple[float, float, bool]:
        """
        计算 Granger 因果关系
        
        Args:
            source_series: 源服务时间序列（形状：[T]）
            target_series: 目标服务时间序列（形状：[T]）
            max_lag: 最大滞后阶数
        
        Returns:
            f_statistic: F 统计量（因果强度）
            p_value: 显著性 p 值
            is_causal: 是否存在因果关系
        """
        if max_lag is None:
            max_lag = self.max_lag
            
        # 构建二维数组 [T, 2]
        data = np.column_stack([target_series, source_series])
        
        try:
            # Granger 因果检验
            # 原假设：source 不 Granger 引起 target
            test_result = grangercausalitytests(data, maxlag=max_lag, verbose=False)
            
            # 获取最大滞后阶数的 F 统计量和 p 值
            max_lag_result = test_result[max_lag][0]  # 'ssr_ftest'
            f_statistic = max_lag_result[0]
            p_value = max_lag_result[1]
            
            is_causal = p_value < self.significance_level
            
            return f_statistic, p_value, is_causal
            
        except Exception as e:
            # 如果检验失败，返回无因果
            return 0.0, 1.0, False
    
    def build_from_metrics(
        self,
        metrics_data: pd.DataFrame,
        dependency_graph,
        metric_column: str = "latency_p99"
    ):
        """
        从指标数据构建因果图
        
        Args:
            metrics_data: 指标数据 DataFrame
                列：[timestamp, service_id, metric_value]
            dependency_graph: 静态依赖图（用于剪枝）
            metric_column: 使用的指标列名
        """
        # 获取候选因果对（基于依赖图剪枝）
        candidate_pairs = dependency_graph.get_candidate_causal_pairs()
        
        # 对每个候选对计算 Granger 因果
        for source, target in candidate_pairs:
            # 提取时间序列
            source_data = metrics_data[metrics_data["service_id"] == source]
            target_data = metrics_data[metrics_data["service_id"] == target]
            
            if len(source_data) == 0 or len(target_data) == 0:
                continue
            
            # 确保时间对齐
            source_series = source_data[metric_column].values
            target_series = target_data[metric_column].values
            
            min_len = min(len(source_series), len(target_series))
            if min_len < self.max_lag * 2:
                continue  # 数据量不足
            
            source_series = source_series[:min_len]
            target_series = target_series[:min_len]
            
            # 计算 Granger 因果
            f_stat, p_val, is_causal = self.compute_granger_causality(
                source_series, target_series
            )
            
            if is_causal:
                edge = CausalEdge(
                    source=source,
                    target=target,
                    strength=f_stat,
                    p_value=p_val,
                    is_significant=True,
                    lag=self.max_lag
                )
                self.add_edge(edge)
        
        return self
    
    def get_causal_neighbors(self, service_id: str, depth: int = 1) -> List[str]:
        """获取因果邻居（指定深度内）"""
        neighbors = set()
        current_level = {service_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # 上游邻居（可能的根因）
                predecessors = self.graph.predecessors(node)
                next_level.update(predecessors)
            neighbors.update(next_level)
            current_level = next_level
            
        return list(neighbors)
    
    def extract_causal_path(self, source: str, target: str) -> List[str]:
        """提取因果路径（按因果强度加权的最短路径）"""
        try:
            path = nx.shortest_path(
                self.graph,
                source=source,
                target=target,
                weight=lambda u, v, d: -d.get('strength', 1)  # 强度越大，权重越小
            )
            return path
        except nx.NetworkXNoPath:
            return []
    
    def get_top_causal_edges(self, top_k: int = 10) -> List[CausalEdge]:
        """获取最强的 K 条因果边"""
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edge = CausalEdge(
                source=u,
                target=v,
                strength=data['strength'],
                p_value=data['p_value'],
                is_significant=True,
                lag=data.get('lag', 1)
            )
            edges.append(edge)
        
        # 按强度排序
        edges.sort(key=lambda e: e.strength, reverse=True)
        return edges[:top_k]
    
    def to_dict(self) -> Dict:
        """导出为字典"""
        return {
            "nodes": list(self.graph.nodes()),
            "edges": [
                {"source": u, "target": v, **data}
                for u, v, data in self.graph.edges(data=True)
            ],
            "significance_level": self.significance_level,
            "max_lag": self.max_lag
        }
    
    @property
    def num_edges(self) -> int:
        """因果边数量"""
        return self.graph.number_of_edges()
    
    @property
    def density(self) -> float:
        """图密度"""
        return nx.density(self.graph)
    
    def __repr__(self):
        return f"CausalGraph(edges={self.num_edges}, density={self.density:.3f})"
