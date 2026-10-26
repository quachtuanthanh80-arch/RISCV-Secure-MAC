import re
import sys

def sync_main_tex():
    tex_path = "paper/main.tex"
    with open(tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Add Vietnamese citations to Section I
    t1 = r"""quyết định thông lượng xử lý của toàn hệ thống~\cite{sze2017efficient}. Tuy nhiên, khi công nghệ chế tạo bán dẫn"""
    r1 = r"""quyết định thông lượng xử lý của toàn hệ thống~\cite{sze2017efficient}. Tại Việt Nam, các hướng tiếp cận tối ưu hóa phần cứng cho khối toán tử MAC trên thiết bị biên như kỹ thuật XNOR-popcount của Phạm Văn Khoa và cộng sự~\cite{pham2025xnor} hay giải pháp tăng tốc xử lý dữ liệu thực nghiệm trên kit FPGA Xilinx Zynq-7000~\cite{pham2025image} đã chứng minh tiềm năng vượt trội của việc cải tiến vi kiến trúc số học nhằm tiết giảm công suất và diện tích. Tuy nhiên, khi công nghệ chế tạo bán dẫn"""
    if t1 in text:
        text = text.replace(t1, r1)
        print("[main.tex] Added Vietnamese citations to Section I")

    # 2. Add Vietnamese citations to Section II
    t2 = r"""khôi phục tức thời trong đúng 1 chu kỳ bằng Shadow Accumulator."""
    r2 = r"""khôi phục tức thời trong đúng 1 chu kỳ bằng Shadow Accumulator.

Bên cạnh các nghiên cứu quốc tế, tại Việt Nam, các hướng tiếp cận tích hợp bộ tăng tốc chuyên dụng cho vi xử lý RISC-V cũng như cơ chế dung lỗi hệ thống đã được đẩy mạnh nghiên cứu: nhóm tác giả của Trần Xuân Tú và cộng sự (VNU-UET) đã đề xuất kiến trúc bộ tăng tốc phần cứng AES-RV tích hợp trực tiếp vào đường truyền vi xử lý RISC-V qua mở rộng tập lệnh với độ trễ cực thấp phục vụ an toàn IoT~\cite{tran2025aes}; đồng thời các nghiên cứu nền tảng của Đặng Nam Khánh và cộng sự~\cite{dang2017low, dang2020soft} đã phát triển các mô hình dung hòa lỗi mềm và lỗi cứng với chi phí phụ trội thấp trên hệ thống mạng kết nối trên chip (NoC). Kế thừa tinh thần tối ưu hóa phần cứng và định hướng thiết kế an toàn nói trên, công trình này tập trung giải quyết bài toán dung lỗi mềm tức thời ngay tại trung tâm tính toán MAC của vi xử lý RISC-V."""
    if t2 in text:
        text = text.replace(t2, r2)
        print("[main.tex] Added Vietnamese citations to Section II")

    # 3. Update Table 1 (Taxonomy)
    tax_old = r"""\textbf{Modulo-3 CED (Bài báo này)} & \textbf{2026} & \textbf{Thặng dư Số học} & \textbf{$+36.4\%$ MAC ($+4.19\%$ SoC)} & \textbf{$+4.58\%$ MAC ($+0.56\%$ SoC)} & \textbf{$+5.55\%$} & \textbf{$100.00\%$} & \textbf{$1$ chu kỳ} & \textbf{Datapath MAC + Shadow Accumulator} \\"""
    tax_new = r"""\textbf{Modulo-3 CED (Bài báo này)} & \textbf{2026} & \textbf{Thặng dư Số học} & \textbf{$+5.14\%$ SoC ($+43$ LUTs)} & \textbf{$+1.47\%$ SoC ($+16$ FFs)} & \textbf{$+6.90\%$} & \textbf{$100.00\%$} & \textbf{$1$ chu kỳ} & \textbf{Datapath MAC + Shadow Accumulator} \\"""
    if tax_old in text:
        text = text.replace(tax_old, tax_new)
        print("[main.tex] Updated Table 1 taxonomy row")

    # 4. Update Table 3 (PPA Table)
    tab3_old = r"""\textbf{Secure MAC (Đề xuất cốt lõi)} & \textbf{135} & \textbf{137} & \textbf{0 (Logic)} & $\mathbf{+2.013}$~\textbf{ns} & \textbf{125.2~MHz} & \textbf{14~mW} & \textbf{117~mW} & \textbf{Rollback 1 chu kỳ (100\% SEU)} \\
\textbf{Secure MAC + EWMA (Đề xuất đầy đủ)} & \textbf{167} & \textbf{202} & \textbf{0 (Logic)} & $\mathbf{+1.658}$~\textbf{ns} & \textbf{119.9~MHz} & \textbf{14.8~mW} & \textbf{118~mW} & \textbf{Rollback 1 CK + EWMA (98.49\% MBU)} \\
\midrule
\textbf{Toàn Bộ SoC RV32I (Baseline)} & 824 & 1,068 & 0 (Logic) & $+1.289$~ns & 116.8~MHz & 13~mW & 116~mW & Bẫy ngắt CPU \\
\textbf{Toàn Bộ SoC RV32I + Secure MAC} & \textbf{860} & \textbf{1,074} & \textbf{0 (Logic)} & $\mathbf{+1.289}$~\textbf{ns} & \textbf{116.8~MHz} & \textbf{19~mW} & \textbf{122~mW} & \textbf{Hardware Rollback + IRQ} \\
\textbf{Mức Độ Phụ Trội Toàn SoC} & \textbf{+36 LUTs (+4.19\%)} & \textbf{+6 FFs (+0.56\%)} & \textbf{0 DSP} & \textbf{Đạt Timing} & \textbf{Vượt 100~MHz} & \textbf{+6~mW} & \textbf{+5.55\%} & \textbf{Cơ sở đánh giá mô phỏng cho ASIL-D} \\"""

    tab3_new = r"""\textbf{Secure MAC (Độc lập -- Standalone)} & \textbf{205} & \textbf{178} & \textbf{0 (Logic)} & $\mathbf{+4.298}$~\textbf{ns} & \textbf{175.4~MHz} & \textbf{11~mW} & \textbf{114~mW} & \textbf{Rollback 1 CK + Mod3-16b (100\% SEU)} \\
\textbf{Secure MAC (Trong SoC -- Sub-block)} & \textbf{142} & \textbf{115} & \textbf{0 (Logic)} & $\mathbf{+0.759}$~\textbf{ns} & \textbf{108.2~MHz} & \textbf{---} & \textbf{---} & \textbf{Rollback 1 CK + Vector IRQ} \\
\midrule
\textbf{Toàn Bộ SoC RV32I (Baseline)} & 836 & 1,085 & 0 (Logic) & $+0.759$~ns & 108.2~MHz & 13~mW & 116~mW & Bẫy ngắt CPU \\
\textbf{Toàn Bộ SoC RV32I + Secure MAC} & \textbf{879} & \textbf{1,101} & \textbf{0 (Logic)} & $\mathbf{+0.759}$~\textbf{ns} & \textbf{108.2~MHz} & \textbf{18~mW} & \textbf{124~mW} & \textbf{Hardware Rollback + IRQ} \\
\textbf{Mức Độ Phụ Trội Toàn SoC} & \textbf{+43 LUTs (+5.14\%)} & \textbf{+16 FFs (+1.47\%)} & \textbf{0 DSP} & \textbf{Đạt Timing (WNS $>0$)} & \textbf{Vượt 100~MHz} & \textbf{+5~mW} & \textbf{+6.90\%} & \textbf{Cơ sở đánh giá mô phỏng cho ASIL-D} \\"""

    if tab3_old in text:
        text = text.replace(tab3_old, tab3_new)
        print("[main.tex] Updated Table 3 PPA rows")

    # 5. Update Section IV-A text
    sec_old = r"""So với mạch Baseline không bảo vệ, khối Secure MAC cốt lõi chỉ phát sinh thêm $+36$ LUTs ($+36.4\%$ trên bản thân MAC, nhưng chỉ $+4.19\%$ trên toàn bộ diện tích SoC) và $+6$ Flip-Flops ($+0.56\%$ trên SoC). Tần số hoạt động cực đại $F_{max}$ đạt $125.2$~MHz, với Worst Negative Slack đạt $WNS = T_{clk} - T_{crit} = 10 - (1000/125.2) = +2.013$~ns ở tần số hệ thống $100$~MHz. Cấu hình hoàn chỉnh tích hợp bộ theo dõi EWMA đạt $F_{max} = 119.9$~MHz ($WNS = +1.658$~ns). Khi tích hợp vào toàn bộ vi xử lý SoC RV32I, đường trễ tới hạn nằm tại khối thực thi ALU của CPU chứ không nằm trên bộ tăng tốc Secure MAC, duy trì $WNS = +1.289$~ns ($F_{max} = 116.8$~MHz), hoàn toàn vượt mức yêu cầu $100$~MHz của hệ thống và đóng gói định thời an toàn. Về mặt công suất, việc tích hợp mạch CED số học làm tăng công suất động của SoC thêm $6$~mW, đưa mức tăng tổng công suất chip lên $+5.55\%$, hoàn toàn nằm trong biên độ cho phép của các hệ thống pin nhúng."""
    
    sec_new = r"""So với mạch SoC Baseline không bảo vệ (tiêu tốn $836$ LUTs, $1,085$ Flip-Flops và $116$~mW), việc tích hợp hoàn chỉnh khối Secure MAC vào hệ thống chỉ phát sinh thêm $+43$ Slice LUTs ($+5.14\%$ trên toàn bộ diện tích SoC) và $+16$ Flip-Flops ($+1.47\%$ trên SoC). Khi tổng hợp và triển khai độc lập (out-of-context ở tần số $200$~MHz), bản thân khối Secure MAC tiêu tốn $205$ LUTs, $178$ FFs và đạt tần số vận hành tối đa $F_{max} = 175.38$~MHz ($WNS = +4.298$~ns ở mốc $100$~MHz). Khi đặt trong cấu trúc phân cấp toàn SoC, bộ tối ưu hóa logic của Vivado đã chia sẻ tài nguyên ghép kênh hiệu quả, giúp phần diện tích thực tế của Secure MAC chỉ chiếm $142$ LUTs và $115$ FFs. Toàn bộ vi xử lý SoC RV32I tích hợp Secure MAC duy trì $WNS = +0.759$~ns tại xung nhịp danh định $100$~MHz ($T_{clk} = 10.0$~ns), đạt tần số vận hành tới hạn $F_{max} = 108.21$~MHz, đáp ứng tuyệt đối yêu cầu đóng gói định thời an toàn. Về mặt năng lượng, công suất động tăng thêm $5$~mW, đưa mức tăng tổng công suất chip lên $+6.90\%$ (tổng $124$~mW), hoàn toàn khả thi trên các thiết bị biên nhúng."""

    if sec_old in text:
        text = text.replace(sec_old, sec_new)
        print("[main.tex] Updated Section IV-A text")

    # 6. Update Pareto text
    par_old = r"""mang lại hiệu suất \textbf{$21.18$ điểm/\% diện tích} (hiệu quả gấp $47\times$ so với TMR)."""
    par_new = r"""mang lại hiệu suất \textbf{$19.16$ điểm/\% diện tích} (hiệu quả gấp $42.6\times$ so với TMR)."""
    if par_old in text:
        text = text.replace(par_old, par_new)
        print("[main.tex] Updated Pareto text")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("[main.tex] Finished synchronizing main.tex!")

if __name__ == "__main__":
    sync_main_tex()
