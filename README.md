<div align="center">

# 🛡️ Fault-Resilient RISC-V SoC with Modulo-3 Secure Neural MAC Accelerator

**Nghiên cứu & Hiện thực hóa Lõi Vi xử lý RISC-V RV32I tích hợp Bộ tăng tốc Học sâu Secure MAC Dung lỗi Bức xạ (SEU/MBU)**  
*Đo đạc & Thực thi Phần cứng Thực tế trên FPGA AMD Xilinx Zynq-7000 (`xc7z020clg400-1`) bằng Vivado 2026.1*

[![Hardware CI](https://github.com/quachtuanthanh80-arch/NCKH-RISCV-Secure-MAC/actions/workflows/ci_regression.yml/badge.svg)](https://github.com/quachtuanthanh80-arch/NCKH-RISCV-Secure-MAC/actions/workflows/ci_regression.yml)
[![PySlang RTL Linter](https://img.shields.io/badge/PySlang%20Linter-Passed%20(15%20RTL%20Files)-brightgreen.svg)](#)
[![Cocotb Tests](https://img.shields.io/badge/Cocotb%20Tests-10%20Suites%20PASS%20(100%25)-brightgreen.svg)](#)
[![Functional Coverage](https://img.shields.io/badge/Functional%20Coverage-100%25%20Residue%20%7C%2091.25%25%20ALU-brightgreen.svg)](#)
[![SVA Formal Checks](https://img.shields.io/badge/SVA%20Formal%20Checks-Timing%20Invariance%20Active-brightgreen.svg)](#)

[![Fault Campaign](https://img.shields.io/badge/Fault%20Campaign-26%2C040%20Core%20%7C%2081%2C000%20Trials-blue.svg)](#)
[![Single-Bit FDR](https://img.shields.io/badge/Single--Bit%20FDR-100.00%25%20(Zero%20SDC)-success.svg)](#)
[![Rollback Accuracy](https://img.shields.io/badge/State%20Rollback-100.00%25%20(1%20CK)-success.svg)](#)
[![FPGA Target](https://img.shields.io/badge/FPGA-Xilinx%20Zynq--7020%20%40%20100MHz-orange.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

### ⚡ Tóm tắt Chỉ số Phần cứng & Độ tin cậy (Key Highlights at a Glance)

| Chỉ tiêu Kỹ thuật | Kết quả Đạt được | Ý nghĩa Thực tiễn & Ứng dụng |
| :--- | :---: | :--- |
| **Phát hiện lỗi lật bit đơn (SEU)** | **`100.00%`** (3,200/3,200 mẫu) | Quét cạn kiệt 32 vị trí bit thanh ghi, triệt tiêu 100% rủi ro lọt lỗi thầm lặng (Zero SDC). |
| **Thời gian tự khôi phục (Rollback)** | **`Đúng 1 CK`** (Tức thời) | Khôi phục bằng **Shadow Accumulator 32-bit**, không gián đoạn hoặc làm trượt luồng lệnh CPU. |
| **Biến thiên định thời (Timing Jitter)** | **`0 ns`** (Bất biến 3 CK) | Độ trễ 3 chu kỳ clock cố định, kháng hoàn toàn các cuộc tấn công kênh phụ thời gian (Timing Side-Channel). |
| **Chi phí phần cứng (Hardware Overhead)** | **`+4.19% LUTs`** / **`+0.56% FFs`** | Chỉ tăng +36 LUTs và +6 FFs trên toàn bộ vi mạch SoC (860 LUTs, 1,074 FFs). |
| **Công suất & Tần số hoạt động** | **`122 mW`** @ **`114.80 MHz`** | Vượt an toàn chuẩn công nghiệp 100 MHz trên chip FPGA Xilinx Zynq-7000 Edge AI. |

---

## 📑 Mục Lục Điều Hướng (Table of Contents)

1. [📌 Tổng quan dự án (Project Overview)](#-tổng-quan-dự-án-project-overview)
2. [🏗️ Kiến trúc Hệ thống (System Architecture)](#️-kiến-trúc-hệ-thống-system-architecture)
3. [🗺️ Bản đồ Bộ nhớ & Thanh ghi MMIO (Memory Map)](#️-bản-đồ-bộ-nhớ--thanh-ghi-mmio-memory-map)
4. [📊 Kết quả Thực nghiệm Tiêm lỗi (Fault Injection Campaign — 26,040 Mẫu thử)](#-kết-quả-thực-nghiệm-tiêm-lỗi-fault-injection-campaign--26040-mẫu-thử)
5. [⚡ Kết quả Tổng hợp Phần cứng Thực tế Vivado 2026.1](#-kết-quả-tổng-hợp-phần-cứng-thực-tế-amd-xilinx-vivado-20261-benchmark)
6. [🔬 Bảng Đối Chiếu Đa Phương Pháp SOTA (13 Tiêu chí)](#-bảng-đối-chiếu-đa-phương-pháp-khớp-bảng-34-trong-báo-cáo)
7. [🧠 Benchmark Thực nghiệm Nơ-ron AI (INT8 FC Layer)](#-benchmark-thực-nghiệm-ứng-dụng-ai-int8-fully-connected-neuron-inference)
8. [🔍 Phân tích Giới hạn & Biện pháp Khắc phục (Limitations & Mitigation)](#-phân-tích-giới-hạn-kỹ-thuật--biện-pháp-khắc-phục-limitations--mitigation)
9. [📁 Cấu trúc Thư mục Dự án (Project Directory Layout)](#-cấu-trúc-thư-mục-dự-án-project-directory-layout)
10. [🚀 Hướng dẫn Chạy & Tái tạo Kết quả (Quick Start)](#-hướng-dẫn-chạy--tái-tạo-kết-quả-quick-start)
11. [👥 Tác giả & Giấy phép (Authors & License)](#-tác-giả--thông-tin-đề-tài-authors--acknowledgments)

---

## 📌 Tổng quan dự án (Project Overview)

Dự án nghiên cứu và hiện thực hóa một hệ thống trên chip (**SoC hoàn chỉnh**) tích hợp **Lõi vi xử lý RISC-V 32-bit (RV32I 5 tầng pipeline)** với **Bộ tăng tốc phần cứng Secure MAC** (Multiply-Accumulate) có khả năng tự phát hiện và tự khôi phục trước các cuộc **Tấn công Tiêm lỗi (Fault Injection Attacks - FIA)** và lỗi bức xạ vật lý (Single Event Upsets - SEU) trong quá trình suy luận mạng nơ-ron (Edge AI Inference).

### 💡 Ý tưởng cốt lõi (Core Innovations):
1. **Kiểm tra sai số số học đồng thời (Concurrent Error Detection - CED):** Ứng dụng mã thặng dư số học **Modulo-3 Arithmetic Residue Code** để phát hiện lỗi tính toán $A \times B + C$ trong thời gian thực với overhead phần cứng siêu nhỏ (+4.19% LUTs trên toàn SoC / +36.36% trên khối MAC).
2. **Khôi phục trạng thái tức thời (Hardware State Rollback):** Tích hợp **Shadow Accumulator** lưu trữ trạng thái hợp lệ gần nhất. Khi phát hiện xung lỗi, mạch ngay lập tức kích hoạt cờ `rollback` để phục hồi dữ liệu gốc, ngăn chặn triệt để hiện tượng Silent Data Corruption (SDC).
3. **Tích hợp SoC & Điều khiển ngắt (Hardware/Software Co-design):** Bộ tăng tốc MAC được kết nối vào bus bộ nhớ CPU thông qua **MMIO** (`0x8000_0000`) và đường ngắt cứng (`irq`), cho phép phần mềm thực thi lớp mạng nơ-ron Fully Connected an toàn.

---

## 🏗️ Kiến trúc Hệ thống (System Architecture)

```
                       +-------------------------------------------------------------+
                       |                        top_module                           |
                       |                                                             |
                       |  +-------------------+      +----------------------------+  |
                       |  |     riscv_cpu     |      |         secure_mac         |  |
                       |  |  5-Stage Pipeline |      |  (Mod-3 Checker + Rollback)|  |
                       |  |                   |      |                            |  |
                       |  |  [IF] [ID] [EX]   |      |  - 8-bit x 8-bit + 32-bit  |  |
                       |  |      [MEM] [WB]   |      |  - Pipelined Mod-3 Encoder |  |
                       |  +---------+---------+      |  - Shadow Accumulator      |  |
                       |            |                +--------------+-------------+  |
                       |            | Memory Bus                    |                |
                       |            v (MMIO / RAM)                  |                |
                       |     +--------------+                       |                |
                       |     | Address Mux  |-----------------------+                |
                       |     +-------+------+       (0x8000_0000..0x8000_0014)       |
                       |             |                                               |
                       |             v (0x0000_0000..0x0000_03FF)                    |
                       |      +-------------+                                        |
                       |      | dmem (RAM)  |                                        |
                       |      +-------------+                                        |
                       |             |                                               |
                       +-------------+-----------------------------------------------+
                                     |
                                     v IRQ (Hardware Fault Interrupt)
```
---

## 📁 Cấu trúc Thư mục Dự án (Project Directory Layout)

```
D:\NCKH
├── .gitattributes          # Quy định chuẩn xuống dòng (LF) và phân loại định dạng nhị phân
├── .gitignore              # Chặn toàn diện tệp rác Vivado, Cocotb, Python và Office
├── LICENSE                 # Giấy phép mã nguồn mở MIT License
├── README.md               # Trang chủ dự án & tài liệu tổng quan
├── run_all_tests.py        # Master Test Runner (Kiểm chứng tự động toàn diện 10 test suites ~56s)
│
├── .github/                # CI/CD Workflows (Tự động chạy linter & 10 suites kiểm chứng trên GitHub)
│   └── workflows/ci_regression.yml
│
├── rtl/                    # Mã nguồn phần cứng RTL synthesizable (SystemVerilog / Verilog)
│   ├── cpu/                      # Lõi RISC-V 5 tầng (ALU, Control, Hazard Unit + SVA, DMEM, IMEM...)
│   ├── mac/                      # Secure MAC (CED + Rollback + SVA) & Baseline MAC (Đối chứng)
│   ├── top/                      # top_module.v (SoC Top) và alu_top.sv (ALU Wrapper)
│   └── filelists/                # Filelist tổng hợp cho trình mô phỏng (project.f, alu_top.f)
│
├── tb/                     # Môi trường kiểm chứng toàn diện (10 Test Suites Cocotb + SVA + Coverage)
│   ├── README.md                 # Hướng dẫn chi tiết chạy 10 suites kiểm chứng
│   ├── cocotb/                   # Cocotb 2.0 Testbenches (Python + Icarus Verilog)
│   │   ├── riscv_isa/            # RV32I ISA Compliance Suite (Branch, ALU, Jump, Mem, Loop)
│   │   ├── hazard_unit/          # Unit test Hazard Unit (Stall, Flush, Forwarding Priority)
│   │   ├── cpu_units/            # Unit test Branch Comparator & Register File
│   │   ├── alu_top/              # ALU Top + alu_coverage.py (Functional Coverage model 91.25%)
│   │   ├── secure_mac/           # Secure MAC + mac_coverage.py (100% Residue Coverage) + Fault Campaigns
│   │   ├── top_module/           # System-level SoC testbench
│   │   └── common/               # BFM SoC Driver & Monitor (bfm_soc.py)
│   └── sv_tb/                    # SystemVerilog testbenches truyền thống tự kiểm tra (Self-Checking)
│       ├── tb_secure_mac.sv      # Secure MAC SV testbench với fatal assertions
│       └── tb_top_module.sv      # SoC Top SV testbench với memory polling
│
├── sw/                     # Phần mềm nhúng, firmware C và mã máy Assembly
│   ├── README.md
│   ├── src/                      # Source code (C, Assembly)
│   └── bin/                      # Compiled hex machine code (mac_program.hex)
│
├── synth/                  # Cấu hình tổng hợp AMD Xilinx Vivado 2026.1 (Zynq-7000)
│   ├── README.md
│   ├── bitstreams/               # File bitstream FPGA đã biên dịch (top_module.bit)
│   ├── checkpoints/              # Post-synth & Post-route design checkpoints (.dcp)
│   ├── constraints/              # File XDC ràng buộc xung nhịp 100 MHz (top_module.xdc)
│   ├── fpga_reports/             # Báo cáo Vivado PPA (Baseline MAC, Secure MAC, Top SoC)
│   ├── scripts/                  # TCL scripts tổng hợp tự động (Baseline, Secure, Top)
│   └── vivado_project/           # Dự án GUI Vivado (.xpr) và waveform viewer (.wcfg)
│
├── reports/                # Báo cáo thực nghiệm, ma trận heatmap và datasets
│   ├── README.md
│   ├── master_verification_report.md # 📋 Báo cáo tổng thể kiểm chứng chất lượng (10 Suites, SVA, Coverage)
│   ├── exhaustive_fault_injection_report.md # Báo cáo tiêm lỗi 81,000 trials
│   ├── data/                     # Raw datasets (CSV, JSON) 26,040 mẫu thử thực nghiệm
│   └── figures/                  # Publication-ready charts and heatmaps (300+ DPI)
│
└── tools/                  # Bộ công cụ tự động hóa, linter và phân tích dữ liệu
    ├── README.md
    ├── analysis/                 # Generator báo cáo Word, Plotting & RTL inspection
    ├── fault_injection/          # Fault injection engine
    └── linting/                  # Static analysis (PySlang RTL Linters)
```

---

## 🗺️ Bản đồ Bộ nhớ & Thanh ghi MMIO (Memory Map)

| Dải địa chỉ (Hex) | Tên thanh ghi | Chức năng |
| :--- | :--- | :--- |
| `0x0000_0000` – `0x0000_03FF` | **Data Memory (DMEM)** | Bộ nhớ RAM 1KB lưu trữ biến, mảng trọng số và kết quả |
| `0x8000_0000` | `REG_MAC_A` (8-bit) | Toán hạng $A$ (Trọng số Weight, INT8 signed) |
| `0x8000_0004` | `REG_MAC_B` (8-bit) | Toán hạng $B$ (Đầu vào Activation, INT8 signed) |
| `0x8000_0008` | `REG_MAC_C` / `MAC_OUT` (32-bit) | Nạp giá trị cộng dồn $C$ hoặc đọc kết quả $A \times B + C$ (INT32) |
| `0x8000_000C` | `REG_MAC_START` (1-bit) | Ghi `1` để kích hoạt chu trình tính toán MAC |
| `0x8000_0014` | `REG_MAC_STATUS` (32-bit) | Bit 1: `valid` (tính xong), Bit 0: `fault_detected` (phát hiện lỗi) |

---

## 📊 Kết quả Thực nghiệm Tiêm lỗi (Fault Injection Campaign — 26,040 Mẫu thử)

| Kịch bản lỗi (Fault Scenario) | Số lượng mẫu | Tỷ lệ phát hiện (**FDR %**) | Lọt lỗi thầm lặng (**SDC %**) | Độ chính xác Rollback | Đặc trưng kỹ thuật |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Lỗi lật bit đơn (Single-Bit SEU)** | 3,200 | **100.00%** | **0.00%** | **100.00%** (1 CK) | Bảo vệ 100% toàn bộ 32 vị trí bit (Exhaustive) |
| **2. Lỗi khối kiểm tra (Checker Robustness)** | 300 | **100.00%** (Safe) | **0.00%** | **100.00%** (1 CK) | 100% Safe Fail / Safe Rollback, 0 SDC |
| **3. Lỗi kép 2-bit (Double-Bit MBU 32×32)** | 19,840 | **76.71%** (w/ Double-Check) | 23.29% | **100.00%** (1 CK) | Tăng từ 49.54% lên 76.71% nhờ Sanity Double-Check |
| **4. Lỗi chùm đa bit (Burst $k=1..6$)** | 2,700 | **92.70%** (Trung bình) | 7.30% | **100.00%** (1 CK) | Burst 2b: 77.4%, 3b: 91.8%, 4b: 92.2%, 5b: 97.0%, 6b: 97.8% |
| **TỔNG CỘNG TOÀN CHIẾN DỊCH** | **26,040** | **Bảo vệ toàn diện** | **Triệt tiêu trên SEU** | **100.00%** | **Timing Invariance 3 CK, 0 ns Jitter** |

> 📐 **Đóng góp lý thuyết:** Chứng minh định lý **Bit-Distance Parity Theorem**, giải thích tại sao tỷ lệ phát hiện lỗi 2-bit tuân theo tính chẵn lẻ của khoảng cách bit trong hệ thặng dư Modulo-3.

---

## ⚡ Kết quả Tổng hợp Phần cứng Thực tế (AMD Xilinx Vivado 2026.1 Benchmark)

Hiện thực hóa trên chip FPGA **Xilinx Zynq-7000** (`xc7z020clg400-1`):

### 1. Phân bổ Tài nguyên Phân cấp Toàn SoC (Khớp Bảng 3.1 trong Báo cáo)
| Khối chức năng (Instance) | Slice LUTs | Flip-Flops (FFs) | CARRY4 / MUX | Tỷ lệ trên XC7Z020 | Timing & Ghi chú |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Lõi CPU RISC-V (`u_cpu`)** | 620 (72.09%) | 864 (80.45%) | 28 CARRY4 | 1.17% LUT / 0.81% FF | WNS = +1.289 ns |
| **2. Bộ tăng tốc Secure MAC (`u_mac`)** | 135 (15.70%) | 138 (12.85%) | 28 CARRY4 | 0.25% LUT / 0.13% FF | Pipeline 3 tầng đồng bộ |
| **3. Bộ nhớ dữ liệu RAM (`u_dmem`)** | 61 (7.09%) | 32 (2.98%) | 32 Dist. RAM | 0.11% LUT / 0.03% FF | Ghép nối tầng MEM (1KB RAM) |
| **4. Logic ghép nối MMIO & Bus** | 44 (5.12%) | 40 (3.72%) | 0 | 0.08% LUT / 0.04% FF | 0 chu kỳ trễ bổ sung |
| **Tổng SoC Top (`top_module`)** | **860 (100.0%)** | **1,074 (100.0%)** | **56 CARRY4, 96 MUX** | **1.62% LUT / 1.01% FF** | **$F_{max} = 114.80$ MHz, WNS = +1.289 ns, Power = 122 mW** |
| *Khối Secure MAC Standalone* | *240 LUTs* | *138 FFs* | *36 CARRY4* | *0.45% LUT / 0.13% FF* | *$F_{max} = 119.88$ MHz, Power = 116 mW* |

### 2. So sánh Trực tiếp Baseline MAC và Secure MAC (Khớp Bảng 3.2 trong Báo cáo)
| Nhóm Chỉ số PPA | Baseline MAC (`baseline_mac.v`) | Secure MAC (`secure_mac.v`) | Chênh lệch / Chi phí (Overhead) | Toàn bộ SoC Top (`top_module.v`) |
| :--- | :--- | :--- | :--- | :--- |
| **Slice LUTs** | **99 LUTs** | **135 LUTs** (trong SoC)<br>*240 LUTs (Standalone)* | **+36 LUTs (+36.36% trên MAC / +4.19% SoC)** | **860 LUTs (1.62% chip)** |
| **Slice Registers (FFs)** | **131 FFs** | **137 FFs** (trong SoC)<br>*138 FFs (Standalone)* | **+6 FFs (+4.58% trên MAC / +0.56% SoC)** | **1,074 FFs (1.01% chip)** |
| **CARRY4 Logic** | **20 CARRY4** | **29 CARRY4** | **+9 CARRY4 (+45.00%)** | **56 CARRY4, 96 MUX** |
| **Khối DSP / BRAM** | **0 DSP, 0 BRAM** | **0 DSP, 0 BRAM** | **Thuần LUT logic fabric, khả chuyển cao** | **32 Dist. RAM (1KB)** |
| **Tần số cực đại ($F_{max}$)** | **176.50 MHz** | **119.88 MHz** (Standalone)<br>**114.80 MHz** (trong SoC) | **Toàn SoC đạt an toàn mốc 100 MHz** | **114.80 MHz** (WNS = +1.289 ns) |
| **Thời gian tới hạn ($T_{min}$)**| **5.665 ns** | **8.342 ns** (Standalone) | **+2.321 ns** (Trễ bộ so sánh & MUX) | **8.711 ns** |
| **Tổng công suất On-Chip** | **108 mW** (5 mW động, 103 mW tĩnh) | **116 mW** (14 mW động, 103 mW tĩnh) | **+6 mW (+5.55% trên MAC / +5.17% SoC)** | **122 mW (19 mW động, 103 mW tĩnh)** |
| **Biến thiên thời gian (Jitter)** | **0 ns** | **0 ns (Bất biến 3 chu kỳ)** | **Kháng Side-Channel Timing Attacks** | **Bất biến 3 CK** |

---

## 🔬 Bảng Đối Chiếu Đa Phương Pháp (Khớp Bảng 3.4 trong Báo cáo)

Bảng đối chiếu tổng hợp 13 tiêu chí kỹ thuật giữa giải pháp đề xuất và 5 nhóm phương pháp dung lỗi đại diện trong y văn quốc tế:

| # | Tiêu chí Đánh giá | TMR [1] | DMR [1, 3] | Parity [8, 13] | SW-EDDI [5, 14, 15] | Residue Code [4, 10, 16] | Modulo-3 CED (Đề xuất) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Cơ chế phát hiện lỗi** | Bỏ phiếu đa số (Majority Voter) từ 3 bản sao | So sánh kết quả song song (Dual Voter / Comparator) | Kiểm tra bit chẵn lẻ (1-bit Parity Tree) đính kèm nhóm dữ liệu | Nhân đôi chỉ lệnh & chèn bẫy so sánh (BNE) ở cấp trình biên dịch | Tính toán và so sánh theo đồng cấu thặng dư (Modulo Arithmetic) | **Đồng cấu số học Modulo-3 CED** |
| **2** | **Phạm vi bảo vệ** | Toàn bộ mạch tổ hợp & thanh ghi (Hardware/System-level) | Nhân đôi đường truyền (Datapath) và mạch logic | Bus, ô nhớ (SRAM/Reg), và không gian trạng thái (như AES) | Chỉ bảo vệ thanh ghi, biến dữ liệu & luồng lệnh CPU | Bảo vệ chuyên biệt cho mạch số học (Multiplier/Adder/Divider) | **Toàn bộ Datapath MAC & Thanh ghi tích lũy** |
| **3** | **Chi phí diện tích (Overhead LUTs)** | Rất lớn: +215% – 260% (> 2.100 LUTs) | Lớn: +108% – 125% (> 1.050 LUTs) | Nhỏ: ~10% – 20% (Chi phí sinh mã Parity) | 0% phần cứng (+115% Code Size phần mềm) | Thấp: +12% – 18% (~120 LUTs) | **+36,36% MAC (+4,19% SoC) (135 LUTs)** |
| **4** | **Chi phí thanh ghi (Overhead FFs)** | Rất cao: +200% – 220% (> 2.200 FFs) | Cao: +100% – 105% (> 1.100 FFs) | Thấp: +1,5% – 3,0% (1–2 bit FFs) | 0% phần cứng (Gây áp lực tràn thanh ghi CPU - Register Spilling) | Thấp: +4,0% – 8,0% (2–4 bit FFs) | **+4,58% MAC (+0,56% SoC) (137 FFs)** |
| **5** | **Phát hiện lỗi đơn SEU** | 100,0% (Voter tự phát hiện và sửa/mask) | 100,0% (Chỉ phát hiện, xuất cờ báo lỗi) | 100,0% (Phát hiện tất cả các lỗi đơn) | 95,2% – 98,6% (Trên luồng lệnh CPU) | 100,0% (Trên mạch số học) | **Có (100,0% Exhaustive)** |
| **6** | **Phát hiện lỗi kép MBU** | Một phần (< 50%) (Vô hiệu hóa nếu 2 nhánh cùng lỗi) | 100,0% (Chỉ không phát hiện nếu 2 kênh bị lỗi y hệt) | Rất cao (~99,1%) Chỉ bỏ sót 0,875% khi 2 bit lỗi tự bù trừ | 32,4% – 44,8% (Thanh ghi CPU) | ~50,0% (Tùy thuộc vào cơ số check base) | **48,39% (76,71% w/ Double-Check)** |
| **7** | **Phát hiện lỗi chùm đa bit ($k > 2$)** | Giảm nhanh (< 33% khi $k \ge 3$) | 100,0% (Nếu lỗi không đối xứng 2 kênh) | 100% (Lỗi chùm bậc lẻ), ~99,997% (Lỗi chùm bậc chẵn) | < 25,0% (Lỗi chùm thanh ghi) | Tiệm cận ~66% (Mô phỏng trên FPU) | **Tiệm cận 2/3 (66,67%)** |
| **8** | **Cơ chế Tự phục hồi (Self-Recovery)** | Có (Voter tự động che khuất lỗi tức thì) | Không (Chỉ báo cờ, cần hệ thống ngoài can thiệp) | Không (Chỉ phát hiện lỗi, trừ kỹ thuật lai PDMR+) | Không ở phần cứng (Cần gọi Error Handler/OS) | Không (Chỉ phát hiện lỗi CED thuần túy) | **Có — 1 CK Hardware Rollback** |
| **9** | **Thời gian phục hồi** | 0 Chu kỳ (CK) (Tức thì tại Voter) | Khởi động lại hoặc khôi phục 50 – 120 CK | N/A (Không tự sửa được) | Lớn (150 – 300 CK) (do trễ xử lý ngắt phần mềm) | N/A (Không hỗ trợ Rollback) | **1 CK (tức thì)** |
| **10** | **Kháng Side-Channel Timing Attack** | Không (Vẫn rò rỉ vết Power/EM) | Không (Nhân đôi vết công suất) | Không (Không thiết kế để bảo mật phần cứng) | Không (Jitter thời gian thực thi bị thay đổi lớn) | Không (Chưa được tối ưu về chu kỳ thời gian) | **Có (Constant-time 3 CK, 0 ns jitter)** |
| **11** | **Tích hợp CPU + MAC hoàn chỉnh** | Không (Thường bọc rời ở cấp hệ thống/block) | Mạng kết nối Bus / SoCs | Thường ở cấp độ Bộ nhớ / Bus / Module mã hóa | Chỉ áp dụng cho CPU (Không bảo vệ bộ tăng tốc) | Thiết kế riêng cho mạch nhân (MAC/FPU) | **Có — SoC RISC-V + Secure MAC** |
| **12** | **Xác thực trên FPGA thực tế / EDA** | Xilinx UltraScale+ (Vivado Design Suite) | Xilinx Zynq-7000 / FPGA | ASIC / FPGA Spartan-6 | Mô phỏng kiến trúc RISC-V Spike / MIPS | Tổng hợp ASIC TSMC (Synopsys DC) | **Có — Zynq-7000 Vivado 2026.1** |
| **13** | **Quy mô tiêm lỗi thực nghiệm** | ~10.000 mẫu (Mô phỏng mức SEU) | ~4.800 mẫu (Tiêm lỗi Bus & Core) | Lên tới $10^7$ phép mã hóa (Thuật toán AES) | ~8.500 mẫu (Tiêm lật bit Register File) | ~6.000 mẫu (Mô phỏng ALU/FPU) | **26.040 mẫu cốt lõi / 81.000 mẫu mở rộng** |

---

## 🧠 Benchmark Thực nghiệm Ứng dụng AI (INT8 Fully-Connected Neuron Inference)

Mô phỏng suy luận một nơ-ron mạng nơ-ron AI (16 đầu vào INT8: $Y = \sum_{i=0}^{15} W_i \cdot X_i + \text{Bias}$) dưới tác động tiêm lỗi lật bit bức xạ (SEU) tại bước tính toán thứ 7:

| Kiến trúc Kiểm chứng | Đầu ra Suy luận ($Y$) | Sai lệch Tuyệt đối (abs $\Delta Y$) | Tỷ lệ Lọt lỗi (SDC) | Kết quả Phân loại (Inference Accuracy) |
| :--- | :---: | :---: | :---: | :---: |
| **Chuẩn đối chứng (Golden Model)** | **-4,360** | **0** | **0.00%** | **Chính xác tuyệt đối (100.0%)** |
| **Mạch MAC cơ sở (Baseline MAC)** | **+12,024** | **16,384** (Lỗi tràn MSB) | **100.00% (SDC)** | **Thất bại (Phân loại sai hoàn toàn)** |
| **Mạch đề xuất (Secure MAC + Rollback)** | **-4,360** | **0** (Khôi phục tức thời) | **0.00% (Zero SDC)** | **Bảo toàn Độ chính xác (100.0%)** |

> [!NOTE]
> **Nhận xét thực nghiệm:** Khi xảy ra lỗi lật bit bức xạ SEU trên bộ tích lũy, Baseline MAC không phát hiện được và gây ra hiện tượng tràn bit MSB làm đảo chiều kết quả phân loại (từ `-4,360` sang `+12,024`). Trong khi đó, kiến trúc Secure MAC đề xuất phát hiện lỗi ngay trong chu kỳ hiện tại, lập tức kích hoạt thanh ghi bóng **Shadow Accumulator** để Rollback hoàn tác trạng thái đúng chỉ trong **đúng 1 chu kỳ clock**, bảo toàn độ chính xác suy luận đạt **100.0%**.

---

## 🔍 Phân tích Giới hạn Kỹ thuật & Biện pháp Khắc phục (Limitations & Mitigation)

1. **Giới hạn 50% FDR đối với Lỗi kép (MBU):**
   - Định lý *Bit-Distance Parity Theorem* giải thích rằng khi hai bit lỗi có khoảng cách lẻ ($d \in \{1, 3, 5...\}$), sai số thặng dư triệt tiêu theo $\pmod 3$.
2. **Biện pháp Khắc phục Toàn diện (3-Tier Mitigation):**
   - **Physical Bit-Interleaving Layout [17]:** Bố trí cell nhớ vật lý xen kẽ chẵn/lẻ (khoảng cách vật lý 1 $\rightarrow$ khoảng cách logic chẵn), chuyển hóa 100% lỗi chùm vật lý thành dạng phát hiện được.
   - **Composite RNS Modulo-3 + Modulo-5 [18]:** Tích hợp thêm kênh Modulo-5 (chu kỳ 4) bù trừ hoàn toàn điểm mù của Modulo-3, nâng độ bao phủ MBU lên **> 93.75%**.
   - **Calibrated Range Checking:** Bẫy dị thường biên tích lũy $\pm 3,276,700$ phát hiện ngay các lỗi lật bit MSB gây tràn biên mạng AI.

---

## 🚀 Hướng dẫn Chạy & Tái tạo Kết quả (Quick Start)

### 1. Cài đặt Môi trường
```bash
pip install cocotb cocotb-tools pyslang python-docx matplotlib
```
*Đảm bảo máy đã cài đặt **Icarus Verilog (`iverilog`)** và **AMD Xilinx Vivado 2026.1**.*

### 2. Chạy toàn bộ 10 Bộ Kiểm thử (Master Regression Runner ~56s)
```bash
python run_all_tests.py
```

### 3. Kiểm tra Độ phủ Chức năng (Functional Coverage Models)
```bash
# Kiểm tra độ phủ toán hạng & thặng dư Modulo-3 của Secure MAC (100%)
python -m pytest tb/cocotb/secure_mac/mac_coverage.py

# Kiểm tra độ phủ tổ hợp ALU Control & Corner Cases (91.25%)
python -m pytest tb/cocotb/alu_top/alu_coverage.py
```

### 4. Chạy Tổng hợp & Thực thi FPGA tự động (AMD Xilinx Vivado 2026.1)
```powershell
# Chạy tổng hợp Baseline MAC
& "C:\AMDDesignTools\2026.1\Vivado\bin\vivado.bat" -mode batch -source "synth/scripts/run_synth_baseline_mac.tcl"

# Chạy tổng hợp Secure MAC
& "C:\AMDDesignTools\2026.1\Vivado\bin\vivado.bat" -mode batch -source "synth/scripts/run_synth.tcl"

# Chạy tổng hợp toàn bộ SoC Top
& "C:\AMDDesignTools\2026.1\Vivado\bin\vivado.bat" -mode batch -source "synth/scripts/run_synth_top.tcl"
```

---

## 👥 Tác giả & Thông tin Đề tài (Authors & Acknowledgments)

- **Tác giả / Chủ nhiệm đề tài:** Quách Tuấn Thành ([@quachtuanthanh80-arch](https://github.com/quachtuanthanh80-arch))
- **Đề tài:** Nghiên cứu & Hiện thực hóa Lõi Vi xử lý RISC-V tích hợp Bộ tăng tốc AI Secure MAC Dung lỗi Phần cứng (Fault-Resilient RISC-V SoC with Modulo-3 Secure MAC).
- **Phân loại:** Đồ án / Đề tài Nghiên cứu Khoa học (NCKH 2026).
- **Mã nguồn chính thức:** [https://github.com/quachtuanthanh80-arch/NCKH-RISCV-Secure-MAC](https://github.com/quachtuanthanh80-arch/NCKH-RISCV-Secure-MAC)

---

## 📜 Giấy phép (License)

Dự án được phát hành theo giấy phép mã nguồn mở **MIT License** — Xem chi tiết tại tệp [LICENSE](LICENSE).
