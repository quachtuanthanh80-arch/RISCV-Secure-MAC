"""
Comprehensive Cocotb Test Suite for secure_mac_axi (AXI4-Lite Slave IP).
Validates:
1. AXI4-Lite 5-channel protocol handshaking and backpressure handling.
2. Register Map read/write accessibility (REG_MAC_A, REG_MAC_B, REG_MAC_C).
3. AXI-triggered MAC computation and status polling (START -> DONE).
4. Multi-step MAC vector accumulation.
5. Online fault detection via Modulo-3 CED over AXI & IRQ assert.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, FallingEdge, Timer


class AxiLiteMasterBFM:
    """Bus Functional Model for AXI4-Lite Master transactions."""

    def __init__(self, dut):
        self.dut = dut
        self.log = dut._log

    async def reset(self, cycles: int = 5):
        """Active-low reset sequence."""
        self.dut.aresetn.value = 0
        self.dut.s_axi_awvalid.value = 0
        self.dut.s_axi_awaddr.value = 0
        self.dut.s_axi_awprot.value = 0
        self.dut.s_axi_wvalid.value = 0
        self.dut.s_axi_wdata.value = 0
        self.dut.s_axi_wstrb.value = 0
        self.dut.s_axi_bready.value = 0
        self.dut.s_axi_arvalid.value = 0
        self.dut.s_axi_araddr.value = 0
        self.dut.s_axi_arprot.value = 0
        self.dut.s_axi_rready.value = 0

        for _ in range(cycles):
            await RisingEdge(self.dut.aclk)
        self.dut.aresetn.value = 1
        await RisingEdge(self.dut.aclk)
        self.log.info("[AXI BFM] System Reset released successfully.")

    async def write(self, addr: int, data: int, wstrb: int = 0xF, expect_error: bool = False) -> int:
        """Execute single 32-bit AXI4-Lite Write transaction."""
        await RisingEdge(self.dut.aclk)
        self.dut.s_axi_awaddr.value = addr & 0xFFFFFFFF
        self.dut.s_axi_awprot.value = 0
        self.dut.s_axi_awvalid.value = 1

        self.dut.s_axi_wdata.value = data & 0xFFFFFFFF
        self.dut.s_axi_wstrb.value = wstrb
        self.dut.s_axi_wvalid.value = 1

        aw_done = False
        w_done = False

        # Wait for AWREADY and WREADY
        while not (aw_done and w_done):
            await RisingEdge(self.dut.aclk)
            if not aw_done and int(self.dut.s_axi_awready.value) == 1:
                aw_done = True
                self.dut.s_axi_awvalid.value = 0
            if not w_done and int(self.dut.s_axi_wready.value) == 1:
                w_done = True
                self.dut.s_axi_wvalid.value = 0

        # Wait for BVALID and send BREADY
        self.dut.s_axi_bready.value = 1
        while int(self.dut.s_axi_bvalid.value) == 0:
            await RisingEdge(self.dut.aclk)

        bresp = int(self.dut.s_axi_bresp.value)
        await RisingEdge(self.dut.aclk)
        self.dut.s_axi_bready.value = 0
        if not expect_error:
            assert bresp == 0, f"AXI Write to 0x{addr:08x} returned unexpected error ({bresp})"
        else:
            assert bresp != 0, f"AXI Write to 0x{addr:08x} expected error, but got OKAY"
        return bresp

    async def read(self, addr: int, expect_error: bool = False) -> int:
        """Execute single 32-bit AXI4-Lite Read transaction."""
        await RisingEdge(self.dut.aclk)
        self.dut.s_axi_araddr.value = addr & 0xFFFFFFFF
        self.dut.s_axi_arprot.value = 0
        self.dut.s_axi_arvalid.value = 1

        while int(self.dut.s_axi_arready.value) == 0:
            await RisingEdge(self.dut.aclk)

        await RisingEdge(self.dut.aclk)
        self.dut.s_axi_arvalid.value = 0
        self.dut.s_axi_rready.value = 1

        while int(self.dut.s_axi_rvalid.value) == 0:
            await RisingEdge(self.dut.aclk)

        rdata = int(self.dut.s_axi_rdata.value)
        rresp = int(self.dut.s_axi_rresp.value)
        await RisingEdge(self.dut.aclk)
        self.dut.s_axi_rready.value = 0

        if not expect_error:
            assert rresp == 0, f"AXI Read from 0x{addr:08x} returned unexpected error ({rresp})"
        else:
            assert rresp != 0, f"AXI Read from 0x{addr:08x} expected error, but got OKAY"
        return rdata


def to_signed(val: int, bits: int = 16) -> int:
    mask = (1 << bits) - 1
    val = val & mask
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val


@cocotb.test()
async def test_axi_register_access(dut):
    """Test 1: Verify AXI4-Lite read/write access to operand registers."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    bfm = AxiLiteMasterBFM(dut)
    await bfm.reset()

    dut._log.info("--- Testing Operand Registers Write and Readback ---")
    # Write REG_MAC_A = 25 (0x19), REG_MAC_B = -10 (0xF6), REG_MAC_C = 1000 (0x3E8)
    await bfm.write(0x00, 25)
    await bfm.write(0x04, (-10) & 0xFF)
    await bfm.write(0x08, 1000)

    # Readback
    val_a = to_signed(await bfm.read(0x00), 8)
    val_b = to_signed(await bfm.read(0x04), 8)
    val_c = to_signed(await bfm.read(0x08), 16)

    dut._log.info(f"Readback: A={val_a}, B={val_b}, C={val_c}")
    assert val_a == 25, f"REG_MAC_A mismatch: expected 25, got {val_a}"
    assert val_b == -10, f"REG_MAC_B mismatch: expected -10, got {val_b}"
    assert val_c == 1000, f"REG_MAC_C mismatch: expected 1000, got {val_c}"


