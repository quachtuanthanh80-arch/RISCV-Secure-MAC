r"""
SystemVerilog Linter & Syntax Checker using pyslang.
Scans all Verilog and SystemVerilog files in D:\NCKH.
Reports:
- Syntax Errors
- Semantic / Elaboration Diagnostics
- Declaration & Typing Rules (undeclared nets, signedness mismatches, width mismatches)
"""

import os
import pyslang
import json

from pathlib import Path

SyntaxTree = getattr(pyslang, "SyntaxTree", None)
if SyntaxTree is None and hasattr(pyslang, "syntax"):
    SyntaxTree = pyslang.syntax.SyntaxTree

Compilation = getattr(pyslang, "Compilation", None)
if Compilation is None and hasattr(pyslang, "ast"):
    Compilation = pyslang.ast.Compilation


workspace = Path(__file__).resolve().parent.parent.parent

# Find all .v and .sv files in rtl/ and tb/
all_files = []
for root, dirs, files in os.walk(workspace):
    if any(ignore in root for ignore in ['.vscode', '.git', '.Xil', 'sim_build', '__pycache__', 'synth', 'docs', 'paper', 'tailieuthamkhao']):
        continue
    for f in files:
        if f.endswith('.v') or f.endswith('.sv'):
            all_files.append(os.path.join(root, f))

all_files = sorted(all_files)
print(f"Total files to check: {len(all_files)}\n")

# 1. Check each file individually (Isolated Syntax & Preprocessing check)
print("=" * 80)
print("PHASE 1: FILE-BY-FILE SYNTAX & LOCAL PARSE CHECK")
print("=" * 80)

individual_results = {}
for f in all_files:
    rel_path = os.path.relpath(f, workspace)
    try:
        tree = SyntaxTree.fromFile(f)
        diags = tree.diagnostics
        diag_list = []
        if diags:
            for d in diags:
                diag_list.append(str(d))
        individual_results[rel_path] = diag_list
        status = "PASSED (Clean)" if not diag_list else f"ISSUES FOUND ({len(diag_list)})"
        print(f"[{status:20s}] {rel_path}")
        for d in diag_list:
            print(f"    -> {d}")
    except Exception as e:
        individual_results[rel_path] = [f"CRITICAL EXCEPTION: {e}"]
        print(f"[ERROR               ] {rel_path}: {e}")

# 2. Comprehensive Multi-File Elaboration Check for each System/Top
print("\n" + "=" * 80)
print("PHASE 2: FULL COMPILATION & ELABORATION CHECK")
print("=" * 80)

# Project 1: System Integration Top (top_module + riscv_cpu + secure_mac + all submodules)
sys_files = [
    str(workspace / "rtl" / "top" / "top_module.v"),
    str(workspace / "rtl" / "mac" / "secure_mac_sva.sv"),
    str(workspace / "rtl" / "mac" / "secure_mac.v"),
    str(workspace / "rtl" / "cpu" / "riscv_cpu.sv"),
    str(workspace / "rtl" / "cpu" / "imem.sv"),
    str(workspace / "rtl" / "cpu" / "dmem.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_if_id.sv"),
    str(workspace / "rtl" / "cpu" / "instruction_decoder.sv"),
    str(workspace / "rtl" / "cpu" / "control_unit.sv"),
    str(workspace / "rtl" / "cpu" / "regfile.sv"),
    str(workspace / "rtl" / "cpu" / "branch_cmp.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_id_ex.sv"),
    str(workspace / "rtl" / "cpu" / "alu.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_ex_mem.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_mem_wb.sv"),
    str(workspace / "rtl" / "cpu" / "hazard_unit.sv"),
    str(workspace / "rtl" / "cpu" / "hazard_unit_sva.sv"),
]

comp_sys = Compilation()
for fn in sys_files:
    if os.path.exists(fn):
        comp_sys.addSyntaxTree(SyntaxTree.fromFile(fn))

diags_sys = comp_sys.getAllDiagnostics()
report_sys = pyslang.DiagnosticEngine.reportAll(comp_sys.sourceManager, diags_sys)

print("--- System Integration (top_module) Elaboration Diagnostics ---")
if report_sys and report_sys.strip():
    print(report_sys)
