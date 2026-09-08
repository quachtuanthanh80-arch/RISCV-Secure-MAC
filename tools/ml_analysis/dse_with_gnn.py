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
    # Plot Pareto Frontier
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9.5, 5.4), dpi=300)

    cat_styles = {
        "Baseline": {"color": "#757575", "marker": "s", "size": 70},
        "Conventional": {"color": "#b0bec5", "marker": "X", "size": 80},
        "Spatial Redundancy": {"color": "#d32f2f", "marker": "^", "size": 100},
        "Residue Code": {"color": "#1976d2", "marker": "D", "size": 85},
        "Proposed (Ours)": {"color": "#2e7d32", "marker": "*", "size": 220}
    }

    for cat, style in cat_styles.items():
        subset = df_dse[df_dse["cat"] == cat]
        ax.scatter(subset["overhead_soc"], subset["mbu_fdr"],
                   color=style["color"], marker=style["marker"], s=style["size"],
                   edgecolors='#212121', linewidths=1.0, label=cat, zorder=4)

    # Pareto non-dominated curve points:
    # Baseline (0, 0) -> Modulo-3+Adaptive (4.65, 98.49) -> AI Selective (5.55, 99.85) -> TMR (220, 100)
    pareto_x = [0.0, 4.19, 4.65, 5.55, 110.0, 220.0]
    pareto_y = [0.0, 76.27, 98.49, 99.85, 100.0, 100.0]
    ax.plot(pareto_x, pareto_y, color='#2e7d32', linestyle='-', linewidth=2.0, alpha=0.8,
            label='Optimal Pareto Frontier (Coverage vs Cost)', zorder=3)

    # Annotate points
    annotations = [
        ("Unprotected (0%)", (0.0, 0.0), (5, 5)),
        ("Linear Parity (Fails)", (2.2, 0.0), (10, -12)),
        ("Raw Modulo-3", (4.19, 49.01), (12, 45)),
        ("Modulo-3 + Static", (4.19, 76.27), (12, 73)),
        ("Adaptive EWMA (Ours)", (4.65, 98.49), (14, 94)),
        ("AI Hardening (Ours)", (5.55, 99.85), (14, 103)),
        ("DMR (+110%)", (110.0, 100.0), (95, 90)),
        ("Full TMR (+220%)", (220.0, 100.0), (180, 90))
    ]

    for label, (x, y), (tx, ty) in annotations:
        ax.annotate(label, xy=(x, y), xytext=(tx, ty),
                    arrowprops=dict(arrowstyle="->", color="#37474f", lw=1.0),
                    fontsize=9.0, fontweight="bold", color="#263238")

    # Shaded Sweet Spot Area
    ax.axvspan(0, 10, color='#e8f5e9', alpha=0.5, label='Ultra-Low Overhead Zone (< 10% SoC Area)')

    ax.set_xlabel("FPGA SoC Area Overhead (% Slice LUTs)", fontweight="bold", labelpad=8)
    ax.set_ylabel("Multi-Bit Upset (MBU) Fault Detection Rate FDR (%)", fontweight="bold", labelpad=8)
    ax.set_title("Pareto Tradeoff: Hardware Area Overhead vs MBU Fault Coverage", fontweight="bold", pad=12)
    ax.set_xlim(-8, 240)
    ax.set_ylim(-8, 115)
    ax.legend(loc="lower right", framealpha=0.95, edgecolor="#b0bec5", fontsize=9.2)

    fig.tight_layout()
    out_pareto = figures_dir / "fig_ml_pareto_frontier.png"
    fig.savefig(out_pareto, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved Pareto Frontier Figure to: {out_pareto}")


if __name__ == "__main__":
    run_dse_analysis()
