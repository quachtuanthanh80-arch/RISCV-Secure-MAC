`timescale 1ns/1ps

module secure_mac_axi_sva #(
    parameter integer C_S_AXI_ADDR_WIDTH = 32,
    parameter integer C_S_AXI_DATA_WIDTH = 32
)(
    input logic                            aclk,
    input logic                            aresetn,
    input logic [C_S_AXI_ADDR_WIDTH-1:0]   s_axi_awaddr,
    input logic [2:0]                      s_axi_awprot,
    input logic                            s_axi_awvalid,
    input logic                            s_axi_awready,
    input logic [C_S_AXI_DATA_WIDTH-1:0]   s_axi_wdata,
    input logic [(C_S_AXI_DATA_WIDTH/8)-1:0] s_axi_wstrb,
    input logic                            s_axi_wvalid,
    input logic                            s_axi_wready,
    input logic [1:0]                      s_axi_bresp,
    input logic                            s_axi_bvalid,
    input logic                            s_axi_bready,
    input logic [C_S_AXI_ADDR_WIDTH-1:0]   s_axi_araddr,
    input logic [2:0]                      s_axi_arprot,
    input logic                            s_axi_arvalid,
    input logic                            s_axi_arready,
    input logic [C_S_AXI_DATA_WIDTH-1:0]   s_axi_rdata,
    input logic [1:0]                      s_axi_rresp,
    input logic                            s_axi_rvalid,
    input logic                            s_axi_rready
);

    // Shadow state registers for temporal checks
    logic                            prev_aresetn;
    logic                            prev_awvalid;
    logic                            prev_awready;
    logic [C_S_AXI_ADDR_WIDTH-1:0]   prev_awaddr;
    logic [2:0]                      prev_awprot;
    logic                            prev_wvalid;
    logic                            prev_wready;
    logic [C_S_AXI_DATA_WIDTH-1:0]   prev_wdata;
    logic [(C_S_AXI_DATA_WIDTH/8)-1:0] prev_wstrb;
    logic                            prev_bvalid;
    logic                            prev_bready;
    logic [1:0]                      prev_bresp;
    logic                            prev_arvalid;
    logic                            prev_arready;
    logic [C_S_AXI_ADDR_WIDTH-1:0]   prev_araddr;
    logic [2:0]                      prev_arprot;
    logic                            prev_rvalid;
    logic                            prev_rready;
    logic [C_S_AXI_DATA_WIDTH-1:0]   prev_rdata;
    logic [1:0]                      prev_rresp;

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            prev_aresetn <= 1'b0;
            prev_awvalid <= 1'b0;
            prev_awready <= 1'b0;
            prev_awaddr  <= '0;
            prev_awprot  <= '0;
            prev_wvalid  <= 1'b0;
            prev_wready  <= 1'b0;
            prev_wdata   <= '0;
            prev_wstrb   <= '0;
            prev_bvalid  <= 1'b0;
            prev_bready  <= 1'b0;
            prev_bresp   <= '0;
            prev_arvalid <= 1'b0;
            prev_arready <= 1'b0;
            prev_araddr  <= '0;
            prev_arprot  <= '0;
            prev_rvalid  <= 1'b0;
            prev_rready  <= 1'b0;
            prev_rdata   <= '0;
            prev_rresp   <= '0;
        end else begin
            prev_aresetn <= aresetn;
            prev_awvalid <= s_axi_awvalid;
            prev_awready <= s_axi_awready;
            prev_awaddr  <= s_axi_awaddr;
            prev_awprot  <= s_axi_awprot;
            prev_wvalid  <= s_axi_wvalid;
            prev_wready  <= s_axi_wready;
            prev_wdata   <= s_axi_wdata;
            prev_wstrb   <= s_axi_wstrb;
            prev_bvalid  <= s_axi_bvalid;
            prev_bready  <= s_axi_bready;
            prev_bresp   <= s_axi_bresp;
            prev_arvalid <= s_axi_arvalid;
            prev_arready <= s_axi_arready;
            prev_araddr  <= s_axi_araddr;
            prev_arprot  <= s_axi_arprot;
            prev_rvalid  <= s_axi_rvalid;
            prev_rready  <= s_axi_rready;
            prev_rdata   <= s_axi_rdata;
            prev_rresp   <= s_axi_rresp;
        end
    end

    // 1. Reset Invariants: Valid signals must be deasserted during reset (AMBA A3.1.2)
    always @(posedge aclk) begin
        if (aresetn === 1'b0) begin
            if (s_axi_bvalid !== 1'bx) begin
                assert (s_axi_bvalid === 1'b0)
                    else $error("[SVA-AXI FAIL] bvalid high while aresetn is LOW!");
            end
            if (s_axi_rvalid !== 1'bx) begin
                assert (s_axi_rvalid === 1'b0)
                    else $error("[SVA-AXI FAIL] rvalid high while aresetn is LOW!");
            end
        end
    end

    // 2. AMBA A3.2.1: Write Address Channel Stability while AWVALID is stalled
    always @(posedge aclk) begin
        if (aresetn && prev_aresetn) begin
            if (prev_awvalid && !prev_awready) begin
                assert (s_axi_awvalid)
                    else $error("[SVA-AXI FAIL] AWVALID dropped before AWREADY handshake!");
                assert (s_axi_awaddr == prev_awaddr)
                    else $error("[SVA-AXI FAIL] AWADDR mutated while AWVALID was stalled!");
                assert (s_axi_awprot == prev_awprot)
                    else $error("[SVA-AXI FAIL] AWPROT mutated while AWVALID was stalled!");
            end
        end
    end

    // 3. AMBA A3.2.1: Write Data Channel Stability while WVALID is stalled
    always @(posedge aclk) begin
        if (aresetn && prev_aresetn) begin
            if (prev_wvalid && !prev_wready) begin
                assert (s_axi_wvalid)
                    else $error("[SVA-AXI FAIL] WVALID dropped before WREADY handshake!");
                assert (s_axi_wdata == prev_wdata)
                    else $error("[SVA-AXI FAIL] WDATA mutated while WVALID was stalled!");
                assert (s_axi_wstrb == prev_wstrb)
                    else $error("[SVA-AXI FAIL] WSTRB mutated while WVALID was stalled!");
            end
        end
    end

    // 4. AMBA A3.2.1: Write Response Channel Stability while BVALID is stalled
    always @(posedge aclk) begin
        if (aresetn && prev_aresetn) begin
            if (prev_bvalid && !prev_bready) begin
                assert (s_axi_bvalid)
                    else $error("[SVA-AXI FAIL] BVALID dropped before BREADY handshake!");
                assert (s_axi_bresp == prev_bresp)
                    else $error("[SVA-AXI FAIL] BRESP mutated while BVALID was stalled!");
            end
        end
    end

    // 5. AMBA A3.2.1: Read Address Channel Stability while ARVALID is stalled
    always @(posedge aclk) begin
        if (aresetn && prev_aresetn) begin
            if (prev_arvalid && !prev_arready) begin
                assert (s_axi_arvalid)
                    else $error("[SVA-AXI FAIL] ARVALID dropped before ARREADY handshake!");
                assert (s_axi_araddr == prev_araddr)
                    else $error("[SVA-AXI FAIL] ARADDR mutated while ARVALID was stalled!");
                assert (s_axi_arprot == prev_arprot)
                    else $error("[SVA-AXI FAIL] ARPROT mutated while ARVALID was stalled!");
            end
        end
    end

    // 6. AMBA A3.2.1: Read Data Channel Stability while RVALID is stalled
    always @(posedge aclk) begin
        if (aresetn && prev_aresetn) begin
            if (prev_rvalid && !prev_rready) begin
                assert (s_axi_rvalid)
                    else $error("[SVA-AXI FAIL] RVALID dropped before RREADY handshake!");
                assert (s_axi_rdata == prev_rdata)
                    else $error("[SVA-AXI FAIL] RDATA mutated while RVALID was stalled!");
                assert (s_axi_rresp == prev_rresp)
                    else $error("[SVA-AXI FAIL] RRESP mutated while RVALID was stalled!");
            end
        end
    end

    // 7. Response Code Validity (OKAY = 2'b00, SLVERR = 2'b10)
    always @(posedge aclk) begin
        if (aresetn) begin
            if (s_axi_bvalid) begin
                assert (s_axi_bresp == 2'b00 || s_axi_bresp == 2'b10)
                    else $error("[SVA-AXI FAIL] Invalid bresp code: %b (must be OKAY=00 or SLVERR=10)", s_axi_bresp);
            end
            if (s_axi_rvalid) begin
                assert (s_axi_rresp == 2'b00 || s_axi_rresp == 2'b10)
                    else $error("[SVA-AXI FAIL] Invalid rresp code: %b (must be OKAY=00 or SLVERR=10)", s_axi_rresp);
            end
        end
    end

endmodule
