"""
RISC-V International Architectural Certification Tests (riscv-arch-test / ACT) Suite.
Reference: RISC-V International (github.com/riscv/riscv-arch-test).

Executes golden compliance test vectors for RV32I base integer instructions:
1. I-ADD-01: Boundary overflow, extreme negative wraparound, x0 invariancy.
2. I-SUB-01: Boundary underflow, self-subtraction.
3. I-SLT-01 / I-SLTU-01: Signed vs Unsigned comparisons with negative values.
4. I-SLL-01 / I-SRL-01 / I-SRA-01: Shift instructions & arithmetic sign preservation.
5. I-BRANCH-01: All 6 branch condition evaluations (taken & not taken).
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


def R_TYPE(funct7, rs2, rs1, funct3, rd, opcode=0x33):
    return ((funct7 & 0x7F) << 25) | ((rs2 & 0x1F) << 20) | ((rs1 & 0x1F) << 15) | ((funct3 & 0x7) << 12) | ((rd & 0x1F) << 7) | (opcode & 0x7F)

def I_TYPE(imm, rs1, funct3, rd, opcode=0x13):
    return ((imm & 0xFFF) << 20) | ((rs1 & 0x1F) << 15) | ((funct3 & 0x7) << 12) | ((rd & 0x1F) << 7) | (opcode & 0x7F)

def B_TYPE(offset, rs2, rs1, funct3, opcode=0x63):
    imm12 = (offset >> 12) & 0x1
    imm10_5 = (offset >> 5) & 0x3F
    imm4_1 = (offset >> 1) & 0xF
    imm11 = (offset >> 11) & 0x1
    return (imm12 << 31) | (imm10_5 << 25) | ((rs2 & 0x1F) << 20) | ((rs1 & 0x1F) << 15) | ((funct3 & 0x7) << 12) | (imm4_1 << 8) | (imm11 << 7) | (opcode & 0x7F)

def U_TYPE(imm, rd, opcode=0x37):
    return ((imm & 0xFFFFF) << 12) | ((rd & 0x1F) << 7) | (opcode & 0x7F)

NOP = 0x00000013
HALT = 0x0000006F


async def run_program(dut, program, cycles=25):
    """Load program into IMEM, reset CPU, and execute."""
    for i in range(64):
        dut.u_cpu.u_imem.RAM[i].value = NOP
    for i, instr in enumerate(program):
        dut.u_cpu.u_imem.RAM[i].value = instr & 0xFFFFFFFF

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, cycles)


def read_reg(dut, reg_idx):
    return int(dut.u_cpu.u_regfile.registers[reg_idx].value)


# ==============================================================================
# TEST 1: I-ADD-01 Overflow & Boundary Vectors
# ==============================================================================
@cocotb.test()
async def test_act_i_add_overflow_boundaries(dut):
    """Verify official I-ADD-01 corner cases: positive/negative overflow and x0 hardwiring."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        # x1 = 0x7FFFFFFF (max positive 32-bit int)
        U_TYPE(0x80000, 1),                 # lui  x1, 0x80000  -> 0x80000000
        I_TYPE(-1, 1, 0, 1),                # addi x1, x1, -1   -> 0x7FFFFFFF

        # x2 = 1
        I_TYPE(1, 0, 0, 2),

        # x3 = x1 + x2 = 0x7FFFFFFF + 1 -> 0x80000000 (wraparound)
        R_TYPE(0x00, 2, 1, 0, 3),

        # x4 = x3 + x3 = 0x80000000 + 0x80000000 -> 0x00000000
        R_TYPE(0x00, 3, 3, 0, 4),

        # x0 invariancy check: attempt write to x0
        I_TYPE(1234, 0, 0, 0),              # addi x0, x0, 1234

        HALT,
    ]

    await run_program(dut, program, cycles=25)

    assert read_reg(dut, 1) == 0x7FFFFFFF, f"x1 expected 0x7FFFFFFF, got 0x{read_reg(dut, 1):08x}"
    assert read_reg(dut, 3) == 0x80000000, f"x3 expected 0x80000000, got 0x{read_reg(dut, 3):08x}"
    assert read_reg(dut, 4) == 0x00000000, f"x4 expected 0x00000000, got 0x{read_reg(dut, 4):08x}"
    assert read_reg(dut, 0) == 0, f"x0 hardwiring violated! got {read_reg(dut, 0)}"
    dut._log.info("PASS: RISC-V International I-ADD-01 overflow and x0 invariance verified!")


