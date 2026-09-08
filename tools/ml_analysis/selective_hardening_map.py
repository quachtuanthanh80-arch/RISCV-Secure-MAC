#!/usr/bin/env python3
"""
Selective Hardening Priority Map & Architectural Vulnerability Visualization
Generates:
1. fig_ml_selective_hardening.png: Hardening priority ranking & cumulative protection curve.
2. fig_ml_gnn_vulnerability_map.png: Hardware graph layout overlay with vulnerability tiers.
Outputs publication-quality figures at 300+ DPI.
"""

import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial"],
    "font.size": 10.5,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--"
})


def generate_hardening_map(data_dir=None, figures_dir=None):
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent / "data"
    else:
        data_dir = Path(data_dir)

    if figures_dir is None:
        figures_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "figures"
    else:
        figures_dir = Path(figures_dir)

    figures_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Generating Selective Hardening Maps -> {figures_dir}")

    csv_path = data_dir / "node_vulnerability_table.csv"
    graph_path = data_dir / "labeled_rtl_graph.json"
    if not csv_path.exists() or not graph_path.exists():
        raise FileNotFoundError("Missing data files. Run previous graph stages first.")

    df = pd.read_csv(csv_path)

    # -------------------------------------------------------------------------
    # 1. Selective Hardening Priority Chart & Cumulative Curve
    # -------------------------------------------------------------------------
    print(">>> Generating Selective Hardening Priority Chart...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.0), dpi=300)

    # Subplot 1: Top 12 Vulnerable Nodes
    top12 = df.head(12).copy().iloc[::-1]
    tier_colors = {
        "CRITICAL": "#c62828",
        "HIGH": "#e65100",
        "MEDIUM": "#f57f17",
        "LOW": "#2e7d32"
    }
    colors = [tier_colors.get(t, "#757575") for t in top12["Criticality_Tier"]]

    bars = ax1.barh(top12["Node_Name"], top12["Vulnerability_Score"], color=colors, alpha=0.88, edgecolor='#212121', height=0.65)
    ax1.set_xlabel("Vulnerability Score (Empirical SDC Susceptibility)", fontweight="bold", labelpad=8)
    ax1.set_title("Hardware Entity Vulnerability Ranking (Top 12)", fontweight="bold", pad=12)
    ax1.set_xlim(0, 1.05)

    for bar, score in zip(bars, top12["Vulnerability_Score"]):
        w = bar.get_width()
        ax1.text(w + 0.02, bar.get_y() + bar.get_height() / 2.0, f"{score:.2f}",
                 ha='left', va='center', fontsize=9.5, fontweight='bold')

    # Subplot 2: Pareto Cumulative Protection Curve
    total_vuln = df["Vulnerability_Score"].sum()
    df["cum_vuln"] = df["Vulnerability_Score"].cumsum() / total_vuln * 100.0
    df["entity_pct"] = (np.arange(len(df)) + 1) / len(df) * 100.0

    ax2.plot(df["entity_pct"], df["cum_vuln"], color='#1565c0', lw=2.5, label='Cumulative Protection Coverage')
    ax2.plot([0, 100], [0, 100], color='#757575', linestyle=':', label='Uniform Protection Baseline')

    # Highlight Top-20% sweet spot
    p20_idx = int(0.20 * len(df))
    p20_cov = df.iloc[p20_idx]["cum_vuln"]

    ax2.scatter([20.0], [p20_cov], color='#b71c1c', s=70, zorder=5)
    ax2.axvline(20.0, color='#b71c1c', linestyle='--', alpha=0.6)
    ax2.axhline(p20_cov, color='#b71c1c', linestyle='--', alpha=0.6)

    ax2.annotate(f"Selective Hardening Sweet Spot:\nHardening Top 20% Entities\nProtects {p20_cov:.1f}% of Vulnerability!",
                 xy=(20.0, p20_cov), xytext=(32, 60),
                 arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.6),
                 fontsize=9.5, fontweight="bold", color="#b71c1c",
                 bbox=dict(boxstyle="round,pad=0.4", fc="#ffebee", ec="#ef9a9a"))

    ax2.set_xlabel("Percentage of Hardened Circuit Entities (%)", fontweight="bold", labelpad=8)
    ax2.set_ylabel("Cumulative Vulnerability Mitigated (%)", fontweight="bold", labelpad=8)
    ax2.set_title("Selective Hardening Optimization (Cumulative Coverage)", fontweight="bold", pad=12)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 105)
    ax2.legend(loc="lower right", framealpha=0.95, edgecolor="#b0bec5")

    fig.tight_layout()
    out_priority = figures_dir / "fig_ml_selective_hardening.png"
    fig.savefig(out_priority, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved Hardening Priority Figure to: {out_priority}")

    # -------------------------------------------------------------------------
    # 2. Network Topology Vulnerability Map
    # -------------------------------------------------------------------------
    print(">>> Generating Circuit Graph Topology Map...")
    with open(graph_path, "r") as f:
        gdata = json.load(f)

    G = nx.DiGraph()
    for n, attrs in gdata["nodes"].items():
        G.add_node(n, **attrs)
    for u, v in gdata["edges"]:
        G.add_edge(u, v)

    fig, ax = plt.subplots(figsize=(10.0, 7.0), dpi=300)
    pos = nx.spring_layout(G, seed=42, k=0.35)

    scores = [G.nodes[n].get("vulnerability_score", 0.1) for n in G.nodes()]
    node_sizes = [120 + 400 * s for s in scores]

    nodes_drawn = nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=scores, cmap='YlOrRd',
        node_size=node_sizes,
        edgecolors='#212121', linewidths=0.8, alpha=0.92
    )
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color='#90a4ae', alpha=0.6,
        arrows=True, arrowsize=10, width=1.0
    )

    # Label prominent nodes
    prominent = df.head(10)["Node_Name"].tolist()
    labels = {n: n for n in prominent if n in G}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight="bold", ax=ax)

    cbar = fig.colorbar(nodes_drawn, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Vulnerability Score (SDC Susceptibility)", fontweight="bold")

    ax.set_title("RTL Circuit Entity Graph with GNN Vulnerability Overlay", fontweight="bold", pad=12)
    ax.axis("off")

    fig.tight_layout()
    out_map = figures_dir / "fig_ml_gnn_vulnerability_map.png"
    fig.savefig(out_map, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved Network Topology Map to: {out_map}")


if __name__ == "__main__":
    generate_hardening_map()
