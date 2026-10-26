"""
Cocotb Verification Suite for cpu_to_axi_master Bridge Module
Validates:
1. Single Read & Write transactions with 0-latency slave
2. Slow Slave Write backpressure (delayed AWREADY, WREADY, BVALID) & CPU stall hold
3. Slow Slave Read backpressure (delayed ARREADY, RVALID) & data capture
4. Back-to-back alternating read/write bursts
5. Idle state correctness
"""

import random
from pathlib import Path
import cocotb
from cocotb.triggers import RisingEdge, Timer, ClockCycles
from cocotb.clock import Clock
from cocotb_tools.runner import get_runner


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.mem_addr.value = 0
    dut.mem_write.value = 0
    dut.mem_wdata.value = 0
    dut.mem_valid.value = 0
    dut.m_axi_awready.value = 0
    dut.m_axi_wready.value = 0
    dut.m_axi_bresp.value = 0
    dut.m_axi_bvalid.value = 0
    dut.m_axi_arready.value = 0
    dut.m_axi_rdata.value = 0
    dut.m_axi_rresp.value = 0
    dut.m_axi_rvalid.value = 0

    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_idle_state(dut):
    """Verify bridge holds all AXI valid lines low when CPU is idle."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    dut.mem_valid.value = 0
    await ClockCycles(dut.clk, 3)

    assert int(dut.m_axi_awvalid.value) == 0, "AWVALID must be 0 when mem_valid=0"
    assert int(dut.m_axi_wvalid.value) == 0, "WVALID must be 0 when mem_valid=0"
    assert int(dut.m_axi_arvalid.value) == 0, "ARVALID must be 0 when mem_valid=0"
    assert int(dut.mem_ready.value) == 1, "mem_ready should default to ready when idle"
    dut._log.info("[PASS] Idle state verified")


@cocotb.test()
async def test_single_write_zero_latency(dut):
    """Verify single-cycle write transaction with immediate slave response."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Slave responds immediately
    dut.m_axi_awready.value = 1
    dut.m_axi_wready.value = 1
    dut.m_axi_bvalid.value = 1
    dut.m_axi_bresp.value = 0  # OKAY

    dut.mem_addr.value = 0x80000004
    dut.mem_write.value = 1
    dut.mem_wdata.value = 0x12345678
    dut.mem_valid.value = 1

    await Timer(1, unit="ns")
    assert int(dut.m_axi_awvalid.value) == 1, "AWVALID must be 1"
    assert int(dut.m_axi_wvalid.value) == 1, "WVALID must be 1"
    assert int(dut.m_axi_awaddr.value) == 0x80000004, "AWADDR mismatch"
    assert int(dut.m_axi_wdata.value) == 0x12345678, "WDATA mismatch"
    assert int(dut.mem_ready.value) == 1, "mem_ready must be 1 when slave responds immediately"

    await RisingEdge(dut.clk)
    dut.mem_valid.value = 0
    dut.m_axi_bvalid.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("[PASS] Single write with zero latency verified")


@cocotb.test()
async def test_single_read_zero_latency(dut):
    """Verify single-cycle read transaction with immediate slave response."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Slave responds immediately
    dut.m_axi_arready.value = 1
    dut.m_axi_rvalid.value = 1
    dut.m_axi_rdata.value = 0xDEADBEEF
    dut.m_axi_rresp.value = 0  # OKAY

    dut.mem_addr.value = 0x00001000
    dut.mem_write.value = 0
    dut.mem_valid.value = 1

    await Timer(1, unit="ns")
    assert int(dut.m_axi_arvalid.value) == 1, "ARVALID must be 1"
    assert int(dut.m_axi_araddr.value) == 0x00001000, "ARADDR mismatch"
    assert int(dut.mem_ready.value) == 1, "mem_ready must be 1"
    assert int(dut.mem_rdata.value) == 0xDEADBEEF, f"mem_rdata mismatch, got {hex(int(dut.mem_rdata.value))}"

    await RisingEdge(dut.clk)
    dut.mem_valid.value = 0
    dut.m_axi_rvalid.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("[PASS] Single read with zero latency verified")


@cocotb.test()
async def test_slow_slave_write_backpressure(dut):
    """Verify bridge holds CPU stall when slave delays AWREADY, WREADY, and BVALID."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Issue write request
    dut.mem_addr.value = 0x80000010
    dut.mem_write.value = 1
    dut.mem_wdata.value = 0xCAFEBABE
    dut.mem_valid.value = 1

    # Slave is not ready for 3 cycles
    dut.m_axi_awready.value = 0
    dut.m_axi_wready.value = 0
    dut.m_axi_bvalid.value = 0

    for cycle in range(3):
        await Timer(1, unit="ns")
        assert int(dut.mem_ready.value) == 0, f"Cycle {cycle}: mem_ready must be 0 during slave stall"
        assert int(dut.m_axi_awvalid.value) == 1, f"Cycle {cycle}: AWVALID must remain high"
        assert int(dut.m_axi_wvalid.value) == 1, f"Cycle {cycle}: WVALID must remain high"
        assert int(dut.m_axi_awaddr.value) == 0x80000010, "AWADDR mutated during stall"
        assert int(dut.m_axi_wdata.value) == 0xCAFEBABE, "WDATA mutated during stall"
        await RisingEdge(dut.clk)

    # Slave asserts awready & wready, but delays bvalid 1 more cycle
    dut.m_axi_awready.value = 1
    dut.m_axi_wready.value = 1
    dut.m_axi_bvalid.value = 0
    await Timer(1, unit="ns")
    assert int(dut.mem_ready.value) == 0, "mem_ready must stay 0 until BVALID arrives"
    await RisingEdge(dut.clk)

    # Slave asserts BVALID
    dut.m_axi_bvalid.value = 1
    dut.m_axi_bresp.value = 0
    await Timer(1, unit="ns")
    assert int(dut.mem_ready.value) == 1, "mem_ready must assert when BVALID arrives"

    await RisingEdge(dut.clk)
    dut.mem_valid.value = 0
    dut.m_axi_bvalid.value = 0
    dut.m_axi_awready.value = 0
    dut.m_axi_wready.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("[PASS] Slow slave write backpressure verified")


