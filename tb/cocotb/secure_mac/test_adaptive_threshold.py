"""
Cocotb Verification Suite for Online Adaptive Anomaly Detection (EWMA Tracker)
Validates:
1. Warmup Convergence: 16-sample baseline transition to dynamic 3-sigma tracking.
2. Sensitivity Gain: Anomaly detection on moderate errors that slip through static thresholds.
3. Workload Adaptation: Contraction and expansion when transitioning between layer workloads.
"""

import sys
import subprocess
from pathlib import Path
import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock
from cocotb_tools.runner import get_runner, Icarus


def to_signed(val, bits):
    mask = (1 << bits) - 1
    val = val & mask
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val


def to_unsigned(val, bits):
    mask = (1 << bits) - 1
    return val & mask


async def reset_dut(dut, cycles=5):
    dut.rst_n.value = 0
    dut.start.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.c.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def send_mac_op(dut, a_val, b_val, c_val):
    """Drive MAC operation through 3 pipeline stages cleanly."""
    await cocotb.triggers.FallingEdge(dut.clk)
    dut.a.value = to_unsigned(a_val, 8)
    dut.b.value = to_unsigned(b_val, 8)
    dut.c.value = to_unsigned(c_val, 32)
    dut.start.value = 1

    await cocotb.triggers.FallingEdge(dut.clk)
    dut.start.value = 0

    # Stage 1 -> Stage 2
    await cocotb.triggers.RisingEdge(dut.clk)
    await cocotb.triggers.Timer(1, unit="ns")

    # Advance until valid
    while int(dut.valid.value) == 0:
        await cocotb.triggers.RisingEdge(dut.clk)
        await cocotb.triggers.Timer(1, unit="ns")

    return int(dut.fault_detected.value), int(dut.rollback.value), to_signed(int(dut.out.value), 32)


@cocotb.test()
async def test_warmup_convergence(dut):
    """Verify EWMA warmup counter reaches 16 samples and transitions threshold."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut._log.info("Starting test_warmup_convergence: streaming 20 normal samples")
    
    # Check default threshold before warmup
    assert int(dut.u_ewma.warmup_done_out.value) == 0, "Warmup should start at 0"
    init_thresh = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Initial threshold (warmup): {init_thresh}")
    assert init_thresh == 3276700, f"Expected default 3276700, got {init_thresh}"

    # Stream 20 valid MAC operations with modest magnitude: 8 * 8 + 100 = 164
    for _ in range(20):
        await send_mac_op(dut, 8, 8, 100)

    # Sample count should have saturated at warmup done
    assert int(dut.u_ewma.warmup_done_out.value) == 1, "Warmup must complete after >= 16 samples"
    adapted_thresh = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Adapted threshold after warmup: {adapted_thresh}")
    assert adapted_thresh < 3276700, f"Threshold should adapt below static bound, got {adapted_thresh}"
    dut._log.info("[PASS] Warmup convergence verified!")


@cocotb.test()
async def test_sudden_anomaly_detection(dut):
    """Verify adaptive threshold catches an anomaly that slips through the static 3.27M bound."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Stream 20 samples with small range (10 * 10 + 200 = 300)
    for _ in range(20):
        await send_mac_op(dut, 10, 10, 200)

    active_thresh = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Active adapted threshold: {active_thresh} (Static bound is 3,276,700)")

    # Inject an out-of-distribution input: c = 45,000 (below 3.27M, but >> adapted threshold ~2,000)
    fault_det, rollback, out_val = await send_mac_op(dut, 10, 10, 45000)

    dut._log.info(f"Anomaly check: fault_detected={fault_det}, rollback={rollback}, out={out_val}")
    assert fault_det == 1, "Expected fault_detected = 1 for 45,000 anomaly!"
    assert rollback == 1, "Expected rollback = 1 on anomaly!"
    dut._log.info("[PASS] Sudden anomaly caught by adaptive threshold!")


@cocotb.test()
async def test_workload_adaptation(dut):
    """Verify threshold contracts and expands smoothly across neural layer workload changes."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Workload A: Large inputs (50 * 50 + 10000 = 12500)
    dut._log.info("Streaming Workload A (Large Magnitude)...")
    for _ in range(25):
        dut.a.value = to_unsigned(50, 8)
        dut.b.value = to_unsigned(50, 8)
        dut.c.value = to_unsigned(10000, 32)
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0
        await ClockCycles(dut.clk, 2)

    thresh_A = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Threshold for Workload A: {thresh_A}")

    # Workload B: Small inputs (2 * 2 + 10 = 14)
    dut._log.info("Streaming Workload B (Small Magnitude)...")
    for _ in range(35):
        dut.a.value = to_unsigned(2, 8)
        dut.b.value = to_unsigned(2, 8)
        dut.c.value = to_unsigned(10, 32)
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0
        await ClockCycles(dut.clk, 2)

    thresh_B = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Threshold for Workload B: {thresh_B}")

    assert thresh_B < thresh_A, f"Threshold must contract: {thresh_B} should be < {thresh_A}"
    dut._log.info("[PASS] Dynamic workload adaptation verified successfully!")


def test_adaptive_threshold_runner():
    """Build and run adaptive threshold cocotb tests."""
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
        parameters={"USE_ADAPTIVE_THRESHOLD": 1},
        build_args=["-g2012"],
        waves=True,
        always=True,
    )
    runner.test(
        hdl_toplevel="secure_mac",
        test_module="test_adaptive_threshold",
        waves=True,
    )


if __name__ == "__main__":
    test_adaptive_threshold_runner()
