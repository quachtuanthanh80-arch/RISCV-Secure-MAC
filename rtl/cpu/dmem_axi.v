`timescale 1ns/1ps

module dmem_axi #(
    parameter integer C_S_AXI_DATA_WIDTH = 32,
    parameter integer C_S_AXI_ADDR_WIDTH = 32
)(
    input  wire                                 aclk,
    input  wire                                 aresetn,

    input  wire [C_S_AXI_ADDR_WIDTH-1:0]        s_axi_awaddr,
    input  wire [2:0]                           s_axi_awprot,
    input  wire                                 s_axi_awvalid,
    output wire                                 s_axi_awready,

    input  wire [C_S_AXI_DATA_WIDTH-1:0]        s_axi_wdata,
    input  wire [(C_S_AXI_DATA_WIDTH/8)-1:0]    s_axi_wstrb,
    input  wire                                 s_axi_wvalid,
    output wire                                 s_axi_wready,

    output wire [1:0]                           s_axi_bresp,
    output wire                                 s_axi_bvalid,
    input  wire                                 s_axi_bready,

    input  wire [C_S_AXI_ADDR_WIDTH-1:0]        s_axi_araddr,
    input  wire [2:0]                           s_axi_arprot,
    input  wire                                 s_axi_arvalid,
    output wire                                 s_axi_arready,

    output wire [C_S_AXI_DATA_WIDTH-1:0]        s_axi_rdata,
    output wire [1:0]                           s_axi_rresp,
    output wire                                 s_axi_rvalid,
    input  wire                                 s_axi_rready
);

    localparam [1:0] AXI_RESP_OKAY   = 2'b00;
    localparam [1:0] AXI_RESP_DECERR = 2'b11;

    wire wr_addr_valid = (s_axi_awaddr[1:0] == 2'b00);
    wire rd_addr_valid = (s_axi_araddr[1:0] == 2'b00);

    reg axi_bvalid_reg;
    reg [1:0] axi_bresp_reg;
    reg axi_rvalid_reg;
    reg [1:0] axi_rresp_reg;
    reg [C_S_AXI_DATA_WIDTH-1:0] axi_rdata_reg;

    wire write_handshake = s_axi_awvalid && s_axi_wvalid;
    wire read_handshake  = s_axi_arvalid;

    assign s_axi_awready = 1'b1;
    assign s_axi_wready  = 1'b1;
    assign s_axi_arready = 1'b1;

    assign s_axi_bvalid = write_handshake | axi_bvalid_reg;
    assign s_axi_bresp  = axi_bvalid_reg ? axi_bresp_reg : (wr_addr_valid ? AXI_RESP_OKAY : AXI_RESP_DECERR);

    assign s_axi_rvalid = read_handshake | axi_rvalid_reg;
    assign s_axi_rresp  = axi_rvalid_reg ? axi_rresp_reg : (rd_addr_valid ? AXI_RESP_OKAY : AXI_RESP_DECERR);
    wire [31:0] mem_rd_data;
    assign s_axi_rdata  = axi_rvalid_reg ? axi_rdata_reg : mem_rd_data;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            axi_bvalid_reg <= 1'b0;
            axi_bresp_reg  <= AXI_RESP_OKAY;
            axi_rvalid_reg <= 1'b0;
            axi_rresp_reg  <= AXI_RESP_OKAY;
            axi_rdata_reg  <= {C_S_AXI_DATA_WIDTH{1'b0}};
        end else begin
            if (write_handshake && !s_axi_bready) begin
                axi_bvalid_reg <= 1'b1;
                axi_bresp_reg  <= wr_addr_valid ? AXI_RESP_OKAY : AXI_RESP_DECERR;
            end else if (s_axi_bready) begin
                axi_bvalid_reg <= 1'b0;
            end

            if (read_handshake && !s_axi_rready) begin
                axi_rvalid_reg <= 1'b1;
                axi_rresp_reg  <= rd_addr_valid ? AXI_RESP_OKAY : AXI_RESP_DECERR;
                axi_rdata_reg  <= mem_rd_data;
            end else if (s_axi_rready) begin
                axi_rvalid_reg <= 1'b0;
            end
        end
    end

    wire mem_we = write_handshake && wr_addr_valid;
    wire [31:0] mem_addr = mem_we ? s_axi_awaddr : s_axi_araddr;

    dmem u_ram (
        .clk   (aclk),
        .we    (mem_we),
        .wstrb (s_axi_wstrb),
        .a     (mem_addr),
        .wd    (s_axi_wdata),
        .rd    (mem_rd_data)
    );

endmodule
