"""
Comprehensive Unit Test Suite for RISC-V Pipeline Hazard Unit.
Tests:
1. Reset / Idle default states
2. RAW Data Hazard: Forwarding A/B from EX/MEM (forward = 2'b10)
3. RAW Data Hazard: Forwarding A/B from MEM/WB (forward = 2'b01)
4. Dual Hazard: Simultaneous forwarding on both operands (rs1 from MEM, rs2 from WB)
5. Forwarding Precedence: EX/MEM takes priority over MEM/WB when both target the same register
6. Zero-Register (x0) isolation: RegWrite to x0 never triggers forwarding
7. Load-Use Hazard Detection: 1-cycle stall bubble (stall_IF=1, stall_ID=1, flush_EX=1)
8. Load-Use on rs2
9. Load-Use with x0 target (no stall)
10. Control Hazard: Branch Taken pipeline flush (flush_ID=1)
11. Control Hazard: Unconditional Jump pipeline flush (flush_ID=1)
"""

import cocotb
from cocotb.triggers import Timer


def set_hazard_inputs(
    dut,
    rs1_EX=0,
    rs2_EX=0,
    rd_MEM=0,
    reg_write_MEM=0,
    rd_WB=0,
    reg_write_WB=0,
    mem_read_EX=0,
    rd_EX=0,
    rs1_ID=0,
    rs2_ID=0,
    branch_taken=0,
    jump=0,
):
    """Helper to apply inputs to the hazard unit."""
    dut.rs1_addr_EX.value = rs1_EX
    dut.rs2_addr_EX.value = rs2_EX
    dut.rd_addr_MEM.value = rd_MEM
    dut.RegWrite_MEM.value = reg_write_MEM
    dut.rd_addr_WB.value = rd_WB
    dut.RegWrite_WB.value = reg_write_WB
    dut.MemRead_EX.value = mem_read_EX
    dut.rd_addr_EX.value = rd_EX
    dut.rs1_addr_ID.value = rs1_ID
    dut.rs2_addr_ID.value = rs2_ID
    dut.branch_taken_ID.value = branch_taken
    dut.jump_ID.value = jump


@cocotb.test()
async def test_hazard_unit_defaults(dut):
    """Test 1: Default outputs when no hazards exist."""
    set_hazard_inputs(dut)
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 0, "Default forwardA must be 0"
    assert int(dut.forwardB_EX.value) == 0, "Default forwardB must be 0"
    assert int(dut.stall_IF.value) == 0, "Default stall_IF must be 0"
    assert int(dut.stall_ID.value) == 0, "Default stall_ID must be 0"
    assert int(dut.flush_ID.value) == 0, "Default flush_ID must be 0"
    assert int(dut.flush_EX.value) == 0, "Default flush_EX must be 0"
    dut._log.info("PASS: Hazard unit default outputs verified")


@cocotb.test()
async def test_forwarding_ex_mem_rs1(dut):
    """Test 2: Forwarding from EX/MEM to rs1 (forwardA = 2'b10)."""
    # EX stage needs x5, MEM stage writes to x5 with RegWrite=1
    set_hazard_inputs(dut, rs1_EX=5, rd_MEM=5, reg_write_MEM=1)
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 2, f"Expected forwardA=2 (EX/MEM), got {int(dut.forwardA_EX.value)}"
    assert int(dut.forwardB_EX.value) == 0, "forwardB should remain 0"
    dut._log.info("PASS: EX/MEM forwarding to rs1 verified")


@cocotb.test()
async def test_forwarding_ex_mem_rs2(dut):
    """Test 3: Forwarding from EX/MEM to rs2 (forwardB = 2'b10)."""
    set_hazard_inputs(dut, rs2_EX=7, rd_MEM=7, reg_write_MEM=1)
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 0, "forwardA should remain 0"
    assert int(dut.forwardB_EX.value) == 2, f"Expected forwardB=2 (EX/MEM), got {int(dut.forwardB_EX.value)}"
    dut._log.info("PASS: EX/MEM forwarding to rs2 verified")


@cocotb.test()
async def test_forwarding_mem_wb_rs1(dut):
    """Test 4: Forwarding from MEM/WB to rs1 (forwardA = 2'b01)."""
    set_hazard_inputs(dut, rs1_EX=12, rd_WB=12, reg_write_WB=1)
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 1, f"Expected forwardA=1 (MEM/WB), got {int(dut.forwardA_EX.value)}"
    assert int(dut.forwardB_EX.value) == 0, "forwardB should remain 0"
    dut._log.info("PASS: MEM/WB forwarding to rs1 verified")


@cocotb.test()
async def test_forwarding_mem_wb_rs2(dut):
    """Test 5: Forwarding from MEM/WB to rs2 (forwardB = 2'b01)."""
    set_hazard_inputs(dut, rs2_EX=15, rd_WB=15, reg_write_WB=1)
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 0, "forwardA should remain 0"
    assert int(dut.forwardB_EX.value) == 1, f"Expected forwardB=1 (MEM/WB), got {int(dut.forwardB_EX.value)}"
    dut._log.info("PASS: MEM/WB forwarding to rs2 verified")


