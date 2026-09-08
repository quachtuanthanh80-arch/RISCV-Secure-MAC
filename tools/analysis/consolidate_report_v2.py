#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dồn các mục trùng lặp và chuẩn hóa cấu trúc phân cấp cho file:
docs/Bao_cao_NCKH_2026_Da_chinh_sua_v2.docx:
1. Dồn Mục 2.4 và Mục 2.4.1 thành một mục thống nhất:
   "2.4. Tổng kết Vi kiến trúc Phần cứng SoC và Chuẩn Hóa Giao Tiếp ARM AMBA AXI4-Lite"
2. Dồn Mục 3.1.1 và Mục 3.1.2 thành một mục hoàn chỉnh:
   "3.1.1. Định lượng Chi phí Silicon và Đối sánh Thực nghiệm PPA Toàn diện Giữa 6 Họ Kiến trúc MAC trên FPGA Vivado 2026.1"
   - Xóa bảng so sánh 2 kiến trúc trùng lặp (Bảng 3.2 cũ).
   - Nâng cấp Bảng PPA 6 kiến trúc thành Bảng 3.2 chính thức.
   - Xóa tiêu đề tiểu mục 3.1.2 thừa.
3. Chuẩn hóa đánh số Mục 3.3.2 trước Bảng 3.4 (tránh nhảy cóc từ 3.3.1 sang 3.3.3).
4. Giữ nguyên 100% template, font chữ, bố cục hình ảnh và dãn dòng của file gốc.
"""

import sys
import io
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import docx

def main():
    doc_path = Path(r"D:\NCKH\docs\Bao_cao_NCKH_2026_Da_chinh_sua_v2.docx")
    if not doc_path.exists():
        print(f"Error: {doc_path} does not exist.")
        return

    doc = docx.Document(str(doc_path))
    print(f"[INFO] Loaded document: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables.")

    # ═════════════════════════════════════════════════════════════════════════
    # 1. DỒN MỤC 2.4 VÀ 2.4.1
    # ═════════════════════════════════════════════════════════════════════════
    p_2_4 = None
    p_2_4_1 = None
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt.startswith("2.4. Tổng kết Vi kiến trúc Phần cứng Hệ thống Đề xuất"):
            p_2_4 = p
        elif txt.startswith("2.4.1. Chuẩn Hóa Giao Tiếp Hệ Thống SoC"):
            p_2_4_1 = p

    if p_2_4:
        p_2_4.text = "2.4. Tổng kết Vi kiến trúc Phần cứng SoC và Chuẩn Hóa Giao Tiếp ARM AMBA AXI4-Lite"
        print("[SUCCESS] Đã đổi tiêu đề Mục 2.4 thành tiêu đề hợp nhất.")

    if p_2_4_1:
        # Xóa paragraph tiêu đề 2.4.1 để nội dung hòa nhập liền mạch vào Mục 2.4
        p_2_4_1._p.getparent().remove(p_2_4_1._p)
        print("[SUCCESS] Đã xóa tiêu đề tiểu mục 2.4.1 thừa.")

    # ═════════════════════════════════════════════════════════════════════════
    # 2. DỒN MỤC 3.1.1 VÀ 3.1.2 (XÓA BẢNG 3.2 CŨ, HỢP NHẤT BẢNG PPA 6 KIẾN TRÚC)
    # ═════════════════════════════════════════════════════════════════════════
    p_3_1_1 = None
    p_tbl3_2_caption = None
    p_3_1_2 = None

    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt.startswith("3.1.1. Định lượng Chi phí Silicon (Silicon Overhead)"):
            p_3_1_1 = p
        elif txt.startswith("Bảng 3.2: Đối chiếu Kỹ thuật Chi tiết giữa Baseline MAC"):
            p_tbl3_2_caption = p
        elif txt.startswith("3.1.2. Đối Sánh Thực Nghiệm PPA Giữa 6 Họ Kiến Trúc MAC"):
            p_3_1_2 = p

    if p_3_1_1:
        p_3_1_1.text = "3.1.1. Định lượng Chi phí Silicon và Đối sánh Thực nghiệm PPA Toàn diện Giữa 6 Họ Kiến trúc MAC trên FPGA Vivado 2026.1"
        print("[SUCCESS] Đã cập nhật tiêu đề Mục 3.1.1 thành mục đối sánh PPA toàn diện.")

    if p_tbl3_2_caption:
        p_tbl3_2_caption.text = "Bảng 3.2: Đối sánh Thực nghiệm Toàn diện PPA và Khả năng Kháng lỗi Giữa 6 Họ Kiến trúc MAC trên FPGA Vivado 2026.1"
        print("[SUCCESS] Đã cập nhật caption Bảng 3.2 chính thức.")

    # Xóa Bảng 2 cũ (Bảng 19 hàng so sánh 2 kiến trúc Baseline vs Secure MAC)
    # Vì Table 2 nằm ngay sau p_tbl3_2_caption cũ, chúng ta xóa phần tử XML của nó
    t2_old = doc.tables[2]
    if len(t2_old.rows) == 19 and len(t2_old.columns) == 5:
        print("[INFO] Xóa Bảng 3.2 cũ (19 hàng x 5 cột) để tránh trùng lặp với Bảng PPA 6 kiến trúc...")
        t2_old._tbl.getparent().remove(t2_old._tbl)
        print("[SUCCESS] Đã xóa Bảng 3.2 cũ thành công.")

    if p_3_1_2:
        # Xóa paragraph tiêu đề 3.1.2
        p_3_1_2._p.getparent().remove(p_3_1_2._p)
        print("[SUCCESS] Đã xóa tiêu đề tiểu mục 3.1.2 thừa.")

    # ═════════════════════════════════════════════════════════════════════════
    # 3. CHUẨN HÓA ĐÁNH SỐ MỤC 3.3.2 CHO BẢNG 3.4
    # ═════════════════════════════════════════════════════════════════════════
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt.startswith("Bảng 3.4: Bảng Đối chiếu Tổng hợp 13 Tiêu chí"):
            p.text = "3.3.2. Bảng Đối Chiếu Tổng Hợp 13 Tiêu Chí Kỹ Thuật Với Các Giải Pháp Dung Lỗi Tiên Tiến (SOTA)"
            p.style = "Heading 3"
            print("[SUCCESS] Đã chuẩn hóa đánh số Mục 3.3.2 cho Bảng 3.4.")
            break

    # ═════════════════════════════════════════════════════════════════════════
    # 4. LƯU TỆP
    # ═════════════════════════════════════════════════════════════════════════
    doc.save(str(doc_path))
    print(f"\n[DONE] Đã lưu tệp sau khi hợp nhất: {doc_path.resolve()}")

if __name__ == "__main__":
    main()
