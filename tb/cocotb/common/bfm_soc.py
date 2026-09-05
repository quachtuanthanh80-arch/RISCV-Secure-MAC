"""
Bus Functional Model (BFM), Driver, and Scoreboard Framework for Cocotb Testbenches.
Provides:
1. SoCDriver: High-level transactions for CPU IMEM loading, DMEM access, and MMIO register polling.
2. MacGoldenModel: Pure Python reference model for Modulo-3 Residue Check & State Rollback.
3. TransactionScoreboard: Asynchronous queue-based transaction comparison.
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from collections import deque


def to_signed(val: int, bits: int = 32) -> int:
    """Convert integer to signed 2's complement representation."""
    mask = (1 << bits) - 1
    val = val & mask
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val


def to_unsigned(val: int, bits: int = 32) -> int:
    """Convert signed integer to unsigned bit vector."""
    mask = (1 << bits) - 1
    return val & mask


class SoCDriver:
    """Transaction-level driver for interacting with SoC top module."""

    def __init__(self, dut):
        self.dut = dut
        self.log = dut._log

    async def reset(self, cycles: int = 5):
        """Assert active-low reset synchronously."""
        self.dut.rst_n.value = 0
        for _ in range(cycles):
            await RisingEdge(self.dut.clk)
        self.dut.rst_n.value = 1
        await RisingEdge(self.dut.clk)
        self.log.info("[BFM] SoC Reset asserted and released cleanly")

    def load_imem_words(self, words: list[int]):
        """Direct backdoor initialization of Instruction Memory."""
        for i, word in enumerate(words):
            self.dut.u_cpu.u_imem.RAM[i].value = word & 0xFFFFFFFF
        self.log.info(f"[BFM] Backdoor loaded {len(words)} instructions into IMEM")

    def read_dmem_word(self, word_addr: int) -> int:
        """Backdoor read from Data Memory RAM."""
        return int(self.dut.u_dmem.RAM[word_addr].value)

    def write_dmem_word(self, word_addr: int, value: int):
        """Backdoor write to Data Memory RAM."""
        self.dut.u_dmem.RAM[word_addr].value = value & 0xFFFFFFFF

    def read_reg(self, reg_idx: int) -> int:
        """Read CPU register value."""
        return int(self.dut.u_cpu.u_regfile.registers[reg_idx].value)


class MacGoldenModel:
    """Independent Python Reference Model for Secure MAC with Modulo-3 Residue Check."""

    def __init__(self):
        self.shadow_acc = 0
        self.history = []

    def compute(self, a: int, b: int, c: int, fault_injected: bool = False) -> tuple[int, bool, bool]:
        """
        Compute expected result.
        Returns: (expected_out, expected_fault_detected, expected_rollback)
        """
        golden_product = a * b
        golden_accum = golden_product + c

        # Modulo 3 residue check
        r_a = (a % 3 + 3) % 3
        r_b = (b % 3 + 3) % 3
        r_c = (c % 3 + 3) % 3

        r_ab = (r_a * r_b) % 3
        expected_mod3 = (r_ab + r_c) % 3
        actual_mod3 = (golden_accum % 3 + 3) % 3

        if fault_injected:
            # Fault detected -> Rollback to shadow
            return self.shadow_acc, True, True
        else:
            self.shadow_acc = golden_accum
            return golden_accum, False, False


class TransactionScoreboard:
    """Scoreboard to verify DUT transactions asynchronously."""

    def __init__(self, log):
        self.log = log
        self.expected_queue = deque()
        self.match_count = 0
        self.mismatch_count = 0

    def add_expected(self, expected_item):
        self.expected_queue.append(expected_item)

    def check_actual(self, actual_item, test_name: str = ""):
        if not self.expected_queue:
            self.log.error(f"[Scoreboard] Unexpected item received: {actual_item}")
            self.mismatch_count += 1
            return False

        expected_item = self.expected_queue.popleft()
        if actual_item == expected_item:
            self.match_count += 1
            return True
        else:
            self.log.error(f"[Scoreboard MISMATCH] {test_name}: Expected {expected_item}, Got {actual_item}")
            self.mismatch_count += 1
            return False

    def report(self) -> bool:
        self.log.info(f"[Scoreboard Summary] Matches: {self.match_count}, Mismatches: {self.mismatch_count}")
        return self.mismatch_count == 0 and len(self.expected_queue) == 0
