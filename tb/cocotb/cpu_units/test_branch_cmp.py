"""
Cocotb Unit Tests for RISC-V Branch Comparator (branch_cmp).
Tests all 6 branch types with signed and unsigned edge-case values:
- BEQ (funct3 = 000)
- BNE (funct3 = 001)
- BLT (funct3 = 100, signed <)
- BGE (funct3 = 101, signed >=)
- BLTU (funct3 = 110, unsigned <)
- BGEU (funct3 = 111, unsigned >=)
- Extreme boundaries: 0x80000000 (-2147483648), 0x7FFFFFFF (+2147483647), 0xFFFFFFFF (-1 unsigned max).
"""

import cocotb
from cocotb.triggers import Timer


BEQ  = 0b000
BNE  = 0b001
BLT  = 0b100
BGE  = 0b101
BLTU = 0b110
BGEU = 0b111


async def check_branch(dut, a, b, funct3, en=1):
    dut.a.value = a & 0xFFFFFFFF
    dut.b.value = b & 0xFFFFFFFF
    dut.funct3.value = funct3
    dut.branch_en.value = en
    await Timer(1, unit="ns")
    return int(dut.branch_taken.value)


@cocotb.test()
async def test_beq_bne(dut):
    """Test BEQ and BNE operations."""
    # a == b
    res = await check_branch(dut, 100, 100, BEQ)
    assert res == 1, "BEQ 100==100 should be taken"
    res = await check_branch(dut, 100, 100, BNE)
    assert res == 0, "BNE 100==100 should NOT be taken"

    # a != b
    res = await check_branch(dut, 100, 200, BEQ)
    assert res == 0, "BEQ 100==200 should NOT be taken"
    res = await check_branch(dut, 100, 200, BNE)
    assert res == 1, "BNE 100==200 should be taken"
    dut._log.info("PASS: BEQ and BNE operations verified")


@cocotb.test()
async def test_signed_vs_unsigned_edge_cases(dut):
    """
    Crucial signed vs unsigned comparison edge cases:
    a = 0xFFFFFFFF (-1 signed, 4294967295 unsigned)
    b = 0x00000001 (+1 signed, 1 unsigned)
    """
    a = 0xFFFFFFFF
    b = 0x00000001

    # Signed comparison: -1 < 1 is TRUE -> BLT taken, BGE not taken
    res_blt = await check_branch(dut, a, b, BLT)
    assert res_blt == 1, "Signed: -1 < 1 must take BLT"
    res_bge = await check_branch(dut, a, b, BGE)
    assert res_bge == 0, "Signed: -1 >= 1 must NOT take BGE"

    # Unsigned comparison: 4294967295 < 1 is FALSE -> BLTU not taken, BGEU taken
    res_bltu = await check_branch(dut, a, b, BLTU)
    assert res_bltu == 0, "Unsigned: MAX < 1 must NOT take BLTU"
    res_bgeu = await check_branch(dut, a, b, BGEU)
    assert res_bgeu == 1, "Unsigned: MAX >= 1 must take BGEU"

    dut._log.info("PASS: Signed vs Unsigned -1 vs +1 corner case verified")


@cocotb.test()
async def test_min_max_signed_boundary(dut):
    """
    Min vs Max signed:
    a = 0x80000000 (INT32_MIN = -2147483648)
    b = 0x7FFFFFFF (INT32_MAX = +2147483647)
    """
    a = 0x80000000
    b = 0x7FFFFFFF

    # Signed: MIN < MAX -> BLT taken
    assert await check_branch(dut, a, b, BLT) == 1, "INT32_MIN < INT32_MAX should be taken"
    assert await check_branch(dut, b, a, BLT) == 0, "INT32_MAX < INT32_MIN should NOT be taken"

    # Unsigned: 0x80000000 > 0x7FFFFFFF -> BLTU not taken, BGEU taken
    assert await check_branch(dut, a, b, BLTU) == 0, "0x80000000 < 0x7FFFFFFF unsigned must be 0"
    assert await check_branch(dut, a, b, BGEU) == 1, "0x80000000 >= 0x7FFFFFFF unsigned must be 1"

    dut._log.info("PASS: INT32_MIN vs INT32_MAX boundary verified")


@cocotb.test()
async def test_branch_disabled(dut):
    """When branch_en=0, branch_taken must always be 0."""
    res = await check_branch(dut, 100, 100, BEQ, en=0)
    assert res == 0, "branch_taken must be 0 when branch_en is disabled"
    dut._log.info("PASS: Branch enable gating verified")
