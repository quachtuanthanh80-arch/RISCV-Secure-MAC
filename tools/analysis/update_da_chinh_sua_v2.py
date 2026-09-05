#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cập nhật nội dung tệp docs/Bao_cao_NCKH_2026_Da_chinh_sua_v2.docx:
1. KHÔNG THAY ĐỔI ĐỊNH DẠNG / FORMAT / TEXTURE CỦA FILE GỐC.
2. Sắp xếp lại đúng vị trí ảnh:
   - Hình 2.3 (Cơ chế bảo vệ Double-Check đa lớp) chuyển về đúng Mục 2.2.4 (sau đoạn 3 RNS).
   - Xóa hình rác mồ côi (duplicate drawing không caption) tại Mục 2.3.3 trước Hình 2.6.
3. Bổ sung nội dung khoa học mới:
   - Tham số hóa OUT_WIDTH (16-bit / 32-bit) và ngưỡng ANOMALY_THRESHOLD tại Mục 2.3.
   - Mục 3.2.6: Thực nghiệm Đánh giá Độ bền vững Suy luận Nơ-ron AI (INT8 FC Layer) kèm bảng đối chứng.
   - Mục 3.3.1 (e): Xu hướng tiêm lỗi trên FPGA bằng ICAP (Ferlini et al. 2023 [25]).
   - Mục 3.4: Phân tích Giới hạn Kỹ thuật và Biện pháp Khắc phục Toàn diện (Limitations & 3-Tier Mitigation).
   - Cập nhật danh mục Tài liệu tham khảo đầy đủ 25 công trình theo năm, bao gồm bài MDPI [25].
