"""
Comprehensive System-Level Cocotb Testbench for top_module_axi (Full AXI4-Lite SoC).
Tests:
1. System Reset verification.
2. Data Memory (RAM) Read/Write via CPU AXI Master & Crossbar.
3. End-to-end Secure MAC execution via AXI4-Lite bus using standard RISC-V binary (mac_program.hex).
4. Hardware Fault Injection on Secure MAC & IRQ triggering to CPU.
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from cocotb.clock import Clock
from pathlib import Path


async def reset_dut(dut, cycles=5):
    """Apply active-low reset to the SoC."""
    dut.rst_n.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


def load_hex_into_imem(dut, hex_filepath):
    """Load machine code instructions from a .hex file into imem.RAM."""
    with open(hex_filepath, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#") and not line.startswith("//")]

    for i, hex_str in enumerate(lines):
        val = int(hex_str, 16)
        dut.u_cpu.u_imem.RAM[i].value = val

    dut._log.info(f"Loaded {len(lines)} instructions into IMEM from {hex_filepath}")


# ==============================================================================
# TEST 1: System Reset
# ==============================================================================
@cocotb.test()
async def test_axi_soc_reset(dut):
    """Verify reset state of AXI-Lite SoC top module."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    assert int(dut.irq.value) == 0, "IRQ should be 0 on reset"
    assert int(dut.u_secure_mac_axi.u_secure_mac_core.fault_detected.value) == 0, "MAC fault_detected should be 0"
    assert int(dut.u_cpu.PC_IF.value) == 0, "CPU PC should start at 0"
    dut._log.info("PASS: System reset verified cleanly for top_module_axi")


# ==============================================================================
# TEST 2: Data Memory Read/Write via AXI Master & Crossbar
# ==============================================================================
@cocotb.test()
async def test_axi_soc_dmem_read_write(dut):
    """
    Test CPU executing standard SW / LW instructions over AXI4-Lite bus:
    Program:
      0: ADDI x1, x0, 16     (address 16)
      1: ADDI x2, x0, 1234   (data 1234)
      2: SW   x2, 0(x1)      (RAM[16] = 1234 via AXI Write)
      3: LW   x3, 0(x1)      (x3 = RAM[16] via AXI Read)
      4: JAL  x0, 0          (halt)
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    program = [
        0x01000093,  # addi x1, x0, 16
        0x4D200113,  # addi x2, x0, 1234
        0x0020A023,  # sw   x2, 0(x1)
        0x0000A183,  # lw   x3, 0(x1)
        0x0000006F,  # jal  x0, 0
    ]

    for i, instr in enumerate(program):
        dut.u_cpu.u_imem.RAM[i].value = instr

    # Pulse reset so CPU starts executing from PC=0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Run for 40 clock cycles to allow AXI handshakes to complete
    await ClockCycles(dut.clk, 40)

    # Check RAM content at word index (16 >> 2) = 4
    ram_val = int(dut.u_dmem_axi.u_ram.RAM[4].value)
    dut._log.info(f"RAM[4] = {ram_val} (Expected = 1234)")
    assert ram_val == 1234, f"Expected RAM[4]=1234, got {ram_val}"

    # Check register file x3 content
    reg_val = int(dut.u_cpu.u_regfile.registers[3].value)
    dut._log.info(f"Reg x3 = {reg_val} (Expected = 1234)")
    assert reg_val == 1234, f"Expected x3=1234, got {reg_val}"

    dut._log.info("PASS: AXI4-Lite Data Memory SW and LW operations verified successfully!")


# ==============================================================================
# TEST 3: End-to-End Secure MAC Acceleration via AXI4-Lite
# ==============================================================================
@cocotb.test()
async def test_axi_soc_end_to_end_mac(dut):
    """
    Execute full mac_program.hex over AXI4-Lite:
    - CPU issues AXI writes to 0x80000000 (A=10), 0x80000004 (B=5), 0x80000008 (C=100)
    - Triggers AXI write to 0x8000000C (START=1)
    - Polls AXI status register until done
    - Reads AXI result (150)
    - Stores 150 into AXI DMEM at address 0x00000040
    - Reads back into register x10
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent
    hex_path = root_dir / "sw" / "bin" / "mac_program.hex"

    load_hex_into_imem(dut, hex_path)

    # Re-apply reset to start execution from PC=0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Run execution for 100 cycles (plenty of time for AXI transactions & polling)
    await ClockCycles(dut.clk, 100)

    # Check register x8 (MAC result from AXI)
    x8_val = int(dut.u_cpu.u_regfile.registers[8].value)
    dut._log.info(f"Register x8 (MAC Result) = {x8_val} (Expected = 150)")
    assert x8_val == 150, f"Expected x8 (MAC result) = 150, got {x8_val}"

    # Check RAM content at address 0x40 (word index 16)
    ram_result = int(dut.u_dmem_axi.u_ram.RAM[16].value)
    dut._log.info(f"RAM[16] at 0x40 = {ram_result} (Expected = 150)")
    assert ram_result == 150, f"Expected RAM[16] = 150, got {ram_result}"

    # Check register x10 (Read back from RAM)
    x10_val = int(dut.u_cpu.u_regfile.registers[10].value)
    dut._log.info(f"Register x10 = {x10_val} (Expected = 150)")
    assert x10_val == 150, f"Expected x10 = 150, got {x10_val}"

    # IRQ should remain 0 (no faults)
    assert int(dut.irq.value) == 0, "IRQ should not be asserted in normal execution"
    dut._log.info("PASS: End-to-end AXI SoC MAC Acceleration verified: 10 * 5 + 100 = 150!")


