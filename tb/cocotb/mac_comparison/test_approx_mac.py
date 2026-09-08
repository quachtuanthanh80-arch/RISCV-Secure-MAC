"""
Cocotb Verification for Approximate Computing MAC.
Tests:
  1. Computes approximate dot-product.
  2. Verifies that numerical error is bounded within truncation tolerance.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_approx_mac_bounded_error(dut):
    """Verify Approximate MAC produces bounded inexact results."""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    test_vectors = [
        (25, 10, 500),   # 250 + 500 = 750
        (40, -6, 1000),  # -240 + 1000 = 760
        (-15, -15, 0),   # 225
        (50, 50, -2000), # 2500 - 2000 = 500
    ]

    for a, b, c in test_vectors:
        golden = a * b + c
        dut.a.value = a
        dut.b.value = b
        dut.c.value = c
        dut.start.value = 1
        await RisingEdge(dut.clk)
        dut.start.value = 0

        while not dut.valid.value:
            await RisingEdge(dut.clk)

        out_val = int(dut.out.value.to_signed())
        diff = abs(out_val - golden)

        dut._log.info(f"Approx MAC: {a}*{b} + {c} = {out_val} (Exact: {golden}, Absolute Error: {diff})")

        # For APPROX_BITS=4, max product discrepancy is <= 2^(4) = 16
        assert diff <= 16, f"Approximate error {diff} exceeded theoretical bound of 16!"
        await RisingEdge(dut.clk)
