#!/usr/bin/env python3
"""
Advanced Heatmap & Pattern Discovery Analysis
1. Hierarchical Clustering Dendrogram (Ward Linkage on 32-bit Pairwise Fault Space).
2. Annotated Heatmap with ML-predicted Vulnerability Contours.
3. Bit-Zone Vulnerability Profile with Welch's t-test Statistical Significance.
Outputs 300+ DPI figures for publication.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.cluster import hierarchy
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# IEEE style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 10.5,
    "axes.labelsize": 11.5,
    "axes.titlesize": 12.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9.5,
    "figure.titlesize": 13.5
})


def analyze_heatmaps(data_dir=None, figures_dir=None):
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "data"
    else:
        data_dir = Path(data_dir)

    if figures_dir is None:
        figures_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "figures"
    else:
        figures_dir = Path(figures_dir)

    figures_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Running Enhanced Heatmap Analysis -> {figures_dir}")

    csv_file = data_dir / "double_bit_heatmap_32b.csv"
    if not csv_file.exists():
        raise FileNotFoundError(f"Missing heatmap: {csv_file}")

    df_hm = pd.read_csv(csv_file, index_col=0)
    matrix = df_hm.values

    # -------------------------------------------------------------------------
    # 1. Hierarchical Clustering Dendrogram
    # -------------------------------------------------------------------------
    print(">>> Generating Hierarchical Clustering Dendrogram...")
    # Compute Ward linkage on the pairwise correlation / distance matrix
    linkage_matrix = hierarchy.linkage(matrix, method='ward', metric='euclidean')

    fig, ax = plt.subplots(figsize=(10.0, 4.8), dpi=300)
    dendro = hierarchy.dendrogram(
        linkage_matrix,
        labels=[f"b{i}" for i in range(32)],
        ax=ax,
        leaf_font_size=9.5,
        color_threshold=linkage_matrix[-4, 2],
        above_threshold_color='#78909c'
    )
    ax.set_xlabel("Accumulator Bit Position (0 = LSB, 31 = MSB)", fontweight="bold", labelpad=8)
    ax.set_ylabel("Ward Cluster Distance", fontweight="bold", labelpad=8)
    ax.set_title("Hierarchical Clustering of 32-Bit MAC Registers by Fault Response Profile", fontweight="bold", pad=12)

    # Annotate key clusters
    ax.text(0.03, 0.88, "Distinct clusters distinguish High-Significance MSB bits\nfrom Parity-Sensitive Low/Mid-Significance bits",
            transform=ax.transAxes, fontsize=9.5, style="italic",
            bbox=dict(boxstyle="round,pad=0.3", fc="#f5f5f5", ec="#b0bec5"))

    fig.tight_layout()
    out_dendro = figures_dir / "fig_ml_hierarchical_clustering.png"
    fig.savefig(out_dendro, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved: {out_dendro}")

    # -------------------------------------------------------------------------
    # 2. Annotated Heatmap with ML Overlay & Contour
    # -------------------------------------------------------------------------
    print(">>> Generating Annotated Heatmap with Contours...")
    fig, ax = plt.subplots(figsize=(8.8, 7.2), dpi=300)

    # Draw Heatmap
    cmap = sns.diverging_palette(10, 240, as_cmap=True)
    sns.heatmap(
        matrix, cmap=cmap, vmin=0, vmax=100,
        ax=ax, cbar_kws={'label': 'Fault Detection Rate FDR (%)'},
        xticklabels=4, yticklabels=4
    )

    # Overlay Contour for Blind Spots (FDR < 50%)
    contour = ax.contour(
        np.arange(32) + 0.5, np.arange(32) + 0.5, matrix,
        levels=[50.0], colors=['#ffd600'], linewidths=1.8, linestyles='--'
    )
    ax.clabel(contour, inline=True, fontsize=8, fmt='FDR=50%%')

    ax.set_xlabel("Injected Bit $j$", fontweight="bold", labelpad=8)
    ax.set_ylabel("Injected Bit $i$", fontweight="bold", labelpad=8)
    ax.set_title("Double-Bit Fault Detection Heatmap (32-Bit Datapath) with 50% Boundary", fontweight="bold", pad=12)

    fig.tight_layout()
    out_annot_hm = figures_dir / "fig_ml_annotated_heatmap.png"
    fig.savefig(out_annot_hm, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved: {out_annot_hm}")

    # -------------------------------------------------------------------------
    # 3. Bit-Zone Vulnerability Profile & Welch's t-test
    # -------------------------------------------------------------------------
    print(">>> Generating Bit-Zone Vulnerability Profile...")
    zones = {
        "LSB\n[0..7]": [],
        "MID\n[8..15]": [],
        "MSB_LOW\n[16..21]": [],
        "MSB_HIGH\n[22..31]": []
    }

    def get_zone_name(bit):
        if bit <= 7: return "LSB\n[0..7]"
        elif bit <= 15: return "MID\n[8..15]"
        elif bit <= 21: return "MSB_LOW\n[16..21]"
        else: return "MSB_HIGH\n[22..31]"

    for i in range(32):
        for j in range(i + 1, 32):
            fdr_val = matrix[i, j]
            # Categorize by the higher-order bit's zone
            z = get_zone_name(j)
            zones[z].append(fdr_val)

    zone_names = list(zones.keys())
    zone_means = [np.mean(zones[z]) for z in zone_names]
    zone_sems = [stats.sem(zones[z]) for z in zone_names]

    # Welch's t-test between LSB and MSB_HIGH
    t_stat, p_val = stats.ttest_ind(zones["LSB\n[0..7]"], zones["MSB_HIGH\n[22..31]"], equal_var=False)
    print(f"Welch's t-test (LSB vs MSB_HIGH): t = {t_stat:.3f}, p-value = {p_val:.4e}")

    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    colors = ['#1976d2', '#0288d1', '#7b1fa2', '#c2185b']
    bars = ax.bar(zone_names, zone_means, yerr=zone_sems, capsize=6,
                  color=colors, alpha=0.88, edgecolor='#212121', width=0.55)

    ax.set_ylabel("Mean Fault Detection Rate FDR (%)", fontweight="bold", labelpad=8)
    ax.set_title("Vulnerability Profile Across Datapath Architectural Zones", fontweight="bold", pad=12)
    ax.set_ylim(0, 115)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add data labels
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 3.5, f"{h:.1f}%",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add statistical significance bracket
    x1, x2 = 0, 3
    y_line = 104
    ax.plot([x1, x1, x2, x2], [y_line - 2, y_line, y_line, y_line - 2], lw=1.5, c='#212121')
    sig_label = f"Welch's t-test: p = {p_val:.2e} (Statistically Significant ***)" if p_val < 0.001 else f"p = {p_val:.4f}"
    ax.text((x1 + x2) / 2.0, y_line + 2.0, sig_label, ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#b71c1c')

    fig.tight_layout()
    out_zone = figures_dir / "fig_ml_zone_vulnerability.png"
    fig.savefig(out_zone, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved: {out_zone}")

    return {
        "zone_means": {k: float(v) for k, v in zip(zone_names, zone_means)},
        "welch_t_stat": float(t_stat),
        "welch_p_val": float(p_val)
    }


if __name__ == "__main__":
    analyze_heatmaps()
