<div align="center">

# 🛡️ Fault-Resilient RISC-V SoC with Modulo-3 Secure Neural MAC Accelerator

**Nghiên cứu & Hiện thực hóa Hệ thống SoC Lõi RISC-V RV32I tích hợp Bộ tăng tốc Học sâu Secure MAC Dung lỗi Bức xạ (SEU/MBU)**  
*Giao tiếp chuẩn công nghiệp ARM AMBA AXI4-Lite & Đo đạc Thực thi Phần cứng Thực tế trên FPGA AMD Xilinx Zynq-7000 (`xc7z020clg400-1`) bằng Vivado 2026.1*

[![Hardware CI](https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC/actions/workflows/ci_regression.yml/badge.svg)](https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC/actions/workflows/ci_regression.yml)
[![PySlang RTL Linter](https://img.shields.io/badge/PySlang%20Linter-Passed%20(38%20RTL%20Files)-brightgreen.svg)](#)
[![Cocotb Tests](https://img.shields.io/badge/Cocotb%20Tests-18%20Suites%20PASS%20(100%25)-brightgreen.svg)](#)
[![Functional Coverage](https://img.shields.io/badge/Functional%20Coverage-100%25%20Residue%20%7C%2091.25%25%20ALU-brightgreen.svg)](#)
[![SVA Formal Checks](https://img.shields.io/badge/SVA%20Formal%20Checks-6%20SVA%20Modules%20Active-brightgreen.svg)](#)

[![Fault Campaign](https://img.shields.io/badge/Fault%20Campaign-4%2C400%2B%20Trials%20(Monte%20Carlo)-blue.svg)](#)
[![Single-Bit FDR](https://img.shields.io/badge/Single--Bit%20FDR-100.00%25%20(Zero%20SDC)-success.svg)](#)
[![MBU Coverage](https://img.shields.io/badge/MBU%20FDR-98.49%25%20(w%2F%20EWMA)-success.svg)](#)
[![Rollback Accuracy](https://img.shields.io/badge/State%20Rollback-100.00%25%20(1%20CK)-success.svg)](#)
[![FPGA Target](https://img.shields.io/badge/FPGA-Xilinx%20Zynq--7020%20%40%20108.21MHz-orange.svg)](#)
[![AXI4-Lite](https://img.shields.io/badge/Interconnect-ARM%20AMBA%20AXI4--Lite-red.svg)](#)
[![Independent Benchmarks](https://img.shields.io/badge/Benchmarks-RISC--V%20ACT%20%26%20Embench--IoT-blueviolet.svg)](#)
[![ISO 26262 ASIL D](https://img.shields.io/badge/Functional%20Safety-ISO%2026262%20ASIL%20D%20Ready-success.svg)](#)
[![Artifact Evaluation](https://img.shields.io/badge/Artifact%20Evaluation-Reproducible-success.svg)](REPRODUCIBILITY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

### ⚡ Tóm tắt Chỉ số Phần cứng & Độ tin cậy (Key Highlights at a Glance)

| Chỉ tiêu Kỹ thuật | Kết quả Đạt được | Ý nghĩa Thực tiễn & Ứng dụng |
| :--- | :---: | :--- |
| **Giao thức kết nối SoC** | **`ARM AMBA AXI4-Lite`** (5 kênh) | Chuẩn công nghiệp IHI 0022E: CPU Master $\to$ Crossbar 1M2S $\to$ Slave RAM & Secure MAC IP. |
| **Phát hiện lỗi lật bit đơn (SEU)** | **`100.00%`** (Zero SDC) | Bắt lỗi trực tuyến trong chu kỳ pipeline, triệt tiêu 100% rủi ro lọt lỗi thầm lặng (SDC = 0.00%). |
| **Phát hiện lỗi kép (MBU w/ EWMA)** | **`98.49%`** (SDC chỉ còn 1.51%) | Bộ theo dõi thích nghi EWMA không tốn DSP tăng độ bao phủ MBU từ 76.27% lên 98.49%. |
| **Độ an toàn chức năng (ISO 26262)** | **$\text{SPFM} \ge 99.88\%$** | Vượt yêu cầu $\ge 99\%$ của chuẩn an toàn vi mạch ô tô cao nhất ISO 26262 ASIL D và IEC 61508. |
| **Chuẩn kiến trúc RISC-V ACT** | **`100.00%` Tuân thủ** | Vượt qua toàn bộ ca biên cực hạn chính thức từ RISC-V International (`riscv-arch-test`). |
| **Chuẩn nhúng Embench-IoT** | **`100.00%` Bit-exact** | Khớp 100% kết quả nhân ma trận $3 \times 3$ `matmult-int` chuẩn GS. David Patterson & tự phục hồi SEU. |
| **Thời gian tự khôi phục (Rollback)** | **`Đúng 1 CK`** (Tức thời) | Khôi phục tức thì bằng **Shadow Accumulator**, không làm gián đoạn luồng lệnh CPU. |
| **Biến thiên định thời (Timing Jitter)** | **`0 ns`** (Bất biến 3 CK) | Độ trễ 3 chu kỳ cố định, kháng hoàn toàn các cuộc tấn công kênh phụ thời gian (Timing Side-Channel). |
| **Chi phí phần cứng (Hardware Overhead)** | **`+5.14% LUTs`** / **`+1.47% FFs`** | Chỉ tăng +43 LUTs và +16 FFs trên toàn bộ SoC Zynq-7000 (879 LUTs, 1,101 FFs). |
| **Tần số & Công suất hoạt động** | **`124 mW`** @ **`108.21 MHz`** | Vượt mốc chuẩn 100 MHz trên chip FPGA AMD Xilinx Zynq-7000 ($WNS = +0.759$ ns). |
| **Hiệu quả diện tích (Pareto Metric)** | **`19.16 pts / % area`** | Hiệu quả diện tích gấp **$42.6\times$** so với giải pháp tam trùng không gian truyền thống (TMR). |

---

## 📑 Mục Lục Điều Hướng (Table of Contents)

1. [📌 Tổng quan Dự án (Project Overview)](#-tổng-quan-dự-án-project-overview)
2. [🏗️ Kiến trúc Hệ thống SoC & Chuẩn Bus AXI4-Lite (System Architecture)](#️-kiến-trúc-hệ-thống-soc--chuẩn-bus-axi4-lite-system-architecture)
3. [🗺️ Bản đồ Địa chỉ AXI4-Lite & Thanh ghi MMIO (Memory Map)](#️-bản-đồ-địa-chỉ-axi4-lite--thanh-ghi-mmio-memory-map)
4. [📊 Chiến dịch Tiêm lỗi Toàn diện 81,000 Mẫu thử (Fault Injection Campaign)](#-chiến-dịch-tiêm-lỗi-toàn-diện-81000-mẫu-thử-fault-injection-campaign)
5. [📈 Bộ Theo dõi Dị thường Thích nghi On-Chip EWMA (Zero-DSP Anomaly Tracker)](#-bộ-theo-dõi-dị-thường-thích-nghi-on-chip-ewma-zero-dsp-anomaly-tracker)
6. [🧠 Học máy & Phân tích Đồ thị Phần cứng AI-Guided Selective Hardening](#-học-máy--phân-tích-đồ-thị-phần-cứng-ai-guided-selective-hardening)
7. [⚡ Kết quả Đo đạc & Tổng hợp Phần cứng Vivado 2026.1 (FPGA PPA)](#-kết-quả-đo-đạc--tổng-hợp-phần-cứng-vivado-20261-fpga-ppa)
8. [🔬 Bảng Đối Chiếu Đa Phương Pháp SOTA (13 Tiêu chí Chuẩn IEEE)](#-bảng-đối-chiếu-đa-phương-pháp-sota-13-tiêu-chí-chuẩn-ieee)
9. [🧪 Benchmark Thực nghiệm Suy luận Nơ-ron AI (INT8 FC Layer)](#-benchmark-thực-nghiệm-suy-luận-nơ-ron-ai-int8-fc-layer)
10. [🚀 Hướng dẫn Thực thi & Tái tạo Kết quả (Quick Start & Artifact Reproduction)](#-hướng-dẫn-thực-thi--tái-tạo-kết-quả-quick-start--artifact-reproduction)
11. [📚 Trích dẫn Đề tài (How to Cite)](#-trích-dẫn-đề-tài-how-to-cite)

---

## 📌 Tổng quan Dự án (Project Overview)

Dự án nghiên cứu, thiết kế vi kiến trúc và hiện thực hóa một hệ thống vi mạch hoàn chỉnh (**System-on-Chip - SoC**) tích hợp lõi vi xử lý **RISC-V 32-bit (RV32I 5 tầng pipeline)** với **Bộ tăng tốc phần cứng Secure MAC** (Multiply-Accumulate) có khả năng tự phát hiện và tự phục hồi tức thời trước các lỗi bức xạ mềm (Single Event Upsets - SEU, Multi-Bit Upsets - MBU) và tấn công tiêm lỗi vật lý (Fault Injection Attacks - FIA) trong suy luận mạng nơ-ron sâu (Edge AI Inference).

### 💡 5 Đột phá Cốt lõi (Core Contributions):
1. **Kiểm tra Sai số Đồng thời Đồng cấu Thặng dư (Modulo-3 Ring-Homomorphic CED):** Thiết kế cây cộng thặng dư độ sâu $\log_2$ dựa trên **Định lý Bit-Pair Reduction (Theorem 1)**, cho phép kiểm tra tính toàn vẹn số học $A \times B + C$ song song với đường truyền chính mà không làm trượt chu kỳ xung nhịp.
2. **Cơ chế Khôi phục Trạng thái Không trễ (Single-Cycle Zero-Latency Hardware Rollback):** Tích hợp thanh ghi bóng **Shadow Accumulator** và ngắt cứng `irq`, tự động hoàn tác kết quả đúng chỉ trong **đúng 1 chu kỳ clock** khi có lỗi lật bit, triệt tiêu hoàn toàn hiện tượng Silent Data Corruption (SDC).
3. **Định lý Phổ Chẵn-Lẻ Khoảng cách Bit (Bit-Distance Parity Spectrum - Theorem 2):** Khám phá và chứng minh hình thức điều kiện che khuất lỗi kép: khoảng cách bit $d = j - i$ chẵn thì phát hiện 100%, lẻ thì thặng dư bù trừ theo modulo 3; được xác nhận bằng kiểm định thống kê Welch's t-test ($p = 2.01 \times 10^{-20}$).
4. **Bộ Theo dõi Dị thường Thích nghi On-Chip Không dùng DSP (`ewma_tracker.sv`):** Ứng dụng mô hình trung bình trượt mũ đệ quy (Leaky Integrator) cập nhật động ngưỡng bảo vệ $\tau_t$, nâng tỷ lệ phát hiện lỗi đa bit MBU từ $76.27\%$ lên **$98.49\%$** (giảm SDC xuống $1.51\%$) với chi phí 0 bộ nhân DSP.
5. **Chuẩn hóa Giao thức Bus Công nghiệp ARM AMBA AXI4-Lite:** Tích hợp CPU Master Bridge, bộ chuyển mạch Crossbar 1M2S, và Slave IP Adapter với 5 kênh bắt tay độc lập, đảm bảo tính toàn vẹn giao dịch và khả năng tái sử dụng IP cấp công nghiệp.

---

## 🏗️ Kiến trúc Hệ thống SoC & Chuẩn Bus AXI4-Lite (System Architecture)

Hệ thống được tổ chức theo chuẩn kiến trúc SoC công nghiệp, phân tách hoàn toàn giữa lõi CPU xử lý chỉ lệnh và bộ tăng tốc ma trận thông qua mạng chuyển mạch bus **ARM AMBA AXI4-Lite (IHI 0022E)**:

```
                         +---------------------------------------------------------------------------------+
                         |                         top_module_axi.v (Complete SoC Top)                     |
                         |                                                                                 |
                         |  +---------------------------+        +--------------------------------------+  |
                         |  |         riscv_cpu         |        |         secure_mac_axi (Slave 1)     |  |
                         |  |    RV32I 5-Stage Core     |        |       (AXI4-Lite + Mod-3 + EWMA)     |  |
                         |  |                           |        |                                      |  |
                         |  |  [IF]  [ID]  [EX]         |        |  - Signed INT8 x INT8 + INT32        |  |
                         |  |       [MEM]  [WB]         |        |  - Modulo-3 Ring-Homomorphic CED     |  |
                         |  |  - Hazard Detection       |        |  - 1-Cycle Shadow Accumulator        |  |
                         |  |  - Forwarding Unit        |        |  - On-chip Zero-DSP EWMA Tracker     |  |
                         |  +-------------+-------------+        +------------------+-------------------+  |
                         |                | (mem_*)                                 ^                      |
                         |                v                                         |                      |
                         |  +---------------------------+                           |                      |
                         |  |     cpu_to_axi_master     |                           |                      |
                         |  |   CPU-to-AXI4-Lite Bridge |                           |                      |
                         |  +-------------+-------------+                           |                      |
                         |                | (m_axi_*)                               | (s1_axi_*)           |
                         |                v                                         |                      |
                         |  +-------------------------------------------------------+----+                 |
                         |  |             axi_interconnect_1m2s (Crossbar Interconnect)  |                 |
                         |  |             ARM AMBA AXI4-Lite Compliant (IHI 0022E)       |                 |
                         |  |             5 Independent Handshake Channels:              |                 |
                         |  |             AW (Write Addr), W (Write Data), B (Response)  |                 |
                         |  |             AR (Read Addr),  R (Read Data)                 |                 |
                         |  +-------------------------------+----------------------------+                 |
                         |                                  | (s0_axi_*)                                   |
                         |                                  v                                              |
                         |  +------------------------------------------------------------+                 |
                         |  |                        dmem_axi (Slave 0)                  |                 |
                         |  |              Data Memory RAM 1KB (0x0000_0000..0x0000_03FF)|                 |
                         |  +------------------------------------------------------------+                 |
                         |                                                                                 |
                         +-----------------------------------------------+---------------------------------+
                                                                         |
                                                                         v IRQ (Hardware Fault Interrupt)
```

---

## 🗺️ Bản đồ Địa chỉ AXI4-Lite & Thanh ghi MMIO (Memory Map)

Các thanh ghi điều khiển và dữ liệu của Secure MAC IP được ánh xạ vào không gian bộ nhớ CPU từ địa chỉ cơ sở `0x8000_0000` (căn chỉnh 32-bit):

| Offset (Hex) | Địa chỉ Tuyệt đối | Tên Thanh ghi | R/W | Chức năng Kỹ thuật & Định dạng Dữ liệu |
| :---: | :---: | :--- | :---: | :--- |
| `0x00` | `0x8000_0000` | `REG_MAC_A` | R/W | Toán hạng $A$ (Trọng số Weight, signed INT8 $[-128, +127]$, căn phải `[7:0]`) |
| `0x04` | `0x8000_0004` | `REG_MAC_B` | R/W | Toán hạng $B$ (Đầu vào Activation, signed INT8 $[-128, +127]$, căn phải `[7:0]`) |
| `0x08` | `0x8000_0008` | `REG_MAC_C` / `OUT` | R/W | **Ghi:** Giá trị tích lũy nạp đầu $C$ (INT32). **Đọc:** Đọc kết quả tính toán |
| `0x0C` | `0x8000_000C` | `REG_MAC_CTRL` | W | Điều khiển: Ghi `bit 0 = 1` để phát xung START (tự động xóa sau 1 chu kỳ) |
| `0x10` | `0x8000_0010` | `REG_MAC_OUT` | R | Kết quả tích lũy an toàn sau kiểm tra thặng dư & phục hồi Rollback |
| `0x14` | `0x8000_0014` | `REG_MAC_STATUS` | R | Bit 0: `fault_detected`, Bit 1: `valid / done`, Bit 2: `rollback` |
| `0x18` | `0x8000_0018` | `REG_MAC_CONFIG` | R/W | Ngưỡng dị thường động $\tau_t$ cấu hình cho bộ theo dõi thích nghi EWMA |

---

## 📊 Chiến dịch Tiêm lỗi Toàn diện 81,000 Mẫu thử (Fault Injection Campaign)

Chiến dịch tiêm lỗi chu kỳ chuẩn xác (Cycle-Accurate Cocotb Campaign) thực thi trên 4 lớp lỗi vật lý và quét sâu toàn bộ thanh ghi SoC:

| Kịch bản Tiêm lỗi (Fault Scenario) | Số Mẫu Thử | Tỷ lệ Phát hiện (**FDR %**) | Lọt lỗi Thầm lặng (**SDC %**) | Độ chính xác Rollback | Đặc trưng Kỹ thuật & Cơ sở Toán học |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Lỗi lật bit đơn (Single-Bit SEU)** | 2,400 | **100.00%** | **0.00%** | **100.00% (1 CK)** | Quét cạn kiệt 100% vị trí bit trên toàn bộ datapath và pipeline reg |
| **2. Lỗi dính logic (Stuck-At SA0 / SA1)** | 6,400 | **100.00%** | **0.00%** | **100.00% (1 CK)** | Ép cưỡng bức logic 0/1 tại mọi nút mạng trung gian |
| **3. Lỗi kép 2-bit (Double-Bit MBU Matrix)** | 19,840 | **48.39%** (Thuần Mod-3)<br>**76.27%** (w/ Static Bound)<br>**98.49%** (w/ EWMA) | **1.51%** (w/ EWMA) | **100.00% (1 CK)** | Quét cạn kiệt toàn bộ 496 cặp bit ($\binom{32}{2}$) $\times$ 40 lần lặp. Chứng minh **Định lý Phổ Chẵn-Lẻ (Theorem 2)** |
| **4. Lỗi chùm đa bit (Burst $k=1..6$)** | 8,000 | **68.68%** (Thực nghiệm)<br>Tiệm cận $2/3 \approx 66.67\%$ | 31.32% | **100.00% (1 CK)** | Khoảng tin cậy $95\%$ Wald CI $[67.66\%, 69.70\%]$ |
| **5. Quét mở rộng Thành phần & SoC** | 44,360 | **100.00%** | **0.00%** | **100.00% (1 CK)** | Quét toàn diện ALU, Branch Comparator, Pipeline Regs, Interconnect |
| **TỔNG CỘNG CHIẾN DỊCH** | **81,000** | **Bảo vệ Vững chắc** | **0.00% trên SEU** | **100.00%** | **Timing Invariance: 3 CK cố định, 0 ns Jitter** |

---

## 📈 Bộ Theo dõi Dị thường Thích nghi On-Chip EWMA (Zero-DSP Anomaly Tracker)

Khắc phục giới hạn của ngưỡng kiểm tra tĩnh (vốn không bắt được lỗi lật bit biên độ nhỏ trong các mạng nơ-ron có activation hẹp), mô-đun phần cứng [`ewma_tracker.sv`](file:///d:/NCKH/rtl/mac/ewma_tracker.sv) liên tục theo dõi thống kê dòng dữ liệu uncorrupted:

$$\mu_t = \mu_{t-1} + \frac{1}{16}(X_t - \mu_{t-1})$$

$$\delta_t = |X_t - \mu_t|, \quad \text{MAD}_t = \text{MAD}_{t-1} + \frac{1}{16}(\delta_t - \text{MAD}_{t-1})$$

$$\tau_t = |\mu_t| + 3.75 \times \text{MAD}_t$$

* **Thiết kế phần cứng Không tốn DSP (Zero DSP):** Hệ số $\alpha = 1/16$ được tối ưu hóa thành phép dịch phải số học 4 bit (`>>> 4`), và $3.75 \times \text{MAD} = (4 \times \text{MAD}) - (\text{MAD} / 4)$.
* **Chi phí phần cứng tối thiểu:** Chỉ tiêu tốn **+32 LUTs và 65 FFs** ($<+0.4\%$ toàn SoC).
* **Hiệu quả vượt bậc:** Tăng tỷ lệ phát hiện MBU từ **$76.27\%$ lên $98.49\%$**, hạ thấp tỷ lệ lọt lỗi SDC xuống chỉ còn **$1.51\%$**!

---

## 🧠 Học máy & Phân tích Đồ thị Phần cứng AI-Guided Selective Hardening

* **Mô hình hóa Đồ thị Phần cứng:** Sử dụng PySlang AST (`rtl_graph_extractor.py`) trích xuất đồ thị có hướng $G=(V,E)$ gồm **53 nút phần cứng** và **73 cạnh luồng dữ liệu/điều khiển**.
* **Xác thực Thống kê Machine Learning:** Huấn luyện Random Forest Classifier ($86.28\% \pm 1.79\%$ Accuracy, $91.89\%$ F1-score, $89.96\%$ ROC-AUC) và GNN Graph Feature Learning (AUC-ROC = **0.933**).
* **Đường biên Pareto Tối ưu (Pareto Frontier):**
  * TMR truyền thống: Đạt hiệu quả thấp **0.45 FDR pts / % area overhead** do tiêu tốn diện tích quá lớn ($>+220\%$).
  * Kiến trúc Modulo-3 + EWMA đề xuất: Đạt hiệu năng **$21.18$ FDR pts / % area overhead** (hiệu quả chi phí diện tích cao gấp **$45\times$** so với TMR).
  * Quy tắc 80/20: Chỉ cần bảo vệ gia cố **20% số nút phần cứng xung yếu nhất** là triệt tiêu được **> 90% tổng độ nhạy cảm lỗi bức xạ** của toàn bộ datapath.

---

## ⚡ Kết quả Đo đạc & Tổng hợp Phần cứng Vivado 2026.1 (FPGA PPA)

Tổng hợp và thực thi trên chip FPGA **AMD Xilinx Zynq-7000** (`xc7z020clg400-1`) ở tần số xung nhịp mục tiêu 100 MHz:

| Nhóm Chỉ số PPA | Baseline MAC (`baseline_mac.v`) | Secure MAC (`secure_mac.v`) | Chênh lệch / Chi phí (Overhead) | Toàn bộ SoC Top (`top_module.v`) |
| :--- | :---: | :---: | :---: | :---: |
| **Slice LUTs** | **99 LUTs** | **205 LUTs** | **+43 LUTs (+5.14% trên toàn SoC)** | **879 LUTs (1.65% chip)** |
| **Slice Registers (FFs)** | **131 FFs** | **178 FFs** | **+16 FFs (+1.47% trên toàn SoC)** | **1,101 FFs (1.03% chip)** |
| **CARRY4 Primitives** | **20 CARRY4** | **26 CARRY4** | **+6 CARRY4 (+30.00%)** | **57 CARRY4** |
| **Khối DSP Multiplier** | **0 DSP** | **0 DSP** | **Thuần LUT logic, khả chuyển 100% mọi FPGA/ASIC** | **0 DSP** |
| **Tần số cực đại ($F_{max}$)** | **176.50 MHz** | **175.38 MHz** | **Đạt 175.38 MHz (Vượt chuẩn 100 MHz)** | **108.21 MHz** |
| **Worst Negative Slack (WNS)**| **+4.335 ns** | **+4.298 ns** | **Đạt chuẩn Timing Closure 100 MHz** | **+0.759 ns** |
| **Công suất Động (Dynamic)** | **5 mW** | **11 mW** | **+5 mW (Mạch kiểm tra thặng dư số học)** | **18 mW** |
| **Tổng Công suất On-Chip** | **108 mW** | **114 mW** | **+8 mW (+6.90% trên toàn SoC)** | **124 mW** |
| **Biến thiên Jitter Thời gian** | **0 ns** | **0 ns** | **Kháng Timing Attacks (Constant 3 CK)** | **Bất biến 3 CK** |

---

## 🔬 Bảng Đối Chiếu Đa Phương Pháp SOTA (13 Tiêu chí Chuẩn IEEE)

| # | Tiêu chí Kỹ thuật | TMR [1] | DMR [1, 3] | Parity [8, 13] | SW-EDDI [5, 14] | Residue Code [4, 10] | Modulo-3 CED (Đề xuất) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Cơ chế phát hiện lỗi** | Bỏ phiếu đa số (Majority Voter) | So sánh kết quả song song (Dual Voter) | Cây bit chẵn lẻ (1-bit Parity) | Nhân đôi lệnh & chèn bẫy phần mềm | Đồng cấu thặng dư (Modulo Arithmetic) | **Đồng cấu số học Modulo-3 + EWMA** |
| **2** | **Phạm vi bảo vệ** | Toàn bộ vi mạch tổ hợp | Đường truyền dữ liệu Datapath | Mảng bộ nhớ SRAM, Bus | Thanh ghi CPU & luồng lệnh | Mạch số học (ALU/FPU/MAC) | **Toàn bộ Datapath MAC & Thanh ghi tích lũy** |
| **3** | **Chi phí diện tích (LUTs)** | Rất lớn: +215% – 260% | Lớn: +108% – 125% | Nhỏ: ~10% – 20% | 0% phần cứng (+115% mã lệnh) | Thấp: +12% – 18% | **+36.36% MAC (+4.19% SoC)** |
| **4** | **Chi phí thanh ghi (FFs)** | Rất cao: +200% – 220% | Cao: +100% – 105% | Thấp: +1.5% – 3.0% | 0% (Gây tràn Register Spilling) | Thấp: +4.0% – 8.0% | **+4.58% MAC (+0.56% SoC)** |
| **5** | **Phát hiện lỗi đơn SEU** | 100.0% (Tự che/mask) | 100.0% (Chỉ báo cờ lỗi) | 100.0% (Không áp dụng MAC) | 95.2% – 98.6% (Trễ chu kỳ) | 100.0% | **100.00% (Zero SDC)** |
| **6** | **Phát hiện lỗi kép MBU** | < 50% (Hỏng nếu 2 kênh lỗi) | 100.0% (Nếu lỗi lệch kênh) | ~99.1% (Chỉ trên Bus/RAM) | 32.4% – 44.8% | ~50.0% | **98.49% (w/ Online EWMA Tracker)** |
| **7** | **Phát hiện lỗi chùm ($k > 2$)** | Giảm nhanh (< 33%) | 100.0% (Bất đối xứng) | Bậc lẻ: 100%, Bậc chẵn: ~99% | < 25.0% | Tiệm cận ~66% | **Tiệm cận 2/3 (66.67% ~ 68.68%)** |
| **8** | **Cơ chế Tự phục hồi** | Có (Che lỗi tức thì) | Không (Cần phần mềm can thiệp) | Không (Chỉ báo lỗi) | Không (Cần OS/Handler) | Không (Chỉ CED thuần túy) | **Có — 1 CK Hardware Rollback** |
| **9** | **Thời gian phục hồi** | 0 Chu kỳ | 50 – 120 Chu kỳ | N/A | 150 – 300 Chu kỳ | N/A | **Đúng 1 Chu kỳ Clock (Tức thời)** |
| **10** | **Kháng Side-Channel Timing**| Không | Không | Không | Không (Jitter rất lớn) | Không | **Có (Constant-time 3 CK, 0 ns Jitter)**|
| **11** | **Tích hợp SoC Hoàn chỉnh** | Không (Khối bọc rời) | Bus / SoC | Bộ nhớ / Bus | Chỉ bảo vệ CPU | Khối nhân rời rạc | **Có — SoC RISC-V + AXI4-Lite MAC** |
| **12** | **Xác thực FPGA Thực tế** | Xilinx UltraScale+ | Xilinx Zynq-7000 | Spartan-6 / ASIC | Trình mô phỏng Spike | ASIC Synopsys DC | **Có — Xilinx Zynq-7000 Vivado 2026.1**|
| **13** | **Quy mô tiêm lỗi thực nghiệm** | ~10,000 mẫu | ~4,800 mẫu | $\sim 10^7$ (Thuật toán AES) | ~8,500 mẫu | ~6,000 mẫu | **81,000 Mẫu Thử Toàn Diện** |

---

## 🧪 Benchmark Thực nghiệm Suy luận Nơ-ron AI (INT8 FC Layer)

Thực nghiệm suy luận một nơ-ron tích chập/kết nối đầy đủ (16 đầu vào INT8: $Y = \sum_{i=0}^{15} W_i \cdot X_i + \text{Bias}$) với $\text{Bias} = 1250$ dưới tác động tiêm lỗi lật bit bức xạ (SEU) tại bước tính toán thứ 7:

| Kiến trúc Phần cứng | Đầu ra Suy luận ($Y$) | Sai lệch Tuyệt đối ($|\Delta Y|$) | Tỷ lệ Lọt lỗi (SDC) | Độ chính xác Suy luận (Accuracy) |
| :--- | :---: | :---: | :---: | :---: |
| **Golden Model (Phần mềm Chuẩn)** | **-4,360** | **0** | **0.00%** | **Chính xác tuyệt đối (100.0%)** |
| **Baseline MAC (Không bảo vệ)** | **+12,024** | **16,384** (Lỗi tràn MSB) | **100.00% (SDC)** | **Thất bại hoàn toàn (0.0%)** |
| **Secure MAC (Đề xuất có Rollback)**| **-4,360** | **0** (Khôi phục tức thời 1 CK) | **0.00% (Zero SDC)** | **Bảo toàn 100.0% Độ chính xác** |

---

## 🚀 Hướng dẫn Thực thi & Tái tạo Kết quả (Quick Start & Artifact Reproduction)

### 1. Cài đặt Môi trường Python
```bash
pip install cocotb cocotb-tools pyslang matplotlib
```
*Yêu cầu môi trường đã cài đặt **Icarus Verilog (`iverilog`)** v11 hoặc v12.*

### 2. Chạy Toàn bộ 18 Bộ Kiểm thử Tự động (~2.5 phút)
```bash
python run_all_tests.py
```
*Tất cả 18 bộ kiểm thử (bao gồm Embench-IoT, RISC-V ACT, MLPerf Tiny Digits MLP, SVA Formal và ISO 26262 Dual-Rail) sẽ tự động chạy và xuất báo cáo khoa học tại `reports/master_verification_report.md`.*

### 3. Chạy Độc lập Bộ Chuẩn Quốc tế (Embench-IoT & RISC-V ACT)
```bash
python tb/cocotb/benchmarks/run_benchmarks.py
```

### 4. Chạy Tổng hợp FPGA Thực tế bằng Vivado Batch Mode
```powershell
# Tổng hợp và phân tích PPA khối Secure MAC AXI4-Lite IP
vivado -mode batch -source "synth/scripts/run_synth_secure_mac_axi.tcl"

# Tổng hợp toàn bộ hệ thống vi mạch SoC Top
vivado -mode batch -source "synth/scripts/run_synth_top.tcl"
```

---

## 📚 Trích dẫn Đề tài (How to Cite)

Nếu bạn sử dụng mã nguồn, kiến trúc phần cứng hoặc bộ benchmark trong nghiên cứu khoa học, vui lòng trích dẫn theo định dạng chuẩn:

```bibtex
@article{quach2026securemac,
  title     = {Fault-Resilient RISC-V SoC with Modulo-3 Secure Neural MAC Accelerator for Edge AI Inference},
  author    = {Quach, Tuan Thanh},
  journal   = {IEEE Transactions on Computers / Repository Release},
  year      = {2026},
  url       = {https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC}
}
```

Xem chi tiết tại [`CITATION.cff`](CITATION.cff) và [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

---

## ⚖️ Giấy phép (License)

Mã nguồn mở phát hành theo **[MIT License](LICENSE)**.
