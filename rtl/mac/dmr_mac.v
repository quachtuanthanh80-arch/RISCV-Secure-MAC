`timescale 1ns/1ps

module dmr_mac #(
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
    output logic                         rollback
);

    logic signed [IN_WIDTH-1:0]   core_reg_a[2], core_reg_b[2];
    logic signed [OUT_WIDTH-1:0]  core_reg_c[2];
    logic                         core_valid_d1[2];

    logic signed [2*IN_WIDTH-1:0] core_pipe_product[2];
    logic signed [OUT_WIDTH-1:0]  core_pipe_c[2];
    logic                         core_valid_d2[2];

    wire signed [OUT_WIDTH-1:0]   core_mac_result[2];
    logic signed [OUT_WIDTH-1:0]  core_out[2];
    logic                         core_valid[2];

    generate
        for (genvar i = 0; i < 2; i++) begin : gen_dmr_core
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

    // Lockstep comparator & Shadow Accumulator Rollback (ISO 26262)
    wire lockstep_mismatch = (core_valid[0] != core_valid[1]) || 
                             (core_valid_d2[0] && (core_mac_result[0] != core_mac_result[1])) ||
                             (core_valid[0] && (core_out[0] != core_out[1]));

    logic signed [OUT_WIDTH-1:0] shadow_accumulator;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out                <= '0;
            shadow_accumulator <= '0;
            valid              <= 1'b0;
            fault_detected     <= 1'b0;
            rollback           <= 1'b0;
        end else begin
            valid          <= core_valid[0];
            fault_detected <= lockstep_mismatch;

            if (lockstep_mismatch) begin
                // Phục hồi Rollback về trạng thái trước đó
                out      <= shadow_accumulator;
                rollback <= 1'b1;
            end else if (core_valid[0]) begin
                out                 <= core_out[0];
                shadow_accumulator  <= core_out[0];
                rollback            <= 1'b0;
            end else begin
                rollback <= 1'b0;
            end
        end
    end

endmodule
