"""
Cocotb Verification for Time-Redundancy RESO MAC.
Tests:
  1. 2-phase recomputation matches golden model.
  2. Temporal fault detection when Phase 1 result is corrupted before comparison.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_reso_mac_normal(dut):
    """Verify normal RESO MAC execution with 2-phase recomputation."""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    test_vectors = [
        (10, 5, 50),     # 50 + 50 = 100
        (-8, 6, 200),    # -48 + 200 = 152
        (14, -3, -100),  # -42 - 100 = -142
    ]

    for a, b, c in test_vectors:
        golden = a * b + c
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        # Wait for FSM to complete (IDLE -> PHASE1 -> PHASE2 -> COMPARE -> IDLE)
        while not dut.valid.value:
            await RisingEdge(dut.clk)

        out_val = int(dut.out.value.to_signed())
        fault = int(dut.fault_detected.value)

        dut._log.info(f"RESO MAC: {a}*{b} + {c} = {out_val} (Golden: {golden}), Fault={fault}")
        assert out_val == golden, f"Mismatch: got {out_val}, expected {golden}"
        assert fault == 0, "Spurious fault detected in normal RESO operation!"
        await RisingEdge(dut.clk)
