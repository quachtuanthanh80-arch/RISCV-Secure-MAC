`timescale 1ns/1ps
//=============================================================================
// cpu_to_axi_master.v – CPU Memory Bus to AXI4-Lite Master Bridge
//
// Converts CPU synchronous memory transactions:
//   (mem_addr, mem_write, mem_wdata, mem_valid, mem_ready, mem_rdata)
// into ARM AMBA AXI4-Lite Master 5-channel transactions:
//   (AW, W, B, AR, R)
//
// Optimized for zero-wait state single-cycle memory transactions when
// slaves respond with immediate ready, while supporting arbitrary slave
// wait states through standard AXI valid/ready handshaking.
//=============================================================================

module cpu_to_axi_master #(
    parameter integer C_M_AXI_ADDR_WIDTH = 32,
    parameter integer C_M_AXI_DATA_WIDTH = 32
)(
    input  wire                                 clk,
    input  wire                                 rst_n,

    //--- CPU Core Memory Interface -------------------------------------------
    input  wire [C_M_AXI_ADDR_WIDTH-1:0]        mem_addr,
    input  wire                                 mem_write,
    input  wire [C_M_AXI_DATA_WIDTH-1:0]        mem_wdata,
    input  wire                                 mem_valid,
    output wire                                 mem_ready,
    output wire [C_M_AXI_DATA_WIDTH-1:0]        mem_rdata,

    //--- AXI4-Lite Master Interface ------------------------------------------
    // Write Address Channel (AW)
    output wire [C_M_AXI_ADDR_WIDTH-1:0]        m_axi_awaddr,
    output wire [2:0]                           m_axi_awprot,
    output wire                                 m_axi_awvalid,
    input  wire                                 m_axi_awready,

    // Write Data Channel (W)
    output wire [C_M_AXI_DATA_WIDTH-1:0]        m_axi_wdata,
    output wire [(C_M_AXI_DATA_WIDTH/8)-1:0]    m_axi_wstrb,
    output wire                                 m_axi_wvalid,
    input  wire                                 m_axi_wready,

    // Write Response Channel (B)
    input  wire [1:0]                           m_axi_bresp,
    input  wire                                 m_axi_bvalid,
    output wire                                 m_axi_bready,

    // Read Address Channel (AR)
    output wire [C_M_AXI_ADDR_WIDTH-1:0]        m_axi_araddr,
    output wire [2:0]                           m_axi_arprot,
    output wire                                 m_axi_arvalid,
    input  wire                                 m_axi_arready,

    // Read Data Channel (R)
    input  wire [C_M_AXI_DATA_WIDTH-1:0]        m_axi_rdata,
    input  wire [1:0]                           m_axi_rresp,
    input  wire                                 m_axi_rvalid,
    output wire                                 m_axi_rready
);

    // Constant protection attributes
    assign m_axi_awprot = 3'b000;
    assign m_axi_arprot = 3'b000;
    assign m_axi_wstrb  = 4'b1111;

    // Direct channel drive when transaction is active
    wire is_write = mem_valid & mem_write;
    wire is_read  = mem_valid & (~mem_write);

    // AW Channel
    assign m_axi_awaddr  = mem_addr;
    assign m_axi_awvalid = is_write;

    // W Channel
    assign m_axi_wdata   = mem_wdata;
    assign m_axi_wvalid  = is_write;

    // B Channel
    assign m_axi_bready  = is_write;

    // AR Channel
    assign m_axi_araddr  = mem_addr;
    assign m_axi_arvalid = is_read;

    // R Channel
    assign m_axi_rready  = is_read;

    // CPU handshaking feedback
    assign mem_ready = is_write ? (m_axi_bvalid & m_axi_awready & m_axi_wready) :
                       is_read  ? (m_axi_rvalid & m_axi_arready) : 1'b1;

    assign mem_rdata = is_read ? m_axi_rdata : {C_M_AXI_DATA_WIDTH{1'b0}};

endmodule
