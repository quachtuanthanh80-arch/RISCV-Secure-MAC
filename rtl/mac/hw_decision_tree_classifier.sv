`timescale 1ns/1ps

module hw_decision_tree_classifier #(
    parameter int WIDTH = 32,
    parameter signed [WIDTH-1:0] T_MAD_HI   = 32'sd500,
    parameter signed [WIDTH-1:0] T_DRIFT_HI = 32'sd100,
    parameter signed [WIDTH-1:0] T_MEAN_HI  = 32'sd800
)(
    input  logic signed [WIDTH-1:0] abs_mean,
    input  logic signed [WIDTH-1:0] mad,
    input  logic signed [WIDTH-1:0] drift,
    input  logic [1:0]              layer_type, // 00: Conv, 01: Pool, 10: FC, 11: Softmax
    output logic [1:0]              classification_class // 00: NORMAL, 01: SUSPICIOUS, 10: FAULT
);

    localparam logic [1:0] CLASS_NORMAL     = 2'b00;
    localparam logic [1:0] CLASS_SUSPICIOUS = 2'b01;
    localparam logic [1:0] CLASS_FAULT      = 2'b10;

    // 3-level binary hardware decision tree
    always_comb begin
        if (mad > T_MAD_HI) begin
            if (drift > T_DRIFT_HI) begin
                classification_class = CLASS_FAULT;
            end else if (abs_mean > T_MEAN_HI) begin
                classification_class = CLASS_SUSPICIOUS;
            end else begin
                classification_class = CLASS_NORMAL;
            end
        end else begin
            // Layer-sensitive drift check
            if ((layer_type == 2'b10) && (drift > T_DRIFT_HI)) begin
                classification_class = CLASS_SUSPICIOUS;
            end else begin
                classification_class = CLASS_NORMAL;
            end
        end
    end

endmodule