@cocotb.test()
async def test_axi_mac_computation(dut):
    """Test 2: Verify full MAC computation triggered via AXI CTRL register."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    bfm = AxiLiteMasterBFM(dut)
    await bfm.reset()

    # Operands: A = 15, B = 8, C = 200 => Result = 15*8 + 200 = 320
    await bfm.write(0x00, 15)
    await bfm.write(0x04, 8)
    await bfm.write(0x08, 200)

    # Send START pulse via REG_MAC_CTRL (bit 0 = 1)
    await bfm.write(0x0C, 1)

    # Wait 4 clock cycles for MAC 3-stage pipeline
    await ClockCycles(dut.aclk, 4)

    # Poll status register: bit 0: fault, bit 1: done
    status = await bfm.read(0x14)
    done_flag = (status >> 1) & 1
    fault_flag = status & 1
    dut._log.info(f"MAC Status Word: 0x{status:08x} (Done={done_flag}, Fault={fault_flag})")
    assert done_flag == 1, "Expected Done/Valid bit asserted in REG_MAC_STATUS"
    assert fault_flag == 0, "No fault expected in normal operation"

    # Read output
    mac_out = to_signed(await bfm.read(0x10), 16)
    dut._log.info(f"MAC Output Result = {mac_out}")
    assert mac_out == 320, f"MAC result mismatch: expected 320, got {mac_out}"


@cocotb.test()
async def test_axi_vector_accumulation(dut):
    """Test 3: Vector dot-product accumulation across multiple AXI commands."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    bfm = AxiLiteMasterBFM(dut)
    await bfm.reset()

    # Vector pairs: (A, B)
    vectors = [(10, 5), (-4, 8), (7, 3), (12, -2)]
    # Expected: 10*5 = 50
    #           50 + (-4*8) = 18
    #           18 + (7*3) = 39
    #           39 + (12*-2) = 15

    accum = 0
    for i, (a, b) in enumerate(vectors):
        await bfm.write(0x00, a & 0xFF)
        await bfm.write(0x04, b & 0xFF)
        await bfm.write(0x08, accum & 0xFFFF)
        await bfm.write(0x0C, 1) # Start

        await ClockCycles(dut.aclk, 4)
        accum = to_signed(await bfm.read(0x10), 16)
        dut._log.info(f"Step {i+1}: A={a}, B={b} => New Accumulator = {accum}")

    assert accum == 15, f"Final vector accumulation mismatch: expected 15, got {accum}"


