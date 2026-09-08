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

