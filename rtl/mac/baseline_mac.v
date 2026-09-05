`timescale 1ns/1ps
// =============================================================================
// Baseline_MAC – Khối MAC 8-bit × 8-bit + 32-bit cơ sở (Không có cơ chế bảo vệ)
// Kiến trúc: 3 tầng pipeline (Pipeline Stages = 3), độ trễ 3 chu kỳ xung nhịp
// Mục đích: Làm đối chứng (Baseline Reference) để đo đạc Silicon Overhead và PPA
// =============================================================================

module baseline_mac #(
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
    output reg                          valid
);

    // =========================================================================
    // TẦNG PIPELINE 1: Thanh ghi ngõ vào (Input Stage)
    // =========================================================================
    reg signed [IN_WIDTH-1:0]  reg_a, reg_b;
    reg signed [OUT_WIDTH-1:0] reg_c;
    reg                        valid_d1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_a    <= {IN_WIDTH{1'b0}};
            reg_b    <= {IN_WIDTH{1'b0}};
            reg_c    <= {OUT_WIDTH{1'b0}};
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

    // Mạch nhân tổ hợp 8x8 -> 16 bit có dấu
    wire signed [2*IN_WIDTH-1:0] product = reg_a * reg_b;

    // =========================================================================
    // TẦNG PIPELINE 2: Thanh ghi trung gian (Multiply -> Accumulate Stage)
    // =========================================================================
    reg signed [2*IN_WIDTH-1:0] pipe_product;
    reg signed [OUT_WIDTH-1:0]  pipe_c;
    reg                         valid_d2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pipe_product <= {(2*IN_WIDTH){1'b0}};
            pipe_c       <= {OUT_WIDTH{1'b0}};
            valid_d2     <= 1'b0;
        end else begin
            valid_d2 <= valid_d1;
            if (valid_d1) begin
                pipe_product <= product;
                pipe_c       <= reg_c;
            end
        end
    end

    // Mạch cộng tổ hợp 16-bit mở rộng dấu + 32-bit tích lũy
    wire signed [OUT_WIDTH-1:0] mac_result = pipe_product + pipe_c;

    // =========================================================================
    // TẦNG PIPELINE 3: Thanh ghi ngõ ra (Output Accumulator Stage)
    // =========================================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out   <= {OUT_WIDTH{1'b0}};
            valid <= 1'b0;
        end else begin
            valid <= valid_d2;
            if (valid_d2) begin
                out <= mac_result;
            end
        end
    end

endmodule
