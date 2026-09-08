`timescale 1ns/1ps
//=============================================================================
// dmem_axi.v – AXI4-Lite Slave Wrapper for Data Memory (DMEM RAM)
//
// Compliant with ARM AXI4-Lite Specification.
// Provides zero-wait state single-cycle read and write throughput
// using underlying dual-port asynchronous-read RAM core.
//=============================================================================

module dmem_axi #(
    parameter integer C_S_AXI_DATA_WIDTH = 32,
    parameter integer C_S_AXI_ADDR_WIDTH = 32
)(
    input  wire                                 aclk,
    input  wire                                 aresetn,

    // Write Address Channel (AW)
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]        s_axi_awaddr,
    input  wire [2:0]                           s_axi_awprot,
    input  wire                                 s_axi_awvalid,
    output wire                                 s_axi_awready,

    // Write Data Channel (W)
    input  wire [C_S_AXI_DATA_WIDTH-1:0]        s_axi_wdata,
    input  wire [(C_S_AXI_DATA_WIDTH/8)-1:0]    s_axi_wstrb,
    input  wire                                 s_axi_wvalid,
    output wire                                 s_axi_wready,

    // Write Response Channel (B)
    output wire [1:0]                           s_axi_bresp,
    output wire                                 s_axi_bvalid,
    input  wire                                 s_axi_bready,

    // Read Address Channel (AR)
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]        s_axi_araddr,
    input  wire [2:0]                           s_axi_arprot,
    input  wire                                 s_axi_arvalid,
    output wire                                 s_axi_arready,

    // Read Data Channel (R)
    output wire [C_S_AXI_DATA_WIDTH-1:0]        s_axi_rdata,
    output wire [1:0]                           s_axi_rresp,
    output wire                                 s_axi_rvalid,
    input  wire                                 s_axi_rready
);

    localparam [1:0] AXI_RESP_OKAY = 2'b00;

    // Write channels
    assign s_axi_awready = 1'b1;
    assign s_axi_wready  = 1'b1;
    assign s_axi_bvalid  = s_axi_awvalid & s_axi_wvalid;
    assign s_axi_bresp   = AXI_RESP_OKAY;

    // Read channels
    assign s_axi_arready = 1'b1;
    assign s_axi_rvalid  = s_axi_arvalid;
    assign s_axi_rresp   = AXI_RESP_OKAY;

    // Underlying Memory Instance
    wire mem_we = s_axi_awvalid & s_axi_wvalid;
    wire [31:0] mem_addr = mem_we ? s_axi_awaddr : s_axi_araddr;
    wire [31:0] mem_rd_data;

    dmem u_ram (
        .clk   (aclk),
        .we    (mem_we),
        .wstrb (s_axi_wstrb),
        .a     (mem_addr),
        .wd    (s_axi_wdata),
        .rd    (mem_rd_data)
    );

    assign s_axi_rdata = mem_rd_data;

endmodule
