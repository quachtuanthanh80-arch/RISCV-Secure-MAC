"""
Cocotb Verification for TMR MAC (Triple Modular Redundancy).
Tests:
  1. Exact computation matching golden model.
  2. Single-core fault injection: Injects SEU bit-flip into Core 1.
     Verifies majority voter masks error (out remains golden) and telemetry
     flags fault_detected=1 and fault_channel=2'b10.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_tmr_mac_normal(dut):
    """Verify normal TMR MAC operation matches golden model."""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    test_vectors = [
        (20, -3, 200),  # -60 + 200 = 140
        (-12, -8, 50),  # 96 + 50 = 146
        (30, 4, 1000),  # 120 + 1000 = 1120
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
        fault = int(dut.fault_detected.value)
        ch = int(dut.fault_channel.value)

        dut._log.info(f"TMR MAC: {a}*{b} + {c} = {out_val} (Golden: {golden}), Fault={fault}, Ch={ch}")
        assert out_val == golden, f"Mismatch: got {out_val}, expected {golden}"
        assert fault == 0, "Spurious fault detected in normal TMR operation!"
        await RisingEdge(dut.clk)


@cocotb.test()
async def test_tmr_mac_fault_masking(dut):
    """Verify majority voter masks single-core fault and outputs correct golden result."""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 0
    dut.start.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    a, b, c = 20, 5, 300  # Golden: 20*5 + 300 = 400
    golden = a * b + c

    dut.a.value = a
    dut.b.value = b
    dut.c.value = c
    dut.start.value = 1
    await RisingEdge(dut.clk)
    dut.start.value = 0

    # Inject bit-flip into Core 1 intermediate product
    await RisingEdge(dut.clk)
    try:
        dut.c1_pipe_product.value = int(dut.c1_pipe_product.value) ^ 0x00FF
    except AttributeError:
        dut.core_pipe_product[1].value = int(dut.core_pipe_product[1].value) ^ 0x00FF
    dut._log.info("[SEU FAULT INJECTION] Corrupted Core 1 intermediate product")

    # Wait for completion
    while not dut.valid.value:
        await RisingEdge(dut.clk)

    out_val = int(dut.out.value.to_signed())
    fault = int(dut.fault_detected.value)
    ch = int(dut.fault_channel.value)

    dut._log.info(f"TMR Output after SEU: out = {out_val} (Golden: {golden}), Fault={fault}, Channel={ch}")

    # Core 1 was corrupted, but majority voter (Core 0 & Core 2) must preserve exact golden result!
    assert out_val == golden, f"TMR failed to mask single-core fault! Got {out_val}, expected {golden}"
    assert fault == 1, "TMR telemetry failed to detect single-core discrepancy!"
    assert ch == 2, f"Expected fault_channel = 2 (Core 1), got {ch}"
