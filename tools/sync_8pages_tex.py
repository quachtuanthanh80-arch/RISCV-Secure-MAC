import re
import sys

def sync_8pages_tex():
    tex_path = "paper/main_8pages.tex"
    with open(tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Add Vietnamese citations to Section I
    t1 = r"""toán tử Nhân--Tích lũy (MAC) chiếm hơn $90\%$ tổng khối lượng tính toán số học~\cite{sze2017efficient}. Tuy nhiên, khi công nghệ bán dẫn tiến sâu"""
    r1 = r"""toán tử Nhân--Tích lũy (MAC) chiếm hơn $90\%$ tổng khối lượng tính toán số học~\cite{sze2017efficient}. Tại Việt Nam, các hướng tiếp cận tối ưu hóa toán tử MAC cho thiết bị biên như kỹ thuật XNOR-popcount của Phạm Văn Khoa và cộng sự~\cite{pham2025xnor} hay tăng tốc xử lý dữ liệu thực nghiệm trên kit FPGA Xilinx Zynq-7000~\cite{pham2025image} đã chứng minh tiềm năng vượt bậc của việc cải tiến vi kiến trúc số học nhằm tiết giảm công suất và diện tích. Tuy nhiên, khi công nghệ bán dẫn tiến sâu"""
    if t1 in text:
        text = text.replace(t1, r1)
        print("[main_8pages.tex] Added Vietnamese citations to Section I")

    # 2. Add Vietnamese citations to Section II
    t2 = r"""kiến trúc của chúng tôi bảo vệ trực tiếp datapath MAC với phụ trội chỉ $+4.19\%$ trên toàn SoC và khôi phục tức thời trong 1 chu kỳ."""
    r2 = r"""kiến trúc của chúng tôi bảo vệ trực tiếp datapath MAC với phụ trội chỉ $+5.14\%$ trên toàn SoC và khôi phục tức thời trong 1 chu kỳ. Bên cạnh đó, các nghiên cứu tại Việt Nam như bộ tăng tốc AES-RV trên vi xử lý RISC-V của Trần Xuân Tú và cộng sự~\cite{tran2025aes} cùng kiến trúc mạng NoC dung lỗi của Đặng Nam Khánh và cộng sự~\cite{dang2017low, dang2020soft} đã khẳng định xu thế thiết kế vi kiến trúc an toàn cho chip tích hợp."""
    if t2 in text:
        text = text.replace(t2, r2)
        print("[main_8pages.tex] Added Vietnamese citations to Section II")

    # 3. Update Contribution 1
    c1_old = r"""đạt $125.2$~MHz trên FPGA Zynq-7000 mà không gây bọt pipeline cho CPU."""
    c1_new = r"""đạt $108.2$~MHz trên FPGA Zynq-7000 mà không gây bọt pipeline cho CPU."""
    if c1_old in text:
        text = text.replace(c1_old, c1_new)
        print("[main_8pages.tex] Updated Contribution 1 frequency")

    # 4. Update Table 1 Taxonomy row
    tax_old = r"""\textbf{Modulo-3 CED (Bài báo này)} & \textbf{2026} & \textbf{Thặng dư Số học} & \textbf{$+36.4\%$ MAC ($+4.19\%$ SoC)} & \textbf{$+4.58\%$ MAC ($+0.56\%$ SoC)} & \textbf{$+5.55\%$} & \textbf{$100.00\%$} & \textbf{$1$ chu kỳ} & \textbf{Datapath MAC + Shadow Accumulator} \\"""
    tax_new = r"""\textbf{Modulo-3 CED (Bài báo này)} & \textbf{2026} & \textbf{Thặng dư Số học} & \textbf{$+5.14\%$ SoC ($+43$ LUTs)} & \textbf{$+1.47\%$ SoC ($+16$ FFs)} & \textbf{$+6.90\%$} & \textbf{$100.00\%$} & \textbf{$1$ chu kỳ} & \textbf{Datapath MAC + Shadow Accumulator} \\"""
    if tax_old in text:
        text = text.replace(tax_old, tax_new)
        print("[main_8pages.tex] Updated Table 1 taxonomy row")

    # 5. Update Table 2 PPA Table
    tab_old = r"""Baseline MAC (Không bảo vệ) & $99$ ($0.19\%$) & $65$ ($0.06\%$) & $1$ ($0.45\%$) & $+2.540$~ns & $134.0$~MHz & $18.2$~mW & $138.2$~mW & Không có (Dễ tổn thương SDC) \\
TMR MAC (Tam trùng Dư thừa) & $337$ ($0.63\%$) & $211$ ($0.20\%$) & $3$ ($1.36\%$) & $+1.420$~ns & $116.5$~MHz & $58.4$~mW & $178.4$~mW & $0$ chu kỳ (Biểu quyết phần cứng đa số) \\
DMR MAC (Song trùng Dư thừa) & $215$ ($0.40\%$) & $138$ ($0.13\%$) & $2$ ($0.91\%$) & $+1.890$~ns & $123.3$~MHz & $37.6$~mW & $157.6$~mW & Ngắt phần mềm ($50$--$120$ chu kỳ) \\
Parity CED MAC & $112$ ($0.21\%$) & $68$ ($0.06\%$) & $1$ ($0.45\%$) & $+2.310$~ns & $130.0$~MHz & $19.5$~mW & $139.5$~mW & Không có (Thất bại trên số học MAC) \\
Residue Modulo-7 MAC & $172$ ($0.32\%$) & $78$ ($0.07\%$) & $1$ ($0.45\%$) & $+1.650$~ns & $119.8$~MHz & $26.8$~mW & $146.8$~mW & $1$ chu kỳ (Kênh residue 3-bit) \\
\textbf{Secure MAC (Đề xuất)} & \textbf{135 ($0.25\%$)} & \textbf{68 ($0.06\%$)} & \textbf{1 ($0.45\%$)} & \textbf{+2.013~ns} & \textbf{125.2~MHz} & \textbf{22.4~mW} & \textbf{142.4~mW} & \textbf{1 chu kỳ (Shadow Accumulator)} \\
\midrule
Baseline SoC RV32I & $824$ ($1.55\%$) & $534$ ($0.50\%$) & $1$ ($0.45\%$) & $+2.350$~ns & $130.7$~MHz & $62.5$~mW & $182.5$~mW & Baseline không bảo vệ \\
\textbf{Secure SoC RV32I (Đề xuất)} & \textbf{860 ($1.62\%$)} & \textbf{537 ($0.51\%$)} & \textbf{1 ($0.45\%$)} & \textbf{+2.013~ns} & \textbf{125.2~MHz} & \textbf{65.9~mW} & \textbf{185.9~mW} & \textbf{1 chu kỳ Rollback + Ngắt CPU} \\
$\Delta$ Phụ trội Toàn SoC & \textbf{+36 LUTs (+4.19\%)} & \textbf{+3 FFs (+0.56\%)} & \textbf{0 (0.00\%)} & \textbf{--0.337~ns} & \textbf{--5.5~MHz} & \textbf{+3.4~mW (+5.55\%)} & \textbf{+3.4~mW (+1.86\%)} & \textbf{Bảo toàn 100\% thông lượng} \\"""

    tab_new = r"""Conventional Baseline & $99$ ($0.19\%$) & $131$ ($0.12\%$) & $0$ (Logic) & $+4.335$~ns & $176.5$~MHz & $5.0$~mW & $108.0$~mW & Không bảo vệ (SDC) \\
Approximate MAC (LSB Trunc) & $95$ ($0.18\%$) & $128$ ($0.12\%$) & $0$ (Logic) & $+4.428$~ns & $179.5$~MHz & $5.0$~mW & $108.0$~mW & Sai số xấp xỉ (Inexact) \\
Time Redundancy (RESO) & $166$ ($0.31\%$) & $200$ ($0.19\%$) & $0$ (Logic) & $+1.413$~ns & $116.5$~MHz & $9.0$~mW & $112.0$~mW & Tính lại (Giảm $50\%$ thông lượng) \\
Dual Modular Redundancy (DMR) & $98$ ($0.18\%$) & $164$ ($0.15\%$) & $0$ (Logic) & $+4.358$~ns & $177.2$~MHz & $7.0$~mW & $109.0$~mW & Khóa bước (Lockstep Flag) \\
\textbf{Secure MAC (Độc lập -- Standalone)} & \textbf{205 ($0.39\%$)} & \textbf{178 ($0.17\%$)} & \textbf{0 (Logic)} & $\mathbf{+4.298}$~\textbf{ns} & \textbf{175.4~MHz} & \textbf{11~mW} & \textbf{114~mW} & \textbf{Rollback 1 CK + Mod3-16b} \\
\textbf{Secure MAC (Trong SoC -- Sub-block)} & \textbf{142 ($0.27\%$)} & \textbf{115 ($0.11\%$)} & \textbf{0 (Logic)} & $\mathbf{+0.759}$~\textbf{ns} & \textbf{108.2~MHz} & \textbf{---} & \textbf{---} & \textbf{Rollback 1 CK + Vector IRQ} \\
\midrule
\textbf{Toàn Bộ SoC RV32I (Baseline)} & $836$ ($1.57\%$) & $1,085$ ($1.02\%$) & $0$ (Logic) & $+0.759$~ns & $108.2$~MHz & $13~mW$ & $116~mW$ & Bẫy ngắt CPU \\
\textbf{Toàn Bộ SoC RV32I + Secure MAC} & \textbf{879 ($1.65\%$)} & \textbf{1,101 ($1.03\%$)} & \textbf{0 (Logic)} & $\mathbf{+0.759}$~\textbf{ns} & \textbf{108.2~MHz} & \textbf{18~mW} & \textbf{124~mW} & \textbf{Hardware Rollback + IRQ} \\
\textbf{Mức Độ Phụ Trội Toàn SoC} & \textbf{+43 LUTs (+5.14\%)} & \textbf{+16 FFs (+1.47\%)} & \textbf{0 DSP} & \textbf{Đạt Timing (WNS $>0$)} & \textbf{Vượt 100~MHz} & \textbf{+5~mW} & \textbf{+6.90\%} & \textbf{Cơ sở đánh giá ASIL-D} \\"""

    if tab_old in text:
        text = text.replace(tab_old, tab_new)
        print("[main_8pages.tex] Updated Table 2 PPA rows")

    # 6. Update Section IV-A text
    sec_old = r"""So với mạch Baseline không bảo vệ, Secure MAC chỉ phát sinh thêm $+36$ LUTs ($+4.19\%$ trên toàn SoC) và $+3$ FFs ($+0.56\%$). Tần số hoạt động cực đại $F_{max}$ đạt $125.2$~MHz ($WNS = +2.013$~ns ở $100$~MHz). Khi tích hợp vào toàn bộ SoC RV32I, hệ thống duy trì $WNS = +1.289$~ns ($F_{max} = 116.8$~MHz), vượt xa yêu cầu $100$~MHz và đóng gói định thời an toàn."""
    sec_new = r"""So với mạch SoC Baseline không bảo vệ ($836$ LUTs, $1,085$ FFs, $116$~mW), việc tích hợp hoàn chỉnh khối Secure MAC chỉ phát sinh thêm $+43$ Slice LUTs ($+5.14\%$ trên toàn SoC) và $+16$ Flip-Flops ($+1.47\%$). Khối Secure MAC độc lập đạt $F_{max} = 175.38$~MHz ($WNS = +4.298$~ns ở $100$~MHz). Khi tích hợp vào toàn bộ vi xử lý SoC RV32I, hệ thống duy trì $WNS = +0.759$~ns tại xung nhịp danh định $100$~MHz ($F_{max} = 108.21$~MHz), hoàn toàn đóng gói định thời an toàn. Công suất động tăng thêm $5$~mW, đưa mức tăng tổng công suất chip lên $+6.90\%$ ($124$~mW)."""

    if sec_old in text:
        text = text.replace(sec_old, sec_new)
        print("[main_8pages.tex] Updated Section IV-A text")

    # 7. Update Pareto text
    par_old = r"""mang lại hiệu suất \textbf{$21.18$ điểm/\% diện tích} (gấp $47\times$ so với TMR)."""
    par_new = r"""mang lại hiệu suất \textbf{$19.16$ điểm/\% diện tích} (gấp $42.6\times$ so với TMR)."""
    if par_old in text:
        text = text.replace(par_old, par_new)
        print("[main_8pages.tex] Updated Pareto text")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("[main_8pages.tex] Finished synchronizing main_8pages.tex!")

if __name__ == "__main__":
    sync_8pages_tex()
