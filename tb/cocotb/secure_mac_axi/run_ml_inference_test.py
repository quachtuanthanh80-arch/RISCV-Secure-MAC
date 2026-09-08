"""
run_ml_inference_test.py
=============================================================================
Pytest and standalone runner for Cocotb Machine Learning Resilience Benchmark
on secure_mac_axi (AXI4-Lite IP).
Uses cocotb_tools.runner with Icarus Verilog.
=============================================================================
"""

import sys
from pathlib import Path
from cocotb_tools.runner import get_runner


def test_ml_inference_resilience_runner():
    """Build and run the full-model ML resilience benchmark for secure_mac_axi."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    sources = [
        root_dir / "rtl" / "mac" / "secure_mac_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker.sv",
        root_dir / "rtl" / "mac" / "secure_mac.v",
        root_dir / "rtl" / "mac" / "secure_mac_axi.v",
    ]
    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="secure_mac_axi",
        parameters={"IN_WIDTH": 8, "OUT_WIDTH": 16},
        build_args=["-g2012"],
        waves=False,
        always=True,
    )
    runner.test(
        hdl_toplevel="secure_mac_axi",
        test_module="test_ml_inference_fault",
        waves=False,
    )


if __name__ == "__main__":
    test_ml_inference_resilience_runner()
