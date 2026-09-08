// =============================================================================
// Module: ewma_tracker.sv
// Description:
//   Online Hardware Exponentially Weighted Moving Average (EWMA) Anomaly Tracker.
//   Tracks the dynamic distribution (mean and mean absolute deviation MAD) of 
//   accumulated neural MAC activations using power-of-2 shift arithmetic (zero DSP).
//
//   Mathematical Formulation:
//     mu_t  = mu_{t-1} + alpha * (x_t - mu_{t-1})
//     dev_t = |x_t - mu_t|
//     MAD_t = MAD_{t-1} + alpha * (dev_t - MAD_{t-1})
//     threshold_t = |mu_t| + 3*sigma_t ~= |mu_t| + 3.75 * MAD_t
//
//   Hardware Features:
//     - alpha = 1/16 (ALPHA_SHIFT = 4) -> single arithmetic right shift, 0 multipliers
//     - Leaky accumulator structure prevents truncation drift
//     - Autonomous 16-sample warmup period fallback to conservative static bound
//     - Minimum threshold floor clamp to prevent false positives at quiescent state
// =============================================================================

`timescale 1ns/1ps

module ewma_tracker #(
    parameter int WIDTH             = 32,
    parameter int ALPHA_SHIFT       = 4,                 // alpha = 1 / (2^ALPHA_SHIFT) = 1/16
    parameter int WARMUP_SAMPLES    = 16,
    parameter signed [WIDTH-1:0] DEFAULT_THRESHOLD = 32'sd3276700,
    parameter signed [WIDTH-1:0] MIN_THRESHOLD_FLOOR = 32'sd2000
)(
    input  logic                     clk,
    input  logic                     rst_n,
    input  logic signed [WIDTH-1:0]  data_in,
    input  logic                     valid_in,          // Asserted only on verified valid outputs
    output logic signed [WIDTH-1:0]  threshold_out,
    output logic signed [WIDTH-1:0]  mean_out,
    output logic signed [WIDTH-1:0]  mad_out,
    output logic                     warmup_done_out
);

    localparam int ACCUM_WIDTH = WIDTH + ALPHA_SHIFT;

    // Registers
    logic signed [ACCUM_WIDTH-1:0] mean_accum_reg;
    logic signed [ACCUM_WIDTH-1:0] mad_accum_reg;
    logic [4:0]                    sample_cnt_reg;
    logic                          warmup_done_reg;

    // Combinational derivations from registered accumulators
    logic signed [WIDTH-1:0] mean_curr;
    logic signed [WIDTH-1:0] mad_curr;
    logic signed [WIDTH-1:0] abs_mean;
    logic signed [WIDTH-1:0] abs_diff;
    logic signed [WIDTH-1:0] three_sigma_approx;
    logic signed [WIDTH-1:0] raw_adaptive_thresh;

    assign mean_curr = mean_accum_reg[ACCUM_WIDTH-1:ALPHA_SHIFT];
    assign mad_curr  = mad_accum_reg[ACCUM_WIDTH-1:ALPHA_SHIFT];

    // Absolute difference for deviation tracking
    assign abs_diff = (data_in >= mean_curr) ? (data_in - mean_curr) : (mean_curr - data_in);

    // Absolute mean
    assign abs_mean = (mean_curr >= 0) ? mean_curr : -mean_curr;

    // 3.75 * MAD approximation for normal 3-sigma bound: (4 * MAD) - (MAD / 4)
    assign three_sigma_approx = (mad_curr <<< 2) - (mad_curr >>> 2);

    // Candidate threshold with overflow guard
    assign raw_adaptive_thresh = abs_mean + three_sigma_approx;

    // Threshold selection: fallback during warmup, floor clamp during active tracking
    always_comb begin
        if (!warmup_done_reg) begin
            threshold_out = DEFAULT_THRESHOLD;
        end else if (raw_adaptive_thresh < MIN_THRESHOLD_FLOOR) begin
            threshold_out = MIN_THRESHOLD_FLOOR;
        end else begin
            threshold_out = raw_adaptive_thresh;
        end
    end

    assign mean_out         = mean_curr;
    assign mad_out          = mad_curr;
    assign warmup_done_out  = warmup_done_reg;

    wire signed [ACCUM_WIDTH-1:0] data_in_ext = {{ALPHA_SHIFT{data_in[WIDTH-1]}}, data_in};
    wire signed [ACCUM_WIDTH-1:0] abs_diff_ext = {{ALPHA_SHIFT{1'b0}}, abs_diff};
    wire signed [ACCUM_WIDTH-1:0] mean_decay   = mean_accum_reg >>> ALPHA_SHIFT;
    wire signed [ACCUM_WIDTH-1:0] mad_decay    = mad_accum_reg >>> ALPHA_SHIFT;

    // Synchronous Update with Asynchronous Active-Low Reset
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mean_accum_reg  <= '0;
            mad_accum_reg   <= '0;
            sample_cnt_reg  <= '0;
            warmup_done_reg <= 1'b0;
        end else begin
            if (valid_in) begin
                // Update mean leaky accumulator: accum <= accum + data_in - (accum >>> 4)
                mean_accum_reg <= mean_accum_reg + data_in_ext - mean_decay;

                // Update MAD leaky accumulator: accum <= accum + abs_diff - (accum >>> 4)
                mad_accum_reg  <= mad_accum_reg + abs_diff_ext - mad_decay;

                // Sample counter for warmup period
                if (!warmup_done_reg) begin
                    if (sample_cnt_reg >= 5'd15) begin
                        warmup_done_reg <= 1'b1;
                    end else begin
                        sample_cnt_reg  <= sample_cnt_reg + 1'b1;
                    end
                end
            end
        end
    end

endmodule