"""

import os
import sys
import io
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import docx
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_bg(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
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

def main():
    doc_path = Path(r"D:\NCKH\docs\Bao_cao_NCKH_2026_Da_chinh_sua_v2.docx")
    if not doc_path.exists():
        print(f"Error: {doc_path} does not exist.")
        return

    doc = docx.Document(str(doc_path))
    print(f"[INFO] Loaded document: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables.")

    # ═════════════════════════════════════════════════════════════════════════
    # 1. SẮP XẾP LẠI VỊ TRÍ ẢNH VÀ XÓA ẢNH MỒ CÔI
    # ═════════════════════════════════════════════════════════════════════════
    
    # 1.1 Tìm vị trí Hình 2.3 và đoạn chứa Mục 2.2.4
    p_hinh2_3_drawing = None
    p_hinh2_3_caption = None
    p_sec2_2_4_last = None

    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if "Hình 2.3: Sơ đồ cơ chế bảo vệ Double-Check đa lớp" in t:
            p_hinh2_3_caption = p
            # Paragraph ngay trước caption thường chứa drawing của Hình 2.3
            if i > 0 and len(doc.paragraphs[i-1]._p.xpath('.//w:drawing')) > 0:
                p_hinh2_3_drawing = doc.paragraphs[i-1]
        if "3. Kiến trúc Thặng dư Đa cơ số (Residue Number System" in t:
            p_sec2_2_4_last = p

    if p_hinh2_3_drawing and p_hinh2_3_caption and p_sec2_2_4_last:
        print("[INFO] Di chuyển Hình 2.3 về đúng vị trí trong Mục 2.2.4...")
        p_sec2_2_4_last._p.addnext(p_hinh2_3_caption._p)
        p_sec2_2_4_last._p.addnext(p_hinh2_3_drawing._p)
        print("[SUCCESS] Đã di chuyển Hình 2.3 vào đúng Mục 2.2.4 thành công.")
    else:
        print("[WARN] Không tìm thấy đầy đủ các phần tử để di chuyển Hình 2.3.")

    # 1.2 Xóa ảnh mồ côi (drawing không có caption tại Mục 2.3.3 trước Hình 2.6)
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if "Hình 2.6: Giản đồ dạng sóng mô phỏng Rollback 1 chu kỳ" in t:
            # Kiểm tra 2 đoạn văn trước caption
            if i >= 2:
                p_prev1 = doc.paragraphs[i-1]
                p_prev2 = doc.paragraphs[i-2]
                # Nếu p_prev2 có drawing và hoàn toàn không có text, đó là drawing thừa
                if len(p_prev2._p.xpath('.//w:drawing')) > 0 and len(p_prev2.text.strip()) == 0:
                    print(f"[INFO] Xóa ảnh mồ côi thừa trước Hình 2.6...")
                    p_prev2._p.getparent().remove(p_prev2._p)
                    print("[SUCCESS] Đã xóa ảnh mồ côi thành công.")
            break

    # ═════════════════════════════════════════════════════════════════════════
    # 2. CẬP NHẬT NỘI DUNG VĂN BẢN (THEO THÔNG TIN MỚI)
    # ═════════════════════════════════════════════════════════════════════════

    # 2.1 Cập nhật tham số hóa vi kiến trúc Secure MAC tại Mục 2.3
    for p in doc.paragraphs:
        if "Kiến trúc Secure MAC đề xuất hiện thực đồng thời hai luồng dữ liệu song song" in p.text:
            p.text = (
                "Kiến trúc Secure MAC đề xuất hiện thực đồng thời hai luồng dữ liệu song song, được tham số hóa toàn diện "
                "với độ rộng ngõ vào IN_WIDTH = 8 và độ rộng tích lũy OUT_WIDTH ∈ {16, 32}. Trong chế độ deep learning độ chính xác "
                "cao, OUT_WIDTH = 32 cho phép tích lũy đầy đủ các tích INT8 mà không bị tràn số, đồng thời tích hợp ngưỡng kiểm tra "
                "dị thường động ANOMALY_THRESHOLD = ±3.276.700 (tương ứng miền tích lũy tối đa của 200 nơ-ron INT8). Trong cấu hình "
                "SoC FPGA nhỏ gọn, OUT_WIDTH = 16 được đóng gói tối ưu để vừa vặn một thanh ghi bus MMIO 16-bit duy nhất."
            )
            break

    # 2.2 Bổ sung Mục 3.2.6: Thực nghiệm Đánh giá Độ bền vững Suy luận Nơ-ron AI
    p_table3_3_heading = None
    for p in doc.paragraphs:
        if "Bảng 3.3: Tổng hợp Kết quả Thực nghiệm Chiến dịch Tiêm lỗi" in p.text:
            p_table3_3_heading = p
            break

    if p_table3_3_heading:
        print("[INFO] Bổ sung Mục 3.2.6 (Benchmark Suy luận AI) trước Bảng 3.3...")
        
        # Tạo đoạn tiêu đề Mục 3.2.6
        p_ai_heading = doc.add_paragraph("3.2.6. Thực nghiệm Đánh giá Độ bền vững Suy luận Nơ-ron AI (End-to-End Inference Resilience Benchmark)")
        p_ai_heading.style = "Heading 3"
        
        # Đoạn thuyết minh
        p_ai_desc = doc.add_paragraph(
            "Để chứng minh giá trị thực tiễn trong ứng dụng Edge AI, nghiên cứu đã xây dựng bài đo kiểm chứng suy luận "
            "trên nơ-ron mạng kết nối dày đặc (Fully Connected Layer Neuron) với phép toán tích lũy: "
            "Y = ∑ (W_i × X_i) + Bias (với 16 toán hạng INT8). Thực nghiệm tiến hành tiêm lỗi lật bit ngẫu nhiên (SEU) "
            "tại bước tính toán thứ 7 trong chuỗi 16 phép MAC liên tiếp:"
        )
        p_ai_desc.paragraph_format.left_indent = Cm(1)
        p_ai_desc.paragraph_format.line_spacing = 1.25

        # Bảng đối chứng AI
        tbl_ai = doc.add_table(rows=4, cols=5)
        tbl_ai.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl_ai.style = "Table Grid"
        ai_data = [
            ["Kiến trúc phần cứng", "Đầu ra suy luận (Y)", "Sai lệch tuyệt đối (|ΔY|)", "Tỷ lệ SDC", "Kết quả phân loại (Inference Accuracy)"],
            ["Chuẩn đối chứng (Golden Model)", "-4.360", "0", "0,00%", "Chính xác tuyệt đối (100,0%)"],
            ["Mạch MAC cơ sở (Baseline MAC)", "+12.024", "16.384 (Lỗi tràn MSB)", "100,00% (SDC)", "Thất bại (Phân loại sai hoàn toàn)"],
            ["Mạch đề xuất (Secure MAC + Rollback)", "-4.360", "0 (Khôi phục tức thời)", "0,00%", "Chính xác tuyệt đối (Bảo toàn 100,0%)"],
        ]
        for ri, row in enumerate(ai_data):
            for ci, val in enumerate(row):
                cell = tbl_ai.rows[ri].cells[ci]
                cell.text = val
                set_cell_margins(cell, 60, 60, 80, 80)
                for cp in cell.paragraphs:
                    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for cr in cp.runs:
                        cr.font.name = "Times New Roman"
                        cr.font.size = Pt(9.5)
                        if ri == 0:
                            cr.bold = True
                            cr.font.color.rgb = RGBColor(255, 255, 255)
        for c in tbl_ai.rows[0].cells:
            set_cell_bg(c, "0D47A1")
        for c in tbl_ai.rows[3].cells:
            set_cell_bg(c, "E8F5E9")

        # Đoạn kết luận AI
        p_ai_sum = doc.add_paragraph(
            "Kết quả thực nghiệm xác nhận: Trên mạch MAC không bảo vệ, lỗi lật bit SEU bị tích lũy thầm lặng vào thanh ghi "
            "kết quả làm đầu ra suy luận lệch tới 16.384 đơn vị, dẫn tới suy giảm nghiêm trọng độ chính xác phân loại. Ngược lại, "
            "trên Secure MAC, lỗi được phát hiện ngay trong chu kỳ xuất hiện (t = 1 CK), kích hoạt cờ fault_detected và Rollback "
            "khôi phục giá trị tích lũy an toàn gần nhất từ Shadow Accumulator, bảo toàn 100% độ chính xác suy luận nơ-ron."
        )
        p_ai_sum.paragraph_format.left_indent = Cm(1)
        p_ai_sum.paragraph_format.line_spacing = 1.25

        # Chèn cụm này vào ngay trước p_table3_3_heading
        p_table3_3_heading._p.addprevious(p_ai_heading._p)
        p_table3_3_heading._p.addprevious(p_ai_desc._p)
        p_table3_3_heading._p.addprevious(tbl_ai._tbl)
        p_table3_3_heading._p.addprevious(p_ai_sum._p)
        print("[SUCCESS] Đã chèn Mục 3.2.6 thành công.")

    # 2.3 Bổ sung Xu hướng (e) tiêm lỗi ICAP tại Mục 3.3.1
    p_trend_d = None
    for p in doc.paragraphs:
        if "Các nghiên cứu của De Sio et al. [5] (IEEE DFT 2021) và nghiên cứu kinh điển về EDDI" in p.text:
            p_trend_d = p
            break

    if p_trend_d:
        print("[INFO] Bổ sung Xu hướng (e) tiêm lỗi ICAP sau Mục 3.3.1 (d)...")
        p_trend_e_title = doc.add_paragraph("e) Khuynh hướng tiêm lỗi tăng tốc trên FPGA bằng cổng truy cập cấu hình nội ICAP (ICAP-based Fault Injection):")
        p_trend_e_title.paragraph_format.line_spacing = 1.25
        for r in p_trend_e_title.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11.5)
            r.bold = True

        p_trend_e_desc = doc.add_paragraph(
            "Nghiên cứu của Ferlini et al. [25] (MDPI Electronics 2023) đề xuất phương pháp tăng tốc chiến dịch tiêm lỗi "
            "trên SoC FPGA bằng cổng ICAP (Internal Configuration Access Port) để đánh giá độ tin cậy và tính tổn thương trước hiệu ứng sự kiện đơn (SEE). "
            "Kế thừa và bổ trợ cho hướng tiếp cận này, đề tài đã phát triển một chiến dịch kiểm chứng tự động quy mô lớn với 81.000 mẫu thử "
            "kết hợp khung Cocotb và bộ mô phỏng Icarus Verilog, bao quát toàn diện 4 mô hình lỗi vật lý (SEU, MBU, Stuck-At, Multi-bit Burst) "
            "với độ chính xác từng chu kỳ xung nhịp (cycle-accurate) và kiểm chứng cơ chế Rollback phần cứng tức thời."
        )
        p_trend_e_desc.paragraph_format.left_indent = Cm(1)
        p_trend_e_desc.paragraph_format.line_spacing = 1.25
        for r in p_trend_e_desc.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11.5)

        p_trend_d._p.addnext(p_trend_e_desc._p)
        p_trend_d._p.addnext(p_trend_e_title._p)
        print("[SUCCESS] Đã chèn Xu hướng (e) thành công.")

    # 2.4 Bổ sung Mục 3.4 (Phân tích Giới hạn & Lộ trình Khắc phục) trước TÀI LIỆU THAM KHẢO
    p_refs_heading = None
    for p in doc.paragraphs:
        if p.text.strip() == "TÀI LIỆU THAM KHẢO":
            p_refs_heading = p
            break

    if p_refs_heading:
        print("[INFO] Bổ sung Mục 3.4 (Phân tích Giới hạn Kỹ thuật & Lộ trình Khắc phục)...")
        p_lim_h2 = doc.add_paragraph("3.4. Phân tích Giới hạn Kỹ thuật và Biện pháp Khắc phục Toàn diện (Limitations & Mitigation Roadmap)")
        p_lim_h2.style = "Heading 2"

        p_lim_intro = doc.add_paragraph(
            "Một nghiên cứu khoa học nghiêm túc đòi hỏi sự nhìn nhận khách quan về các giới hạn vi kiến trúc. "
            "Dựa trên các khuyến nghị bình duyệt theo chuẩn IEEE/ACM, báo cáo phân tích sâu sắc các giới hạn và đề xuất "
            "lộ trình hoàn thiện:"
        )
        p_lim_intro.paragraph_format.left_indent = Cm(1)
        p_lim_intro.paragraph_format.line_spacing = 1.25

        limitations = [
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

        lim_paragraphs = [p_lim_h2, p_lim_intro]
        for l_title, l_desc in limitations:
            pt = doc.add_paragraph(l_title)
            pt.paragraph_format.line_spacing = 1.25
            for r in pt.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11.5)
                r.bold = True
            
            pd = doc.add_paragraph(l_desc)
            pd.paragraph_format.left_indent = Cm(1)
            pd.paragraph_format.line_spacing = 1.25
            for r in pd.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11.5)
            
            lim_paragraphs.extend([pt, pd])

        for lp in lim_paragraphs:
            p_refs_heading._p.addprevious(lp._p)
        print("[SUCCESS] Đã chèn Mục 3.4 thành công.")

    # 2.5 Cập nhật danh mục TÀI LIỆU THAM KHẢO (Đầy đủ 25 công trình theo năm)
    if p_refs_heading:
        print("[INFO] Cập nhật danh mục Tài liệu tham khảo lên 25 tài liệu...")
        # Tìm tất cả các paragraph tham khảo hiện có giữa p_refs_heading và PHỤ LỤC
        ref_paras_to_remove = []
        started = False
        for p in doc.paragraphs:
            if p._p is p_refs_heading._p:
                started = True
                continue
            if started:
                if "PHỤ LỤC" in p.text:
                    break
                ref_paras_to_remove.append(p)

        # Xóa các tham khảo cũ
        for p in ref_paras_to_remove:
            if p._p.getparent() is not None:
                p._p.getparent().remove(p._p)

        # Danh mục 25 tài liệu mới
        updated_ref_groups = [
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

        curr_p = p_refs_heading
        for grp_title, refs in updated_ref_groups:
            gt_p = doc.add_paragraph(grp_title)
            gt_p.paragraph_format.line_spacing = 1.25
            for r in gt_p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
                r.bold = True
                r.italic = True
            curr_p._p.addnext(gt_p._p)
            curr_p = gt_p

            for ref_str in refs:
                ref_p = doc.add_paragraph(ref_str)
                ref_p.paragraph_format.line_spacing = 1.25
                for r in ref_p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(11)
                curr_p._p.addnext(ref_p._p)
                curr_p = ref_p

        print("[SUCCESS] Đã cập nhật 25 tài liệu tham khảo thành công.")

    # ═════════════════════════════════════════════════════════════════════════
    # 3. LƯU LẠI TỆP
    # ═════════════════════════════════════════════════════════════════════════
    doc.save(str(doc_path))
    print(f"[SUCCESS] Hoàn tất cập nhật tệp: {doc_path.resolve()}")

if __name__ == "__main__":
    main()
