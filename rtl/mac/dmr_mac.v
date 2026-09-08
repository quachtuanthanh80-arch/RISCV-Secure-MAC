`timescale 1ns/1ps
// =============================================================================
// DMR_MAC – Dual Modular Redundancy (DMR) Lockstep MAC Unit
// =============================================================================
// Architecture:
//   - Two fully redundant, identical 3-stage signed Multiply-Accumulate pipelines
//     (Core 0 = Primary Execution, Core 1 = Shadow Verification).
//   - Lockstep Comparator: Monitors pipeline validity and final accumulator values.
//   - Immediate fault detection: Flags single-event transients (SEU) and stuck-at
//     faults occurring in either pipeline without silent data corruption.
// Standards:
//   - Synthesizable Verilog-2001 / SystemVerilog, FPGA & ASIC friendly.
// =============================================================================

module dmr_mac #(
    parameter IN_WIDTH  = 8,
    parameter OUT_WIDTH = 32
)(
    input  wire                         clk,
    input  wire                         rst_n,
    input  wire signed [IN_WIDTH-1:0]   a,
    input  wire signed [IN_WIDTH-1:0]   b,
    input  wire signed [OUT_WIDTH-1:0]  c,
    input  wire                         start,
    output reg  signed [OUT_WIDTH-1:0]  out,
    output reg                          valid,
    output reg                          fault_detected
);

    // =========================================================================
    // CORE 0 (PRIMARY PIPELINE)
    // =========================================================================
    reg signed [IN_WIDTH-1:0]  c0_reg_a, c0_reg_b;
    reg signed [OUT_WIDTH-1:0] c0_reg_c;
    reg                        c0_valid_d1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c0_reg_a    <= {IN_WIDTH{1'b0}};
            c0_reg_b    <= {IN_WIDTH{1'b0}};
            c0_reg_c    <= {OUT_WIDTH{1'b0}};
            c0_valid_d1 <= 1'b0;
        end else begin
            c0_valid_d1 <= start;
            if (start) begin
                c0_reg_a <= a;
                c0_reg_b <= b;
                c0_reg_c <= c;
            end
        end
    end

    wire signed [2*IN_WIDTH-1:0] c0_product = c0_reg_a * c0_reg_b;

    reg signed [2*IN_WIDTH-1:0] c0_pipe_product;
    reg signed [OUT_WIDTH-1:0]  c0_pipe_c;
    reg                         c0_valid_d2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c0_pipe_product <= {(2*IN_WIDTH){1'b0}};
            c0_pipe_c       <= {OUT_WIDTH{1'b0}};
            c0_valid_d2     <= 1'b0;
        end else begin
            c0_valid_d2 <= c0_valid_d1;
            if (c0_valid_d1) begin
                c0_pipe_product <= c0_product;
                c0_pipe_c       <= c0_reg_c;
            end
        end
    end

    wire signed [OUT_WIDTH-1:0] c0_product_ext = {{ (OUT_WIDTH-2*IN_WIDTH){c0_pipe_product[2*IN_WIDTH-1]} }, c0_pipe_product};
    wire signed [OUT_WIDTH-1:0] c0_mac_result  = c0_product_ext + c0_pipe_c;

    reg signed [OUT_WIDTH-1:0] c0_out;
    reg                        c0_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c0_out   <= {OUT_WIDTH{1'b0}};
            c0_valid <= 1'b0;
        end else begin
            c0_valid <= c0_valid_d2;
            if (c0_valid_d2) begin
                c0_out <= c0_mac_result;
            end
        end
    end

    // =========================================================================
    // CORE 1 (SHADOW REDUNDANT PIPELINE)
    // =========================================================================
    reg signed [IN_WIDTH-1:0]  c1_reg_a, c1_reg_b;
    reg signed [OUT_WIDTH-1:0] c1_reg_c;
    reg                        c1_valid_d1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c1_reg_a    <= {IN_WIDTH{1'b0}};
            c1_reg_b    <= {IN_WIDTH{1'b0}};
            c1_reg_c    <= {OUT_WIDTH{1'b0}};
            c1_valid_d1 <= 1'b0;
        end else begin
            c1_valid_d1 <= start;
            if (start) begin
                c1_reg_a <= a;
                c1_reg_b <= b;
                c1_reg_c <= c;
            end
        end
    end

    wire signed [2*IN_WIDTH-1:0] c1_product = c1_reg_a * c1_reg_b;

    reg signed [2*IN_WIDTH-1:0] c1_pipe_product;
    reg signed [OUT_WIDTH-1:0]  c1_pipe_c;
    reg                         c1_valid_d2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c1_pipe_product <= {(2*IN_WIDTH){1'b0}};
            c1_pipe_c       <= {OUT_WIDTH{1'b0}};
            c1_valid_d2     <= 1'b0;
        end else begin
            c1_valid_d2 <= c1_valid_d1;
            if (c1_valid_d1) begin
                c1_pipe_product <= c1_product;
                c1_pipe_c       <= c1_reg_c;
            end
        end
    end

    wire signed [OUT_WIDTH-1:0] c1_product_ext = {{ (OUT_WIDTH-2*IN_WIDTH){c1_pipe_product[2*IN_WIDTH-1]} }, c1_pipe_product};
    wire signed [OUT_WIDTH-1:0] c1_mac_result  = c1_product_ext + c1_pipe_c;

    reg signed [OUT_WIDTH-1:0] c1_out;
    reg                        c1_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c1_out   <= {OUT_WIDTH{1'b0}};
            c1_valid <= 1'b0;
        end else begin
            c1_valid <= c1_valid_d2;
            if (c1_valid_d2) begin
                c1_out <= c1_mac_result;
            end
        end
    end

    // =========================================================================
    // LOCKSTEP COMPARATOR & OUTPUT STAGE
    // =========================================================================
    wire lockstep_mismatch = (c0_valid != c1_valid) || 
                             (c0_valid_d2 && (c0_mac_result != c1_mac_result)) ||
                             (c0_valid && (c0_out != c1_out));

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out            <= {OUT_WIDTH{1'b0}};
            valid          <= 1'b0;
            fault_detected <= 1'b0;
        end else begin
            valid          <= c0_valid;
            out            <= c0_out;
            fault_detected <= lockstep_mismatch;
        end
    end

endmodule
