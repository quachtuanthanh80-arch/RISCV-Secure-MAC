"""
Pytest and standalone runner for cpu_to_axi_master Cocotb tests.
Uses cocotb_tools.runner with Icarus Verilog.
"""
from pathlib import Path
from cocotb_tools.runner import get_runner


def test_cpu_axi_bridge_runner():
    """Build and run all Cocotb tests for cpu_to_axi_master."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    sources = [
        root_dir / "rtl" / "bus" / "cpu_to_axi_master_sva.sv",
        root_dir / "rtl" / "bus" / "cpu_to_axi_master.v",
    ]
    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="cpu_to_axi_master",
        parameters={"C_M_AXI_ADDR_WIDTH": 32, "C_M_AXI_DATA_WIDTH": 32},
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner.test(
        hdl_toplevel="cpu_to_axi_master",
        test_module="test_cpu_axi_bridge",
        waves=True,
    )


if __name__ == "__main__":
    test_cpu_axi_bridge_runner()
