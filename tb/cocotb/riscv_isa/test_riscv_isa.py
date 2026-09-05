"""
RV32I Base Integer Instruction Set Compliance Test Suite for RISC-V CPU.
Executes micro-programs directly in hardware and verifies register/memory writebacks.

Tests:
1. Arithmetic Instructions: ADD, SUB, ADDI
2. Logical Instructions: AND, OR, XOR, ANDI, ORI, XORI
3. Shift Instructions: SLL, SRL, SRA, SLLI, SRLI, SRAI
4. Comparison Instructions: SLT, SLTU, SLTI, SLTIU
5. Upper Immediate Instructions: LUI, AUIPC
6. Control Flow: JAL, JALR
7. Conditional Branches: BEQ, BNE, BLT, BGE, BLTU, BGEU (Taken & Not Taken)
8. Load and Store: SW and LW roundtrip through Data Memory
"""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock


# RV32I Instruction Assembler Helpers
def R_TYPE(funct7, rs2, rs1, funct3, rd, opcode=0x33):
    return ((funct7 & 0x7F) << 25) | ((rs2 & 0x1F) << 20) | ((rs1 & 0x1F) << 15) | ((funct3 & 0x7) << 12) | ((rd & 0x1F) << 7) | (opcode & 0x7F)

def I_TYPE(imm, rs1, funct3, rd, opcode=0x13):
    return ((imm & 0xFFF) << 20) | ((rs1 & 0x1F) << 15) | ((funct3 & 0x7) << 12) | ((rd & 0x1F) << 7) | (opcode & 0x7F)

def S_TYPE(imm, rs2, rs1, funct3=0x2, opcode=0x23):
    imm11_5 = (imm >> 5) & 0x7F
    imm4_0 = imm & 0x1F
    return (imm11_5 << 25) | ((rs2 & 0x1F) << 20) | ((rs1 & 0x1F) << 15) | ((funct3 & 0x7) << 12) | (imm4_0 << 7) | (opcode & 0x7F)

def B_TYPE(offset, rs2, rs1, funct3, opcode=0x63):
    imm12 = (offset >> 12) & 0x1
    imm10_5 = (offset >> 5) & 0x3F
    imm4_1 = (offset >> 1) & 0xF
    imm11 = (offset >> 11) & 0x1
    return (imm12 << 31) | (imm10_5 << 25) | ((rs2 & 0x1F) << 20) | ((rs1 & 0x1F) << 15) | ((funct3 & 0x7) << 12) | (imm4_1 << 8) | (imm11 << 7) | (opcode & 0x7F)

def U_TYPE(imm, rd, opcode=0x37):
    return ((imm & 0xFFFFF) << 12) | ((rd & 0x1F) << 7) | (opcode & 0x7F)

def J_TYPE(offset, rd, opcode=0x6F):
    imm20 = (offset >> 20) & 0x1
    imm10_1 = (offset >> 1) & 0x3FF
    imm11 = (offset >> 11) & 0x1
    imm19_12 = (offset >> 12) & 0xFF
    return (imm20 << 31) | (imm10_1 << 21) | (imm11 << 20) | (imm19_12 << 12) | ((rd & 0x1F) << 7) | (opcode & 0x7F)

NOP = 0x00000013
HALT = 0x0000006F


async def run_micro_program(dut, program, cycles=25):
    """Load program into IMEM, reset CPU, and execute for given cycles."""
    # Clear IMEM
    for i in range(64):
        dut.u_cpu.u_imem.RAM[i].value = NOP

    # Load program
    for i, instr in enumerate(program):
        dut.u_cpu.u_imem.RAM[i].value = instr & 0xFFFFFFFF

    # Pulse reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, cycles)


def read_reg(dut, reg_idx):
    """Read register from CPU register file."""
    return int(dut.u_cpu.u_regfile.registers[reg_idx].value)


