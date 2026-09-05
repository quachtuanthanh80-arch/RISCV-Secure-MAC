"""
Test runner for CPU Core sub-units (branch_cmp and regfile).
"""
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner


def run_all_cpu_unit_tests():
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    # 1. Run branch_cmp tests
    print("\n--- Running branch_cmp unit tests ---")
    sources_bc = [root_dir / "rtl" / "cpu" / "branch_cmp.sv"]
    runner_bc = get_runner("icarus")
    runner_bc.build(
        sources=sources_bc,
        hdl_toplevel="branch_cmp",
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner_bc.test(
        hdl_toplevel="branch_cmp",
        test_module="test_branch_cmp",
        waves=True,
    )

    # 2. Run regfile tests
    print("\n--- Running regfile unit tests ---")
    sources_rf = [root_dir / "rtl" / "cpu" / "regfile.sv"]
    runner_rf = get_runner("icarus")
    runner_rf.build(
        sources=sources_rf,
        hdl_toplevel="regfile",
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner_rf.test(
        hdl_toplevel="regfile",
        test_module="test_regfile",
        waves=True,
    )


if __name__ == "__main__":
    run_all_cpu_unit_tests()
