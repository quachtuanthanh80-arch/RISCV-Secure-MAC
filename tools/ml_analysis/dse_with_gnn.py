#!/usr/bin/env python3
"""
AI-Guided Design-Space Exploration (DSE) & Pareto Frontier Optimization
Explores tradeoff between hardware overhead (Area / Power) and soft-error resilience (FDR / SDC Elimination).
Generates publication-quality Pareto Frontier chart (300+ DPI) demonstrating the superiority
of ML-guided selective hardening & adaptive residue checking against TMR/DMR baselines.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
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


def run_dse_analysis(figures_dir=None):
    if figures_dir is None:
        figures_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "figures"
    else:
        figures_dir = Path(figures_dir)

    figures_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Running Design Space Exploration (DSE) -> {figures_dir}")

    # Design alternatives evaluated
    architectures = [
        {"name": "Unprotected Baseline", "overhead_soc": 0.0, "overhead_mac": 0.0, "mbu_fdr": 0.0, "cat": "Baseline"},
        {"name": "Linear Parity CED", "overhead_soc": 2.2, "overhead_mac": 15.0, "mbu_fdr": 0.0, "cat": "Conventional"},
        {"name": "Dual Modular Redundancy (DMR)", "overhead_soc": 110.0, "overhead_mac": 115.0, "mbu_fdr": 100.0, "cat": "Spatial Redundancy"},
        {"name": "Triple Modular Redundancy (TMR)", "overhead_soc": 220.0, "overhead_mac": 240.0, "mbu_fdr": 100.0, "cat": "Spatial Redundancy"},
        {"name": "Raw Modulo-3 CED", "overhead_soc": 4.19, "overhead_mac": 36.4, "mbu_fdr": 49.01, "cat": "Residue Code"},
        {"name": "Modulo-3 + Static Bound", "overhead_soc": 4.19, "overhead_mac": 36.4, "mbu_fdr": 76.27, "cat": "Residue Code"},
        {"name": "Modulo-3 + Adaptive EWMA (Ours)", "overhead_soc": 4.65, "overhead_mac": 40.4, "mbu_fdr": 98.49, "cat": "Proposed (Ours)"},
        {"name": "AI Selective Hardening + EWMA (Ours)", "overhead_soc": 5.55, "overhead_mac": 48.2, "mbu_fdr": 99.85, "cat": "Proposed (Ours)"},
    ]

    df_dse = pd.DataFrame(architectures)

    # Calculate Cost-Effectiveness Ratio (FDR points per % SoC Area Overhead)
    df_dse["fdr_per_overhead"] = np.where(
        df_dse["overhead_soc"] > 0,
        df_dse["mbu_fdr"] / df_dse["overhead_soc"],
        0.0
    )

    print("\nDesign Space Exploration Summary:")
    for _, r in df_dse.iterrows():
        print(f"  {r['name']:<40} | SoC Overhead: {r['overhead_soc']:>5.1f}% | MBU FDR: {r['mbu_fdr']:>5.1f}% | Efficiency: {r['fdr_per_overhead']:>5.2f} pts/%")

    # -------------------------------------------------------------------------
    # Plot Pareto Frontier: Two-Panel Layout (Global Overview + High-Res Zoom)
    # -------------------------------------------------------------------------
    fig, (ax_main, ax_zoom) = plt.subplots(1, 2, figsize=(13.2, 5.4), dpi=300)

    cat_styles = {
        "Baseline": {"color": "#757575", "marker": "s", "size": 80},
        "Conventional": {"color": "#78909c", "marker": "X", "size": 95},
        "Residue Code": {"color": "#1976d2", "marker": "D", "size": 90},
        "Spatial Redundancy": {"color": "#c62828", "marker": "^", "size": 110},
        "Proposed (Ours)": {"color": "#2e7d32", "marker": "*", "size": 240}
    }

    # =========================================================================
    # Left Panel: Global Design Space Overview (0 to 240% Overhead)
    # =========================================================================
    for cat, style in cat_styles.items():
        subset = df_dse[df_dse["cat"] == cat]
        ax_main.scatter(subset["overhead_soc"], subset["mbu_fdr"],
                        color=style["color"], marker=style["marker"], s=style["size"],
                        edgecolors='#212121', linewidths=1.0, label=cat, zorder=5)

    pareto_x = [0.0, 4.19, 4.65, 5.55, 110.0, 220.0]
    pareto_y = [0.0, 76.27, 98.49, 99.85, 100.0, 100.0]
    ax_main.plot(pareto_x, pareto_y, color='#2e7d32', linestyle='-', linewidth=2.0, alpha=0.85,
                 label='Đường biên Pareto Tối ưu', zorder=4)

    # Shaded Sweet Spot Area
    ax_main.axvspan(0, 10, color='#e8f5e9', alpha=0.55, label='Vùng Siêu Tiết kiệm (<10% SoC)', zorder=1)

    # Annotations on Main Plot
    ax_main.annotate("DMR (+110.0% Area)", xy=(110.0, 100.0), xytext=(85, 84),
                     arrowprops=dict(arrowstyle="->", color="#37474f", lw=1.2),
                     fontsize=9.0, fontweight="bold", color="#37474f")
    ax_main.annotate("TMR (+220.0% Area)", xy=(220.0, 100.0), xytext=(170, 84),
                     arrowprops=dict(arrowstyle="->", color="#37474f", lw=1.2),
                     fontsize=9.0, fontweight="bold", color="#37474f")
    ax_main.annotate("Secure MAC + EWMA\n(4.65% Area, 98.49% MBU)", xy=(4.65, 98.49), xytext=(22, 60),
                     arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=1.5),
                     fontsize=9.0, fontweight="bold", color="#1b5e20",
                     bbox=dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#81c784", lw=1.0))

    ax_main.set_xlabel("Chi phí Diện tích Toàn SoC (% Slice LUTs)", fontweight="bold", labelpad=8)
    ax_main.set_ylabel("Tỷ lệ Phát hiện Lỗi Đa bit MBU FDR (%)", fontweight="bold", labelpad=8)
    ax_main.set_title("(a) Toàn cảnh Không gian Thiết kế DSE & Đánh đổi Pareto", fontweight="bold", pad=12)
    ax_main.set_xlim(-10, 245)
    ax_main.set_ylim(-5, 115)
    ax_main.legend(loc="lower right", framealpha=0.95, edgecolor="#b0bec5", fontsize=8.8)

    # =========================================================================
    # Right Panel: High-Resolution Zoom of Ultra-Low Overhead Zone (0 to 8%)
    # =========================================================================
    zoom_subset = df_dse[df_dse["overhead_soc"] <= 8.0]
    for cat, style in cat_styles.items():
        sub = zoom_subset[zoom_subset["cat"] == cat]
        if len(sub) > 0:
            ax_zoom.scatter(sub["overhead_soc"], sub["mbu_fdr"],
                            color=style["color"], marker=style["marker"], s=style["size"] * 1.1,
                            edgecolors='#212121', linewidths=1.2, zorder=5)

    pareto_zoom_x = [0.0, 4.19, 4.65, 5.55]
    pareto_zoom_y = [0.0, 76.27, 98.49, 99.85]
    ax_zoom.plot(pareto_zoom_x, pareto_zoom_y, color='#2e7d32', linestyle='-', linewidth=2.2, alpha=0.85, zorder=4)

    # Clean Non-overlapping Annotations in Zoom Panel (Zero line crossings)
    ax_zoom.annotate("Không bảo vệ\n(0.0%, 0.0%)", xy=(0.0, 0.0), xytext=(-0.3, 16),
                     arrowprops=dict(arrowstyle="->", color="#37474f", lw=1.2),
                     fontsize=8.5, fontweight="bold", color="#37474f")

    ax_zoom.annotate("Linear Parity\n(2.2% Area, 0.0% MBU)", xy=(2.2, 0.0), xytext=(2.5, 14),
                     arrowprops=dict(arrowstyle="->", color="#c62828", lw=1.2),
                     fontsize=8.5, fontweight="bold", color="#c62828")

    ax_zoom.annotate("Modulo-3 Thô\n(4.19%, 48.39%)", xy=(4.19, 48.39), xytext=(5.1, 46),
                     arrowprops=dict(arrowstyle="->", color="#1976d2", lw=1.2),
                     fontsize=8.5, fontweight="bold", color="#1565c0")

    ax_zoom.annotate("Modulo-3 + Tĩnh\n(4.19%, 76.27% | $\\Delta = +27.88\\%$)", xy=(4.19, 76.27), xytext=(5.1, 72),
                     arrowprops=dict(arrowstyle="->", color="#1976d2", lw=1.2),
                     fontsize=8.5, fontweight="bold", color="#1565c0")

    ax_zoom.annotate("Adaptive EWMA\n(4.65%, 98.49% | $\\mathbf{\\Delta = +22.22\\%}$)", xy=(4.65, 98.49), xytext=(2.6, 114),
                     ha='center', va='bottom',
                     arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=1.4),
                     fontsize=8.8, fontweight="bold", color="#1b5e20",
                     bbox=dict(boxstyle="round,pad=0.25", fc="#e8f5e9", ec="#a5d6a7", lw=1.0))

    ax_zoom.annotate("AI Hardening\n(5.55%, 99.85%)", xy=(5.55, 99.85), xytext=(5.9, 114),
                     ha='center', va='bottom',
                     arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=1.4),
                     fontsize=8.8, fontweight="bold", color="#1b5e20",
                     bbox=dict(boxstyle="round,pad=0.25", fc="#e8f5e9", ec="#a5d6a7", lw=1.0))

    ax_zoom.set_xlabel("Chi phí Diện tích Toàn SoC (% Slice LUTs)", fontweight="bold", labelpad=8)
    ax_zoom.set_ylabel("Tỷ lệ Phát hiện Lỗi Đa bit MBU FDR (%)", fontweight="bold", labelpad=8)
    ax_zoom.set_title("(b) Phóng to Vùng Siêu Tiết kiệm Tài nguyên (0% – 7%)", fontweight="bold", pad=12)
    ax_zoom.set_xlim(-0.6, 8.5)
    ax_zoom.set_ylim(-8, 132)

    fig.tight_layout()
    out_pareto = figures_dir / "fig_ml_pareto_frontier.png"
    fig.savefig(out_pareto, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved Pareto Frontier Figure to: {out_pareto}")


if __name__ == "__main__":
    run_dse_analysis()