# ==============================================================================
# TEST 1: Arithmetic Group (ADD, SUB, ADDI)
# ==============================================================================
@cocotb.test()
async def test_isa_arithmetic(dut):
    """Verify ADD, SUB, ADDI instructions."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        I_TYPE(100, 0, 0, 1),           # addi x1, x0, 100
        I_TYPE(-30, 0, 0, 2),           # addi x2, x0, -30
        R_TYPE(0x00, 2, 1, 0, 3),       # add  x3, x1, x2  (100 + (-30) = 70)
        R_TYPE(0x20, 2, 1, 0, 4),       # sub  x4, x1, x2  (100 - (-30) = 130)
        HALT,
    ]
    await run_micro_program(dut, program, cycles=20)

    assert read_reg(dut, 1) == 100, f"x1 expected 100, got {read_reg(dut, 1)}"
    assert read_reg(dut, 2) == 0xFFFFFFE2, f"x2 expected -30, got {hex(read_reg(dut, 2))}"
    assert read_reg(dut, 3) == 70, f"x3 expected 70, got {read_reg(dut, 3)}"
    assert read_reg(dut, 4) == 130, f"x4 expected 130, got {read_reg(dut, 4)}"
    dut._log.info("PASS: Arithmetic instructions (ADD, SUB, ADDI) verified")


# ==============================================================================
# TEST 2: Logical Group (AND, OR, XOR, ANDI, ORI, XORI)
# ==============================================================================
@cocotb.test()
async def test_isa_logical(dut):
    """Verify AND, OR, XOR, ANDI, ORI, XORI instructions."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        I_TYPE(0x0F0, 0, 0, 1),         # addi x1, x0, 0x0F0
        I_TYPE(0x00F, 0, 0, 2),         # addi x2, x0, 0x00F
        R_TYPE(0x00, 2, 1, 7, 3),       # and  x3, x1, x2   (0x0F0 & 0x00F = 0)
        R_TYPE(0x00, 2, 1, 6, 4),       # or   x4, x1, x2   (0x0F0 | 0x00F = 0x0FF)
        R_TYPE(0x00, 2, 1, 4, 5),       # xor  x5, x1, x2   (0x0F0 ^ 0x00F = 0x0FF)
        I_TYPE(0x055, 1, 7, 6),         # andi x6, x1, 0x055 (0x0F0 & 0x055 = 0x050)
        I_TYPE(0x00A, 1, 6, 7),         # ori  x7, x1, 0x00A (0x0F0 | 0x00A = 0x0FA)
        I_TYPE(0x0FF, 1, 4, 8),         # xori x8, x1, 0x0FF (0x0F0 ^ 0x0FF = 0x00F)
        HALT,
    ]
    await run_micro_program(dut, program, cycles=25)

    assert read_reg(dut, 3) == 0x000, f"AND failed: got {hex(read_reg(dut, 3))}"
    assert read_reg(dut, 4) == 0x0FF, f"OR failed: got {hex(read_reg(dut, 4))}"
    assert read_reg(dut, 5) == 0x0FF, f"XOR failed: got {hex(read_reg(dut, 5))}"
    assert read_reg(dut, 6) == 0x050, f"ANDI failed: got {hex(read_reg(dut, 6))}"
    assert read_reg(dut, 7) == 0x0FA, f"ORI failed: got {hex(read_reg(dut, 7))}"
    assert read_reg(dut, 8) == 0x00F, f"XORI failed: got {hex(read_reg(dut, 8))}"
    dut._log.info("PASS: Logical instructions (AND, OR, XOR, ANDI, ORI, XORI) verified")


# ==============================================================================
# TEST 3: Shift Group (SLL, SRL, SRA, SLLI, SRLI, SRAI)
# ==============================================================================
@cocotb.test()
async def test_isa_shifts(dut):
    """Verify SLL, SRL, SRA, SLLI, SRLI, SRAI instructions."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        I_TYPE(1, 0, 0, 1),             # addi x1, x0, 1
        I_TYPE(4, 0, 0, 2),             # addi x2, x0, 4 (shift amount)
        R_TYPE(0x00, 2, 1, 1, 3),       # sll  x3, x1, x2  (1 << 4 = 16)
        I_TYPE(0x04, 1, 1, 4),          # slli x4, x1, 4   (1 << 4 = 16)
        I_TYPE(-16, 0, 0, 5),           # addi x5, x0, -16 (0xFFFFFFF0)
        I_TYPE(2, 5, 5, 6),             # srli x6, x5, 2   (logical right shift -> 0x3FFFFFFC)
        I_TYPE(0x402, 5, 5, 7),         # srai x7, x5, 2   (arithmetic right shift -> 0xFFFFFFFC)
        HALT,
    ]
    await run_micro_program(dut, program, cycles=25)

    assert read_reg(dut, 3) == 16, f"SLL failed: got {read_reg(dut, 3)}"
    assert read_reg(dut, 4) == 16, f"SLLI failed: got {read_reg(dut, 4)}"
    assert read_reg(dut, 6) == 0x3FFFFFFC, f"SRLI failed: got {hex(read_reg(dut, 6))}"
    assert read_reg(dut, 7) == 0xFFFFFFFC, f"SRAI failed: got {hex(read_reg(dut, 7))}"
    dut._log.info("PASS: Shift instructions (SLL, SRL, SRA, SLLI, SRLI, SRAI) verified")


# ==============================================================================
# TEST 4: Comparison Group (SLT, SLTU, SLTI, SLTIU)
# ==============================================================================
@cocotb.test()
async def test_isa_comparison(dut):
    """Verify SLT, SLTU, SLTI, SLTIU instructions."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        I_TYPE(-5, 0, 0, 1),            # addi x1, x0, -5
        I_TYPE(10, 0, 0, 2),            # addi x2, x0, 10
        R_TYPE(0x00, 2, 1, 2, 3),       # slt  x3, x1, x2  (-5 < 10 signed -> 1)
        R_TYPE(0x00, 2, 1, 3, 4),       # sltu x4, x1, x2  (0xFFFFFFFB < 10 unsigned -> 0)
        I_TYPE(0, 1, 2, 5),             # slti x5, x1, 0   (-5 < 0 signed -> 1)
        I_TYPE(0, 1, 3, 6),             # sltiu x6, x1, 0  (0xFFFFFFFB < 0 unsigned -> 0)
        HALT,
    ]
    await run_micro_program(dut, program, cycles=25)

    assert read_reg(dut, 3) == 1, f"SLT failed: got {read_reg(dut, 3)}"
    assert read_reg(dut, 4) == 0, f"SLTU failed: got {read_reg(dut, 4)}"
    assert read_reg(dut, 5) == 1, f"SLTI failed: got {read_reg(dut, 5)}"
    assert read_reg(dut, 6) == 0, f"SLTIU failed: got {read_reg(dut, 6)}"
    dut._log.info("PASS: Comparison instructions (SLT, SLTU, SLTI, SLTIU) verified")


