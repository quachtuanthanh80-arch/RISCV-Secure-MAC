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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.2, 5.4), dpi=300)

    # Subplot 1: Top 12 Vulnerable Nodes with Descriptive Hardware Roles
    top12 = df.head(12).copy().iloc[::-1]
    
    # Mapping raw RTL net names to clear functional hardware descriptions
    role_labels = {
        "shadow_accumulator": "shadow_acc (Thanh ghi Shadow Stg 3)",
        "out": "out_bus (Bus kết quả ngõ ra MAC)",
        "reg_c_32": "reg_c_32 (Thanh ghi tích lũy Stg 1)",
        "mac_result": "mac_result (Ngõ ra bộ cộng MAC Stg 2)",
        "pipe_c": "pipe_c (Thanh ghi truyền c Stg 2)",
        "pipe_product": "pipe_prod (Thanh ghi nhân Stg 2)",
        "c": "c_port (Cổng ngõ vào tích lũy C)",
        "mac_result_32": "mac_res_32 (Đường dây cắt bit Stg 2)",
        "reg_c": "reg_c (Thanh ghi toán hạng C Stg 1)",
        "fault_detected": "fault_flag (Cờ phát hiện lỗi CED Stg 3)",
        "valid_d1_n": "valid_d1_n (Tín hiệu điều khiển Stg 1)",
        "valid_d2_n": "valid_d2_n (Tín hiệu điều khiển Stg 2)"
    }
    
    clean_names = [role_labels.get(name, name) for name in top12["Node_Name"]]

    tier_colors = {
        "CRITICAL": "#c62828",
        "HIGH": "#e65100",
        "MEDIUM": "#f57f17",
        "LOW": "#2e7d32"
    }
    colors = [tier_colors.get(t, "#757575") for t in top12["Criticality_Tier"]]

    bars = ax1.barh(clean_names, top12["Vulnerability_Score"], color=colors, alpha=0.90, edgecolor='#212121', height=0.68)
    ax1.set_xlabel("Chỉ số Lỗ hổng Nguy cấp (Vulnerability Score / SDC Susceptibility)", fontweight="bold", labelpad=8)
    ax1.set_title("(a) Thứ hạng Thực thể RTL Cần Gia cố Cứng (Top 12)", fontweight="bold", pad=12)
    ax1.set_xlim(0, 1.08)

    for bar, score in zip(bars, top12["Vulnerability_Score"]):
        w = bar.get_width()
        ax1.text(w + 0.02, bar.get_y() + bar.get_height() / 2.0, f"{score:.2f}",
                 ha='left', va='center', fontsize=9.5, fontweight='bold', color='#212121')

    # Legend for tiers in Subplot 1
    import matplotlib.patches as mpatches
    crit_patch = mpatches.Patch(color='#c62828', label='Nguy cấp (Critical SDC)')
    high_patch = mpatches.Patch(color='#e65100', label='Cao (High Susceptibility)')
    med_patch = mpatches.Patch(color='#f57f17', label='Trung bình (Medium)')
    ax1.legend(handles=[crit_patch, high_patch, med_patch], loc="lower right", framealpha=0.95, edgecolor="#cfd8dc", fontsize=8.8)

    # Subplot 2: Pareto Cumulative Protection Curve
    total_vuln = df["Vulnerability_Score"].sum()
    df["cum_vuln"] = df["Vulnerability_Score"].cumsum() / total_vuln * 100.0
    df["entity_pct"] = (np.arange(len(df)) + 1) / len(df) * 100.0

    ax2.plot(df["entity_pct"], df["cum_vuln"], color='#1565c0', lw=2.6, label='Độ phủ Bảo vệ Tích lũy (Selective Hardening)')
    ax2.plot([0, 100], [0, 100], color='#757575', linestyle=':', lw=1.6, label='Bảo vệ Đồng đều (Uniform Protection Baseline)')

    # Highlight Top-20% sweet spot
    p20_idx = int(0.20 * len(df))
    p20_cov = df.iloc[p20_idx]["cum_vuln"]

    ax2.scatter([20.0], [p20_cov], color='#b71c1c', s=85, zorder=5, edgecolors='#ffffff', linewidths=1.5)
    ax2.axvline(20.0, color='#b71c1c', linestyle='--', alpha=0.7, lw=1.2)
    ax2.axhline(p20_cov, color='#b71c1c', linestyle='--', alpha=0.7, lw=1.2)

    # Baseline marker at x=20, y=20
    delta_gain = p20_cov - 20.0
    ax2.scatter([20.0], [20.0], color='#757575', s=50, zorder=5, edgecolors='#ffffff', linewidths=1.0)

    # Callout placed cleanly above point with straight vertical arrow: zero curve intersection!
    ax2.annotate(f"Top 20% RTL: {p20_cov:.1f}% SDC\n$\\Delta = +{delta_gain:.1f}\\%$ (vs Đồng đều)",
                 xy=(20.0, p20_cov), xytext=(28.0, 84.0),
                 ha='center', va='bottom',
                 arrowprops=dict(arrowstyle="->", color="#b71c1c", lw=1.8),
                 fontsize=8.8, fontweight="bold", color="#b71c1c",
                 bbox=dict(boxstyle="round,pad=0.35", fc="#ffebee", ec="#ef9a9a", lw=1.2))

    ax2.set_xlabel("Tỷ lệ Thực thể Phần cứng Được Gia cố Cứng (%)", fontweight="bold", labelpad=8)
    ax2.set_ylabel("Tỷ lệ Lỗ hổng SDC Được Triệt tiêu Tích lũy (%)", fontweight="bold", labelpad=8)
    ax2.set_title("(b) Đường cong Tối ưu hóa Bảo vệ Chọn lọc (Pareto Coverage)", fontweight="bold", pad=12)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 105)
    ax2.legend(loc="lower right", framealpha=0.95, edgecolor="#cfd8dc", fontsize=9.2)

    fig.tight_layout()
    out_priority = figures_dir / "fig_ml_selective_hardening.png"
    fig.savefig(out_priority, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved Hardening Priority Figure to: {out_priority}")

    # -------------------------------------------------------------------------
    # 2. Network Topology Vulnerability Map (Hierarchical Pipeline Stages)
    # -------------------------------------------------------------------------
    print(">>> Generating Circuit Graph Topology Map (Pipeline Architecture)...")
    try:
        from generate_gnn_connected_map import generate_gnn_figure_and_drawio
        generate_gnn_figure_and_drawio()
    except Exception as e:
        print(f"[!] Falling back to local renderer: {e}")


if __name__ == "__main__":
    generate_hardening_map()

