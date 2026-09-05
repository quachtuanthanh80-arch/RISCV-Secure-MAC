"""
Runner for Traditional SystemVerilog Self-Checking Testbenches.
Executes tb_secure_mac.sv and tb_top_module.sv via Icarus Verilog.
"""

import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, cwd, desc):
    print(f"--> [SV-TB] Running: {desc}")
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(f"[FAIL] {desc} exited with returncode {proc.returncode}")
        print("STDOUT:\n", proc.stdout)
        print("STDERR:\n", proc.stderr)
        return False
    print(f"[PASS] {desc}")
    return True


def main():
    root_dir = Path(__file__).resolve().parent.parent  # D:/NCKH
    sim_build = root_dir / "sim_build"
    sim_build.mkdir(parents=True, exist_ok=True)

    # 1. Run tb_secure_mac.sv
    vvp_mac = sim_build / "tb_secure_mac.vvp"
    cmd_compile_mac = [
        "iverilog",
        "-g2012",
        "-o", str(vvp_mac),
        str(root_dir / "rtl" / "mac" / "secure_mac_sva.sv"),
        str(root_dir / "rtl" / "mac" / "secure_mac.v"),
        str(root_dir / "tb" / "sv_tb" / "tb_secure_mac.sv"),
    ]
    if not run_cmd(cmd_compile_mac, root_dir, "Compiling tb_secure_mac.sv"):
        sys.exit(1)
    if not run_cmd(["vvp", str(vvp_mac)], root_dir, "Executing tb_secure_mac.vvp"):
        sys.exit(1)

    # 2. Run tb_top_module.sv
    vvp_top = sim_build / "tb_top_module.vvp"
    cpu_sources = [
        root_dir / "rtl" / "cpu" / "alu.sv",
        root_dir / "rtl" / "cpu" / "branch_cmp.sv",
        root_dir / "rtl" / "cpu" / "control_unit.sv",
        root_dir / "rtl" / "cpu" / "hazard_unit.sv",
        root_dir / "rtl" / "cpu" / "hazard_unit_sva.sv",
        root_dir / "rtl" / "cpu" / "imem.sv",
        root_dir / "rtl" / "cpu" / "dmem.sv",
        root_dir / "rtl" / "cpu" / "instruction_decoder.sv",
        root_dir / "rtl" / "cpu" / "pipe_if_id.sv",
        root_dir / "rtl" / "cpu" / "pipe_id_ex.sv",
        root_dir / "rtl" / "cpu" / "pipe_ex_mem.sv",
        root_dir / "rtl" / "cpu" / "pipe_mem_wb.sv",
        root_dir / "rtl" / "cpu" / "regfile.sv",
        root_dir / "rtl" / "cpu" / "riscv_cpu.sv",
        root_dir / "rtl" / "mac" / "secure_mac_sva.sv",
        root_dir / "rtl" / "mac" / "secure_mac.v",
        root_dir / "rtl" / "top" / "top_module.v",
        root_dir / "tb" / "sv_tb" / "tb_top_module.sv",
    ]
    cmd_compile_top = ["iverilog", "-g2012", "-o", str(vvp_top)] + [str(s) for s in cpu_sources]
    if not run_cmd(cmd_compile_top, root_dir, "Compiling tb_top_module.sv"):
        sys.exit(1)
    if not run_cmd(["vvp", str(vvp_top)], root_dir, "Executing tb_top_module.vvp"):
        sys.exit(1)

    print("\n[ALL SV TESTBENCHES PASSED CLEANLY!]")
    sys.exit(0)


if __name__ == "__main__":
    main()
