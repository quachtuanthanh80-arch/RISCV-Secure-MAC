import os
import re
import sys

def parse_comparative_ppa():
    report_dir = "synth/fpga_reports"
    macs = [
        ("baseline_mac", "Conventional Baseline (Không bảo vệ)"),
        ("approx_mac",   "Approximate MAC (Cắt giảm LSBs)"),
        ("reso_mac",     "Time Redundancy (RESO 2 chu kỳ)"),
        ("dmr_mac",      "Dual Modular Redundancy (DMR)"),
        ("tmr_mac",      "Triple Modular Redundancy (TMR)"),
        ("secure_mac",   "Secure MAC (Đề xuất: Modulo-3 + Rollback)")
    ]

    results = []

    for key, name in macs:
        util_file = os.path.join(report_dir, f"{key}_utilization.txt")
        timing_file = os.path.join(report_dir, f"{key}_timing.txt")
        power_file = os.path.join(report_dir, f"{key}_power.txt")

        if not (os.path.exists(util_file) and os.path.exists(timing_file) and os.path.exists(power_file)):
            print(f"[WAIT] {key} reports not all ready yet.")
            return None

        # Parse Utilization
        with open(util_file, "r", encoding="utf-8", errors="ignore") as f:
            u_txt = f.read()
        luts_m = re.search(r"Slice LUTs\*?\s*\|\s*(\d+)", u_txt)
        ffs_m = re.search(r"Slice Registers\s*\|\s*(\d+)", u_txt)
        dsps_m = re.search(r"DSPs\s*\|\s*(\d+)", u_txt)
        luts = int(luts_m.group(1)) if luts_m else 0
        ffs = int(ffs_m.group(1)) if ffs_m else 0
        dsps = int(dsps_m.group(1)) if dsps_m else 0

        # Parse Timing
        with open(timing_file, "r", encoding="utf-8", errors="ignore") as f:
            t_txt = f.read()
        wns_m = re.search(r"Design Timing Summary.*?WNS\(ns\)\s+TNS\(ns\).*?\n\s*[-]+\s+[-]+.*?\n\s*([-\d\.]+)", t_txt, re.DOTALL)
        if not wns_m:
            # Fallback regex
            wns_m = re.search(r"Worst Negative Slack \(WNS\):\s*([-\d\.]+)\s*ns", t_txt)
        wns = float(wns_m.group(1)) if wns_m else 0.0
        # Target period is 5.0 ns (200 MHz)
        t_crit = 5.0 - wns if wns < 0 else 5.0 - wns
        fmax = 1000.0 / t_crit

        # Parse Power
        with open(power_file, "r", encoding="utf-8", errors="ignore") as f:
            p_txt = f.read()
        tot_m = re.search(r"Total On-Chip Power \(W\)\s*\|\s*([\d\.]+)", p_txt)
        dyn_m = re.search(r"Dynamic \(W\)\s*\|\s*([\d\.]+)", p_txt)
        tot_power = float(tot_m.group(1)) * 1000 if tot_m else 0.0
        dyn_power = float(dyn_m.group(1)) * 1000 if dyn_m else 0.0

        results.append({
            "key": key,
            "name": name,
            "luts": luts,
            "ffs": ffs,
            "dsps": dsps,
            "wns": wns,
            "fmax": fmax,
            "dyn_power": dyn_power,
            "tot_power": tot_power
        })

    print("=" * 80)
    print(" AMD XILINX VIVADO 2026.1 MEASURED POST-IMPLEMENTATION PPA METRICS")
    print("=" * 80)
    for r in results:
        print(f"{r['key']:15} | LUTs: {r['luts']:4d} | FFs: {r['ffs']:4d} | DSPs: {r['dsps']:2d} | WNS: {r['wns']:+6.3f} ns | Fmax: {r['fmax']:6.2f} MHz | Dyn: {r['dyn_power']:4.1f} mW | Tot: {r['tot_power']:5.1f} mW")
    print("=" * 80)

    # Generate Markdown table
    md_content = "# Bảng Đối Sánh Thực Nghiệm PPA Giữa 6 Kiến Trúc MAC (AMD Xilinx Vivado 2026.1)\n\n"
    md_content += "> **Target FPGA Device**: AMD Xilinx Zynq-7000 (`xc7z020clg400-1`)\n"
    md_content += "> **Clock Constraint**: 200 MHz ($T_{clk} = 5.0\\text{ ns}$)\n"
    md_content += "> **Methodology**: Post-Implementation (Place & Route, Timing Closure, Vector-less Power Analysis)\n\n"
    md_content += "| Kiến Trúc MAC | Slice LUTs | Slice FFs | DSP48 | Slack WNS (ns) | $F_{max}$ (MHz) | Dynamic Power (mW) | Total Power (mW) | Cơ Chế Phục Hồi |\n"
    md_content += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
    
    recovery_mechanisms = {
        "baseline_mac": "Không bảo vệ (Dễ tổn thương SDC)",
        "approx_mac": "Sai số xấp xỉ (Inexact DNN)",
        "reso_mac": "Tính lại 2 chu kỳ (Giảm 50% thông lượng)",
        "dmr_mac": "Khóa bước (Lockstep Flag, ngắt phần mềm)",
        "tmr_mac": "Biểu quyết phần cứng đa số (0 chu kỳ)",
        "secure_mac": "Rollback tức thời 1 chu kỳ (Shadow Reg)"
    }

    for r in results:
        rec = recovery_mechanisms.get(r['key'], "-")
        md_content += f"| **{r['name']}** | {r['luts']} | {r['ffs']} | {r['dsps']} | {r['wns']:+.3f} | {r['fmax']:.1f} | {r['dyn_power']:.1f} | {r['tot_power']:.1f} | {rec} |\n"

    with open(os.path.join(report_dir, "mac_comparison_ppa.md"), "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[SUCCESS] Updated {os.path.join(report_dir, 'mac_comparison_ppa.md')}")

    return results

if __name__ == "__main__":
    parse_comparative_ppa()
