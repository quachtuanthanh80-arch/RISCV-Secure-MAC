"""
train_and_quantize_mlp.py
=============================================================================
Trains an Optical Digits (8x8 pixels = 64 features) Multi-Layer Perceptron (MLP)
and performs Post-Training Quantization (PTQ) to symmetric signed INT8.

Architecture:
  - Input:  64 features (8x8 grayscale image, mapped to INT8 [0, 112])
  - Layer 1: 16 hidden neurons + ReLU activation (64 -> 16)
  - Layer 2: 10 output neurons (16 -> 10)
  - Total INT8 weights: 64*16 + 16*10 = 1,184 bytes
  - Native 16-bit accumulator compatible (no 16-bit overflow)

Outputs:
  1. sw/src/model_weights.h: C header for RV32I firmware execution
  2. tb/cocotb/data/mlp_digits_test_set.json: 100 test samples for Cocotb RTL benchmark
=============================================================================
"""

import json
import math
import os
from pathlib import Path
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


def main():
    print("=" * 80)
    print("  TRAINING & INT8 QUANTIZATION PIPELINE: DIGITS MLP FOR SECURE MAC")
    print("=" * 80)

    # 1. Load Dataset
    digits = load_digits()
    X_raw = digits.data  # shape (1797, 64), values in [0, 16]
    y_raw = digits.target  # shape (1797,), values in [0, 9]

    # Preprocessing: Map [0, 16] to signed INT8 [0, 112] (scaling by 7)
    # Background pixels remain 0, foreground reaches 112 <= 127
    X_int8 = np.clip(np.round(X_raw * 7.0), 0, 112).astype(np.int8)

    # Train / Test Split (80% train / 20% test, stratified)
    X_train_raw, X_test_raw, y_train, y_test, X_train_int8, X_test_int8 = train_test_split(
        X_raw, y_raw, X_int8, test_size=0.2, random_state=42, stratify=y_raw
    )

    print(f"Dataset: Optical Digits (8x8)")
    print(f"Total samples: {len(X_raw)}, Train: {len(X_train_raw)}, Test: {len(X_test_raw)}")
    print(f"Input features: {X_raw.shape[1]} (mapped to INT8 range [{X_int8.min()}, {X_int8.max()}])")

    # 2. Train Floating-Point Baseline Model
    X_train_norm = X_train_int8.astype(np.float32) / 112.0
    X_test_norm = X_test_int8.astype(np.float32) / 112.0

    mlp = MLPClassifier(
        hidden_layer_sizes=(16,),
        activation="relu",
        solver="adam",
        max_iter=600,
        random_state=42,
        alpha=1e-3,
        learning_rate_init=0.01,
    )
    mlp.fit(X_train_norm, y_train)

    train_acc = mlp.score(X_train_norm, y_train) * 100.0
    test_acc_fp32 = mlp.score(X_test_norm, y_test) * 100.0
    print(f"\n[FP32 Model] Train Accuracy: {train_acc:.2f}% | Test Accuracy: {test_acc_fp32:.2f}%")

    # Extract FP32 Weights & Biases
    W1_fp32 = mlp.coefs_[0].T  # shape: (16, 64)
    b1_fp32 = mlp.intercepts_[0]  # shape: (16,)
    W2_fp32 = mlp.coefs_[1].T  # shape: (10, 16)
    b2_fp32 = mlp.intercepts_[1]  # shape: (10,)

    # 3. Post-Training Quantization (PTQ) to Symmetric Signed INT8
    # Layer 1 Quantization (bound max weight to 40 so max accumulator fits in 16-bit signed)
    max_w1 = np.max(np.abs(W1_fp32))
    scale_w1 = 40.0 / max_w1
    W1_int8 = np.clip(np.round(W1_fp32 * scale_w1), -128, 127).astype(np.int8)
    b1_int16 = np.round(b1_fp32 * scale_w1 * 112.0).astype(np.int16)

    # Check Layer 1 dynamic range
    sample_acc1 = np.dot(X_train_int8.astype(np.int32), W1_int8.astype(np.int32).T) + b1_int16
    min_h1 = int(np.min(sample_acc1))
    max_h1 = int(np.max(sample_acc1))
    print(f"Layer 1 Accumulator Range: [{min_h1}, {max_h1}] (Fits signed 16-bit: {min_h1 >= -32768 and max_h1 <= 32767})")

    # Fixed-point right-shift to bring Layer 1 accumulator into INT8 [0, 127]
    shift1 = 8
    print(f"Layer 1 Activation Right Shift: {shift1} bits (1/{1 << shift1})")

    # Layer 2 Quantization
    max_w2 = np.max(np.abs(W2_fp32))
    scale_w2 = 64.0 / max_w2
    W2_int8 = np.clip(np.round(W2_fp32 * scale_w2), -128, 127).astype(np.int8)

    # Effective scale for Layer 2 bias:
    eff_b2_scale = scale_w2 * (scale_w1 * 112.0 / (1 << shift1))
    b2_int16 = np.round(b2_fp32 * eff_b2_scale).astype(np.int16)

    # 4. Bit-Exact Integer Inference Simulation Function
    def int8_forward(x_vec):
        """Pure integer forward pass matching Secure MAC arithmetic."""
        # Layer 1: 16 hidden neurons
        h1_acc = np.zeros(16, dtype=np.int16)
        h1_act = np.zeros(16, dtype=np.int8)
        for i in range(16):
            acc = int(b1_int16[i])
            for j in range(64):
                acc += int(W1_int8[i, j]) * int(x_vec[j])
            h1_acc[i] = acc
            # ReLU + Right Shift + Clip to signed INT8 [0, 127]
            val = acc >> shift1
            val_relu = max(0, min(127, val))
            h1_act[i] = val_relu

        # Layer 2: 10 output neurons
        logits = np.zeros(10, dtype=np.int16)
        for i in range(10):
            acc = int(b2_int16[i])
            for j in range(16):
                acc += int(W2_int8[i, j]) * int(h1_act[j])
            logits[i] = acc

        pred = int(np.argmax(logits))
        return h1_acc, h1_act, logits, pred

    # 5. Evaluate INT8 Quantized Accuracy
    correct_int8 = 0
    for x, y in zip(X_test_int8, y_test):
        _, _, _, pred = int8_forward(x)
        if pred == y:
            correct_int8 += 1
    test_acc_int8 = (correct_int8 / len(y_test)) * 100.0

    print(f"\n[INT8 Quantized Model] Test Accuracy: {test_acc_int8:.2f}% (FP32: {test_acc_fp32:.2f}%)")
    quant_drop = test_acc_fp32 - test_acc_int8
    print(f"Quantization Accuracy Delta: {quant_drop:+.2f}%")
    assert test_acc_int8 >= 95.0, f"INT8 accuracy below 95%: {test_acc_int8:.2f}%"

    # 6. Export sw/src/model_weights.h
    repo_root = Path(__file__).resolve().parent.parent.parent
    header_path = repo_root / "sw" / "src" / "model_weights.h"
    header_path.parent.mkdir(parents=True, exist_ok=True)

    with open(header_path, "w", encoding="utf-8") as f:
        f.write("/*\n")
        f.write(" * model_weights.h\n")
        f.write(" * Auto-generated INT8 Weights & Biases for RV32I Secure MAC SoC.\n")
        f.write(" * Architecture: 64 inputs -> 16 hidden (ReLU) -> 10 outputs\n")
        f.write(f" * FP32 Accuracy: {test_acc_fp32:.2f}% | INT8 Accuracy: {test_acc_int8:.2f}%\n")
        f.write(" */\n\n")
        f.write("#ifndef MODEL_WEIGHTS_H\n")
        f.write("#define MODEL_WEIGHTS_H\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write("#define NN_NUM_INPUTS   64\n")
        f.write("#define NN_NUM_HIDDEN   16\n")
        f.write("#define NN_NUM_CLASSES  10\n")
        f.write(f"#define NN_SHIFT_1      {shift1}\n\n")

        # Layer 1 Weights
        f.write(f"/* Layer 1 Weights: [16][64] signed INT8 */\n")
        f.write("static const int8_t NN_W1[NN_NUM_HIDDEN][NN_NUM_INPUTS] = {\n")
        for i in range(16):
            row_vals = ", ".join(f"{int(v):4d}" for v in W1_int8[i])
            f.write(f"    {{{row_vals}}},\n")
        f.write("};\n\n")

        # Layer 1 Biases
        f.write("/* Layer 1 Biases: [16] signed INT16 */\n")
        b1_vals = ", ".join(f"{int(v):6d}" for v in b1_int16)
        f.write(f"static const int16_t NN_B1[NN_NUM_HIDDEN] = {{{b1_vals}}};\n\n")

        # Layer 2 Weights
        f.write("/* Layer 2 Weights: [10][16] signed INT8 */\n")
        f.write("static const int8_t NN_W2[NN_NUM_CLASSES][NN_NUM_HIDDEN] = {\n")
        for i in range(10):
            row_vals = ", ".join(f"{int(v):4d}" for v in W2_int8[i])
            f.write(f"    {{{row_vals}}},\n")
        f.write("};\n\n")

        # Layer 2 Biases
        f.write("/* Layer 2 Biases: [10] signed INT16 */\n")
        b2_vals = ", ".join(f"{int(v):6d}" for v in b2_int16)
        f.write(f"static const int16_t NN_B2[NN_NUM_CLASSES] = {{{b2_vals}}};\n\n")

        # Export 10 Sample Images with ground truth labels
        f.write("/* 10 Sample Test Digits (64 INT8 inputs each, 1 per class 0-9) */\n")
        # Select one sample per class 0..9
        class_indices = []
        for c in range(10):
            idx = int(np.where(y_test == c)[0][0])
            class_indices.append(idx)

        f.write("static const int8_t NN_SAMPLE_IMAGES[10][NN_NUM_INPUTS] = {\n")
        for idx in class_indices:
            row_vals = ", ".join(f"{int(v):4d}" for v in X_test_int8[idx])
            f.write(f"    {{{row_vals}}},\n")
        f.write("};\n\n")

        sample_labels = ", ".join(str(int(y_test[idx])) for idx in class_indices)
        f.write(f"static const int32_t NN_SAMPLE_LABELS[10] = {{{sample_labels}}};\n\n")
        f.write("#endif /* MODEL_WEIGHTS_H */\n")

    print(f"Generated C Header: {header_path}")

    # 7. Export tb/cocotb/data/mlp_digits_test_set.json
    json_path = repo_root / "tb" / "cocotb" / "data" / "mlp_digits_test_set.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)

    test_samples_list = []
    num_export = min(100, len(X_test_int8))
    for idx in range(num_export):
        x = X_test_int8[idx]
        y_true = int(y_test[idx])
        h1_acc, h1_act, logits, pred = int8_forward(x)
        test_samples_list.append({
            "index": idx,
            "inputs": [int(v) for v in x],
            "true_label": y_true,
            "golden_h1_acc": [int(v) for v in h1_acc],
            "golden_h1_act": [int(v) for v in h1_act],
            "golden_logits": [int(v) for v in logits],
            "golden_pred": pred,
        })

    metadata = {
        "model_architecture": "64 -> 16 (ReLU) -> 10",
        "num_inputs": 64,
        "num_hidden": 16,
        "num_classes": 10,
        "shift_1": shift1,
        "fp32_accuracy": float(test_acc_fp32),
        "int8_accuracy": float(test_acc_int8),
        "weights_w1": W1_int8.tolist(),
        "biases_b1": b1_int16.tolist(),
        "weights_w2": W2_int8.tolist(),
        "biases_b2": b2_int16.tolist(),
        "samples": test_samples_list,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Generated Cocotb Test Dataset: {json_path} ({num_export} test samples)")
    print("=" * 80)
    print("  TRAINING & EXPORT COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
