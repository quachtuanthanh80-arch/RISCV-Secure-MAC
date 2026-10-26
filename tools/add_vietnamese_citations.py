import re

path = 'paper/main_onecolumn.tex'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target1 = r"""quyết định thông lượng xử lý của toàn hệ thống~\cite{sze2017efficient}. Tuy nhiên, khi công nghệ chế tạo bán dẫn"""
replacement1 = r"""quyết định thông lượng xử lý của toàn hệ thống~\cite{sze2017efficient}. Tại Việt Nam, các hướng tiếp cận tối ưu hóa phần cứng cho khối toán tử MAC trên thiết bị biên như kỹ thuật XNOR-popcount của Phạm Văn Khoa và cộng sự~\cite{pham2025xnor} hay giải pháp tăng tốc xử lý dữ liệu thực nghiệm trên kit FPGA Xilinx Zynq-7000~\cite{pham2025image} đã chứng minh tiềm năng vượt trội của việc cải tiến vi kiến trúc số học nhằm tiết giảm công suất và diện tích. Tuy nhiên, khi công nghệ chế tạo bán dẫn"""

assert target1 in text, "target1 not found"
text = text.replace(target1, replacement1)

target2 = r"""khôi phục tức thời trong đúng 1 chu kỳ bằng Shadow Accumulator."""
replacement2 = r"""khôi phục tức thời trong đúng 1 chu kỳ bằng Shadow Accumulator.

Bên cạnh các nghiên cứu quốc tế, tại Việt Nam, các hướng tiếp cận tích hợp bộ tăng tốc chuyên dụng cho vi xử lý RISC-V cũng như cơ chế dung lỗi hệ thống đã được đẩy mạnh nghiên cứu: nhóm tác giả của Trần Xuân Tú và cộng sự (VNU-UET) đã đề xuất kiến trúc bộ tăng tốc phần cứng AES-RV tích hợp trực tiếp vào đường truyền vi xử lý RISC-V qua mở rộng tập lệnh với độ trễ cực thấp phục vụ an toàn IoT~\cite{tran2025aes}; đồng thời các nghiên cứu nền tảng của Đặng Nam Khánh và cộng sự~\cite{dang2017low, dang2020soft} đã phát triển các mô hình dung hòa lỗi mềm và lỗi cứng với chi phí phụ trội thấp trên hệ thống mạng kết nối trên chip (NoC). Kế thừa tinh thần tối ưu hóa phần cứng và định hướng thiết kế an toàn nói trên, công trình này tập trung giải quyết bài toán dung lỗi mềm tức thời ngay tại trung tâm tính toán MAC của vi xử lý RISC-V."""

assert target2 in text, "target2 not found"
text = text.replace(target2, replacement2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Vietnamese authors citations successfully!")
