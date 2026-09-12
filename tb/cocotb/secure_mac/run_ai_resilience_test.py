import os
from pathlib import Path
from cocotb_tools.runner import get_runner


def run_ai_resilience():
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    sources = [
        root_dir / "rtl" / "mac" / "secure_mac_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker.sv",
        root_dir / "rtl" / "mac" / "secure_mac.v",
    ]
    for src in sources:
        assert src.exists(), f"Source not found: {src}"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="secure_mac",
        build_args=["-g2012"],
        waves=False,
        always=True,
    )
    runner.test(
        hdl_toplevel="secure_mac",
        test_module="test_ai_inference_resilience",
        waves=False,
    )


if __name__ == "__main__":
    run_ai_resilience()
