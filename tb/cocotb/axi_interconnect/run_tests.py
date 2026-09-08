"""
Pytest and standalone runner for axi_interconnect_1m2s Cocotb tests.
Uses cocotb_tools.runner with Icarus Verilog.
"""
import os
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner


def test_axi_interconnect_runner():
    """Build and run all Cocotb tests for axi_interconnect_1m2s."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    sources = [
        root_dir / "rtl" / "bus" / "axi_interconnect_1m2s.v",
    ]
    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="axi_interconnect_1m2s",
        parameters={"C_AXI_ADDR_WIDTH": 32, "C_AXI_DATA_WIDTH": 32},
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner.test(
        hdl_toplevel="axi_interconnect_1m2s",
        test_module="test_axi_interconnect",
        waves=True,
    )


if __name__ == "__main__":
    test_axi_interconnect_runner()
