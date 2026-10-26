"""
Master Test Runner for NCKH RISC-V + Secure MAC SoC Project.
Runs all Linters, Unit Tests, SVA Assertions, and System-Level Cocotb Testbenches.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_step(step_name, cmd, cwd):
    print("\n" + "=" * 80)
    print(f"RUNNING STEP: {step_name}")
    print("=" * 80)
    start_time = time.time()
    
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=False,
    )
    elapsed = time.time() - start_time
    status = "PASSED" if proc.returncode == 0 else "FAILED"
    print(f"\n>>> [{status}] {step_name} (Time: {elapsed:.2f}s)\n")
    return proc.returncode == 0, elapsed


def main():
    root_dir = Path(__file__).resolve().parent
    py_cmd = [sys.executable]

    steps = [
        # 1. Linter execution: Analyzes RTL files for syntax and semantic errors using PySlang
        ("1. PySlang RTL Linter & Elaboration Check", py_cmd + [str(root_dir / "tools" / "linting" / "run_full_linter.py")]),
        
        # 2. Arithmetic Logic Unit corner cases and functional coverage
        ("2. Cocotb ALU Top Tests & Functional Coverage (30 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "alu_top" / "run_tests.py")]),
        
        # 3. Dedicated Hazard Unit testing (Forwarding, Stalls, Flushes, SVA)
        ("3. Cocotb Hazard Unit Tests & SVA Invariants (13 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "hazard_unit" / "run_tests.py")]),
        
        # 4. CPU Sub-Units (Branch Comparator & Regfile)
        ("4. Cocotb CPU Core Sub-Units (Branch & Regfile)", py_cmd + [str(root_dir / "tb" / "cocotb" / "cpu_units" / "run_tests.py")]),
        
        # 5. RV32I ISA Architectural Compliance Suite
        ("5. Cocotb RV32I ISA Compliance Suite (7 Micro-Programs)", py_cmd + [str(root_dir / "tb" / "cocotb" / "riscv_isa" / "run_tests.py")]),
        
        # 6. Validates normal operation and fault-tolerance of Secure MAC
        ("6. Cocotb Secure MAC Tests & Modulo-3 Coverage (10 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "secure_mac" / "run_mac_tests.py")]),
        
        # 7. EWMA Adaptive Anomaly Detection & Corner Cases (8 Cases)
        ("7. Cocotb EWMA Adaptive Anomaly & Corner Cases (8 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "secure_mac" / "test_adaptive_threshold.py")]),

        # 8. ISO 26262 ASIL D Dual-Rail Control-Path Fault Injection (5 Cases)
        ("8. Cocotb Dual-Rail Control-Path Fault Injection (5 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "secure_mac" / "test_control_fault.py")]),

        # 9. Complete SoC integration testing
        ("9. Cocotb SoC System Integration Tests (4 End-to-End Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "top_module" / "run_top_tests.py")]),
        
        # 10. Traditional SystemVerilog Self-Checking Testbenches
        ("10. Traditional SystemVerilog Self-Checking Testbenches", py_cmd + [str(root_dir / "tools" / "run_sv_tb.py")]),

        # 11. Statistical fault injection campaign
        ("11. Cocotb Fault Injection Campaign (4,400 Trials & Coverage)", py_cmd + [str(root_dir / "tb" / "cocotb" / "secure_mac" / "run_fault_campaign.py")]),
        
        # 12. AI workload resilience benchmark
        ("12. Cocotb AI Inference Resilience Benchmark (INT8 FC Layer)", py_cmd + [str(root_dir / "tb" / "cocotb" / "secure_mac" / "run_ai_resilience_test.py")]),

        # 13. CPU-to-AXI Master Bridge isolated test suite (6 Cases)
        ("13. Cocotb CPU-to-AXI Master Bridge Suite (6 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "cpu_axi_bridge" / "run_tests.py")]),

        # 14. Secure MAC AXI4-Lite IP test suite (Protocol, Byte Strobes, SLVERR, BIST, Telemetry, Masking)
        ("14. Cocotb Secure MAC AXI4-Lite IP Suite (10 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "secure_mac_axi" / "run_tests.py")]),

        # 15. Dedicated AXI4-Lite Crossbar Interconnect test suite (Routing, DECERR, Concurrent RW, Strobes)
        ("15. Cocotb AXI4-Lite Crossbar Interconnect Suite (6 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "axi_interconnect" / "run_tests.py")]),

        # 16. Full AXI-Lite SoC System Integration Suite (Reset, DMEM, MAC, Fault IRQ, Vector Dot, IRQ Clear)
        ("16. Cocotb Full AXI-Lite SoC Integration Suite (6 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "top_module_axi" / "run_tests.py")]),

        # 17. End-to-End Real-World Digits MLP AXI Inference Resilience Benchmark
        ("17. Cocotb Digits MLP AXI Resilience Benchmark (2 Cases)", py_cmd + [str(root_dir / "tb" / "cocotb" / "secure_mac_axi" / "run_ml_inference_test.py")]),

        # 18. Reputable Independent Benchmarks (Embench-IoT matmult-int & RISC-V ACT)
        ("18. Independent Benchmarks (Embench-IoT & RISC-V ACT)", py_cmd + [str(root_dir / "tb" / "cocotb" / "benchmarks" / "run_benchmarks.py")]),
    ]
    
    results = []
    all_passed = True
    
    for name, cmd in steps:
        passed, elapsed = run_step(name, cmd, root_dir)
        results.append((name, passed, elapsed))
        if not passed:
            all_passed = False
            
    print("\n" + "=" * 80)
    print("                      SUMMARY TEST DASHBOARD")
    print("=" * 80)
    print(f"{'Test Suite':<62} | {'Status':<8} | {'Time':<8}")
    print("-" * 80)
    for name, passed, elapsed in results:
        status_str = "[PASS]" if passed else "[FAIL]"
        print(f"{name:<62} | {status_str:<8} | {elapsed:>6.2f}s")
    print("=" * 80)
    
    # Generate Master Verification Report
    try:
        from tools.generate_verification_report import generate_report
        report_path = root_dir / "reports" / "master_verification_report.md"
        generate_report(results, report_path)
    except Exception as e:
        print(f"Note: Could not generate master report: {e}")

    if all_passed:
        print(f"\n[SUCCESS] ALL {len(steps)} COMPREHENSIVE VERIFICATION SUITES PASSED (100% SUCCESS)!\n")
        sys.exit(0)
    else:
        print("\n[FAIL] SOME TESTS FAILED. PLEASE CHECK LOGS ABOVE.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
