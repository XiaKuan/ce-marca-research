#!/usr/bin/env python3
"""
论文图表绘制脚本

生成论文所需的所有图表
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # 使用英文字体避免中文问题
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = Path("results/figures")
output_dir.mkdir(parents=True, exist_ok=True)


def load_experiment_results():
    """加载实验结果"""
    with open("results/metrics/summary.json", 'r') as f:
        main_results = json.load(f)
    
    with open("results/metrics/ablation_summary.json", 'r') as f:
        ablation_results = json.load(f)
    
    return main_results, ablation_results


def plot_accuracy_comparison(main_results):
    """图 5：准确率对比"""
    methods = list(main_results.keys())
    accuracies = [main_results[m]["top1_accuracy"] for m in methods]
    
    plt.figure(figsize=(10, 6))
    colors = ['lightcoral', 'lightblue', 'darkgreen']
    bars = plt.bar(methods, accuracies, color=colors)
    
    # 添加数值标签
    for bar, acc in zip(bars, accuracies):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f'{acc:.1%}',
            ha='center',
            va='bottom',
            fontsize=11
        )
    
    plt.xlabel('Method', fontsize=12)
    plt.ylabel('Top-1 Accuracy', fontsize=12)
    plt.title('Main Experiment: Accuracy Comparison', fontsize=14)
    plt.ylim(0, 1.0)
    plt.xticks(rotation=15)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    save_path = output_dir / "fig5_accuracy_comparison.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_efficiency_comparison(main_results):
    """图 6：效率对比"""
    methods = list(main_results.keys())
    times = [main_results[m]["avg_analysis_time_sec"] for m in methods]
    tokens = [main_results[m]["avg_tokens"] for m in methods]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 推理时间
    colors1 = ['lightcoral', 'lightblue', 'darkgreen']
    bars1 = ax1.bar(methods, times, color=colors1)
    ax1.set_xlabel('Method', fontsize=12)
    ax1.set_ylabel('Average Time (s)', fontsize=12)
    ax1.set_title('Inference Time', fontsize=13)
    
    for bar, t in zip(bars1, times):
        if t < 0.01:
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                '<0.01s',
                ha='center',
                va='bottom',
                fontsize=10
            )
        else:
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f'{t:.1f}s',
                ha='center',
                va='bottom',
                fontsize=10
            )
    
    # Token 成本
    colors2 = ['lightcoral', 'lightblue', 'darkgreen']
    bars2 = ax2.bar(methods, tokens, color=colors2)
    ax2.set_xlabel('Method', fontsize=12)
    ax2.set_ylabel('Average Tokens', fontsize=12)
    ax2.set_title('Token Consumption', fontsize=13)
    
    for bar, t in zip(bars2, tokens):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 200,
            f'{t:.0f}',
            ha='center',
            va='bottom',
            fontsize=10,
            rotation=45
        )
    
    plt.suptitle('Efficiency Comparison', fontsize=14, y=1.02)
    plt.tight_layout()
    
    save_path = output_dir / "fig6_efficiency_comparison.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_ablation_study(ablation_results):
    """图 7：消融实验"""
    variants = list(ablation_results.keys())
    accuracies = [ablation_results[v]["top1_accuracy"] for v in variants]
    
    # 找出完整方法
    full_idx = variants.index("CE-MARCA (Full)")
    
    colors = ['lightblue'] * len(variants)
    colors[full_idx] = 'darkgreen'  # 完整方法用绿色突出
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(variants, accuracies, color=colors)
    
    # 添加数值标签
    for bar, acc in zip(bars, accuracies):
        drop = accuracies[full_idx] - acc
        label = f'{acc:.1%}'
        if drop > 0.01:
            label += f'\n(-{drop:.1%})'
        elif drop < -0.01:
            label += f'\n(+{abs(drop):.1%})'
        
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            label,
            ha='center',
            va='bottom',
            fontsize=9,
            rotation=45
        )
    
    plt.xlabel('Method Variant', fontsize=12)
    plt.ylabel('Top-1 Accuracy', fontsize=12)
    plt.title('Ablation Study: Component Contributions', fontsize=14)
    plt.ylim(0, 1.0)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    save_path = output_dir / "fig7_ablation_study.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_architecture_diagram():
    """图 1：CE-MARCA 整体架构图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    # 使用文本框绘制简化架构图
    boxes = [
        (0.5, 0.9, "User Interface / API Gateway", "lightblue"),
        (0.5, 0.75, "Coordinator Agent", "lightgreen"),
        (0.2, 0.55, "Metrics Agent", "lightcoral"),
        (0.5, 0.55, "Logs Agent", "lightcoral"),
        (0.8, 0.55, "Traces Agent", "lightcoral"),
        (0.5, 0.35, "Causal Graph Engine", "lightyellow"),
        (0.5, 0.15, "Data Layer (Prometheus, ELK, Jaeger)", "lightgray"),
    ]
    
    for x, y, text, color in boxes:
        ax.text(x, y, text, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.7),
               fontsize=11)
    
    # 添加箭头
    arrow_props = dict(arrowstyle='->', color='gray', lw=1.5)
    ax.annotate('', xy=(0.5, 0.85), xytext=(0.5, 0.8), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.68), xytext=(0.5, 0.65), arrowprops=arrow_props)
    ax.annotate('', xy=(0.2, 0.65), xytext=(0.2, 0.62), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.65), xytext=(0.5, 0.62), arrowprops=arrow_props)
    ax.annotate('', xy=(0.8, 0.65), xytext=(0.8, 0.62), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.48), xytext=(0.5, 0.45), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.28), xytext=(0.5, 0.25), arrowprops=arrow_props)
    
    plt.title('Figure 1: CE-MARCA Architecture', fontsize=14, pad=20)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    
    save_path = output_dir / "fig1_architecture.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_causal_graph_example():
    """图 2：双层图结构示例"""
    import networkx as nx
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 静态依赖图
    G1 = nx.DiGraph()
    G1.add_edges_from([
        ('api-gateway', 'order-service'),
        ('order-service', 'payment-service'),
        ('order-service', 'inventory-service'),
        ('payment-service', 'database'),
        ('inventory-service', 'database')
    ])
    
    pos1 = nx.spring_layout(G1, seed=42)
    nx.draw_networkx_nodes(G1, pos1, node_size=2000, node_color='lightblue', ax=ax1)
    nx.draw_networkx_edges(G1, pos1, arrowstyle='->', arrows=True, ax=ax1)
    nx.draw_networkx_labels(G1, pos1, font_size=9, ax=ax1)
    ax1.set_title('Static Dependency Graph', fontsize=12)
    ax1.axis('off')
    
    # 动态因果图
    G2 = nx.DiGraph()
    G2.add_edges_from([
        ('api-gateway', 'order-service', {'weight': 15.2}),
        ('order-service', 'payment-service', {'weight': 22.5}),
        ('payment-service', 'database', {'weight': 28.3})
    ])
    
    pos2 = nx.spring_layout(G2, seed=42)
    nx.draw_networkx_nodes(G2, pos2, node_size=2000, node_color='lightcoral', ax=ax2)
    nx.draw_networkx_edges(G2, pos2, arrowstyle='->', arrows=True, 
                          width=[1.5, 2.0, 2.5], ax=ax2)
    nx.draw_networkx_labels(G2, pos2, font_size=9, ax=ax2)
    ax2.set_title('Dynamic Causal Graph (Granger)', fontsize=12)
    ax2.axis('off')
    
    plt.suptitle('Figure 2: Dual-Layer Graph Structure', fontsize=14, y=1.02)
    plt.tight_layout()
    
    save_path = output_dir / "fig2_dual_layer_graph.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_cahp_protocol():
    """图 3：CAHP 协议 3 轮推理流程"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    # 绘制 3 轮推理流程
    rounds = [
        (0.5, 0.85, "Round 1: Parallel Data Collection", "lightblue"),
        (0.2, 0.65, "Metrics Agent", "lightcoral"),
        (0.5, 0.65, "Logs Agent", "lightcoral"),
        (0.8, 0.65, "Traces Agent", "lightcoral"),
        (0.5, 0.45, "Round 2: Causal-Constrained Reasoning", "lightgreen"),
        (0.5, 0.25, "Round 3: Hypothesis Arbitration", "lightyellow"),
    ]
    
    for x, y, text, color in rounds:
        ax.text(x, y, text, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.7),
               fontsize=11)
    
    # 添加箭头
    arrow_props = dict(arrowstyle='->', color='gray', lw=1.5)
    ax.annotate('', xy=(0.5, 0.78), xytext=(0.5, 0.75), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.58), xytext=(0.5, 0.55), arrowprops=arrow_props)
    ax.annotate('', xy=(0.5, 0.38), xytext=(0.5, 0.35), arrowprops=arrow_props)
    
    plt.title('Figure 3: CAHP Protocol - 3-Round Reasoning', fontsize=14, pad=20)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    
    save_path = output_dir / "fig3_cahp_protocol.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("Generating Paper Figures")
    print("=" * 60)
    
    # 加载结果
    print("\n[1/6] Loading experiment results...")
    main_results, ablation_results = load_experiment_results()
    
    # 生成图表
    print("\n[2/6] Generating Figure 1: Architecture...")
    plot_architecture_diagram()
    
    print("\n[3/6] Generating Figure 2: Dual-Layer Graph...")
    plot_causal_graph_example()
    
    print("\n[4/6] Generating Figure 3: CAHP Protocol...")
    plot_cahp_protocol()
    
    print("\n[5/6] Generating Figure 5: Accuracy Comparison...")
    plot_accuracy_comparison(main_results)
    
    print("\n[6/6] Generating Figure 6-7: Efficiency & Ablation...")
    plot_efficiency_comparison(main_results)
    plot_ablation_study(ablation_results)
    
    print("\n" + "=" * 60)
    print("All figures saved to: results/figures/")
    print("=" * 60)


if __name__ == "__main__":
    main()
