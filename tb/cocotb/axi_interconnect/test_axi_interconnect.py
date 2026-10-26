"""
Dedicated Cocotb Test Suite for axi_interconnect_1m2s (1M2S Crossbar Interconnect).
Verifies:
1. System Reset & Idle Handshake Lines.
2. Slave 0 Address Space Routing (0x0000_XXXX -> DMEM).
3. Slave 1 Address Space Routing (0x8000_XXXX -> Secure MAC).
4. Unmapped Address Space Protection & DECERR (2'b11) Handshake.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


async def reset_dut(dut):
    """Reset interconnect DUT."""
    await Timer(2, unit="ns")
    dut.m0_axi_bvalid.value = 0
    dut.m0_axi_rvalid.value = 0
    dut.m1_axi_bvalid.value = 0
    dut.m1_axi_rvalid.value = 0

    dut.s_axi_awvalid.value = 0
    dut.s_axi_awaddr.value = 0
    dut.s_axi_awprot.value = 0
    dut.s_axi_wvalid.value = 0
    dut.s_axi_wdata.value = 0
    dut.s_axi_wstrb.value = 0
    dut.s_axi_bready.value = 0
    dut.s_axi_arvalid.value = 0
    dut.s_axi_araddr.value = 0
    dut.s_axi_arprot.value = 0
    dut.s_axi_rready.value = 0
    dut.aresetn.value = 0

    dut.m0_axi_awready.value = 1
    dut.m0_axi_wready.value = 1
    dut.m0_axi_bresp.value = 0
    dut.m0_axi_arready.value = 1
    dut.m0_axi_rdata.value = 0x11112222
    dut.m0_axi_rresp.value = 0

    dut.m1_axi_awready.value = 1
    dut.m1_axi_wready.value = 1
    dut.m1_axi_bresp.value = 0
    dut.m1_axi_arready.value = 1
    dut.m1_axi_rdata.value = 0x33334444
    dut.m1_axi_rresp.value = 0

    await Timer(2, unit="ns")
    for _ in range(3):
        await RisingEdge(dut.aclk)
    await FallingEdge(dut.aclk)
    dut.aresetn.value = 1
    await RisingEdge(dut.aclk)

    # After reset, slaves can provide active valid mocks
    dut.m0_axi_bvalid.value = 1
    dut.m0_axi_rvalid.value = 1
    dut.m1_axi_bvalid.value = 1
    dut.m1_axi_rvalid.value = 1


@cocotb.test()
async def test_interconnect_route_slave0(dut):
    """Test 1: Routing write and read to Slave 0 (0x0000_0010)."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Issue write to Slave 0
    dut.s_axi_awaddr.value = 0x00000010
    dut.s_axi_awvalid.value = 1
    dut.s_axi_wdata.value = 0xAABBCCDD
    dut.s_axi_wstrb.value = 0xF
    dut.s_axi_wvalid.value = 1
    dut.s_axi_bready.value = 1

    await Timer(1, unit="ns")
    assert int(dut.m0_axi_awvalid.value) == 1, "Expected m0_axi_awvalid high for Slave 0"
    assert int(dut.m1_axi_awvalid.value) == 0, "Expected m1_axi_awvalid low for Slave 0"
    assert int(dut.s_axi_bresp.value) == 0, "Expected OKAY response for Slave 0"

    # Issue read from Slave 0
    dut.s_axi_awvalid.value = 0
    dut.s_axi_wvalid.value = 0
    dut.s_axi_araddr.value = 0x00000010
    dut.s_axi_arvalid.value = 1
    dut.s_axi_rready.value = 1

    await Timer(1, unit="ns")
    assert int(dut.m0_axi_arvalid.value) == 1, "Expected m0_axi_arvalid high for Slave 0"
    assert int(dut.m1_axi_arvalid.value) == 0, "Expected m1_axi_arvalid low for Slave 0"
    assert int(dut.s_axi_rdata.value) == 0x11112222, "Expected m0 read data routed to master"
    dut._log.info("PASS: Slave 0 address routing verified!")


