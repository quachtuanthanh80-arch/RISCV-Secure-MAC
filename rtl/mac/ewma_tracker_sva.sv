`timescale 1ns/1ps

module ewma_tracker_sva #(
    parameter int WIDTH = 32,
    parameter int WARMUP_SAMPLES = 16,
    parameter signed [WIDTH-1:0] MIN_THRESHOLD_FLOOR = 32'sd2000
)(
    input  logic                     clk,
    input  logic                     rst_n,
    input  logic                     context_reset,
    input  logic                     valid_in,
    input  logic                     warmup_done,
    input  logic signed [WIDTH-1:0]  threshold_out,
    input  logic signed [WIDTH-1:0]  mean_out,
    input  logic signed [WIDTH-1:0]  mad_out
);

    logic prev_warmup_done;
    logic prev_context_reset;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prev_warmup_done   <= 1'b0;
            prev_context_reset <= 1'b0;
        end else begin
            prev_warmup_done   <= warmup_done;
            prev_context_reset <= context_reset;
        end
    end

    // 1. Reset Property: Reset must clear warmup state
    always @(negedge rst_n) begin
        #1;
        assert (!warmup_done)
            else $error("[SVA FAIL] EWMA reset did not clear warmup_done!");
    end

    // 2. Context Reset Property: A context_reset pulse must clear warmup_done on next cycle
    always @(posedge clk) begin
        if (rst_n && prev_context_reset) begin
            assert (!warmup_done)
                else $error("[SVA FAIL] EWMA context_reset did not clear warmup_done!");
        end
    end

    // 3. Floor Clamping Property: When warmup is completed, threshold must not be below floor
    always @(posedge clk) begin
        if (rst_n && warmup_done && !$isunknown(threshold_out)) begin
            assert (threshold_out >= MIN_THRESHOLD_FLOOR)
                else $error("[SVA FAIL] EWMA threshold violated MIN_THRESHOLD_FLOOR! threshold=%0d, floor=%0d", threshold_out, MIN_THRESHOLD_FLOOR);
        end
    end

    // 4. Warmup Monotonicity Property: warmup_done stays high until reset or context_reset
    always @(posedge clk) begin
        if (rst_n && !context_reset && prev_warmup_done) begin
            assert (warmup_done)
                else $error("[SVA FAIL] EWMA warmup_done de-asserted without reset or context_reset!");
        end
    end

endmodule
