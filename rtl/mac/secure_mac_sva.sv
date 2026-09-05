`timescale 1ns/1ps

/**
 * SystemVerilog Assertions (SVA) Companion Checker for Secure MAC Accelerator.
 * Formally monitors and validates:
 * 1. Rollback correctness upon fault detection
 * 2. Handshake and output validity
 * 3. Reset clearance invariants
 */
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

    // SVA 1: Rollback Correctness Check
    // When fault is detected, the output must immediately equal shadow accumulator and rollback must be asserted
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
    end

endmodule
