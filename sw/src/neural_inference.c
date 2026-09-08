/*
 * neural_inference.c
 * =============================================================================
 * Bare-metal RV32I C Firmware executing End-to-End Neural Network Inference
 * accelerated by the Secure MAC (Modulo-3 CED + Rollback) IP via AXI4-Lite/MMIO.
 *
 * Model: Multi-Layer Perceptron (MLP) for Optical Digits Classification
 * Architecture: 64 inputs (8x8) -> 16 hidden (ReLU) -> 10 outputs (Argmax)
 * Quantization: Symmetric INT8 weights & activations, INT16 bias & accumulator
 * =============================================================================
 */

#include <stdint.h>
#include <stdbool.h>
#include "model_weights.h"

/* --------------------------------------------------------------------------
 * MMIO Register Map for Secure MAC IP (Base: 0x80000000)
 * -------------------------------------------------------------------------- */
#define MAC_BASE        0x80000000U
#define MAC_A_REG       ((volatile int32_t *)(MAC_BASE + 0x00))
#define MAC_B_REG       ((volatile int32_t *)(MAC_BASE + 0x04))
#define MAC_C_REG       ((volatile int32_t *)(MAC_BASE + 0x08))
#define MAC_START_REG   ((volatile uint32_t *)(MAC_BASE + 0x0C))
#define MAC_OUT_REG     ((volatile int32_t *)(MAC_BASE + 0x10))
#define MAC_STATUS_REG  ((volatile uint32_t *)(MAC_BASE + 0x14))

/* Data Memory Result Mailbox (in DMEM RAM) */
#define RESULT_BASE     ((volatile int32_t *)0x00000020U)

/* --------------------------------------------------------------------------
 * Perform Dot-Product Accumulation using Secure MAC Hardware:
 *   out = initial_bias + Sum_{i=0..n-1} (w[i] * a[i])
 * -------------------------------------------------------------------------- */
static int16_t mac_dot_product(const int8_t *w, const int8_t *a, int n, int16_t initial_bias) {
    int16_t acc = initial_bias;

    for (int i = 0; i < n; ++i) {
        // Feed operands to Secure MAC
        *MAC_A_REG = (int32_t)w[i];
        *MAC_B_REG = (int32_t)a[i];
        *MAC_C_REG = (int32_t)acc;

        // Trigger single-cycle execution
        *MAC_START_REG = 0x01U;

        // In synchronous AXI bus, readback provides the updated accumulator
        // If a fault occurred and was rolled back, MAC_OUT_REG holds the safe checkpoint
        acc = (int16_t)(*MAC_OUT_REG & 0xFFFF);
    }

    return acc;
}

/* --------------------------------------------------------------------------
 * End-to-End Neural Network Forward Pass:
 *   1. Layer 1: 16 neurons * 64 dot products + ReLU + right-shift 8
 *   2. Layer 2: 10 neurons * 16 dot products
 *   3. Argmax classification
 * -------------------------------------------------------------------------- */
int neural_network_predict(const int8_t *image) {
    int8_t hidden_activations[NN_NUM_HIDDEN];
    int16_t logits[NN_NUM_CLASSES];

    // Layer 1: 64 inputs -> 16 hidden neurons
    for (int h = 0; h < NN_NUM_HIDDEN; ++h) {
        int16_t acc = mac_dot_product(NN_W1[h], image, NN_NUM_INPUTS, NN_B1[h]);

        // Fixed-point scaling: right shift by NN_SHIFT_1
        int16_t scaled = acc >> NN_SHIFT_1;

        // ReLU Activation + clip to signed INT8 [0, 127]
        if (scaled < 0) {
            scaled = 0;
        } else if (scaled > 127) {
            scaled = 127;
        }
        hidden_activations[h] = (int8_t)scaled;
    }

    // Layer 2: 16 hidden -> 10 output classes
    for (int c = 0; c < NN_NUM_CLASSES; ++c) {
        logits[c] = mac_dot_product(NN_W2[c], hidden_activations, NN_NUM_HIDDEN, NN_B2[c]);
    }

    // Argmax: find class with maximum logit
    int best_class = 0;
    int16_t max_val = logits[0];
    for (int c = 1; c < NN_NUM_CLASSES; ++c) {
        if (logits[c] > max_val) {
            max_val = logits[c];
            best_class = c;
        }
    }

    return best_class;
}

/* --------------------------------------------------------------------------
 * Main Firmware Entry Point:
 *   Evaluates 10 test samples (1 of each digit 0-9)
 *   Writes predictions to DMEM for testbench assertion
 * -------------------------------------------------------------------------- */
int main(void) {
    int correct_count = 0;

    for (int s = 0; s < 10; ++s) {
        int predicted_class = neural_network_predict(NN_SAMPLE_IMAGES[s]);
        RESULT_BASE[s] = (int32_t)predicted_class;

        if (predicted_class == NN_SAMPLE_LABELS[s]) {
            correct_count++;
        }
    }

    // Write final score: correct_count (e.g. 10/10) to RESULT_BASE[10]
    RESULT_BASE[10] = (int32_t)correct_count;

    // Loop forever
    while (1) {
        __asm__ volatile ("nop");
    }

    return 0;
}
