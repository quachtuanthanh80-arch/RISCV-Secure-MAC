#!/usr/bin/env python3
"""
Manifold Learning & Dimensionality Reduction for Hardware Fault Space Visualization
1. PCA (Principal Component Analysis): 2D/3D projection of the 32-bit datapath fault manifold.
2. t-SNE (t-Distributed Stochastic Neighbor Embedding): Clustering of detected vs SDC vs masked errors.
Outputs publication-quality 300+ DPI figures for IEEE conference/journal.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# Set IEEE-style publication aesthetics
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 10.5,
    "axes.labelsize": 11.5,
    "axes.titlesize": 12.5,
    "xtick.labelsize": 10.0,
    "ytick.labelsize": 10.0,
    "legend.fontsize": 9.5,
    "figure.titlesize": 13.5,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--"
})


def generate_visualizations(data_dir=None, figures_dir=None):
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent / "data"
    else:
        data_dir = Path(data_dir)

    if figures_dir is None:
        figures_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "figures"
    else:
        figures_dir = Path(figures_dir)

    figures_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Generating fault space visualizations -> {figures_dir}")

    double_csv = data_dir / "double_bit_features.csv"
    if not double_csv.exists():
        raise FileNotFoundError(f"Missing {double_csv}. Please run data_preprocessing.py first.")

    df = pd.read_csv(double_csv)
    df_32 = df[df["target_signal"] == "pipe_c"].copy().reset_index(drop=True)

    feature_cols = [
        "bit_i", "bit_j", "bit_distance", "distance_parity",
        "bit_i_parity", "bit_j_parity", "same_bit_parity",
        "bit_weight_i_log2", "bit_weight_j_log2"
    ]
    X = df_32[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # -------------------------------------------------------------------------
    # 1. PCA Projection
    # -------------------------------------------------------------------------
    print(">>> Running PCA...")
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    var_ratio = pca.explained_variance_ratio_

    fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=300)
    
    # Separate points by distance parity (Even: Detected, Odd: Masked/SDC)
    even_mask = (df_32["distance_parity"] == 0)
    odd_mask = (df_32["distance_parity"] == 1)

    scatter_even = ax.scatter(
        X_pca[even_mask, 0], X_pca[even_mask, 1],
        c='#1565c0', label=f'Even Stride $d$ (FDR = 100%, n={np.sum(even_mask)})',
        alpha=0.85, edgecolors='#0d47a1', s=45, marker='o'
    )
    scatter_odd = ax.scatter(
        X_pca[odd_mask, 0], X_pca[odd_mask, 1],
        c='#d32f2f', label=f'Odd Stride $d$ (SDC / Masked, n={np.sum(odd_mask)})',
        alpha=0.85, edgecolors='#b71c1c', s=45, marker='^'
    )

    # Annotate variance explained
    ax.set_xlabel(f"Principal Component 1 ({var_ratio[0]*100:.1f}% Variance)", fontweight="bold")
    ax.set_ylabel(f"Principal Component 2 ({var_ratio[1]*100:.1f}% Variance)", fontweight="bold")
    ax.set_title("PCA Projection of 32-Bit Datapath Double-Bit Fault Space", fontweight="bold", pad=12)
    ax.legend(loc="upper right", framealpha=0.95, edgecolor="#b0bec5")

    # Annotate total variance
    total_var = np.sum(var_ratio) * 100
    ax.text(0.03, 0.05, f"Cumulative Explained Variance: {total_var:.1f}%",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", fc="#f5f5f5", ec="#bdbdbd", lw=1))

    fig.tight_layout()
    out_pca = figures_dir / "fig_ml_pca_fault_space.png"
    fig.savefig(out_pca, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved: {out_pca}")

    # -------------------------------------------------------------------------
    # 2. t-SNE Clustering
    # -------------------------------------------------------------------------
    print(">>> Running t-SNE Clustering...")
    tsne = TSNE(n_components=2, perplexity=30, max_iter=1000, random_state=42)
    X_tsne = tsne.fit_transform(X_scaled)

    fig, ax = plt.subplots(figsize=(8.0, 5.2), dpi=300)

    # Colormap by continuous FDR
    fdr_vals = df_32["fdr"].values
    scatter = ax.scatter(
        X_tsne[:, 0], X_tsne[:, 1],
        c=fdr_vals, cmap='coolwarm',
        alpha=0.9, edgecolors='#212121', linewidths=0.5, s=50
    )
    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("Fault Detection Rate FDR (%)", fontweight="bold", labelpad=8)

    ax.set_xlabel("t-SNE Dimension 1", fontweight="bold")
    ax.set_ylabel("t-SNE Dimension 2", fontweight="bold")
    ax.set_title("t-SNE Manifold Representation of Double-Bit Upsets (32-Bit MAC)", fontweight="bold", pad=12)

    # Highlight separable clusters
    ax.text(0.04, 0.92, "Separation driven by Bit-Distance Parity\n(Clean segregation of Residue-Detected vs SDC)",
            transform=ax.transAxes, fontsize=9.5, style="italic",
            bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#cfd8dc", alpha=0.95))

    fig.tight_layout()
    out_tsne = figures_dir / "fig_ml_tsne_clusters.png"
    fig.savefig(out_tsne, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved: {out_tsne}")


if __name__ == "__main__":
    generate_visualizations()
