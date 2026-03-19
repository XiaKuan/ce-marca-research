"""
可视化工具
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path


class ResultsVisualizer:
    """结果可视化"""
    
    def __init__(self, output_dir: str = "results/figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置样式
        sns.set_style("whitegrid")
        plt.rcParams["font.size"] = 12
    
    def plot_accuracy_comparison(
        self,
        results: Dict[str, float],
        title: str = "Root Cause Analysis Accuracy Comparison",
        save_name: str = "accuracy_comparison.png"
    ):
        """
        绘制准确率对比图
        
        Args:
            results: {method_name: accuracy}
        """
        methods = list(results.keys())
        accuracies = list(results.values())
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(methods, accuracies, color='steelblue')
        
        # 添加数值标签
        for bar, acc in zip(bars, accuracies):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f'{acc:.1%}',
                ha='center',
                va='bottom',
                fontsize=10
            )
        
        plt.xlabel('Method')
        plt.ylabel('Top-1 Accuracy')
        plt.title(title)
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {save_path}")
    
    def plot_precision_recall(
        self,
        results: Dict[str, Dict[str, float]],
        title: str = "Precision@K Comparison",
        save_name: str = "precision_comparison.png"
    ):
        """
        绘制 Precision@K 对比图
        
        Args:
            results: {method_name: {"precision@1": val, "precision@3": val, ...}}
        """
        methods = list(results.keys())
        k_values = sorted([k for k in results[methods[0]].keys() if k.startswith("precision@")])
        
        x = np.arange(len(methods))
        width = 0.8 / len(k_values)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i, k in enumerate(k_values):
            values = [results[m][k] for m in methods]
            offset = (i - len(k_values) / 2 + 0.5) * width
            ax.bar(x + offset, values, width, label=f'{k}')
        
        ax.set_xlabel('Method')
        ax.set_ylabel('Precision')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(methods, rotation=45)
        ax.legend()
        ax.set_ylim(0, 1.0)
        
        plt.tight_layout()
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {save_path}")
    
    def plot_efficiency_comparison(
        self,
        results: Dict[str, Dict[str, float]],
        title: str = "Efficiency Comparison",
        save_name: str = "efficiency_comparison.png"
    ):
        """
        绘制效率对比图（推理步骤和 token 成本）
        
        Args:
            results: {method_name: {"avg_steps": val, "avg_tokens": val}}
        """
        methods = list(results.keys())
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 推理步骤
        steps = [results[m]["avg_steps"] for m in methods]
        bars1 = ax1.bar(methods, steps, color='coral')
        ax1.set_xlabel('Method')
        ax1.set_ylabel('Average Reasoning Steps')
        ax1.set_title('Reasoning Steps')
        
        for bar, step in zip(bars1, steps):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f'{step:.1f}',
                ha='center',
                va='bottom',
                fontsize=10
            )
        
        # Token 成本（归一化）
        tokens = [results[m]["avg_tokens"] for m in methods]
        max_tokens = max(tokens)
        normalized_tokens = [t / max_tokens for t in tokens]
        
        bars2 = ax2.bar(methods, normalized_tokens, color='teal')
        ax2.set_xlabel('Method')
        ax2.set_ylabel('Relative Token Cost (normalized)')
        ax2.set_title('Token Cost')
        ax2.set_ylim(0, 1.0)
        
        for bar, nt in zip(bars2, normalized_tokens):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f'{nt:.2f}',
                ha='center',
                va='bottom',
                fontsize=10
            )
        
        plt.suptitle(title)
        plt.tight_layout()
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {save_path}")
    
    def plot_ablation_study(
        self,
        results: Dict[str, float],
        full_method_name: str = "CE-MARCA (Full)",
        title: str = "Ablation Study",
        save_name: str = "ablation_study.png"
    ):
        """
        绘制消融实验图
        
        Args:
            results: {variant_name: accuracy}
        """
        variants = list(results.keys())
        accuracies = list(results.values())
        
        # 找出完整方法
        full_idx = variants.index(full_method_name) if full_method_name in variants else 0
        
        colors = ['steelblue'] * len(variants)
        colors[full_idx] = 'darkgreen'  # 完整方法用绿色突出
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(variants, accuracies, color=colors)
        
        # 添加数值标签
        for bar, acc in zip(bars, accuracies):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f'{acc:.1%}',
                ha='center',
                va='bottom',
                fontsize=10,
                rotation=45
            )
        
        plt.xlabel('Method Variant')
        plt.ylabel('Top-1 Accuracy')
        plt.title(title)
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {save_path}")
    
    def plot_causal_graph(
        self,
        causal_graph,
        save_name: str = "causal_graph.png"
    ):
        """
        绘制因果图
        
        Args:
            causal_graph: CausalGraph 实例
        """
        import networkx as nx
        
        G = causal_graph.graph
        
        plt.figure(figsize=(14, 10))
        
        # 使用 spring 布局
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 获取边的权重（因果强度）
        edge_weights = [G[u][v]['strength'] for u, v in G.edges()]
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue', alpha=0.8)
        
        # 绘制边（宽度与因果强度成正比）
        nx.draw_networkx_edges(
            G, pos,
            width=[w / 5 for w in edge_weights],
            edge_color='gray',
            alpha=0.6,
            arrows=True,
            arrowsize=20
        )
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.title("Causal Graph (Granger Causality)")
        plt.axis('off')
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {save_path}")
    
    def plot_confusion_matrix(
        self,
        y_true: List[str],
        y_pred: List[str],
        title: str = "Confusion Matrix",
        save_name: str = "confusion_matrix.png"
    ):
        """绘制混淆矩阵"""
        from sklearn.metrics import confusion_matrix
        
        # 获取所有服务
        all_services = sorted(set(y_true) | set(y_pred))
        
        cm = confusion_matrix(y_true, y_pred, labels=all_services)
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=all_services,
            yticklabels=all_services
        )
        
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        save_path = self.output_dir / save_name
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved: {save_path}")


if __name__ == "__main__":
    # 示例用法
    viz = ResultsVisualizer()
    
    # 示例数据
    results = {
        "Standard RAG": 0.55,
        "Graph-RAG": 0.68,
        "mABC": 0.72,
        "CE-MARCA (Ours)": 0.82
    }
    
    viz.plot_accuracy_comparison(results)
