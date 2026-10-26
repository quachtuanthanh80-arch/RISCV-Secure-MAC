`timescale 1ns/1ps

module cpu_to_axi_master_sva #(
    parameter integer C_M_AXI_ADDR_WIDTH = 32,
    parameter integer C_M_AXI_DATA_WIDTH = 32
)(
    input logic                            clk,
    input logic                            rst_n,

    // CPU Side Interface
    input logic [C_M_AXI_ADDR_WIDTH-1:0]   mem_addr,
    input logic                            mem_write,
    input logic [C_M_AXI_DATA_WIDTH-1:0]   mem_wdata,
    input logic                            mem_valid,
    input logic                            mem_ready,
    input logic [C_M_AXI_DATA_WIDTH-1:0]   mem_rdata,

    // AXI Master Side Interface
    input logic [C_M_AXI_ADDR_WIDTH-1:0]   m_axi_awaddr,
    input logic [2:0]                      m_axi_awprot,
    input logic                            m_axi_awvalid,
    input logic                            m_axi_awready,
    input logic [C_M_AXI_DATA_WIDTH-1:0]   m_axi_wdata,
    input logic [(C_M_AXI_DATA_WIDTH/8)-1:0] m_axi_wstrb,
    input logic                            m_axi_wvalid,
    input logic                            m_axi_wready,
    input logic [1:0]                      m_axi_bresp,
    input logic                            m_axi_bvalid,
    input logic                            m_axi_bready,
    input logic [C_M_AXI_ADDR_WIDTH-1:0]   m_axi_araddr,
    input logic [2:0]                      m_axi_arprot,
    input logic                            m_axi_arvalid,
    input logic                            m_axi_arready,
    input logic [C_M_AXI_DATA_WIDTH-1:0]   m_axi_rdata,
    input logic [1:0]                      m_axi_rresp,
    input logic                            m_axi_rvalid,
    input logic                            m_axi_rready
);

    // Shadow registers for tracking previous state
    logic                            prev_rst_n;
    logic                            prev_mem_valid;
    logic                            prev_mem_ready;
    logic                            prev_mem_write;
    logic [C_M_AXI_ADDR_WIDTH-1:0]   prev_mem_addr;
    logic [C_M_AXI_DATA_WIDTH-1:0]   prev_mem_wdata;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prev_rst_n     <= 1'b0;
            prev_mem_valid <= 1'b0;
            prev_mem_ready <= 1'b0;
            prev_mem_write <= 1'b0;
            prev_mem_addr  <= '0;
            prev_mem_wdata <= '0;
        end else begin
            prev_rst_n     <= rst_n;
            prev_mem_valid <= mem_valid;
            prev_mem_ready <= mem_ready;
            prev_mem_write <= mem_write;
            prev_mem_addr  <= mem_addr;
            prev_mem_wdata <= mem_wdata;
        end
    end

    // 1. Request Translation Invariants
    always @(posedge clk) begin
        if (rst_n) begin
            if (mem_valid && mem_write) begin
                assert (m_axi_awvalid == 1'b1)
                    else $error("[SVA-BRIDGE FAIL] mem_write without m_axi_awvalid!");
                assert (m_axi_wvalid == 1'b1)
                    else $error("[SVA-BRIDGE FAIL] mem_write without m_axi_wvalid!");
                assert (m_axi_awaddr == mem_addr)
                    else $error("[SVA-BRIDGE FAIL] AWADDR mismatch with mem_addr!");
                assert (m_axi_wdata == mem_wdata)
                    else $error("[SVA-BRIDGE FAIL] WDATA mismatch with mem_wdata!");
                assert (m_axi_bready == 1'b1)
                    else $error("[SVA-BRIDGE FAIL] BREADY not asserted during write request!");
            end else if (mem_valid && !mem_write) begin
                assert (m_axi_arvalid == 1'b1)
                    else $error("[SVA-BRIDGE FAIL] mem_read without m_axi_arvalid!");
                assert (m_axi_araddr == mem_addr)
                    else $error("[SVA-BRIDGE FAIL] ARADDR mismatch with mem_addr!");
                assert (m_axi_rready == 1'b1)
                    else $error("[SVA-BRIDGE FAIL] RREADY not asserted during read request!");
            end else begin
                assert (m_axi_awvalid == 1'b0)
                    else $error("[SVA-BRIDGE FAIL] AWVALID asserted while CPU is idle!");
                assert (m_axi_wvalid == 1'b0)
                    else $error("[SVA-BRIDGE FAIL] WVALID asserted while CPU is idle!");
                assert (m_axi_arvalid == 1'b0)
                    else $error("[SVA-BRIDGE FAIL] ARVALID asserted while CPU is idle!");
            end
        end
    end

    // 2. Response / Ready Handshake Invariants
    always @(posedge clk) begin
        if (rst_n) begin
            if (mem_valid && mem_write) begin
                if (m_axi_bvalid && m_axi_awready && m_axi_wready) begin
                    assert (mem_ready == 1'b1)
                        else $error("[SVA-BRIDGE FAIL] mem_ready not asserted upon full write handshake!");
                end else begin
                    assert (mem_ready == 1'b0)
                        else $error("[SVA-BRIDGE FAIL] mem_ready prematurely high before write response!");
                end
            end else if (mem_valid && !mem_write) begin
                if (m_axi_rvalid && m_axi_arready) begin
                    assert (mem_ready == 1'b1)
                        else $error("[SVA-BRIDGE FAIL] mem_ready not asserted upon full read handshake!");
                    assert (mem_rdata == m_axi_rdata)
                        else $error("[SVA-BRIDGE FAIL] mem_rdata does not mirror m_axi_rdata!");
                end else begin
                    assert (mem_ready == 1'b0)
                        else $error("[SVA-BRIDGE FAIL] mem_ready prematurely high before read response!");
                end
            end
        end
    end

    // 3. Signal Stability while CPU is stalled waiting for AXI Slave
    always @(posedge clk) begin
        if (rst_n && prev_rst_n) begin
            if (prev_mem_valid && !prev_mem_ready) begin
                assert (mem_valid == 1'b1)
                    else $error("[SVA-BRIDGE FAIL] mem_valid dropped before mem_ready handshake!");
                assert (mem_addr == prev_mem_addr)
                    else $error("[SVA-BRIDGE FAIL] mem_addr mutated while stalled!");
                assert (mem_write == prev_mem_write)
                    else $error("[SVA-BRIDGE FAIL] mem_write mutated while stalled!");
                if (mem_write) begin
                    assert (mem_wdata == prev_mem_wdata)
                        else $error("[SVA-BRIDGE FAIL] mem_wdata mutated while stalled!");
                end
            end
        end
    end

endmodule
