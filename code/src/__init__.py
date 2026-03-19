"""
CE-MARCA: Causal-Enhanced Multi-Agent Root Cause Analysis
"""

__version__ = "0.1.0"
__author__ = "Research Team"

# 简化导入，避免循环依赖
# from .graph.dual_layer import DualLayerGraph
# from .agents.coordinator import CoordinatorAgent
# from .core.cemarca import CEMARCA

__all__ = [
    "DualLayerGraph",
    "CoordinatorAgent",
    "CEMARCA",
]
