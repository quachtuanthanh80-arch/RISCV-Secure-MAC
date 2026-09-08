# Experimental Reports & Fault Injection Datasets

Thư mục chứa toàn bộ dữ liệu thực nghiệm, báo cáo phân tích độ phủ lỗi (Fault Coverage) và ma trận tương quan cho bài báo khoa học.

## Danh mục File Báo cáo & Dữ liệu
| Tên File | Loại | Mô tả |
| :--- | :--- | :--- |
| [`master_verification_report.md`](file:///d:/NCKH/reports/master_verification_report.md) | Markdown | **Báo cáo tổng kiểm chứng chất lượng phần cứng (Master Verification Report)**: Tổng hợp 10 Test Suites (100% PASS), mô hình Functional Coverage (Residue & ALU), SystemVerilog Assertions (SVA) và CI/CD. |
| [`exhaustive_fault_injection_report.md`](file:///d:/NCKH/reports/exhaustive_fault_injection_report.md) | Markdown | **Báo cáo tổng kết 81,000 thử nghiệm tiêm lỗi**: Phân tích Single-Bit (100%), Double-Bit (49.3%), Stuck-At (100%), Multi-Bit Bursts (68.7%), định lý chẵn lẻ Bit-Pair Parity Theorem. |
| [`data/double_bit_heatmap_32b.csv`](file:///d:/NCKH/reports/data/double_bit_heatmap_32b.csv) | CSV | **Ma trận 2D $32 \times 32$**: Tỷ lệ phát hiện lỗi cho tất cả $\binom{32}{2} = 496$ cặp bit trong thanh ghi Accumulator `pipe_c`. Dùng để vẽ Heatmap biểu đồ bài báo. |
| [`data/double_bit_heatmap_16b.csv`](file:///d:/NCKH/reports/data/double_bit_heatmap_16b.csv) | CSV | **Ma trận 2D $16 \times 16$**: Tỷ lệ phát hiện lỗi cho tất cả $\binom{16}{2} = 120$ cặp bit trong thanh ghi Multiplier `pipe_product`. |
| [`data/stuck_at_coverage.csv`](file:///d:/NCKH/reports/data/stuck_at_coverage.csv) | CSV | Bảng chi tiết kết quả kiểm thử mô hình lỗi Stuck-At-0 (SA0) và Stuck-At-1 (SA1) theo từng bit vị trí. |
| [`data/fault_injection_coverage.csv`](file:///d:/NCKH/reports/data/fault_injection_coverage.csv) | CSV | Dataset phân tích lỗi đơn theo vị trí bit từ $0$ đến $31$. |
| [`data/fault_injection_results.json`](file:///d:/NCKH/reports/data/fault_injection_results.json) | JSON | Dữ liệu thô định dạng JSON xuất trực tiếp từ Cocotb runner. |

---

## 🖼️ Danh mục Đồ thị Khoa học (300+ DPI Figures for IEEE Paper)

Trong thư mục [`reports/figures/`](file:///d:/NCKH/reports/figures):
1. **[`fig3_1_fpga_ppa_implementation.png`](file:///d:/NCKH/reports/figures/fig3_1_fpga_ppa_implementation.png)**: Bảng và đồ thị 4 panel PPA phần cứng sau tổng hợp và thực thi trên FPGA Xilinx Zynq-7000 (Tài nguyên, Slack @ 100MHz, $F_{max}$, Công suất).
2. **[`fig3_2_single_bit_fdr.png`](file:///d:/NCKH/reports/figures/fig3_2_single_bit_fdr.png)**: Biểu đồ cột độ phủ lỗi đơn (FDR = 100.00% trên cả 32 bit) và độ chính xác State Rollback (100.00%).
3. **[`fig3_3_bit_distance_parity_spectrum.png`](file:///d:/NCKH/reports/figures/fig3_3_bit_distance_parity_spectrum.png)**: Phổ phát hiện lỗi 2-bit theo khoảng cách bit (Bit-Distance Parity Spectrum) — Khẳng định tính đối xứng $d$ chẵn = 100% FDR, $d$ lẻ = 0% FDR.
4. **[`fig3_4_fault_classification_breakdown.png`](file:///d:/NCKH/reports/figures/fig3_4_fault_classification_breakdown.png)**: Biểu đồ Donut phân bổ 496 cặp lỗi 2-bit và độ bao phủ lỗi FDR/Rollback 100% trên 5 khối con Secure MAC.
5. **[`fig3_5_multibit_burst_scaling.png`](file:///d:/NCKH/reports/figures/fig3_5_multibit_burst_scaling.png)**: Biểu đồ đường phân tích lỗi cụm đa bit ($k = 1..6$ bit) tiệm cận ngưỡng lý thuyết $2/3 \approx 66.67\%$.


---

## Cách tái tạo dữ liệu (How to Reproduce)

1. **Chạy bộ thử nghiệm Exhaustive Suite (81,000 ca, ~2 giây)**:
   ```bash
   python tools/exhaustive_fault_injection.py
   ```
2. **Chạy bộ mô phỏng RTL Cocotb (4,400 ca, ~7 giây)**:
   ```bash
   python tb/cocotb/secure_mac/run_fault_campaign.py
   ```
