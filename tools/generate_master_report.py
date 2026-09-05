"""
Master Script: Generate Complete Academic NCKH Report (.docx)
Strictly matching the user's image with an 8-column comparison table (13 criteria):
Columns: [#] [Tiêu chí so sánh] [TMR [6]] [DMR [7]] [Parity [9]] [SW-EDDI [14][16]] [Residue Code [10]] [Đề xuất: Mod-3 MAC + Rollback]
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

TEMPLATE_PATH = r"D:\NCKH\Bản thảo.docx"
OUT_PATH_1 = r"D:\NCKH\docs\Bao_cao_NCKH_Toan_Dien_2026.docx"
OUT_PATH_2 = r"D:\NCKH\docs\Bao_cao_NCKH_Chuan_Full_v2.docx"
OUT_PATH_3 = r"D:\NCKH\docs\Bao_cao_NCKH_16_References_Full.docx"

def add_page_number(run):
    """Inject dynamic PAGE XML field into footer run."""
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def set_footer_page_numbers(doc):
    """Set dynamic page numbers in all section footers."""
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.text = ""
        r1 = p.add_run("Trang ")
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(100, 100, 100)
        
        r_num = p.add_run()
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(10)
        r_num.font.color.rgb = RGBColor(100, 100, 100)
        add_page_number(r_num)
        
        r2 = p.add_run(" / ")
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGBColor(100, 100, 100)
        
        # NumPages
        r_total = p.add_run()
        r_total.font.name = "Times New Roman"
        r_total.font.size = Pt(10)
        r_total.font.color.rgb = RGBColor(100, 100, 100)
        fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
        instr = parse_xml(r'<w:instrText %s xml:space="preserve"> NUMPAGES </w:instrText>' % nsdecls('w'))
        fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
        fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
        r_total._r.append(fld1)
        r_total._r.append(instr)
        r_total._r.append(fld2)
        r_total._r.append(fld3)

def update_abbreviations_table(doc):
    """Update Table 0 with comprehensive 38 acronyms matching the project and local files."""
    tbl = doc.tables[0]
    
    # Remove existing rows except header
    for i in range(len(tbl.rows)-1, 0, -1):
        row = tbl.rows[i]
        tbl._tbl.remove(row._tr)
        
    hdr = tbl.rows[0].cells
    hdr[0].text = "Từ viết tắt"
    hdr[1].text = "Giải thích thuật ngữ chi tiết"
    for c in hdr:
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in c.paragraphs[0].runs:
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)

    abbreviations = [
        ("SoC", "System-on-Chip (Hệ thống hoàn chỉnh tích hợp trên một vi mạch duy nhất)"),
        ("RISC-V", "Reduced Instruction Set Computer - Architecture V (Kiến trúc tập lệnh mở thế hệ 5)"),
        ("RV32I", "RISC-V 32-bit Base Integer Instruction Set (Tập lệnh số nguyên 32-bit cơ sở chuẩn)"),
        ("ISA", "Instruction Set Architecture (Kiến trúc tập lệnh phần cứng vi xử lý)"),
        ("MAC", "Multiply-Accumulate (Phép tính nhân tích lũy: Y = A × B + C)"),
        ("Edge AI", "Edge Artificial Intelligence (Trí tuệ nhân tạo biên / Tính toán AI tại biên)"),
        ("DNN", "Deep Neural Network (Mạng nơ-ron học sâu)"),
        ("CNN", "Convolutional Neural Network (Mạng nơ-ron tích chập)"),
        ("FIA", "Fault Injection Attack (Tấn công tiêm lỗi vật lý chủ động)"),
        ("EMFI", "ElectroMagnetic Fault Injection (Tấn công tiêm lỗi bằng xung cảm ứng điện từ)"),
        ("SEU", "Single Event Upset (Lỗi lật bit đơn do bức xạ hạt ion hóa hoặc nhiễu nguồn)"),
        ("MBU", "Multiple-Bit Upset (Lỗi lật nhiều bit đồng thời do xung bức xạ mạnh)"),
        ("SDC", "Silent Data Corruption (Hỏng dữ liệu thầm lặng không phát sinh cảnh báo)"),
        ("CED", "Concurrent Error Detection (Phát hiện lỗi đồng thời trong chu kỳ tính toán)"),
        ("TMR", "Triple Modular Redundancy (Dự phòng phần cứng ba mô-đun với bộ bỏ phiếu đa số)"),
        ("DMR", "Dual Modular Redundancy (Dự phòng phần cứng hai mô-đun với bộ so sánh)"),
        ("PDMR", "Parity-based Dual Modular Redundancy (Dự phòng kép kết hợp kiểm tra chẵn lẻ)"),
        ("EDDI", "Error Detection by Duplicated Instructions (Phát hiện lỗi bằng nhân đôi chỉ lệnh)"),
        ("ED4I", "Error Detection by Diverse Data and Duplicated Instructions (Dung lỗi dữ liệu đa dạng)"),
        ("ABFT", "Algorithm-Based Fault Tolerance (Dung lỗi dựa trên cấu trúc thuật toán)"),
        ("SECDED", "Single Error Correction, Double Error Detection (Mã sửa 1 bit, phát hiện 2 bit)"),
        ("FDR", "Fault Detection Rate (Tỷ lệ phát hiện lỗi phần cứng đạt được)"),
        ("MMIO", "Memory-Mapped Input/Output (Vào/ra ánh xạ trực tiếp trong không gian địa chỉ bộ nhớ)"),
        ("IRQ", "Interrupt Request (Tín hiệu yêu cầu ngắt phần cứng khẩn cấp gửi CPU)"),
        ("ISR", "Interrupt Service Routine (Chương trình con phục vụ xử lý ngắt)"),
        ("ALU", "Arithmetic Logic Unit (Đơn vị tính toán số học và logic của CPU)"),
        ("FPU", "Floating-Point Unit (Đơn vị tính toán số học dấu chấm động)"),
        ("RTL", "Register Transfer Level (Mức thiết kế chuyển đổi thanh ghi khả tổng hợp)"),
        ("FPGA", "Field-Programmable Gate Array (Mảng cổng logic lập trình được dạng trường)"),
        ("LUT", "Look-Up Table (Bảng tra cứu logic đa ngõ vào trên FPGA)"),
        ("FF", "Flip-Flop (Phần tử nhớ thanh ghi đồng bộ 1-bit)"),
        ("PPA", "Power, Performance, Area (Bộ 3 chỉ số thiết kế: Công suất, Hiệu năng, Diện tích)"),
        ("WNS", "Worst Negative Slack (Độ dôi thời gian thiết lập tới hạn trong phân tích định thì STA)"),
        ("COTS", "Commercial Off-The-Shelf (Linh kiện điện tử thương mại sản xuất đại trà)"),
        ("UART", "Universal Asynchronous Receiver-Transmitter (Giao tiếp truyền nhận nối tiếp bất đồng bộ)"),
        ("GPIO", "General-Purpose Input/Output (Cổng vào/ra dữ liệu đa dụng điều khiển số)"),
        ("PC", "Program Counter (Thanh ghi con trỏ lệnh / Bộ đếm chương trình của CPU)"),
        ("Pipeline", "Đường ống xử lý lệnh 5 tầng: IF (Fetch), ID (Decode), EX (Execute), MEM (Memory), WB (Write-back)")
    ]

    for abbr, desc in abbreviations:
        row_cells = tbl.add_row().cells
        row_cells[0].text = abbr
        row_cells[1].text = desc
        
        p0 = row_cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p0.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r.bold = True
            
        p1 = row_cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p1.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)

def update_text_citations(doc):
    """Enrich paragraphs with citations strictly from local references [1] to [16]."""
    for p in doc.paragraphs:
        txt = p.text.strip()
        
        # 1.1 Sze [1], Li [12]
        if "Về mặt toán học, hơn 90% khối lượng tính toán" in txt:
            p.text = "Về mặt toán học, hơn 90% khối lượng tính toán trong các mạng nơ-ron tích chập (CNN), mạng nơ-ron truyền thẳng (DNN) và các mô hình Edge AI hiện đại tập trung vào các phép tích vô hướng ma trận (Dot Product) và phép nhân tích lũy (Multiply-Accumulate - MAC) [1], [12]:"
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)
                
        # 1.2 Bar-El [4], Avizienis [2]
        elif "Khác với các hệ thống máy chủ trong phòng lab" in txt:
            p.text = "Khác với các hệ thống máy chủ trong phòng lab được bảo vệ vật lý nghiêm ngặt, các thiết bị Edge AI thường xuyên triển khai tại môi trường biên khắc nghiệt, đối mặt với các nguy cơ tấn công tiêm lỗi vật lý chủ động (Fault Injection Attacks - FIA) [4] và hiện tượng nhiễu bức xạ tự nhiên:"
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)
                
        elif "Hậu quả nguy hiểm nhất là hiện tượng Hỏng dữ liệu thầm lặng (Silent Data Corruption" in txt:
            p.text = "Hậu quả nguy hiểm nhất là hiện tượng Hỏng dữ liệu thầm lặng (Silent Data Corruption - SDC) theo phân loại chuẩn tắc về độ tin cậy của Avizienis và cộng sự [2]. Lỗi phần cứng làm sai lệch một vài trọng số hoặc kết quả tích lũy có thể dẫn đến việc nhận dạng sai hoàn toàn đối tượng, gây hậu quả thảm khốc trong các ứng dụng an toàn nghiêm ngặt như xe tự hành hoặc thiết bị y tế."
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        # 1.3 Flad [6], Alves [7], IEEE [8], Webber [9], Bertoni [5], De Sio [13], Oh [14], [15], Cao [16]
        elif "Để chống lại lỗi phần cứng, các kỹ thuật dung lỗi kinh điển" in txt:
            p.text = "Để chống lại lỗi phần cứng, các kỹ thuật dung lỗi kinh điển đã được đề xuất rộng rãi trong y văn nhưng đều bộc lộ những điểm nghẽn nghiêm trọng khi áp dụng cho thiết bị biên:"
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        elif "Triple Modular Redundancy (TMR)" in txt and "Nhân bản 3 lần" in txt:
            p.text = "- Dự phòng phần cứng Ba mô-đun (Triple Modular Redundancy - TMR) [6], [16]: Nhân bản 3 lần toàn bộ mạch tính toán và sử dụng bộ bỏ phiếu đa số (Majority Voter). TMR chiếm dụng chi phí diện tích và tiêu thụ năng lượng cực lớn (> 200% - 300% overhead) [6], [16], hoàn toàn bất khả thi cho vi mạch Edge AI bị giới hạn năng lượng."
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        elif "Dual Modular Redundancy (DMR)" in txt and "Nhân bản 2 lần" in txt:
            p.text = "- Dự phòng phần cứng Hai mô-đun (Dual Modular Redundancy - DMR) [7], [8]: Nhân bản 2 lần mạch MAC và so sánh kết quả. DMR vẫn tăng diện tích hơn 100% và không có khả năng tự sửa lỗi (Fault Recovery) nếu không có cơ chế dừng CPU tính toán lại từ đầu."
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        elif "Mã kiểm tra chẵn lẻ (Parity)" in txt or "Parity / SECDED" in txt:
            p.text = "- Mã kiểm tra chẵn lẻ (Parity Code / SECDED) [5], [9]: Dù có chi phí phần cứng thấp, mã Parity tuyến tính chỉ bảo vệ được đường truyền dữ liệu (Bus) hoặc ô nhớ (RAM/Registers). Khi đi qua mạch số học nhân cộng có chuỗi nhớ lan truyền (Carry Ripple), tính chất Parity bị phá vỡ hoàn toàn và không thể phát hiện lỗi tính toán [9]."
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        elif "Dự phòng phần mềm (Software-level Redundancy)" in txt:
            p.text = "- Dự phòng phần mềm (Software-level Redundancy / SW-EDDI) [13], [14], [15]: Nhân bản chỉ lệnh hoặc chạy lặp lại thuật toán (ABFT) [14], [15]. Phương pháp này làm giảm 2-3 lần thông lượng xử lý của CPU và không ngăn chặn được các lỗi xung kích tức thời (Transient Glitches) trong thời gian thực [13]."
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        # Section 3.3 title and lead-in text matching image
        elif "2.8.4 Đối chiếu Định lượng Toàn diện" in txt or "3.3. Phân tích Tính mới" in txt:
            p.text = "3.3. Phân tích Tính mới và Đối chiếu với các Công trình Nghiên cứu Liên quan"
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(14)
                r.bold = True

        elif "Bảng 2.2: Đối chiếu định lượng toàn diện" in txt or "Bảng dưới đây so sánh 13 tiêu chí" in txt:
            p.text = "Bảng dưới đây so sánh 13 tiêu chí kỹ thuật giữa phương pháp đề xuất và các nhóm giải pháp khác:"
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        # 2.1 RISC-V Foundation [3], DuckCore [12], Cao [16]
        elif "Kiến trúc tập lệnh RISC-V (RV32I) là chuẩn tập lệnh mở" in txt:
            p.text = "Kiến trúc tập lệnh RISC-V (RV32I) là chuẩn tập lệnh mở không bản quyền được quản lý bởi RISC-V International [3]. Với cấu trúc tải/lưu (Load/Store) tinh gọn và không gian thanh ghi trực giao, RISC-V là nền tảng lý tưởng cho các vi xử lý chuyên dụng và nghiên cứu an toàn phần cứng tin cậy [12], [16]."
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

        # 2.2 Sparmann [10], Maniatakos [11]
        elif "Mã thặng dư số học Modulo-3 (Residue Code)" in txt and "thuộc lớp mã số học không tuyến tính" in txt:
            p.text = "Mã thặng dư số học Modulo-3 (Residue Code) thuộc lớp mã số học không tách rời (Non-separable Arithmetic Code) có lịch sử phát triển lâu đời trong lý thuyết máy tính tin cậy [10], [11]. Điểm đặc biệt của mã thặng dư là bảo toàn tính đồng cấu toán học qua cả hai phép toán cộng (+) và nhân (×):"
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(13)

def update_comparison_table_8_columns(doc):
    """
    Replace Table 2.2 with the EXACT 8-column layout shown in user image:
    Columns: [#] [Tiêu chí so sánh] [TMR [6]] [DMR [7]] [Parity [9]] [SW-EDDI [14][16]] [Residue Code [10]] [Đề xuất: Mod-3 MAC + Rollback]
    """
    old_tbl = doc.tables[2]
    
    # Table headers exactly matching image
    headers = [
        '#',
        'Tiêu chí\nso sánh',
        'TMR [6]',
        'DMR [7]',
        'Parity [9]',
        'SW-\nEDDI\n[14][16]',
        'Residue\nCode [10]',
        'Đề xuất:\nMod-3\nMAC +\nRollback'
    ]
    
    # 13 criteria rows across all 6 methods
    table_data = [
        [
            '1',
            'Cơ chế phát hiện lỗi',
            'Bỏ phiếu đa số (Majority Voter)',
            'So sánh kết quả song song (Dual Voter)',
            'Kiểm tra bit chẵn lẻ 1-bit',
            'Nhân đôi chỉ lệnh & chèn bẫy so sánh BNE',
            'Đồng cấu thặng dư (CED thuần túy)',
            'Đồng cấu số học Modulo-3 CED'
        ],
        [
            '2',
            'Phạm vi bảo vệ',
            'Toàn bộ mạch tổ hợp & thanh ghi',
            'Nhân đôi đường Datapath',
            'Chỉ bảo vệ Bus dữ liệu & ô nhớ',
            'Chỉ bảo vệ thanh ghi & luồng lệnh CPU',
            'Bảo vệ mạch tính toán số học',
            'Toàn bộ Datapath MAC & Thanh ghi tích lũy'
        ],
        [
            '3',
            'Chi phí diện tích (Overhead LUTs)',
            '> 200% – 300%\n(> 2.000 LUTs)',
            '> 100% – 110%\n(> 1.000 LUTs)',
            'Cực thấp\n(< 3% LUTs)',
            '0%\n(Thuần phần mềm)',
            '12% – 15%\n(Bộ Checker thặng dư)',
            '15,0%\n(135 LUTs cho Checker + Shadow)'
        ],
        [
            '4',
            'Chi phí thanh ghi (Overhead FFs)',
            '> 200% – 220%\n(> 2.200 FFs)',
            '> 100% – 105%\n(> 1.100 FFs)',
            'Rất thấp\n(1-2 bit FFs)',
            '0% phần cứng\n(Chiếm thanh ghi CPU)',
            '4% – 8%\n(2-4 bit FFs)',
            '42,7%\n(137 FFs cho Checkpoint)'
        ],
        [
            '5',
            'Ảnh hưởng trễ thực thi (Latency)',
            '0 chu kỳ\n(Tức thời qua Voter)',
            '0 chu kỳ\n(So sánh song song)',
            '0 chu kỳ',
            'Tăng 2,2x – 2,8x\n(Overhead 220%)',
            '0 chu kỳ\n(CED song song)',
            '0 chu kỳ\n(CED song song trong 1 cycle)'
        ],
        [
            '6',
            'Bảo vệ phép toán số học (Carry)',
            'Có\n(Nhân 3 khối)',
            'Có\n(Nhân 2 khối)',
            'KÉM\n(Bị phá vỡ qua Carry Ripple)',
            'KÉM\n(Không bắt được lỗi xung ALU)',
            'Tuyệt đối\n(Bảo toàn số học)',
            'Bảo vệ tuyệt đối\n(Đồng cấu toán học 100%)'
        ],
        [
            '7',
            'Tỷ lệ phát hiện lỗi đơn SEU (FDR)',
            '100,0%\n(Tự sửa lỗi)',
            '100,0%\n(Chỉ phát hiện)',
            '100,0%\n(Trên Bus dữ liệu)',
            '~90% – 95%\n(Tùy vị trí lệnh)',
            '100,00%',
            '100,00%\n(4.800/4.800 mẫu tiêm thử)'
        ],
        [
            '8',
            'Tỷ lệ phát hiện lỗi dính Stuck-At',
            '100,0%\n(Tự sửa lỗi)',
            '100,0%\n(Chỉ phát hiện)',
            '50,0%\n(Dính chẵn bit)',
            'Kém trên mạch số học MAC',
            '100,00%',
            '100,00%\n(6.400/6.400 mẫu tiêm thử)'
        ],
        [
            '9',
            'Tỷ lệ phát hiện lỗi kép Double-Bit',
            'Phụ thuộc layout',
            '50,0% – 75,0%',
            '0,00%\n(Bị triệt tiêu chẵn lẻ)',
            'Kém nếu lỗi cùng cặp thanh ghi',
            '50,00%\n(Lý thuyết Modulo)',
            '49,32%\n(Khớp Định lý Bit-Pair Parity)'
        ],
        [
            '10',
            'Tỷ lệ phát hiện lỗi xung rải (Burst)',
            'Tốt nếu độc lập',
            'Trung bình',
            '~50,0%',
            'Kém',
            '~66,67%\n(Ngưỡng 2/3)',
            '68,68%\n(Tiệm cận ngưỡng lý thuyết 2/3)'
        ],
        [
            '11',
            'Khả năng tự khôi phục khi có lỗi',
            'Tự sửa tức thời qua Voter',
            'Không tự sửa\n(Phải báo ngắt)',
            'Không tự sửa\n(Phải báo ngắt)',
            'Bẫy Exception trap phần mềm',
            'Không tự sửa\n(Chỉ phát hiện)',
            'Tự động khôi phục phần cứng (Rollback)'
        ],
        [
            '12',
            'Thời gian khôi phục lỗi (Recovery)',
            '0 chu kỳ\n(Trong cùng cycle)',
            '> 100 chu kỳ\n(CPU tính lại)',
            '> 100 chu kỳ\n(CPU tính lại)',
            '> 200 chu kỳ\n(Chạy lại hàm)',
            '> 100 chu kỳ\n(Nhờ CPU can thiệp)',
            'Đúng 1 chu kỳ xung nhịp\n(Shadow Accumulator)'
        ],
        [
            '13',
            'Tác động bộ nhớ mã lệnh (Code Size)',
            '0%\n(Không đổi)',
            '0%\n(Không đổi)',
            '0%\n(Không đổi)',
            'Tăng gấp 2 lần\n(2x Code Size)',
            '0%\n(Không đổi)',
            '0%\n(Trong suốt 100% với phần mềm)'
        ]
    ]

    # Create new 8-column table and place it in the exact position of old_tbl
    new_tbl = doc.add_table(rows=0, cols=8)
    old_tbl._tbl.addprevious(new_tbl._tbl)
    old_tbl._tbl.getparent().remove(old_tbl._tbl)
    
    tbl = new_tbl
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Column widths (Total ~17.0 cm fitting A4 page width with 2cm margins)
    col_widths = [Cm(0.6), Cm(3.2), Cm(2.1), Cm(2.1), Cm(2.1), Cm(2.2), Cm(2.2), Cm(2.6)]
    
    # Add header row
    hdr_row = tbl.add_row()
    hdr_tr = hdr_row._tr.get_or_add_trPr()
    hdr_tr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    
    for idx, (cell, h_text, width) in enumerate(zip(hdr_row.cells, headers, col_widths)):
        cell.width = width
        cell.text = h_text
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        # Shading
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F2F2F2"/>')
        cell._tc.get_or_add_tcPr().append(shading)
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        for r in p.runs:
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)

    # Add data rows
    for row_data in table_data:
        row = tbl.add_row()
        for idx, (cell, val, width) in enumerate(zip(row.cells, row_data, col_widths)):
            cell.width = width
            cell.text = val
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            
            if idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(8.0)
                if idx == 7: # Proposed method column
                    r.bold = True
                    
            # Highlight proposed column with subtle background
            if idx == 7:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F9FBFD"/>')
                cell._tc.get_or_add_tcPr().append(shd)

def update_references_section(doc):
    """Replace References section with the exact 16 local references present on machine."""
    p_ref = None
    p_phuluc = None
    for p in doc.paragraphs:
        if p.text.strip().upper() == "TÀI LIỆU THAM KHẢO":
            p_ref = p
        elif "PHỤ LỤC" in p.text.upper():
            p_phuluc = p

    if not p_ref or not p_phuluc:
        print("Could not find TÀI LIỆU THAM KHẢO or PHỤ LỤC headings!")
        return

    # Delete all elements between p_ref and p_phuluc
    parent = p_ref._p.getparent()
    curr = p_ref._p.getnext()
    while curr is not None and curr != p_phuluc._p:
        next_node = curr.getnext()
        parent.remove(curr)
        curr = next_node

    # Exactly 16 local references present on machine
    categorized_refs = [
        ("— Tài liệu nền tảng (Foundation) —", True),
        ('[1] V. Sze, Y.-H. Chen, T.-J. Yang, and J. S. Emer, "Efficient Processing of Deep Neural Networks: A Tutorial and Survey," Proceedings of the IEEE, vol. 105, no. 12, pp. 2295–2329, Dec. 2017.', False),
        ('[2] A. Avizienis, J.-C. Laprie, B. Randell, and C. Landwehr, "Basic Concepts and Taxonomy of Dependable and Secure Computing," IEEE Transactions on Dependable and Secure Computing, vol. 1, no. 1, pp. 11–33, 2004.', False),
        ('[3] RISC-V Foundation, "The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA," Document Version 20191213, Dec. 2019.', False),
        ('[4] H. Bar-El, H. Choukri, D. Naccache, M. Tunstall, and C. Whelan, "The Sorcerer’s Apprentice Guide to Fault Attacks," Proceedings of the IEEE, vol. 94, no. 2, pp. 370–382, 2006.', False),
        ('[5] G. Bertoni, L. Breveglieri, I. Koren, P. Maistri, and V. Piuri, "Error Analysis and Detection Procedures for a Hardware Implementation of the AES," IEEE Transactions on Computers, vol. 52, no. 4, pp. 492–505, 2003.', False),
        ("— Kỹ thuật dung lỗi phần cứng (TMR, DMR, Parity — 2018–2026) —", True),
        ('[6] L. Flad, M. Leyer, F. S. Nitz, and T. Krawutschke, "A Comprehensive Survey of Redundancy Systems with a Focus on Triple Modular Redundancy (TMR)," ACM Computing Surveys, 2026.', False),
        ('[7] A. C. R. Alves, L. F. Q. Silveira, et al., "A Parity-Based Dual Modular Redundancy Approach for the Reliability of Data Transmission in COTS SoCs," IEEE Access, vol. 12, pp. 90815–90829, 2024.', False),
        ('[8] IEEE Industry Applications Society, "Dual Modular Redundancy and Self-Monitoring Schemes for Power System Monitoring and Automation Equipment," IEEE Transactions on Industry Applications, 2020.', False),
        ('[9] R. P. Webber, "Error Detection: Parity Bits and Check Digits," Department of Mathematics and Computer Science, Longwood University, Farmville, VA, Technical Report, 2018.', False),
        ("— Concurrent Error Detection, Mã Thặng Dư & Bộ Vi Xử Lý RISC-V —", True),
        ('[10] U. Sparmann and S. M. Reddy, "On the Effectiveness of Residue Code Checking for Parallel Multipliers," in Proc. 24th International Symposium on Fault-Tolerant Computing (FTCS-24), pp. 219–228, 1994.', False),
        ('[11] M. Maniatakos, N. Karimi, C. Tirumurti, A. Jas, and Y. Makris, "Low-Cost Concurrent Error Detection for Floating-Point Unit Controllers," IEEE Transactions on Computers, vol. 62, no. 7, pp. 1376–1388, 2013.', False),
        ('[12] J. Li, S. Zhang, and C. Bao, "DuckCore: A Fault-Tolerant Processor Core Based on RISC-V Architecture," Electronics (MDPI), vol. 11, no. 19, p. 3085, 2022.', False),
        ("— Dung Lỗi Phần Mềm (SW-EDDI) & Vi Kiến Trúc RISC-V Kháng Lỗi Hiện Đại (2021–2026) —", True),
        ('[13] C. De Sio, V. Cammarota, and S. Di Carlo, "SEU Evaluation of Hardened-by-Replication Software in RISC-V Architecture," in IEEE International Symposium on Defect and Fault Tolerance in VLSI and Nanotechnology Systems (DFT), pp. 1–6, 2021.', False),
        ('[14] N. Oh, P. P. Shirvani, and E. J. McCluskey, "Error Detection by Duplicated Instructions in Super-Scalar Processors," IEEE Transactions on Reliability, vol. 51, no. 1, pp. 63–75, 2002.', False),
        ('[15] N. Oh, S. Mitra, and E. J. McCluskey, "ED4I: Error Detection by Diverse Data and Duplicated Instructions," IEEE Transactions on Computers, vol. 51, no. 2, pp. 180–199, 2002.', False),
        ('[16] Z. Cao, Y. Yang, and Q. Wang, "I-COR: Instruction-Level Fault Tolerance for Register File in 3-Stage Pipeline RISC-V Processors," ACM Transactions on Embedded Computing Systems, vol. 25, no. 2, pp. 1–25, 2026.', False)
    ]

    for text, is_header in categorized_refs:
        new_p = doc.add_paragraph()
        new_p.style = doc.styles['Normal']
        r = new_p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        
        if is_header:
            r.bold = True
            r.italic = True
            new_p.paragraph_format.left_indent = Cm(0)
            new_p.paragraph_format.first_line_indent = Cm(0)
            new_p.paragraph_format.space_before = Pt(10)
            new_p.paragraph_format.space_after = Pt(4)
        else:
            new_p.paragraph_format.left_indent = Cm(1.0)
            new_p.paragraph_format.first_line_indent = Cm(-1.0)
            new_p.paragraph_format.space_before = Pt(2)
            new_p.paragraph_format.space_after = Pt(2)
            
        # Move new_p right before p_phuluc in the XML tree
        p_phuluc._p.addprevious(new_p._p)

def main():
    print(f"Loading template: {TEMPLATE_PATH}")
    doc = Document(TEMPLATE_PATH)
    
    print("1. Updating Abbreviations Table (38 items)...")
    update_abbreviations_table(doc)
    
    print("2. Updating citations across body text (local [1]-[16])...")
    update_text_citations(doc)
    
    print("3. Updating 8-column comparison table matching user image (13 criteria)...")
    update_comparison_table_8_columns(doc)
    
    print("4. Updating References section with 16 local papers...")
    update_references_section(doc)
    
    print("5. Injecting dynamic page numbers in footer...")
    set_footer_page_numbers(doc)
    
    # Save to files
    for path in [OUT_PATH_1, OUT_PATH_2, OUT_PATH_3]:
        try:
            doc.save(path)
            print(f"SUCCESS: Saved to {path}")
        except PermissionError:
            print(f"WARNING: {path} is currently locked by another application.")

if __name__ == "__main__":
    main()
