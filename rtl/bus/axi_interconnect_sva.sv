`timescale 1ns/1ps

module axi_interconnect_sva #(
    parameter integer C_AXI_ADDR_WIDTH = 32,
    parameter integer C_AXI_DATA_WIDTH = 32
)(
    input logic                            aclk,
    input logic                            aresetn,

    // Upstream Slave Port (from CPU)
    input logic [C_AXI_ADDR_WIDTH-1:0]     s_axi_awaddr,
    input logic [2:0]                      s_axi_awprot,
    input logic                            s_axi_awvalid,
    input logic                            s_axi_awready,
    input logic [C_AXI_DATA_WIDTH-1:0]     s_axi_wdata,
    input logic [(C_AXI_DATA_WIDTH/8)-1:0] s_axi_wstrb,
    input logic                            s_axi_wvalid,
    input logic                            s_axi_wready,
    input logic [1:0]                      s_axi_bresp,
    input logic                            s_axi_bvalid,
    input logic                            s_axi_bready,
    input logic [C_AXI_ADDR_WIDTH-1:0]     s_axi_araddr,
    input logic [2:0]                      s_axi_arprot,
    input logic                            s_axi_arvalid,
    input logic                            s_axi_arready,
    input logic [C_AXI_DATA_WIDTH-1:0]     s_axi_rdata,
    input logic [1:0]                      s_axi_rresp,
    input logic                            s_axi_rvalid,
    input logic                            s_axi_rready,

    // Downstream Port 0 (Data RAM)
    input logic                            m0_axi_awvalid,
    input logic                            m0_axi_wvalid,
    input logic                            m0_axi_arvalid,

    // Downstream Port 1 (Secure MAC)
    input logic                            m1_axi_awvalid,
    input logic                            m1_axi_wvalid,
    input logic                            m1_axi_arvalid
);

    localparam [1:0] AXI_RESP_DECERR = 2'b11;

    logic                            prev_aresetn;
    logic                            prev_awvalid;
    logic                            prev_awready;
    logic [C_AXI_ADDR_WIDTH-1:0]   prev_awaddr;
    logic                            prev_wvalid;
    logic                            prev_wready;
    logic [C_AXI_DATA_WIDTH-1:0]   prev_wdata;
    logic                            prev_arvalid;
    logic                            prev_arready;
    logic [C_AXI_ADDR_WIDTH-1:0]   prev_araddr;

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            prev_aresetn <= 1'b0;
            prev_awvalid <= 1'b0;
            prev_awready <= 1'b0;
            prev_awaddr  <= '0;
            prev_wvalid  <= 1'b0;
            prev_wready  <= 1'b0;
            prev_wdata   <= '0;
            prev_arvalid <= 1'b0;
            prev_arready <= 1'b0;
            prev_araddr  <= '0;
        end else begin
            prev_aresetn <= aresetn;
            prev_awvalid <= s_axi_awvalid;
            prev_awready <= s_axi_awready;
            prev_awaddr  <= s_axi_awaddr;
            prev_wvalid  <= s_axi_wvalid;
            prev_wready  <= s_axi_wready;
            prev_wdata   <= s_axi_wdata;
            prev_arvalid <= s_axi_arvalid;
            prev_arready <= s_axi_arready;
            prev_araddr  <= s_axi_araddr;
        end
    end

    // 1. Reset Invariant Checks
    always @(posedge aclk) begin
        if (aresetn === 1'b0) begin
            if (s_axi_bvalid !== 1'bx) begin
                assert (s_axi_bvalid === 1'b0)
                    else $error("[SVA-XBAR FAIL] s_axi_bvalid high during reset!");
            end
            if (s_axi_rvalid !== 1'bx) begin
                assert (s_axi_rvalid === 1'b0)
                    else $error("[SVA-XBAR FAIL] s_axi_rvalid high during reset!");
            end
        end
    end

    // 2. Routing Isolation for Write Address Channel
    always @(posedge aclk) begin
        if (aresetn) begin
            if (s_axi_awvalid) begin
                if (s_axi_awaddr[31:16] == 16'h0000) begin
                    assert (m0_axi_awvalid == 1'b1 && m1_axi_awvalid == 1'b0)
                        else $error("[SVA-XBAR FAIL] S0 AW routing violation! s_axi_awaddr=%h", s_axi_awaddr);
                end else if (s_axi_awaddr[31:16] == 16'h8000) begin
                    assert (m1_axi_awvalid == 1'b1 && m0_axi_awvalid == 1'b0)
                        else $error("[SVA-XBAR FAIL] S1 AW routing violation! s_axi_awaddr=%h", s_axi_awaddr);
                end else begin
                    assert (m0_axi_awvalid == 1'b0 && m1_axi_awvalid == 1'b0)
                        else $error("[SVA-XBAR FAIL] Unmapped AW leaked to downstream slaves! addr=%h", s_axi_awaddr);
                    if (s_axi_wvalid) begin
                        assert (s_axi_bresp == AXI_RESP_DECERR && s_axi_bvalid == 1'b1)
                            else $error("[SVA-XBAR FAIL] Unmapped write did not generate DECERR (2'b11)!");
                    end
                end
            end
        end
    end

    // 3. Routing Isolation for Read Address Channel
    always @(posedge aclk) begin
        if (aresetn) begin
            if (s_axi_arvalid) begin
                if (s_axi_araddr[31:16] == 16'h0000) begin
                    assert (m0_axi_arvalid == 1'b1 && m1_axi_arvalid == 1'b0)
                        else $error("[SVA-XBAR FAIL] S0 AR routing violation! s_axi_araddr=%h", s_axi_araddr);
                end else if (s_axi_araddr[31:16] == 16'h8000) begin
                    assert (m1_axi_arvalid == 1'b1 && m0_axi_arvalid == 1'b0)
                        else $error("[SVA-XBAR FAIL] S1 AR routing violation! s_axi_araddr=%h", s_axi_araddr);
                end else begin
                    assert (m0_axi_arvalid == 1'b0 && m1_axi_arvalid == 1'b0)
                        else $error("[SVA-XBAR FAIL] Unmapped AR leaked to downstream slaves! addr=%h", s_axi_araddr);
                    assert (s_axi_rresp == AXI_RESP_DECERR && s_axi_rvalid == 1'b1)
                        else $error("[SVA-XBAR FAIL] Unmapped read did not generate DECERR (2'b11)!");
                end
            end
        end
    end

    // 4. Upstream Channel Stability while Stalled
    always @(posedge aclk) begin
        if (aresetn && prev_aresetn) begin
            if (prev_awvalid && !prev_awready) begin
                assert (s_axi_awvalid && s_axi_awaddr == prev_awaddr)
                    else $error("[SVA-XBAR FAIL] AW channel dropped or mutated while stalled!");
            end
            if (prev_wvalid && !prev_wready) begin
                assert (s_axi_wvalid && s_axi_wdata == prev_wdata)
                    else $error("[SVA-XBAR FAIL] W channel dropped or mutated while stalled!");
            end
            if (prev_arvalid && !prev_arready) begin
                assert (s_axi_arvalid && s_axi_araddr == prev_araddr)
                    else $error("[SVA-XBAR FAIL] AR channel dropped or mutated while stalled!");
            end
        end
    end

endmodule
