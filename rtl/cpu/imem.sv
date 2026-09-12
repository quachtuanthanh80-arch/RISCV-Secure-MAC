`timescale 1ns/1ps
module imem (
    input  logic [31:0] a,
    output logic [31:0] rd
);

    logic [31:0] RAM[63:0];

    initial begin
        RAM[0]  = 32'h00A00093; // 0: ADDI x1, x0, 10 (x1 = 10)
        RAM[1]  = 32'h01400113; // 1: ADDI x2, x0, 20 (x2 = 20)
        RAM[2]  = 32'h002081B3; // 2: ADD  x3, x1, x2 (x3 = 10 + 20 = 30)
        RAM[3]  = 32'h800002B7; // 3: LUI  x5, 20'h80000 (x5 = 0x8000_0000: Địa chỉ cơ sở MMIO Secure MAC)
        RAM[4]  = 32'h0012A023; // 4: SW   x1, 0(x5) (Ghi A = 10 vào REG_OP_A tại 0x8000_0000)
        RAM[5]  = 32'h0022A223; // 5: SW   x2, 4(x5) (Ghi B = 20 vào REG_OP_B tại 0x8000_0004)
        RAM[6]  = 32'h0032A423; // 6: SW   x3, 8(x5) (Ghi C = 30 vào REG_ACC_IN tại 0x8000_0008)
        RAM[7]  = 32'h00100313; // 7: ADDI x6, x0, 1 (x6 = 1)
        RAM[8]  = 32'h0062A623; // 8: SW   x6, 12(x5) (Ghi start = 1 vào REG_CTRL để kích hoạt MAC)
        RAM[9]  = 32'h00000013; // 9: NOP (Chờ pipeline Secure MAC)
        RAM[10] = 32'h00000013;
        RAM[11] = 32'h00000013;
        RAM[12] = 32'h00000013;
        RAM[13] = 32'h00000013;
        RAM[14] = 32'h0082A383; // 14: LW  x7, 8(x5) (Đọc kết quả MAC vào x7: 10*20 + 30 = 230)
        RAM[15] = 32'h0000006F; // 15: JAL x0, 0 (Vòng lặp kết thúc)
    end

    assign rd = RAM[a[7:2]];

endmodule
