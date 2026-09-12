`timescale 1ns/1ps

module ewma_tracker #(
    parameter int WIDTH               = 32,
    parameter int ALPHA_SHIFT         = 4,                 // Slow alpha = 1 / (2^4) = 1/16
    parameter int ALPHA_FAST_SHIFT    = 2,                 // Fast alpha = 1 / (2^2) = 1/4
    parameter int WARMUP_SAMPLES      = 16,
    parameter signed [WIDTH-1:0] DEFAULT_THRESHOLD   = 32'sd3276700,
    parameter signed [WIDTH-1:0] MIN_THRESHOLD_FLOOR = 32'sd2000
)(
    input  logic                     clk,
    input  logic                     rst_n,
    input  logic signed [WIDTH-1:0]  data_in,
    input  logic                     valid_in,          // Asserted on verified valid outputs
    input  logic                     context_reset,     // Active-high pulse to reset EWMA on layer/context switch
    input  logic                     alpha_sel,         // 0: fast adaptation (alpha=1/4), 1: slow steady-state (alpha=1/16)
    output logic signed [WIDTH-1:0]  threshold_out,
    output logic signed [WIDTH-1:0]  mean_out,
    output logic signed [WIDTH-1:0]  mad_out,
    output logic                     warmup_done_out
);

    localparam int ACCUM_WIDTH = WIDTH + ALPHA_SHIFT;
    localparam int CNT_WIDTH   = (WARMUP_SAMPLES > 1) ? $clog2(WARMUP_SAMPLES + 1) : 2;

    logic signed [ACCUM_WIDTH-1:0] mean_accum_reg;
    logic signed [ACCUM_WIDTH-1:0] mad_accum_reg;
    logic [CNT_WIDTH-1:0]          sample_cnt_reg;
    logic                          warmup_done_reg;

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

    // alpha_sel = 0 chọn thích nghi nhanh (alpha=1/4), alpha_sel = 1 chọn ổn định (alpha=1/16)
    wire use_fast = (alpha_sel === 1'b0);

    wire signed [ACCUM_WIDTH-1:0] data_in_scaled = use_fast ?
        ({{ALPHA_FAST_SHIFT{data_in[WIDTH-1]}}, data_in} <<< (ALPHA_SHIFT - ALPHA_FAST_SHIFT)) :
        {{ALPHA_SHIFT{data_in[WIDTH-1]}}, data_in};

    wire signed [ACCUM_WIDTH-1:0] abs_diff_scaled = use_fast ?
        ({{ALPHA_FAST_SHIFT{1'b0}}, abs_diff} <<< (ALPHA_SHIFT - ALPHA_FAST_SHIFT)) :
        {{ALPHA_SHIFT{1'b0}}, abs_diff};

    wire signed [ACCUM_WIDTH-1:0] mean_decay = use_fast ?
        (mean_accum_reg >>> ALPHA_FAST_SHIFT) :
        (mean_accum_reg >>> ALPHA_SHIFT);

    wire signed [ACCUM_WIDTH-1:0] mad_decay = use_fast ?
        (mad_accum_reg >>> ALPHA_FAST_SHIFT) :
        (mad_accum_reg >>> ALPHA_SHIFT);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mean_accum_reg  <= '0;
            mad_accum_reg   <= '0;
            sample_cnt_reg  <= '0;
            warmup_done_reg <= 1'b0;
        end else if (context_reset) begin
            mean_accum_reg  <= '0;
            mad_accum_reg   <= '0;
            sample_cnt_reg  <= '0;
            warmup_done_reg <= 1'b0;
        end else begin
            if (valid_in) begin
                mean_accum_reg <= mean_accum_reg + data_in_scaled - mean_decay;
                mad_accum_reg  <= mad_accum_reg + abs_diff_scaled - mad_decay;

                if (!warmup_done_reg) begin
                    if (sample_cnt_reg >= (CNT_WIDTH'(WARMUP_SAMPLES - 1))) begin
                        warmup_done_reg <= 1'b1;
                    end else begin
                        sample_cnt_reg  <= sample_cnt_reg + 1'b1;
                    end
                end
            end
        end
    end

`ifndef SYNTHESIS
    ewma_tracker_sva #(
        .WIDTH(WIDTH),
        .WARMUP_SAMPLES(WARMUP_SAMPLES),
        .MIN_THRESHOLD_FLOOR(MIN_THRESHOLD_FLOOR)
    ) u_ewma_sva (
        .clk(clk),
        .rst_n(rst_n),
        .context_reset(context_reset),
        .valid_in(valid_in),
        .warmup_done(warmup_done_reg),
        .threshold_out(threshold_out),
        .mean_out(mean_curr),
        .mad_out(mad_curr)
    );
`endif

endmodule
