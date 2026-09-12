`timescale 1ns/1ps

module approx_mac #(
    parameter int IN_WIDTH    = 8,
    parameter int OUT_WIDTH   = 32,
    parameter int APPROX_BITS = 4 // Number of lower product bits approximated/truncated
)(
    input  logic                         clk,
    input  logic                         rst_n,
    input  logic signed [IN_WIDTH-1:0]   a,
    input  logic signed [IN_WIDTH-1:0]   b,
    input  logic signed [OUT_WIDTH-1:0]  c,
    input  logic                         start,
    output logic signed [OUT_WIDTH-1:0]  out,
    output logic                         valid
);

    logic signed [IN_WIDTH-1:0]  reg_a, reg_b;
    logic signed [OUT_WIDTH-1:0] reg_c;
    logic                        valid_d1;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_a    <= '0;
            reg_b    <= '0;
            reg_c    <= '0;
            valid_d1 <= 1'b0;
        end else begin
            valid_d1 <= start;
            if (start) begin
                reg_a <= a;
                reg_b <= b;
                reg_c <= c;
            end
        end
    end

    wire signed [2*IN_WIDTH-1:0] full_exact_prod = reg_a * reg_b;

    // Truncate lower bits with midpoint rounding bias to eliminate carry chains
    wire [APPROX_BITS-1:0] approx_lsb = (APPROX_BITS > 0) ? {1'b1, {(APPROX_BITS-1){1'b0}}} : '0;
    wire signed [2*IN_WIDTH-1:0] approx_product = 
        $signed({ full_exact_prod[2*IN_WIDTH-1 : APPROX_BITS], approx_lsb });

    logic signed [2*IN_WIDTH-1:0] pipe_product;
    logic signed [OUT_WIDTH-1:0]  pipe_c;
    logic                         valid_d2;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pipe_product <= '0;
            pipe_c       <= '0;
            valid_d2     <= 1'b0;
        end else begin
            valid_d2 <= valid_d1;
            if (valid_d1) begin
                pipe_product <= approx_product;
                pipe_c       <= reg_c;
            end
        end
    end

    wire signed [OUT_WIDTH-1:0] pipe_product_ext = {{ (OUT_WIDTH-2*IN_WIDTH){pipe_product[2*IN_WIDTH-1]} }, pipe_product};
    wire signed [OUT_WIDTH-1:0] mac_result       = pipe_product_ext + pipe_c;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out   <= '0;
            valid <= 1'b0;
        end else begin
            valid <= valid_d2;
            if (valid_d2) begin
                out <= mac_result;
            end
        end
    end

endmodule
