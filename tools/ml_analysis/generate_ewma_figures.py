#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate EWMA Publication Figures for IEEE Transactions Manuscript:
1. fig_ml_04_fdr_static_vs_adaptive.png: MBU Fault Detection Rate & False Positive Rate comparison
2. fig_ml_05_ewma_convergence.png: Hardware convergence timeline and fault detection threshold
"""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.5,
    "axes.labelsize": 10.0,
    "axes.titlesize": 10.5,
    "xtick.labelsize": 9.0,
    "ytick.labelsize": 9.0,
    "legend.fontsize": 8.5,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "--"
})

def generate_ewma_plots():
    repo_root = Path(__file__).resolve().parent.parent.parent
    paper_fig_dir = repo_root / "paper" / "figures"
    reports_fig_dir = repo_root / "reports" / "figures"
    paper_fig_dir.mkdir(parents=True, exist_ok=True)
    reports_fig_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # FIGURE 1: FDR vs FPR (fig_ml_04_fdr_static_vs_adaptive.png)
    # -------------------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(6.0, 3.2), dpi=300)

    methods = ["Modulo-3 Thô\n(Raw CED)", "Ngưỡng Tĩnh\n(Static Limit)", "EWMA Thích Nghi\n(Đề Xuất, k=3.75)"]
    fdr_vals = [48.39, 76.27, 98.49]
    fpr_vals = [0.00, 1.85, 0.04]

    x = np.arange(len(methods))
    width = 0.34

    bars1 = ax1.bar(x - width/2, fdr_vals, width, label="FDR (%)",
                    color=["#e53935", "#fb8c00", "#2e7d32"], edgecolor="#263238", linewidth=1.1, alpha=0.92)
    ax1.set_ylabel("FDR (%)", fontsize=10, fontweight="bold", color="#1b5e20")
    ax1.set_ylim(0, 120)
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, fontsize=9.0, fontweight="bold")

    # Secondary axis for FPR
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, fpr_vals, width, label="FPR (%)",
                    color=["#b0bec5", "#90a4ae", "#0288d1"], edgecolor="#1a237e", linewidth=1.1, hatch="//", alpha=0.85)
    ax2.set_ylabel("FPR (%)", fontsize=10, fontweight="bold", color="#01579b")
    ax2.set_ylim(0, 3.2)
    ax2.grid(False)

    # Value callouts on FDR bars
    for i, (b, fdr) in enumerate(zip(bars1, fdr_vals)):
        ax1.text(b.get_x() + b.get_width()/2, fdr + 2.5, f"{fdr:.2f}%",
                 ha="center", va="bottom", fontsize=9.0, fontweight="bold",
                 color="#b71c1c" if i == 0 else ("#e65100" if i == 1 else "#1b5e20"))

    # Value callouts on FPR bars
    for b, fpr in zip(bars2, fpr_vals):
        ax2.text(b.get_x() + b.get_width()/2, fpr + 0.08, f"{fpr:.2f}%",
                 ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#01579b")

    # Callout arrow for improvement
    ax1.annotate("+50.10% FDR\n(FPR=0.04%)", xy=(2 - width/2, 98.49), xytext=(1.25, 104),
                 arrowprops=dict(facecolor="#2e7d32", shrink=0.08, width=1.4, headwidth=5),
                 fontsize=8.8, fontweight="bold", color="#1b5e20",
                 bbox=dict(boxstyle="round,pad=0.25", fc="#e8f5e9", ec="#2e7d32", lw=1.1))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.92, fontsize=8.5)

    plt.title("Độ Dung Lỗi MBU & Tính Khả Dụng Hệ Thống", fontsize=10.5, fontweight="bold", pad=8)
    plt.tight_layout()

    out_p1 = paper_fig_dir / "fig_ml_04_fdr_static_vs_adaptive.png"
    out_r1 = reports_fig_dir / "fig_ml_04_fdr_static_vs_adaptive.png"
    fig.savefig(out_p1, dpi=300, bbox_inches="tight")
    fig.savefig(out_r1, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved {out_p1}")

    # -------------------------------------------------------------------------
    # FIGURE 2: EWMA Hardware Convergence (fig_ml_05_ewma_convergence.png)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.0, 3.0), dpi=300)

    np.random.seed(42)
    cycles = 40
    t = np.arange(cycles)

    act = np.random.normal(0, 24, size=cycles).astype(int)
    
    mu = np.zeros(cycles)
    mad = np.zeros(cycles)
    tau = np.zeros(cycles)
    
    curr_mu = 0.0
    curr_mad = 0.0
    alpha = 1.0 / 16.0
    
    for i in range(cycles):
        x_val = act[i]
        curr_mu += alpha * (x_val - curr_mu)
        delta = abs(x_val - curr_mu)
        curr_mad += alpha * (delta - curr_mad)
        mu[i] = curr_mu
        mad[i] = curr_mad
        tau[i] = abs(curr_mu) + 3.75 * curr_mad

    fault_cycle = 28
    act_faulty = act.copy()
    act_faulty[fault_cycle] = 175

    ax.axvspan(0, 16, color="#e3f2fd", alpha=0.6, label="Hội tụ (16 CK)")
    ax.axvline(16, color="#1976d2", linestyle=":", linewidth=1.4)
    ax.text(8, 165, "Khởi động &\nỔn định", ha="center", va="center", fontsize=8.0, color="#0d47a1", fontweight="bold")

    ax.plot(t, act, color="#90a4ae", marker="o", markersize=3.0, linestyle="-", linewidth=0.9, label="Dữ liệu chuẩn ($X_t$)", alpha=0.7)
    ax.plot([fault_cycle], [act_faulty[fault_cycle]], marker="*", markersize=13, color="#d50000",
            label="Lỗi Kép MBU (SDC)", zorder=5)

    ax.plot(t, tau, color="#d84315", linestyle="-", linewidth=1.8, label=r"Ngưỡng $\tau_t$")
    ax.plot(t, -tau, color="#d84315", linestyle="-", linewidth=1.8)
    ax.fill_between(t, -tau, tau, color="#ffe0b2", alpha=0.32)

    ax.plot(t, mu, color="#1565c0", linestyle="--", linewidth=1.3, label=r"$\mu_t$ ($\alpha=1/16$)")

    ax.annotate("Bắt Lỗi: $|X_{28}| > \\tau_{28}$\nRollback 1 CK",
                xy=(fault_cycle, 175), xytext=(fault_cycle - 11, 138),
                arrowprops=dict(facecolor="#d50000", shrink=0.08, width=1.5, headwidth=5),
                fontsize=8.0, fontweight="bold", color="#b71c1c",
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffebee", ec="#c62828", lw=1.1))

    ax.set_xlabel("Chu Kỳ Xung Nhịp Phần Cứng (Cycles)", fontsize=9.5, fontweight="bold")
    ax.set_ylabel("Biên Độ Dữ Liệu", fontsize=9.5, fontweight="bold")
    ax.set_title("Đặc Tuyến Hội Tụ Thích Nghi & Bắt Lỗi MBU Sau 16 Chu Kỳ", fontsize=10.5, fontweight="bold", pad=8)
    ax.set_xlim(0, cycles - 1)
    ax.set_ylim(-130, 215)
    ax.legend(loc="lower left", framealpha=0.92, fontsize=8.0, ncol=2)

    plt.tight_layout()

    out_p2 = paper_fig_dir / "fig_ml_05_ewma_convergence.png"
    out_r2 = reports_fig_dir / "fig_ml_05_ewma_convergence.png"
    fig.savefig(out_p2, dpi=300, bbox_inches="tight")
    fig.savefig(out_r2, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved {out_p2}")

if __name__ == "__main__":
    generate_ewma_plots()
