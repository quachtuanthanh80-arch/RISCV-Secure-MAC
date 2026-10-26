# tools/build_8_pages_main.py
# Generates the compact, high-density 8-page IEEE Transactions manuscript
# Preserves 100% of core contributions, theorems, proofs, and experimental evaluations

import os

def build_8_page_manuscript():
    tex = r'''\documentclass[journal]{IEEEtran}

% ==============================================================================
% GÓI HỖ TRỢ NGÔN NGỮ TIẾNG VIỆT VÀ ĐỊNH DẠNG CHUẨN IEEE TRANSACTIONS (BẢN 8 TRANG)
% ==============================================================================
\usepackage[T5]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[english,vietnamese]{babel}

\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{algorithmic}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{placeins}
\usepackage{url}
\def\UrlBreaks{\do\/\do-\do\_}

\graphicspath{{figures/}{./}{../reports/figures/}}

\newtheorem{theorem}{Định lý}
\newtheorem{lemma}{Bổ đề}
\newtheorem{remark}{Nhận xét}
\renewcommand{\qedsymbol}{$\blacksquare$}

\renewcommand{\abstractname}{Tóm tắt}
\renewcommand{\IEEEkeywordsname}{Từ khóa}
\renewcommand{\refname}{Tài liệu tham khảo}
\renewcommand{\tablename}{BẢNG}
\renewcommand{\figurename}{Hình}

% Tối ưu hóa phân bố float trong 2 cột IEEEtran cho bản thảo chuẩn 8 trang
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.90}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.85}
\renewcommand{\dbltopfraction}{0.95}
\renewcommand{\dblfloatpagefraction}{0.85}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{3}
\setcounter{totalnumber}{6}
\setcounter{dbltopnumber}{4}

\begin{document}

\title{SoC RISC-V Dung Lỗi Tích Hợp Mã Thặng Dư Modulo-3 Cho Bộ Tăng Tốc Neural MAC An Toàn}

\author{\IEEEauthorblockN{Nhóm Nghiên Cứu Phần Cứng An Toàn}
\IEEEauthorblockA{\textit{Phòng Thí Nghiệm Thiết Kế Vi Mạch \& Hệ Thống Tin Cậy, Khoa Điện Tử - Viễn Thông}\\
Hà Nội, Việt Nam --- Email: contact@hardware-sec.edu.vn}
}

\maketitle

\selectlanguage{vietnamese}

\begin{abstract}
Lỗi mềm do bức xạ ion hóa gây ra sai lệch dữ liệu thầm lặng (SDC) trong các bộ tăng tốc Edge AI. Trong khi Tam trùng Dư thừa (TMR) tiêu tốn diện tích cấm kỵ ($>200\%$) và kiểm tra chẵn lẻ bất lực trên mạch số học, mã thặng dư Modulo-3 mở ra giải pháp chi phí thấp tối ưu. Bài báo trình bày SoC RISC-V RV32I tích hợp bộ tăng tốc Nhân--Tích lũy (MAC) dung lỗi qua bus AXI4-Lite, sử dụng kiểm tra lỗi đồng thời (CED) Modulo-3 kết hợp khôi phục trạng thái 1 chu kỳ bằng Shadow Accumulator. Hiện thực hóa trên FPGA AMD Zynq-7000, mạch CED chỉ tăng $+36$~LUTs ($+4.19\%$ SoC) và $+5.55\%$ công suất, đạt $125.2$~MHz (WNS $+2.013$~ns). Tiêm $81.000$ lỗi xác nhận tỷ lệ phát hiện (FDR) đạt $100.00\%$ đối với SEU đơn bit (khoảng tin cậy Clopper-Pearson $95\%$ $[99.923\%, 100.00\%]$), triệt tiêu SDC. Với lỗi kép MBU, phòng thủ 3 lớp kết hợp EWMA thích nghi nâng FDR lên $98.49\%$. Suy luận mạng MLP ($64 \to 16 \to 10$) bảo toàn $96.00\%$ độ chính xác ($0.00\%$ suy giảm), hỗ trợ thẩm định chỉ tiêu ISO 26262 ASIL-D.
\end{abstract}

\begin{IEEEkeywords}
SoC RISC-V, Kiểm Tra Lỗi Đồng Thời (CED), Mã Thặng Dư Số Học, Modulo-3, Single Event Upset (SEU), Rollback Phần Cứng, Shadow Accumulator, Edge AI, Mạng Nơ-ron Nhúng, FPGA.
\end{IEEEkeywords}

% ==============================================================================
\section{Giới Thiệu}
% ==============================================================================
Sự bùng nổ của Mạng Nơ-ron Sâu (DNN) trên các hệ thống nhúng đòi hỏi các bộ tăng tốc phần cứng có hiệu năng tính toán và hiệu quả năng lượng vượt bậc~\cite{sze2017efficient}. Trong hầu hết các kiến trúc học sâu, toán tử Nhân--Tích lũy (MAC) chiếm hơn $90\%$ tổng khối lượng tính toán số học~\cite{sze2017efficient}. Tuy nhiên, khi công nghệ bán dẫn tiến sâu vào thang đo FinFET dưới 16nm, thể tích nhạy cảm của các nút lưu trữ giảm mạnh ($Q_{crit} < 1.0\,\text{fC}$), khiến vi mạch số trở nên cực kỳ nhạy cảm với bức xạ tự nhiên gây Lỗi Mềm Tức Thời (SET) và Lật Bit Ngẫu Nhiên (SEU)~\cite{barel2006sorcerer, libano2024analyzing, li2026radiation, cai2026transient}.

Trong các ứng dụng nhúng an toàn tới hạn (safety-critical) như xe tự hành, sự cố lật bit đơn lẻ tại thanh ghi tích lũy MAC có thể lan truyền qua các tầng phi tuyến, tạo ra sai lệch dữ liệu thầm lặng (Silent Data Corruption -- SDC)~\cite{ahmadi2026maed, reagen2018ares}. Tiêu chuẩn ISO 26262 ASIL-D đòi hỏi tỷ lệ bao phủ lỗi đơn điểm (SPFM) phải đạt trên $99.0\%$ và lỗi tiềm ẩn (LFM) trên $90.0\%$~\cite{iso26262_2018, andreasyan2026riscv}. Các giải pháp truyền thống như Tam trùng Dư thừa (TMR) làm phình diện tích silicon và công suất từ $+215\%$ đến $+260\%$~\cite{flad2026comprehensive}, không khả thi cho Edge AI. Song trùng Dư thừa (DMR)~\cite{alves2024parity} tốn $>+100\%$ diện tích; dò lỗi trễ Razor~\cite{fojtik2013bubble} bất lực trước bit-flip tĩnh; giải pháp phần mềm EDDI~\cite{oh2002eddi} tăng $>115\%$ mã lệnh và trễ khôi phục $150$--$300$ chu kỳ; còn kiểm tra chẵn lẻ (Parity CED)~\cite{bertoni2003error} thất bại hoàn toàn trên mạch số học do quá trình truyền nhớ (carry propagation).

Mã thặng dư số học (Arithmetic Residue Codes -- ARC), đặc biệt là mã Modulo-3 ($p=3$), duy trì tính toàn cấu vành: thặng dư của tích bằng tích các thặng dư, và thặng dư của tổng bằng tổng các thặng dư. Số dư modulo-3 chỉ chiếm đúng 2 bit nhị phân ($\{0, 1, 2\}$), không cần bộ chia phần cứng phức tạp và có thể thực thi qua cây cộng lát cắt 2-bit với trễ cực tiểu.

\textbf{Các Đóng góp Cốt lõi của Bài báo:}
\begin{enumerate}
    \item \textbf{Vi kiến trúc CED Modulo-3 Luồng Đôi Cân Bằng:} Cây cộng thặng dư logarit xử lý trực tiếp toán hạng bù hai INT8 $\times$ INT8 + INT32 với trễ định tuyến cực nhỏ ($1.10$~ns), đạt $125.2$~MHz trên FPGA Zynq-7000 mà không gây bọt pipeline cho CPU.
    \item \textbf{Cơ Chế Phục Hồi Rollback 1 Chu Kỳ Tức Thời:} Hiện thực hóa Shadow Accumulator liên kết vector ngắt AXI4-Lite, khôi phục trạng thái an toàn trong đúng 1 chu kỳ khi phát hiện lỗi, bảo toàn thông lượng tính toán tối đa.
    \item \textbf{Chứng Minh Hình Thức Định Lý Phổ Chẵn Lẻ Khoảng Cách Bit:} Phát biểu và chứng minh toán học điều kiện che dấu lỗi kép trong mã Modulo-3, giải thích bản chất hiện tượng triệt tiêu thặng dư đối với các cặp bit có khoảng cách lẻ.
    \item \textbf{Tích Hợp SoC RISC-V \& Kiểm Chứng Thực Nghiệm:} Tích hợp bộ tăng tốc vào lõi RV32I 5 tầng qua bus AXI4-Lite, thực thi trên chip AMD Zynq-7000 qua chiến dịch tiêm $81.000$ mẫu lỗi, bảo toàn $96.00\%$ độ chính xác mạng nơ-ron MLP ($64 \to 16 \to 10$).
    \item \textbf{Bộ Theo Dõi Thích Nghi EWMA Trực Tuyến \& DSE Hướng AI:} Module phần hardware EWMA fixed-point Q8.8 không tốn DSP nâng FDR lỗi kép lên $98.49\%$, kết hợp mô hình Graph Neural Network (GNN) định vị điểm nghẽn độ tin cậy để đạt hiệu quả diện tích gấp $47\times$ so với TMR.
\end{enumerate}

% ==============================================================================
\section{Tổng Quan Nghiên Cứu \& Phân Loại Phương Pháp}
% ==============================================================================
Bảng~\ref{tab:taxonomy} đối chiếu định lượng kiến trúc đề xuất với các giải pháp tiên tiến nhất hiện nay. Các kỹ thuật kiểm tra cổ điển như mã Berger~\cite{berger1961note} hay mã chẵn lẻ Parity~\cite{bertoni2003error} thất bại trên mạch số học do tính chất phi tuyến của phép nhân và lan truyền bit nhớ. Mã tích số AN ($A=3$)~\cite{avizienis1971arithmetic} tăng diện tích $+85\%$--$+110\%$. Mã Modulo-$(2^n-1)$ như Mod-7/15~\cite{nicolaidis2005design} đòi hỏi mở rộng kênh residue lên 3--4 bit làm tăng trễ và công suất. Gần đây, HARV-SoC~\cite{imianosky2026reliability} bảo vệ bộ xử lý vector RISC-V dưới bức xạ proton nhưng tốn $>+140\%$ LUTs và mất $8$--$16$ chu kỳ khôi phục; còn FORTALESA~\cite{cherezova2025fortalesa} dùng mảng systolic tái cấu hình nhưng tốn $+45\%$--$60\%$ diện tích và mất hàng chục chu kỳ ngắt quãng. So với các công trình trên, kiến trúc của chúng tôi bảo vệ trực tiếp datapath MAC với phụ trội chỉ $+4.19\%$ trên toàn SoC và khôi phục tức thời trong 1 chu kỳ.

\begin{table*}[!t]
\caption{Đối Chiếu Định Lượng Các Phương Pháp Đảm Bảo Độ Tin Cậy Phần Cứng Vi Xử Lý và Bộ Tăng Tốc AI}
\label{tab:taxonomy}
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{lcccccccl}
\toprule
\textbf{Kiến trúc / Kỹ thuật} & \textbf{Năm} & \textbf{Loại Dư Thừa} & \textbf{Chi phí LUT} & \textbf{Chi phí FF} & \textbf{$\Delta$ Công Suất} & \textbf{FDR SEU} & \textbf{Trễ Khôi Phục} & \textbf{Đối Tượng \& Cơ Chế Bảo Vệ} \\
\midrule
TMR Chuẩn~\cite{flad2026comprehensive} & 2026 & Không gian (Tam trùng) & $+215\%$--$260\%$ & $+200\%$--$220\%$ & $>+200\%$ & $100.0\%$ & $0$ chu kỳ & Toàn SoC, Triplicate + Voter đa số \\
Sơ đồ DMR~\cite{tedeschi2026safe, alves2024parity} & 2024 & Không gian (Song trùng) & $+108\%$--$125\%$ & $+100\%$--$105\%$ & $>+100\%$ & $100.0\%$ & $50$--$120$ chu kỳ & Datapath MAC, Compare + Ngắt phần mềm \\
Parity CED~\cite{bertoni2003error, alves2024parity} & 2018 & Thông tin & $+10\%$--$20\%$ & $+2\%$--$4\%$ & $+5\%$ & $0.0\%^*$ (Số học) & Không áp dụng & Bộ nhớ/Thanh ghi, Cây Parity 1-bit \\
SW-EDDI~\cite{oh2002eddi, souvatzoglou2021analyzing} & 2021 & Phần mềm & $0\%$ ($+115\%$ Lệnh) & $0\%$ & Cao & $95.2\%$--$98.6\%$ & $150$--$300$ chu kỳ & Nhân bản chỉ lệnh tại trình biên dịch \\
SoC RISCBench~\cite{ojika2026riscbench} & 2026 & Lõi Điều phối & $+85.0\%$ & $+78.0\%$ & $+70\%$ & $100.0\%$ & $4$--$8$ chu kỳ & Khung tăng tốc RISC-V trên FPGA \\
I-COR~\cite{cao2026icor} & 2026 & Vi kiến trúc & $+12.0\%$ & $+8.0\%$ & $+15\%$ & $100.0\%$ & $1$ chu kỳ & Tệp thanh ghi CPU RISC-V 3 tầng \\
Spectral TMR MAC~\cite{thulasi2026spectral} & 2026 & Không gian Lai & $+185.0\%$ & $+160.0\%$ & $+140\%$ & $100.0\%$ & $0$ chu kỳ & Bộ nhân Booth + Bộ cộng CLA TMR \\
HARV-SoC VEU~\cite{imianosky2026reliability} & 2026 & Vector / TMR Cục bộ & $+140\%$--$195\%$ & $+120\%$--$150\%$ & $+110\%$ & $99.8\%$ & $8$--$16$ chu kỳ & RISC-V VEU cho CNN, TMR Vector \\
FORTALESA~\cite{cherezova2025fortalesa} & 2025 & Tái Cấu Hình Logic & $+45\%$--$60\%$ & $+30\%$--$40\%$ & $+35\%$ & $98.5\%$ & $20$--$50$ chu kỳ & Mảng Systolic DNN, Cô lập PE hỏng \\
Mã AN-Code~\cite{avizienis1971arithmetic} & 1971 & Thặng dư Số học & $+85\%$--$110\%$ & $+40\%$--$60\%$ & $+45\%$ & $100.0\%$ & $2$--$3$ chu kỳ & Bộ nhân $A \times$ + Bộ chia kiểm tra \\
Mã Modulo-$(2^n-1)$~\cite{nicolaidis2005design} & 2005 & Thặng dư Số học & $+65\%$--$90\%$ & $+20\%$--$35\%$ & $+30\%$ & $100.0\%$ & $1$ chu kỳ & Kênh thặng dư $3$--$4$ bit (Mod-7/15) \\
\textbf{Modulo-3 CED (Bài báo này)} & \textbf{2026} & \textbf{Thặng dư Số học} & \textbf{$+36.4\%$ MAC ($+4.19\%$ SoC)} & \textbf{$+4.58\%$ MAC ($+0.56\%$ SoC)} & \textbf{$+5.55\%$} & \textbf{$100.00\%$} & \textbf{$1$ chu kỳ} & \textbf{Datapath MAC + Shadow Accumulator} \\
\bottomrule
\end{tabular}
}
\vspace{1mm}
\footnotesize{$^*$Kiểm tra chẵn lẻ phát hiện $\approx 100\%$ lỗi bit-flip trong thanh ghi lưu trữ, nhưng đạt $0.0\%$ trên đường truyền số học ALU/MAC do hiện tượng nhớ carry.}
\end{table*}

% ==============================================================================
\section{Kiến Trúc Hệ Thống Đề Xuất}
% ==============================================================================

\subsection{Tích Hợp SoC RISC-V RV32I}
Kiến trúc tổng thể (Hình~\ref{fig:soc_arch}) tích hợp lõi vi xử lý RV32I 5 tầng pipeline hoàn chỉnh (hỗ trợ đầy đủ Forwarding và Hazard Detection) với bộ tăng tốc Secure MAC thông qua giao diện bus chuẩn AMBA AXI4-Lite. Mạch AXI Interconnect 1M--2S ánh xạ bộ nhớ MMIO \texttt{0x8000\_0000}--\texttt{0x8000\_001F} (Slave 1: \texttt{secure\_mac\_axi}; Slave 0: Data RAM tại \texttt{0x0000\_0000}--\texttt{0x0000\_03FF}). Bộ điều khiển AXI4-Lite Slave được quản lý bởi FSM 4 trạng thái: \texttt{ST\_IDLE} (chờ bus), \texttt{ST\_COMPUTE} (tính toán 4 tầng, \texttt{wready=0}), \texttt{ST\_ROLLBACK} (khi $r_{act} \neq r_{exp}$, kích hoạt nạp ngược \texttt{last\_valid\_out} vào thanh ghi tích lũy trong 1 chu kỳ), và \texttt{ST\_ERROR\_SYNC} (đồng bộ ngắt phần cứng \texttt{irq} đến CPU và xác lập \texttt{bvalid}).

\begin{figure}[!t]
\centering
\includegraphics[width=0.88\columnwidth]{fig2_1_rv32i_soc_datapath.png}
\caption{Mặt bằng kiến trúc tổng thể của SoC RISC-V RV32I tích hợp bộ tăng tốc Neural Secure MAC qua bus AMBA AXI4-Lite.}
\label{fig:soc_arch}
\end{figure}

\subsection{Đường Truyền Dữ Liệu \& Mô Hình 3 Lớp Phòng Thủ}
Bộ tăng tốc Secure MAC (Hình~\ref{fig:mac_arch}) tiếp nhận hai toán hạng ngõ vào INT8 ($A, B \in [-128, +127]$) và tích lũy vào thanh ghi $C \in \text{INT32}$. Đường truyền dữ liệu gồm 4 tầng pipeline đồng bộ: Tầng 1 (Chốt thanh ghi ngõ vào), Tầng 2 (Bộ nhân 16-bit có dấu), Tầng 3 (Bộ cộng tích lũy 32-bit), và Tầng 4 (Kiểm tra thặng dư Modulo-3 và Chốt ngõ ra). Ánh xạ thặng dư $\varphi(X) = X \bmod 3$ thỏa mãn tính toàn cấu vành:
\begin{equation}
\label{eq:ring_homo}
\varphi(A \times B + C) = [\varphi(A) \times \varphi(B) + \varphi(C)] \bmod 3.
\end{equation}
Luồng kiểm tra song song tính toán thặng dư kỳ vọng $r_{exp} = [r_A \times r_B + r_C] \bmod 3$ độc lập với luồng dữ liệu chính. Tại Tầng 4, bộ so sánh kiểm tra $r_{exp} == r_{act} = \varphi(S)$.

\begin{figure}[!t]
\centering
\includegraphics[width=0.92\columnwidth]{fig2_2_secure_mac_architecture.png}
\caption{Vi kiến trúc bộ tăng tốc Secure MAC luồng đôi song song 4 tầng với cơ chế phục hồi Rollback 1 chu kỳ bằng Shadow Accumulator.}
\label{fig:mac_arch}
\end{figure}

Để triệt tiêu điểm mù lý thuyết trước các dạng lỗi vật lý, hệ thống triển khai cơ chế phòng thủ 3 lớp chiều sâu (Hình~\ref{fig:double_check}):
\begin{itemize}
    \item \textbf{Lớp 1: Modulo-3 CED (Vi kiến trúc):} Phát hiện $100.00\%$ lỗi SEU. Với lỗi kép 2-bit MBU, phát hiện $240/496$ cặp bit ($48.39\%$) có khoảng cách $d = |j - i|$ chẵn theo Định lý~\ref{thm:masking}.
    \item \textbf{Lớp 2: Đan Xen Bit Layout (Bố trí Vật lý):} Bố trí các ô nhớ vật lý kề cận với khoảng cách $D \ge 3$ bit logic~\cite{baeg2009sram}, biến cụm lỗi vật lý (MCU) thành các lỗi đơn SEU phân tán hoặc chuyển khoảng cách bit logic thành chẵn.
    \item \textbf{Lớp 3: Bộ Theo Dõi EWMA Thích Nghi (Hệ thống):} Module \texttt{ewma\_tracker.sv} theo dõi kỳ vọng $\mu_t$ và độ lệch $\text{MAD}_t$ trên luồng dữ liệu, đặt ngưỡng trượt $\tau_t = |\mu_t| + 3.75 \times \text{MAD}_t$ bắt các đột biến của $256/496$ cặp lỗi lẻ, nâng FDR MBU tổng thể lên \textbf{$98.49\%$}.
\end{itemize}

\begin{figure}[!t]
\centering
\includegraphics[width=0.88\columnwidth]{fig2_3_double_check_layers.png}
\caption{Mô hình phòng thủ 3 lớp: Lớp 1 (Modulo-3 CED bắt SEU và MBU chẵn), Lớp 2 (Bit-Interleaving bố trí layout), và Lớp 3 (Bộ theo dõi EWMA).}
\label{fig:double_check}
\end{figure}

\subsection{Tính Đúng Đắn Hình Thức của Cây Mã Hóa Modulo-3}
\begin{theorem}[Thu gọn Cặp Bit Modulo-3]
\label{thm:pairwise}
Cho $X = \sum_{k=0}^{N-1} x_k 2^k$ là số nguyên nhị phân $N$-bit ($N$ chẵn). Khi đó:
\begin{equation}
\varphi(X) = \left( \sum_{i=0}^{N/2-1} (x_{2i} - x_{2i+1}) \right) \bmod 3.
\end{equation}
\end{theorem}
\begin{proof}
Vì $2^2 \equiv 1 \pmod 3$, với chỉ số chẵn $k=2i$ thì $2^{2i} \equiv 1^i \equiv 1 \pmod 3$. Với chỉ số lẻ $k=2i+1$ thì $2^{2i+1} \equiv 1 \cdot 2 \equiv -1 \pmod 3$. Do đó, tách $X$ thành các cặp bit: $\varphi(X) \equiv \sum_{i=0}^{N/2-1} [x_{2i}(1) + x_{2i+1}(-1)] \equiv \sum_{i=0}^{N/2-1} (x_{2i} - x_{2i+1}) \pmod 3$.
\end{proof}

Từ Định lý~\ref{thm:pairwise}, phép chia dư được chuyển thành cây cộng nhị phân thu gọn dựa trên các lát cắt 2-bit:
\begin{itemize}
    \item \textbf{Khối Cơ Bản (\texttt{slice\_mod3}):} Mỗi cặp bit không dấu $\{x_{2i+1}, x_{2i}\}$ ánh xạ thành số dư 2-bit: $(00)_2 \to 0, (01)_2 \to 1, (10)_2 \to 2, (11)_2 \to 0$. Logic này chỉ tốn 2 cổng cơ bản với trễ dưới $0.15$~ns.
    \item \textbf{Xử Lý Số Bù Hai (\texttt{msb\_pair\_mod3}):} Trong biểu diễn bù hai $N$-bit, bit MSB $x_{N-1}$ mang trọng số $-2^{N-1}$. Khi $N-1$ lẻ ($2m+1$), ta có: $-2^{2m+1} \equiv -(1 \cdot 2) \equiv +1 \pmod 3$. Do đó, lát cắt dấu $\{x_{N-1}, x_{N-2}\}$ được tính bởi $(x_{N-2} + x_{N-1}) \bmod 3$, hỗ trợ trực tiếp số có dấu INT8/INT32 mà không cần bộ chuyển đổi bù hai ở ngõ vào.
    \item \textbf{Cây Mã Hóa 8-bit và 32-bit (Hình~\ref{fig:mod3_trees}):} Áp dụng cho $A, B$ (hoàn thành trong $0.42$~ns) và $S[31:0]$ (cây cộng logarit cân bằng 4 tầng $\lceil\log_2 16\rceil=4$, trễ cực đại chỉ \textbf{$1.10$~ns} trên FPGA), đảm bảo mạch kiểm tra không bao giờ là đường trễ tới hạn.
\end{itemize}

\begin{figure}[!t]
\centering
\includegraphics[width=0.88\columnwidth]{fig2_4_mod3_encoder_8b.png}\\[0.3ex]
\footnotesize{(a) Cây thu gọn nhị phân 8-bit (\texttt{msb\_pair})}\\[1.0ex]
\includegraphics[width=0.88\columnwidth]{fig2_5_mod3_encoder_32b.png}\\[0.3ex]
\footnotesize{(b) Cây cộng logarit cân bằng 4 tầng 32-bit ($1.10$~ns)}
\caption{Kiến trúc cây mã hóa Modulo-3: (a) Cho dữ liệu INT8, (b) Cây cộng logarit cân bằng 4 tầng cho thanh ghi tích lũy INT32.}
\label{fig:mod3_trees}
\end{figure}

\subsection{Cơ Chế Phục Hồi Rollback Bằng Shadow Accumulator}
Khi chu kỳ tính toán hợp lệ ($valid=1 \land fault\_detected=0$), kết quả được chốt vào thanh ghi bóng \textit{Shadow Accumulator} (\texttt{last\_valid\_out}). Khi phát hiện lỗi ($fault\_detected=1$), cờ \texttt{rollback} được kích hoạt tức thời, cô lập ngõ ra hỏng và nạp ngược trạng thái hợp lệ gần nhất trong đúng 1 chu kỳ ($1$~CK) mà không tạo bọt pipeline.

Giản đồ dạng sóng mô phỏng Vivado chu kỳ chính xác (Hình~\ref{fig:waveform_rollback}) xác nhận 4 giai đoạn vận hành: (1) Reset hệ thống ($0 - 20$~ns); (2) Vận hành hợp lệ và chốt điểm an toàn $\texttt{last\_valid\_out} = 150$ ($30 - 70$~ns); (3) Tiêm lỗi bit-flip SEU tại $t = 70$~ns làm kết quả sai lệch thành $261$; (4) Bắt lỗi tức thời tại $t = 95$~ns khi $r_{act} = 0 \neq r_{exp} = 2$, giương cờ \texttt{fault\_detected} và Rollback khôi phục $\texttt{out} = 150$ tại $t = 100.000$~ns. Hệ thống hỗ trợ 2 cơ chế: \textit{Drop-and-Skip} (bỏ qua kết quả hỏng, giữ nguyên thông lượng $1.0$~op/CK) và \textit{Micro-Replay} (nạp lại toán hạng qua ngắt CPU với chi phí $+1$~CK bọt, suy giảm thông lượng $<1\%$).

\begin{figure}[!t]
\centering
\includegraphics[width=0.96\columnwidth]{fig2_6_waveform_rollback.png}
\caption{Giản đồ dạng sóng mô phỏng Vivado chu kỳ chính xác minh họa cơ chế tự phục hồi Rollback trong 1 chu kỳ tại $t = 100.000$~ns khi tiêm lỗi SEU.}
\label{fig:waveform_rollback}
\end{figure}

% ==============================================================================
\section{Kết Quả Thực Nghiệm \& Đánh Giá}
% ==============================================================================

\subsection{Triển Khai FPGA \& Phân Tích PPA}
Hệ thống được hiện thực hóa trên FPGA AMD Xilinx Zynq-7000 ($xc7z020clg400-1$) bằng Vivado 2026.1 ở tần số $100$~MHz ($W_{in}=8, W_{out}=16$). Bảng~\ref{tab:ppa} và Hình~\ref{fig:ppa_implementation} tổng hợp các chỉ số PPA chi tiết sau định tuyến thực tế giữa Secure MAC và 6 kiến trúc tham chiếu.

\begin{table*}[!t]
\caption{Đối Sánh Thực Nghiệm PPA Giữa Các Kiến Trúc MAC và Toàn Bộ Hệ Thống SoC Sau Thực Thi Trên FPGA Xilinx Zynq-7000 ($W_{in}=8, W_{out}=16$)}
\label{tab:ppa}
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{lcccccccc}
\toprule
\textbf{Kiến Trúc Phần Cứng} & \textbf{Slice LUTs} & \textbf{Slice FFs} & \textbf{DSP48} & \textbf{Worst Slack (WNS)} & \textbf{$F_{max}$ (MHz)} & \textbf{Công Suất Động} & \textbf{Tổng Công Suất} & \textbf{Cơ Chế Phục Hồi} \\
\midrule
Baseline MAC (Không bảo vệ) & $99$ ($0.19\%$) & $65$ ($0.06\%$) & $1$ ($0.45\%$) & $+2.540$~ns & $134.0$~MHz & $18.2$~mW & $138.2$~mW & Không có (Dễ tổn thương SDC) \\
TMR MAC (Tam trùng Dư thừa) & $337$ ($0.63\%$) & $211$ ($0.20\%$) & $3$ ($1.36\%$) & $+1.420$~ns & $116.5$~MHz & $58.4$~mW & $178.4$~mW & $0$ chu kỳ (Biểu quyết phần cứng đa số) \\
DMR MAC (Song trùng Dư thừa) & $215$ ($0.40\%$) & $138$ ($0.13\%$) & $2$ ($0.91\%$) & $+1.890$~ns & $123.3$~MHz & $37.6$~mW & $157.6$~mW & Ngắt phần mềm ($50$--$120$ chu kỳ) \\
Parity CED MAC & $112$ ($0.21\%$) & $68$ ($0.06\%$) & $1$ ($0.45\%$) & $+2.310$~ns & $130.0$~MHz & $19.5$~mW & $139.5$~mW & Không có (Thất bại trên số học MAC) \\
Residue Modulo-7 MAC & $172$ ($0.32\%$) & $78$ ($0.07\%$) & $1$ ($0.45\%$) & $+1.650$~ns & $119.8$~MHz & $26.8$~mW & $146.8$~mW & $1$ chu kỳ (Kênh residue 3-bit) \\
\textbf{Secure MAC (Đề xuất)} & \textbf{135 ($0.25\%$)} & \textbf{68 ($0.06\%$)} & \textbf{1 ($0.45\%$)} & \textbf{+2.013~ns} & \textbf{125.2~MHz} & \textbf{22.4~mW} & \textbf{142.4~mW} & \textbf{1 chu kỳ (Shadow Accumulator)} \\
\midrule
Baseline SoC RV32I & $824$ ($1.55\%$) & $534$ ($0.50\%$) & $1$ ($0.45\%$) & $+2.350$~ns & $130.7$~MHz & $62.5$~mW & $182.5$~mW & Baseline không bảo vệ \\
\textbf{Secure SoC RV32I (Đề xuất)} & \textbf{860 ($1.62\%$)} & \textbf{537 ($0.51\%$)} & \textbf{1 ($0.45\%$)} & \textbf{+2.013~ns} & \textbf{125.2~MHz} & \textbf{65.9~mW} & \textbf{185.9~mW} & \textbf{1 chu kỳ Rollback + Ngắt CPU} \\
$\Delta$ Phụ trội Toàn SoC & \textbf{+36 LUTs (+4.19\%)} & \textbf{+3 FFs (+0.56\%)} & \textbf{0 (0.00\%)} & \textbf{--0.337~ns} & \textbf{--5.5~MHz} & \textbf{+3.4~mW (+5.55\%)} & \textbf{+3.4~mW (+1.86\%)} & \textbf{Bảo toàn 100\% thông lượng} \\
\bottomrule
\end{tabular}
}
\vspace{1mm}
\footnotesize{Ghi chú: Kết quả sau Implementation trên Vivado tại điều kiện nhiệt độ tiếp giáp $T_j = 25^\circ\text{C}$, điện áp danh định $V_{CCINT} = 1.0\text{V}$.}
\end{table*}

\begin{figure}[!t]
\centering
\includegraphics[width=0.92\columnwidth]{fig3_1_fpga_ppa_implementation.png}
\caption{Đánh giá thực nghiệm PPA sau thực thi trên FPGA Xilinx Zynq-7000: Đối sánh tài nguyên LUTs, FFs, Worst Negative Slack (WNS) và tần số cực đại $F_{max}$.}
\label{fig:ppa_implementation}
\end{figure}

Mạch Secure MAC đề xuất chỉ tiêu tốn thêm $+36$ LUTs ($+36.4\%$ trên khối MAC, chỉ $+4.19\%$ trên toàn SoC) và $+3$ FFs ($+0.56\%$ SoC), không cần thêm DSP48. Tần số đạt $125.2$~MHz với WNS $+2.013$~ns ở chu kỳ $10$~ns, thỏa mãn vượt trội yêu cầu vận hành danh định $100$~MHz. Công suất toàn SoC chỉ tăng khiêm tốn $+3.4$~mW ($+5.55\%$ động).

\subsection{Chiến Dịch Tiêm Lỗi Thực Nghiệm (81.000 Mẫu Lỗi)}
Chiến dịch tiêm lỗi tự động qua Cocotb tiêm tổng cộng $81.000$ mẫu lỗi phân bổ ngẫu nhiên trên thanh ghi $C[31:0]$, thanh ghi ngõ vào, và các nút logic tổ hợp. Kết quả xác nhận:
\begin{itemize}
    \item \textbf{Lỗi SEU Đơn Bit:} Tỷ lệ phát hiện lỗi đạt tuyệt đối \textbf{$100.00\%$} ($40.000/40.000$ mẫu lỗi SEU), triệt tiêu hoàn toàn SDC. Khoảng tin cậy Clopper-Pearson 2 phía mức $95\%$ đạt $[99.923\%, 100.00\%]$.
    \item \textbf{Lỗi Kẹt Mức (Stuck-At-0/1):} Đạt tỷ lệ phát hiện $100.00\%$ ($1.000/1.000$ ca tiêm).
    \item \textbf{Lỗi Kép Đa Bit (MBU 2-bit):} Kiểm thử toàn diện tất cả $\binom{32}{2} = 496$ cặp bit trên thanh ghi tích lũy 32-bit (mỗi cặp tiêm 80 mẫu $\to 39.680$ ca). Tỷ lệ phát hiện đạt đúng $240/496$ cặp ($48.39\%$).
\end{itemize}

\begin{theorem}[Che Dấu Lỗi Kép Trong Mã Modulo-3]
\label{thm:masking}
Một lỗi lật bit kép đồng thời tại hai vị trí $i$ và $j$ ($0 \le i < j < N$) cùng cực tính sẽ bị che dấu bởi mã Modulo-3 khi và chỉ khi khoảng cách bit $d = j - i$ là một số lẻ.
\end{theorem}
\begin{proof}
Độ sai lệch số học tạo bởi lỗi kép cùng cực tính là $\Delta = \pm (2^i + 2^j) = \pm 2^i (1 + 2^{j-i}) = \pm 2^i (1 + 2^d)$. Lỗi bị che dấu khi $\Delta \equiv 0 \pmod 3 \iff 1 + 2^d \equiv 0 \pmod 3 \iff 2^d \equiv -1 \equiv 2 \pmod 3$. Vì $2 \equiv -1 \pmod 3$, ta có $2^d \equiv (-1)^d \pmod 3$. Do đó, $(-1)^d \equiv -1 \pmod 3$ xảy ra khi và chỉ khi $d$ là số lẻ. Khi $d$ chẵn ($d = 2m$), $2^d \equiv 1 \pmod 3 \implies 1 + 2^d \equiv 2 \not\equiv 0 \pmod 3$, lỗi luôn được phát hiện $100\%$.
\end{proof}

\begin{figure}[!t]
\centering
\includegraphics[width=0.88\columnwidth]{fig3_3_bit_distance_parity_spectrum.png}\\[0.3ex]
\footnotesize{(a) Ma trận nhiệt phổ chẵn lẻ khoảng cách bit xác nhận Định lý 2}\\[1.0ex]
\includegraphics[width=0.88\columnwidth]{fig3_2_single_bit_fdr.png}\\[0.3ex]
\footnotesize{(b) Tỷ lệ phát hiện lỗi đơn bit SEU đạt tuyệt đối $100.00\%$}
\caption{Kiểm chứng thực nghiệm chiến dịch tiêm lỗi: (a) Ma trận nhiệt MBU xác nhận Định lý 2, (b) Tỷ lệ phát hiện lỗi đơn bit SEU theo vị trí bit.}
\label{fig:fault_campaign}
\end{figure}

Định lý~\ref{thm:masking} giải thích hoàn hảo kết quả thực nghiệm: trong 496 cặp bit của từ 32-bit, có đúng 240 cặp có $d$ chẵn (FDR $100\%$) và 256 cặp có $d$ lẻ (tự triệt tiêu thặng dư), tạo nên tỷ lệ phát hiện thô $240/496 = 48.39\%$.

\subsection{Kiểm Chứng Suy Luận Mạng Nơ-ron Đa Tầng (MLP)}
Chúng tôi tích hợp Secure MAC vào quá trình suy luận mạng nơ-ron đa tầng MLP ($64 \to 16 \to 10$) phân loại chữ số viết tay trên 100 mẫu thử nghiệm thực tế dưới 4 mức suất tiêm lỗi SEU ($0\%, 0.1\%, 1.0\%, 5.0\%$).

\begin{table}[!t]
\caption{Độ Chính Xác Suy Luận Mạng Nơ-ron MLP Dưới Các Mức Suất Lỗi}
\label{tab:nn_eval}
\centering
\resizebox{\columnwidth}{!}{
\begin{tabular}{ccccc}
\toprule
\textbf{Tỷ Lệ Tiêm SEU} & \textbf{Kiến Trúc} & \textbf{Độ Chính Xác} & \textbf{Suy Giảm $\Delta$} & \textbf{SDC / Lỗi Bị Bỏ Sót} \\
\midrule
$0.0\%$ (Sạch) & Baseline / Secure & $96.00\%$ & $0.00\%$ & Không có lỗi tiêm \\
$0.1\%$ & Baseline MAC & $84.00\%$ & $-12.00\%$ & $8$ trường hợp SDC \\
$0.1\%$ & \textbf{Secure MAC} & \textbf{96.00\%} & \textbf{0.00\%} & \textbf{0 SDC (Phát hiện 100\%)} \\
$1.0\%$ & Baseline MAC & $57.00\%$ & $-39.00\%$ & $39$ trường hợp SDC \\
$1.0\%$ & \textbf{Secure MAC} & \textbf{96.00\%} & \textbf{0.00\%} & \textbf{0 SDC (Phát hiện 100\%)} \\
$5.0\%$ & Baseline MAC & $18.00\%$ & $-78.00\%$ & $78$ trường hợp SDC \\
$5.0\%$ & \textbf{Secure MAC} & \textbf{96.00\%} & \textbf{0.00\%} & \textbf{0 SDC (Phát hiện 100\%)} \\
\bottomrule
\end{tabular}
}
\vspace{1mm}
\footnotesize{Độ trễ suy luận trung bình: $1.25\,\mu\text{s}$/mẫu ở $100$~MHz; bù trễ Rollback $<0.8\%$.}
\end{table}

Kết quả (Bảng~\ref{tab:nn_eval}) khẳng định: ở Baseline MAC, lỗi SEU làm suy sụp độ chính xác từ $96.00\%$ xuống $18.00\%$ (mất an toàn nghiêm trọng). Ngược lại, Secure MAC kích hoạt Rollback cô lập kịp thời mọi sai lệch, bảo toàn nguyên vẹn \textbf{$96.00\%$ độ chính xác} ($0.00\%$ suy giảm) dưới mọi tỷ lệ lỗi.

\subsection{Bộ Theo Dõi Thích Nghi EWMA Trực Tuyến}
Để bắt giữ các lỗi MBU có khoảng cách lẻ thuộc điểm mù của Lớp 1, module \texttt{ewma\_tracker.sv} theo dõi kỳ vọng $\mu_t$ và độ lệch $\text{MAD}_t$ trên luồng tính toán với trọng số $\alpha = 1/16$ ($>>> 4$) và $3.75 \times \text{MAD} = (4 \times \text{MAD}) - (\text{MAD} / 4)$, không tốn DSP và chỉ thêm $+32$ LUTs ($<0.4\%$ SoC).

\begin{figure}[!t]
\centering
\includegraphics[width=0.88\columnwidth]{fig_ml_04_fdr_static_vs_adaptive.png}\\[0.3ex]
\footnotesize{(a) So sánh dung lỗi MBU: Modulo-3, Ngưỡng Tĩnh và EWMA}\\[1.0ex]
\includegraphics[width=0.88\columnwidth]{fig_ml_05_ewma_convergence.png}\\[0.3ex]
\footnotesize{(b) Đặc tuyến phần cứng hội tụ thích nghi sau 16 chu kỳ}
\caption{Đặc tính bộ theo dõi EWMA thích nghi: (a) So sánh dung lỗi MBU giữa Modulo-3 Thô ($48.39\%$), Ngưỡng Tĩnh ($76.27\%$) và EWMA ($98.49\%$), (b) Đặc tuyến phần cứng hội tụ sau 16 chu kỳ.}
\label{fig:ml_ewma_combined}
\end{figure}

Đánh giá trên $50.000$ chu kỳ tính toán cho thấy hệ số $k=3.75$ đạt FDR $98.49\%$ với tỷ lệ báo động giả cực thấp $\text{FPR} = 0.04\%$ (Hình~\ref{fig:ml_ewma_combined}a), đồng thời hội tụ thích nghi nhanh chóng sau 16 chu kỳ (Hình~\ref{fig:ml_ewma_combined}b).

\subsection{Định Vị Điểm Nghẽn Bằng Đồ Thị GNN \& Gia Cố Hướng AI}
Chúng tôi mô hình hóa vi kiến trúc Secure MAC thành đồ thị có hướng $G = (V, E)$ gồm $|V| = 48$ nút logic và $|E| = 73$ cạnh luồng dữ liệu. Mô hình Graph Convolutional Network (GCN) 2 tầng ($d_{hidden} = 32$) đạt AUC-ROC $0.933 \pm 0.042$. Tại ngưỡng $0.5$, ma trận nhầm lẫn gộp đạt $\text{TP} = 478, \text{FP} = 36, \text{TN} = 460, \text{FN} = 26$ (Accuracy $93.80\%$, Recall $94.84\%$).

\begin{figure}[!t]
\centering
\includegraphics[width=0.92\columnwidth]{fig_ml_07_selective_hardening.png}
\caption{Gia cố chọn lọc hướng AI: Xếp hạng tổn thương nút GNN và đường cong tích lũy độ phủ bảo vệ Pareto.}
\label{fig:ml_hardening}
\end{figure}

Đặc tuyến Pareto Coverage (Hình~\ref{fig:ml_hardening}) chỉ ra: chỉ cần làm cứng $20\%$ thực thể phần cứng hàng đầu (như \texttt{shadow\_acc}, \texttt{out\_bus}, \texttt{reg\_c\_32}), hệ thống đã triệt tiêu được $45.1\%$ tổng số lỗ hổng SDC trong toàn mạch, bao phủ $>90\%$ độ nhạy lỗi datapath với chi phí phụ trội chỉ $+1.2\%$ LUTs. Đối sánh kiến trúc khẳng định: trong khi TMR chịu mức phạt diện tích quá nặng ($+220\%$ SoC) với tỷ số hiệu quả $0.45$ điểm FDR/\% diện tích, kiến trúc Modulo-3 + EWMA của chúng tôi đạt FDR MBU $98.49\%$ chỉ với $+4.65\%$ phụ trội SoC, mang lại hiệu suất \textbf{$21.18$ điểm/\% diện tích} (gấp \textbf{$47\times$ so với TMR}).

% ==============================================================================
\section{Thảo Luận Giới Hạn Nghiên Cứu}
\label{sec:limitations}
% ==============================================================================
Nhằm đảm bảo tính khách quan khoa học, chúng tôi nêu rõ 8 ranh giới kỹ thuật cốt lõi:
\begin{enumerate}
    \item \textbf{Lỗi Chế Độ Chung (Common-Mode):} Lỗi đồng thời tạo ra sai lệch là bội số của 3 ($|\Delta| \equiv 0 \pmod 3$) trên cả hai đường tính toán sẽ thoát khỏi CED.
    \item \textbf{Điểm Mù Lỗi Kép $1.51\%$:} Các lỗi MBU có khoảng cách lẻ và đột biến biên độ nhỏ dưới ngưỡng trượt $\tau_t$ của EWMA vẫn có thể lọt lưới.
    \item \textbf{Độ Sâu Checkpoint Đơn Tầng ($N=1$):} Shadow Accumulator chỉ lưu 1 trạng thái gần nhất; chùm lỗi kéo dài cần hàng đợi FIFO đa tầng.
    \item \textbf{Khả Năng Tự Kiểm Tra (TSC):} Bộ so sánh thặng dư chưa thiết kế theo chuẩn Totally Self-Checking hoàn chỉnh~\cite{mitra2000concurrent, rogenmoser2026who}.
    \item \textbf{Tiêm Lỗi Mô Phỏng vs Chiếu Xạ Silicon:} Đánh giá dựa trên mô phỏng RTL chu kỳ chính xác trên FPGA, cần tiếp tục thẩm định qua chùm proton thực tế trên ASIC.
    \item \textbf{Quy Mô Mạng Nơ-ron:} Nghiên cứu đã xác thực trên mạng MLP ($64 \to 16 \to 10$); việc mở rộng lên CNN lớn (ResNet) và tổng hợp ASIC (TSMC 28nm) là hướng tiếp theo.
    \item \textbf{Làm Ấm EWMA (16 Chu Kỳ):} Khi chuyển đổi ngữ cảnh đột ngột, EWMA cần 16 chu kỳ kích hoạt ngưỡng tĩnh dự phòng để tránh cảnh báo giả.
    \item \textbf{Giao Tiếp Đa Miền Xung Nhịp (CDC):} Khi accelerator chạy xung nhịp khác CPU, bus AXI4-Lite cần bổ sung Asynchronous FIFO CDC để chống hiện tượng siêu ổn định.
\end{enumerate}

% ==============================================================================
\section{Kết Luận \& Khả Năng Tái Lập}
\label{sec:conclusion}
% ==============================================================================
Bài báo đã trình bày giải pháp toàn diện cho bộ tăng tốc Neural Secure MAC dung lỗi tích hợp vào SoC RISC-V RV32I qua bus AMBA AXI4-Lite. Khai thác toàn cấu vành Modulo-3 và mô hình phòng thủ 3 lớp, kiến trúc đạt FDR $100.00\%$ đối với SEU, $98.49\%$ đối với MBU, và khôi phục an toàn trong 1 chu kỳ bằng Shadow Accumulator với phụ trội chỉ $+4.19\%$ diện tích SoC và $+5.55\%$ công suất động. Thử nghiệm suy luận mạng MLP INT8 bảo toàn nguyên vẹn $96.00\%$ độ chính xác. Toàn bộ mã nguồn RTL, testbench Cocotb, dữ liệu tiêm lỗi và mô hình GNN được công khai tại: \url{https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC}.

% ==============================================================================
% TÀI LIỆU THAM KHẢO (CHỌN LỌC 27 TÀI LIỆU THEN CHỐT CHO BẢN 8 TRANG)
% ==============================================================================
\IEEEtriggeratref{14}
\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
'''
    return tex

def main():
    target = 'paper/main_8pages.tex'
    tex = build_8_page_manuscript()
    with open(target, 'w', encoding='utf-8') as f:
        f.write(tex)
    print(f"[SUCCESS] Generated 8-page manuscript at: {target}")

if __name__ == '__main__':
    main()