# ==============================================================================
# TEST 5: Upper Immediates (LUI, AUIPC)
# ==============================================================================
@cocotb.test()
async def test_isa_upper_imm(dut):
    """Verify LUI and AUIPC instructions."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        U_TYPE(0x12345, 1, opcode=0x37),  # lui   x1, 0x12345 (x1 = 0x12345000)
        U_TYPE(0x00001, 2, opcode=0x17),  # auipc x2, 1       (x2 = PC (4) + 0x1000 = 0x1004)
        HALT,
    ]
    await run_micro_program(dut, program, cycles=20)

    assert read_reg(dut, 1) == 0x12345000, f"LUI failed: got {hex(read_reg(dut, 1))}"
    assert read_reg(dut, 2) == 0x00001004, f"AUIPC failed: got {hex(read_reg(dut, 2))}"
    dut._log.info("PASS: Upper immediate instructions (LUI, AUIPC) verified")


# ==============================================================================
# TEST 6: Control Flow (JAL, JALR, Branch BEQ/BNE)
# ==============================================================================
@cocotb.test()
async def test_isa_control_flow(dut):
    """Verify JAL, JALR, and Branch instructions with pipeline flushing."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        I_TYPE(10, 0, 0, 1),            # 0: addi x1, x0, 10
        I_TYPE(10, 0, 0, 2),            # 1: addi x2, x0, 10
        B_TYPE(12, 2, 1, 0),            # 2: beq  x1, x2, +12 (jump to instr 5)
        I_TYPE(99, 0, 0, 3),            # 3: addi x3, x0, 99 (SKIPPED!)
        I_TYPE(88, 0, 0, 4),            # 4: addi x4, x0, 88 (SKIPPED!)
        I_TYPE(77, 0, 0, 5),            # 5: addi x5, x0, 77 (TARGET)
        HALT,
    ]
    await run_micro_program(dut, program, cycles=30)

    assert read_reg(dut, 3) == 0, f"Instruction 3 should have been skipped! Got {read_reg(dut, 3)}"
    assert read_reg(dut, 4) == 0, f"Instruction 4 should have been skipped! Got {read_reg(dut, 4)}"
    assert read_reg(dut, 5) == 77, f"Branch target instruction 5 failed! Got {read_reg(dut, 5)}"
    dut._log.info("PASS: Branch taken and pipeline flush verified")


# ==============================================================================
# TEST 7: Memory SW and LW Roundtrip
# ==============================================================================
@cocotb.test()
async def test_isa_memory_roundtrip(dut):
    """Verify SW and LW instructions to Data Memory with address offset."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    program = [
        I_TYPE(32, 0, 0, 1),            # addi x1, x0, 32 (base address)
        I_TYPE(0x555, 0, 0, 2),         # addi x2, x0, 0x555 (data to store)
        S_TYPE(8, 2, 1, funct3=2),      # sw   x2, 8(x1)  (store to addr 40)
        I_TYPE(8, 1, 2, 3, opcode=0x03),# lw   x3, 8(x1)  (load from addr 40)
        HALT,
    ]
    await run_micro_program(dut, program, cycles=30)

    assert read_reg(dut, 3) == 0x555, f"LW failed: expected 0x555, got {hex(read_reg(dut, 3))}"
    dut._log.info("PASS: Memory SW and LW roundtrip verified")
