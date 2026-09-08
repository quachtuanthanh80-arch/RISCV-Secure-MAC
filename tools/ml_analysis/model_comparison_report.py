#!/usr/bin/env python3
"""
Model Comparison & Statistical Theorem Synthesis Report
1. Generates Model Performance Comparison Bar Chart (RF, GBR, Logistic Regression).
2. Generates Feature Importance Ranking Chart (Architectural vs Arithmetic Features).
3. Compares ML Predicted FDR vs Analytical Theorem Predictions (Empirical vs Formal Proof).
Outputs 300+ DPI figures for IEEE conference/journal.
"""

import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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


def generate_reports(data_dir=None, figures_dir=None):
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent / "data"
    else:
        data_dir = Path(data_dir)

    if figures_dir is None:
        figures_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "figures"
    else:
        figures_dir = Path(figures_dir)

    figures_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Generating model comparison reports -> {figures_dir}")

    metrics_file = data_dir / "ml_evaluation_metrics.json"
    pred_file = data_dir / "double_bit_predictions.csv"

    if not metrics_file.exists():
        raise FileNotFoundError(f"Missing {metrics_file}. Please run ml_fault_predictor.py first.")

    with open(metrics_file, "r") as f:
        metrics = json.load(f)

    # -------------------------------------------------------------------------
    # 1. Model Comparison Chart
    # -------------------------------------------------------------------------
    print(">>> Generating Model Comparison Chart...")
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)

    models = ["Random Forest\nClassifier", "Logistic\nRegression", "Gradient Boosting\n(Regressor $R^2$)"]
    scores = [
        metrics["Random_Forest"]["Accuracy_mean"] * 100.0,
        metrics["Logistic_Regression"]["Accuracy_mean"] * 100.0,
        metrics["Gradient_Boosting"]["R2_mean"] * 100.0
    ]
    colors = ['#1565c0', '#2e7d32', '#6a1b9a']

    bars = ax.bar(models, scores, color=colors, alpha=0.88, edgecolor='#212121', width=0.48)
    ax.set_ylabel("Validation Performance Score (%)", fontweight="bold", labelpad=8)
    ax.set_ylim(0, 115)
    ax.set_title("Cross-Validated Performance of ML Models for Fault Prediction", fontweight="bold", pad=12)

    for bar, score in zip(bars, scores):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 2.5, f"{score:.2f}%",
                ha='center', va='bottom', fontsize=10.5, fontweight='bold')

    # Annotate baseline
    ax.axhline(50.0, color='#d32f2f', linestyle=':', linewidth=1.5, label="Random Guess / Raw Residue Baseline (50%)")
    ax.legend(loc="lower right", framealpha=0.95, edgecolor="#b0bec5")

    fig.tight_layout()
    out_comp = figures_dir / "fig_ml_model_comparison.png"
    fig.savefig(out_comp, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved: {out_comp}")

    # -------------------------------------------------------------------------
    # 2. Feature Importance Chart
    # -------------------------------------------------------------------------
    print(">>> Generating Feature Importance Chart...")
    rf_feat = metrics["Random_Forest"]["Feature_Importance"]
    feat_names = list(rf_feat.keys())[::-1]
    feat_vals = [rf_feat[k] * 100.0 for k in feat_names]

    # Clean label names
    label_map = {
        "bit_j": "Upper Bit Index $j$",
        "bit_i": "Lower Bit Index $i$",
        "bit_distance": "Bit Distance $d = |i - j|$",
        "distance_parity": "Bit-Distance Parity ($d$ mod 2)",
        "bit_j_parity": "Bit $j$ Parity",
        "bit_i_parity": "Bit $i$ Parity"
    }
    cleaned_labels = [label_map.get(k, k) for k in feat_names]

    fig, ax = plt.subplots(figsize=(8.5, 4.6), dpi=300)
    y_pos = np.arange(len(cleaned_labels))
    bars = ax.barh(y_pos, feat_vals, color='#0277bd', alpha=0.88, edgecolor='#01579b', height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cleaned_labels, fontsize=10)
    ax.set_xlabel("Relative Feature Importance (MDI, %)", fontweight="bold", labelpad=8)
    ax.set_title("Machine Learning Feature Importance in Datapath Fault Predictability", fontweight="bold", pad=12)
    ax.set_xlim(0, max(feat_vals) * 1.25)

    for bar, val in zip(bars, feat_vals):
        w = bar.get_width()
        ax.text(w + 0.8, bar.get_y() + bar.get_height() / 2.0, f"{val:.1f}%",
                ha='left', va='center', fontsize=9.5, fontweight='bold')

    fig.tight_layout()
    out_feat = figures_dir / "fig_ml_feature_importance.png"
    fig.savefig(out_feat, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved: {out_feat}")

    # -------------------------------------------------------------------------
    # 3. ML Prediction vs Bit-Distance Parity Theorem
    # -------------------------------------------------------------------------
    print(">>> Generating Prediction vs Theorem Comparison...")
    if pred_file.exists():
        df_pred = pd.read_csv(pred_file)
        
        # Theoretical formula from Theorem 2:
        # If distance is even: 100.0%. If distance is odd: 0.0% (raw residue).
        # High MSB bits (bit_j >= 22) elevated to 100% via dynamic range check.
        theo_fdr = []
        for _, r in df_pred.iterrows():
            d = int(r["bit_distance"])
            j = int(r["bit_j"])
            if d % 2 == 0:
                theo_fdr.append(100.0)
            elif j >= 22:
                theo_fdr.append(100.0) # Range check caught it
            else:
                theo_fdr.append(0.0)

        df_pred["theoretical_fdr"] = theo_fdr
        corr = np.corrcoef(df_pred["gbr_predicted_fdr"], df_pred["fdr"])[0, 1]

        fig, ax = plt.subplots(figsize=(7.5, 5.0), dpi=300)
        ax.scatter(df_pred["fdr"], df_pred["gbr_predicted_fdr"],
                   c='#00838f', alpha=0.75, edgecolors='#004d40', s=35, label=f"496 Double-Bit Pairs (Pearson $r = {corr:.3f}$)")
        
        # 1:1 Identity Line
        ax.plot([0, 100], [0, 100], 'r--', linewidth=2.0, label="Ideal 1:1 Concordance")

        ax.set_xlabel("Empirical Simulation FDR (%)", fontweight="bold", labelpad=8)
        ax.set_ylabel("ML-Predicted FDR (%) [Gradient Boosting]", fontweight="bold", labelpad=8)
        ax.set_title("Empirical Fault Detection vs Machine Learning Prediction", fontweight="bold", pad=12)
        ax.set_xlim(-5, 105)
        ax.set_ylim(-5, 105)
        ax.legend(loc="upper left", framealpha=0.95, edgecolor="#b0bec5")

        # Text box
        rmse_val = metrics["Gradient_Boosting"]["RMSE_mean"]
        ax.text(0.65, 0.12, f"RMSE = {rmse_val:.2f}%\n$R^2$ = {metrics['Gradient_Boosting']['R2_mean']:.3f}",
                transform=ax.transAxes, fontsize=10.5, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2f1", ec="#00695c"))

        fig.tight_layout()
        out_pred = figures_dir / "fig_ml_prediction_vs_theorem.png"
        fig.savefig(out_pred, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"[+] Saved: {out_pred}")


if __name__ == "__main__":
    generate_reports()
