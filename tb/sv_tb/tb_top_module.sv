`timescale 1ns/1ps

module tb_top_module();

    // 1. Tín hiệu điều khiển
    reg clk;
    reg rst_n;
    wire irq;

    // 2. Tạo xung nhịp 100 MHz (chu kỳ 10ns: 5ns High, 5ns Low)
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    // 3. Khởi tạo khối SoC Top Module (DUT)
    top_module dut (
        .clk(clk),
        .rst_n(rst_n),
        .irq(irq)
    );

    // 4. Kích hoạt Reset và chu trình mô phỏng
    initial begin
        $display("=================================================");
        $display("  BẮT ĐẦU MÔ PHỎNG SOC TOP MODULE (tb_top_module)");
        $display("=================================================");

        // Bước 1: Kích hoạt Reset (Tích cực mức thấp)
        rst_n = 1'b0;
        #25; // Giữ reset trong 2.5 chu kỳ xung nhịp

        // Bước 2: Nhả Reset để CPU bắt đầu thực thi từ PC = 0x0000_0000
        @(negedge clk);
        rst_n = 1'b1;
        $display("[%0t ns] Reset released. CPU starting execution...", $time);

        // Bước 3: Cho hệ thống chạy 100 chu kỳ xung nhịp (1000 ns)
        #1000;

        // Bước 4: Tự động kiểm thử tính đúng đắn (Self-Checking Verifications)
        if (dut.u_cpu.u_regfile.registers[7] !== 32'd230) begin
            $display("[FAIL] Register x7 mismatch: expected 230, got %0d", dut.u_cpu.u_regfile.registers[7]);
            $fatal(1, "SoC Self-Checking Verification Failed!");
        end else begin
            $display("[PASS] Register x7 matches expected Secure MAC result: 230");
        end

        if (dut.u_cpu.u_regfile.registers[1] !== 32'd10 || dut.u_cpu.u_regfile.registers[2] !== 32'd20) begin
            $fatal(1, "Operand registers x1/x2 corrupted!");
        end

        $display("=================================================");
        $display("  ALL SOC SELF-CHECKS PASSED SUCCESSFULLY (100%%)!");
        $display("=================================================");
        $finish;
    end

    // 5. Ghi nhận dữ liệu ra waveform (VCD / Vivado Waveform)
    initial begin
        $dumpfile("tb_top_module.vcd");
        $dumpvars(0, tb_top_module);
    end

endmodule
