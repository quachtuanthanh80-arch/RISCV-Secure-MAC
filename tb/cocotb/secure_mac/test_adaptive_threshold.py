"""
Cocotb Verification Suite for Online Adaptive Anomaly Detection (EWMA Tracker)
Validates:
1. Warmup Convergence: 16-sample baseline transition to dynamic 3-sigma tracking.
2. Sensitivity Gain: Anomaly detection on moderate errors that slip through static thresholds.
3. Workload Adaptation: Contraction and expansion when transitioning between layer workloads.
4. Corner Case 1: Warmup phase with all-zero inputs (threshold clamps to MIN_THRESHOLD_FLOOR).
5. Corner Case 2: alpha_sel switching mid-stream (no transient overflow or false alarms).
6. Corner Case 3: context_reset during warmup (proper counter abort & reset).
7. Corner Case 4: Extreme integer values with overflow guard in mean/mad accumulators.
8. Corner Case 5: Rapid oscillating inputs (+A / -A) with large variance tracking.
"""

from pathlib import Path
import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock
from cocotb_tools.runner import get_runner


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
    dut.context_reset.value = 0
    dut.alpha_sel.value = 1
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def send_mac_op(dut, a_val, b_val, c_val):
    """Drive MAC operation through pipeline stages cleanly."""
    await cocotb.triggers.FallingEdge(dut.clk)
    dut.a.value = to_unsigned(a_val, 8)
    dut.b.value = to_unsigned(b_val, 8)
    dut.c.value = to_unsigned(c_val, 32)
    dut.start.value = 1

    await cocotb.triggers.FallingEdge(dut.clk)
    dut.start.value = 0

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

    assert int(dut.u_ewma.warmup_done_out.value) == 0, "Warmup should start at 0"
    init_thresh = int(dut.u_ewma.threshold_out.value)
    assert init_thresh == 3276700, f"Expected default 3276700, got {init_thresh}"

    for _ in range(20):
        await send_mac_op(dut, 8, 8, 100)

    assert int(dut.u_ewma.warmup_done_out.value) == 1, "Warmup must complete after >= 16 samples"
    adapted_thresh = int(dut.u_ewma.threshold_out.value)
    assert adapted_thresh < 3276700, f"Threshold should adapt below static bound, got {adapted_thresh}"
    dut._log.info("[PASS] Warmup convergence verified!")


@cocotb.test()
async def test_sudden_anomaly_detection(dut):
    """Verify adaptive threshold catches an anomaly that slips through the static 3.27M bound."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    for _ in range(20):
        await send_mac_op(dut, 10, 10, 200)

    active_thresh = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Active adapted threshold: {active_thresh} (Static bound is 3,276,700)")

    fault_det, rollback, out_val = await send_mac_op(dut, 10, 10, 45000)
    assert fault_det == 1, "Expected fault_detected = 1 for 45,000 anomaly!"
    assert rollback == 1, "Expected rollback = 1 on anomaly!"
    dut._log.info("[PASS] Sudden anomaly caught by adaptive threshold!")


@cocotb.test()
async def test_workload_adaptation(dut):
    """Verify threshold contracts and expands smoothly across neural layer workload changes."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Workload A: Large inputs
    for _ in range(25):
        await send_mac_op(dut, 50, 50, 10000)
    thresh_A = int(dut.u_ewma.threshold_out.value)

    # Workload B: Small inputs
    for _ in range(35):
        await send_mac_op(dut, 2, 2, 10)
    thresh_B = int(dut.u_ewma.threshold_out.value)

    assert thresh_B < thresh_A, f"Threshold must contract: {thresh_B} should be < {thresh_A}"
    dut._log.info("[PASS] Dynamic workload adaptation verified successfully!")


