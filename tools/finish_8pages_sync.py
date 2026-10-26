import re

def finish_sync():
    path = "paper/main_8pages.tex"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Section IV-A text
    old_p = r"""Mạch Secure MAC đề xuất chỉ tiêu tốn thêm $+36$ LUTs ($+36.4\%$ trên khối MAC, chỉ $+4.19\%$ trên toàn SoC) và $+3$ FFs ($+0.56\%$ SoC), không cần thêm DSP48. Tần số đạt $125.2$~MHz với WNS $+2.013$~ns ở chu kỳ $10$~ns, thỏa mãn vượt trội yêu cầu vận hành danh định $100$~MHz. Công suất toàn SoC chỉ tăng khiêm tốn $+3.4$~mW ($+5.55\%$ động)."""
    new_p = r"""Mạch Secure MAC độc lập tiêu tốn $205$ LUTs, $178$ FFs và đạt tần số $F_{max} = 175.38$~MHz. Khi tích hợp vào vi xử lý SoC RV32I, Secure MAC chỉ phát sinh thêm $+43$ LUTs ($+5.14\%$ trên toàn SoC) và $+16$ FFs ($+1.47\%$ SoC), không sử dụng DSP48. Toàn bộ hệ thống SoC đạt tần số $108.21$~MHz ($WNS = +0.759$~ns ở chu kỳ $10$~ns), hoàn toàn đóng gói định thời an toàn. Công suất toàn SoC chỉ tăng khiêm tốn $+5$~mW động ($+6.90\%$ tổng công suất chip, đạt $124$~mW)."""
    assert old_p in text, "old_p not found"
    text = text.replace(old_p, new_p)

    # Pareto text in Sec IV-C
    old_par = r"""\textbf{$21.18$ điểm/\% diện tích} (gấp \textbf{$47\times$ so với TMR})."""
    new_par = r"""\textbf{$19.16$ điểm/\% diện tích} (gấp \textbf{$42.6\times$ so với TMR})."""
    assert old_par in text, "old_par not found"
    text = text.replace(old_par, new_par)

    # Contribution 4
    old_c4 = r"""đạt hiệu quả diện tích gấp $47\times$ so với TMR."""
    new_c4 = r"""đạt hiệu quả diện tích gấp $42.6\times$ so với TMR."""
    if old_c4 in text:
        text = text.replace(old_c4, new_c4)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    print("Updated 8-page text and Pareto metrics successfully!")

if __name__ == "__main__":
    finish_sync()
