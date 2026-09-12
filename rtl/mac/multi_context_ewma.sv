`timescale 1ns/1ps

module multi_context_ewma #(
    parameter int WIDTH          = 32,
    parameter int NUM_CONTEXTS   = 4,
    parameter int WARMUP_SAMPLES = 16,
    parameter int MIN_FLOOR      = 100
)(
    input  logic                             clk,
    input  logic                             rst_n,
    input  logic signed [WIDTH-1:0]          data_in,
    input  logic                             valid_in,
    input  logic [$clog2(NUM_CONTEXTS)-1:0]  context_id,
    input  logic                             context_reset,
    input  logic                             alpha_sel,
    output logic signed [WIDTH-1:0]          threshold_out,
    output logic                             warmup_done,
    output logic signed [WIDTH-1:0]          mean_out,
    output logic signed [WIDTH-1:0]          mad_out
);

    localparam int CNT_WIDTH = (WARMUP_SAMPLES > 1) ? $clog2(WARMUP_SAMPLES + 1) : 1;

    logic signed [WIDTH-1:0] ctx_mean_accum  [NUM_CONTEXTS];
    logic signed [WIDTH-1:0] ctx_mad_accum   [NUM_CONTEXTS];
    logic [CNT_WIDTH-1:0]    ctx_sample_cnt  [NUM_CONTEXTS];
    logic                    ctx_warmup_done [NUM_CONTEXTS];

    // Dual-alpha: 0 for fast adaptation (1/4), 1 for steady-state tracking (1/16)
    wire [2:0] shift_alpha = (alpha_sel === 1'b0) ? 3'd2 : 3'd4;

    logic signed [WIDTH-1:0] active_mean;
    logic signed [WIDTH-1:0] active_mad;
    logic [CNT_WIDTH-1:0]    active_cnt;
    logic                    active_done;

    assign active_mean = ctx_mean_accum[context_id];
    assign active_mad  = ctx_mad_accum[context_id];
    assign active_cnt  = ctx_sample_cnt[context_id];
    assign active_done = ctx_warmup_done[context_id];

    assign mean_out    = active_mean;
    assign mad_out     = active_mad;
    assign warmup_done = active_done;

    // Deviation from current mean: dev = |x - mean|
    wire signed [WIDTH-1:0] diff = data_in - active_mean;
    wire signed [WIDTH-1:0] abs_diff = (diff < 0) ? -diff : diff;

    // Approximating 3.75 * MAD as 4*MAD - MAD/4
    wire signed [WIDTH-1:0] mad_x4 = active_mad <<< 2;
    wire signed [WIDTH-1:0] mad_div4 = active_mad >>> 2;
    wire signed [WIDTH-1:0] mad_3_75 = mad_x4 - mad_div4;

    wire signed [WIDTH-1:0] abs_mean = (active_mean < 0) ? -active_mean : active_mean;
    wire signed [WIDTH-1:0] raw_threshold = abs_mean + mad_3_75;
    wire signed [WIDTH-1:0] clamped_threshold = (raw_threshold < MIN_FLOOR) ? MIN_FLOOR : raw_threshold;

    assign threshold_out = active_done ? clamped_threshold : MIN_FLOOR;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int i = 0; i < NUM_CONTEXTS; i++) begin
                ctx_mean_accum[i]  <= '0;
                ctx_mad_accum[i]   <= '0;
                ctx_sample_cnt[i]  <= '0;
                ctx_warmup_done[i] <= 1'b0;
            end
        end else if (context_reset) begin
            ctx_mean_accum[context_id]  <= '0;
            ctx_mad_accum[context_id]   <= '0;
            ctx_sample_cnt[context_id]  <= '0;
            ctx_warmup_done[context_id] <= 1'b0;
        end else if (valid_in) begin
            // Update selected context registers
            if (!active_done) begin
                ctx_mean_accum[context_id] <= active_mean + (diff >>> 2);
                ctx_mad_accum[context_id]  <= active_mad + ((abs_diff - active_mad) >>> 2);
                if (active_cnt >= (WARMUP_SAMPLES - 1)) begin
                    ctx_warmup_done[context_id] <= 1'b1;
                end else begin
                    ctx_sample_cnt[context_id]  <= active_cnt + 1'b1;
                end
            end else begin
                ctx_mean_accum[context_id] <= active_mean + (diff >>> shift_alpha);
                ctx_mad_accum[context_id]  <= active_mad + ((abs_diff - active_mad) >>> shift_alpha);
            end
        end
    end

endmodule