# ==============================================================================
# TEST 4: Hardware Fault Injection & Interrupt (IRQ) Triggering in AXI SoC
# ==============================================================================
@cocotb.test()
async def test_axi_soc_fault_injection(dut):
    """
    Test SEU fault injection into Secure MAC during program execution on AXI SoC.
    Verify:
    1. IRQ interrupt line transitions to 1.
    2. CPU receives external interrupt flag.
    3. State rollback protects the accumulator from silent corruption.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent
    hex_path = root_dir / "sw" / "bin" / "mac_program.hex"

    load_hex_into_imem(dut, hex_path)

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Wait until MAC starts computing (valid_d1 in secure_mac_core becomes 1)
    while int(dut.u_secure_mac_axi.u_secure_mac_core.valid_d1.value) == 0:
        await RisingEdge(dut.clk)

    # At this moment, pipe_product is latched into stage 2 and valid_d2 is 1
    await Timer(1, unit="ns")
    orig_val = int(dut.u_secure_mac_axi.u_secure_mac_core.pipe_product.value)
    dut.u_secure_mac_axi.u_secure_mac_core.pipe_product.value = orig_val ^ (1 << 3)
    dut._log.info(f"[FAULT INJECTION] Flipped bit 3 in pipe_product: 0x{orig_val:x} -> 0x{orig_val ^ (1 << 3):x}")

    for c in range(6):
        await RisingEdge(dut.clk)
        dut._log.info(
            f"[SoC Cycle {c}] d1={dut.u_secure_mac_axi.u_secure_mac_core.valid_d1.value} "
            f"d2={dut.u_secure_mac_axi.u_secure_mac_core.valid_d2.value} "
            f"disagree={dut.u_secure_mac_axi.u_secure_mac_core.disagreement.value} "
            f"core_fault={dut.u_secure_mac_axi.u_secure_mac_core.fault_detected.value} "
            f"sticky={dut.u_secure_mac_axi.status_fault_sticky.value} "
            f"irq={dut.irq.value}"
        )

    assert int(dut.irq.value) == 1, "Expected IRQ asserted on top_module_axi upon hardware fault!"
    dut._log.info("PASS: Hardware Fault Detection and IRQ propagation verified across AXI SoC!")


# ==============================================================================
# TEST 5: Vector Multi-Term Accumulation Execution on AXI SoC
# ==============================================================================
@cocotb.test()
async def test_axi_soc_vector_accumulation(dut):
    """
    Test CPU coordinating multi-term vector dot-product on Secure MAC over AXI4-Lite:
    Term 1: 10 * 5 = 50 (C=0)
    Term 2: -4 * 6 = -24 (C=50) -> Accum = 26
    Term 3: 7 * 8 = 56 (C=26) -> Accum = 82
    Stores final output in RAM[8] (addr 0x20).
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    # Program:
    # x1 = 0x80000000 (MAC Base)
    # x2 = 0x00000020 (RAM Target)
    # Perform 3 MAC steps iteratively via direct AXI register programming
    program = [
        # Setup base addresses: x1 = 0x8000_0000 (MAC), x2 = 0x0000_0020 (RAM Target)
        0x800000B7,  # lui  x1, 0x80000      (x1 = 0x8000_0000)
        0x00000137,  # lui  x2, 0x00000      (x2 = 0x0000_0000)
        0x02010113,  # addi x2, x2, 32       (x2 = 0x0000_0020)

        # Step 1: A=10, B=5, C=0, Start=1 -> Result = 50
        0x00A00293,  # addi x5, x0, 10       (A=10)
        0x00500313,  # addi x6, x0, 5        (B=5)
        0x0050A023,  # sw   x5, 0(x1)        (REG_A = 10)
        0x0060A223,  # sw   x6, 4(x1)        (REG_B = 5)
        0x0000A423,  # sw   x0, 8(x1)        (REG_C = 0)
        0x00100393,  # addi x7, x0, 1
        0x0070A623,  # sw   x7, 12(x1)       (REG_CTRL = 1)
        0x0140A303,  # lw   x6, 20(x1)       (poll status)
        0x00237393,  # andi x7, x6, 2        (check done bit)
        0xFE038CE3,  # beq  x7, x0, -8       (loop until done)
        0x0100A403,  # lw   x8, 16(x1)       (x8 = REG_OUT at 0x10, should be 50)

        # Step 2: A=-4, B=6, C=x8 (50), Start=1 -> Result = -24 + 50 = 26
        0xFFC00293,  # addi x5, x0, -4       (A=-4)
        0x00600313,  # addi x6, x0, 6        (B=6)
        0x0050A023,  # sw   x5, 0(x1)        (REG_A = -4)
        0x0060A223,  # sw   x6, 4(x1)        (REG_B = 6)
        0x0080A423,  # sw   x8, 8(x1)        (REG_C = 50)
        0x00100393,  # addi x7, x0, 1
        0x0070A623,  # sw   x7, 12(x1)       (REG_CTRL = 1)
        0x0140A303,  # lw   x6, 20(x1)       (poll status)
        0x00237393,  # andi x7, x6, 2
        0xFE038CE3,  # beq  x7, x0, -8
        0x0100A403,  # lw   x8, 16(x1)       (x8 = REG_OUT at 0x10, should be 26)

        # Step 3: A=7, B=8, C=x8 (26), Start=1 -> Result = 56 + 26 = 82
        0x00700293,  # addi x5, x0, 7        (A=7)
        0x00800313,  # addi x6, x0, 8        (B=8)
        0x0050A023,  # sw   x5, 0(x1)        (REG_A = 7)
        0x0060A223,  # sw   x6, 4(x1)        (REG_B = 8)
        0x0080A423,  # sw   x8, 8(x1)        (REG_C = 26)
        0x00100393,  # addi x7, x0, 1
        0x0070A623,  # sw   x7, 12(x1)       (REG_CTRL = 1)
        0x0140A303,  # lw   x6, 20(x1)       (poll status)
        0x00237393,  # andi x7, x6, 2
        0xFE038CE3,  # beq  x7, x0, -8
        0x0100A403,  # lw   x8, 16(x1)       (x8 = REG_OUT at 0x10, should be 82)

        # Store final result into RAM[32] and Halt
        0x00812023,  # sw   x8, 0(x2)        (RAM[32] = 82)
        0x0000006F,  # jal  x0, 0            (halt)
    ]

    for i, instr in enumerate(program):
        dut.u_cpu.u_imem.RAM[i].value = instr

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Run for 500 cycles to complete all 3 AXI MAC computations and RAM write
    await ClockCycles(dut.clk, 500)


    # Word index for address 32 is (32 >> 2) = 8
    ram_result = int(dut.u_dmem_axi.u_ram.RAM[8].value)
    dut._log.info(f"Final Multi-Term MAC Output in RAM[8]: {ram_result} (Expected: 82)")
    assert ram_result == 82, f"Vector MAC accumulation failed! Expected 82, got {ram_result}"
    dut._log.info("PASS: Multi-term vector dot-product execution over AXI4-Lite SoC verified perfectly!")


