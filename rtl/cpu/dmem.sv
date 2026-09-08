`timescale 1ns/1ps
module dmem (
    input  logic        clk,
    input  logic        we,
    input  logic [3:0]  wstrb,
    input  logic [31:0] a,
    input  logic [31:0] wd,
    output logic [31:0] rd
);

    logic [31:0] RAM[63:0];

    integer i;
    initial begin
        for (i = 0; i < 64; i = i + 1) begin
            RAM[i] = 32'd0;
        end
    end

    // Ghi dữ liệu đồng bộ theo xung nhịp có mặt nạ byte strobe (wstrb)
    always_ff @(posedge clk) begin
        if (we) begin
            if (wstrb[0]) RAM[a[7:2]][7:0]   <= wd[7:0];
            if (wstrb[1]) RAM[a[7:2]][15:8]  <= wd[15:8];
            if (wstrb[2]) RAM[a[7:2]][23:16] <= wd[23:16];
            if (wstrb[3]) RAM[a[7:2]][31:24] <= wd[31:24];
        end
    end

    // Đọc dữ liệu tổ hợp (không đợi xung nhịp)
    assign rd = RAM[a[7:2]];

endmodule
