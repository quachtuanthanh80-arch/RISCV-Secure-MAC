`timescale 1ns/1ps

module reso_mac #(
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
    output logic                         fault_detected
);

    typedef enum logic [1:0] {
        S_IDLE    = 2'd0,
        S_PHASE1  = 2'd1, // Direct computation R1 = A * B + C
        S_PHASE2  = 2'd2, // Shifted recomputation R2_raw = (A<<1)*B + (C<<1)
        S_COMPARE = 2'd3  // Compare R1 == (R2_raw >>> 1)
    } state_t;

    state_t state;

    logic signed [IN_WIDTH:0]    op_a;     // 1 extra bit for left shift
    logic signed [IN_WIDTH-1:0]  op_b;
    logic signed [OUT_WIDTH:0]   op_c;     // 1 extra bit for left shift
    logic signed [IN_WIDTH-1:0]  saved_a, saved_b;
    logic signed [OUT_WIDTH-1:0] saved_c;

    logic signed [OUT_WIDTH-1:0] res_phase1;
    logic signed [OUT_WIDTH:0]   res_phase2_raw;

    wire signed [2*IN_WIDTH:0]  shared_product = op_a * $signed({op_b[IN_WIDTH-1], op_b});
    wire signed [OUT_WIDTH+1:0] shared_prod_ext = {{ (OUT_WIDTH+1 - 2*IN_WIDTH){shared_product[2*IN_WIDTH]} }, shared_product};
    wire signed [OUT_WIDTH+1:0] shared_mac      = shared_prod_ext + op_c;
    wire signed [OUT_WIDTH-1:0] res_phase2_norm = $signed(res_phase2_raw[OUT_WIDTH:1]);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state          <= S_IDLE;
            op_a           <= '0;
            op_b           <= '0;
            op_c           <= '0;
            saved_a        <= '0;
            saved_b        <= '0;
            saved_c        <= '0;
            res_phase1     <= '0;
            res_phase2_raw <= '0;
            out            <= '0;
            valid          <= 1'b0;
            fault_detected <= 1'b0;
        end else begin
            case (state)
                S_IDLE: begin
                    valid          <= 1'b0;
                    fault_detected <= 1'b0;
                    if (start) begin
                        saved_a <= a;
                        saved_b <= b;
                        saved_c <= c;
                        op_a    <= $signed({a[IN_WIDTH-1], a});
                        op_b    <= b;
                        op_c    <= $signed({c[OUT_WIDTH-1], c});
                        state   <= S_PHASE1;
                    end
                end

                S_PHASE1: begin
                    res_phase1 <= shared_mac[OUT_WIDTH-1:0];
                    op_a       <= $signed({saved_a, 1'b0});
                    op_b       <= saved_b;
                    op_c       <= $signed({saved_c, 1'b0});
                    state      <= S_PHASE2;
                end

                S_PHASE2: begin
                    res_phase2_raw <= shared_mac[OUT_WIDTH:0];
                    state          <= S_COMPARE;
                end

                S_COMPARE: begin
                    if (res_phase1 == res_phase2_norm) begin
                        out            <= res_phase1;
                        fault_detected <= 1'b0;
                        valid          <= 1'b1;
                    end else begin
                        out            <= res_phase1;
                        fault_detected <= 1'b1;
                        valid          <= 1'b0;
                    end
                    state <= S_IDLE;
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
