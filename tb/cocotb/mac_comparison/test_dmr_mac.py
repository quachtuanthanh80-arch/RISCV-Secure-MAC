"""
Cocotb Verification for DMR MAC (Dual Modular Redundancy).
Tests:
  1. Exact computation matching golden model.
  2. Fault Injection: Corrupting Core 1 induces immediate fault_detected assertion.
"""

import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def test_dmr_mac_normal(dut):
    """Verify normal DMR MAC operation produces exact golden results."""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.start.value = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.c.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Test cases: (A, B, C)
    test_vectors = [
        (15, 4, 100),    # 15*4 + 100 = 160
        (-10, 8, 200),   # -80 + 200 = 120
        (12, -5, -50),   # -60 - 50 = -110
        (0, 50, 999),    # 0 + 999 = 999
    ]

    for a, b, c in test_vectors:
        golden = a * b + c
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # Wait for 3-stage pipeline latency
        while not dut.valid.value:
            await RisingEdge(dut.clk)

        out_val = int(dut.out.value.to_signed())
        fault = int(dut.fault_detected.value)

        dut._log.info(f"DMR MAC: {a}*{b} + {c} = {out_val} (Golden: {golden}), Fault={fault}")
        assert out_val == golden, f"Mismatch: got {out_val}, expected {golden}"
        assert fault == 0, f"Spurious fault detected in normal operation!"
        await RisingEdge(dut.clk)


@cocotb.test()
async def test_dmr_mac_fault_detection(dut):
    """Verify lockstep comparator flags fault_detected when Core 1 is corrupted."""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    dut.a.value = 25
    dut.b.value = 4
    dut.c.value = 500  # Expected: 25*4 + 500 = 600
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Inject bit-flip into Core 1 intermediate pipeline register
    await RisingEdge(dut.clk)
    dut.c1_pipe_product.value = int(dut.c1_pipe_product.value) ^ 0x0080
    dut._log.info("[SEU FAULT INJECTION] Corrupted Core 1 pipe_product register")

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    fault = int(dut.fault_detected.value)
    dut._log.info(f"DMR Status after fault: fault_detected = {fault}")
    assert fault == 1, "DMR Lockstep failed to detect single-core discrepancy!"
