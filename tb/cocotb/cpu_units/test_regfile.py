"""
Cocotb Unit Tests for RISC-V Register File (regfile).
Tests:
1. Reset clears all registers (x0..x31 == 0)
2. Writes to general registers x1..x31 and read-back
3. Hardwired Zero Register (x0): Writing any non-zero value to x0 must still yield 0
4. Internal Forwarding (Simultaneous Read and Write on same clock cycle)
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.reg_write.value = 0
    dut.rs1_addr.value = 0
    dut.rs2_addr.value = 0
    dut.rd_addr.value = 0
    dut.rd_data.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_regfile_reset(dut):
    """Test 1: Reset clears all 32 registers."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    for i in range(32):
        dut.rs1_addr.value = i
        await Timer(1, unit="ns")
        assert int(dut.rs1_data.value) == 0, f"Register x{i} not 0 on reset!"
    dut._log.info("PASS: All 32 registers confirmed 0 after reset")


@cocotb.test()
async def test_write_and_read(dut):
    """Test 2: Write unique patterns to x1..x31 and read back."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Write each register
    for i in range(1, 32):
        await FallingEdge(dut.clk)
        dut.reg_write.value = 1
        dut.rd_addr.value = i
        val = ((i << 24) | (i << 16) | (i << 8) | i) & 0xFFFFFFFF
        dut.rd_data.value = val
        await RisingEdge(dut.clk)

    await FallingEdge(dut.clk)
    dut.reg_write.value = 0

    # Read back asynchronously
    for i in range(1, 32):
        dut.rs1_addr.value = i
        dut.rs2_addr.value = 32 - i
        await Timer(1, unit="ns")
        expected_rs1 = ((i << 24) | (i << 16) | (i << 8) | i) & 0xFFFFFFFF
        j = 32 - i
        expected_rs2 = ((j << 24) | (j << 16) | (j << 8) | j) & 0xFFFFFFFF
        assert int(dut.rs1_data.value) == expected_rs1, f"x{i} mismatch: expected {hex(expected_rs1)}, got {hex(int(dut.rs1_data.value))}"
        assert int(dut.rs2_data.value) == expected_rs2, f"x{j} mismatch"
    dut._log.info("PASS: Write and Read back across all registers x1..x31 verified")


@cocotb.test()
async def test_x0_hardwired_zero(dut):
    """Test 3: Writes to x0 must never change x0 from 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await FallingEdge(dut.clk)
    dut.reg_write.value = 1
    dut.rd_addr.value = 0
    dut.rd_data.value = 0xDEADBEEF
    await RisingEdge(dut.clk)

    await FallingEdge(dut.clk)
    dut.reg_write.value = 0
    dut.rs1_addr.value = 0
    dut.rs2_addr.value = 0
    await Timer(1, unit="ns")

    assert int(dut.rs1_data.value) == 0, "x0 must always be 0!"
    assert int(dut.rs2_data.value) == 0, "x0 must always be 0!"
    dut._log.info("PASS: Register x0 hardwired-zero verified")


@cocotb.test()
async def test_internal_forwarding(dut):
    """Test 4: Reading and writing to same register simultaneously forwards new data."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    await FallingEdge(dut.clk)
    dut.reg_write.value = 1
    dut.rd_addr.value = 7
    dut.rd_data.value = 0xCAFEBABE
    dut.rs1_addr.value = 7
    await Timer(1, unit="ns")

    assert int(dut.rs1_data.value) == 0xCAFEBABE, "Internal forwarding failed: did not see rd_data immediately!"
    dut._log.info("PASS: Regfile internal write-to-read forwarding verified")
