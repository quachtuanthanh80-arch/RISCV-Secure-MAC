"""
Pytest and standalone runner for top_module_axi Cocotb tests.
Uses cocotb_tools.runner with Icarus Verilog.
"""
import os
import subprocess
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner, Icarus


def test_top_module_axi_runner():
    """Build and run all Cocotb tests for top_module_axi."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    sources = [
        root_dir / "rtl" / "cpu" / "alu.sv",
        root_dir / "rtl" / "cpu" / "branch_cmp.sv",
        root_dir / "rtl" / "cpu" / "control_unit.sv",
        root_dir / "rtl" / "cpu" / "hazard_unit.sv",
        root_dir / "rtl" / "cpu" / "hazard_unit_sva.sv",
        root_dir / "rtl" / "cpu" / "imem.sv",
        root_dir / "rtl" / "cpu" / "dmem.sv",
        root_dir / "rtl" / "cpu" / "dmem_axi.v",
        root_dir / "rtl" / "cpu" / "instruction_decoder.sv",
        root_dir / "rtl" / "cpu" / "pipe_if_id.sv",
        root_dir / "rtl" / "cpu" / "pipe_id_ex.sv",
        root_dir / "rtl" / "cpu" / "pipe_ex_mem.sv",
        root_dir / "rtl" / "cpu" / "pipe_mem_wb.sv",
        root_dir / "rtl" / "cpu" / "regfile.sv",
        root_dir / "rtl" / "cpu" / "riscv_cpu.sv",
        root_dir / "rtl" / "bus" / "cpu_to_axi_master.v",
        root_dir / "rtl" / "bus" / "axi_interconnect_1m2s.v",
        root_dir / "rtl" / "mac" / "secure_mac_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker.sv",
        root_dir / "rtl" / "mac" / "secure_mac.v",
        root_dir / "rtl" / "mac" / "secure_mac_axi.v",
        root_dir / "rtl" / "top" / "top_module_axi.v",
    ]

    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="top_module_axi",
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner.test(
        hdl_toplevel="top_module_axi",
        test_module="test_top_module_axi",
        waves=True,
    )


if __name__ == "__main__":
    test_top_module_axi_runner()
