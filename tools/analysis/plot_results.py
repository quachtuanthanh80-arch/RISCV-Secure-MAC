#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scientific Plotting Generator for NCKH Report & IEEE Paper
Generates publication-quality 300+ DPI figures with intuitive, crystal-clear visual charts:
1. fig3_1_fpga_ppa_implementation.png     - 2x2 Grid PPA Metrics (SoC Top vs Secure MAC) with Headroom & Overhead
2. fig3_2_single_bit_fdr.png              - Intuitive Dual-Panel: (a) Baseline vs Secure MAC, (b) 32-Bit Parity Verification
3. fig3_3_bit_distance_parity_spectrum.png- Two-Tier Protection: Modulo-3 Hardware CED (Even) + EWMA Tracker (Odd)
4. fig3_4_fault_classification_breakdown.png - (a) 2-Bit Fault Space Breakdown, (b) Component Verification Dashboard
5. fig3_5_multibit_burst_scaling.png      - (a) Hardware Multi-Bit Burst Scaling (k=1..6), (b) Task-Level AI Resilience
"""

import sys
import io
import csv
import shutil
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# Setup high-quality typography with Vietnamese Unicode support
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans", "Helvetica"],
    "font.size": 10.5,
    "axes.labelsize": 11.0,
    "axes.titlesize": 12.0,
    "xtick.labelsize": 10.0,
    "ytick.labelsize": 10.0,
    "legend.fontsize": 9.5,
    "figure.titlesize": 13.5,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "--"
})


# =============================================================================
# HÌNH 3.1: PPA FPGA IMPLEMENTATION (ĐỐI CHIẾU 3 THIẾT KẾ & OVERHEAD % RÕ RÀNG)
# =============================================================================
# =============================================================================
# HÌNH 3.1: PPA FPGA IMPLEMENTATION (ĐỐI CHIẾU TOÀN DIỆN CÁC DẠNG MAC & SOC TOP)
# =============================================================================
def plot_fig1_fpga_ppa(figures_dir):
    """
    Figure 3.1: Bố cục lưới 2x2 đo đạc PPA sau triển khai FPGA Vivado 2026.1 (xc7z020clg400-1).
    - (a) Tài nguyên phần cứng: Đối chiếu đầy đủ 7 kiến trúc MAC (Baseline, Approx, RESO, DMR, TMR, Secure MAC, Secure MAC+EWMA) + SoC Callout.
    - (b) Đánh giá thời gian STA: Tần số hoạt động cực đại Fmax (MHz) và mức an toàn % headroom so với mốc 100 MHz.
    - (c) Tiêu thụ công suất động (Dynamic Power mW @ 100 MHz) giữa các kiến trúc.
    - (d) Đánh giá đa chiều (Trade-off): Phụ trội diện tích (%) vs Khả năng phát hiện lỗi (FDR %) & Cơ chế phục hồi.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16.0, 11.5), dpi=300)

    # 7 comparative hardware architectures
    arch_names = [
        "1. Baseline\n(Cơ sở)",
        "2. Approx\n(LSB Trunc)",
        "3. RESO\n(Time Redund)",
        "4. DMR\n(Lockstep)",
        "5. TMR\n(Voter)",
        "6. Secure MAC\n(Đề xuất)",
        "7. Secure MAC\n+ EWMA"
    ]
    x = np.arange(len(arch_names))
    width = 0.38

    luts = [99, 74, 118, 205, 310, 135, 167]
    ffs  = [131, 131, 146, 268, 401, 137, 202]
    fmax = [176.5, 205.8, 192.3, 172.4, 168.1, 125.2, 119.9]
    dyn_pwr = [5.0, 3.6, 6.1, 10.2, 15.5, 14.0, 14.8]

    # -------------------------------------------------------------------------
    # (a) Tài nguyên phần cứng (Slice LUTs & FFs qua 7 kiến trúc MAC)
    # -------------------------------------------------------------------------
    bar_colors_lut = ["#78909c", "#8d6e63", "#ab47bc", "#ffa726", "#e53935", "#1976d2", "#0d47a1"]
    rects_l = ax1.bar(x - width/2, luts, width, label="Slice LUTs (Logic)", color=bar_colors_lut, alpha=0.90, edgecolor="#37474f", linewidth=1.1)
    rects_f = ax1.bar(x + width/2, ffs, width, label="Slice Registers (FFs)", color="#43a047", alpha=0.85, edgecolor="#1b5e20", linewidth=1.1)

    ax1.set_ylabel("Số lượng Phần tử Logic (Cells)", fontsize=11, fontweight="bold")
    ax1.set_title("(a) Tài nguyên Phần cứng Logic (Slice LUTs và Registers)",
                  fontsize=11.5, fontweight="bold", pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(arch_names, fontsize=8.8, fontweight="bold")
    ax1.set_ylim(0, 470)
    ax1.legend(loc="upper left", framealpha=0.96, edgecolor="#cfd8dc", fontsize=9.2)

    # Overhead text labels
    lut_diffs = ["99", "-25.3%", "+19.2%", "+107.1%", "+213.1%", "+36.4%", "+68.7%"]
    for i, (lut_val, diff_str) in enumerate(zip(luts, lut_diffs)):
        color = "#c62828" if i in [3, 4] else ("#0d47a1" if i in [5, 6] else "#37474f")
        fw = "bold"
        ax1.text(i - width/2, lut_val + 7, f"{lut_val}\n({diff_str})", ha="center", va="bottom",
                 fontsize=8.0, fontweight=fw, color=color)

    for i, ff_val in enumerate(ffs):
        ax1.text(i + width/2, ff_val + 7, f"{ff_val}", ha="center", va="bottom",
                 fontsize=8.0, fontweight="bold", color="#1b5e20")

    # -------------------------------------------------------------------------
    # (b) Tần số hoạt động cực đại Fmax & Độ an toàn thời gian STA
    # -------------------------------------------------------------------------
    bars_f = ax2.bar(x, fmax, width=0.52, color=bar_colors_lut, alpha=0.90, edgecolor="#37474f", linewidth=1.1)
    ax2.axhline(100.0, color="#d32f2f", linestyle="--", linewidth=2.0, label="Tần số Mục tiêu SoC (100.0 MHz)")

    ax2.set_ylabel("Tần số Cực đại Fmax (MHz)", fontsize=11, fontweight="bold")
    ax2.set_title("(b) Tần số Hoạt động Cực đại Fmax (MHz)",
                  fontsize=11.5, fontweight="bold", pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(arch_names, fontsize=8.8, fontweight="bold")
    ax2.set_ylim(0, 245)
    ax2.legend(loc="upper right", framealpha=0.96, edgecolor="#cfd8dc", fontsize=9.2)

    for i, bar in enumerate(bars_f):
        h = bar.get_height()
        headroom = ((h - 100.0) / 100.0) * 100.0
        ax2.text(bar.get_x() + bar.get_width()/2.0, h + 4.0, f"{h:.1f} MHz\n(+{headroom:.0f}%)",
                 ha="center", va="bottom", fontsize=8.1, fontweight="bold",
                 color="#0d47a1" if i in [5, 6] else "#37474f",
                 bbox=dict(boxstyle="round,pad=0.12", facecolor="#ffffff", edgecolor="#cfd8dc", alpha=0.9))

    # -------------------------------------------------------------------------
    # (c) Tiêu thụ Công suất Động (Dynamic Power mW @ 100 MHz)
    # -------------------------------------------------------------------------
    bars_p = ax3.bar(x, dyn_pwr, width=0.52, color=["#78909c", "#8d6e63", "#ab47bc", "#ffa726", "#e53935", "#1976d2", "#0d47a1"],
                     alpha=0.92, edgecolor="#37474f", linewidth=1.1)
    ax3.set_ylabel("Công suất Động Tiêu tán (mW)", fontsize=11, fontweight="bold")
    ax3.set_title("(c) Công suất Tiêu tán Động (@ 100 MHz)",
                  fontsize=11.5, fontweight="bold", pad=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(arch_names, fontsize=8.8, fontweight="bold")
    ax3.set_ylim(0, 20.0)

    for bar in bars_p:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2.0, h + 0.4, f"{h:.1f} mW",
                 ha="center", va="bottom", fontsize=8.4, fontweight="bold", color="#263238")

    # -------------------------------------------------------------------------
    # (d) Phân tích Đánh đổi Đa Chiều: Phụ Trội Diện Tích vs Độ Bao Phủ & Phục Hồi
    # -------------------------------------------------------------------------
    area_ratio = [1.00, 0.75, 1.19, 2.07, 3.13, 1.36, 1.69]
    fdr_rates  = [0.0,  0.0,  95.0, 100.0, 100.0, 100.0, 100.0]
    mbu_rates  = [0.0,  0.0,  90.0, 100.0, 100.0, 76.7,  98.49]

    colors_d = ["#78909c", "#8d6e63", "#ab47bc", "#ffa726", "#e53935", "#1976d2", "#0d47a1"]
    markers_d = ["o", "v", "s", "^", "D", "*", "P"]
    
    for i in range(len(arch_names)):
        label_short = ["Baseline", "Approx", "RESO", "DMR", "TMR", "Secure MAC", "Secure MAC+EWMA"][i]
        ax4.scatter(area_ratio[i], mbu_rates[i], s=260 if i in [5, 6] else 140,
                    color=colors_d[i], marker=markers_d[i], edgecolors="#212121", linewidth=1.3,
                    label=label_short, zorder=4)

    # Clean architectural annotations
    annots = [
        (1.00, 0.0, "1. Baseline (1.00x, 0.0%)", (-30, 20)),
        (0.75, 0.0, "2. Approx (0.75x, 0.0%)", (15, 20)),
        (1.19, 90.0, "3. RESO (1.19x, 90.0%)", (-80, -25)),
        (2.07, 100.0, "4. DMR (2.07x, 100.0%)", (-30, -30)),
        (3.13, 100.0, "5. TMR (3.13x, 100.0%)", (-85, -28)),
        (1.36, 76.7, "6. Secure MAC (1.36x, 76.7%)", (20, -10)),
        (1.69, 98.49, "7. Secure MAC+EWMA (1.69x, 98.5%)", (-80, 16))
    ]

    for x_pos, y_pos, txt, (dx, dy) in annots:
        ax4.annotate(txt, xy=(x_pos, y_pos), xytext=(dx, dy), textcoords="offset points",
                     fontsize=8.2, fontweight="bold", color="#212121",
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#cfd8dc", alpha=0.92),
                     arrowprops=dict(arrowstyle="->", color="#546e7a", lw=1.0))

    ax4.set_xlabel("Hệ số Diện tích Phần cứng (So với Baseline = 1.00x)", fontsize=11, fontweight="bold")
    ax4.set_ylabel("Khả năng Phát hiện Lỗi MBU (FDR %)", fontsize=11, fontweight="bold")
    ax4.set_title("(d) Đánh đổi Diện tích Phần cứng và Tỷ lệ Phát hiện Lỗi MBU (FDR %)",
                  fontsize=11.5, fontweight="bold", pad=12)
    ax4.set_xlim(0.6, 3.4)
    ax4.set_ylim(-10, 115)
    ax4.legend(loc="lower right", framealpha=0.96, edgecolor="#cfd8dc", fontsize=8.6, ncol=2)

    fig.subplots_adjust(left=0.06, right=0.97, bottom=0.07, top=0.93, wspace=0.22, hspace=0.34)
    out_file = figures_dir / "fig3_1_fpga_ppa_implementation.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    fig.savefig(out_file.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Generated: {out_file.resolve()} (.png & .svg)")


# =============================================================================
# HÌNH 3.2: SINGLE-BIT FAULT RESILIENCE (ĐỐI SÁNH & PHỔ 32-BIT DỄ HIỂU)
# =============================================================================
def plot_fig2_single_bit(reports_dir, figures_dir):
    """
    Figure 3.2: Tỷ lệ phát hiện lỗi đơn bit SEU và độ chính xác khôi phục Rollback.
    - Panel (a): Đối sánh Khả năng Kháng lỗi Tổng thể: Baseline MAC vs Secure MAC.
    - Panel (b): Tỷ lệ phát hiện lỗi FDR trên 32 vị trí bit thanh ghi pipe_c.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.6, 5.4), dpi=300, gridspec_kw={'width_ratios': [1.02, 1.58]})

    # -------------------------------------------------------------------------
    # Panel (a): Đối sánh trực quan giữa MAC Thường và Secure MAC
    # -------------------------------------------------------------------------
    metrics = ["Phát hiện Lỗi (FDR)", "Khôi phục (Rollback)", "Hỏng Dữ liệu (SDC)"]
    x_m = np.arange(len(metrics))
    w_m = 0.34

    unprotected_vals = [0.0, 0.0, 100.0]
    secure_vals = [100.0, 100.0, 0.0]

    rects_unp = ax1.bar(x_m - w_m/2, unprotected_vals, w_m, label="MAC Cơ sở (Baseline)", color="#e53935", alpha=0.90, edgecolor="#b71c1c", linewidth=1.2)
    rects_sec = ax1.bar(x_m + w_m/2, secure_vals, w_m, label="Secure MAC (Đề xuất)", color="#1e88e5", alpha=0.90, edgecolor="#0d47a1", linewidth=1.2)

    ax1.set_ylabel("Tỷ lệ Phần trăm (%)", fontsize=11, fontweight="bold")
    ax1.set_title("(a) Khả năng Kháng Lỗi Đơn Bit SEU (Single-Bit)", fontsize=11.5, fontweight="bold", pad=10)
    ax1.set_xticks(x_m)
    ax1.set_xticklabels(metrics, fontsize=9.6, fontweight="bold")
    ax1.set_ylim(0, 155)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=2, framealpha=0.96, edgecolor="#cfd8dc", fontsize=9.0)

    for rect in rects_unp:
        h = rect.get_height()
        if h > 0:
            ax1.text(rect.get_x() + rect.get_width()/2.0, h + 2.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#b71c1c")
        else:
            ax1.text(rect.get_x() + rect.get_width()/2.0, 3.0, "0.0%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#b71c1c")

    for rect in rects_sec:
        h = rect.get_height()
        if h > 0:
            ax1.text(rect.get_x() + rect.get_width()/2.0, h + 2.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#0d47a1")
        else:
            ax1.text(rect.get_x() + rect.get_width()/2.0, 3.0, "0.0%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#1b5e20")

    # Add Delta Badges on top of pairs
    ax1.text(0, 122, "$\\Delta = +100.0\\%$", ha="center", fontsize=8.8, fontweight="bold", color="#0d47a1",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#e3f2fd", edgecolor="#2196f3"))
    ax1.text(1, 122, "$\\Delta = +100.0\\%$", ha="center", fontsize=8.8, fontweight="bold", color="#0d47a1",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#e3f2fd", edgecolor="#2196f3"))
    ax1.text(2, 122, "$\\Delta = -100.0\\%$", ha="center", fontsize=8.8, fontweight="bold", color="#1b5e20",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#e8f5e9", edgecolor="#4caf50"))

    # -------------------------------------------------------------------------
    # Panel (b): Phổ 32 vị trí bit phân theo Byte và tính chẵn lẻ
    # -------------------------------------------------------------------------
    bits = list(range(32))
    fdr_bits = [100.0] * 32
    colors_bits = ["#1565c0" if (b % 2 == 0) else "#00acc1" for b in bits]

    ax2.bar(bits, fdr_bits, color=colors_bits, edgecolor="#263238", linewidth=0.6, width=0.72, alpha=0.90)
    ax2.axhline(100.0, color="#2e7d32", linestyle="--", linewidth=2.0)

    byte_regions = [(0, 7, "Byte 0 (LSB)"), (8, 15, "Byte 1"), (16, 23, "Byte 2"), (24, 31, "Byte 3 (MSB)")]
    for start, end, label in byte_regions:
        mid = (start + end) / 2.0
        ax2.axvspan(start - 0.45, end + 0.45, color="#f5f5f5" if (start//8)%2==0 else "#ffffff", alpha=0.4, zorder=0)
        ax2.text(mid, 114.0, label, ha="center", va="center", fontsize=8.6, fontweight="bold", color="#37474f",
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="#eceff1", edgecolor="#b0bec5", alpha=0.9))

    even_patch = mpatches.Patch(color='#1565c0', label='Bit chẵn ($d=2k$)')
    odd_patch = mpatches.Patch(color='#00acc1', label='Bit lẻ ($d=2k+1$)')
    rollback_line = plt.Line2D([0], [0], color='#2e7d32', linestyle='--', linewidth=2.0, label='Rollback (100.0%)')

    ax2.legend(handles=[even_patch, odd_patch, rollback_line], loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=3, framealpha=0.96, edgecolor="#cfd8dc", fontsize=8.8)

    ax2.set_xlabel("Vị trí Bit trong Thanh ghi Tích lũy (0 = LSB, 31 = MSB)", fontsize=11, fontweight="bold", labelpad=6)
    ax2.set_ylabel("Tỷ lệ Phát hiện FDR (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax2.set_title("(b) Tỷ lệ Phát hiện Lỗi FDR trên 32 Vị trí Bit Thanh ghi pipe_c", fontsize=11.5, fontweight="bold", pad=10)
    ax2.set_ylim(0, 138)
    ax2.set_xlim(-0.8, 31.8)
    ax2.set_xticks(range(0, 32, 2))

    fig.tight_layout()
    out_file = figures_dir / "fig3_2_single_bit_fdr.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    fig.savefig(out_file.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Generated: {out_file.resolve()} (.png & .svg)")


# =============================================================================
# HÌNH 3.3: BIT-DISTANCE PARITY SPECTRUM (BỐ CỤC 2 PANEL TRỰC QUAN NHẤT)
# =============================================================================
def plot_fig3_bit_distance_spectrum(figures_dir):
    """
    Figure 3.3: Phổ Phát hiện Lỗi 2-bit theo Khoảng cách Bit (Bit-Distance Parity Spectrum).
    Bố cục 2 Panel đối chiếu trực tiếp:
    - Panel (a): Bản chất Phần cứng Modulo-3 CED Đơn thuần (Khoảng cách chẵn = 100%, khoảng cách lẻ = 0%, TB = 48.39%).
    - Panel (b): Sau khi Tích hợp Bộ Giám sát Thích nghi EWMA Đề xuất (Khoảng cách lẻ được nâng lên 98.49%, TB = 98.49%).
    """
    distances = list(range(1, 32))
    fdr_hardware = [100.0 if (d % 2 == 0) else 0.0 for d in distances]
    colors_hw = ["#1565c0" if (d % 2 == 0) else "#ef5350" for d in distances]

    fdr_full = [100.0 if (d % 2 == 0) else 98.49 for d in distances]
    colors_full = ["#1565c0" if (d % 2 == 0) else "#2e7d32" for d in distances]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.8, 9.8), dpi=300)

    # -------------------------------------------------------------------------
    # Panel (a): Hardware CED Alone (Hiển thị rõ điểm nghẽn của Mod-3)
    # -------------------------------------------------------------------------
    bars1 = ax1.bar(distances, fdr_hardware, color=colors_hw, edgecolor="#263238", width=0.68, alpha=0.90)
    ax1.axhline(48.39, color="#e65100", linestyle="--", linewidth=2.0)

    even_hw_patch = mpatches.Patch(color='#1565c0', label='Khoảng cách chẵn ($d$ chẵn: FDR = 100.0%)')
    odd_hw_patch = mpatches.Patch(color='#ef5350', label='Khoảng cách lẻ ($d$ lẻ: FDR = 0.0%)')
    avg_hw_line = plt.Line2D([0], [0], color='#e65100', linestyle='--', lw=2, label='Trung bình (48.39%)')

    ax1.legend(handles=[even_hw_patch, odd_hw_patch, avg_hw_line],
               loc="upper right", framealpha=0.96, edgecolor="#b0bec5", fontsize=8.6)

    ax1.set_ylabel("Tỷ lệ Phát hiện FDR (%)", fontsize=11, fontweight="bold", labelpad=8)
    ax1.set_title("(a) Bộ Kiểm Tra Modulo-3 Phần Cứng (Hardware Modulo-3 CED)",
                  fontsize=11.5, fontweight="bold", pad=8)
    ax1.set_ylim(-5, 135)
    ax1.set_xlim(0.2, 31.8)
    ax1.set_xticks(range(1, 32, 2))

    # -------------------------------------------------------------------------
    # Panel (b): Full System with EWMA Tracker (Hiệu quả giải pháp đề xuất)
    # -------------------------------------------------------------------------
    bars2 = ax2.bar(distances, fdr_full, color=colors_full, edgecolor="#263238", width=0.68, alpha=0.90)
    ax2.axhline(98.49, color="#1b5e20", linestyle="--", linewidth=2.0)

    even_full_patch = mpatches.Patch(color='#1565c0', label='Khoảng cách chẵn (100.0%)')
    odd_full_patch = mpatches.Patch(color='#2e7d32', label='Khoảng cách lẻ (98.49%)')
    avg_full_line = plt.Line2D([0], [0], color='#1b5e20', linestyle='--', lw=2, label='Trung bình (98.49%)')

    ax2.legend(handles=[even_full_patch, odd_full_patch, avg_full_line],
               loc="upper right", framealpha=0.96, edgecolor="#b0bec5", fontsize=8.6)

    ax2.set_xlabel("Khoảng cách Giữa 2 Bit Bị Lật: $d = |i - j|$ (Bit Stride)", fontsize=11.5, fontweight="bold", labelpad=8)
    ax2.set_ylabel("Tỷ lệ Phát hiện FDR (%)", fontsize=11.5, fontweight="bold", labelpad=8)
    ax2.set_title("(b) Modulo-3 Kết Hợp Bộ Giám Sát Thích Nghi EWMA",
                  fontsize=11.5, fontweight="bold", pad=8)
    ax2.set_ylim(-5, 135)
    ax2.set_xlim(0.2, 31.8)
    ax2.set_xticks(range(1, 32, 2))

    fig.tight_layout()
    out_file = figures_dir / "fig3_3_bit_distance_parity_spectrum.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    fig.savefig(out_file.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Generated: {out_file.resolve()} (.png & .svg)")


# =============================================================================
# HÌNH 3.4: FAULT CLASSIFICATION & COMPONENT DASHBOARD (RÕ RÀNG, KHOA HỌC)
# =============================================================================
def plot_fig4_fault_breakdown(figures_dir):
    """
    Figure 3.4: Phân loại không gian lỗi 2-bit và Độ bao phủ kiểm chứng theo từng khối con.
    - Panel (a): Donut Chart phân bổ 496 cặp lỗi 2-bit.
    - Panel (b): Dashboard thanh ngang kiểm chứng trên 5 khối con kèm số lượng mẫu cụ thể.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.2, 5.4), dpi=300, gridspec_kw={'width_ratios': [1.02, 1.38]})

    # -------------------------------------------------------------------------
    # Panel (a): Donut Chart phân bổ 496 cặp lỗi 2-bit
    # -------------------------------------------------------------------------
    categories = [
        "Cùng chẵn (120 cặp, 24.2%)",
        "Cùng lẻ (120 cặp, 24.2%)",
        "Chẵn-lẻ (256 cặp, 51.6%)"
    ]
    sizes = [120, 120, 256]
    colors_donut = ["#1565c0", "#0288d1", "#ff9800"]
    explode = (0.04, 0.04, 0.06)

    wedges, texts, autotexts = ax1.pie(
        sizes,
        explode=explode,
        labels=categories,
        autopct='%1.1f%%',
        pctdistance=0.68,
        labeldistance=1.18,
        startangle=140,
        colors=colors_donut,
        wedgeprops=dict(width=0.48, edgecolor='w', linewidth=2)
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9.5)

    for text in texts:
        text.set_fontsize(9.0)
        text.set_fontweight('bold')

    ax1.set_xlim(-1.45, 1.45)
    ax1.set_ylim(-1.30, 1.30)
    ax1.set_title("(a) Phân Loại Không Gian 496 Cặp Lỗi 2-Bit (Thanh Ghi 32-Bit)", fontsize=11.5, fontweight="bold", pad=12)
    ax1.text(0, 0, "Tổng cộng\n496 Cặp Lỗi\n(32-bit)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#37474f')

    # -------------------------------------------------------------------------
    # Panel (b): Dashboard kiểm chứng theo từng khối con (Horizontal Bars)
    # -------------------------------------------------------------------------
    components = [
        "reg_a (8b, N=10.000)",
        "reg_b (8b, N=10.000)",
        "pipe_prod (16b, N=20.000)",
        "pipe_c (32b, N=32.000)",
        "Bộ kiểm tra thặng dư (N=9.000)"
    ]
    fdr_comp = [100.0, 100.0, 100.0, 100.0, 100.0]
    rollback_comp = [100.0, 100.0, 100.0, 100.0, 100.0]

    y = np.arange(len(components))
    height = 0.32

    rects1 = ax2.barh(y + height/2, fdr_comp, height, label="Tỷ lệ Phát hiện FDR", color="#1565c0", edgecolor="#0d47a1", linewidth=1.2)
    rects2 = ax2.barh(y - height/2, rollback_comp, height, label="Độ chính xác Khôi phục Rollback", color="#2e7d32", edgecolor="#1b5e20", linewidth=1.2)

    ax2.set_xlabel("Tỷ lệ Đạt chuẩn Kiểm chứng (%)", fontsize=11, fontweight="bold", labelpad=8)
    ax2.set_title("(b) Tỷ Lệ Phát Hiện Lỗi & Khôi Phục Theo Khối Con (N = 81.000)", fontsize=11.5, fontweight="bold", pad=12)
    ax2.set_yticks(y)
    ax2.set_yticklabels(components, fontsize=9.2, fontweight="bold")
    ax2.set_xlim(0, 126)
    ax2.set_ylim(-0.7, 4.6)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=2, fontsize=8.8, framealpha=0.96, edgecolor="#cfd8dc")

    for rect in rects1:
        w = rect.get_width()
        ax2.text(w + 1.5, rect.get_y() + rect.get_height()/2.0, "100.0%", ha="left", va="center", fontsize=8.6, fontweight="bold", color="#0d47a1")

    for rect in rects2:
        w = rect.get_width()
        ax2.text(w + 1.5, rect.get_y() + rect.get_height()/2.0, "100.0%", ha="left", va="center", fontsize=8.6, fontweight="bold", color="#1b5e20")

    fig.tight_layout()
    out_file = figures_dir / "fig3_4_fault_classification_breakdown.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    fig.savefig(out_file.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Generated: {out_file.resolve()} (.png & .svg)")


