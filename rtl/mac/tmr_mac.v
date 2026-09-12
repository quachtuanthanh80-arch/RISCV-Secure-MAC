`timescale 1ns/1ps

module tmr_mac #(
    parameter int IN_WIDTH  = 8,
    parameter int OUT_WIDTH = 32
)(
    input  logic                         clk,
    input  logic                         rst_n,
    input  logic signed [IN_WIDTH-1:0]   a,
    input  logic signed [IN_WIDTH-1:0]   b,
    input  logic signed [OUT_WIDTH-1:0]  c,
    input  logic                         start,
    output logic signed [OUT_WIDTH-1:0]  out,
    output logic                         valid,
    output logic                         fault_detected,
    output logic        [1:0]            fault_channel
);

    logic signed [IN_WIDTH-1:0]   core_reg_a[3], core_reg_b[3];
    logic signed [OUT_WIDTH-1:0]  core_reg_c[3];
    logic                         core_valid_d1[3];

    logic signed [2*IN_WIDTH-1:0] core_pipe_product[3];
    logic signed [OUT_WIDTH-1:0]  core_pipe_c[3];
    logic                         core_valid_d2[3];

    wire signed [OUT_WIDTH-1:0]   core_mac_result[3];
    logic signed [OUT_WIDTH-1:0]  core_out[3];
    logic                         core_valid[3];

    generate
        for (genvar i = 0; i < 3; i++) begin : gen_tmr_core
            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    core_reg_a[i]    <= '0;
                    core_reg_b[i]    <= '0;
                    core_reg_c[i]    <= '0;
                    core_valid_d1[i] <= 1'b0;
                end else begin
                    core_valid_d1[i] <= start;
                    if (start) begin
                        core_reg_a[i] <= a;
                        core_reg_b[i] <= b;
                        core_reg_c[i] <= c;
                    end
                end
            end

            wire signed [2*IN_WIDTH-1:0] prod = core_reg_a[i] * core_reg_b[i];

            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    core_pipe_product[i] <= '0;
                    core_pipe_c[i]       <= '0;
                    core_valid_d2[i]     <= 1'b0;
                end else begin
                    core_valid_d2[i] <= core_valid_d1[i];
                    if (core_valid_d1[i]) begin
                        core_pipe_product[i] <= prod;
                        core_pipe_c[i]       <= core_reg_c[i];
                    end
                end
            end

            wire signed [OUT_WIDTH-1:0] prod_ext = {{ (OUT_WIDTH-2*IN_WIDTH){core_pipe_product[i][2*IN_WIDTH-1]} }, core_pipe_product[i]};
            assign core_mac_result[i] = prod_ext + core_pipe_c[i];

            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    core_out[i]   <= '0;
                    core_valid[i] <= 1'b0;
                end else begin
                    core_valid[i] <= core_valid_d2[i];
                    if (core_valid_d2[i]) begin
                        core_out[i] <= core_mac_result[i];
                    end
                end
            end
        end
    endgenerate

    // Bộ biểu quyết theo đa số từng bit (Bitwise Majority Voter)
    wire signed [OUT_WIDTH-1:0] voted_out;
    generate
        for (genvar bit_idx = 0; bit_idx < OUT_WIDTH; bit_idx++) begin : gen_majority_voter
            assign voted_out[bit_idx] = (core_out[0][bit_idx] & core_out[1][bit_idx]) | 
                                        (core_out[1][bit_idx] & core_out[2][bit_idx]) | 
                                        (core_out[0][bit_idx] & core_out[2][bit_idx]);
        end
    endgenerate

    wire voted_valid = (core_valid[0] & core_valid[1]) | 
                       (core_valid[1] & core_valid[2]) | 
                       (core_valid[0] & core_valid[2]);

    // Fault Detection & Channel Identification
    wire c0_fault = (core_out[0] != voted_out) || (core_valid[0] != voted_valid);
    wire c1_fault = (core_out[1] != voted_out) || (core_valid[1] != voted_valid);
    wire c2_fault = (core_out[2] != voted_out) || (core_valid[2] != voted_valid);

    wire any_fault = c0_fault | c1_fault | c2_fault;

    wire [1:0] enc_channel = c0_fault ? 2'b01 :
                             c1_fault ? 2'b10 :
                             c2_fault ? 2'b11 : 2'b00;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out            <= '0;
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
