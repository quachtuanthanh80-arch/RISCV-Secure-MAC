import os

def update_readme_exact():
    path = "README.md"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Summary Highlights
    t_start = "| **Chi phí phần cứng (Hardware Overhead)** |"
    t_end = "| **Hiệu quả diện tích (Pareto Metric)** | **`21.18 pts / % area`** | Hiệu quả diện tích gấp **$45\\times$** so với giải pháp tam trùng không gian truyền thống (TMR). |"

    idx1 = text.find(t_start)
    idx2 = text.find(t_end) + len(t_end)

    new_highlights = """| **Chi phí phần cứng (Hardware Overhead)** | **`+5.14% LUTs`** / **`+1.47% FFs`** | Chỉ tăng +43 LUTs và +16 FFs trên toàn bộ SoC Zynq-7000 (879 LUTs, 1,101 FFs). |
| **Tần số & Công suất hoạt động** | **`124 mW`** @ **`108.21 MHz`** | Vượt mốc chuẩn 100 MHz trên chip FPGA AMD Xilinx Zynq-7000 ($WNS = +0.759$ ns). |
| **Hiệu quả diện tích (Pareto Metric)** | **`19.16 pts / % area`** | Hiệu quả diện tích gấp **$42.6\\times$** so với giải pháp tam trùng không gian truyền thống (TMR). |"""

    text = text[:idx1] + new_highlights + text[idx2:]

    # 2. Section 7 PPA Table
    p_start = "| Nhóm Chỉ số PPA | Baseline MAC (`baseline_mac.v`)"
    p_end = "| **Biến thiên Jitter Thời gian** | **0 ns** | **0 ns** | **Kháng Timing Attacks (Constant 3 CK)** | **Bất biến 3 CK** |"

    idx3 = text.find(p_start)
    idx4 = text.find(p_end) + len(p_end)

    new_ppa_table = """| Nhóm Chỉ số PPA | Baseline MAC (`baseline_mac.v`) | Secure MAC (`secure_mac.v`) | Chênh lệch / Chi phí (Overhead) | Toàn bộ SoC Top (`top_module.v`) |
| :--- | :---: | :---: | :---: | :---: |
| **Slice LUTs** | **99 LUTs** | **205 LUTs** | **+43 LUTs (+5.14% trên toàn SoC)** | **879 LUTs (1.65% chip)** |
| **Slice Registers (FFs)** | **131 FFs** | **178 FFs** | **+16 FFs (+1.47% trên toàn SoC)** | **1,101 FFs (1.03% chip)** |
| **CARRY4 Primitives** | **20 CARRY4** | **26 CARRY4** | **+6 CARRY4 (+30.00%)** | **57 CARRY4** |
| **Khối DSP Multiplier** | **0 DSP** | **0 DSP** | **Thuần LUT logic, khả chuyển 100% mọi FPGA/ASIC** | **0 DSP** |
| **Tần số cực đại ($F_{max}$)** | **176.50 MHz** | **175.38 MHz** | **Đạt 175.38 MHz (Vượt chuẩn 100 MHz)** | **108.21 MHz** |
| **Worst Negative Slack (WNS)**| **+4.335 ns** | **+4.298 ns** | **Đạt chuẩn Timing Closure 100 MHz** | **+0.759 ns** |
| **Công suất Động (Dynamic)** | **5 mW** | **11 mW** | **+5 mW (Mạch kiểm tra thặng dư số học)** | **18 mW** |
| **Tổng Công suất On-Chip** | **108 mW** | **114 mW** | **+8 mW (+6.90% trên toàn SoC)** | **124 mW** |
| **Biến thiên Jitter Thời gian** | **0 ns** | **0 ns** | **Kháng Timing Attacks (Constant 3 CK)** | **Bất biến 3 CK** |"""

    text = text[:idx3] + new_ppa_table + text[idx4:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    print("Updated README.md successfully via slice replacement!")

if __name__ == "__main__":
    update_readme_exact()
