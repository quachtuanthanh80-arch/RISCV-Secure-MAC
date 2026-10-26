# FPGA Synthesis & Implementation Results (AMD Xilinx Vivado 2026.1)

Thư mục chứa cấu hình tổng hợp, file ràng buộc chân & xung nhịp (XDC constraints), tập lệnh TCL tự động hóa và các báo cáo PPA thực nghiệm đo đạc trên vi mạch FPGA **Xilinx Zynq-7000** (`xc7z020clg400-1`).

---

## 1. Cấu trúc Thư mục

* [`constraints/top_module.xdc`](file:///d:/NCKH/synth/constraints/top_module.xdc): Ràng buộc xung nhịp hệ thống $100\text{ MHz}$ ($10\text{ ns}$ period) và khai báo timing constraints.
* [`bitstreams/`](file:///d:/NCKH/synth/bitstreams/): File bitstream FPGA đã biên dịch (`top_module.bit`) sẵn sàng nạp trực tiếp lên kit Zynq-7020.
* [`checkpoints/`](file:///d:/NCKH/synth/checkpoints/): Tệp lưu trữ trạng thái thiết kế Post-synthesis và Post-route Design Checkpoints (`.dcp`).
* [`fpga_reports/`](file:///d:/NCKH/synth/fpga_reports/): Thư mục chứa các tệp báo cáo PPA gốc đo đạc từ Vivado:
  * `top_module_*.txt` (Toàn bộ SoC: 860 LUTs, 1.074 FFs, 122 mW, Fmax = 114,80 MHz, WNS = +1,289 ns)
  * `secure_mac_*.txt` (Secure MAC độc lập: 240 LUTs / 135 trong SoC, 138 FFs, 116 mW, Fmax = 119,88 MHz)
  * `baseline_mac_*.txt` (Baseline MAC cơ sở: 99 LUTs, 131 FFs, 108 mW, Fmax = 176,50 MHz)
* [`scripts/`](file:///d:/NCKH/synth/scripts/): Tập lệnh TCL tự động hóa Vivado (chạy batch synthesis và tạo GUI project).
* [`vivado_project/`](file:///d:/NCKH/synth/vivado_project/): Dự án GUI Vivado (`RV32I_Secure_MAC.xpr`) kèm các file cấu hình hiển thị dạng sóng (`.wcfg`).

---

## 2. Bảng Kết quả Tổng hợp & Thực thi Thực tế (Vivado PPA Benchmark)

### Bảng 3.1: Phân bổ tài nguyên phân cấp và PPA trong SoC (Hierarchical Utilization & STA)
| Khối chức năng (Instance) | Slice LUTs | Flip-Flops (FFs) | CARRY4 / MUX | Tỷ lệ trên XC7Z020 | Timing & Ghi chú |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Lõi CPU RISC-V (`u_cpu`)** | 633 (72,01%) | 901 (81,83%) | 28 CARRY4 | 1,19% LUT / 0,85% FF | WNS = +0,759 ns |
| **2. Bộ tăng tốc Secure MAC (`u_mac`)** | 142 (16,15%) | 115 (10,45%) | 28 CARRY4 | 0,27% LUT / 0,11% FF | Pipeline 3 tầng đồng bộ + Mod3 CED |
| **3. Bộ nhớ dữ liệu RAM (`u_dmem`)** | 61 (6,94%) | 0 (0,00%) | 32 Dist. RAM | 0,11% LUT / 0,00% FF | Ghép nối tầng MEM (1KB RAM) |
| **4. Logic ghép nối MMIO & Bus** | 45 (5,12%) | 85 (7,72%) | 0 | 0,08% LUT / 0,08% FF | 0 chu kỳ trễ bổ sung |
| **Tổng SoC Top (`top_module`)** | **879 (100,0%)** | **1.101 (100,0%)** | **56 CARRY4, 96 MUX** | **1,65% LUT / 1,03% FF** | **$F_{max} = 108,21$ MHz, WNS = +0,759 ns, Power = 124 mW** |
| *Khối Secure MAC Standalone* | *205 LUTs* | *178 FFs* | *26 CARRY4* | *0,39% LUT / 0,17% FF* | *$F_{max} = 175,38$ MHz, Power = 114 mW* |

### Bảng 3.2: Đối chiếu Kỹ thuật Chi tiết giữa Baseline MAC và Secure MAC Đề xuất
| Nhóm Tiêu chí Kỹ thuật | Chỉ số Chi tiết | Baseline MAC (`baseline_mac.v`) | Secure MAC (`secure_mac.v`) | Chênh lệch / Chi phí (Overhead) |
| :--- | :--- | :---: | :---: | :--- |
| **1. Vi kiến trúc & Logic** | Độ rộng toán hạng & Pipeline | 8×8-bit (INT8) + 32-bit Acc, 3 tầng | 8×8-bit (INT8) + 32-bit Acc, 3 tầng | 0 tầng trễ bổ sung (Latency = 3 CK) |
| | Cơ chế kiểm tra lỗi (CED) | Không tích hợp (0% bảo vệ) | Đồng cấu Modulo-3 (Cây nhị phân $O(\log_2 N)$) | Kênh thặng dư 2-bit tính song song |
| | Bộ mã hoá thặng dư Modulo-3 | 0 bộ | 5 bộ ($2\times$ mod3_8b, mod3_16b, $2\times$ mod3_32b) | Khối mã hoá chuyên biệt cực nhỏ |
| | Cơ chế tự khôi phục (Rollback) | Không có (SDC = 100% khi lỗi) | Shadow Accumulator 32-bit + MUX | Tự hoàn tác trạng thái trong 1 chu kỳ |
| | Tín hiệu cảnh báo / Giao tiếp | `out[31:0]`, `valid` | `out`, `valid`, `fault_detected`, `rollback`, `irq` | Xuất ngắt phần cứng trực tiếp cho CPU |
| **2. PPA Phần cứng (XC7Z020)** | Bảng tra cứu Logic (Slice LUTs) | **99 LUTs** | **142 LUTs** (trong SoC)<br>*205 LUTs (Standalone)* | **+43 LUTs (+43,43% trên MAC / +5,14% SoC)** |
| | Thanh ghi Flip-Flops (FFs) | **131 FFs** | **115 FFs** (trong SoC)<br>*178 FFs (Standalone)* | **+16 FFs (+1,47% SoC)** |
| | Bộ cộng chuỗi (CARRY4) | **20 CARRY4** | **26 CARRY4** (trong SoC: 28) | **+6 CARRY4 (+30,00%)** |
| | Khối DSP / RAM chuyên dụng | 0 DSP, 0 BRAM | 0 DSP, 0 BRAM | Thuần LUT fabric, khả chuyển cao |
| **3. Timing & Công suất** | Tần số cực đại ($F_{max}$) | **176,50 MHz** (Standalone) | **175,38 MHz** (Standalone)<br>**108,21 MHz** (trong SoC) | Toàn SoC vượt an toàn mốc 100 MHz (WNS = +0,759 ns) |
| | Thời gian tới hạn ($T_{min}$) | **5,665 ns** | **5,702 ns** (Standalone)<br>**9,241 ns** (trong SoC) | +0,037 ns (Standalone) / +3,576 ns (SoC) |
| | Tổng công suất On-Chip (Power) | **108 mW** (5 mW động, 103 mW tĩnh) | **114 mW** (Standalone: 11 mW động)<br>**124 mW** (SoC: 18 mW động) | **+5 mW động (+6,90% tổng SoC)** |
| | Biến thiên thời gian (Timing Jitter)| **0 ns** (Không sửa) | **0 ns** (Bất biến 3 chu kỳ) | Kháng Side-Channel Timing Attacks |
| **4. Khả năng Dung lỗi** | Lỗi lật bit đơn (Single-Bit SEU) | FDR = 0,00% (SDC = 100,00%) | FDR = 100,00% (SDC = 0,00%) | Triệt tiêu 100% rủi ro hỏng dữ liệu thầm lặng |
| | Lỗi kẹt logic (Stuck-At Faults) | FDR = 0,00% | FDR = 100,00% | Phát hiện 100% lỗi SA0/SA1 trên 5 khối con |
| | Lỗi kép 2-bit (Double-Bit MBU) | FDR = 0,00% | FDR = 48,39% (TB) / 76,71% w/ Double-Check | 100% cặp d chẵn, 0% cặp d lẻ |
| | Lỗi chùm đa bit (Bursts $k=1..6$) | FDR = 0,00% | FDR = 68,68% | Tiệm cận ngưỡng lý thuyết $2/3 \approx 66,67\%$ |
| | Độ chính xác Khôi phục Rollback | 0,00% | 100,00% (trong đúng 1 chu kỳ) | Phục hồi tức thời không gián đoạn CPU |

---

## 3. Hướng dẫn Chạy Đo đạc Tự động (One-Click Reproduction)

Mở PowerShell / Command Prompt tại thư mục dự án và thực thi:
```powershell
# Đo đạc PPA cho Baseline MAC
& "C:\AMDDesignTools\2026.1\Vivado\bin\vivado.bat" -mode batch -source "synth/scripts/run_synth_baseline_mac.tcl"

# Đo đạc PPA cho Secure MAC
& "C:\AMDDesignTools\2026.1\Vivado\bin\vivado.bat" -mode batch -source "synth/scripts/run_synth.tcl"

# Đo đạc PPA cho Toàn bộ SoC Top Module
& "C:\AMDDesignTools\2026.1\Vivado\bin\vivado.bat" -mode batch -source "synth/scripts/run_synth_top.tcl"
```
