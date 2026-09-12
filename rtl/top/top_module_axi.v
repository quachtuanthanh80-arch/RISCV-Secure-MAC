`timescale 1ns/1ps

module top_module_axi (
    input  wire        clk,
    input  wire        rst_n,
    output wire        irq
);

    wire [31:0] cpu_mem_addr;
    wire        cpu_mem_write;
    wire [31:0] cpu_mem_wdata;
    wire        cpu_mem_valid;
    wire        cpu_mem_ready;
    wire [31:0] cpu_mem_rdata;

    // CPU Debug / Monitoring Signals
    wire        reg_write;
    wire [4:0]  rd_addr, rs1_addr, rs2_addr;
    wire [31:0] alu_out;
    wire [31:0] pc, pc_next;
    wire        mem_read;

    wire [31:0] m_axi_awaddr;
    wire [2:0]  m_axi_awprot;
    wire        m_axi_awvalid;
    wire        m_axi_awready;

    wire [31:0] m_axi_wdata;
    wire [3:0]  m_axi_wstrb;
    wire        m_axi_wvalid;
    wire        m_axi_wready;

    wire [1:0]  m_axi_bresp;
    wire        m_axi_bvalid;
    wire        m_axi_bready;

    wire [31:0] m_axi_araddr;
    wire [2:0]  m_axi_arprot;
    wire        m_axi_arvalid;
    wire        m_axi_arready;

    wire [31:0] m_axi_rdata;
    wire [1:0]  m_axi_rresp;
    wire        m_axi_rvalid;
    wire        m_axi_rready;

    wire [31:0] s0_axi_awaddr;
    wire [2:0]  s0_axi_awprot;
    wire        s0_axi_awvalid;
    wire        s0_axi_awready;

    wire [31:0] s0_axi_wdata;
    wire [3:0]  s0_axi_wstrb;
    wire        s0_axi_wvalid;
    wire        s0_axi_wready;

    wire [1:0]  s0_axi_bresp;
    wire        s0_axi_bvalid;
    wire        s0_axi_bready;

    wire [31:0] s0_axi_araddr;
    wire [2:0]  s0_axi_arprot;
    wire        s0_axi_arvalid;
    wire        s0_axi_arready;

    wire [31:0] s0_axi_rdata;
    wire [1:0]  s0_axi_rresp;
    wire        s0_axi_rvalid;
    wire        s0_axi_rready;

    wire [31:0] s1_axi_awaddr;
    wire [2:0]  s1_axi_awprot;
    wire        s1_axi_awvalid;
    wire        s1_axi_awready;

    wire [31:0] s1_axi_wdata;
    wire [3:0]  s1_axi_wstrb;
    wire        s1_axi_wvalid;
    wire        s1_axi_wready;

    wire [1:0]  s1_axi_bresp;
    wire        s1_axi_bvalid;
    wire        s1_axi_bready;

    wire [31:0] s1_axi_araddr;
    wire [2:0]  s1_axi_arprot;
    wire        s1_axi_arvalid;
    wire        s1_axi_arready;

    wire [31:0] s1_axi_rdata;
    wire [1:0]  s1_axi_rresp;
    wire        s1_axi_rvalid;
    wire        s1_axi_rready;

    wire        mac_irq;
    assign irq = mac_irq;

    (* dont_touch = "true" *)
    riscv_cpu u_cpu (
        .clk            (clk),
        .rst_n          (rst_n),

        .mem_addr       (cpu_mem_addr),
        .mem_write      (cpu_mem_write),
        .mem_wdata      (cpu_mem_wdata),
        .mem_valid      (cpu_mem_valid),
        .mem_ready      (cpu_mem_ready),
        .mem_rdata      (cpu_mem_rdata),

        .mac_start      (),
        .mac_a          (),
        .mac_b          (),
        .mac_c          (),
        .mac_out        (16'b0),
        .mac_fault      (mac_irq),
        .mac_valid      (1'b0),
        .mac_rollback   (1'b0),

        .irq            (mac_irq),

        .reg_write      (reg_write),
        .rd_addr        (rd_addr),
        .rs1_addr       (rs1_addr),
        .rs2_addr       (rs2_addr),
        .alu_out        (alu_out),
        .pc             (pc),
        .mem_read       (mem_read),
        .pc_next        (pc_next)
    );

    cpu_to_axi_master #(
        .C_M_AXI_ADDR_WIDTH (32),
        .C_M_AXI_DATA_WIDTH (32)
    ) u_cpu_axi_master (
        .clk           (clk),
        .rst_n         (rst_n),

        .mem_addr      (cpu_mem_addr),
        .mem_write     (cpu_mem_write),
        .mem_wdata     (cpu_mem_wdata),
        .mem_valid     (cpu_mem_valid),
        .mem_ready     (cpu_mem_ready),
        .mem_rdata     (cpu_mem_rdata),

        .m_axi_awaddr  (m_axi_awaddr),
        .m_axi_awprot  (m_axi_awprot),
        .m_axi_awvalid (m_axi_awvalid),
        .m_axi_awready (m_axi_awready),

        .m_axi_wdata   (m_axi_wdata),
        .m_axi_wstrb   (m_axi_wstrb),
        .m_axi_wvalid  (m_axi_wvalid),
        .m_axi_wready  (m_axi_wready),

        .m_axi_bresp   (m_axi_bresp),
        .m_axi_bvalid  (m_axi_bvalid),
        .m_axi_bready  (m_axi_bready),

        .m_axi_araddr  (m_axi_araddr),
        .m_axi_arprot  (m_axi_arprot),
        .m_axi_arvalid (m_axi_arvalid),
        .m_axi_arready (m_axi_arready),

        .m_axi_rdata   (m_axi_rdata),
        .m_axi_rresp   (m_axi_rresp),
        .m_axi_rvalid  (m_axi_rvalid),
        .m_axi_rready  (m_axi_rready)
    );

    axi_interconnect_1m2s #(
        .C_AXI_ADDR_WIDTH (32),
        .C_AXI_DATA_WIDTH (32)
    ) u_axi_crossbar (
        .aclk          (clk),
        .aresetn       (rst_n),

        // Master Input from CPU Bridge
        .s_axi_awaddr  (m_axi_awaddr),
        .s_axi_awprot  (m_axi_awprot),
        .s_axi_awvalid (m_axi_awvalid),
        .s_axi_awready (m_axi_awready),

        .s_axi_wdata   (m_axi_wdata),
        .s_axi_wstrb   (m_axi_wstrb),
        .s_axi_wvalid  (m_axi_wvalid),
        .s_axi_wready  (m_axi_wready),

        .s_axi_bresp   (m_axi_bresp),
        .s_axi_bvalid  (m_axi_bvalid),
        .s_axi_bready  (m_axi_bready),

        .s_axi_araddr  (m_axi_araddr),
        .s_axi_arprot  (m_axi_arprot),
        .s_axi_arvalid (m_axi_arvalid),
        .s_axi_arready (m_axi_arready),

        .s_axi_rdata   (m_axi_rdata),
        .s_axi_rresp   (m_axi_rresp),
        .s_axi_rvalid  (m_axi_rvalid),
        .s_axi_rready  (m_axi_rready),

        // Slave 0: Data RAM
        .m0_axi_awaddr  (s0_axi_awaddr),
        .m0_axi_awprot  (s0_axi_awprot),
        .m0_axi_awvalid (s0_axi_awvalid),
        .m0_axi_awready (s0_axi_awready),

        .m0_axi_wdata   (s0_axi_wdata),
        .m0_axi_wstrb   (s0_axi_wstrb),
        .m0_axi_wvalid  (s0_axi_wvalid),
        .m0_axi_wready  (s0_axi_wready),

        .m0_axi_bresp   (s0_axi_bresp),
        .m0_axi_bvalid  (s0_axi_bvalid),
        .m0_axi_bready  (s0_axi_bready),

        .m0_axi_araddr  (s0_axi_araddr),
        .m0_axi_arprot  (s0_axi_arprot),
        .m0_axi_arvalid (s0_axi_arvalid),
        .m0_axi_arready (s0_axi_arready),

        .m0_axi_rdata   (s0_axi_rdata),
        .m0_axi_rresp   (s0_axi_rresp),
        .m0_axi_rvalid  (s0_axi_rvalid),
        .m0_axi_rready  (s0_axi_rready),

        // Slave 1: Secure MAC Accelerator
        .m1_axi_awaddr  (s1_axi_awaddr),
        .m1_axi_awprot  (s1_axi_awprot),
        .m1_axi_awvalid (s1_axi_awvalid),
        .m1_axi_awready (s1_axi_awready),

        .m1_axi_wdata   (s1_axi_wdata),
        .m1_axi_wstrb   (s1_axi_wstrb),
        .m1_axi_wvalid  (s1_axi_wvalid),
        .m1_axi_wready  (s1_axi_wready),

        .m1_axi_bresp   (s1_axi_bresp),
        .m1_axi_bvalid  (s1_axi_bvalid),
        .m1_axi_bready  (s1_axi_bready),

        .m1_axi_araddr  (s1_axi_araddr),
        .m1_axi_arprot  (s1_axi_arprot),
        .m1_axi_arvalid (s1_axi_arvalid),
        .m1_axi_arready (s1_axi_arready),

        .m1_axi_rdata   (s1_axi_rdata),
        .m1_axi_rresp   (s1_axi_rresp),
        .m1_axi_rvalid  (s1_axi_rvalid),
        .m1_axi_rready  (s1_axi_rready)
    );

    dmem_axi #(
        .C_S_AXI_DATA_WIDTH (32),
        .C_S_AXI_ADDR_WIDTH (32)
    ) u_dmem_axi (
        .aclk          (clk),
        .aresetn       (rst_n),

        .s_axi_awaddr  (s0_axi_awaddr),
        .s_axi_awprot  (s0_axi_awprot),
        .s_axi_awvalid (s0_axi_awvalid),
        .s_axi_awready (s0_axi_awready),

        .s_axi_wdata   (s0_axi_wdata),
        .s_axi_wstrb   (s0_axi_wstrb),
        .s_axi_wvalid  (s0_axi_wvalid),
        .s_axi_wready  (s0_axi_wready),

        .s_axi_bresp   (s0_axi_bresp),
        .s_axi_bvalid  (s0_axi_bvalid),
        .s_axi_bready  (s0_axi_bready),

        .s_axi_araddr  (s0_axi_araddr),
        .s_axi_arprot  (s0_axi_arprot),
        .s_axi_arvalid (s0_axi_arvalid),
        .s_axi_arready (s0_axi_arready),

        .s_axi_rdata   (s0_axi_rdata),
        .s_axi_rresp   (s0_axi_rresp),
        .s_axi_rvalid  (s0_axi_rvalid),
        .s_axi_rready  (s0_axi_rready)
    );

    (* dont_touch = "true" *)
    secure_mac_axi #(
        .IN_WIDTH            (8),
        .OUT_WIDTH           (16),
        .C_S_AXI_DATA_WIDTH  (32),
        .C_S_AXI_ADDR_WIDTH  (32)
    ) u_secure_mac_axi (
        .aclk          (clk),
        .aresetn       (rst_n),

        .s_axi_awaddr  (s1_axi_awaddr),
        .s_axi_awprot  (s1_axi_awprot),
        .s_axi_awvalid (s1_axi_awvalid),
        .s_axi_awready (s1_axi_awready),

        .s_axi_wdata   (s1_axi_wdata),
        .s_axi_wstrb   (s1_axi_wstrb),
        .s_axi_wvalid  (s1_axi_wvalid),
        .s_axi_wready  (s1_axi_wready),

        .s_axi_bresp   (s1_axi_bresp),
        .s_axi_bvalid  (s1_axi_bvalid),
        .s_axi_bready  (s1_axi_bready),

        .s_axi_araddr  (s1_axi_araddr),
        .s_axi_arprot  (s1_axi_arprot),
        .s_axi_arvalid (s1_axi_arvalid),
        .s_axi_arready (s1_axi_arready),

        .s_axi_rdata   (s1_axi_rdata),
        .s_axi_rresp   (s1_axi_rresp),
        .s_axi_rvalid  (s1_axi_rvalid),
        .s_axi_rready  (s1_axi_rready),

        .irq           (mac_irq)
    );

endmodule
