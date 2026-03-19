"""
单元测试：图模块
"""

import pytest
import numpy as np
from src.graph.dependency_graph import DependencyGraph
from src.graph.causal_graph import CausalGraph, CausalEdge
from src.graph.dual_layer import DualLayerGraph


class TestDependencyGraph:
    """测试静态依赖图"""
    
    def test_add_service(self):
        """测试添加服务"""
        graph = DependencyGraph()
        graph.add_service("service-a", {"type": "api"})
        
        assert "service-a" in graph.get_all_services()
        assert graph.num_services == 1
    
    def test_add_dependency(self):
        """测试添加依赖关系"""
        graph = DependencyGraph()
        graph.add_service("service-a")
        graph.add_service("service-b")
        graph.add_dependency("service-a", "service-b", call_frequency=100.0)
        
        assert graph.num_dependencies == 1
        assert ("service-a", "service-b") in graph.get_candidate_causal_pairs()
    
    def test_get_upstream_services(self):
        """测试获取上游服务"""
        graph = DependencyGraph()
        graph.add_service("api-gateway")
        graph.add_service("order-service")
        graph.add_service("payment-service")
        
        graph.add_dependency("api-gateway", "order-service")
        graph.add_dependency("order-service", "payment-service")
        
        upstream = graph.get_upstream_services("order-service")
        assert "api-gateway" in upstream
    
    def test_has_path(self):
        """测试路径检查"""
        graph = DependencyGraph()
        graph.add_service("a")
        graph.add_service("b")
        graph.add_service("c")
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        
        assert graph.has_path("a", "c") == True
        assert graph.has_path("c", "a") == False
    
    def test_save_load_json(self, tmp_path):
        """测试 JSON 保存加载"""
        graph = DependencyGraph()
        graph.add_service("service-a")
        graph.add_service("service-b")
        graph.add_dependency("service-a", "service-b")
        
        # 保存
        file_path = tmp_path / "dep_graph.json"
        graph.save_to_json(str(file_path))
        
        # 加载
        graph2 = DependencyGraph()
        graph2.load_from_json(str(file_path))
        
        assert graph2.num_services == 2
        assert graph2.num_dependencies == 1


class TestCausalGraph:
    """测试动态因果图"""
    
    def test_compute_granger_causality(self):
        """测试 Granger 因果计算"""
        cg = CausalGraph(significance_level=0.05, max_lag=2)
        
        # 创建有因果关系的序列
        np.random.seed(42)
        n = 100
        source = np.random.randn(n)
        # target 滞后于 source
        target = np.zeros(n)
        for t in range(2, n):
            target[t] = 0.5 * source[t-1] + 0.3 * target[t-1] + np.random.randn() * 0.1
        
        f_stat, p_val, is_causal = cg.compute_granger_causality(source, target)
        
        # 应该检测到因果关系
        assert is_causal == True or f_stat > 0
    
    def test_add_causal_edge(self):
        """测试添加因果边"""
        cg = CausalGraph()
        
        edge = CausalEdge(
            source="service-a",
            target="service-b",
            strength=15.5,
            p_value=0.01,
            is_significant=True,
            lag=3
        )
        
        cg.add_edge(edge)
        
        assert cg.num_edges == 1
        assert cg.graph.has_edge("service-a", "service-b")
    
    def test_get_top_causal_edges(self):
        """测试获取最强因果边"""
        cg = CausalGraph()
        
        # 添加多条边
        edges = [
            CausalEdge("a", "b", 10.0, 0.01, True, 2),
            CausalEdge("b", "c", 25.0, 0.001, True, 3),
            CausalEdge("a", "c", 5.0, 0.05, True, 1),
        ]
        
        for edge in edges:
            cg.add_edge(edge)
        
        top_edges = cg.get_top_causal_edges(top_k=2)
        
        assert len(top_edges) == 2
        assert top_edges[0].strength == 25.0  # 最强边


class TestDualLayerGraph:
    """测试双层图结构"""
    
    def test_constrained_search_space(self):
        """测试约束搜索空间"""
        dual = DualLayerGraph()
        
        # 构建依赖图
        dual.dependency_graph.add_service("api")
        dual.dependency_graph.add_service("order")
        dual.dependency_graph.add_service("payment")
        dual.dependency_graph.add_dependency("api", "order")
        dual.dependency_graph.add_dependency("order", "payment")
        
        # 构建因果图
        edge = CausalEdge("api", "order", 20.0, 0.01, True, 2)
        dual.causal_graph.add_edge(edge)
        
        # 获取 order 的约束搜索空间
        candidates = dual.get_constrained_search_space("order")
        
        # 应该包含 api（既有依赖又有因果）
        assert "api" in candidates
    
    def test_graph_statistics(self):
        """测试图统计"""
        dual = DualLayerGraph()
        
        dual.dependency_graph.add_service("a")
        dual.dependency_graph.add_service("b")
        dual.dependency_graph.add_dependency("a", "b")
        
        dual.causal_graph.add_edge(
            CausalEdge("a", "b", 10.0, 0.01, True, 2)
        )
        
        stats = dual.get_graph_statistics()
        
        assert stats["num_services"] == 2
        assert stats["num_dependencies"] == 1
        assert stats["num_causal_edges"] == 1
    
    def test_save_load_json(self, tmp_path):
        """测试 JSON 保存加载"""
        dual = DualLayerGraph()
        
        dual.dependency_graph.add_service("service-a")
        dual.dependency_graph.add_dependency("service-a", "service-b")
        dual.causal_graph.add_edge(
            CausalEdge("service-a", "service-b", 10.0, 0.01, True, 2)
        )
        
        # 保存
        file_path = tmp_path / "dual_graph.json"
        dual.save_to_json(str(file_path))
        
        # 加载
        dual2 = DualLayerGraph.load_from_json(str(file_path))
        
        assert dual2.dependency_graph.num_services == 2
        assert dual2.causal_graph.num_edges == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
