`timescale 1ns/1ps

module secure_mac_sva #(
    parameter OUT_WIDTH = 32
)(
    input logic clk,
    input logic rst_n,
    input logic valid,
    input logic fault_detected,
    input logic rollback,
    input logic signed [OUT_WIDTH-1:0] out,
    input logic signed [OUT_WIDTH-1:0] shadow_acc
);

    // SVA 1: Khi phát hiện lỗi, ngõ ra lập tức rollback về shadow_acc và bật cờ rollback
    always @(posedge clk) begin
        if (rst_n && fault_detected) begin
            assert (rollback == 1'b1)
                else $error("[SVA-MAC FAIL] Rollback flag not asserted upon fault_detected!");
            assert (out == shadow_acc)
                else $error("[SVA-MAC FAIL] Output (%0d) did not rollback to shadow accumulator (%0d)!", out, shadow_acc);
        end
    end

    // SVA 2: Reset Clear Invariant
    always @(negedge rst_n) begin
        #1;
        assert (fault_detected == 1'b0)
            else $error("[SVA-MAC FAIL] fault_detected not 0 during reset!");
        assert (rollback == 1'b0)
            else $error("[SVA-MAC FAIL] rollback not 0 during reset!");
        assert (valid == 1'b0)
            else $error("[SVA-MAC FAIL] valid not 0 during reset!");
    end

    // SVA 3: Output Stability and Unknown Prevention
    always @(posedge clk) begin
        if (rst_n && valid) begin
            assert (!$isunknown(out))
                else $error("[SVA-MAC FAIL] 'out' has X/Z bits while valid is asserted!");
        end
    end

    // SVA 4: Rollback and Fault Detected Alignment
    always @(posedge clk) begin
        if (rst_n && fault_detected) begin
            assert (rollback == 1'b1)
                else $error("[SVA-MAC FAIL] fault_detected asserted without rollback!");
        end
    end

endmodule