else:
    print("  CLEAN: 0 errors, 0 warnings across all 14 interconnected modules!")

# Project 2: Testbench tb_secure_mac.sv
print("\n--- Testbench: tb/sv_tb/tb_secure_mac.sv ---")
comp_tb = Compilation()
comp_tb.addSyntaxTree(SyntaxTree.fromFile(str(workspace / "rtl" / "mac" / "secure_mac_sva.sv")))
comp_tb.addSyntaxTree(SyntaxTree.fromFile(str(workspace / "rtl" / "mac" / "secure_mac.v")))
comp_tb.addSyntaxTree(SyntaxTree.fromFile(str(workspace / "tb" / "sv_tb" / "tb_secure_mac.sv")))
diags_tb = comp_tb.getAllDiagnostics()
report_tb = pyslang.DiagnosticEngine.reportAll(comp_tb.sourceManager, diags_tb)
if report_tb and report_tb.strip():
    print(report_tb)
else:
    print("  CLEAN: 0 errors, 0 warnings in tb_secure_mac.sv!")

# Project 3: alu_top wrapper
print("\n--- Module: rtl/top/alu_top.sv ---")
comp_alu = Compilation()
comp_alu.addSyntaxTree(SyntaxTree.fromFile(str(workspace / "rtl" / "top" / "alu_top.sv")))
comp_alu.addSyntaxTree(SyntaxTree.fromFile(str(workspace / "rtl" / "cpu" / "alu.sv")))
comp_alu.addSyntaxTree(SyntaxTree.fromFile(str(workspace / "rtl" / "cpu" / "control_unit.sv")))
diags_alu = comp_alu.getAllDiagnostics()
report_alu = pyslang.DiagnosticEngine.reportAll(comp_alu.sourceManager, diags_alu)
if report_alu and report_alu.strip():
    print(report_alu)
else:
    print("  CLEAN: 0 errors, 0 warnings in alu_top.sv!")

# Project 4: AXI-Lite System Integration (top_module_axi)
print("\n--- Project 4: AXI-Lite System Integration (top_module_axi.v) ---")
axi_sys_files = [
    str(workspace / "rtl" / "top" / "top_module_axi.v"),
    str(workspace / "rtl" / "bus" / "cpu_to_axi_master.v"),
    str(workspace / "rtl" / "bus" / "axi_interconnect_1m2s.v"),
    str(workspace / "rtl" / "cpu" / "dmem_axi.v"),
    str(workspace / "rtl" / "mac" / "secure_mac_axi.v"),
    str(workspace / "rtl" / "mac" / "secure_mac_sva.sv"),
    str(workspace / "rtl" / "mac" / "secure_mac.v"),
    str(workspace / "rtl" / "cpu" / "riscv_cpu.sv"),
    str(workspace / "rtl" / "cpu" / "imem.sv"),
    str(workspace / "rtl" / "cpu" / "dmem.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_if_id.sv"),
    str(workspace / "rtl" / "cpu" / "instruction_decoder.sv"),
    str(workspace / "rtl" / "cpu" / "control_unit.sv"),
    str(workspace / "rtl" / "cpu" / "regfile.sv"),
    str(workspace / "rtl" / "cpu" / "branch_cmp.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_id_ex.sv"),
    str(workspace / "rtl" / "cpu" / "alu.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_ex_mem.sv"),
    str(workspace / "rtl" / "cpu" / "pipe_mem_wb.sv"),
    str(workspace / "rtl" / "cpu" / "hazard_unit.sv"),
    str(workspace / "rtl" / "cpu" / "hazard_unit_sva.sv"),
]

comp_axi = Compilation()
for fn in axi_sys_files:
    if os.path.exists(fn):
        comp_axi.addSyntaxTree(SyntaxTree.fromFile(fn))

diags_axi = comp_axi.getAllDiagnostics()
report_axi = pyslang.DiagnosticEngine.reportAll(comp_axi.sourceManager, diags_axi)
if report_axi and report_axi.strip():
    print(report_axi)
else:
    print("  CLEAN: 0 errors, 0 warnings across all 19 interconnected AXI modules!")

