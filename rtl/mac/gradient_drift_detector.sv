`timescale 1ns/1ps

module gradient_drift_detector #(
    parameter int WIDTH             = 32,
    parameter int DRIFT_THRESHOLD   = 50,
    parameter int CONSECUTIVE_LIMIT = 3
)(
    input  logic                    clk,
    input  logic                    rst_n,
    input  logic signed [WIDTH-1:0] mean_in,
    input  logic                    update_en,
    output logic signed [WIDTH-1:0] drift_out,
    output logic                    drift_alarm
);

    logic signed [WIDTH-1:0] prev_mean;
    logic [3:0]              consecutive_drift_cnt;

    // 2nd-order drift metric: drift_t = |mu_t - mu_{t-1}|
    wire signed [WIDTH-1:0] diff = mean_in - prev_mean;
    wire signed [WIDTH-1:0] abs_drift = (diff < 0) ? -diff : diff;
    assign drift_out = abs_drift;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prev_mean             <= '0;
            consecutive_drift_cnt <= '0;
            drift_alarm           <= 1'b0;
        end else if (update_en) begin
            prev_mean <= mean_in;

            // Detect sustained rapid drift across consecutive updates
            if (abs_drift > DRIFT_THRESHOLD) begin
                if (consecutive_drift_cnt >= (CONSECUTIVE_LIMIT - 1)) begin
                    drift_alarm <= 1'b1;
                end else begin
                    consecutive_drift_cnt <= consecutive_drift_cnt + 1'b1;
                end
            end else begin
                consecutive_drift_cnt <= '0;
                drift_alarm           <= 1'b0;
            end
        end
    end

endmodule
