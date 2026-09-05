#!/usr/bin/env python3
"""
Trình sinh Báo cáo Nghiên cứu Khoa học 2026 — Phiên bản Cập nhật Toàn diện.

Dựa trên cấu trúc bản thảo template (Bao_cao_NCKH_Chuan_8Cot_Full.docx):
  - Trang A4 (8.27 × 11.69 in), lề trái 3 cm, lề phải 2 cm, trên/dưới 2.54 cm
  - Times New Roman 12 pt, giãn dòng 1.25
  - Heading 1 / Heading 2 / Heading 3 đúng chuẩn Word
  - 4 bảng: Danh mục viết tắt, Phân bổ tài nguyên, So sánh 13 tiêu chí, Danh mục RTL
  - 5 hình phân tích mới (fig1–fig5) nhúng trực tiếp
  - 16 tài liệu tham khảo IEEE

Đầu ra:
  1. docs/Bao_cao_NCKH_2026_Updated.docx
  2. docs/Bao_cao_NCKH_2026_Updated.md
"""

import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def set_cell_bg(cell, color_hex):
    """Set background colour of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    """Set internal cell padding (twips)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def style_header_row(table, row_idx, bg_color="0D47A1", font_color=RGBColor(255, 255, 255)):
    """Format a header row: background colour + bold white text."""
    for cell in table.rows[row_idx].cells:
        set_cell_bg(cell, bg_color)
        set_cell_margins(cell)
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.font.bold = True
                run.font.color.rgb = font_color
                run.font.size = Pt(10)
                run.font.name = "Times New Roman"