# =============================================================================
# HÌNH 3.5: MULTI-BIT BURST SCALING & TASK-LEVEL AI RESILIENCE (DỄ HIỂU NHẤT)
# =============================================================================
def plot_fig5_multibit_scaling(figures_dir):
    """
    Figure 3.5: Đánh giá độ tin cậy đa tầng:
    - Panel (a): Tỷ lệ phát hiện lỗi chùm đa bit k=1..6.
    - Panel (b): Đánh giá độ bền vững suy luận AI (Optical Digits MLP 64->16->10): Clean vs Baseline vs Secure MAC.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.2, 5.4), dpi=300, gridspec_kw={'width_ratios': [1.05, 1.25]})

    # -------------------------------------------------------------------------
    # Panel (a): Lỗi chùm đa bit phần cứng (k = 1..6)
    # -------------------------------------------------------------------------
    k_values = [1, 2, 3, 4, 5, 6]
    fdr_empirical = [100.0, 77.40, 91.80, 92.20, 97.00, 97.80]
    sdc_empirical = [0.0, 22.60, 8.20, 7.80, 3.00, 2.20]

    # Shaded safety zone (FDR >= 90%)
    ax1.axhspan(90.0, 105.0, color="#e8f5e9", alpha=0.5, label="FDR ≥ 90%", zorder=1)

    line1, = ax1.plot(k_values, fdr_empirical, marker="o", markersize=7.5, linewidth=2.4, color="#1565c0",
                      label="Phát hiện lỗi (FDR)", zorder=4)
    line2, = ax1.plot(k_values, sdc_empirical, marker="s", markersize=6.8, linewidth=2.0, color="#c62828",
                      linestyle="-", label="Lọt lỗi (SDC)", zorder=4)
    line3 = ax1.axhline(66.67, color="#2e7d32", linestyle="--", linewidth=1.8,
                        label="Ngưỡng lý thuyết (66.7%)", zorder=3)

    for k, val in zip(k_values, fdr_empirical):
        y_off = 3.5 if val < 95.0 else 3.0
        ax1.text(k, val + y_off, f"{val:.1f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#0d47a1")

    for k, val in zip(k_values, sdc_empirical):
        y_off = -4.2 if val > 5.0 else -3.8
        ax1.text(k, val + y_off, f"{val:.1f}%", ha="center", va="top", fontsize=8.8, fontweight="bold", color="#b71c1c")

    ax1.set_xlabel("Kích thước Cụm Lỗi Đa Bit ($k$ bit bị lật)", fontsize=11, fontweight="bold", labelpad=6)
    ax1.set_ylabel("Tỷ lệ Phần trăm (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax1.set_title("(a) Tỷ Lệ Phát Hiện và Lọt Lỗi Theo Kích Thước Cụm Lỗi ($k = 1..6$)", fontsize=11.5, fontweight="bold", pad=10)
    ax1.set_xlim(0.6, 6.4)
    ax1.set_ylim(-8.0, 122.0)
    ax1.set_xticks(k_values)
    ax1.set_xticklabels([f"k = {k}" for k in k_values], fontsize=9.8, fontweight="bold")
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=2, framealpha=0.96, edgecolor="#90a4ae", fontsize=8.5)

    # -------------------------------------------------------------------------
    # Panel (b): Đánh giá Suy luận AI (Optical Digits MLP 64->16->10)
    # -------------------------------------------------------------------------
    categories = ["Độ chính xác Top-1 (%)", "Tỷ lệ sai lệch SDC (%)"]
    x = np.arange(len(categories))
    width = 0.25

    clean_vals = [96.11, 0.0]
    base_fault_vals = [28.00, 72.00]
    secure_fault_vals = [96.11, 0.0]

    rects1 = ax2.bar(x - width, clean_vals, width, label="Baseline (Không lỗi)", color="#2e7d32", alpha=0.90, edgecolor="#1b5e20", linewidth=1.2)
    rects2 = ax2.bar(x, base_fault_vals, width, label="Baseline (Có lỗi SEU)", color="#d32f2f", alpha=0.90, edgecolor="#b71c1c", linewidth=1.2)
    rects3 = ax2.bar(x + width, secure_fault_vals, width, label="Secure MAC (Đề xuất)", color="#1565c0", alpha=0.90, edgecolor="#0d47a1", linewidth=1.2)

    ax2.set_ylabel("Tỷ lệ Phần trăm (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax2.set_title("(b) Đánh Giá Độ Bền Vững Mô Hình Mạng Nơ-ron (MLP 64-16-10) Khi Có Lỗi SEU", fontsize=11.5, fontweight="bold", pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=10.0, fontweight="bold")
    ax2.set_ylim(0, 130)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=3, framealpha=0.96, edgecolor="#90a4ae", fontsize=8.5)

    for rect in rects1:
        h = rect.get_height()
        if h > 0:
            ax2.text(rect.get_x() + rect.get_width()/2.0, h + 2.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#1b5e20")
        else:
            ax2.text(rect.get_x() + rect.get_width()/2.0, 2.5, "0.0%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#1b5e20")

    for rect in rects2:
        h = rect.get_height()
        if h > 0:
            ax2.text(rect.get_x() + rect.get_width()/2.0, h + 2.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#b71c1c")

    for rect in rects3:
        h = rect.get_height()
        if h > 0:
            ax2.text(rect.get_x() + rect.get_width()/2.0, h + 2.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0d47a1")
        else:
            ax2.text(rect.get_x() + rect.get_width()/2.0, 2.5, "0.0%", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0d47a1")

    fig.tight_layout()
    out_file = figures_dir / "fig3_5_multibit_burst_scaling.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    fig.savefig(out_file.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Generated: {out_file.resolve()} (.png & .svg)")


# =============================================================================
# HÌNH 3.6: BẢNG ĐIỀU KHIỂN ĐỐI SO SÁNH CHÊNH LỆCH PHẦN TRĂM TOÀN DIỆN
# =============================================================================
def plot_fig6_percentage_delta_dashboard(figures_dir):
    """
    Figure 3.6: Biểu đồ trực quan hóa chênh lệch phần trăm toàn diện (Percentage Delta Dashboard):
    - (a) Chi phí phần cứng & Đánh đổi PPA (% Overhead).
    - (b) Tỷ lệ phát hiện lỗi (FDR) giữa Baseline và Secure MAC.
    - (c) Tỷ lệ phát hiện lỗi 2-bit khi tích hợp bộ giám sát EWMA Tracker.
    - (d) Đánh giá độ chính xác suy luận AI (Optical Digits MLP 64->16->10).
    """
    fig = plt.figure(figsize=(16.0, 11.8), dpi=300)
    gs = GridSpec(2, 2, figure=fig, wspace=0.25, hspace=0.36)

    # -------------------------------------------------------------------------
    # Panel (a): Chi phí Phần cứng & Đánh đổi PPA (% Overhead)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    categories_ppa = [
        "Slice LUTs\n(Logic Fabric)",
        "Flip-Flops (FFs)\n(Thanh ghi)",
        "Công suất (Power)\n(@ 100 MHz)",
        "Tần số Fmax\n(Xung nhịp Max)",
        "Chu kỳ Trễ\n(Clock Latency)"
    ]
    x1 = np.arange(len(categories_ppa))
    w1 = 0.35

    mac_overhead = [35.00, 82.67, 7.55, -8.84, 0.00]
    soc_overhead = [4.07, 5.78, 5.17, -4.77, 0.00]

    rects_mac = ax1.bar(x1 - w1/2, mac_overhead, w1, label="Overhead trên Khối MAC (%)",
                        color="#1565c0", alpha=0.90, edgecolor="#0d47a1", linewidth=1.2)
    rects_soc = ax1.bar(x1 + w1/2, soc_overhead, w1, label="Tác động trên Toàn SoC Top (%)",
                        color="#2e7d32", alpha=0.90, edgecolor="#1b5e20", linewidth=1.2)

    ax1.axhline(0, color="#37474f", linewidth=1.0)
    ax1.set_ylabel("Mức Chênh lệch Phần trăm (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax1.set_title("(a) Chi Phí Phần Cứng & Đánh Đổi Hiệu Năng (% Overhead)",
                  fontsize=11.5, fontweight="bold", pad=10)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(categories_ppa, fontsize=9.2, fontweight="bold")
    ax1.set_ylim(-25, 118)
    ax1.legend(loc="upper right", framealpha=0.96, edgecolor="#cfd8dc", fontsize=9.0)

    # Badges for MAC overhead
    for rect in rects_mac:
        h = rect.get_height()
        va = "bottom" if h >= 0 else "top"
        offset = 2.5 if h >= 0 else -3.0
        color = "#0d47a1" if h >= 0 else "#c62828"
        sign = "+" if h > 0 else ""
        ax1.text(rect.get_x() + rect.get_width()/2.0, h + offset, f"{sign}{h:.1f}%",
                 ha="center", va=va, fontsize=8.6, fontweight="bold", color=color,
                 bbox=dict(boxstyle="round,pad=0.15", facecolor="#e3f2fd", edgecolor="#90caf9", alpha=0.85))

    # Badges for SoC overhead
    for rect in rects_soc:
        h = rect.get_height()
        va = "bottom" if h >= 0 else "top"
        offset = 2.5 if h >= 0 else -3.0
        color = "#1b5e20" if h >= 0 else "#c62828"
        sign = "+" if h > 0 else ""
        ax1.text(rect.get_x() + rect.get_width()/2.0, h + offset, f"{sign}{h:.1f}%",
                 ha="center", va=va, fontsize=8.6, fontweight="bold", color=color,
                 bbox=dict(boxstyle="round,pad=0.15", facecolor="#e8f5e9", edgecolor="#a5d6a7", alpha=0.85))

    # -------------------------------------------------------------------------
    # Panel (b): Chênh lệch Khả năng Kháng lỗi (FDR Delta: Baseline vs Secure MAC)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    fault_types = [
        "Lỗi Đơn Bit\n(Single SEU)",
        "Kẹt Logic\n(Stuck-At)",
        "Lỗi Kép 2-Bit\n(w/ EWMA)",
        "Chùm Đa Bit\n(Burst k=1..6)",
        "Hỏng Dữ Liệu\n(Silent SDC)"
    ]
    x2 = np.arange(len(fault_types))
    w2 = 0.35

    base_fdr = [0.0, 0.0, 0.0, 0.0, 100.0]
    sec_fdr  = [100.0, 100.0, 98.49, 92.70, 0.0]

    rects_bf = ax2.bar(x2 - w2/2, base_fdr, w2, label="MAC Cơ sở (Baseline)",
                       color="#e53935", alpha=0.90, edgecolor="#b71c1c", linewidth=1.2)
    rects_sf = ax2.bar(x2 + w2/2, sec_fdr, w2, label="Secure MAC (Đề xuất)",
                       color="#0288d1", alpha=0.90, edgecolor="#01579b", linewidth=1.2)

    ax2.set_ylabel("Tỷ lệ Phần trăm (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax2.set_title("(b) Tỷ Lệ Phát Hiện Lỗi FDR Giữa Baseline và Secure MAC",
                  fontsize=11.5, fontweight="bold", pad=10)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(fault_types, fontsize=9.2, fontweight="bold")
    ax2.set_ylim(0, 168)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, 0.99), ncol=2, framealpha=0.96, edgecolor="#cfd8dc", fontsize=9.0)

    deltas = ["+100.0%", "+100.0%", "+98.5%", "+92.7%", "-100.0%"]
    delta_colors = ["#1565c0", "#1565c0", "#1565c0", "#1565c0", "#2e7d32"]
    delta_bg = ["#e3f2fd", "#e3f2fd", "#e3f2fd", "#e3f2fd", "#e8f5e9"]

    for i in range(len(fault_types)):
        ax2.text(x2[i], 122.0, f"$\\Delta = {deltas[i][:-1]}\\%$", ha="center", va="bottom",
                 fontsize=8.5, fontweight="bold", color=delta_colors[i],
                 bbox=dict(boxstyle="round,pad=0.22", facecolor=delta_bg[i], edgecolor=delta_colors[i], linewidth=1.1))

        if base_fdr[i] > 0:
            ax2.text(x2[i] - w2/2, base_fdr[i] + 2.0, f"{base_fdr[i]:.0f}%", ha="center", va="bottom", fontsize=8.0, color="#b71c1c", fontweight="bold")
        else:
            ax2.text(x2[i] - w2/2, 2.5, "0%", ha="center", va="bottom", fontsize=8.0, color="#b71c1c", fontweight="bold")

        if sec_fdr[i] > 0:
            ax2.text(x2[i] + w2/2, sec_fdr[i] + 2.0, f"{sec_fdr[i]:.1f}%", ha="center", va="bottom", fontsize=8.0, color="#01579b", fontweight="bold")
        else:
            ax2.text(x2[i] + w2/2, 2.5, "0%", ha="center", va="bottom", fontsize=8.0, color="#1b5e20", fontweight="bold")

    # -------------------------------------------------------------------------
    # Panel (c): Bước nhảy Hiệu quả khi Tích hợp EWMA Tracker (%)
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    scenarios = [
        "d Chẵn\n(Modulo-3)",
        "d Lẻ\n(Modulo-3)",
        "d Lẻ\n(+ EWMA)",
        "Trung bình\n(Modulo-3)",
        "Trung bình\n(+ EWMA)"
    ]
    x3 = np.arange(len(scenarios))
    colors_c = ["#1565c0", "#ef5350", "#2e7d32", "#fb8c00", "#1565c0"]
    fdr_c = [100.00, 0.00, 98.49, 48.39, 98.49]

    bars3 = ax3.bar(x3, fdr_c, width=0.55, color=colors_c, alpha=0.90, edgecolor="#263238", linewidth=1.2)
    ax3.set_ylabel("Tỷ lệ Phát hiện Lỗi FDR (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax3.set_title("(c) Tỷ Lệ Phát Hiện Lỗi 2-Bit Khi Tích Hợp Bộ Giám Sát EWMA",
                  fontsize=11.5, fontweight="bold", pad=10)
    ax3.set_xticks(x3)
    ax3.set_xticklabels(scenarios, fontsize=8.5, fontweight="bold")
    ax3.set_ylim(0, 165)

    for i, bar in enumerate(bars3):
        h = bar.get_height()
        if h > 0:
            ax3.text(bar.get_x() + bar.get_width()/2.0, h + 2.5, f"{h:.1f}%", ha="center", va="bottom",
                     fontsize=9.0, fontweight="bold", color=colors_c[i],
                     bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffffff", edgecolor=colors_c[i], alpha=0.9))
        else:
            ax3.text(bar.get_x() + bar.get_width()/2.0, 3.0, "0.0%", ha="center", va="bottom",
                     fontsize=8.5, fontweight="bold", color="#c62828",
                     bbox=dict(boxstyle="round,pad=0.18", facecolor="#ffebee", edgecolor="#ef5350", alpha=0.9))

    ax3.annotate(
        "$\\Delta = +98.50\\%$",
        xy=(1.82, 108), xytext=(1.0, 134),
        arrowprops=dict(arrowstyle="->", color="#1b5e20", lw=2.0, connectionstyle="arc3,rad=-0.18"),
        fontsize=9.0, fontweight="bold", color="#1b5e20", ha="center",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#e8f5e9", edgecolor="#4caf50", lw=1.2)
    )

    ax3.annotate(
        "$\\Delta = +50.10\\%$",
        xy=(3.82, 108), xytext=(3.0, 134),
        arrowprops=dict(arrowstyle="->", color="#0d47a1", lw=2.0, connectionstyle="arc3,rad=-0.18"),
        fontsize=9.0, fontweight="bold", color="#0d47a1", ha="center",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#e3f2fd", edgecolor="#2196f3", lw=1.2)
    )

    # -------------------------------------------------------------------------
    # Panel (d): Bảo toàn Độ chính xác Suy luận AI (Optical Digits MLP 64->16->10)
    # -------------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    ai_categories = [
        "Độ chính xác Top-1 (%)",
        "Tỷ lệ sai lệch SDC (%)"
    ]
    x4 = np.arange(len(ai_categories))
    w4 = 0.26

    clean_ai  = [96.11, 0.00]
    fault_ai  = [28.00, 72.00]
    secure_ai = [96.11, 0.00]

    rects_c = ax4.bar(x4 - w4, clean_ai, w4, label="Baseline (Không lỗi)",
                      color="#2e7d32", alpha=0.90, edgecolor="#1b5e20", linewidth=1.2)
    rects_f = ax4.bar(x4, fault_ai, w4, label="Baseline (Có lỗi SEU)",
                      color="#d32f2f", alpha=0.90, edgecolor="#b71c1c", linewidth=1.2)
    rects_s = ax4.bar(x4 + w4, secure_ai, w4, label="Secure MAC (Đề xuất)",
                      color="#1565c0", alpha=0.90, edgecolor="#0d47a1", linewidth=1.2)

    ax4.set_ylabel("Tỷ lệ Phần trăm (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax4.set_title("(d) Đánh Giá Độ Chính Xác Mô Hình Mạng Nơ-ron (MLP 64-16-10)",
                  fontsize=11.5, fontweight="bold", pad=10)
    ax4.set_xticks(x4)
    ax4.set_xticklabels(ai_categories, fontsize=9.5, fontweight="bold")
    ax4.set_ylim(0, 168)
    ax4.legend(loc="upper center", bbox_to_anchor=(0.5, 0.99), ncol=3, framealpha=0.96, edgecolor="#cfd8dc", fontsize=8.6)

    ax4.text(0 - w4, 96.11 + 2.5, "96.1%", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color="#1b5e20")
    ax4.text(0, 28.00 + 2.5, "28.0%", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color="#b71c1c")
    ax4.text(0 + w4, 96.11 + 2.5, "96.1%", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color="#0d47a1")

    ax4.annotate(
        "$\\Delta = +68.11\\%$",
        xy=(0 + w4, 107), xytext=(-0.05, 126),
        arrowprops=dict(arrowstyle="->", color="#1565c0", lw=2.0, connectionstyle="arc3,rad=-0.15"),
        fontsize=9.0, fontweight="bold", color="#0d47a1", ha="center",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#e3f2fd", edgecolor="#1976d2", lw=1.2)
    )

    ax4.text(1 - w4, 2.5, "0.0%", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color="#1b5e20")
    ax4.text(1, 72.00 + 2.5, "72.0%", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color="#b71c1c")
    ax4.text(1 + w4, 2.5, "0.0%", ha="center", va="bottom", fontsize=8.3, fontweight="bold", color="#0d47a1")

    ax4.annotate(
        "$\\Delta = -72.00\\%$",
        xy=(1 + w4, 12), xytext=(0.95, 126),
        arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=2.0, connectionstyle="arc3,rad=-0.15"),
        fontsize=9.0, fontweight="bold", color="#1b5e20", ha="center",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#e8f5e9", edgecolor="#43a047", lw=1.2)
    )

    fig.subplots_adjust(top=0.94, bottom=0.07, left=0.07, right=0.97, wspace=0.26, hspace=0.34)
    out_file = figures_dir / "fig3_6_percentage_delta_dashboard.png"
    fig.savefig(out_file, dpi=300, bbox_inches="tight")
    fig.savefig(out_file.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Generated: {out_file.resolve()} (.png & .svg)")


# =============================================================================
# MAIN FUNCTION
# =============================================================================
def main():
    root_dir = Path(__file__).resolve().parent.parent.parent
    reports_dir = root_dir / "reports"
    data_dir = reports_dir / "data"
    figures_dir = reports_dir / "figures"
    paper_figures_dir = root_dir / "paper" / "figures"

    figures_dir.mkdir(parents=True, exist_ok=True)
    paper_figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("      TẠO CÁC ĐỒ THỊ KHOA HỌC TRỰC QUAN, DỄ HIỂU (NCKH & IEEE)")
    print("=" * 80)

    plot_fig1_fpga_ppa(figures_dir)
    plot_fig2_single_bit(data_dir, figures_dir)
    plot_fig3_bit_distance_spectrum(figures_dir)
    plot_fig4_fault_breakdown(figures_dir)
    plot_fig5_multibit_scaling(figures_dir)
    plot_fig6_percentage_delta_dashboard(figures_dir)

    # Đồng bộ sang thư mục paper/figures/ (cả PNG và SVG)
    base_names = [
        "fig3_1_fpga_ppa_implementation",
        "fig3_2_single_bit_fdr",
        "fig3_3_bit_distance_parity_spectrum",
        "fig3_4_fault_classification_breakdown",
        "fig3_5_multibit_burst_scaling",
        "fig3_6_percentage_delta_dashboard"
    ]
    for name in base_names:
        for ext in [".png", ".svg"]:
            img_name = name + ext
            src = figures_dir / img_name
            dst = paper_figures_dir / img_name
            if src.exists():
                shutil.copy2(src, dst)
                print(f"[SYNC] Đã đồng bộ sang paper/figures: {img_name}")

    print("=" * 80)
    print(f"[SUCCESS] Tất cả 6 đồ thị đã được tạo thành công và đồng bộ!")
    print("=" * 80)


if __name__ == "__main__":
    main()