@cocotb.test()
async def test_dual_forwarding(dut):
    """Test 6: Simultaneous forwarding to rs1 (MEM) and rs2 (WB)."""
    set_hazard_inputs(
        dut,
        rs1_EX=3,
        rs2_EX=4,
        rd_MEM=3,
        reg_write_MEM=1,
        rd_WB=4,
        reg_write_WB=1,
    )
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 2, "forwardA must be 2 (MEM)"
    assert int(dut.forwardB_EX.value) == 1, "forwardB must be 1 (WB)"
    dut._log.info("PASS: Dual forwarding to rs1 and rs2 verified simultaneously")


@cocotb.test()
async def test_forwarding_precedence(dut):
    """Test 7: Precedence test - when both MEM and WB write to same reg, MEM wins."""
    set_hazard_inputs(
        dut,
        rs1_EX=10,
        rd_MEM=10,
        reg_write_MEM=1,
        rd_WB=10,
        reg_write_WB=1,
    )
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 2, f"Expected forwardA=2 (EX/MEM priority), got {int(dut.forwardA_EX.value)}"
    dut._log.info("PASS: Forwarding precedence (MEM over WB) verified")


@cocotb.test()
async def test_x0_forwarding_protection(dut):
    """Test 8: Writes to x0 must never trigger forwarding."""
    set_hazard_inputs(
        dut,
        rs1_EX=0,
        rs2_EX=0,
        rd_MEM=0,
        reg_write_MEM=1,
        rd_WB=0,
        reg_write_WB=1,
    )
    await Timer(1, unit="ns")

    assert int(dut.forwardA_EX.value) == 0, "x0 must never trigger forwardA"
    assert int(dut.forwardB_EX.value) == 0, "x0 must never trigger forwardB"
    dut._log.info("PASS: x0 register forwarding protection verified")


@cocotb.test()
async def test_load_use_hazard_rs1(dut):
    """Test 9: Load-Use Hazard on rs1 triggers stall and flush."""
    # EX stage has LOAD instruction writing to x8, ID stage reads x8 on rs1
    set_hazard_inputs(
        dut,
        mem_read_EX=1,
        rd_EX=8,
        rs1_ID=8,
        rs2_ID=2,
    )
    await Timer(1, unit="ns")

    assert int(dut.stall_IF.value) == 1, "stall_IF must be 1 on load-use"
    assert int(dut.stall_ID.value) == 1, "stall_ID must be 1 on load-use"
    assert int(dut.flush_EX.value) == 1, "flush_EX must be 1 to insert bubble"
    assert int(dut.flush_ID.value) == 0, "flush_ID should not be 1 on load-use"
    dut._log.info("PASS: Load-Use hazard on rs1 correctly stalled and bubbled pipeline")


@cocotb.test()
async def test_load_use_hazard_rs2(dut):
    """Test 10: Load-Use Hazard on rs2 triggers stall and flush."""
    set_hazard_inputs(
        dut,
        mem_read_EX=1,
        rd_EX=9,
        rs1_ID=1,
        rs2_ID=9,
    )
    await Timer(1, unit="ns")

    assert int(dut.stall_IF.value) == 1, "stall_IF must be 1 on load-use rs2"
    assert int(dut.stall_ID.value) == 1, "stall_ID must be 1 on load-use rs2"
    assert int(dut.flush_EX.value) == 1, "flush_EX must be 1 to insert bubble"
    dut._log.info("PASS: Load-Use hazard on rs2 correctly stalled and bubbled pipeline")


@cocotb.test()
async def test_load_use_x0_no_stall(dut):
    """Test 11: Load writing to x0 must not cause stall."""
    set_hazard_inputs(
        dut,
        mem_read_EX=1,
        rd_EX=0,
        rs1_ID=0,
        rs2_ID=0,
    )
    await Timer(1, unit="ns")

    assert int(dut.stall_IF.value) == 0, "Load to x0 must not stall IF"
    assert int(dut.stall_ID.value) == 0, "Load to x0 must not stall ID"
    assert int(dut.flush_EX.value) == 0, "Load to x0 must not flush EX"
    dut._log.info("PASS: Load to x0 correctly ignored without stall")


@cocotb.test()
async def test_branch_taken_flush(dut):
    """Test 12: Branch Taken flushes the ID stage."""
    set_hazard_inputs(dut, branch_taken=1)
    await Timer(1, unit="ns")

    assert int(dut.flush_ID.value) == 1, "flush_ID must be 1 when branch taken"
    assert int(dut.stall_IF.value) == 0, "stall_IF should remain 0 on branch"
    dut._log.info("PASS: Branch Taken flush verified")


@cocotb.test()
async def test_jump_flush(dut):
    """Test 13: Unconditional Jump flushes the ID stage."""
    set_hazard_inputs(dut, jump=1)
    await Timer(1, unit="ns")

    assert int(dut.flush_ID.value) == 1, "flush_ID must be 1 on jump"
    dut._log.info("PASS: Jump flush verified")
