#!/usr/bin/env python3
"""
Publication-Quality Generator for RTL Circuit Entity Graph with GNN Vulnerability Overlay
Generates:
  - reports/figures/fig_ml_06_gnn_vulnerability_map.png
  - paper/figures/fig_ml_06_gnn_vulnerability_map.png
Optimized with enlarged, prominent text fitting circular node frames for high-legibility IEEE printing.
"""

import os
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np


def generate_gnn_figure_and_drawio():
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "data" / "labeled_rtl_graph.json"
    
    with open(data_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    
    nodes_meta = graph_data["nodes"]
    edges_list = graph_data["edges"]

    # -------------------------------------------------------------------------
    # Layout Grid Definition (4 Stages, 7 Sub-Columns, 48 Physical RTL Nodes)
    # -------------------------------------------------------------------------
    # Canvas dimensions in inches
    fig_w, fig_h = 22.5, 12.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(-0.3, 22.2)
    ax.set_ylim(-1.5, 12.2)
    ax.axis("off")

    # Column X coordinates
    col_x = {
        0: 1.6,         # Stage 0: Primary Inputs
        1: 4.5,         # Stage 1a: Registers & Multiplier
        2: 7.2,         # Stage 1b: Mod-3 Tree Encoders
        3: 10.1,        # Stage 2a: Pipeline Regs
        4: 12.8,        # Stage 2b: Adder & Mod3 Checkers
        5: 15.5,        # Stage 2c: EWMA Monitor
        6: 19.4         # Stage 3: Shadow & Protection
    }

    # Node allocations per column
    col_nodes = {
        0: ['clk', 'rst_n', 'start', 'a', 'b', 'c'],
        1: ['reg_c_32', 'reg_c', 'product', 'reg_a', 'reg_b', 'valid_d1', 'valid_d1_n'],
        2: ['u_enc_a', 'u_enc_b', 'u_enc_c', 'a_mod3', 'b_mod3', 'c_mod3', 'ab_mod3_product'],
        3: ['pipe_product', 'pipe_c', 'pipe_ab_mod3', 'pipe_c_mod3', 'expected_mod3_reg', 'valid_d2', 'valid_d2_n'],
        4: ['mac_result', 'mac_result_32', 'u_enc_out', 'out_mod3', 'rns_calc', 'expected_mod3', 'mod3_mismatch', 'disagreement'],
        5: ['u_ewma', 'adaptive_threshold', 'active_threshold', 'ewma_mean', 'ewma_mad', 'ewma_warmup_done', 'range_anomaly', 'control_fault'],
        6: ['shadow_accumulator', 'out', 'fault_detected', 'rollback', 'valid']
    }

    # Compute node (x, y) coordinates
    node_pos = {}
    
    # Y-range for node placement (ensuring clean clearance below stage headers)
    y_top = 9.6
    y_bot = 0.7

    for c_idx, n_list in col_nodes.items():
        x = col_x[c_idx]
        count = len(n_list)
        y_positions = np.linspace(y_top, y_bot, count)
        for name, y in zip(n_list, y_positions):
            node_pos[name] = (x, y)

    # -------------------------------------------------------------------------
    # Draw Stage Background Enclosures (Curved Bounding Boxes)
    # -------------------------------------------------------------------------
    stage_boxes = [
        # (x_min, y_min, width, height, title, subtitle, bg_color, border_color)
        (0.2, 0.0, 2.8, 11.3,
         "STAGE 0: CỔNG NGÕ VÀO (PRIMARY INPUTS)",
         "[Toán hạng đầu vào & Xung nhịp clk, rst_n]",
         "#f8fafc", "#cbd5e1"),
        (3.3, 0.0, 5.2, 11.3,
         "STAGE 1: THANH GHI VÀO & MÃ HÓA MOD-3",
         "[Thanh ghi đầu vào, Bộ nhân 8x8 & Tree Encoders]",
         "#f0fdf4", "#86efac"),
        (8.9, 0.0, 8.0, 11.3,
         "STAGE 2: ALU NHÂN-CỘNG & THẶNG DƯ MOD-3 / EWMA",
         "[Cộng tích lũy 32b, Cây thặng dư RNS & Module Giám sát EWMA]",
         "#ecfeff", "#a5f3fc"),
        (17.3, 0.0, 4.3, 11.3,
         "STAGE 3: SHADOW CHECKPOINT & BẢO VỆ ROLLBACK",
         "[Shadow Checkpoint, Phục hồi dữ liệu & Cắt xung Clock]",
         "#fff1f2", "#fecdd3")
    ]

    for x_b, y_b, w_b, h_b, s_title, s_sub, bg_col, brd_col in stage_boxes:
        box = FancyBboxPatch((x_b, y_b), w_b, h_b,
                             boxstyle="round,pad=0.25,rounding_size=0.6",
                             facecolor=bg_col, edgecolor=brd_col,
                             linewidth=1.8, alpha=0.85, zorder=1)
        ax.add_patch(box)
        # Stage Titles
        ax.text(x_b + w_b / 2.0, y_b + h_b - 0.22, s_title,
                ha='center', va='top', fontsize=11.5, fontweight='bold',
                color='#1e293b', zorder=2)
        ax.text(x_b + w_b / 2.0, y_b + h_b - 0.58, s_sub,
                ha='center', va='top', fontsize=9.2, fontstyle='italic',
                color='#475569', zorder=2)

    # Main Chart Title
    ax.text(11.25, 11.9,
            "SƠ ĐỒ PHÂN TẦNG KIẾN TRÚC PHẦN CỨNG RTL VÀ ĐIỂM LỖ HỔNG DỰ ĐOÁN BỞI GNN",
            ha='center', va='center', fontsize=16.5, fontweight='bold',
            color='#0f172a', zorder=5)

    # -------------------------------------------------------------------------
    # Categorize Edges and Draw Wiring Connections
    # -------------------------------------------------------------------------
    # Edge Styling Table
    edge_styles = {
        'clock': {'color': '#94a3b8', 'lw': 1.1, 'ls': '--', 'rad': 0.10, 'alpha': 0.45},
        'reset': {'color': '#c084fc', 'lw': 1.2, 'ls': '--', 'rad': -0.12, 'alpha': 0.65},
        'alert': {'color': '#dc2626', 'lw': 2.0, 'ls': '-',  'rad': 0.08, 'alpha': 0.95},
        'ewma':  {'color': '#d97706', 'lw': 1.6, 'ls': '-',  'rad': 0.06, 'alpha': 0.90},
        'mod3':  {'color': '#16a34a', 'lw': 1.6, 'ls': '-',  'rad': 0.05, 'alpha': 0.90},
        'data':  {'color': '#0284c7', 'lw': 1.8, 'ls': '-',  'rad': 0.04, 'alpha': 0.90}
    }

    def get_edge_category(u, v):
        if u == 'clk': return 'clock'
        if u == 'rst_n': return 'reset'
        if u in ['disagreement', 'fault_detected', 'rollback', 'shadow_accumulator'] and v in ['out', 'fault_detected', 'rollback']:
            return 'alert'
        if u == 'mod3_mismatch' and v == 'disagreement':
            return 'alert'
        if 'ewma' in u or 'threshold' in u or 'anomaly' in u or 'control_fault' in u or \
           'ewma' in v or 'threshold' in v or 'anomaly' in v or 'control_fault' in v or \
           (u == 'mac_result' and v in ['u_ewma', 'range_anomaly']) or \
           (u == 'valid_d2' and v in ['u_ewma', 'control_fault']) or \
           (u in ['valid_d1', 'valid_d1_n'] and v == 'control_fault'):
            return 'ewma'
        if ('mod3' in u or 'mod3' in v or 'rns' in u or 'rns' in v or 'enc' in u or 'enc' in v):
            return 'mod3'
        return 'data'

    node_radius = 0.58  # Node circle radius in data coordinates

    # Draw all 73 edges with smooth arcs
    for u, v in edges_list:
        if u not in node_pos or v not in node_pos:
            continue
        cat = get_edge_category(u, v)
        st = edge_styles[cat]
        
        p1 = node_pos[u]
        p2 = node_pos[v]
        
        # Determine curvature direction based on layout flow
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        rad = st['rad']
        if cat == 'clock':
            rad = 0.08 if dy > 0 else -0.08
        elif cat == 'reset':
            rad = -0.10 if dy < 0 else 0.10
        elif cat == 'mod3' and abs(dx) < 0.1:
            rad = 0.20  # Intra-column vertical curve
        elif cat == 'ewma' and abs(dx) < 0.1:
            rad = -0.20
        elif dx < 0:
            rad = -0.25 # Backward connection (e.g. feedback/rollback)

        arrow = FancyArrowPatch(
            posA=p1, posB=p2,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=5.0,head_width=3.2",
            color=st['color'],
            linewidth=st['lw'],
            linestyle=st['ls'],
            alpha=st['alpha'],
            shrinkA=node_radius * 72 * (fig_w / 22.5),  # Points shrinkage
            shrinkB=node_radius * 72 * (fig_w / 22.5),
            zorder=3
        )
        ax.add_patch(arrow)

    # -------------------------------------------------------------------------
    # Draw Circular Hardware Entity Nodes with Enlarged, Well-Fitted Text
    # -------------------------------------------------------------------------
    # Vulnerability tier color mappings
    # CRITICAL (>= 0.70): Deep Red with White Text
    # HIGH (0.45 - 0.70): Rich Orange-Red with White Text
    # MEDIUM (0.20 - 0.45): Amber-Orange with Dark Text
    # LOW (< 0.20): Soft Cream-Yellow with Dark Text
    def get_tier_color(score):
        if score >= 0.70:
            return "#991b1b", "#ffffff", "#7f1d1d"  # fill, text, border
        elif score >= 0.45:
            return "#ea580c", "#ffffff", "#c2410c"
        elif score >= 0.20:
            return "#f59e0b", "#1e293b", "#d97706"
        else:
            return "#fef08a", "#1e293b", "#eab308"

    # Display text formatting rules
    name_display = {
        'ab_mod3_product': 'ab_mod3\nproduct',
        'pipe_product': 'pipe_\nproduct',
        'pipe_ab_mod3': 'pipe_ab\n_mod3',
        'pipe_c_mod3': 'pipe_c\n_mod3',
        'expected_mod3_reg': 'expected_\nmod3_reg',
        'expected_mod3': 'expected_\nmod3',
        'mac_result_32': 'mac_res\n_32',
        'mod3_mismatch': 'mod3_\nmismatch',
        'disagreement': 'dis-\nagreement',
        'adaptive_threshold': 'adaptive_\nthresh',
        'active_threshold': 'active_\nthresh',
        'ewma_mean': 'ewma_\nmean',
        'ewma_mad': 'ewma_\nmad',
        'ewma_warmup_done': 'ewma_\nwarmup',
        'range_anomaly': 'range_\nanomaly',
        'control_fault': 'control_\nfault',
        'shadow_accumulator': 'shadow_\nacc',
        'fault_detected': 'fault_\ndetect'
    }

    for name, (x, y) in node_pos.items():
        meta = nodes_meta[name]
        score = meta.get("vulnerability_score", 0.1)
        bw = meta.get("bit_width", 1)
        fill_col, text_col, border_col = get_tier_color(score)

        # Draw circle node
        circ = Circle((x, y), node_radius,
                      facecolor=fill_col, edgecolor=border_col,
                      linewidth=1.8, zorder=4)
        ax.add_patch(circ)

        # Label formatting
        disp_name = name_display.get(name, name)
        score_str = f"[{bw}b] {score:.2f}"

        # Font sizing based on text lines
        lines = disp_name.split('\n')
        if len(lines) == 1:
            name_y = y + 0.12
            score_y = y - 0.22
            name_fs = 11.0 if len(disp_name) <= 8 else 9.8
            score_fs = 9.8
        else:
            name_y = y + 0.16
            score_y = y - 0.26
            name_fs = 9.5
            score_fs = 9.2

        ax.text(x, name_y, disp_name,
                ha='center', va='center',
                fontsize=name_fs, fontweight='bold',
                color=text_col, zorder=5)
        ax.text(x, score_y, score_str,
                ha='center', va='center',
                fontsize=score_fs, fontweight='bold',
                color=text_col, zorder=5)

    # -------------------------------------------------------------------------
    # Draw Publication-Quality Legend Bar at Bottom
    # -------------------------------------------------------------------------
    # Legend background container
    leg_box = FancyBboxPatch((2.2, -1.3), 18.0, 1.05,
                             boxstyle="round,pad=0.15,rounding_size=0.4",
                             facecolor="#ffffff", edgecolor="#cbd5e1",
                             linewidth=1.4, alpha=0.98, zorder=6)
    ax.add_patch(leg_box)

    # 1. Vulnerability Tiers
    tiers = [
        ("Nguy cấp (≥ 0.70)", "#991b1b", "#7f1d1d"),
        ("Cao (0.45 - 0.70)", "#ea580c", "#c2410c"),
        ("Trung bình (0.20 - 0.45)", "#f59e0b", "#d97706"),
        ("Thấp (< 0.20)", "#fef08a", "#eab308")
    ]
    t_start_x = 2.6
    t_step_x = 2.6
    for i, (t_lbl, t_fill, t_brd) in enumerate(tiers):
        rx = t_start_x + i * t_step_x
        ry = -0.6
        rect = patches.Rectangle((rx, ry - 0.12), 0.35, 0.24,
                                 facecolor=t_fill, edgecolor=t_brd,
                                 linewidth=1.2, zorder=7)
        ax.add_patch(rect)
        ax.text(rx + 0.44, ry, t_lbl,
                ha='left', va='center', fontsize=9.2, fontweight='bold',
                color='#1e293b', zorder=7)

    # 2. Wire Connection Types
    wires = [
        ("Luồng Dữ liệu (23 dây)", "#0284c7", "-"),
        ("Mod-3 / RNS (14 dây)", "#16a34a", "-"),
        ("EWMA Monitor (14 dây)", "#d97706", "-"),
        ("Alert / Rollback (5 dây)", "#dc2626", "-"),
        ("Clock Tree (14 dây)", "#94a3b8", "--"),
        ("Reset (3 dây)", "#c084fc", "--")
    ]
    w_start_x = 2.6
    w_step_x = 2.9
    for j, (w_lbl, w_col, w_ls) in enumerate(wires):
        wx = w_start_x + (j % 6) * w_step_x
        wy = -1.02
        ax.plot([wx, wx + 0.45], [wy, wy],
                color=w_col, linestyle=w_ls, linewidth=2.2, zorder=7)
        ax.text(wx + 0.52, wy, w_lbl,
                ha='left', va='center', fontsize=9.0, fontweight='bold',
                color='#334155', zorder=7)

    # -------------------------------------------------------------------------
    # Save High-Resolution 300+ DPI Outputs
    # -------------------------------------------------------------------------
    rep_out = base_dir.parent.parent / "reports" / "figures" / "fig_ml_06_gnn_vulnerability_map.png"
    pap_out = base_dir.parent.parent / "paper" / "figures" / "fig_ml_06_gnn_vulnerability_map.png"
    
    rep_out.parent.mkdir(parents=True, exist_ok=True)
    pap_out.parent.mkdir(parents=True, exist_ok=True)

    fig.tight_layout()
    plt.savefig(rep_out, dpi=300, bbox_inches="tight")
    plt.savefig(pap_out, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"[SUCCESS] Exported High-Legibility GNN Map -> {rep_out}")
    print(f"[SUCCESS] Exported High-Legibility GNN Map -> {pap_out}")


if __name__ == "__main__":
    generate_gnn_figure_and_drawio()
