`timescale 1ns/1ps

package mod3_pkg;
    // Hàm cộng modulo 3 giữa 2 số dư 2-bit (1 tầng LUT4)
    function automatic logic [1:0] mod3_add(input logic [1:0] x, input logic [1:0] y);
        logic [2:0] s;
        s = x + y;
        case (s)
            3'd0, 3'd3: return 2'd0;
            3'd1, 3'd4: return 2'd1;
            3'd2:       return 2'd2;
            default:    return 2'd0;
        endcase
    endfunction

    // Chuyển cặp bit [1:0] thông thường thành số dư mod 3 (2*b1 + b0 mod 3)
    function automatic logic [1:0] slice_mod3(input logic [1:0] pair);
        case (pair)
            2'b00, 2'b11: return 2'd0;
            2'b01:        return 2'd1;
            2'b10:        return 2'd2;
            default:      return 2'd0;
        endcase
    endfunction

    // Chuyển cặp bit MSB có dấu: -2^(2k-1)*b1 + 2^(2k-2)*b0 = 1*b1 + 1*b0 (mod 3)
    function automatic logic [1:0] msb_pair_mod3(input logic [1:0] pair);
        case (pair)
            2'b00:   return 2'd0;
            2'b01:   return 2'd1;
            2'b10:   return 2'd1;
            2'b11:   return 2'd2;
            default: return 2'd0;
        endcase
    endfunction
endpackage

import mod3_pkg::*;

module secure_mac #(
    parameter int IN_WIDTH  = 8,
    parameter int OUT_WIDTH = 32,
    // Ngưỡng phát hiện dị thường động (Calibrated Dynamic Range Checking):
    parameter signed [OUT_WIDTH-1:0] ANOMALY_THRESHOLD = (OUT_WIDTH >= 32) ? 32'sd3276700 : 16'sd30000,
    parameter signed [OUT_WIDTH-1:0] HYSTERESIS_BAND   = (OUT_WIDTH >= 32) ? 32'sd100 : 16'sd20,
    parameter int USE_ADAPTIVE_THRESHOLD = 0
)(
    input  logic                                clk,
    input  logic                                rst_n,
    input  logic                                test_mode,       // IEC 61508 DFT scan test mode input
    input  logic signed [IN_WIDTH-1:0]          a,
    input  logic signed [IN_WIDTH-1:0]          b,
    input  logic signed [OUT_WIDTH-1:0]         c,
    input  logic                                start,
    input  logic                                context_reset,   // ML EWMA dynamic layer recalibration pulse
    input  logic                                alpha_sel,       // 0: fast adaptation, 1: steady-state
    output logic signed [OUT_WIDTH-1:0]         out,
    output logic                                fault_detected,
    output logic                                valid,
    output logic                                rollback
);

    // Stage 1: Thanh ghi ngõ vào & Dual-rail control
    logic signed [IN_WIDTH-1:0]  reg_a, reg_b;
    logic signed [OUT_WIDTH-1:0] reg_c;
    logic                        valid_d1;
    logic                        valid_d1_n; // Dual-rail complementary control register for ISO 26262 ASIL D

    wire signed [2*IN_WIDTH-1:0] product;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_a      <= '0;
            reg_b      <= '0;
            reg_c      <= '0;
            valid_d1   <= 1'b0;
            valid_d1_n <= 1'b1;
        end else begin
            valid_d1   <= start;
            valid_d1_n <= ~start;
            if (start) begin
                reg_a <= a;
                reg_b <= b;
                reg_c <= c;
            end
        end
    end

    assign product = reg_a * reg_b;

    wire [1:0] a_mod3;
    wire [1:0] b_mod3;
    wire [1:0] c_mod3;

    wire signed [31:0] reg_c_32 = (OUT_WIDTH == 32) ? reg_c : { { (32-OUT_WIDTH){reg_c[OUT_WIDTH-1]} }, reg_c };
    mod3_encoder_8b  u_enc_a (.in(reg_a), .out(a_mod3));
    mod3_encoder_8b  u_enc_b (.in(reg_b), .out(b_mod3));
    mod3_encoder_32b u_enc_c (.in(reg_c_32), .out(c_mod3));

    wire [3:0] ab_mod3_product = a_mod3 * b_mod3;

    // Stage 2: Nhân, tích lũy trung gian & Modulo-3 Encoder
    logic signed [2*IN_WIDTH-1:0] pipe_product;
    logic signed [OUT_WIDTH-1:0]  pipe_c;
    logic [3:0]                   pipe_ab_mod3;
    logic [1:0]                   pipe_c_mod3;
    logic                         valid_d2;
    logic                         valid_d2_n;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pipe_product <= '0;
            pipe_c       <= '0;
            pipe_ab_mod3 <= '0;
            pipe_c_mod3  <= '0;
            valid_d2     <= 1'b0;
            valid_d2_n   <= 1'b1;
        end else begin
            valid_d2   <= valid_d1;
            valid_d2_n <= ~valid_d1;
            if (valid_d1) begin
                pipe_product <= product;
                pipe_c       <= reg_c;
                pipe_ab_mod3 <= ab_mod3_product;
                pipe_c_mod3  <= c_mod3;
            end
        end
    end

    wire signed [OUT_WIDTH-1:0] mac_result = pipe_product + pipe_c;
    wire [1:0] stage2_out_mod3;
    wire [1:0] stage2_expected_mod3;

    wire signed [31:0] mac_result_32 = (OUT_WIDTH == 32) ? mac_result : { { (32-OUT_WIDTH){mac_result[OUT_WIDTH-1]} }, mac_result };
    mod3_encoder_32b u_enc_out (.in(mac_result_32), .out(stage2_out_mod3));

    wire [3:0] rns_calc = pipe_ab_mod3 + pipe_c_mod3;
    logic [1:0] expected_mod3_comb;

    always_comb begin
        case (rns_calc)
            4'd0, 4'd3, 4'd6, 4'd9: expected_mod3_comb = 2'd0;
            4'd1, 4'd4, 4'd7:       expected_mod3_comb = 2'd1;
            4'd2, 4'd5, 4'd8:       expected_mod3_comb = 2'd2;
            default:                expected_mod3_comb = 2'd0;
        endcase
    end
    assign stage2_expected_mod3 = expected_mod3_comb;

    // Stage 3: Chốt Mod3 residue & Kiểm tra bất thường (tách trễ tới hạn đạt WNS >= 0 tại 200 MHz)
    logic signed [OUT_WIDTH-1:0] pipe_mac_result;
    logic [1:0]                  pipe_out_mod3;
    logic [1:0]                  pipe_expected_mod3;
    logic                        valid_d3;
    logic                        valid_d3_n;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pipe_mac_result    <= '0;
            pipe_out_mod3      <= '0;
            pipe_expected_mod3 <= '0;
            valid_d3           <= 1'b0;
            valid_d3_n         <= 1'b1;
        end else begin
            valid_d3   <= valid_d2;
            valid_d3_n <= ~valid_d2;
            if (valid_d2) begin
                pipe_mac_result    <= mac_result;
                pipe_out_mod3      <= stage2_out_mod3;
                pipe_expected_mod3 <= stage2_expected_mod3;
            end
        end
    end

    wire mod3_mismatch = (pipe_expected_mod3 != pipe_out_mod3);

    // ML-Guided Online Adaptive Range Anomaly Detection (EWMA + MAD 3-sigma)
    wire signed [OUT_WIDTH-1:0] adaptive_threshold;
    wire signed [OUT_WIDTH-1:0] ewma_mean;
    wire signed [OUT_WIDTH-1:0] ewma_mad;
    wire                        ewma_warmup_done;

    wire safe_context_reset = (context_reset === 1'b1) ? 1'b1 : 1'b0;
    wire safe_alpha_sel     = (alpha_sel === 1'b0) ? 1'b0 : 1'b1;

    ewma_tracker #(
        .WIDTH(OUT_WIDTH),
        .ALPHA_SHIFT(4),
        .ALPHA_FAST_SHIFT(2),
        .WARMUP_SAMPLES(16),
        .DEFAULT_THRESHOLD(ANOMALY_THRESHOLD),
        .MIN_THRESHOLD_FLOOR((OUT_WIDTH >= 32) ? 32'sd2000 : 16'sd500)
    ) u_ewma (
        .clk(clk),
        .rst_n(rst_n),
        .data_in(pipe_mac_result),
        .valid_in(valid_d3 & ~mod3_mismatch),
        .context_reset(safe_context_reset),
        .alpha_sel(safe_alpha_sel),
        .threshold_out(adaptive_threshold),
        .mean_out(ewma_mean),
        .mad_out(ewma_mad),
        .warmup_done_out(ewma_warmup_done)
    );

    wire signed [OUT_WIDTH-1:0] active_threshold = (USE_ADAPTIVE_THRESHOLD) ? adaptive_threshold : ANOMALY_THRESHOLD;

    // Range anomaly check với hysteresis deadband chống flickering và bảo vệ chống tràn số
    wire signed [OUT_WIDTH:0] sum_upper = {active_threshold[OUT_WIDTH-1], active_threshold} + {HYSTERESIS_BAND[OUT_WIDTH-1], HYSTERESIS_BAND};
    wire signed [OUT_WIDTH-1:0] max_pos_val = {1'b0, {(OUT_WIDTH-1){1'b1}}};
    wire signed [OUT_WIDTH-1:0] upper_thresh_hyst = (sum_upper > {1'b0, max_pos_val}) ? max_pos_val : sum_upper[OUT_WIDTH-1:0];
    wire signed [OUT_WIDTH-1:0] lower_thresh_hyst = -upper_thresh_hyst;
    wire range_anomaly = (pipe_mac_result > upper_thresh_hyst) || (pipe_mac_result < lower_thresh_hyst);

    // Control Path Integrity: Parity check kép giữa valid và valid_n
    wire control_fault = (valid_d1 == valid_d1_n) || (valid_d2 == valid_d2_n) || (valid_d3 == valid_d3_n);

    // Disagreement trigger: Modulo-3 sai lệch | Vượt biên biên độ | Lỗi điều khiển
    wire disagreement = mod3_mismatch | range_anomaly | control_fault;

    // Stage 4: Chốt ngõ ra & Phục hồi Rollback
    logic signed [OUT_WIDTH-1:0] shadow_accumulator;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out                <= '0;
            shadow_accumulator <= '0;
            fault_detected     <= 1'b0;
            rollback           <= 1'b0;
            valid              <= 1'b0;
        end else begin
            valid <= valid_d3 & (~control_fault);
            if (valid_d3 || control_fault) begin
                if (disagreement) begin
                    // Phát hiện lỗi -> Phục hồi trạng thái cũ (Rollback tức thời)
                    out            <= shadow_accumulator;
                    fault_detected <= 1'b1;
                    rollback       <= 1'b1;
                end else begin
                    out                 <= pipe_mac_result;
                    shadow_accumulator  <= pipe_mac_result;
                    fault_detected      <= 1'b0;
                    rollback            <= 1'b0;
                end
            end else begin
                fault_detected <= 1'b0;
                rollback       <= 1'b0;
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


// Bộ mã hóa Modulo 3 cho số 8-bit có dấu dạng cây nhị phân
module mod3_encoder_8b (
    input  wire [7:0] in,
    output wire [1:0] out
);
    import mod3_pkg::*;

    wire [1:0] l0_0 = slice_mod3(in[1:0]);
    wire [1:0] l0_1 = slice_mod3(in[3:2]);
    wire [1:0] l0_2 = slice_mod3(in[5:4]);
    wire [1:0] l0_3 = msb_pair_mod3(in[7:6]);

    wire [1:0] l1_0 = mod3_add(l0_0, l0_1);
    wire [1:0] l1_1 = mod3_add(l0_2, l0_3);

    assign out = mod3_add(l1_0, l1_1);

endmodule


// Bộ mã hóa Modulo 3 cho số 32-bit có dấu dạng cây nhị phân 5 tầng
module mod3_encoder_32b (
    input  wire [31:0] in,
    output wire [1:0]  out
);
    import mod3_pkg::*;

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

    wire [1:0] l1_0 = mod3_add(l0_0,  l0_1);
    wire [1:0] l1_1 = mod3_add(l0_2,  l0_3);
    wire [1:0] l1_2 = mod3_add(l0_4,  l0_5);
    wire [1:0] l1_3 = mod3_add(l0_6,  l0_7);
    wire [1:0] l1_4 = mod3_add(l0_8,  l0_9);
    wire [1:0] l1_5 = mod3_add(l0_10, l0_11);
    wire [1:0] l1_6 = mod3_add(l0_12, l0_13);
    wire [1:0] l1_7 = mod3_add(l0_14, l0_15);

    wire [1:0] l2_0 = mod3_add(l1_0, l1_1);
    wire [1:0] l2_1 = mod3_add(l1_2, l1_3);
    wire [1:0] l2_2 = mod3_add(l1_4, l1_5);
    wire [1:0] l2_3 = mod3_add(l1_6, l1_7);

    wire [1:0] l3_0 = mod3_add(l2_0, l2_1);
    wire [1:0] l3_1 = mod3_add(l2_2, l2_3);

    assign out = mod3_add(l3_0, l3_1);

endmodule