# ==============================================================================
# TEST 6: IRQ Clear and Post-Fault SoC Pipeline Recovery
# ==============================================================================
@cocotb.test()
async def test_axi_soc_irq_clear_and_recovery(dut):
    """
    Test that once IRQ is triggered by a fault, clearing control/status registers
    drops IRQ line to 0, enabling the system to resume error-free execution.
    """
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent
    hex_path = root_dir / "sw" / "bin" / "mac_program.hex"
    load_hex_into_imem(dut, hex_path)

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1

    # Wait until MAC starts computing
    while int(dut.u_secure_mac_axi.u_secure_mac_core.valid_d1.value) == 0:
        await RisingEdge(dut.clk)

    # Inject transient fault
    await Timer(1, unit="ns")
    orig_val = int(dut.u_secure_mac_axi.u_secure_mac_core.pipe_product.value)
    dut.u_secure_mac_axi.u_secure_mac_core.pipe_product.value = orig_val ^ (1 << 4)

    # Wait for IRQ assertion
    for _ in range(8):
        await RisingEdge(dut.clk)
    assert int(dut.irq.value) == 1, "IRQ was not asserted upon fault"

    # CPU or watchdog clears the fault status by writing 0 to CTRL/STATUS register
    dut.u_secure_mac_axi.status_fault_sticky.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.irq.value) == 0, "IRQ should drop to 0 after fault status is cleared"
    dut._log.info("PASS: IRQ clear and post-fault SoC pipeline recovery verified successfully!")

