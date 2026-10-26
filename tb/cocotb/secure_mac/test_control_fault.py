"""
Cocotb Dedicated Verification Suite for Control-Path Dual-Rail Fault Protection
Tests ISO 26262 ASIL D / IEC 61508 dual-rail complementary control registers in Secure MAC.
Validates:
1. Clean operation complementary invariant: valid_dx == ~valid_dx_n (control_fault = 0).
2. Stage 1 Control SEU Injection (valid_d1 == valid_d1_n) -> triggers fault_detected & rollback.
3. Stage 2 Control SEU Injection (valid_d2 == valid_d2_n) -> triggers fault_detected & rollback.
4. Stage 3 Control SEU Injection (valid_d3 == valid_d3_n) -> triggers fault_detected & rollback.
5. Post-fault recovery on subsequent clean cycles.
"""

from pathlib import Path
import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer, FallingEdge
from cocotb.clock import Clock
from cocotb_tools.runner import get_runner


def to_unsigned(val, bits):
    mask = (1 << bits) - 1
    return val & mask


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.start.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.c.value = 0
    dut.context_reset.value = 0
    dut.alpha_sel.value = 1
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_control_fault_clean_operation(dut):
    """Test 1: Verify dual-rail valid/valid_n complementarity during normal MAC execution."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.a.value = to_unsigned(10, 8)
    dut.b.value = to_unsigned(5, 8)
    dut.c.value = to_unsigned(50, 32)
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    for stage in range(4):
        await Timer(1, unit="ns")
        d1 = int(dut.valid_d1.value)
        d1_n = int(dut.valid_d1_n.value)
        d2 = int(dut.valid_d2.value)
        d2_n = int(dut.valid_d2_n.value)
        d3 = int(dut.valid_d3.value)
        d3_n = int(dut.valid_d3_n.value)
        ctrl_fault = int(dut.control_fault.value)

        assert d1 != d1_n, f"Stage {stage}: valid_d1 ({d1}) must be complement of valid_d1_n ({d1_n})"
        assert d2 != d2_n, f"Stage {stage}: valid_d2 ({d2}) must be complement of valid_d2_n ({d2_n})"
        assert d3 != d3_n, f"Stage {stage}: valid_d3 ({d3}) must be complement of valid_d3_n ({d3_n})"
        assert ctrl_fault == 0, f"Stage {stage}: Unexpected control_fault asserted!"
        await RisingEdge(dut.clk)

    dut._log.info("[PASS] Clean dual-rail complementarity verified across all stages")


@cocotb.test()
async def test_control_fault_injection_stage1(dut):
    """Test 2: Inject bit-flip into Stage 1 complementary valid register."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Prime shadow accumulator with known value: 10 * 5 + 50 = 100
    dut.a.value = to_unsigned(10, 8)
    dut.b.value = to_unsigned(5, 8)
    dut.c.value = to_unsigned(50, 32)
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await ClockCycles(dut.clk, 4)
    assert int(dut.out.value) == 100, f"Expected initial out=100, got {int(dut.out.value)}"

    # Start new operation: 20 * 2 + 100 = 140
    dut.a.value = to_unsigned(20, 8)
    dut.b.value = to_unsigned(2, 8)
    dut.c.value = to_unsigned(100, 32)
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Inject control SEU on valid_d1_n: force valid_d1_n to match valid_d1
    await FallingEdge(dut.clk)
    dut.valid_d1_n.value = dut.valid_d1.value
    await Timer(1, unit="ns")

    dut._log.info(f"Injected Stage 1 SEU: valid_d1={int(dut.valid_d1.value)}, valid_d1_n={int(dut.valid_d1_n.value)}")
    assert int(dut.control_fault.value) == 1, "control_fault must assert when valid_d1 == valid_d1_n"

    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1, "fault_detected must assert on control fault!"
    assert int(dut.rollback.value) == 1, "rollback must assert on control fault!"
    assert int(dut.out.value) == 100, f"Output must rollback to shadow accumulator (100), got {int(dut.out.value)}"
    dut._log.info("[PASS] Stage 1 control-path fault detected and mitigated successfully!")