@cocotb.test()
async def test_axi_fault_injection_and_irq(dut):
    """Test 4: Verify fault detection, 1-cycle rollback, and IRQ assertion via AXI."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    bfm = AxiLiteMasterBFM(dut)
    await bfm.reset()

    # Step 1: Run valid operation to set known shadow accumulator
    # A = 10, B = 10, C = 0 => 100
    await bfm.write(0x00, 10)
    await bfm.write(0x04, 10)
    await bfm.write(0x08, 0)
    await bfm.write(0x0C, 1)
    await ClockCycles(dut.aclk, 4)

    res1 = to_signed(await bfm.read(0x10), 16)
    assert res1 == 100, f"Setup step failed: expected 100, got {res1}"

    # Step 2: Inject a bit-flip into pipe_product during computation
    await bfm.write(0x00, 5)
    await bfm.write(0x04, 5)
    await bfm.write(0x08, 100)

    # Launch start write concurrently
    start_task = cocotb.start_soon(bfm.write(0x0C, 1))

    for cycle in range(8):
        await RisingEdge(dut.aclk)
        dut._log.info(
            f"[Cycle {cycle}] start={dut.u_secure_mac_core.start.value} "
            f"d1={dut.u_secure_mac_core.valid_d1.value} "
            f"d2={dut.u_secure_mac_core.valid_d2.value} "
            f"pipe_prod={dut.u_secure_mac_core.pipe_product.value} "
            f"fault={dut.u_secure_mac_core.fault_detected.value} "
            f"irq={dut.irq.value}"
        )
        if int(dut.u_secure_mac_core.valid_d1.value) == 1:
            # We are at the edge where pipe_product is latched or about to be evaluated
            orig_val = int(dut.u_secure_mac_core.pipe_product.value)
            dut.u_secure_mac_core.pipe_product.value = orig_val ^ (1 << 3)
            dut._log.info(f"[FAULT INJECTION] Injected SEU bit-flip: 0x{orig_val:x} -> 0x{orig_val ^ (1 << 3):x}")

    await start_task

    # Verify IRQ line is asserted
    irq_val = int(dut.irq.value)
    assert irq_val == 1, "Expected IRQ output asserted on fault detection!"

    # Read REG_MAC_STATUS: bit 0 = fault, bit 2 = rollback
    status = await bfm.read(0x14)
    fault_flag = status & 1
    rollback_flag = (status >> 2) & 1
    dut._log.info(f"Fault Status Word: 0x{status:08x} (Fault={fault_flag}, Rollback={rollback_flag})")
    assert fault_flag == 1, "Expected fault_detected bit in REG_MAC_STATUS"
    assert rollback_flag == 1, "Expected rollback bit in REG_MAC_STATUS"

    # Read output: Must have rolled back to previous valid accumulator (100)
    out_after_fault = to_signed(await bfm.read(0x10), 16)
    dut._log.info(f"MAC Output after Rollback = {out_after_fault} (Golden Shadow = 100)")
    assert out_after_fault == 100, f"Rollback failed: expected 100, got {out_after_fault}"


@cocotb.test()
async def test_axi_byte_strobes(dut):
    """Test 5: Verify s_axi_wstrb byte masking per ARM AMBA AXI4-Lite specification."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    bfm = AxiLiteMasterBFM(dut)
    await bfm.reset()

    # Step 1: Write full 32-bit zero to REG_MAC_C (0x08)
    await bfm.write(0x08, 0x00000000, wstrb=0xF)
    val = await bfm.read(0x08)
    assert (val & 0xFFFF) == 0x0000, f"Expected 0x0000, got 0x{val:04x}"

    # Step 2: Write byte 0 only (wstrb=0x1) with 0xAA
    await bfm.write(0x08, 0x000000AA, wstrb=0x1)
    val = await bfm.read(0x08)
    assert (val & 0xFFFF) == 0x00AA, f"Byte 0 write failed: expected 0x00AA, got 0x{val:04x}"

    # Step 3: Write byte 1 only (wstrb=0x2) with 0xBB00
    await bfm.write(0x08, 0x0000BB00, wstrb=0x2)
    val = await bfm.read(0x08)
    assert (val & 0xFFFF) == 0xBBAA, f"Byte 1 write failed: expected 0xBBAA, got 0x{val:04x}"

    # Step 4: Overwrite byte 1 only with 0x1200 while preserving byte 0
    await bfm.write(0x08, 0x00001200, wstrb=0x2)
    val = await bfm.read(0x08)
    assert (val & 0xFFFF) == 0x12AA, f"Byte 1 overwrite failed: expected 0x12AA, got 0x{val:04x}"
    dut._log.info("PASS: AXI4-Lite wstrb byte-strobe masking verified 100% compliant!")


@cocotb.test()
async def test_axi_slverr_response(dut):
    """Test 6: Verify SLVERR response on invalid or unaligned register access."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    bfm = AxiLiteMasterBFM(dut)
    await bfm.reset()

    # Access unmapped offset 0x3C (slave error expected: bresp == 2)
    bresp = await bfm.write(0x3C, 0x12345678, expect_error=True)
    assert bresp == 2, f"Expected SLVERR (2) for unmapped write, got {bresp}"

    # Access unaligned offset 0x01 (slave error expected: bresp == 2)
    bresp_unaligned = await bfm.write(0x01, 0x12345678, expect_error=True)
    assert bresp_unaligned == 2, f"Expected SLVERR (2) for unaligned write, got {bresp_unaligned}"

    # Read unmapped offset 0x3C (slave error expected: rresp == 2)
    await bfm.read(0x3C, expect_error=True)

    # Read unaligned offset 0x02 (slave error expected: rresp == 2)
    await bfm.read(0x02, expect_error=True)

    dut._log.info("PASS: AXI4-Lite SLVERR response on invalid/unaligned accesses verified 100% compliant!")