@cocotb.test()
async def test_warmup_all_zeros(dut):
    """Corner 1: Verify all-zero inputs during warmup clamp cleanly to MIN_THRESHOLD_FLOOR."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    for _ in range(20):
        fault, rb, out_val = await send_mac_op(dut, 0, 0, 0)
        assert fault == 0, "No fault on valid zero inputs"
        assert rb == 0

    assert int(dut.u_ewma.warmup_done_out.value) == 1
    thresh = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Threshold for all-zero stream: {thresh}")
    # Floor is 2000 for 32-bit OUT_WIDTH
    assert thresh == 2000, f"Expected threshold clamped to MIN_THRESHOLD_FLOOR (2000), got {thresh}"
    dut._log.info("[PASS] Corner 1 (All-Zero Warmup Clamp) verified!")


@cocotb.test()
async def test_alpha_sel_switching_midstream(dut):
    """Corner 2: Verify switching alpha_sel between fast (0) and slow (1) mid-stream causes no false alarms."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Start with alpha_sel = 0 (fast adaptation 1/4)
    dut.alpha_sel.value = 0
    for _ in range(20):
        fault, rb, _ = await send_mac_op(dut, 5, 5, 50)
        assert fault == 0

    # Switch mid-stream to alpha_sel = 1 (slow steady-state 1/16)
    dut.alpha_sel.value = 1
    for _ in range(20):
        fault, rb, _ = await send_mac_op(dut, 5, 5, 50)
        assert fault == 0, "False alarm when switching alpha_sel to slow mode!"
        assert rb == 0

    # Switch back to fast mode
    dut.alpha_sel.value = 0
    for _ in range(15):
        fault, rb, _ = await send_mac_op(dut, 8, 8, 120)
        assert fault == 0, "False alarm when switching alpha_sel back to fast mode!"

    dut._log.info("[PASS] Corner 2 (alpha_sel midstream switching) verified!")


@cocotb.test()
async def test_context_reset_during_warmup(dut):
    """Corner 3: Verify context_reset aborts in-progress warmup and resets counter."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Stream 8 samples (< 16 samples)
    for _ in range(8):
        await send_mac_op(dut, 4, 4, 20)

    assert int(dut.u_ewma.warmup_done_out.value) == 0, "Warmup should not be done at 8 samples"

    # Pulse context_reset
    dut.context_reset.value = 1
    await ClockCycles(dut.clk, 2)
    dut.context_reset.value = 0
    await RisingEdge(dut.clk)

    # Verify counter cleared and threshold is DEFAULT_THRESHOLD
    thresh = int(dut.u_ewma.threshold_out.value)
    assert thresh == 3276700, f"Threshold after context_reset must be DEFAULT_THRESHOLD (3276700), got {thresh}"
    assert int(dut.u_ewma.warmup_done_out.value) == 0

    # Now stream 16 fresh samples to finish warmup
    for _ in range(16):
        await send_mac_op(dut, 4, 4, 20)

    assert int(dut.u_ewma.warmup_done_out.value) == 1, "Warmup should complete after 16 new samples"
    dut._log.info("[PASS] Corner 3 (context_reset during warmup) verified!")


@cocotb.test()
async def test_large_magnitude_overflow_protection(dut):
    """Corner 4: Verify large values do not cause accumulator sign wrap or false anomaly."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Stream positive large inputs (within normal 30,000 range)
    for _ in range(25):
        fault, rb, out_val = await send_mac_op(dut, 100, 100, 20000)
        assert fault == 0, f"False alarm on legitimate large input: out={out_val}"
        assert rb == 0

    mean_val = to_signed(int(dut.u_ewma.mean_out.value), 32)
    dut._log.info(f"Tracked mean for large input stream: {mean_val}")
    assert mean_val > 0, "Tracked mean should be positive and non-overflowed"

    # Stream negative inputs
    for _ in range(30):
        fault, rb, out_val = await send_mac_op(dut, -100, 50, -10000)
        assert fault == 0, f"False alarm on legitimate negative input: out={out_val}"
        assert rb == 0

    dut._log.info("[PASS] Corner 4 (Large magnitude overflow protection) verified!")


@cocotb.test()
async def test_rapid_oscillating_inputs(dut):
    """Corner 5: Verify rapid alternating signs (+A / -A) expand MAD appropriately without false alarms."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Alternate +500 and -500
    for i in range(40):
        c_in = 500 if (i % 2 == 0) else -500
        fault, rb, _ = await send_mac_op(dut, 0, 0, c_in)
        assert fault == 0, f"False alarm on oscillating input at iteration {i}"
        assert rb == 0

    mad_val = int(dut.u_ewma.mad_out.value)
    thresh = int(dut.u_ewma.threshold_out.value)
    dut._log.info(f"Tracked MAD for alternating input: {mad_val}, Threshold: {thresh}")
    assert mad_val > 300, f"MAD should expand to reflect oscillation, got {mad_val}"
    dut._log.info("[PASS] Corner 5 (Rapid oscillating inputs) verified!")


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
