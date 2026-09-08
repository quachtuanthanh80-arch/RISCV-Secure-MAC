`timescale 1ns/1ps
//=============================================================================
// axi_interconnect_1m2s.v – 1-Master to 2-Slave AXI4-Lite Crossbar Interconnect
//
// Address Mapping:
//   - Slave 0 (m0_axi_*): Base 0x0000_0000 (Data Memory DMEM RAM, addr[31] == 0)
//   - Slave 1 (m1_axi_*): Base 0x8000_0000 (Secure MAC Accelerator, addr[31] == 1)
//
// Clean combinational crossbar routing for zero-wait state operations:
//   - 0 pipeline cycles added
//   - Direct AXI handshaking between Master and addressed Slave
//=============================================================================

module axi_interconnect_1m2s #(
    parameter integer C_AXI_ADDR_WIDTH = 32,
    parameter integer C_AXI_DATA_WIDTH = 32
)(
    input  wire                             aclk,
    input  wire                             aresetn,

    //=========================================================================
    // Master Port (Connects to CPU Master)
    //=========================================================================
    // AW
    input  wire [C_AXI_ADDR_WIDTH-1:0]      s_axi_awaddr,
    input  wire [2:0]                       s_axi_awprot,
    input  wire                             s_axi_awvalid,
    output wire                             s_axi_awready,
    // W
    input  wire [C_AXI_DATA_WIDTH-1:0]      s_axi_wdata,
    input  wire [(C_AXI_DATA_WIDTH/8)-1:0]  s_axi_wstrb,
    input  wire                             s_axi_wvalid,
    output wire                             s_axi_wready,
    // B
    output wire [1:0]                       s_axi_bresp,
    output wire                             s_axi_bvalid,
    input  wire                             s_axi_bready,
    // AR
    input  wire [C_AXI_ADDR_WIDTH-1:0]      s_axi_araddr,
    input  wire [2:0]                       s_axi_arprot,
    input  wire                             s_axi_arvalid,
    output wire                             s_axi_arready,
    // R
    output wire [C_AXI_DATA_WIDTH-1:0]      s_axi_rdata,
    output wire [1:0]                       s_axi_rresp,
    output wire                             s_axi_rvalid,
    input  wire                             s_axi_rready,

    //=========================================================================
    // Slave 0 Port: Data RAM (addr[31] == 0)
    //=========================================================================
    output wire [C_AXI_ADDR_WIDTH-1:0]      m0_axi_awaddr,
    output wire [2:0]                       m0_axi_awprot,
    output wire                             m0_axi_awvalid,
    input  wire                             m0_axi_awready,
    output wire [C_AXI_DATA_WIDTH-1:0]      m0_axi_wdata,
    output wire [(C_AXI_DATA_WIDTH/8)-1:0]  m0_axi_wstrb,
    output wire                             m0_axi_wvalid,
    input  wire                             m0_axi_wready,
    input  wire [1:0]                       m0_axi_bresp,
    input  wire                             m0_axi_bvalid,
    output wire                             m0_axi_bready,

    output wire [C_AXI_ADDR_WIDTH-1:0]      m0_axi_araddr,
    output wire [2:0]                       m0_axi_arprot,
    output wire                             m0_axi_arvalid,
    input  wire                             m0_axi_arready,
    input  wire [C_AXI_DATA_WIDTH-1:0]      m0_axi_rdata,
    input  wire [1:0]                       m0_axi_rresp,
    input  wire                             m0_axi_rvalid,
    output wire                             m0_axi_rready,

    //=========================================================================
    // Slave 1 Port: Secure MAC (addr[31] == 1)
    //=========================================================================
    output wire [C_AXI_ADDR_WIDTH-1:0]      m1_axi_awaddr,
    output wire [2:0]                       m1_axi_awprot,
    output wire                             m1_axi_awvalid,
    input  wire                             m1_axi_awready,
    output wire [C_AXI_DATA_WIDTH-1:0]      m1_axi_wdata,
    output wire [(C_AXI_DATA_WIDTH/8)-1:0]  m1_axi_wstrb,
    output wire                             m1_axi_wvalid,
    input  wire                             m1_axi_wready,
    input  wire [1:0]                       m1_axi_bresp,
    input  wire                             m1_axi_bvalid,
    output wire                             m1_axi_bready,

    output wire [C_AXI_ADDR_WIDTH-1:0]      m1_axi_araddr,
    output wire [2:0]                       m1_axi_arprot,
    output wire                             m1_axi_arvalid,
    input  wire                             m1_axi_arready,
    input  wire [C_AXI_DATA_WIDTH-1:0]      m1_axi_rdata,
    input  wire [1:0]                       m1_axi_rresp,
    input  wire                             m1_axi_rvalid,
    output wire                             m1_axi_rready
);

    localparam [1:0] AXI_RESP_DECERR = 2'b11;

    // Address Decoding (Standard 16-bit prefix mapping)
    // Slave 0: Data RAM (0x0000_0000 - 0x0000_FFFF)
    // Slave 1: Secure MAC Accelerator (0x8000_0000 - 0x8000_FFFF)
    wire wr_sel_s0 = (s_axi_awaddr[31:16] == 16'h0000);
    wire wr_sel_s1 = (s_axi_awaddr[31:16] == 16'h8000);
    wire wr_unmapped = ~(wr_sel_s0 | wr_sel_s1);

    assign m0_axi_awaddr  = s_axi_awaddr;
    assign m0_axi_awprot  = s_axi_awprot;
    assign m0_axi_awvalid = s_axi_awvalid & wr_sel_s0;
    assign m0_axi_wdata   = s_axi_wdata;
    assign m0_axi_wstrb   = s_axi_wstrb;
    assign m0_axi_wvalid  = s_axi_wvalid & wr_sel_s0;
    assign m0_axi_bready  = s_axi_bready & wr_sel_s0;

    assign m1_axi_awaddr  = s_axi_awaddr;
    assign m1_axi_awprot  = s_axi_awprot;
    assign m1_axi_awvalid = s_axi_awvalid & wr_sel_s1;
    assign m1_axi_wdata   = s_axi_wdata;
    assign m1_axi_wstrb   = s_axi_wstrb;
    assign m1_axi_wvalid  = s_axi_wvalid & wr_sel_s1;
    assign m1_axi_bready  = s_axi_bready & wr_sel_s1;

    // Master Write Channel Feedback with DECERR handling
    assign s_axi_awready  = wr_sel_s0 ? m0_axi_awready :
                            wr_sel_s1 ? m1_axi_awready : 1'b1;

    assign s_axi_wready   = wr_sel_s0 ? m0_axi_wready  :
                            wr_sel_s1 ? m1_axi_wready  : 1'b1;

    assign s_axi_bvalid   = wr_sel_s0 ? m0_axi_bvalid  :
                            wr_sel_s1 ? m1_axi_bvalid  : (s_axi_awvalid & s_axi_wvalid);

    assign s_axi_bresp    = wr_sel_s0 ? m0_axi_bresp   :
                            wr_sel_s1 ? m1_axi_bresp   : AXI_RESP_DECERR;

    // Read Path Decoding
    wire rd_sel_s0 = (s_axi_araddr[31:16] == 16'h0000);
    wire rd_sel_s1 = (s_axi_araddr[31:16] == 16'h8000);
    wire rd_unmapped = ~(rd_sel_s0 | rd_sel_s1);

    assign m0_axi_araddr  = s_axi_araddr;
    assign m0_axi_arprot  = s_axi_arprot;
    assign m0_axi_arvalid = s_axi_arvalid & rd_sel_s0;
    assign m0_axi_rready  = s_axi_rready & rd_sel_s0;

    assign m1_axi_araddr  = s_axi_araddr;
    assign m1_axi_arprot  = s_axi_arprot;
    assign m1_axi_arvalid = s_axi_arvalid & rd_sel_s1;
    assign m1_axi_rready  = s_axi_rready & rd_sel_s1;

    // Master Read Channel Feedback with DECERR handling
    assign s_axi_arready  = rd_sel_s0 ? m0_axi_arready :
                            rd_sel_s1 ? m1_axi_arready : 1'b1;

    assign s_axi_rvalid   = rd_sel_s0 ? m0_axi_rvalid  :
                            rd_sel_s1 ? m1_axi_rvalid  : s_axi_arvalid;

    assign s_axi_rdata    = rd_sel_s0 ? m0_axi_rdata   :
                            rd_sel_s1 ? m1_axi_rdata   : {C_AXI_DATA_WIDTH{1'b0}};

    assign s_axi_rresp    = rd_sel_s0 ? m0_axi_rresp   :
                            rd_sel_s1 ? m1_axi_rresp   : AXI_RESP_DECERR;

endmodule
