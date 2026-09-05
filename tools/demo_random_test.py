import sys
import os
import random

# Enable ANSI colors on Windows Terminal & cmd
if os.name == 'nt':
    os.system('')

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ANSI Color Codes
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_RED     = "\033[1;91m"
C_GREEN   = "\033[1;92m"
C_YELLOW  = "\033[1;93m"
C_BLUE    = "\033[1;94m"
C_MAGENTA = "\033[1;95m"
C_CYAN    = "\033[1;96m"
C_WHITE   = "\033[1;97m"
C_DIM     = "\033[2m"

def run_random_demo(num_tests=20):
    print(f"{C_CYAN}==================================================================================================={C_RESET}")
    print(f"{C_WHITE}{C_BOLD}             CHƯƠNG TRÌNH KIỂM THỬ TRỰC QUAN TRÊN TERMINAL (LIVE COLORFUL DEMO){C_RESET}")
    print(f"{C_YELLOW}             Kiểm tra Cơ chế Dung lỗi Modulo-3 CED & Bộ Giám sát Double-Check{C_RESET}")
    print(f"{C_CYAN}==================================================================================================={C_RESET}")
    print(f"\n{C_WHITE}Bắt đầu chạy {C_YELLOW}{C_BOLD}{num_tests}{C_RESET}{C_WHITE} ca thử ngẫu nhiên ({C_CYAN}1-Bit SEU{C_RESET}, {C_MAGENTA}2-Bit MBU{C_RESET}, {C_YELLOW}Burst Đa Bit{C_RESET})...\n{C_RESET}")
    
    # Table Header
    print(f"{C_BOLD}{C_WHITE}{'STT':<4} | {'Toán hạng (A×B+C)':<18} | {'Loại Lỗi Tiêm Vào':<22} | {'Trạng Thái':<18} | {'Cơ chế Hoạt động'}{C_RESET}")
    print(f"{C_DIM}-----+--------------------+------------------------+--------------------+----------------------------------{C_RESET}")
    
    passed_count = 0
    failed_count = 0
    
    for i in range(1, num_tests + 1):
        # 1. Generate random inputs
        a = random.randint(-128, 127)
        b = random.randint(-128, 127)
        c = random.randint(0, 1000)
        correct_mac = a * b + c
        
        # 2. Pick fault type
        fault_type = random.choices(["SEU_1BIT", "MBU_2BIT", "BURST_MBIT"], weights=[40, 35, 25])[0]
        
        corrupted_mac = correct_mac
        
        if fault_type == "SEU_1BIT":
            bit = random.randint(0, 31)
            corrupted_mac = correct_mac ^ (1 << bit)
            type_badge = f"{C_CYAN}1-Bit SEU (Bit {bit:2d}){C_RESET}"
        elif fault_type == "MBU_2BIT":
            b1, b2 = sorted(random.sample(range(32), 2))
            d = b2 - b1
            corrupted_mac = correct_mac ^ (1 << b1) ^ (1 << b2)
            type_badge = f"{C_MAGENTA}2-Bit MBU (d={d:2d}, b{b1}){C_RESET}"
        else:
            k = random.randint(3, 6)
            bits = random.sample(range(32), k)
            mask = 0
            for b_idx in bits:
                mask |= (1 << b_idx)
            corrupted_mac = correct_mac ^ mask
            type_badge = f"{C_YELLOW}{k}-Bit Burst ({','.join(map(str, sorted(bits)[:2]))}..){C_RESET}"
            
        # 3. Hardware Modulo-3 Arithmetic Residue Check
        expected_mod3 = ((a % 3) * (b % 3) + (c % 3)) % 3
        actual_mod3 = corrupted_mac % 3
        mod3_detected = (expected_mod3 != actual_mod3)
        
        # 4. Double-Check Sanity & Range Bound Check
        range_anomaly = (corrupted_mac > 3276700 or corrupted_mac < -3276700)
        
        # Combined Hardware Disagreement Trigger
        disagreement = mod3_detected or range_anomaly
        
        expr_str = f"{a}×{b}+{c}"
        if len(expr_str) > 16:
            expr_str = expr_str[:15] + ".."
            
        if disagreement:
            passed_count += 1
            status_badge = f"{C_GREEN}[PASS DETECTED]{C_RESET}"
            if mod3_detected:
                mech_str = f"{C_GREEN}✔ Bắt bởi Modulo-3 CED -> Rollback 1-CK{C_RESET}"
            else:
                mech_str = f"{C_CYAN}✔ Bắt bởi Sanity Double-Check -> Rollback{C_RESET}"
        else:
            failed_count += 1
            status_badge = f"{C_RED}[FAIL SDC ERROR]{C_RESET}"
            mech_str = f"{C_RED}✘ Lọt lỗi (Triệt tiêu thặng dư Δ ≡ 0 mod 3){C_RESET}"
            
        print(f"{C_WHITE}{i:<4}{C_RESET} | {C_WHITE}{expr_str:<18}{C_RESET} | {type_badge:<31} | {status_badge:<27} | {mech_str}")
        
    print(f"{C_DIM}-----+--------------------+------------------------+--------------------+----------------------------------{C_RESET}")
    
    # Summary Card
    pass_pct = (passed_count / num_tests) * 100
    fail_pct = (failed_count / num_tests) * 100
    
    print(f"\n{C_BLUE}==================================================================================================={C_RESET}")
    print(f"{C_WHITE}{C_BOLD}                                   TỔNG KẾT THỰC NGHIỆM TIÊM LỖI{C_RESET}")
    print(f"{C_BLUE}==================================================================================================={C_RESET}")
    print(f"{C_WHITE}  Tổng số ca thử nghiệm ngẫu nhiên         : {C_BOLD}{num_tests:<6}{C_RESET}")
    print(f"{C_WHITE}  Số ca {C_GREEN}AN TOÀN (Phát hiện & Khôi phục){C_WHITE}    : {C_GREEN}{C_BOLD}{passed_count:<4} ca ({pass_pct:>5.1f}%){C_RESET}")
    print(f"{C_WHITE}  Số ca {C_RED}LỌT LỖI (Silent Data Corruption){C_WHITE}   : {C_RED}{C_BOLD}{failed_count:<4} ca ({fail_pct:>5.1f}%){C_RESET}")
    print(f"{C_BLUE}==================================================================================================={C_RESET}")
    print(f"{C_YELLOW}✦ Ghi chú phân tích:{C_RESET}")
    print(f"  • {C_GREEN}100% Lỗi đơn bit SEU{C_RESET} luôn được Modulo-3 phát hiện tức thời và tự động khôi phục trong 1 chu kỳ.")
    print(f"  • {C_CYAN}Lỗi 2-bit và Burst đa bit{C_RESET} được bảo vệ phối hợp bởi Modulo-3 và bộ giám sát phạm vi Double-Check.")
    print(f"  • {C_RED}Các ca lọt lỗi (SDC){C_RESET} xảy ra khi vector lỗi rơi đúng vào bội số của 3 (được triệt tiêu hoàn toàn khi layout Bit-Interleaving).\n")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    run_random_demo(n)