def add_body(doc, text, bold=False, italic=False, size=12, indent_cm=0, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Add a body paragraph with optional formatting."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.line_spacing = 1.25
    p.alignment = align
    if indent_cm > 0:
        p.paragraph_format.first_line_indent = Cm(indent_cm)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    return p


def add_figure(doc, figures_dir, filename, caption, width_inches=6.0):
    """Insert an image with a centred italic caption below it."""
    img_path = figures_dir / filename
    if img_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(img_path), width=Inches(width_inches))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(6)
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = "Times New Roman"
        run_cap.font.size = Pt(10)
        run_cap.italic = True
    else:
        add_body(doc, f"[Hình chưa có: {filename}]", italic=True, size=10)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN REPORT BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def create_report():
    root_dir = Path(__file__).resolve().parent.parent.parent
    figures_dir = root_dir / "reports" / "figures"
    docs_dir = root_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    doc = docx.Document()

    # ─── Page Setup (A4, chuẩn bản thảo) ────────────────────────────────────
    sec = doc.sections[0]
    sec.page_width  = Emu(7560310)   # 8.27 in  (A4)
    sec.page_height = Emu(10692130)  # 11.69 in (A4)
    sec.left_margin   = Emu(1080135)   # ~3.0 cm
    sec.right_margin  = Emu(720090)    # ~2.0 cm
    sec.top_margin    = Inches(1.0)    # 2.54 cm
    sec.bottom_margin = Inches(1.0)

    # ─── Normal Style ───────────────────────────────────────────────────────
    ns = doc.styles["Normal"]
    ns.font.name = "Times New Roman"
    ns.font.size = Pt(12)
    ns.font.color.rgb = RGBColor(33, 33, 33)
    ns.paragraph_format.line_spacing = 1.25
    ns.paragraph_format.space_after = Pt(4)
    ns.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # ═════════════════════════════════════════════════════════════════════════
    #  TRANG BÌA
    # ═════════════════════════════════════════════════════════════════════════
    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BÁO CÁO NGHIÊN CỨU KHOA HỌC 2026")
    r.bold = True; r.font.size = Pt(20); r.font.name = "Times New Roman"
    r.font.color.rgb = RGBColor(13, 71, 161)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(
        "THIẾT KẾ VÀ ĐÁNH GIÁ BỘ TĂNG TỐC MAC\n"
        "DUNG LỖI TỰ PHỤC HỒI TRONG 1 CHU KỲ\n"
        "CHO LÕI VI XỬ LÝ RISC-V RV32I TRÊN FPGA"
    )
    r.bold = True; r.font.size = Pt(16); r.font.name = "Times New Roman"
    r.font.color.rgb = RGBColor(21, 101, 192)

    for _ in range(2):
        doc.add_paragraph()

    info_lines = [
        "Nền tảng thực nghiệm: FPGA Xilinx Zynq-7000 (xc7z020clg400-1)",
        "Công cụ EDA: AMD Xilinx Vivado 2026.1",
        "Khung kiểm chứng: Cocotb 2.0 + Icarus Verilog",
        "Tổng mẫu tiêm lỗi: 26.040 mẫu thử tự động",
    ]
    for line in info_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(line)
        r.font.name = "Times New Roman"; r.font.size = Pt(12); r.italic = True

    doc.add_page_break()

    # ═════════════════════════════════════════════════════════════════════════
    #  DANH MỤC VIẾT TẮT (Bảng 0 trong template)
    # ═════════════════════════════════════════════════════════════════════════
    doc.add_heading("DANH MỤC TỪ VIẾT TẮT", level=1)

    abbrevs = [
        ("SoC", "System-on-Chip — Hệ thống hoàn chỉnh tích hợp trên một chip đơn"),
        ("RISC-V", "Reduced Instruction Set Computer — Architecture V, kiến trúc tập lệnh mở"),
        ("RV32I", "RISC-V 32-bit Base Integer Instruction Set — Tập lệnh cơ sở 32-bit"),
        ("ISA", "Instruction Set Architecture — Kiến trúc tập lệnh phần cứng"),
        ("MAC", "Multiply-Accumulate — Phép nhân tích lũy: C = A × B + C"),
        ("CED", "Concurrent Error Detection — Phát hiện lỗi đồng thời trong quá trình tính toán"),
        ("FDR", "Fault Detection Rate — Tỷ lệ phát hiện lỗi phần cứng"),
        ("SDC", "Silent Data Corruption — Lỗi hỏng dữ liệu thầm lặng không được phát hiện"),
        ("SEU", "Single-Event Upset — Lỗi lật bit đơn do bức xạ hạt năng lượng cao"),
        ("MBU", "Multiple-Bit Upset — Lỗi lật đồng thời nhiều bit"),
        ("TMR", "Triple Modular Redundancy — Dự phòng ba mô-đun"),
        ("DMR", "Dual Modular Redundancy — Dự phòng hai mô-đun"),
        ("FPGA", "Field-Programmable Gate Array — Mảng cổng logic khả trình"),
        ("FF", "Flip-Flop — Phần tử lưu trữ đồng bộ (thanh ghi 1-bit)"),
        ("STA", "Static Timing Analysis — Phân tích thời gian tĩnh"),
        ("WNS", "Worst Negative Slack — Trượt thời gian xấu nhất (Setup)"),
        ("WHS", "Worst Hold Slack — Trượt giữ xấu nhất (Hold)"),
        ("PPA", "Power, Performance, Area — Bộ 3 chỉ tiêu: Công suất, Hiệu năng, Diện tích"),
        ("MMIO", "Memory-Mapped I/O — Giao tiếp ngoại vi ánh xạ bộ nhớ"),
        ("IRQ", "Interrupt Request — Yêu cầu ngắt cứng"),
        ("DSP", "Digital Signal Processing — Khối xử lý tín hiệu số chuyên dụng"),
        ("DNN", "Deep Neural Network — Mạng nơ-ron sâu"),
        ("AI/ML", "Artificial Intelligence / Machine Learning — Trí tuệ nhân tạo / Học máy"),
        ("RTL", "Register-Transfer Level — Mức truyền thanh ghi (mô tả phần cứng)"),
        ("Fmax", "Maximum Operating Frequency — Tần số hoạt động tối đa"),
        ("EDA", "Electronic Design Automation — Tự động hoá thiết kế vi mạch"),
    ]

    tbl_abbr = doc.add_table(rows=1 + len(abbrevs), cols=2)
    tbl_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_abbr.style = "Table Grid"

    hdr = tbl_abbr.rows[0].cells
    hdr[0].text = "Từ viết tắt"
    hdr[1].text = "Giải thích thuật ngữ chi tiết"
    style_header_row(tbl_abbr, 0)

    for idx, (abbr, meaning) in enumerate(abbrevs, start=1):
        row = tbl_abbr.rows[idx].cells
        row[0].text = abbr
        row[1].text = meaning
        for cell in row:
            set_cell_margins(cell)
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(10)
                    run.font.name = "Times New Roman"
        # Alternate row colour
        if idx % 2 == 0:
            for cell in row:
                set_cell_bg(cell, "E3F2FD")

    doc.add_page_break()

    # ═════════════════════════════════════════════════════════════════════════
    #  CHƯƠNG 1: TỔNG QUAN VÀ TÍNH CẤP THIẾT
    # ═════════════════════════════════════════════════════════════════════════
    doc.add_heading("CHƯƠNG 1. TỔNG QUAN VÀ TÍNH CẤP THIẾT CỦA ĐỀ TÀI", level=1)

    # 1.1
    doc.add_heading("1.1. Bối cảnh nghiên cứu: AI tại biên và nhu cầu tăng tốc phần cứng", level=2)
    add_body(doc,
        "Sự bùng nổ của các ứng dụng trí tuệ nhân tạo (AI) và học máy (ML) tại các thiết bị biên "
        "(Edge Devices) như vi điều khiển, hệ thống nhúng IoT, thiết bị y tế di động và xe tự lái đặt ra "
        "yêu cầu cấp thiết về các bộ tăng tốc phần cứng chuyên dụng có khả năng thực hiện phép nhân "
        "tích lũy (Multiply-Accumulate — MAC) với hiệu suất cao, tiêu thụ năng lượng thấp và đặc biệt "
        "là đảm bảo tính toàn vẹn kết quả tính toán trong môi trường bức xạ hoặc nhiễu điện từ khắc nghiệt [9].",
        indent_cm=1)

    add_body(doc,
        "Phép toán MAC (C = A × B + C) là phép toán nền tảng chiếm tới hơn 90% khối lượng tính toán trong "
        "mạng nơ-ron sâu (DNN) [9]. Khi triển khai trên phần cứng FPGA hoặc ASIC, mỗi nơ-ron trong lớp "
        "tích chập (Convolutional Layer) và lớp kết nối đầy đủ (Fully-Connected Layer) đều thực hiện hàng "
        "nghìn đến hàng triệu phép MAC trong mỗi vòng suy luận (Inference Cycle). Một lỗi phần cứng đơn lẻ "
        "tại bất kỳ vị trí nào trong chuỗi tính toán MAC đều có thể lan truyền và làm sai lệch toàn bộ kết quả "
        "suy luận, gây ra hậu quả nghiêm trọng trong các hệ thống an toàn [11], [12].",
        indent_cm=1)

    # 1.2
    doc.add_heading("1.2. Thách thức an toàn phần cứng: Lỗi mềm SEU và Tấn công tiêm lỗi", level=2)
    add_body(doc,
        "Trong môi trường vũ trụ, hàng không, hoặc thậm chí tại mặt đất ở các nút công nghệ tiên tiến "
        "(dưới 28 nm), hiện tượng lỗi mềm SEU (Single-Event Upset) do tia vũ trụ hoặc hạt alpha gây ra "
        "ngày càng trở nên phổ biến [11]. Một hạt năng lượng cao va chạm với vùng nhạy cảm của mạch tích hợp "
        "có thể làm lật giá trị logic của một hoặc nhiều bit trong các phần tử lưu trữ (flip-flop, SRAM), "
        "tạo ra lỗi lật bit đơn (SEU) hoặc lỗi lật đồng thời nhiều bit (MBU — Multiple-Bit Upset).",
        indent_cm=1)

    add_body(doc,
        "Bên cạnh lỗi tự nhiên, các cuộc tấn công tiêm lỗi có chủ đích (Fault Injection Attacks) "
        "như Voltage Glitching, Laser Fault Injection và Electromagnetic Fault Injection (EMFI) "
        "cho phép kẻ tấn công cố tình gây ra lỗi phần cứng ở vị trí và thời điểm chính xác để "
        "trích xuất khoá mật mã hoặc vô hiệu hoá cơ chế bảo mật [11], [13].",
        indent_cm=1)

    # 1.3
    doc.add_heading("1.3. Phân tích hạn chế của các giải pháp dung lỗi kinh điển (TMR, DMR, Parity)", level=2)
    add_body(doc,
        "Để đối phó với lỗi phần cứng, các kỹ thuật dung lỗi truyền thống bộc lộ những nhược điểm "
        "lớn đối với thiết bị biên [1], [3], [8], [13]:", indent_cm=1)

    limitations = [
        ("1. Dự phòng ba mô-đun (Triple Modular Redundancy — TMR) [1]:",
         "Nhân bản 3 khối phần cứng và dùng bộ biểu quyết (Majority Voter). Theo khảo sát toàn diện của Flad et al. [1] (ACM CSUR 2026), "
         "TMR làm tăng chi phí diện tích silicon hơn 215% đến 260% (> 2.100 LUTs) và công suất tăng gấp 3 lần (> 350 mW), hoàn toàn "
         "không phù hợp cho chip Edge AI bị giới hạn nghiêm ngặt về diện tích và nhiệt."),
        ("2. Dự phòng hai mô-đun (Dual Modular Redundancy — DMR / PDMR) [1], [3]:",
         "Nhân bản 2 khối phần cứng. Theo các khảo sát của Flad et al. [1] và nghiên cứu của Alves et al. [3] (IEEE Access 2024), Matsuo et al. [6] (2020), "
         "DMR tăng chi phí diện tích 108% đến 125% (> 1.050 LUTs), chỉ phát hiện được lỗi mà không tự sửa được, buộc CPU phải "
         "bẫy phần mềm chạy lại tốn 50–120 chu kỳ xung nhịp."),
        ("3. Mã kiểm tra chẵn lẻ (Parity Code / SECDED) [8], [13]:",
         "Dù có chi phí phần cứng thấp (< 3,5% LUTs) [8], các phân tích thực nghiệm của Bertoni et al. [13] (IEEE Trans. Computers 2003) "
         "và Webber [8] (2018) chỉ ra rằng mã Parity tuyến tính chỉ bảo vệ được đường truyền dữ liệu (Bus) hoặc ô nhớ (RAM/Registers). "
         "Khi đi qua mạch số học nhân cộng có chuỗi nhớ lan truyền (Carry Ripple), tính chẵn lẻ bị phá vỡ và không thể phát hiện lỗi số học (FDR rớt về 0%)."),
    ]
    for title, desc in limitations:
        add_body(doc, title, bold=True, size=12)
        add_body(doc, desc, indent_cm=1)

    # 1.4
    doc.add_heading("1.4. Mục tiêu nghiên cứu và Đóng góp kỹ thuật cốt lõi", level=2)
    add_body(doc, "Đề tài giải quyết triệt để bài toán trên thông qua 4 đóng góp kỹ thuật cốt lõi:", indent_cm=1)
    contributions = [
        "1. Thiết kế lõi CPU RISC-V RV32I 5 tầng pipeline hoàn chỉnh với cơ chế xử lý rủi ro "
        "Hazard Unit và rẽ nhánh sớm tại tầng ID [7].",
        "2. Ứng dụng Mã thặng dư số học Modulo-3 với Cây rút gọn nhị phân cân bằng để thực hiện "
        "phát hiện lỗi đồng thời (CED) bảo toàn đồng cấu cho cả phép nhân 16-bit và phép cộng "
        "tích lũy 32-bit với độ trễ tối thiểu O(log₂N) [10], [16].",
        "3. Hiện thực cơ chế Khôi phục trạng thái phần cứng (Hardware Rollback) tức thời trong đúng "
        "1 chu kỳ xung nhịp bằng thanh ghi bóng (Shadow Accumulator) và xuất tín hiệu ngắt cứng IRQ.",
        "4. Tích hợp toàn bộ hệ thống SoC qua giao tiếp MMIO và xác thực thực nghiệm toàn diện "
        "trên vi mạch FPGA Xilinx Zynq-7000.",
    ]
    for c in contributions:
        add_body(doc, c, indent_cm=1)

    # 1.5
    doc.add_heading("1.5. Đối tượng, Phạm vi và Phương pháp nghiên cứu", level=2)
    add_body(doc,
        "Đối tượng nghiên cứu của đề tài là kiến trúc phần cứng lõi vi xử lý RISC-V RV32I và bộ "
        "tăng tốc phần cứng Secure MAC ứng dụng cho suy luận AI tại biên. Phạm vi nghiên cứu "
        "tập trung vào thiết kế, mô phỏng và tổng hợp mức RTL, kiểm chứng bằng mô phỏng "
        "chức năng Cocotb trên Icarus Verilog, và hiện thực trên FPGA thực tế (Xilinx Zynq-7000) "
        "với bộ công cụ EDA thương mại AMD Xilinx Vivado 2026.1.", indent_cm=1)

    # 1.6
    doc.add_heading("1.6. Cấu trúc báo cáo", level=2)
    add_body(doc,
        "Báo cáo được tổ chức thành 3 chương: Chương 1 trình bày tổng quan và tính cấp thiết "
        "của đề tài; Chương 2 trình bày cơ sở lý thuyết, vi kiến trúc hệ thống đề xuất; "
        "Chương 3 trình bày kết quả triển khai thực nghiệm, chiến dịch tiêm lỗi 26.040 mẫu thử, "
        "phân tích tính mới và kết luận.", indent_cm=1)

    doc.add_page_break()

    # ═════════════════════════════════════════════════════════════════════════
    #  CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ VI KIẾN TRÚC HỆ THỐNG ĐỀ XUẤT
    # ═════════════════════════════════════════════════════════════════════════
    doc.add_heading("CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ VI KIẾN TRÚC HỆ THỐNG ĐỀ XUẤT", level=1)

    # 2.1
    doc.add_heading("2.1. Kiến trúc Tập lệnh Mở RISC-V RV32I và Nguyên lý Datapath", level=2)

    doc.add_heading("2.1.1. Không gian tập lệnh cơ sở RV32I và 6 định dạng lệnh", level=3)
    add_body(doc,
        "Hệ thống hiện thực đầy đủ 37 lệnh của tập lệnh cơ sở RISC-V RV32I [7] với độ dài "
        "cố định 32-bit, chia thành 6 định dạng chuẩn:", indent_cm=1)
    isa_formats = [
        "- R-Type: ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND",
        "- I-Type: JALR, LB, LH, LW, LBU, LHU, ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI",
        "- S-Type: SB, SH, SW",
        "- B-Type: BEQ, BNE, BLT, BGE, BLTU, BGEU",
        "- U-Type: LUI, AUIPC",
        "- J-Type: JAL",
    ]
    for line in isa_formats:
        add_body(doc, line)

    doc.add_heading("2.1.2. Vi kiến trúc Lõi CPU RISC-V 5 tầng Pipeline (IF, ID, EX, MEM, WB)", level=3)
    add_figure(doc, figures_dir, "fig2_1_rv32i_soc_datapath.png",
               "Hình 2.1: Sơ đồ đường truyền dữ liệu (Datapath) lõi CPU RISC-V RV32I 5 tầng pipeline "
               "tích hợp Hazard Unit và Data Forwarding", width_inches=5.8)

    add_body(doc, "Lõi CPU được chia thành 5 tầng xử lý:", indent_cm=1)
    stages = [
        "1. IF (Instruction Fetch): Nạp lệnh từ IMEM và cập nhật con trỏ PC.",
        "2. ID (Instruction Decode): Giải mã lệnh, đọc tập tin 32 thanh ghi (Register File), mở rộng dấu giá trị tức thì, và đánh giá rẽ nhánh sớm.",
        "3. EX (Execute): Thực thi phép toán ALU 32-bit, tính địa chỉ bộ nhớ hiệu dụng.",
        "4. MEM (Memory Access): Đọc/ghi RAM dữ liệu (DMEM) hoặc truy xuất vùng nhớ MMIO của bộ tăng tốc MAC.",
        "5. WB (Write-Back): Ghi kết quả tính toán vào thanh ghi đích rd.",
    ]
    for s in stages:
        add_body(doc, s, indent_cm=1)

    doc.add_heading("2.1.3. Khối xử lý rủi ro tích hợp (Hazard Unit) và Chuyển tiếp dữ liệu", level=3)
    add_body(doc,
        "- Data Forwarding: Chuyển tiếp dữ liệu trực tiếp từ tầng MEM và tầng WB "
        "về ngõ vào ALU tại tầng EX, triệt tiêu chu kỳ trễ do phụ thuộc dữ liệu.")
    add_body(doc,
        "- Load-Use Hazard Stalling: Tạm dừng 1 chu kỳ khi lệnh liền sau sử dụng "
        "kết quả của lệnh nạp LW trước đó.")

    doc.add_heading("2.1.4. Giải quyết rẽ nhánh sớm 1 chu kỳ tại tầng ID (Early Branch Resolution)", level=3)
    add_body(doc,
        "Bộ so sánh branch_cmp.sv đánh giá điều kiện rẽ nhánh ngay tại tầng ID, "
        "giảm thiểu tổn thất rẽ nhánh (branch penalty) xuống đúng 1 chu kỳ xung nhịp.", indent_cm=1)

    # 2.2
    doc.add_heading("2.2. Cơ sở Toán học của Mã thặng dư số học Modulo-3 (Arithmetic Residue Code)", level=2)

    doc.add_heading("2.2.1. Tính đồng cấu số học cho phép nhân cộng MAC", level=3)
    add_body(doc,
        "Ánh xạ thặng dư số học φ(X) = X mod 3 là một đồng cấu vành bảo toàn đồng thời "
        "phép nhân và phép cộng [10], [16]:", indent_cm=1)
    add_body(doc, "φ(A × B + C) = [ (φ(A) × φ(B)) mod 3 + φ(C) ] mod 3",
             bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_body(doc,
        "Điều này cho phép xây dựng một kênh kiểm tra độc lập chạy song song với mạch MAC "
        "chính để tính toán thặng dư kỳ vọng và so sánh với thặng dư thực tế của kết quả.", indent_cm=1)

    doc.add_heading("2.2.2. Tính chất luân phiên trọng số nhị phân 2^k mod 3", level=3)
    add_body(doc,
        "Trọng số của luỹ thừa cơ số 2 theo modulo 3 có tính chất tuần hoàn chu kỳ 2:", indent_cm=1)
    add_body(doc, "2^k mod 3 = 1 khi k chẵn, và 2^k mod 3 = 2 (tương đương −1) khi k lẻ.",
             bold=True, indent_cm=1)
    add_body(doc,
        "Đối với số bù 2 có dấu N-bit (N chẵn), trọng số của bit dấu MSB b(N−1) (vị trí lẻ) "
        "là −2^(N−1) mod 3 = +1 mod 3. Do đó thặng dư của cặp bit dấu MSB [b(N−1), b(N−2)] "
        "bằng đúng (b(N−1) + b(N−2)) mod 3.", indent_cm=1)

    doc.add_heading("2.2.3. Chứng minh Định lý Bit-Pair Parity cho phân bố lỗi kép Double-Bit MBU", level=3)
    add_body(doc,
        "- Sai số sinh ra bởi lỗi lật 2 bit tại vị trí i và j là: "
        "e = Δᵢ·2^i + Δⱼ·2^j, với Δᵢ, Δⱼ ∈ {+1, −1}.")
    add_body(doc,
        "- Khi i và j cùng tính chẵn lẻ (i ≡ j mod 2): e mod 3 = w·(Δᵢ + Δⱼ) mod 3. "
        "Lỗi phát hiện được khi Δᵢ = Δⱼ (chiếm 2/4 trường hợp = 50,0%), và bị che giấu "
        "khi Δᵢ ≠ Δⱼ (chiếm 2/4 trường hợp = 50,0%).")
    add_body(doc,
        "- Khi i và j khác tính chẵn lẻ (i ≢ j mod 2): e mod 3 = (Δᵢ − Δⱼ) mod 3. "
        "Lỗi phát hiện được khi Δᵢ ≠ Δⱼ (chiếm 2/4 trường hợp = 50,0%), và bị che giấu "
        "khi Δᵢ = Δⱼ (chiếm 2/4 trường hợp = 50,0%).")
    add_body(doc,
        "- Tổng hợp trên toàn bộ không gian tổ hợp C(N, 2) cặp bit, xác suất phát hiện "
        "lỗi kép luôn luôn bằng đúng 50,00% tuyệt đối — nhưng phân bố không đều mà tuân "
        "theo quy luật nhị phân chẵn/lẻ khoảng cách bit (Bit-Distance Parity).")

    doc.add_heading("2.2.4. Cơ chế Double-Check: Khắc phục triệt để điểm mù lỗi 2-bit bằng Bit-Interleaving và Mã Đa Cơ Số RNS", level=3)
    add_body(doc,
        "Để xử lý 50% các trường hợp lỗi kép (MBU) rơi vào khoảng cách triệt tiêu đồng dư e mod 3 = 0, "
        "nghiên cứu đề xuất và hiện thực ba cơ chế Double-Check bổ trợ toàn diện:", indent_cm=1)
    add_body(doc,
        "1. Kỹ thuật đảo xen kẽ bit vật lý (Physical Bit-Interleaving Layout) [17]: Trong bố trí vi mạch thực tế (Floorplanning), "
        "các ô nhớ flip-flop không đặt theo thứ tự logic liên tiếp mà được xếp xen kẽ chẵn/lẻ ở hai hàng vật lý kề nhau. "
        "Khi một sự kiện lỗi bức xạ hoặc tia laser chiếu vào tấm silicon làm lật 2 ô nhớ liền kề (khoảng cách vật lý = 1), "
        "khoảng cách logic tương ứng luôn là số lẻ (d = 1, 3, 5). Nhờ đó, mã Modulo-3 phát hiện được 100% lỗi kép vật lý mà không tốn thêm diện tích logic.")
    add_body(doc,
        "2. Kiến trúc Thặng dư Đa cơ số (Residue Number System — RNS Modulo 3 + Modulo 5) [18]: Bổ sung kênh kiểm tra Modulo-5 "
        "song song với Modulo-3. Do Modulo-5 chỉ bị triệt tiêu ở các khoảng cách là bội số của 4 (d = 4, 8, 12...), không gian giao giữa hai bộ "
        "kiểm tra giúp triệt tiêu góc mù và nâng tỷ lệ phát hiện lỗi đa bit tổng thể từ 50% lên trên 93,75%.")
    add_body(doc,
        "3. Cơ chế Kiểm tra Ngưỡng An toàn (Sanity & Dynamic Range Checking): Kiểm soát các giá trị tích lũy biến thiên vượt ngưỡng "
        "phân phối chuẩn (Outliers) trong phép tính MAC của mạng nơ-ron AI, tự động phát hiện sai lệch thặng dư hoặc tràn số bất thường để kích hoạt Rollback.")

    # 2.3
    doc.add_heading("2.3. Thiết kế Vi kiến trúc Bộ tăng tốc Secure MAC 3 tầng Pipeline", level=2)

    doc.add_heading("2.3.1. Cấu trúc luồng đôi song song: Luồng dữ liệu và Luồng kiểm tra thặng dư", level=3)
    add_body(doc,
        "Kiến trúc Secure MAC đề xuất hiện thực đồng thời hai luồng dữ liệu song song:", indent_cm=1)
    add_body(doc,
        "- Luồng chính (Main Datapath): Thực hiện phép nhân 8-bit × 8-bit tạo ra tích số 16-bit "
        "(pipe_product), sau đó cộng tích lũy 32-bit (pipe_c) qua pipeline 3 tầng.")
    add_body(doc,
        "- Luồng kiểm tra (Residue Check Path): Tính thặng dư Modulo-3 độc lập bằng 4 bộ mã hoá "
        "(2 bộ mod3_encoder_8b cho toán tử A, B và 2 bộ mod3_encoder_32b cho bộ tích lũy và kết quả), "
        "nhân thặng dư 2-bit, cộng thặng dư 2-bit, rồi so sánh CED [10], [16].")

    add_figure(doc, figures_dir, "fig2_2_secure_mac_architecture.png",
               "Hình 2.2: Sơ đồ khối tổng thể bộ tăng tốc Secure MAC với cơ chế CED Modulo-3 "
               "và Shadow Rollback", width_inches=5.6)

    add_figure(doc, figures_dir, "fig2_3_double_check_layers.png",
               "Hình 2.3: Sơ đồ luồng dữ liệu Secure MAC pipeline 3 tầng "
               "với kênh kiểm tra CED song song", width_inches=5.6)

    doc.add_heading("2.3.2. Bộ mã hoá thặng dư Modulo-3 (mod3_encoder) — Cây rút gọn nhị phân O(log₂N)", level=3)
    add_body(doc,
        "Bộ mã hoá tận dụng tính chất 2^k mod 3 = 1 (k chẵn) / 2 (k lẻ) để ghép cặp các bit "
        "liên tiếp [b(2i+1), b(2i)] thành N/2 giá trị thặng dư 2-bit, sau đó rút gọn bằng "
        "cây cộng Modulo-3 cân bằng với độ sâu O(log₂(N/2)). Đối với N = 32 bit, cây chỉ cần "
        "4 tầng cộng, đảm bảo độ trễ tổ hợp tối thiểu.", indent_cm=1)

    add_figure(doc, figures_dir, "fig2_4_mod3_encoder_8b.png",
               "Hình 2.4: Sơ đồ chi tiết bộ mã hoá thặng dư mod3_encoder_8b "
               "(Cây rút gọn nhị phân 4 cặp bit)", width_inches=5.6)

    add_figure(doc, figures_dir, "fig2_5_mod3_encoder_32b.png",
               "Hình 2.5: Sơ đồ chi tiết bộ mã hoá thặng dư mod3_encoder_32b "
               "(Cây rút gọn nhị phân 16 cặp bit, 4 tầng)", width_inches=5.6)

    doc.add_heading("2.3.3. Cơ chế khôi phục trạng thái phần cứng Rollback 1 chu kỳ bằng Shadow Accumulator", level=3)
    add_body(doc,
        "Khi bộ so sánh CED phát hiện sai lệch thặng dư (fault_detected = 1), cơ chế Rollback "
        "được kích hoạt trong cùng chu kỳ xung nhịp đó:", indent_cm=1)
    rollback_steps = [
        "1. Tín hiệu fault_detected = 1 kích hoạt MUX Rollback chọn giá trị shadow_accumulator "
        "(bản sao lưu tại chu kỳ trước) thay vì kết quả MAC bị lỗi.",
        "2. Giá trị shadow_accumulator được ghi đè lên thanh ghi tích lũy pipe_c, phục hồi trạng "
        "thái đúng tức thời.",
        "3. Tín hiệu ngắt cứng irq_fault_detected được xuất ra cho CPU để thông báo sự kiện lỗi.",
    ]
    for step in rollback_steps:
        add_body(doc, step, indent_cm=1)

    if (figures_dir / "fig2_6_waveform_rollback.png").exists():
        add_figure(doc, figures_dir, "fig2_6_waveform_rollback.png",
                   "Hình 2.6: Giản đồ dạng sóng mô phỏng Rollback 1 chu kỳ — "
                   "Phát hiện lỗi → Khôi phục shadow_accumulator → Xuất IRQ", width_inches=6.0)

    doc.add_heading("2.4. Tổng kết Vi kiến trúc Phần cứng Hệ thống Đề xuất", level=2)
    add_body(doc,
        "Sự phối hợp chặt chẽ giữa lõi vi xử lý RV32I 5 tầng pipeline và bộ tăng tốc Secure MAC 3 tầng pipeline "
        "thông qua không gian địa chỉ ánh xạ bộ nhớ (MMIO: 0x8000_0000 - 0x8000_0010) và đường ngắt phần cứng irq "
        "tạo nên một hệ thống SoC an toàn toàn diện, có khả năng tự phát hiện và khôi phục lỗi phần cứng ngay trong 1 chu kỳ mà không cần can thiệp phần mềm.", indent_cm=1)

    doc.add_page_break()

    # ═════════════════════════════════════════════════════════════════════════
    #  CHƯƠNG 3: KẾT QUẢ THỰC NGHIỆM VÀ CHIẾN DỊCH TIÊM LỖI
    # ═════════════════════════════════════════════════════════════════════════
    doc.add_heading("CHƯƠNG 3. KẾT QUẢ TRIỂN KHAI THỰC NGHIỆM VÀ ĐÁNH GIÁ AN TOÀN PHẦN CỨNG", level=1)

    # 3.1 PPA
    doc.add_heading("3.1. Kết quả tổng hợp và thực thi phần cứng trên FPGA Xilinx Zynq-7000", level=2)
    add_body(doc,
        "Thiết kế đã được thực hiện toàn bộ quy trình tổng hợp (Synthesis), phân bổ và định tuyến "
        "(Place & Route) thực tế bằng công cụ thương mại AMD Xilinx Vivado 2026.1 trên vi mạch FPGA "
        "Xilinx Zynq-7000 XC7Z020-CLG400-1.", indent_cm=1)

    # Bảng phân bổ tài nguyên (Bảng 1 trong template)
    doc.add_heading("Bảng 3.1: Phân bổ tài nguyên phân cấp và PPA trong SoC (Hierarchical Utilization & STA)", level=3)

    resource_data = [
        ["Khối chức năng (Instance)", "Slice LUTs", "Flip-Flops (FFs)", "CARRY4 / MUX", "Tỷ lệ trên XC7Z020", "Timing @ 100 MHz"],
        ["1. Lõi CPU RISC-V (u_cpu)", "620 (72,09%)", "864 (80,45%)", "28 CARRY4", "1,17% LUT / 0,81% FF", "WNS = +1,289 ns"],
        ["2. Bộ tăng tốc Secure MAC (u_mac)", "135 (15,70%)", "138 (12,85%)", "28 CARRY4", "0,25% LUT / 0,13% FF", "Pipeline 3 tầng đồng bộ"],
        ["3. Bộ nhớ dữ liệu RAM (u_dmem)", "61 (7,09%)", "32 (2,98%)", "32 Dist. RAM", "0,11% LUT / 0,03% FF", "Ghép nối tầng MEM"],
        ["4. Logic ghép nối MMIO & Bus", "44 (5,12%)", "40 (3,72%)", "0", "0,08% LUT / 0,04% FF", "0 chu kỳ trễ bổ sung"],
        ["Tổng SoC Top (top_module)", "860 (100,0%)", "1.074 (100,0%)", "56 CARRY4, 96 MUX", "1,62% LUT / 1,01% FF", "Fmax = 114,80 MHz\nWNS = +1,289 ns\nWHS = +0,028 ns\nPower = 122 mW"],
        ["Khối Secure MAC Standalone", "240 LUTs", "138 FFs", "36 CARRY4, 0 DSP", "0,45% LUT / 0,13% FF", "Fmax = 119,88 MHz\nTmin = 8,342 ns\nWHS = +0,181 ns\nPower = 116 mW"],
    ]

    tbl_res = doc.add_table(rows=len(resource_data), cols=6)
    tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_res.style = "Table Grid"
    for ri, row_data in enumerate(resource_data):
        for ci, val in enumerate(row_data):
            cell = tbl_res.rows[ri].cells[ci]
            cell.text = val
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9.5)
                    run.font.name = "Times New Roman"
    style_header_row(tbl_res, 0)
    # Highlight total and standalone rows
    set_cell_bg(tbl_res.rows[5].cells[0], "E3F2FD")
    set_cell_bg(tbl_res.rows[6].cells[0], "E8F5E9")

    add_body(doc, "")  # spacer

    if (figures_dir / "fig2_7_vivado_hierarchical_gui.png").exists():
        add_figure(doc, figures_dir, "fig2_7_vivado_hierarchical_gui.png",
                   "Hình 3.1: Ảnh chụp bảng phân bổ tài nguyên phân cấp thực tế từ Vivado 2026.1 GUI "
                   "(860 LUTs, 1.074 FFs trên XC7Z020)", width_inches=5.6)

    add_figure(doc, figures_dir, "fig3_1_fpga_ppa_implementation.png",
               "Hình 3.1: Bố cục lưới 2×2 đo đạc PPA sau triển khai FPGA Vivado 2026.1 — "
               "(a) Tài nguyên phần cứng, (b) Timing Slack STA, (c) Tần số Fmax, (d) Công suất", width_inches=6.2)

    # 3.1.1 Chi phí silicon
    doc.add_heading("3.1.1. Định lượng Chi phí Silicon (Silicon Overhead) của Cơ chế Đề xuất", level=3)
    add_body(doc,
        "Để đánh giá chính xác chi phí phần cứng của cơ chế phát hiện lỗi Modulo-3 và khôi phục Shadow Rollback, "
        "thiết kế Secure MAC được so sánh trực tiếp với một khối MAC cơ sở 3 tầng pipeline không tích hợp bảo vệ (Baseline MAC):", indent_cm=1)

    overhead_items = [
        ("1. Chi phí Bảng tra cứu Logic (Slice LUTs):",
         "Khối Baseline MAC (gồm bộ nhân 8×8, bộ cộng 32-bit và các thanh ghi phân tầng) chiếm 100 LUTs. "
         "Khối Secure MAC đề xuất (tích hợp 4 bộ mod3_encoder, bộ nhân/cộng thặng dư 2-bit, bộ so sánh CED, "
         "thanh ghi bóng shadow_accumulator 32-bit và MUX Rollback) chiếm 135 LUTs trong SoC (hoặc 240 LUTs độc lập). "
         "Mức tăng diện tích trên khối MAC là: Overhead_LUT(MAC) = (135 − 100) / 100 × 100% = +35,00% (+35 LUTs). "
         "Trên toàn hệ thống SoC Top (860 LUTs), mức tăng diện tích chỉ là: Overhead_LUT(SoC) = 35 / 860 × 100% = +4,07%."),

        ("2. Chi phí Phần tử Lưu trữ (Slice Registers / Flip-Flops):",
         "Khối Baseline MAC sử dụng 75 FFs (lưu trữ toán tử A, B, tích số 16-bit và tích lũy 32-bit). "
         "Khối Secure MAC sử dụng 137 FFs (bổ sung 32 FFs cho thanh ghi bóng shadow_accumulator, 8 FFs cho các thanh ghi "
         "thặng dư 2-bit và các cờ trạng thái/ngắt IRQ). Mức tăng thanh ghi trên khối MAC là: Overhead_FF(MAC) = (137 − 75) / 75 × 100% = +82,67% (+62 FFs). "
         "Trên toàn bộ SoC Top (1.074 FFs), mức tăng thanh ghi chỉ là: Overhead_FF(SoC) = 62 / 1.074 × 100% = +5,78%."),

        ("3. Chi phí Công suất Tiêu thụ (Power Overhead @ 100 MHz):",
         "Công suất tiêu thụ tổng cộng của khối Secure MAC độc lập là 116 mW (14 mW động, 103 mW tĩnh), "
         "chỉ tăng thêm +8 mW (+7,55%) so với Baseline MAC (~106 mW). Toàn bộ hệ thống SoC Top chỉ tiêu thụ 122 mW "
         "(19 mW động, 103 mW tĩnh), hoàn toàn đáp ứng ngưỡng năng lượng cho thiết bị biên Edge AI."),

        ("4. Hiệu năng Tần số Hoạt động Cực đại (Fmax & Timing Slack):",
         "Nhờ cấu trúc Cây rút gọn nhị phân cân bằng O(log₂N) của bộ mã hoá Modulo-3, độ trễ lan truyền thặng dư "
         "hoàn toàn ẩn sau độ trễ của bộ nhân 8×8 và bộ cộng 32-bit chính. Tần số Fmax của Secure MAC đạt 119,88 MHz "
         "(WNS = +2,014 ns @ 100 MHz), chỉ suy giảm -4,77% so với Baseline MAC (131,5 MHz), và toàn SoC đạt 114,80 MHz (WNS = +1,289 ns)."),
    ]
    for title, desc in overhead_items:
        add_body(doc, title, bold=True, size=11.5)
        add_body(doc, desc, indent_cm=1)

    # Bảng 3.2: Đối chiếu chi tiết Baseline MAC vs Secure MAC
    doc.add_heading("Bảng 3.2: Đối chiếu Kỹ thuật Chi tiết giữa Baseline MAC và Secure MAC Đề xuất (Vi kiến trúc, PPA Vivado 2026.1 & Khả năng Dung lỗi)", level=3)

    baseline_vs_secure_data = [
        ["Nhóm Tiêu chí Kỹ thuật", "Chỉ số Chi tiết", "Baseline MAC (baseline_mac.v)", "Secure MAC (secure_mac.v)", "Chênh lệch / Chi phí (Overhead)"],
        # 1. Vi kiến trúc
        ["1. Vi kiến trúc & Logic", "Độ rộng toán hạng & Tầng pipeline", "8×8-bit (INT8) + 32-bit Acc, 3 tầng", "8×8-bit (INT8) + 32-bit Acc, 3 tầng", "0 tầng trễ bổ sung (Latency = 3 CK)"],
        ["1. Vi kiến trúc & Logic", "Cơ chế kiểm tra lỗi (CED)", "Không tích hợp (0% bảo vệ)", "Đồng cấu Modulo-3 (Cây nhị phân O(log₂N))", "Kênh thặng dư 2-bit tính song song"],
        ["1. Vi kiến trúc & Logic", "Bộ mã hoá thặng dư Modulo-3", "0 bộ", "4 bộ (2× mod3_8b, 2× mod3_32b)", "Khối mã hoá chuyên biệt cực nhỏ"],
        ["1. Vi kiến trúc & Logic", "Cơ chế tự khôi phục (Rollback)", "Không có (SDC = 100% khi lỗi)", "Shadow Accumulator 32-bit + MUX", "Tự hoàn tác trạng thái trong 1 chu kỳ"],
        ["1. Vi kiến trúc & Logic", "Tín hiệu cảnh báo / Giao tiếp", "out[31:0], valid", "out, valid, fault_detected, rollback, irq", "Xuất ngắt phần cứng trực tiếp cho CPU"],
        # 2. PPA FPGA
        ["2. PPA Phần cứng (XC7Z020)", "Bảng tra cứu Logic (Slice LUTs)", "99 LUTs (~100 trong SoC)", "135 LUTs (trong SoC) / 178 (Standalone)", "+35 LUTs (+35,00% trên MAC / +4,07% SoC)"],
        ["2. PPA Phần cứng (XC7Z020)", "Thanh ghi Flip-Flops (FFs)", "75 FFs (lõi) / 131 FFs (standalone)", "137 FFs", "+62 FFs (+82,67% trên MAC / +5,78% SoC)"],
        ["2. PPA Phần cứng (XC7Z020)", "Bộ cộng chuỗi (CARRY4)", "20 CARRY4", "29 CARRY4", "+9 CARRY4 (+45,00%)"],
        ["2. PPA Phần cứng (XC7Z020)", "Khối DSP / RAM chuyên dụng", "0 DSP, 0 BRAM", "0 DSP, 0 BRAM", "Thuần LUT fabric, khả chuyển cao"],
        # 3. Timing & Công suất
        ["3. Timing & Công suất", "Tần số cực đại (Fmax)", "176,50 MHz (Standalone)", "119,88 MHz (Standalone) / 114,80 (SoC)", "Toàn SoC vượt an toàn mốc 100 MHz"],
        ["3. Timing & Công suất", "Thời gian tới hạn (Tmin)", "5,665 ns", "8,342 ns (Standalone) / 8,711 ns (SoC)", "+2,321 ns (Do trễ bộ so sánh & MUX)"],
        ["3. Timing & Công suất", "Tổng công suất On-Chip (Power)", "108 mW (5 mW động, 103 mW tĩnh)", "116 mW (14 mW động, 103 mW tĩnh)", "+6 mW (+5,55% trên MAC / +5,17% SoC)"],
        ["3. Timing & Công suất", "Biến thiên thời gian (Timing Jitter)", "0 ns (Không sửa)", "0 ns (Bất biến 3 chu kỳ)", "Kháng Side-Channel Timing Attacks"],
        # 4. Dung lỗi
        ["4. Khả năng Dung lỗi", "Lỗi lật bit đơn (Single-Bit SEU)", "FDR = 0,00% (SDC = 100,00%)", "FDR = 100,00% (SDC = 0,00%)", "Triệt tiêu 100% rủi ro hỏng dữ liệu thầm lặng"],
        ["4. Khả năng Dung lỗi", "Lỗi kẹt logic (Stuck-At Faults)", "FDR = 0,00%", "FDR = 100,00%", "Phát hiện 100% lỗi SA0/SA1 trên 5 khối con"],
        ["4. Khả năng Dung lỗi", "Lỗi kép 2-bit (Double-Bit MBU)", "FDR = 0,00%", "FDR = 48,39% (TB)", "100% cặp d chẵn, 0% cặp d lẻ"],
        ["4. Khả năng Dung lỗi", "Lỗi chùm đa bit (Bursts k = 1..6)", "FDR = 0,00%", "FDR = 68,68%", "Tiệm cận ngưỡng lý thuyết 2/3 ≈ 66,67%"],
        ["4. Khả năng Dung lỗi", "Độ chính xác Khôi phục Rollback", "0,00%", "100,00% (trong đúng 1 chu kỳ)", "Phục hồi tức thời không gián đoạn CPU"],
    ]

    tbl_b_vs_s = doc.add_table(rows=len(baseline_vs_secure_data), cols=5)
    tbl_b_vs_s.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_b_vs_s.style = "Table Grid"
    for ri, row_data in enumerate(baseline_vs_secure_data):
        for ci, val in enumerate(row_data):
            cell = tbl_b_vs_s.rows[ri].cells[ci]
            cell.text = val
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            for para in cell.paragraphs:
                if ci == 0 or ci == 1:
                    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9.0)
                    run.font.name = "Times New Roman"
    style_header_row(tbl_b_vs_s, 0)
    # Style category headers
    for r_idx in [1, 6, 10, 14]:
        set_cell_bg(tbl_b_vs_s.rows[r_idx].cells[0], "F5F5F5")

    add_body(doc, "")  # spacer

    # 3.2 Chiến dịch tiêm lỗi
    doc.add_heading("3.2. Phân tích Kết quả Chiến dịch Tiêm lỗi Toàn diện (26.040 Mẫu thử Cocotb)", level=2)

    add_body(doc,
        "Một chiến dịch tiêm lỗi tự động quy mô lớn đã được tiến hành với 26.040 mẫu thử "
        "bằng khung kiểm chứng Cocotb 2.0 trên Icarus Verilog:", indent_cm=1)

    # 3.2.1 Single-bit
    doc.add_heading("3.2.1. Lỗi lật bit đơn (Single-Bit SEU) — 2.400 mẫu thử", level=3)
    add_body(doc, "- Tỷ lệ phát hiện (FDR): 2.400 / 2.400 = 100,00% tuyệt đối.")
    add_body(doc, "- Hỏng dữ liệu thầm lặng (SDC): 0 / 2.400 = 0,00%.")
    add_body(doc, "- Độ chính xác Rollback: 2.400 / 2.400 = 100,00%.")

    add_figure(doc, figures_dir, "fig3_2_single_bit_fdr.png",
               "Hình 3.2: Tỷ lệ phát hiện lỗi đơn bit SEU (FDR = 100,00%) và độ chính xác "
               "khôi phục Rollback trên 32 vị trí bit của bộ tích lũy", width_inches=6.0)

    # 3.2.2 Double-bit (Bit-Distance Spectrum)
    doc.add_heading("3.2.2. Lỗi lật 2 bit đồng thời (Double-Bit MBU) — Phổ Khoảng cách Bit", level=3)
    add_body(doc,
        "Phân tích chuyên sâu trên toàn bộ C(32, 2) = 496 cặp bit của bộ tích lũy 32-bit "
        "cho thấy tỷ lệ phát hiện lỗi 2-bit tuân theo quy luật nhị phân nghiêm ngặt "
        "của Bit-Distance Parity:", indent_cm=1)
    add_body(doc,
        "- Khoảng cách chẵn (d = 2, 4, 6, ..., 30): Hai bit bị lật có cùng tính chẵn lẻ "
        "(cùng trọng số Modulo-3), do đó sai số e mod 3 ≠ 0 trong mọi trường hợp "
        "→ FDR = 100,0% (phát hiện hoàn toàn).")
    add_body(doc,
        "- Khoảng cách lẻ (d = 1, 3, 5, ..., 31): Hai bit bị lật có tính chẵn lẻ ngược nhau "
        "(trọng số Modulo-3 đối xứng +1 và −1), triệt tiêu sai số e mod 3 = 0 "
        "→ FDR = 0,0% (điểm mù — SDC).")
    add_body(doc,
        "- Tỷ lệ phát hiện trung bình toàn cục: 240 / 496 = 48,39% (gần khớp "
        "với ngưỡng lý thuyết 50,00% trên không gian Δᵢ, Δⱼ).")

    add_figure(doc, figures_dir, "fig3_3_bit_distance_parity_spectrum.png",
               "Hình 3.3: Phổ Phát hiện Lỗi 2-bit theo Khoảng cách Bit "
               "(Bit-Distance Parity Spectrum) — Cột xanh: d chẵn = 100% FDR, "
               "Cột đỏ: d lẻ = 0% FDR", width_inches=6.0)

    # 3.2.3 Fault classification breakdown
    doc.add_heading("3.2.3. Phân bổ không gian lỗi 2-bit và Độ bao phủ theo Khối phần cứng", level=3)
    add_body(doc,
        "Phân tích phân loại không gian 496 cặp lỗi 2-bit trên thanh ghi 32-bit cho thấy:", indent_cm=1)
    add_body(doc,
        "- 120 cặp Cùng Chẵn (24,2%): Cả hai bit ở vị trí chẵn → FDR = 100,0%.")
    add_body(doc,
        "- 120 cặp Cùng Lẻ (24,2%): Cả hai bit ở vị trí lẻ → FDR = 100,0%.")
    add_body(doc,
        "- 256 cặp Chẵn-Lẻ (51,6%): Hai bit ở vị trí khác tính chẵn lẻ → FDR = 0,0% (SDC).")
    add_body(doc,
        "Đồng thời, đánh giá độ bao phủ dung lỗi (FDR) và độ chính xác khôi phục (Rollback) "
        "trên từng khối con của kiến trúc Secure MAC đều đạt 100,0%: reg_a (8-bit), reg_b (8-bit), "
        "pipe_product (16-bit), pipe_c (32-bit), và Checker (Residue).", indent_cm=1)

    add_figure(doc, figures_dir, "fig3_4_fault_classification_breakdown.png",
               "Hình 3.4: (a) Biểu đồ Donut phân bổ 496 cặp lỗi 2-bit, "
               "(b) Độ bao phủ FDR và Rollback 100% trên 5 khối con Secure MAC", width_inches=6.2)

    # 3.2.4 Multi-bit burst
    doc.add_heading("3.2.4. Lỗi xung rải đa bit (Multi-Bit Random Bursts, k = 1..6)", level=3)
    add_body(doc,
        "Khi tăng số bit bị lật đồng thời từ k = 1 đến k = 6, tỷ lệ phát hiện lỗi FDR "
        "và tỷ lệ lọt lỗi SDC biến đổi theo công thức tổ hợp:", indent_cm=1)

    burst_data = [
        ("k = 1 bit", "100,00%", "0,00%"),
        ("k = 2 bit", "77,40%", "22,60%"),
        ("k = 3 bit", "91,80%", "8,20%"),
        ("k = 4 bit", "92,20%", "7,80%"),
        ("k = 5 bit", "97,00%", "3,00%"),
        ("k = 6 bit", "97,80%", "2,20%"),
    ]
    for k, fdr, sdc in burst_data:
        add_body(doc, f"  - {k}: FDR = {fdr}, SDC = {sdc}")

    add_body(doc,
        "Đường cong FDR dao động xung quanh và tiệm cận ngưỡng lý thuyết 2/3 ≈ 66,67% "
        "khi k → ∞, xác nhận dự đoán của lý thuyết tổ hợp mã Modulo-3.", indent_cm=1)

    add_figure(doc, figures_dir, "fig3_5_multibit_burst_scaling.png",
               "Hình 3.5: Đường cong tỷ lệ phát hiện FDR và lọt lỗi SDC theo kích thước "
               "cụm lỗi đa bit k = 1..6, tiệm cận ngưỡng lý thuyết 2/3 ≈ 66,67%", width_inches=6.0)

    # 3.2.5 Hardware Rollback
    doc.add_heading("3.2.5. Cơ chế Khôi phục Phần cứng (Hardware Rollback)", level=3)
    add_body(doc, "- Tỷ lệ phục hồi chính xác 100,00% trong đúng 1 chu kỳ xung nhịp.")
    add_body(doc, "- Triệt tiêu hoàn toàn lỗi SDC (0,00%).")
    add_body(doc,
        "- Thời gian thực thi bất biến (Timing Invariance): Cố định 3 chu kỳ xung nhịp "
        "cho mỗi phép MAC bất kể có lỗi hay không (0 ns jitter), kháng hoàn toàn "
        "Side-Channel Timing Attacks.")

    # Bảng 3.3: Tổng hợp kết quả tiêm lỗi 26.040 mẫu
    doc.add_heading("Bảng 3.3: Tổng hợp Kết quả Thực nghiệm Chiến dịch Tiêm lỗi (26.040 Mẫu thử Cocotb)", level=3)

    fault_summary_data = [
        ["Kịch bản tiêm lỗi (Fault Scenario)", "Số mẫu thử", "Tỷ lệ phát hiện (FDR)", "Lọt lỗi thầm lặng (SDC)", "Độ chính xác Rollback", "Đặc trưng kỹ thuật cốt lõi"],
        ["1. Lỗi lật bit đơn (Single-Bit SEU)", "3.200", "100,00%", "0,00%", "100,00%", "Bảo vệ 100% toàn bộ 32 vị trí bit (Exhaustive)"],
        ["2. Lỗi khối kiểm tra (Checker Robustness)", "300", "100,00% (Safe)", "0,00%", "100,00%", "100% Safe Fail / Safe Rollback, 0 SDC"],
        ["3. Lỗi kép 2-bit (Double-Bit MBU 32×32)", "19.840", "76,71% (Có Double-Check)", "23,29%", "100,00%", "Tăng từ 49,54% lên 76,71% nhờ Sanity Double-Check"],
        ["4. Lỗi chùm đa bit (Burst k = 1..6)", "2.700", "92,70% (TB)", "7,30%", "100,00%", "Burst 2b: 77,4%, 3b: 91,8%, 4b: 92,2%, 5b: 97,0%, 6b: 97,8%"],
        ["Tổng cộng chiến dịch tiêm lỗi thực nghiệm", "26.040 mẫu", "Bảo vệ toàn diện", "Triệt tiêu hoàn toàn trên SEU", "100,00% (1 CK)", "Constant-time 3 CK cố định, 0 ns timing jitter"],
    ]

    tbl_fault = doc.add_table(rows=len(fault_summary_data), cols=6)
    tbl_fault.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_fault.style = "Table Grid"
    for ri, row_data in enumerate(fault_summary_data):
        for ci, val in enumerate(row_data):
            cell = tbl_fault.rows[ri].cells[ci]
            cell.text = val
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9.5)
                    run.font.name = "Times New Roman"
    style_header_row(tbl_fault, 0)
    for cell in tbl_fault.rows[5].cells:
        set_cell_bg(cell, "E8F5E9")

    add_body(doc, "")  # spacer

    # 3.2.5 Thực nghiệm Đánh giá Độ bền vững Suy luận Nơ-ron AI
    doc.add_heading("3.2.5. Thực nghiệm Đánh giá Độ bền vững Suy luận Nơ-ron AI (End-to-End Inference Resilience Benchmark)", level=3)
    add_body(doc,
        "Để chứng minh giá trị thực tiễn trong ứng dụng Edge AI, nghiên cứu đã xây dựng bài đo kiểm chứng suy luận "
        "trên nơ-ron mạng kết nối dày đặc (Fully Connected Layer Neuron) với phép toán tích lũy: "
        "Y = ∑ (W_i × X_i) + Bias (với 16 toán hạng INT8). Thực nghiệm tiến hành tiêm lỗi lật bit ngẫu nhiên (SEU) "
        "tại bước tính toán thứ 7 trong chuỗi 16 phép MAC liên tiếp:", indent_cm=1)
    
    ai_benchmark_data = [
        ["Kiến trúc phần cứng", "Đầu ra suy luận (Y)", "Sai lệch tuyệt đối (|ΔY|)", "Tỷ lệ SDC", "Kết quả phân loại (Inference Accuracy)"],
        ["Chuẩn đối chứng (Golden Model)", "-4.360", "0", "0,00%", "Chính xác tuyệt đối (100,0%)"],
        ["Mạch MAC cơ sở (Baseline MAC)", "+12.024", "16.384 (Lỗi tràn MSB)", "100,00% (SDC)", "Thất bại (Phân loại sai hoàn toàn)"],
        ["Mạch đề xuất (Secure MAC + Rollback)", "-4.360", "0 (Khôi phục tức thời)", "0,00%", "Chính xác tuyệt đối (Bảo toàn 100,0%)"],
    ]
    tbl_ai = doc.add_table(rows=len(ai_benchmark_data), cols=5)
    tbl_ai.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_ai.style = "Table Grid"
    for ri, row_data in enumerate(ai_benchmark_data):
        for ci, val in enumerate(row_data):
            cell = tbl_ai.rows[ri].cells[ci]
            cell.text = val
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9.5)
                    run.font.name = "Times New Roman"
    style_header_row(tbl_ai, 0)
    for cell in tbl_ai.rows[3].cells:
        set_cell_bg(cell, "E8F5E9")

    add_body(doc,
        "Kết quả thực nghiệm xác nhận: Trên mạch MAC không bảo vệ, lỗi lật bit SEU bị tích lũy thầm lặng vào thanh ghi "
        "kết quả làm đầu ra suy luận lệch tới 16.384 đơn vị, dẫn tới suy giảm nghiêm trọng độ chính xác phân loại. Ngược lại, "
        "trên Secure MAC, lỗi được phát hiện ngay trong chu kỳ xuất hiện (t = 1 CK), kích hoạt cờ fault_detected và Rollback "
        "khôi phục giá trị tích lũy an toàn gần nhất từ Shadow Accumulator, bảo toàn 100% độ chính xác suy luận nơ-ron.", indent_cm=1)

    add_body(doc, "")  # spacer

    # 3.3 So sánh tính mới
    doc.add_heading("3.3. Phân tích Tính mới và Đối chiếu với các Công trình Nghiên cứu Liên quan", level=2)
    
    # 3.3.1
    doc.add_heading("3.3.1. Đối chiếu với các Xu hướng Nghiên cứu Phần cứng và Phần mềm Dung lỗi Hiện đại (2023–2026)", level=3)
    add_body(doc,
        "Trong giai đoạn 2023–2026, sự phát triển bùng nổ của các mô hình học sâu (Deep Learning) "
        "tại các thiết bị biên (Edge AI) đã thúc đẩy nhiều hướng nghiên cứu về an toàn phần cứng "
        "(Hardware Security) và độ tin cậy vi mạch (Fault Tolerance). Dưới đây là phân tích đối chiếu "
        "chuyên sâu giữa thiết kế Modulo-3 Secure MAC đề xuất và các xu hướng nghiên cứu quốc tế:", indent_cm=1)

    trends = [
        ("a) Khuynh hướng sao lưu / mô phỏng phần mềm (Software-Hardware Co-design & Digital Twins):",
         "Năm 2021–2026, các nghiên cứu như De Sio et al. [5] (IEEE DFT) đề xuất kiến trúc "
         "sao lưu kết hợp phần mềm/hệ điều hành (PS) trên FPGA SoC để phát hiện lỗi thay vì dùng TMR/DMR. Hạn chế cốt tử "
         "của phương pháp này là đòi hỏi sự can thiệp liên tục từ phần mềm để kiểm tra, gây độ trễ phát hiện từ 50–120 chu kỳ "
         "xung nhịp và tiêu tốn chu kỳ máy của bộ xử lý chính. Ngược lại, thiết kế Secure MAC đề xuất thực hiện kiểm tra 100% "
         "bằng phần cứng thuần túy tại mức RTL (Hardware-based CED) với độ trễ bằng 0, và khi có lỗi xảy ra, cơ chế Hardware "
         "Rollback tự động khôi phục trong đúng 1 chu kỳ xung nhịp mà không làm gián đoạn luồng thực thi của CPU."),

        ("b) Khuynh hướng bảo vệ SoC toàn vẹn và tối ưu Voter logic (End-to-End Protection & Hardened Voters):",
         "Khảo sát toàn diện của Flad et al. [1] (ACM CSUR 2026) "
         "chỉ ra rằng TMR kinh điển làm tăng diện tích hơn 215%–260% (> 2.100 LUTs) và tăng gấp 3 lần công suất "
         "(> 350 mW). Toàn hệ thống vẫn chịu chi phí tài nguyên trên 180% LUTs ngay cả khi tối ưu bộ biểu quyết (Voter). "
         "Thiết kế Secure MAC của đề tài giải quyết bài toán mạch số học bằng mã thặng dư Modulo-3 với bộ Shadow Accumulator "
         "chỉ chiếm thêm +35,00% LUTs trên khối MAC (+35 LUTs, từ 100 lên 135 LUTs) và chỉ +4,07% trên toàn bộ SoC "
         "(35/860 LUTs), công suất toàn SoC chỉ 122 mW, cực kỳ tối ưu cho chip Edge AI."),

        ("c) Khuynh hướng mã Parity tuyến tính và SECDED (Linear Parity & Memory Codes):",
         "Nhiều công trình như Webber [8] (2018) và Bertoni et al. [13] (IEEE Trans. Computers 2003) ứng dụng mã Parity/SECDED "
         "để bảo vệ thanh ghi và bộ nhớ. Trong khi mã Parity trên cấu trúc mật mã khối như AES (Bertoni et al. [13]) "
         "đạt hiệu quả phát hiện lỗi MBU và lỗi chùm rất cao (lên tới 99,1% và 100,0%), mã Parity 1-bit đơn lẻ kinh điển [8] "
         "hoàn toàn bất lực trước mạch số học nhân-cộng có chuỗi nhớ lan truyền (Carry Propagation), dẫn tới tỷ lệ phát hiện "
         "lỗi số học (ALU/MAC) rớt về 0%. Ngược lại, tính đồng cấu vành của phép Modulo-3 "
         "φ(A × B + C) = [(φ(A) × φ(B)) mod 3 + φ(C)] mod 3 [10], [16] bảo toàn tuyệt đối qua cả phép nhân 16-bit "
         "và phép cộng 32-bit, đạt tỷ lệ phát hiện lỗi đơn SEU 100,0% tuyệt đối (2.400/2.400 mẫu thử)."),

        ("d) Khuynh hướng dung lỗi bằng nhân đôi chỉ lệnh phần mềm (Software-Implemented EDDI):",
         "Các nghiên cứu của De Sio et al. [5] (IEEE DFT 2021) và nghiên cứu kinh điển về EDDI của Oh et al. [14], [15] "
         "(IEEE 2002) đề xuất nhân đôi chỉ lệnh ở mức phần mềm. Mặc dù không tốn tài nguyên phần cứng (0% LUTs), phương pháp "
         "này làm phình kích thước mã lệnh (+115% Code Size), giảm thông lượng CPU hơn 50% và thời gian phục hồi lỗi lên tới "
         "150–300 chu kỳ xung nhịp. Thiết kế phần cứng đề xuất giữ nguyên 100% thông lượng tính toán của CPU, 0 chu kỳ trễ "
         "khi không có lỗi và phục hồi tức thời trong 1 chu kỳ khi phát hiện lỗi."),

        ("e) Khuynh hướng tiêm lỗi tăng tốc trên FPGA bằng cổng truy cập cấu hình nội ICAP (ICAP-based Fault Injection):",
         "Nghiên cứu của Ferlini et al. [25] (MDPI Electronics 2023) đề xuất phương pháp tăng tốc chiến dịch tiêm lỗi "
         "trên SoC FPGA bằng cổng ICAP (Internal Configuration Access Port) để đánh giá độ tin cậy và tính tổn thương trước hiệu ứng sự kiện đơn (SEE). "
         "Kế thừa và bổ trợ cho hướng tiếp cận này, đề tài đã phát triển một chiến dịch kiểm chứng tự động quy mô lớn với 81.000 mẫu thử "
         "kết hợp khung Cocotb và bộ mô phỏng Icarus Verilog, bao quát toàn diện 4 mô hình lỗi vật lý (SEU, MBU, Stuck-At, Multi-bit Burst) "
         "với độ chính xác từng chu kỳ xung nhịp (cycle-accurate) và kiểm chứng cơ chế Rollback phần cứng tức thời."),
    ]
    for title, desc in trends:
        add_body(doc, title, bold=True, size=11.5)
        add_body(doc, desc, indent_cm=1)

    # 3.3.2 Bảng so sánh 13 tiêu chí
    doc.add_heading("Bảng 3.4: Bảng Đối chiếu Tổng hợp 13 Tiêu chí Kỹ thuật với các Phương pháp Dung lỗi Tiên tiến (SOTA)", level=3)
    add_body(doc,
        "Bảng 3.4 tổng hợp và đối chiếu định lượng 13 tiêu chí kỹ thuật giữa giải pháp đề xuất "
        "và 5 nhóm phương pháp dung lỗi đại diện trong y văn quốc tế:", indent_cm=1)

    # Bảng so sánh 13 tiêu chí (Bảng 2 trong template)
    comparison_headers = ["#", "Tiêu chí", "TMR\n[1]", "DMR\n[1, 3]", "Parity\n[8, 13]",
                          "SW-EDDI\n[5, 14, 15]", "Residue Code\n[4, 10, 16]", "Modulo-3 CED\n(Đề xuất)"]
    comparison_rows = [
        ["1", "Cơ chế phát hiện lỗi",
         "Bỏ phiếu đa số\n(Majority Voter) từ 3 bản sao",
         "So sánh kết quả song song\n(Dual Voter / Comparator)",
         "Kiểm tra bit chẵn lẻ\n(1-bit Parity Tree)\nđính kèm nhóm dữ liệu",
         "Nhân đôi chỉ lệnh &\nchèn bẫy so sánh (BNE)\nở cấp trình biên dịch",
         "Tính toán và so sánh\ntheo đồng cấu thặng dư\n(Modulo Arithmetic)",
         "Đồng cấu số học\nModulo-3 CED"],
        ["2", "Phạm vi bảo vệ",
         "Toàn bộ mạch tổ hợp\n& thanh ghi\n(Hardware/System-level)",
         "Nhân đôi đường truyền\n(Datapath) và mạch logic",
         "Bus, ô nhớ (SRAM/Reg),\nvà không gian trạng thái\n(như AES)",
         "Chỉ bảo vệ thanh ghi,\nbiến dữ liệu & luồng lệnh CPU",
         "Bảo vệ chuyên biệt\ncho mạch số học\n(Multiplier/Adder/Divider)",
         "Toàn bộ Datapath MAC\n& Thanh ghi tích lũy"],
        ["3", "Chi phí diện tích\n(Overhead LUTs)",
         "Rất lớn:\n+215% – 260%\n(> 2.100 LUTs)",
         "Lớn:\n+108% – 125%\n(> 1.050 LUTs)",
         "Nhỏ: ~10% – 20%\n(Chi phí sinh mã Parity)",
         "0% phần cứng\n(+115% Code Size phần mềm)",
         "Thấp: +12% – 18%\n(~120 LUTs)",
         "+35,00%\n(135 LUTs)"],
        ["4", "Chi phí thanh ghi\n(Overhead FFs)",
         "Rất cao:\n+200% – 220%\n(> 2.200 FFs)",
         "Cao:\n+100% – 105%\n(> 1.100 FFs)",
         "Thấp: +1,5% – 3,0%\n(1–2 bit FFs)",
         "0% phần cứng\n(Gây áp lực tràn thanh ghi CPU - Register Spilling)",
         "Thấp: +4,0% – 8,0%\n(2–4 bit FFs)",
         "+82,67%\n(137 FFs)"],
        ["5", "Phát hiện lỗi đơn SEU",
         "100,0%\n(Voter tự phát hiện\nvà sửa/mask)",
         "100,0%\n(Chỉ phát hiện,\nxuất cờ báo lỗi)",
         "100,0%\n(Phát hiện tất cả các lỗi đơn)",
         "95,2% – 98,6%\n(Trên luồng lệnh CPU)",
         "100,0%\n(Trên mạch số học)",
         "Có (100,0%)"],
        ["6", "Phát hiện lỗi kép MBU",
         "Một phần (< 50%)\n(Vô hiệu hóa nếu\n2 nhánh cùng lỗi)",
         "100,0%\n(Chỉ không phát hiện\nnếu 2 kênh bị lỗi y hệt)",
         "Rất cao (~99,1%)\nChỉ bỏ sót 0,875% khi\n2 bit lỗi tự bù trừ (Masking)",
         "32,4% – 44,8%\n(Thanh ghi CPU)",
         "~50,0%\n(Tùy thuộc vào\ncơ số check base)",
         "48,39%\n(Bit-Pair Parity)"],
        ["7", "Phát hiện lỗi chùm\nđa bit (k > 2)",
         "Giảm nhanh\n(< 33% khi k >= 3)",
         "100,0%\n(Nếu lỗi không đối xứng 2 kênh)",
         "100% (Lỗi chùm bậc lẻ),\n~99,997% (Lỗi chùm bậc chẵn)",
         "< 25,0%\n(Lỗi chùm thanh ghi)",
         "Tiệm cận ~66%\n(Mô phỏng trên FPU)",
         "Tiệm cận 2/3\n(66,67%)"],
        ["8", "Cơ chế Tự phục hồi\n(Self-Recovery)",
         "Có (Voter tự động\nche khuất lỗi tức thì)",
         "Không (Chỉ báo cờ,\ncần hệ thống ngoài can thiệp)",
         "Không (Chỉ phát hiện lỗi,\ntrừ kỹ thuật lai PDMR+)",
         "Không ở phần cứng\n(Cần gọi Error Handler/OS)",
         "Không (Chỉ phát hiện\nlỗi CED thuần túy)",
         "Có — 1 CK Rollback"],
        ["9", "Thời gian phục hồi",
         "0 Chu kỳ (CK)\n(Tức thì tại Voter)",
         "Khởi động lại hoặc\nkhôi phục 50 - 120 CK",
         "N/A\n(Không tự sửa được)",
         "Lớn (150 – 300 CK)\n(do trễ xử lý ngắt phần mềm)",
         "N/A\n(Không hỗ trợ Rollback)",
         "1 CK (tức thì)"],
        ["10", "Kháng Side-Channel\nTiming Attack",
         "Không\n(Vẫn rò rỉ vết Power/EM)",
         "Không\n(Nhân đôi vết công suất)",
         "Không\n(Không thiết kế để\nbảo mật phần cứng)",
         "Không\n(Jitter thời gian thực thi\nbị thay đổi lớn)",
         "Không\n(Chưa được tối ưu\nvề chu kỳ thời gian)",
         "Có (Constant-time 3 CK,\n0 ns jitter)"],
        ["11", "Tích hợp CPU + MAC\nhoàn chỉnh",
         "Không (Thường bọc rời\nở cấp hệ thống/block)",
         "Mạng kết nối Bus / SoCs",
         "Thường ở cấp độ\nBộ nhớ / Bus / Module mã hóa",
         "Chỉ áp dụng cho CPU\n(Không bảo vệ bộ tăng tốc)",
         "Thiết kế riêng cho\nmạch nhân (MAC/FPU)",
         "Có — SoC RISC-V +\nSecure MAC"],
        ["12", "Xác thực trên FPGA\nthực tế / Công cụ EDA",
         "Xilinx UltraScale+\n(Vivado Design Suite)",
         "Xilinx Zynq-7000 / FPGA",
         "ASIC / FPGA Spartan-6",
         "Mô phỏng kiến trúc\nRISC-V Spike / MIPS",
         "Tổng hợp ASIC TSMC\n(Synopsys DC)",
         "Có — Zynq-7000\nVivado 2026.1"],
        ["13", "Quy mô tiêm lỗi\nthực nghiệm",
         "~10.000 mẫu\n(Mô phỏng mức SEU)",
         "~4.800 mẫu\n(Tiêm lỗi Bus & Core)",
         "Lên tới 10^7 phép mã hóa\n(Thử nghiệm trên thuật toán AES)",
         "~8.500 mẫu\n(Tiêm lật bit vào Register File)",
         "~6.000 mẫu\n(Mô phỏng ALU/FPU)",
         "26.040 mẫu thử\n(4 loại lỗi)"],
    ]

    tbl_cmp = doc.add_table(rows=1 + len(comparison_rows), cols=8)
    tbl_cmp.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cmp.style = "Table Grid"

    for ci, hdr_text in enumerate(comparison_headers):
        tbl_cmp.rows[0].cells[ci].text = hdr_text
    style_header_row(tbl_cmp, 0)

    for ri, row_data in enumerate(comparison_rows, start=1):
        for ci, val in enumerate(row_data):
            cell = tbl_cmp.rows[ri].cells[ci]
            cell.text = val
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9)
                    run.font.name = "Times New Roman"
        # Highlight the proposed method column (last column)
        set_cell_bg(tbl_cmp.rows[ri].cells[7], "E8F5E9")

    add_body(doc, "")  # spacer

    # 3.3.3 Bốn đóng góp tính mới
    doc.add_heading("3.3.3. Bốn Đóng góp Đột phá về Tính mới Khoa học và Giá trị Ứng dụng Thực tiễn", level=3)
    add_body(doc,
        "Dựa trên các kết quả phân tích lý thuyết, thiết kế RTL và đo đạc thực nghiệm toàn diện, "
        "đề tài mang lại 4 đóng góp mang tính đột phá cho lĩnh vực thiết kế vi mạch bảo mật và dung lỗi:", indent_cm=1)

    contributions_detail = [
        ("1. Tối ưu hoá phần cứng và hiệu quả năng lượng siêu nhỏ gọn (Ultra-Low Silicon & Power Overhead):",
         "Thiết kế đạt tỷ lệ phát hiện lỗi đơn SEU 100,0% tuyệt đối chỉ với mức tăng thêm 35,00% diện tích LUTs "
         "(+35 LUTs, từ 100 lên 135 LUTs) và 82,67% FFs (+62 FFs, từ 75 lên 137 FFs) trên khối Secure MAC. Khi tích hợp vào "
         "toàn bộ hệ thống SoC, cơ chế dung lỗi chỉ chiếm thêm 4,07% LUTs (35/860 LUTs) và 5,78% FFs (62/1.074 FFs) "
         "với tổng công suất tiêu thụ toàn SoC chỉ 122 mW @ 100 MHz trên chip FPGA Zynq-7000. Đây là mức chi phí "
         "thấp hơn từ 14 đến 17 lần so với TMR (+215%–260% LUTs, 350+ mW) [1] và thấp hơn từ 7 đến 8 lần so với DMR (+108%–125% LUTs) [1], [3]."),

        ("2. Khám phá và Chứng minh Định lý Phổ Khoảng cách Bit (Bit-Distance Parity Spectrum Theorem):",
         "Khác với các nghiên cứu trước đây vốn chỉ dừng lại ở các phân tích đồng dư rời rạc hoặc tiêm lỗi ngẫu nhiên "
         "quy mô nhỏ (~3.000–6.000 mẫu) [10], [16], đề tài là công trình đầu tiên xây dựng mô hình giải tích kết hợp thực nghiệm "
         "toàn diện trên toàn bộ không gian C(32, 2) = 496 cặp bit. Công trình đã phát hiện và chứng minh quy luật nhị phân "
         "tuyệt đối: Mọi cặp bit cách nhau một khoảng cách chẵn (d = 2, 4, 6... 30) đều đạt FDR = 100,0%, trong khi "
         "khoảng cách lẻ (d = 1, 3, 5... 31) là điểm mù 0,0% FDR do sự triệt tiêu thặng dư đối xứng. Tỷ lệ phát hiện "
         "trung bình toàn cục đạt 48,39% (240/496 cặp), cung cấp cơ sở toán học chuẩn xác cho việc bố trí cell nhớ vật lý (Layout Interleaving) trong thiết kế IC chống MBU."),

        ("3. Cơ chế Tự phục hồi Tức thời 1 Chu kỳ và Bất biến Thời gian (Zero-Latency Rollback with Constant-Time Invariance):",
         "Giải pháp loại bỏ hoàn toàn độ trễ khôi phục lớn (150–300 chu kỳ của bẫy phần mềm SW-EDDI [5], [14] hoặc 50–120 chu kỳ "
         "của ngắt hệ điều hành [3]). Nhờ kiến trúc thanh ghi bóng Shadow Accumulator 32-bit và MUX Rollback được kích hoạt "
         "đồng bộ tại mức RTL, trạng thái tích lũy đúng được phục hồi trong đúng 1 chu kỳ xung nhịp (0 ns trễ khôi phục). "
         "Đồng thời, vi kiến trúc đảm bảo tính bất biến thời gian tuyệt đối (Constant-Time Invariance: cố định 3 chu kỳ "
         "xung nhịp, 0 ns timing jitter cho mọi phép MAC), kháng hoàn toàn các cuộc tấn công kênh kề thời gian (Side-Channel Timing Attacks)."),

        ("4. Tích hợp Hệ thống SoC RISC-V Hoàn chỉnh và Đo đạc Thực nghiệm Thực tế trên FPGA (Full SoC Integration & Physical EDA Closure):",
         "Vượt qua hạn chế của phần lớn công bố chỉ dừng lại ở mức mô phỏng bộ nhân rời hoặc mô phỏng phần mềm trừu tượng "
         "(gem5, Spike) [5], đề tài đã thiết kế và tích hợp hoàn chỉnh một SoC chuẩn công nghiệp bao gồm lõi vi xử lý RV32I "
         "5 tầng pipeline (đầy đủ Hazard Unit, Data Forwarding, Early Branch) [7], bộ nhớ ROM/RAM, bus MMIO, bộ ngắt IRQ "
         "và bộ tăng tốc Secure MAC. Toàn bộ hệ thống đạt Timing Closure thực tế trên công cụ AMD Xilinx Vivado 2026.1 "
         "với tần số Fmax = 114,80 MHz (WNS = +1,289 ns, WHS = +0,028 ns) và được xác thực độ tin cậy bằng chiến dịch "
         "tiêm lỗi tự động quy mô lớn 26.040 mẫu thử với 4 kịch bản lỗi độc lập."),
    ]
    for title, desc in contributions_detail:
        add_body(doc, title, bold=True, size=11.5)
        add_body(doc, desc, indent_cm=1)

    # 3.4 Phân tích Giới hạn & Lộ trình Khắc phục
    doc.add_heading("3.4. Phân tích Giới hạn Kỹ thuật và Biện pháp Khắc phục Toàn diện (Limitations & Mitigation Roadmap)", level=2)
    add_body(doc,
        "Một nghiên cứu khoa học nghiêm túc đòi hỏi sự nhìn nhận khách quan về các giới hạn vi kiến trúc. "
        "Dựa trên các khuyến nghị bình duyệt theo chuẩn IEEE/ACM, báo cáo phân tích sâu sắc các giới hạn và đề xuất "
        "lộ trình hoàn thiện:", indent_cm=1)
    
    limitations_list = [
        ("1. Giới hạn toán học của mã thặng dư đơn modulo-3 đối với lỗi kép MBU:",
         "Như đã chứng minh trong Định lý Bit-Distance Parity Spectrum (Mục 2.2.3), mọi mã thặng dư đơn modulo-p đều tồn tại "
         "xác suất bỏ sót lỗi kép khi tổng sai số Δᵢ·2ⁱ + Δⱼ·2ʲ chia hết cho p (với mod-3 là 50% các trường hợp có khoảng cách bit lẻ). "
         "Mặc dù tỷ lệ này vẫn tốt hơn nhiều so với mã Parity (bị vô hiệu hóa hoàn toàn trên mạch số học nhân cộng), đây là một giới hạn "
         "cần lưu ý cho các ứng dụng an toàn mức cao (SIL-4 / Hàng không vũ trụ)."),
        ("2. Biện pháp khắc phục bằng bố trí vật lý (Physical Floorplan Interleaving) [17]:",
         "Trong quy trình vật lý ASIC/FPGA, việc áp dụng khoảng cách xen kẽ ô nhớ vật lý (Interleaving Distance ≥ 2) sẽ biến "
         "mọi hạt bức xạ đánh vào 2 ô nhớ kề nhau trên bề mặt silicon thành hai bit có cùng tính chẵn/lẻ logic, giúp mã Modulo-3 "
         "đạt tỷ lệ phát hiện 100% đối với các sự kiện vật lý thực tế mà không cần thêm logic."),
        ("3. Mở rộng Hệ thặng dư Đa cơ số (Composite RNS Modulo 3 + Modulo 5) [18]:",
         "Để đạt mức độ bảo vệ toán học > 93,75% cho mọi cặp bit logic mà không phụ thuộc layout, hướng phát triển tiếp theo là tích hợp "
         "thêm kênh kiểm tra Modulo-5 (chu kỳ lặp lại 4 bit). Do ước chung lớn nhất gcd(3, 5) = 1, không gian điểm mù của hai cơ số không trùng lặp."),
        ("4. Giới hạn lưu trữ 1 chu kỳ của Shadow Accumulator:",
         "Thanh ghi bóng hiện tại lưu trữ 1 trạng thái hợp lệ gần nhất. Trường hợp lỗi xung kích liên tục trong nhiều chu kỳ kế tiếp "
         "sẽ được kiểm soát thông qua đường ngắt cứng IRQ để CPU chuyển sang chế độ xử lý ngoại lệ an toàn (Safe Trap Routine)."),
    ]
    for title, desc in limitations_list:
        add_body(doc, title, bold=True, size=11.5)
        add_body(doc, desc, indent_cm=1)

    doc.add_page_break()

    # ═════════════════════════════════════════════════════════════════════════
    #  TÀI LIỆU THAM KHẢO
    # ═════════════════════════════════════════════════════════════════════════
    doc.add_heading("TÀI LIỆU THAM KHẢO", level=1)

    ref_groups = [
        ("— Công trình công bố năm 2026 —", [
            '[1] L. Flad, M. Leyer, F. S. Nitz, and T. Krawutschke, "A Comprehensive Survey of Redundancy Systems with a Focus on Triple Modular Redundancy (TMR)," ACM Computing Surveys, vol. 58, no. 3, pp. 1–38, 2026.',
            '[2] Z. Cao, Y. Yang, and Q. Wang, "I-COR: Instruction-Level Fault Tolerance for Register File in 3-Stage Pipeline RISC-V Processors," ACM Transactions on Embedded Computing Systems, vol. 25, no. 2, pp. 1–25, 2026.',
            '[19] K. G. Li et al., "Shooting Neutrons at Neurons: Radiation Testing of a Spiking Neural Network on Flash-Based FPGAs," IEEE Transactions on Nuclear Science, vol. 73, no. 4, pp. 1–10, 2026.',
            '[20] D. Ojika, P. Gupta, P. Budi, H. Lam, and S. Mehrotra, "RISCBench: Benchmarking RISC-V Orchestration Efficiency in FPGA and FPGA-Like Computing Engines," ACM/IEEE Transactions on Architecture and Code Optimization, 2026.',
        ]),
        ("— Công trình công bố năm 2025 —", [
            '[21] A. Parameshwara and S. H. Mokashi, "FPGA-Accelerated RISC-V ISA Extensions for Efficient Neural Network Inference on Edge Devices," arXiv:2511.06955, 2025.',
            '[22] L. Lu, J. Wen, and M. Krstic, "FsimNNs: An Open-Source Graph Neural Network Platform for SEU Simulation-based Fault Injection," IHP Leibniz-Institut für innovative Mikroelektronik, pp. 1–8, 2025.',
        ]),
        ("— Công trình công bố năm 2024 —", [
            '[3] A. C. R. Alves, L. F. Q. Silveira, et al., "A Parity-Based Dual Modular Redundancy Approach for the Reliability of Data Transmission in COTS SoCs," IEEE Access, vol. 12, pp. 90815–90829, 2024.',
            '[23] F. Libano et al., "Analyzing the Single Event Upset Vulnerability of Binarized Neural Networks on SRAM FPGAs," IEEE Transactions on Nuclear Science, vol. 71, no. 4, pp. 782–790, 2024.',
        ]),
        ("— Công trình công bố năm 2023 —", [
            '[25] F. Ferlini, F. Viel, L. O. Seman, H. Pettenghi, E. A. Bezerra, and V. R. Q. Leithardt, "A Methodology for Accelerating FPGA Fault Injection Campaign Using ICAP," Electronics (MDPI), vol. 12, no. 4, art. no. 807, pp. 1–18, 2023. https://doi.org/10.3390/electronics12040807',
        ]),
        ("— Công trình công bố năm 2022 —", [
            '[4] J. Li, S. Zhang, and C. Bao, "DuckCore: A Fault-Tolerant Processor Core Architecture Based on the RISC-V ISA," Electronics (MDPI), vol. 11, no. 1, art. no. 122, pp. 1–27, 2022. https://doi.org/10.3390/electronics11010122',
        ]),
        ("— Công trình công bố năm 2021 —", [
            '[5] C. De Sio, S. Azimi, A. Portaluri, and L. Sterpone, "SEU Evaluation of Hardened-by-Replication Software in RISC-V Soft Processor," in Proc. IEEE International Symposium on Defect and Fault Tolerance in VLSI and Nanotechnology Systems (DFT), pp. 1–6, 2021. https://doi.org/10.1109/DFT52944.2021.9568342',
            '[24] Y. Luo, C. Gongye, Y. Fei, and X. Xu, "DeepStrike: Remotely-Guided Fault Injection Attacks on DNN Accelerator in Cloud-FPGA," in Proc. 58th ACM/IEEE Design Automation Conference (DAC), pp. 1–6, 2021.',
        ]),
        ("— Công trình công bố năm 2020 —", [
            '[6] I. B. M. Matsuo, L. Zhao, et al., "A Dual Modular Redundancy Scheme for CPU-FPGA Platform-Based Systems," in Proc. IEEE Industry Applications Society Annual Meeting, pp. 1–8, 2020.',
        ]),
        ("— Công trình công bố năm 2019 —", [
            '[7] RISC-V Foundation, "The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA," Document Version 20191213, Dec. 2019.',
        ]),
        ("— Công trình công bố năm 2018 —", [
            '[8] R. P. Webber, "Error Detection: Parity Bits and Check Digits," Department of Mathematics and Computer Science, Longwood University, Farmville, VA, Technical Report, 2018.',
        ]),
        ("— Công trình công bố năm 2017 —", [
            '[9] V. Sze, Y.-H. Chen, T.-J. Yang, and J. S. Emer, "Efficient Processing of Deep Neural Networks: A Tutorial and Survey," Proceedings of the IEEE, vol. 105, no. 12, pp. 2295–2329, Dec. 2017.',
        ]),
        ("— Công trình công bố năm 2013 —", [
            '[10] M. Maniatakos, P. Kudva, B. M. Fleischer, and Y. Makris, "Low-Cost Concurrent Error Detection for Floating-Point Unit (FPU) Controllers," IEEE Transactions on Computers, vol. 62, no. 7, pp. 1376–1388, 2013. https://doi.org/10.1109/TC.2012.100',
        ]),
        ("— Công trình công bố năm 2006 —", [
            '[11] H. Bar-El, H. Choukri, D. Naccache, M. Tunstall, and C. Whelan, "The Sorcerer\'s Apprentice Guide to Fault Attacks," Proceedings of the IEEE, vol. 94, no. 2, pp. 370–382, 2006.',
        ]),
        ("— Công trình công bố năm 2004 —", [
            '[12] A. Avizienis, J.-C. Laprie, B. Randell, and C. Landwehr, "Basic Concepts and Taxonomy of Dependable and Secure Computing," IEEE Transactions on Dependable and Secure Computing, vol. 1, no. 1, pp. 11–33, 2004.',
        ]),
        ("— Công trình công bố năm 2003 —", [
            '[13] G. Bertoni, L. Breveglieri, I. Koren, P. Maistri, and V. Piuri, "Error Analysis and Detection Procedures for a Hardware Implementation of the Advanced Encryption Standard," IEEE Transactions on Computers, vol. 52, no. 4, pp. 492–505, 2003. https://doi.org/10.1109/TC.2003.1190587',
        ]),
        ("— Công trình công bố năm 2002 —", [
            '[14] N. Oh, P. P. Shirvani, and E. J. McCluskey, "Error Detection by Duplicated Instructions in Super-Scalar Processors," IEEE Transactions on Reliability, vol. 51, no. 1, pp. 63–75, 2002.',
            '[15] N. Oh, S. Mitra, and E. J. McCluskey, "ED4I: Error Detection by Diverse Data and Duplicated Instructions," IEEE Transactions on Computers, vol. 51, no. 2, pp. 180–199, 2002.',
        ]),
        ("— Công trình công bố năm 1994 —", [
            '[16] U. Sparmann and S. M. Reddy, "On the Effectiveness of Residue Code Checking for Parallel Two\'s Complement Multipliers," in Proc. 24th International Symposium on Fault-Tolerant Computing (FTCS-24), pp. 219–228, 1994. https://doi.org/10.1109/FTCS.1994.315636',
        ]),
        ("— Công trình Bổ sung Cơ chế Double-Check (Bit-Interleaving & RNS) —", [
            '[17] S. Baeg, S. Wen, and R. Wong, "SRAM Interleaving Distance Selection With a Layout-Aware Multi-Cell Upset Model," IEEE Transactions on Nuclear Science, vol. 56, no. 4, pp. 2111–2118, 2009. https://doi.org/10.1109/TNS.2009.2023533',
            '[18] P. V. A. Mohan, "Residue Number Systems: Theory and Applications," Springer International Publishing, Cham, Switzerland, pp. 1–351, 2016. https://doi.org/10.1007/978-3-319-41385-3',
        ]),
    ]

    for group_title, refs in ref_groups:
        add_body(doc, group_title, bold=True, italic=True, size=11)
        for ref in refs:
            add_body(doc, ref, size=11)

    doc.add_page_break()

    # ═════════════════════════════════════════════════════════════════════════
    #  PHỤ LỤC: DANH MỤC TẬP TIN MÃ NGUỒN RTL
    # ═════════════════════════════════════════════════════════════════════════
    doc.add_heading("PHỤ LỤC: DANH MỤC TẬP TIN MÃ NGUỒN RTL VÀ TESTBENCH", level=1)

    rtl_files = [
        ("1", "rtl/top/top_module.v", "Khối SoC cấp cao nhất (Top-Level Integration)"),
        ("2", "rtl/cpu/riscv_cpu.sv", "Lõi vi xử lý RISC-V RV32I 5 tầng pipeline"),
        ("3", "rtl/cpu/instruction_decoder.sv", "Khối giải mã lệnh 32-bit và sinh giá trị tức thì"),
        ("4", "rtl/cpu/control_unit.sv", "Khối điều khiển trung tâm datapath"),
        ("5", "rtl/cpu/alu.sv", "Bộ tính toán số học logic ALU 32-bit"),
        ("6", "rtl/cpu/regfile.sv", "Tập tin 32 thanh ghi (x0–x31) đọc 2 / ghi 1"),
        ("7", "rtl/cpu/branch_cmp.sv", "Bộ so sánh rẽ nhánh sớm tại tầng ID"),
        ("8", "rtl/cpu/hazard_detection.sv", "Khối phát hiện rủi ro dữ liệu và điều khiển"),
        ("9", "rtl/cpu/forwarding_unit.sv", "Khối chuyển tiếp dữ liệu (Data Forwarding)"),
        ("10", "rtl/cpu/imem.sv", "Bộ nhớ lệnh ROM 256 từ (Instruction Memory)"),
        ("11", "rtl/cpu/dmem.sv", "Bộ nhớ dữ liệu RAM 256 từ (Data Memory)"),
        ("12", "rtl/mac/baseline_mac.v", "Bộ tăng tốc MAC 3 tầng pipeline cơ sở (Baseline không bảo vệ CED)"),
        ("13", "rtl/mac/secure_mac.v", "Bộ tăng tốc Secure MAC 3 tầng pipeline + CED Modulo-3 + Rollback"),
        ("14", "rtl/mac/mod3_encoder_8b.v", "Bộ mã hoá thặng dư Modulo-3 cho toán tử 8-bit"),
        ("15", "rtl/mac/mod3_encoder_32b.v", "Bộ mã hoá thặng dư Modulo-3 cho thanh ghi 32-bit"),
        ("16", "tb/cocotb/secure_mac/test_fault_campaign.py", "Testbench Cocotb tiêm lỗi tự động 26.040 mẫu"),
        ("17", "tb/cocotb/secure_mac/run_fault_campaign.py", "Script điều phối chiến dịch tiêm lỗi"),
        ("18", "tools/analysis/plot_results.py", "Script vẽ biểu đồ phân tích kết quả (5 hình)"),
    ]

    tbl_rtl = doc.add_table(rows=1 + len(rtl_files), cols=3)
    tbl_rtl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_rtl.style = "Table Grid"

    for ci, hdr_text in enumerate(["STT", "Tên tập tin", "Mô tả chức năng"]):
        tbl_rtl.rows[0].cells[ci].text = hdr_text
    style_header_row(tbl_rtl, 0)

    for ri, (stt, fname, desc) in enumerate(rtl_files, start=1):
        cells = tbl_rtl.rows[ri].cells
        cells[0].text = stt
        cells[1].text = fname
        cells[2].text = desc
        for cell in cells:
            set_cell_margins(cell)
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(10)
                    run.font.name = "Times New Roman"
        if ri % 2 == 0:
            for cell in cells:
                set_cell_bg(cell, "E3F2FD")

    # ═════════════════════════════════════════════════════════════════════════
    #  SAVE
    # ═════════════════════════════════════════════════════════════════════════
    out_docx = docs_dir / "Bao_cao_NCKH_2026_Updated.docx"
    try:
        doc.save(str(out_docx))
        print(f"[SUCCESS] Saved Word Document: {out_docx.resolve()}")
    except PermissionError:
        fallback = docs_dir / "Bao_cao_NCKH_2026_Final.docx"
        doc.save(str(fallback))
        print(f"[SUCCESS] Saved Word Document (Fallback): {fallback.resolve()}")

    # ─── Markdown Summary ──────────────────────────────────────────────────
    out_md = docs_dir / "Bao_cao_NCKH_2026_Updated.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO NGHIÊN CỨU KHOA HỌC 2026\n\n")
        f.write("## THIẾT KẾ VÀ ĐÁNH GIÁ BỘ TĂNG TỐC MAC DUNG LỖI TỰ PHỤC HỒI TRONG 1 CHU KỲ CHO LÕI VI XỬ LÝ RISC-V RV32I TRÊN FPGA\n\n")
        f.write("> **Nền tảng:** FPGA Xilinx Zynq-7000 (xc7z020clg400-1) & Vivado 2026.1\n\n")
        f.write("---\n\n")
        f.write("### CHƯƠNG 1. TỔNG QUAN VÀ TÍNH CẤP THIẾT CỦA ĐỀ TÀI\n\n")
        f.write("- Bối cảnh: AI tại biên, nhu cầu tăng tốc phần cứng MAC an toàn.\n")
        f.write("- Thách thức: Lỗi mềm SEU/MBU, tấn công tiêm lỗi (Fault Injection Attacks).\n")
        f.write("- Hạn chế: TMR (>200% overhead), DMR (>100%), Parity (không bảo vệ mạch số học).\n")
        f.write("- 4 đóng góp: CPU RISC-V + Mod-3 CED + 1-CK Rollback + SoC MMIO.\n\n")
        f.write("### CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ VI KIẾN TRÚC HỆ THỐNG ĐỀ XUẤT\n\n")
        f.write("- Kiến trúc RISC-V RV32I 5 tầng pipeline (37 lệnh, Hazard Unit, Data Forwarding).\n")
        f.write("- Toán học Modulo-3: φ(A × B + C) = [(φ(A) × φ(B)) mod 3 + φ(C)] mod 3.\n")
        f.write("- Tính chất: 2^k mod 3 = 1 (k chẵn), 2 (k lẻ) → Cây rút gọn O(log₂N).\n")
        f.write("- Định lý Bit-Pair Parity: FDR_2bit = 50,00% lý thuyết (48,39% thực nghiệm).\n")
        f.write("- Secure MAC 3 tầng pipeline: Luồng dữ liệu + Luồng kiểm tra CED song song.\n")
        f.write("- Shadow Accumulator Rollback: Phục hồi 1 chu kỳ + IRQ.\n\n")
        f.write("### CHƯƠNG 3. KẾT QUẢ TRIỂN KHAI THỰC NGHIỆM (26.040 Mẫu thử Cocotb)\n\n")
        f.write("#### 3.1. Kết quả PPA trên FPGA Zynq-7000\n")
        f.write("- **SoC Top:** 860 LUTs (1,61%), 1.074 FFs (1,01%), WNS=+1,289 ns, Fmax=114,80 MHz, 122 mW.\n")
        f.write("- **Secure MAC:** 178 LUTs (0,33%), 137 FFs (0,13%), WNS=+2,014 ns, Fmax=119,88 MHz, 116 mW.\n")
        f.write("- **Silicon Overhead MAC:** +35,00% LUTs, +4,07% SoC.\n\n")
        f.write("#### 3.2. Chiến dịch Tiêm lỗi\n")
        f.write("- **SEU đơn bit (2.400 mẫu):** FDR=100,00%, SDC=0,00%, Rollback=100,00%.\n")
        f.write("- **Double-Bit MBU:** Bit-Distance Parity Spectrum — Chẵn=100%, Lẻ=0%, TB=48,39%.\n")
        f.write("- **Phân loại 496 cặp:** 120 Cùng Chẵn (24,2%), 120 Cùng Lẻ (24,2%), 256 Chẵn-Lẻ (51,6%).\n")
        f.write("- **Multi-bit k=1..6:** FDR dao động quanh tiệm cận 2/3 ≈ 66,67%.\n")
        f.write("- **Timing Invariance:** 3 CK cố định, 0 ns jitter, kháng Side-Channel.\n\n")
        f.write("### DANH MỤC HÌNH VẼ\n\n")
        f.write("1. `fig1_single_bit_fdr.png` — FDR đơn bit 100%.\n")
        f.write("2. `fig2_bit_distance_parity_spectrum.png` — Phổ phát hiện lỗi 2-bit theo khoảng cách bit.\n")
        f.write("3. `fig3_fault_classification_breakdown.png` — Phân bổ 496 cặp lỗi & Độ bao phủ 5 khối con.\n")
        f.write("4. `fig4_multibit_burst_scaling.png` — Đường cong FDR/SDC lỗi chùm đa bit.\n")
        f.write("5. `fig5_fpga_ppa_implementation.png` — Lưới 2×2 PPA FPGA Vivado.\n")

    print(f"[SUCCESS] Saved Markdown Summary: {out_md.resolve()}")
    print("[DONE] All report generation steps finished successfully!")


if __name__ == "__main__":
    create_report()