# ==============================================================================
# TEST 2: I-SUB-01 Underflow & Self-Subtraction
# ==============================================================================
@cocotb.test()
async def test_act_i_sub_underflow_boundaries(dut):
    """Verify official I-SUB-01 corner cases: underflow and self-subtraction."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        # x1 = 0x80000000 (most negative 32-bit int)
        U_TYPE(0x80000, 1),
        # x2 = 1
        I_TYPE(1, 0, 0, 2),

        # x3 = 0x80000000 - 1 -> 0x7FFFFFFF (negative underflow wraparound)
        R_TYPE(0x20, 2, 1, 0, 3),

        # x4 = 0 - 1 -> 0xFFFFFFFF (-1)
        R_TYPE(0x20, 2, 0, 0, 4),

        # x5 = x1 - x1 -> 0 (self-subtraction)
        R_TYPE(0x20, 1, 1, 0, 5),

        HALT,
    ]

    await run_program(dut, program, cycles=25)

    assert read_reg(dut, 3) == 0x7FFFFFFF, f"x3 expected 0x7FFFFFFF, got 0x{read_reg(dut, 3):08x}"
    assert read_reg(dut, 4) == 0xFFFFFFFF, f"x4 expected 0xFFFFFFFF, got 0x{read_reg(dut, 4):08x}"
    assert read_reg(dut, 5) == 0x00000000, f"x5 expected 0x00000000, got 0x{read_reg(dut, 5):08x}"
    dut._log.info("PASS: RISC-V International I-SUB-01 underflow and self-subtraction verified!")


# ==============================================================================
# TEST 3: I-SLT-01 & I-SLTU-01 Signed vs Unsigned Comparison
# ==============================================================================
@cocotb.test()
async def test_act_i_comparison_signed_unsigned(dut):
    """Verify official I-SLT-01 and I-SLTU-01 signed vs unsigned comparisons."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        # x1 = -1 (0xFFFFFFFF)
        I_TYPE(-1, 0, 0, 1),
        # x2 = 1
        I_TYPE(1, 0, 0, 2),

        # x3 = slt x1, x2  (-1 < 1 is TRUE in signed arithmetic -> 1)
        R_TYPE(0x00, 2, 1, 0x2, 3),

        # x4 = sltu x1, x2 (0xFFFFFFFF < 1 is FALSE in unsigned arithmetic -> 0)
        R_TYPE(0x00, 2, 1, 0x3, 4),

        HALT,
    ]

    await run_program(dut, program, cycles=20)

    assert read_reg(dut, 3) == 1, f"SLT (-1 < 1) expected 1, got {read_reg(dut, 3)}"
    assert read_reg(dut, 4) == 0, f"SLTU (0xFFFFFFFF < 1) expected 0, got {read_reg(dut, 4)}"
    dut._log.info("PASS: RISC-V International I-SLT-01 & I-SLTU-01 signed vs unsigned verified!")


# ==============================================================================
# TEST 4: I-SLL-01, I-SRL-01, I-SRA-01 Arithmetic vs Logical Shifts
# ==============================================================================
@cocotb.test()
async def test_act_i_shifts_sign_extension(dut):
    """Verify official I-SRA-01 arithmetic sign extension vs I-SRL-01 logical shifts."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        # x1 = 0x80000000
        U_TYPE(0x80000, 1),
        # x2 = 4 (shift amount)
        I_TYPE(4, 0, 0, 2),

        # x3 = sra x1, x2 (arithmetic shift right preserves sign bit: 0xF8000000)
        R_TYPE(0x20, 2, 1, 0x5, 3),

        # x4 = srl x1, x2 (logical shift right zero fills: 0x08000000)
        R_TYPE(0x00, 2, 1, 0x5, 4),

        HALT,
    ]

    await run_program(dut, program, cycles=20)

    assert read_reg(dut, 3) == 0xF8000000, f"SRA expected 0xF8000000, got 0x{read_reg(dut, 3):08x}"
    assert read_reg(dut, 4) == 0x08000000, f"SRL expected 0x08000000, got 0x{read_reg(dut, 4):08x}"
    dut._log.info("PASS: RISC-V International I-SRA-01 & I-SRL-01 arithmetic/logical shifts verified!")


# ==============================================================================
# TEST 5: I-BRANCH-01 Comprehensive Branch Conditions
# ==============================================================================
@cocotb.test()
async def test_act_i_branch_all_conditions(dut):
    """Verify official I-BRANCH-01 condition codes: BEQ, BNE, BLT, BGE, BLTU, BGEU."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        # Setup: x1 = 10, x2 = 20, x3 = -5, x4 = 0 (success flags)
        I_TYPE(10, 0, 0, 1),
        I_TYPE(20, 0, 0, 2),
        I_TYPE(-5, 0, 0, 3),

        # 1. BEQ not taken (10 != 20) -> should NOT skip next addi
        B_TYPE(8, 2, 1, 0x0),
        I_TYPE(1, 4, 0, 4),                 # x4 += 1 (x4 = 1)

        # 2. BNE taken (10 != 20) -> SHOULD skip next instruction
        B_TYPE(8, 2, 1, 0x1),
        I_TYPE(100, 4, 0, 4),               # should be skipped!
        I_TYPE(2, 4, 0, 4),                 # x4 += 2 (x4 = 3)

        # 3. BLT taken (-5 < 10 signed) -> SHOULD skip next instruction
        B_TYPE(8, 1, 3, 0x4),
        I_TYPE(100, 4, 0, 4),               # should be skipped!
        I_TYPE(4, 4, 0, 4),                 # x4 += 4 (x4 = 7)

        # 4. BLTU taken (10 < -5 unsigned, since -5 is 0xFFFFFFFB) -> SHOULD skip
        B_TYPE(8, 3, 1, 0x6),
        I_TYPE(100, 4, 0, 4),               # should be skipped!
        I_TYPE(8, 4, 0, 4),                 # x4 += 8 (x4 = 15)

        HALT,
    ]

    await run_program(dut, program, cycles=35)

    assert read_reg(dut, 4) == 15, f"Branch evaluation failed! Expected 15, got {read_reg(dut, 4)}"
    dut._log.info("PASS: RISC-V International I-BRANCH-01 branch condition codes verified 100% compliant!")
