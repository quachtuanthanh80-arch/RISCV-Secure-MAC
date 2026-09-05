`timescale 1ns/1ps
// Secure_MAC – Khối MAC 8-bit × 8-bit + 32-bit có khả năng kháng tấn công tiêm lỗi
// Kiến trúc: Luồng dữ liệu cơ sở + Mã thặng dư số học (Modulo 3)
module secure_mac #(
    parameter IN_WIDTH  = 8,
    parameter OUT_WIDTH = 32,
    // Ngưỡng phát hiện dị thường động (Calibrated Dynamic Range Checking):
    // Với ngõ vào INT8 ([-128, +127]), tích đơn cực đại là (-128)*(-128) = 16,384.
    // Đối với một lớp mạng nơ-ron với K = 200 tích lũy, miền tích lũy vật lý hợp lệ
    // là [-3,276,800, +3,276,800]. Lỗi lật bit ở các bit MSB đẩy kết quả vượt quá ngưỡng này
    // sẽ được kích hoạt bẫy dị thường để Rollback tức thời.
    parameter signed [OUT_WIDTH-1:0] ANOMALY_THRESHOLD = (OUT_WIDTH >= 32) ? 32'sd3276700 : {1'b0, {(OUT_WIDTH-2){1'b1}}, 1'b0}
)(
    input  wire                 clk,
    input  wire                 rst_n,
    input  wire signed [IN_WIDTH-1:0]  a,
    input  wire signed [IN_WIDTH-1:0]  b,
    input  wire signed [OUT_WIDTH-1:0] c,
    input  wire                 start,
    output reg signed  [OUT_WIDTH-1:0] out,
    output reg                  fault_detected,
    output reg                  valid,
    output reg                  rollback
);

    // Luồng dữ liệu chính (8x8 -> 16, + 32 -> 32)

    reg signed [IN_WIDTH-1:0]  reg_a, reg_b;
    reg signed [OUT_WIDTH-1:0] reg_c;
    reg valid_d1;

    wire signed [2*IN_WIDTH-1:0] product;
    wire signed [OUT_WIDTH-1:0]  mac_result;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_a <= 0;
            reg_b <= 0;
            reg_c <= 0;
            valid_d1 <= 0;
        end else begin
            valid_d1 <= start;
            if (start) begin
                reg_a <= a;
                reg_b <= b;
                reg_c <= c;
            end
        end
    end

    // TẦNG PIPELINE 1.5: Khối tổ hợp 1
    
    assign product = reg_a * reg_b;

    wire [1:0] a_mod3;
    wire [1:0] b_mod3;
    wire [1:0] c_mod3;

    // Mở rộng dấu (sign-extension) chuẩn xác khi OUT_WIDTH < 32 để bảo toàn số dư modulo 3
    wire signed [31:0] reg_c_32 = (OUT_WIDTH == 32) ? reg_c : { { (32-OUT_WIDTH){reg_c[OUT_WIDTH-1]} }, reg_c };
    mod3_encoder_8b  u_enc_a (.in(reg_a), .out(a_mod3));
    mod3_encoder_8b  u_enc_b (.in(reg_b), .out(b_mod3));
    mod3_encoder_32b u_enc_c (.in(reg_c_32), .out(c_mod3));

    wire [3:0] ab_mod3_product = a_mod3 * b_mod3;

    // TẦNG PIPELINE 2: Các thanh ghi trung gian
  
    reg signed [2*IN_WIDTH-1:0] pipe_product;
    reg signed [OUT_WIDTH-1:0]  pipe_c;
    reg [3:0]                   pipe_ab_mod3;
    reg [1:0]                   pipe_c_mod3;
    reg                         valid_d2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pipe_product <= 0;
            pipe_c       <= 0;
            pipe_ab_mod3 <= 0;
            pipe_c_mod3  <= 0;
            valid_d2     <= 0;
        end else begin
            valid_d2 <= valid_d1;
            if (valid_d1) begin
                pipe_product <= product;
                pipe_c       <= reg_c;
                pipe_ab_mod3 <= ab_mod3_product;
                pipe_c_mod3  <= c_mod3;
            end
        end
    end

 
    // TẦNG PIPELINE 2.5: Khối tổ hợp 2
    
    assign mac_result = pipe_product + pipe_c;

    wire [1:0] out_mod3;       
    wire [1:0] expected_mod3;  

    wire signed [31:0] mac_result_32 = (OUT_WIDTH == 32) ? mac_result : { { (32-OUT_WIDTH){mac_result[OUT_WIDTH-1]} }, mac_result };
    mod3_encoder_32b u_enc_out (.in(mac_result_32), .out(out_mod3));

    wire [3:0] rns_calc = pipe_ab_mod3 + pipe_c_mod3;
    reg  [1:0] expected_mod3_reg;

    always @(*) begin
        case (rns_calc)
            4'd0, 4'd3, 4'd6, 4'd9: expected_mod3_reg = 2'd0;
            4'd1, 4'd4, 4'd7:       expected_mod3_reg = 2'd1;
            4'd2, 4'd5, 4'd8:       expected_mod3_reg = 2'd2;
            default:                expected_mod3_reg = 2'd0; 
        endcase
    end
    assign expected_mod3 = expected_mod3_reg;

    // Khối phát hiện lỗi: Kết hợp Modulo-3 CED và Bộ kiểm tra Double-Check Ngưỡng An toàn (Sanity Check)
    wire mod3_mismatch = (expected_mod3 != out_mod3);
    
    // Sanity / Range Anomaly Detection: Phát hiện lỗi tích lũy vượt ngưỡng cực biên bất thường
    wire range_anomaly = (mac_result > ANOMALY_THRESHOLD || mac_result < -ANOMALY_THRESHOLD);

    // Tín hiệu kích hoạt Rollback khi Modulo-3 không khớp hoặc phát hiện dị thường
    wire disagreement = mod3_mismatch | range_anomaly;

    
    // TẦNG PIPELINE 3: Thanh ghi ngõ ra, Cờ lỗi & Khôi phục trạng thái
   
    reg signed [OUT_WIDTH-1:0] shadow_accumulator;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out                <= 0;
            shadow_accumulator <= 0;
            fault_detected     <= 0;
            rollback           <= 0;
            valid              <= 0;
        end else begin
            valid <= valid_d2;
            if (valid_d2) begin
                if (disagreement) begin
                    // Lỗi được phát hiện -> Kích hoạt Rollback
                    out            <= shadow_accumulator; // Khôi phục giá trị cũ hợp lệ
                    fault_detected <= 1'b1;
                    rollback       <= 1'b1;
                end else begin
                    // Hoạt động bình thường -> Cập nhật out và shadow
                    out                <= mac_result;
                    shadow_accumulator <= mac_result;     // Lưu lại kết quả hợp lệ
                    fault_detected     <= 1'b0;
                    rollback           <= 1'b0;
                end
            end else begin
                fault_detected <= 0;
                rollback       <= 0;
            end
        end
    end

`ifndef SYNTHESIS
    secure_mac_sva #(
        .OUT_WIDTH(OUT_WIDTH)
    ) u_sva (
        .clk(clk),
        .rst_n(rst_n),
        .valid(valid),
        .fault_detected(fault_detected),
        .rollback(rollback),
        .out(out),
        .shadow_acc(shadow_accumulator)
    );
