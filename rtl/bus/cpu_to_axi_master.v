`timescale 1ns/1ps
module cpu_to_axi_master #(
    parameter integer C_M_AXI_ADDR_WIDTH = 32,
    parameter integer C_M_AXI_DATA_WIDTH = 32
)(
    input  wire                                 clk,
    input  wire                                 rst_n,

    input  wire [C_M_AXI_ADDR_WIDTH-1:0]        mem_addr,
    input  wire                                 mem_write,
    input  wire [C_M_AXI_DATA_WIDTH-1:0]        mem_wdata,
    input  wire                                 mem_valid,
    output wire                                 mem_ready,
    output wire [C_M_AXI_DATA_WIDTH-1:0]        mem_rdata,

    output wire [C_M_AXI_ADDR_WIDTH-1:0]        m_axi_awaddr,
    output wire [2:0]                           m_axi_awprot,
    output wire                                 m_axi_awvalid,
    input  wire                                 m_axi_awready,

    output wire [C_M_AXI_DATA_WIDTH-1:0]        m_axi_wdata,
    output wire [(C_M_AXI_DATA_WIDTH/8)-1:0]    m_axi_wstrb,
    output wire                                 m_axi_wvalid,
    input  wire                                 m_axi_wready,

    input  wire [1:0]                           m_axi_bresp,
    input  wire                                 m_axi_bvalid,
    output wire                                 m_axi_bready,

    output wire [C_M_AXI_ADDR_WIDTH-1:0]        m_axi_araddr,
    output wire [2:0]                           m_axi_arprot,
    output wire                                 m_axi_arvalid,
    input  wire                                 m_axi_arready,

    input  wire [C_M_AXI_DATA_WIDTH-1:0]        m_axi_rdata,
    input  wire [1:0]                           m_axi_rresp,
    input  wire                                 m_axi_rvalid,
    output wire                                 m_axi_rready
);

    assign m_axi_awprot = 3'b000;
    assign m_axi_arprot = 3'b000;
    assign m_axi_wstrb  = 4'b1111;

    wire is_write = mem_valid & mem_write;
    wire is_read  = mem_valid & (~mem_write);

    assign m_axi_awaddr  = mem_addr;
    assign m_axi_awvalid = is_write;

    assign m_axi_wdata   = mem_wdata;
    assign m_axi_wvalid  = is_write;

    assign m_axi_bready  = is_write;

    assign m_axi_araddr  = mem_addr;
    assign m_axi_arvalid = is_read;

    assign m_axi_rready  = is_read;

    // CPU handshaking feedback
    assign mem_ready = is_write ? (m_axi_bvalid & m_axi_awready & m_axi_wready) :
                       is_read  ? (m_axi_rvalid & m_axi_arready) : 1'b1;

    assign mem_rdata = is_read ? m_axi_rdata : {C_M_AXI_DATA_WIDTH{1'b0}};

endmodule
