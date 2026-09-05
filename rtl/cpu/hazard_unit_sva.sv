`timescale 1ns/1ps

/**
 * SystemVerilog Assertions (SVA) Checker for RISC-V Pipeline Hazard Unit.
 * Validates:
 * 1. Load-Use Hazard detection and mandatory Pipeline Stall/Bubble generation
 * 2. Branch/Jump misprediction pipeline flush
 * 3. Forwarding precedence: EX/MEM (newer) over MEM/WB (older)
 * 4. Zero-Register (x0) isolation invariant
 */
module hazard_unit_sva (
    input logic clk,
    input logic rst_n,
    
    input logic [4:0] rs1_addr_EX,
    input logic [4:0] rs2_addr_EX,
    input logic [4:0] rd_addr_MEM,
    input logic       RegWrite_MEM,
    input logic [4:0] rd_addr_WB,
    input logic       RegWrite_WB,
    
    input logic       MemRead_EX,
    input logic [4:0] rd_addr_EX,
    input logic [4:0] rs1_addr_ID,
    input logic [4:0] rs2_addr_ID,
    input logic       branch_taken_ID,
    input logic       jump_ID,
    
    input logic [1:0] forwardA_EX,
    input logic [1:0] forwardB_EX,
    input logic       stall_IF,
    input logic       stall_ID,
    input logic       flush_ID,
    input logic       flush_EX
);

    // SVA 1: Load-Use Hazard Stall Invariant
    always_comb begin
        if (rst_n && MemRead_EX && (rd_addr_EX != 5'd0) && 
            ((rd_addr_EX == rs1_addr_ID) || (rd_addr_EX == rs2_addr_ID))) begin
            assert (stall_IF == 1'b1 && stall_ID == 1'b1 && flush_EX == 1'b1)
                else $error("[SVA-HAZARD FAIL] Load-Use hazard did not trigger stall (stall_IF=1, stall_ID=1, flush_EX=1)!");
        end
    end

    // SVA 2: Branch Misprediction Flush Invariant
    always_comb begin
        if (rst_n && (branch_taken_ID || jump_ID)) begin
            assert (flush_ID == 1'b1)
                else $error("[SVA-HAZARD FAIL] Branch/Jump did not trigger flush_ID!");
        end
    end

    // SVA 3: Forwarding Priority Precedence (MEM over WB)
    always_comb begin
        if (rst_n && RegWrite_MEM && RegWrite_WB && (rd_addr_MEM != 5'd0) && (rd_addr_MEM == rd_addr_WB)) begin
            if (rs1_addr_EX == rd_addr_MEM) begin
                assert (forwardA_EX == 2'b10)
                    else $error("[SVA-HAZARD FAIL] Forwarding A did not prioritize EX/MEM over MEM/WB!");
            end
            if (rs2_addr_EX == rd_addr_MEM) begin
                assert (forwardB_EX == 2'b10)
                    else $error("[SVA-HAZARD FAIL] Forwarding B did not prioritize EX/MEM over MEM/WB!");
            end
        end
    end

    // SVA 4: Zero Register x0 Invariant (Never Forward to/from x0)
    always_comb begin
        if (rst_n) begin
            if (rd_addr_MEM == 5'd0 && rs1_addr_EX == 5'd0 && RegWrite_MEM) begin
                assert (forwardA_EX != 2'b10)
                    else $error("[SVA-HAZARD FAIL] Forwarding triggered on x0 from MEM stage!");
            end
            if (rd_addr_WB == 5'd0 && rs1_addr_EX == 5'd0 && RegWrite_WB) begin
                assert (forwardA_EX != 2'b01)
                    else $error("[SVA-HAZARD FAIL] Forwarding triggered on x0 from WB stage!");
            end
        end
    end

endmodule