`endif

endmodule


// Module hỗ trợ: Bộ mã hóa Modulo 3 cho số 8-bit có dấu dạng Cây nhị phân tối ưu
module mod3_encoder_8b (
    input  wire [7:0] in,
    output wire [1:0] out
);
    // Hàm cộng modulo 3 giữa 2 số dư 2-bit (1 tầng LUT4)
    function [1:0] mod3_add;
        input [1:0] x;
        input [1:0] y;
        reg [2:0] s;
        begin
            s = x + y;
            case (s)
                3'd0, 3'd3: mod3_add = 2'd0;
                3'd1, 3'd4: mod3_add = 2'd1;
                3'd2:       mod3_add = 2'd2;
                default:    mod3_add = 2'd0;
            endcase
        end
    endfunction

    // Chuyển cặp bit [1:0] thông thường thành số dư mod 3 (2*b1 + b0 mod 3)
    function [1:0] slice_mod3;
        input [1:0] pair;
        begin
            case (pair)
                2'b00, 2'b11: slice_mod3 = 2'd0;
                2'b01:        slice_mod3 = 2'd1;
                2'b10:        slice_mod3 = 2'd2;
                default:      slice_mod3 = 2'd0;
            endcase
        end
    endfunction

    // Chuyển cặp bit MSB có dấu [7:6] (-128*b7 + 64*b6 = 1*b7 + 1*b6 mod 3)
    function [1:0] msb_pair_mod3;
        input [1:0] pair;
        begin
            case (pair)
                2'b00:   msb_pair_mod3 = 2'd0;
                2'b01:   msb_pair_mod3 = 2'd1;
                2'b10:   msb_pair_mod3 = 2'd1;
                2'b11:   msb_pair_mod3 = 2'd2;
                default: msb_pair_mod3 = 2'd0;
            endcase
        end
    endfunction

    // Tầng 0: 4 cặp bit
    wire [1:0] l0_0 = slice_mod3(in[1:0]);
    wire [1:0] l0_1 = slice_mod3(in[3:2]);
    wire [1:0] l0_2 = slice_mod3(in[5:4]);
    wire [1:0] l0_3 = msb_pair_mod3(in[7:6]);

    // Tầng 1: 2 nút
    wire [1:0] l1_0 = mod3_add(l0_0, l0_1);
    wire [1:0] l1_1 = mod3_add(l0_2, l0_3);

    // Tầng 2: Kết quả ngõ ra
    assign out = mod3_add(l1_0, l1_1);

endmodule


// Module hỗ trợ: Bộ mã hóa Modulo 3 cho số 32-bit có dấu dạng Cây nhị phân 5 tầng
module mod3_encoder_32b (
    input  wire [31:0] in,
    output wire [1:0]  out
);
    // Hàm cộng modulo 3 giữa 2 số dư 2-bit (1 tầng LUT4)
    function [1:0] mod3_add;
        input [1:0] x;
        input [1:0] y;
        reg [2:0] s;
        begin
            s = x + y;
            case (s)
                3'd0, 3'd3: mod3_add = 2'd0;
                3'd1, 3'd4: mod3_add = 2'd1;
                3'd2:       mod3_add = 2'd2;
                default:    mod3_add = 2'd0;
            endcase
        end
    endfunction

    // Chuyển cặp bit [1:0] thông thường thành số dư mod 3
    function [1:0] slice_mod3;
        input [1:0] pair;
        begin
            case (pair)
                2'b00, 2'b11: slice_mod3 = 2'd0;
                2'b01:        slice_mod3 = 2'd1;
                2'b10:        slice_mod3 = 2'd2;
                default:      slice_mod3 = 2'd0;
            endcase
        end
    endfunction

    // Chuyển cặp bit MSB [31:30] (-2^31*b31 + 2^30*b30 = 1*b31 + 1*b30 mod 3)
    function [1:0] msb_pair_mod3;
        input [1:0] pair;
        begin
            case (pair)
                2'b00:   msb_pair_mod3 = 2'd0;
                2'b01:   msb_pair_mod3 = 2'd1;
                2'b10:   msb_pair_mod3 = 2'd1;
                2'b11:   msb_pair_mod3 = 2'd2;
                default: msb_pair_mod3 = 2'd0;
            endcase
        end
    endfunction

    // Tầng 0: 16 cặp bit (15 cặp thường + 1 cặp MSB)
    wire [1:0] l0_0  = slice_mod3(in[1:0]);
    wire [1:0] l0_1  = slice_mod3(in[3:2]);
    wire [1:0] l0_2  = slice_mod3(in[5:4]);
    wire [1:0] l0_3  = slice_mod3(in[7:6]);
    wire [1:0] l0_4  = slice_mod3(in[9:8]);
    wire [1:0] l0_5  = slice_mod3(in[11:10]);
    wire [1:0] l0_6  = slice_mod3(in[13:12]);
    wire [1:0] l0_7  = slice_mod3(in[15:14]);
    wire [1:0] l0_8  = slice_mod3(in[17:16]);
    wire [1:0] l0_9  = slice_mod3(in[19:18]);
    wire [1:0] l0_10 = slice_mod3(in[21:20]);
    wire [1:0] l0_11 = slice_mod3(in[23:22]);
    wire [1:0] l0_12 = slice_mod3(in[25:24]);
    wire [1:0] l0_13 = slice_mod3(in[27:26]);
    wire [1:0] l0_14 = slice_mod3(in[29:28]);
    wire [1:0] l0_15 = msb_pair_mod3(in[31:30]);

    // Tầng 1: 8 nút
    wire [1:0] l1_0 = mod3_add(l0_0,  l0_1);
    wire [1:0] l1_1 = mod3_add(l0_2,  l0_3);
    wire [1:0] l1_2 = mod3_add(l0_4,  l0_5);
    wire [1:0] l1_3 = mod3_add(l0_6,  l0_7);
    wire [1:0] l1_4 = mod3_add(l0_8,  l0_9);
    wire [1:0] l1_5 = mod3_add(l0_10, l0_11);
    wire [1:0] l1_6 = mod3_add(l0_12, l0_13);
    wire [1:0] l1_7 = mod3_add(l0_14, l0_15);

    // Tầng 2: 4 nút
    wire [1:0] l2_0 = mod3_add(l1_0, l1_1);
    wire [1:0] l2_1 = mod3_add(l1_2, l1_3);
    wire [1:0] l2_2 = mod3_add(l1_4, l1_5);
    wire [1:0] l2_3 = mod3_add(l1_6, l1_7);

    // Tầng 3: 2 nút
    wire [1:0] l3_0 = mod3_add(l2_0, l2_1);
    wire [1:0] l3_1 = mod3_add(l2_2, l2_3);

    // Tầng 4: Kết quả ngõ ra
    assign out = mod3_add(l3_0, l3_1);

endmodule