@cocotb.test()
async def test_interconnect_route_slave1(dut):
    """Test 2: Routing write and read to Slave 1 (0x8000_0004)."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Issue write to Slave 1
    dut.s_axi_awaddr.value = 0x80000004
    dut.s_axi_awvalid.value = 1
    dut.s_axi_wdata.value = 0x55667788
    dut.s_axi_wstrb.value = 0xF
    dut.s_axi_wvalid.value = 1
    dut.s_axi_bready.value = 1

    await Timer(1, unit="ns")
    assert int(dut.m1_axi_awvalid.value) == 1, "Expected m1_axi_awvalid high for Slave 1"
    assert int(dut.m0_axi_awvalid.value) == 0, "Expected m0_axi_awvalid low for Slave 1"
    assert int(dut.s_axi_bresp.value) == 0, "Expected OKAY response for Slave 1"

    # Issue read from Slave 1
    dut.s_axi_awvalid.value = 0
    dut.s_axi_wvalid.value = 0
    dut.s_axi_araddr.value = 0x80000004
    dut.s_axi_arvalid.value = 1
    dut.s_axi_rready.value = 1

    await Timer(1, unit="ns")
    assert int(dut.m1_axi_arvalid.value) == 1, "Expected m1_axi_arvalid high for Slave 1"
    assert int(dut.m0_axi_arvalid.value) == 0, "Expected m0_axi_arvalid low for Slave 1"
    assert int(dut.s_axi_rdata.value) == 0x33334444, "Expected m1 read data routed to master"
    dut._log.info("PASS: Slave 1 address routing verified!")


@cocotb.test()
async def test_interconnect_decerr_unmapped(dut):
    """Test 3: Unmapped address access returns DECERR (2'b11) without hanging."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    unmapped_addresses = [0x10000000, 0x40000000, 0x90000000, 0xFFFF0000]

    for addr in unmapped_addresses:
        # Write to unmapped address
        dut.s_axi_awaddr.value = addr
        dut.s_axi_awvalid.value = 1
        dut.s_axi_wdata.value = 0xDEADBEEF
        dut.s_axi_wvalid.value = 1
        dut.s_axi_bready.value = 1

        await Timer(1, unit="ns")
        # Verify neither slave saw the transaction
        assert int(dut.m0_axi_awvalid.value) == 0, f"m0 saw unmapped address 0x{addr:08x}!"
        assert int(dut.m1_axi_awvalid.value) == 0, f"m1 saw unmapped address 0x{addr:08x}!"
        # Verify interconnect generated DECERR (2'b11 = 3)
        bresp = int(dut.s_axi_bresp.value)
        assert bresp == 3, f"Expected DECERR (3) for write to 0x{addr:08x}, got {bresp}"

        # Read from unmapped address
        dut.s_axi_awvalid.value = 0
        dut.s_axi_wvalid.value = 0
        dut.s_axi_araddr.value = addr
        dut.s_axi_arvalid.value = 1
        dut.s_axi_rready.value = 1

        await Timer(1, unit="ns")
        assert int(dut.m0_axi_arvalid.value) == 0, f"m0 saw unmapped read 0x{addr:08x}!"
        assert int(dut.m1_axi_arvalid.value) == 0, f"m1 saw unmapped read 0x{addr:08x}!"
        rresp = int(dut.s_axi_rresp.value)
        assert rresp == 3, f"Expected DECERR (3) for read from 0x{addr:08x}, got {rresp}"

    dut.s_axi_arvalid.value = 0
    dut.s_axi_rready.value = 0
    await Timer(1, unit="ns")

    dut._log.info("PASS: All unmapped address accesses safely terminated with AXI DECERR (2'b11)!")


@cocotb.test()
async def test_interconnect_concurrent_rw(dut):
    """Test 4: Simultaneous Write to Slave 0 and Read from Slave 1 without deadlock."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    # Issue concurrent Write to Slave 0 and Read from Slave 1
    dut.s_axi_awaddr.value = 0x00000020
    dut.s_axi_awvalid.value = 1
    dut.s_axi_wdata.value = 0xCAFEBABE
    dut.s_axi_wstrb.value = 0xF
    dut.s_axi_wvalid.value = 1
    dut.s_axi_bready.value = 1

    dut.s_axi_araddr.value = 0x80000004
    dut.s_axi_arvalid.value = 1
    dut.s_axi_rready.value = 1

    await Timer(1, unit="ns")
    # Verify independent concurrent routing
    assert int(dut.m0_axi_awvalid.value) == 1, "m0_axi_awvalid should be active for Slave 0"
    assert int(dut.m1_axi_awvalid.value) == 0, "m1_axi_awvalid should be inactive for Slave 0"
    assert int(dut.m1_axi_arvalid.value) == 1, "m1_axi_arvalid should be active for Slave 1"
    assert int(dut.m0_axi_arvalid.value) == 0, "m0_axi_arvalid should be inactive for Slave 1"

    assert int(dut.s_axi_bresp.value) == 0, "Expected OKAY write response"
    assert int(dut.s_axi_rdata.value) == 0x33334444, "Expected m1 read data returned"
    assert int(dut.s_axi_rresp.value) == 0, "Expected OKAY read response"

    dut.s_axi_awvalid.value = 0
    dut.s_axi_wvalid.value = 0
    dut.s_axi_bready.value = 0
    dut.s_axi_arvalid.value = 0
    dut.s_axi_rready.value = 0
    await Timer(1, unit="ns")

    dut._log.info("PASS: Concurrent crossbar Read/Write verified successfully with zero interference!")


@cocotb.test()
async def test_interconnect_byte_strobes(dut):
    """Test 5: Byte strobe propagation through crossbar."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    strobes = [0x1, 0x2, 0x4, 0x8, 0x3, 0xC, 0xF]
    for strb in strobes:
        dut.s_axi_awaddr.value = 0x00000030
        dut.s_axi_awvalid.value = 1
        dut.s_axi_wdata.value = 0x11223344
        dut.s_axi_wstrb.value = strb
        dut.s_axi_wvalid.value = 1
        dut.s_axi_bready.value = 1

        await Timer(1, unit="ns")
        assert int(dut.m0_axi_wstrb.value) == strb, f"WSTRB mismatch: expected 0x{strb:x}, got 0x{int(dut.m0_axi_wstrb.value):x}"
        assert int(dut.m0_axi_awvalid.value) == 1

    dut.s_axi_awvalid.value = 0
    dut.s_axi_wvalid.value = 0
    dut.s_axi_bready.value = 0
    await Timer(1, unit="ns")

    dut._log.info("PASS: All partial byte strobes correctly propagated through crossbar!")


@cocotb.test()
async def test_interconnect_boundary_decerr(dut):
    """Test 6: Boundary address transition DECERR protection."""
    clock = Clock(dut.aclk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)

    boundary_addrs = [
        0x00010000,  # Exactly 1 byte above Slave 0 64KB region
        0x80010000,  # Exactly 1 byte above Slave 1 64KB region
        0x7FFFFFFC,  # Just below Slave 1 base
        0xFFFFFFFC,  # Top of 32-bit address space
    ]

    for b_addr in boundary_addrs:
        dut.s_axi_araddr.value = b_addr
        dut.s_axi_arvalid.value = 1
        dut.s_axi_rready.value = 1
        await Timer(1, unit="ns")

        assert int(dut.s_axi_rresp.value) == 3, f"Expected DECERR at boundary 0x{b_addr:08x}"
        assert int(dut.m0_axi_arvalid.value) == 0
        assert int(dut.m1_axi_arvalid.value) == 0

    dut._log.info("PASS: Address space boundary DECERR traps verified successfully!")