@cocotb.test()
async def test_control_fault_injection_stage2(dut):
    """Test 3: Inject bit-flip into Stage 2 complementary valid register."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Prime shadow accumulator: 10 * 5 + 0 = 50
    dut.a.value = to_unsigned(10, 8)
    dut.b.value = to_unsigned(5, 8)
    dut.c.value = 0
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await ClockCycles(dut.clk, 4)

    # Start new operation
    dut.a.value = to_unsigned(8, 8)
    dut.b.value = to_unsigned(8, 8)
    dut.c.value = 50
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await RisingEdge(dut.clk)  # Advance to stage 2

    # Inject SEU on valid_d2_n
    await FallingEdge(dut.clk)
    dut.valid_d2_n.value = dut.valid_d2.value
    await Timer(1, unit="ns")

    assert int(dut.control_fault.value) == 1, "control_fault must assert for stage 2 violation"
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    assert int(dut.rollback.value) == 1
    assert int(dut.out.value) == 50, f"Output must rollback to 50, got {int(dut.out.value)}"
    dut._log.info("[PASS] Stage 2 control-path fault detected and mitigated successfully!")


@cocotb.test()
async def test_control_fault_injection_stage3(dut):
    """Test 4: Inject bit-flip into Stage 3 complementary valid register."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Prime shadow accumulator
    dut.a.value = to_unsigned(6, 8)
    dut.b.value = to_unsigned(7, 8)
    dut.c.value = 0
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await ClockCycles(dut.clk, 4)
    assert int(dut.out.value) == 42

    # Start new op
    dut.a.value = to_unsigned(3, 8)
    dut.b.value = to_unsigned(3, 8)
    dut.c.value = 42
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0
    await ClockCycles(dut.clk, 2)  # Advance to stage 3

    # Inject SEU on valid_d3_n
    await FallingEdge(dut.clk)
    dut.valid_d3_n.value = dut.valid_d3.value
    await Timer(1, unit="ns")

    assert int(dut.control_fault.value) == 1, "control_fault must assert for stage 3 violation"
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.fault_detected.value) == 1
    assert int(dut.rollback.value) == 1
    assert int(dut.out.value) == 42, f"Output must rollback to 42, got {int(dut.out.value)}"
    dut._log.info("[PASS] Stage 3 control-path fault detected and mitigated successfully!")


@cocotb.test()
async def test_control_fault_recovery(dut):
    """Test 5: Verify automatic recovery on subsequent clean operations after control fault."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Inject fault on idle pipeline
    await FallingEdge(dut.clk)
    dut.valid_d1_n.value = dut.valid_d1.value
    await Timer(1, unit="ns")
    assert int(dut.control_fault.value) == 1

    # Send new clean operation
    await FallingEdge(dut.clk)
    dut.a.value = to_unsigned(12, 8)
    dut.b.value = to_unsigned(10, 8)
    dut.c.value = 0
    dut.start.value = 1

    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Wait for completion
    await ClockCycles(dut.clk, 3)
    await Timer(1, unit="ns")

    assert int(dut.control_fault.value) == 0, "control_fault must clear on clean transaction"
    assert int(dut.fault_detected.value) == 0, "fault_detected must clear"
    assert int(dut.out.value) == 120, f"Expected output 120, got {int(dut.out.value)}"
    dut._log.info("[PASS] Post-fault recovery verified successfully!")


def test_control_fault_runner():
    """Build and run control-path fault injection cocotb tests."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent  # D:/NCKH

    sources = [
        root_dir / "rtl" / "mac" / "secure_mac_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker.sv",
        root_dir / "rtl" / "mac" / "secure_mac.v",
    ]
    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="secure_mac",
        parameters={"USE_ADAPTIVE_THRESHOLD": 0},
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner.test(
        hdl_toplevel="secure_mac",
        test_module="test_control_fault",
        waves=True,
    )


if __name__ == "__main__":
    test_control_fault_runner()
