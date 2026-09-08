#!/usr/bin/env python3
"""
Data Preprocessing & Feature Engineering for Hardware Fault Analysis
Extracts structural, arithmetic, and physical bit-level features from fault injection datasets.
Outputs processed tabular data for ML classification, regression, and manifold learning.
"""

import os
import json
import csv
from pathlib import Path
import pandas as pd
import numpy as np


def get_bit_zone(bit_pos):
    """Partition bit positions into 4 architectural sensitivity tiers."""
    if bit_pos <= 7:
        return "LSB"
    elif bit_pos <= 15:
        return "MID"
    elif bit_pos <= 21:
        return "MSB_LOW"
    else:
        return "MSB_HIGH"


def preprocess_all(data_dir=None, output_dir=None):
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "data"
    else:
        data_dir = Path(data_dir)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "data"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Preprocessing datasets from: {data_dir}")

    # -------------------------------------------------------------------------
    # 1. Process Single-Bit Coverage
    # -------------------------------------------------------------------------
    cov_file = data_dir / "fault_injection_coverage.csv"
    single_rows = []
    if cov_file.exists():
        df_cov = pd.read_csv(cov_file)
        for _, r in df_cov.iterrows():
            pos = int(r["Bit_Position"])
            sig = str(r["Target_Signal"])
            inj = int(r["Injected"])
            det = int(r["Detected"])
            sdc = int(r["SDC"])
            fdr = float(r["FDR_Percent"])
            single_rows.append({
                "bit_position": pos,
                "bit_weight_log2": pos,
                "bit_parity": pos % 2,
                "bit_zone": get_bit_zone(pos),
                "target_signal": sig,
                "fault_type": "single_bit",
                "bit_distance": 0,
                "distance_parity": 0,
                "injected": inj,
                "detected": det,
                "sdc": sdc,
                "fdr": fdr,
                "is_detected": 1 if fdr >= 99.0 else 0
            })

    # -------------------------------------------------------------------------
    # 2. Process Stuck-At Coverage
    # -------------------------------------------------------------------------
    sa_file = data_dir / "stuck_at_coverage.csv"
    if sa_file.exists():
        df_sa = pd.read_csv(sa_file)
        for _, r in df_sa.iterrows():
            pos = int(r["Bit"])
            sig = str(r["Signal"])
            ftype = str(r["Model"])  # SA0 / SA1
            inj = int(r["Injected"])
            det = int(r["Detected"])
            sdc = int(r["SDC"])
            fdr = float(r["FDR_Percent"])
            single_rows.append({
                "bit_position": pos,
                "bit_weight_log2": pos,
                "bit_parity": pos % 2,
                "bit_zone": get_bit_zone(pos),
                "target_signal": sig,
                "fault_type": ftype,
                "bit_distance": 0,
                "distance_parity": 0,
                "injected": inj,
                "detected": det,
                "sdc": sdc,
                "fdr": fdr,
                "is_detected": 1 if fdr >= 99.0 else 0
            })

    df_single = pd.DataFrame(single_rows)
    out_single = output_dir / "processed_fault_features.csv"
    df_single.to_csv(out_single, index=False)
    print(f"[+] Exported single-bit & stuck-at dataset: {out_single} ({len(df_single)} rows)")

    # -------------------------------------------------------------------------
    # 3. Process Double-Bit Heatmaps (32b and 16b)
    # -------------------------------------------------------------------------
    double_rows = []
    
    # pipe_c 32b
    hm32_file = data_dir / "double_bit_heatmap_32b.csv"
    if hm32_file.exists():
        df_hm32 = pd.read_csv(hm32_file, index_col=0)
        # 32x32 matrix
        for i in range(32):
            for j in range(i + 1, 32):
                col_name = f"Bit_{j}"
                row_name = f"Bit_{i}"
                if row_name in df_hm32.index and col_name in df_hm32.columns:
                    fdr_val = float(df_hm32.loc[row_name, col_name])
                else:
                    # fallback symmetric
                    fdr_val = float(df_hm32.iloc[i, j])
                
                dist = j - i
                dist_parity = dist % 2
                double_rows.append({
                    "target_signal": "pipe_c",
                    "bit_i": i,
                    "bit_j": j,
                    "bit_distance": dist,
                    "distance_parity": dist_parity,
                    "bit_i_parity": i % 2,
                    "bit_j_parity": j % 2,
                    "same_bit_parity": 1 if (i % 2 == j % 2) else 0,
                    "bit_i_zone": get_bit_zone(i),
                    "bit_j_zone": get_bit_zone(j),
                    "bit_weight_i_log2": i,
                    "bit_weight_j_log2": j,
                    "fdr": fdr_val,
                    "is_detected": 1 if fdr_val >= 50.0 else 0,
                    "sdc_rate": 100.0 - fdr_val
                })

    # pipe_product 16b
    hm16_file = data_dir / "double_bit_heatmap_16b.csv"
    if hm16_file.exists():
        df_hm16 = pd.read_csv(hm16_file, index_col=0)
        for i in range(16):
            for j in range(i + 1, 16):
                col_name = f"Bit_{j}"
                row_name = f"Bit_{i}"
                if row_name in df_hm16.index and col_name in df_hm16.columns:
                    fdr_val = float(df_hm16.loc[row_name, col_name])
                else:
                    fdr_val = float(df_hm16.iloc[i, j])

                dist = j - i
                dist_parity = dist % 2
                double_rows.append({
                    "target_signal": "pipe_product",
                    "bit_i": i,
                    "bit_j": j,
                    "bit_distance": dist,
                    "distance_parity": dist_parity,
                    "bit_i_parity": i % 2,
                    "bit_j_parity": j % 2,
                    "same_bit_parity": 1 if (i % 2 == j % 2) else 0,
                    "bit_i_zone": get_bit_zone(i),
                    "bit_j_zone": get_bit_zone(j),
                    "bit_weight_i_log2": i,
                    "bit_weight_j_log2": j,
                    "fdr": fdr_val,
                    "is_detected": 1 if fdr_val >= 50.0 else 0,
                    "sdc_rate": 100.0 - fdr_val
                })

    df_double = pd.DataFrame(double_rows)
    out_double = output_dir / "double_bit_features.csv"
    df_double.to_csv(out_double, index=False)
    print(f"[+] Exported double-bit dataset: {out_double} ({len(df_double)} pairs)")

    return df_single, df_double


if __name__ == "__main__":
    preprocess_all()