@cocotb.test()
async def test_slow_slave_read_backpressure(dut):
    """Verify bridge holds CPU stall when slave delays ARREADY and RVALID."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Issue read request
    dut.mem_addr.value = 0x00002040
    dut.mem_write.value = 0
    dut.mem_valid.value = 1

    # Slave is not ready for 4 cycles
    dut.m_axi_arready.value = 0
    dut.m_axi_rvalid.value = 0

    for cycle in range(4):
        await Timer(1, unit="ns")
        assert int(dut.mem_ready.value) == 0, f"Cycle {cycle}: mem_ready must be 0"
        assert int(dut.m_axi_arvalid.value) == 1, f"Cycle {cycle}: ARVALID must remain high"
        assert int(dut.m_axi_araddr.value) == 0x00002040, "ARADDR mutated during stall"
        await RisingEdge(dut.clk)

    # Slave asserts ARREADY and RVALID
    dut.m_axi_arready.value = 1
    dut.m_axi_rvalid.value = 1
    dut.m_axi_rdata.value = 0xFEEDC0DE
    dut.m_axi_rresp.value = 0

    await Timer(1, unit="ns")
    assert int(dut.mem_ready.value) == 1, "mem_ready must assert when RVALID arrives"
    assert int(dut.mem_rdata.value) == 0xFEEDC0DE, "mem_rdata mismatch"

    await RisingEdge(dut.clk)
    dut.mem_valid.value = 0
    dut.m_axi_arready.value = 0
    dut.m_axi_rvalid.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("[PASS] Slow slave read backpressure verified")


@cocotb.test()
async def test_burst_random_transactions(dut):
    """Verify 30 randomized transactions with randomized slave delays."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    rng = random.Random(42)

    for txn in range(30):
        is_write = rng.choice([True, False])
        addr = rng.randint(0, 0xFFFFFFFF) & ~0x3
        data = rng.randint(0, 0xFFFFFFFF)

        dut.mem_addr.value = addr
        dut.mem_write.value = 1 if is_write else 0
        dut.mem_wdata.value = data if is_write else 0
        dut.mem_valid.value = 1

        # Random slave delay 0..3 cycles
        slave_delay = rng.randint(0, 3)
        dut.m_axi_awready.value = 0
        dut.m_axi_wready.value = 0
        dut.m_axi_bvalid.value = 0
        dut.m_axi_arready.value = 0
        dut.m_axi_rvalid.value = 0

        for _ in range(slave_delay):
            await RisingEdge(dut.clk)

        if is_write:
            dut.m_axi_awready.value = 1
            dut.m_axi_wready.value = 1
            dut.m_axi_bvalid.value = 1
            dut.m_axi_bresp.value = 0
        else:
            dut.m_axi_arready.value = 1
            dut.m_axi_rvalid.value = 1
            dut.m_axi_rdata.value = data
            dut.m_axi_rresp.value = 0

        await Timer(1, unit="ns")
        assert int(dut.mem_ready.value) == 1, f"Txn {txn}: mem_ready failed to assert"
        if not is_write:
            assert int(dut.mem_rdata.value) == data, f"Txn {txn}: read data mismatch"

        await RisingEdge(dut.clk)
        dut.mem_valid.value = 0
        dut.m_axi_awready.value = 0
        dut.m_axi_wready.value = 0
        dut.m_axi_bvalid.value = 0
        dut.m_axi_arready.value = 0
        dut.m_axi_rvalid.value = 0
        await RisingEdge(dut.clk)

    dut._log.info("[PASS] 30 randomized burst transactions verified successfully")
