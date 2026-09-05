"""
Runner for RISC-V Pipeline Hazard Unit cocotb tests.
Uses cocotb_tools.runner with Icarus Verilog.
"""
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner


def test_hazard_unit_runner():
    """Build and run all cocotb tests for hazard_unit."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    sources = [
        root_dir / "rtl" / "cpu" / "hazard_unit.sv",
    ]
    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="hazard_unit",
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner.test(
        hdl_toplevel="hazard_unit",
        test_module="test_hazard_unit",
        waves=True,
    )


if __name__ == "__main__":
    test_hazard_unit_runner()
