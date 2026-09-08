`timescale 1ns/1ps
// =============================================================================
// TMR_MAC – Triple Modular Redundancy (TMR) MAC Unit with Majority Voting
// =============================================================================
// Architecture:
//   - Three independent, identical 3-stage Multiply-Accumulate pipelines
//     (Core 0, Core 1, Core 2).
//   - Bitwise Majority Voter:
//       voted[i] = (C0[i] & C1[i]) | (C1[i] & C2[i]) | (C0[i] & C2[i])
//   - Zero-latency Hardware Error Masking: Mask single-core transient (SEU)
//     or permanent stuck-at faults without stalling or halting the CPU pipeline.
//   - Real-time Diagnostic Telemetry:
//       fault_detected: Asserted if any core deviates from the majority.
//       fault_channel[1:0]: Identifies precisely which core has failed.
// Standards:
//   - High-reliability Aerospace & Rad-Hard Computing Standard.
// =============================================================================

module tmr_mac #(
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
    output reg                          fault_detected,
    output reg         [1:0]            fault_channel
);

    // =========================================================================
    // CORE 0 PIPELINE
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
    // CORE 1 PIPELINE
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
    // CORE 2 PIPELINE
    // =========================================================================
    reg signed [IN_WIDTH-1:0]  c2_reg_a, c2_reg_b;
    reg signed [OUT_WIDTH-1:0] c2_reg_c;
    reg                        c2_valid_d1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c2_reg_a    <= {IN_WIDTH{1'b0}};
            c2_reg_b    <= {IN_WIDTH{1'b0}};
            c2_reg_c    <= {OUT_WIDTH{1'b0}};
            c2_valid_d1 <= 1'b0;
        end else begin
            c2_valid_d1 <= start;
            if (start) begin
                c2_reg_a <= a;
                c2_reg_b <= b;
                c2_reg_c <= c;
            end
        end
    end

    wire signed [2*IN_WIDTH-1:0] c2_product = c2_reg_a * c2_reg_b;

    reg signed [2*IN_WIDTH-1:0] c2_pipe_product;
    reg signed [OUT_WIDTH-1:0]  c2_pipe_c;
    reg                         c2_valid_d2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c2_pipe_product <= {(2*IN_WIDTH){1'b0}};
            c2_pipe_c       <= {OUT_WIDTH{1'b0}};
            c2_valid_d2     <= 1'b0;
        end else begin
            c2_valid_d2 <= c2_valid_d1;
            if (c2_valid_d1) begin
                c2_pipe_product <= c2_product;
                c2_pipe_c       <= c2_reg_c;
            end
        end
    end

    wire signed [OUT_WIDTH-1:0] c2_product_ext = {{ (OUT_WIDTH-2*IN_WIDTH){c2_pipe_product[2*IN_WIDTH-1]} }, c2_pipe_product};
    wire signed [OUT_WIDTH-1:0] c2_mac_result  = c2_product_ext + c2_pipe_c;

    reg signed [OUT_WIDTH-1:0] c2_out;
    reg                        c2_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            c2_out   <= {OUT_WIDTH{1'b0}};
            c2_valid <= 1'b0;
        end else begin
            c2_valid <= c2_valid_d2;
            if (c2_valid_d2) begin
                c2_out <= c2_mac_result;
            end
        end
    end

    // =========================================================================
    // BITWISE MAJORITY VOTER & FAULT DIAGNOSTICS
    // =========================================================================
    wire signed [OUT_WIDTH-1:0] voted_out;
    genvar i;
    generate
        for (i = 0; i < OUT_WIDTH; i = i + 1) begin : gen_majority_voter
            assign voted_out[i] = (c0_out[i] & c1_out[i]) | 
                                  (c1_out[i] & c2_out[i]) | 
                                  (c0_out[i] & c2_out[i]);
        end
    endgenerate

    wire voted_valid = (c0_valid & c1_valid) | (c1_valid & c2_valid) | (c0_valid & c2_valid);

    // Fault Detection & Channel Identification
    wire c0_fault = (c0_out != voted_out) || (c0_valid != voted_valid);
    wire c1_fault = (c1_out != voted_out) || (c1_valid != voted_valid);
    wire c2_fault = (c2_out != voted_out) || (c2_valid != voted_valid);

    wire any_fault = c0_fault | c1_fault | c2_fault;

    wire [1:0] enc_channel = c0_fault ? 2'b01 :
                             c1_fault ? 2'b10 :
                             c2_fault ? 2'b11 : 2'b00;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out            <= {OUT_WIDTH{1'b0}};
            valid          <= 1'b0;
            fault_detected <= 1'b0;
            fault_channel  <= 2'b00;
        end else begin
            out            <= voted_out;
            valid          <= voted_valid;
            fault_detected <= any_fault;
            fault_channel  <= enc_channel;
        end
    end

endmodule
