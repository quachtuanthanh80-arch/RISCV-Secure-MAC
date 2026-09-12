`timescale 1ns/1ps

module secure_mac_axi #(
    parameter integer IN_WIDTH             = 8,
    parameter integer OUT_WIDTH            = 16,
    parameter integer C_S_AXI_DATA_WIDTH   = 32,
    parameter integer C_S_AXI_ADDR_WIDTH   = 32
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
    input  wire                                 s_axi_rready,

    output wire                                 irq
);

    localparam [5:0] ADDR_MAC_A      = 6'h00; // Toán hạng A (signed 8-bit)
    localparam [5:0] ADDR_MAC_B      = 6'h04; // Toán hạng B (signed 8-bit)
    localparam [5:0] ADDR_MAC_C      = 6'h08; // Ghi: toán hạng C, Đọc: kết quả MAC
    localparam [5:0] ADDR_MAC_CTRL   = 6'h0C; // Bit 0: START pulse (tự động xóa sau 1 chu kỳ)
    localparam [5:0] ADDR_MAC_OUT    = 6'h10; // Kết quả MAC sau rollback
    localparam [5:0] ADDR_MAC_STATUS = 6'h14; // Bit 0: fault, Bit 1: valid, Bit 2: rollback
    localparam [5:0] ADDR_MAC_CONFIG = 6'h18; // Ngưỡng dị thường động ANOMALY_THRESHOLD

    localparam [1:0] AXI_RESP_OKAY   = 2'b00;
    localparam [1:0] AXI_RESP_SLVERR = 2'b10;

    // Write Protection: Read-only registers (OUT, STATUS) bị từ chối ghi (SLVERR)
    wire wr_addr_valid = (s_axi_awaddr[1:0] == 2'b00) && 
                         (s_axi_awaddr[5:0] == ADDR_MAC_A ||
                          s_axi_awaddr[5:0] == ADDR_MAC_B ||
                          s_axi_awaddr[5:0] == ADDR_MAC_C ||
                          s_axi_awaddr[5:0] == ADDR_MAC_CTRL ||
                          s_axi_awaddr[5:0] == ADDR_MAC_CONFIG);

    wire rd_addr_valid = (s_axi_araddr[1:0] == 2'b00) && (s_axi_araddr[5:0] <= ADDR_MAC_CONFIG);

    // Chốt phản hồi AXI để giữ valid/resp khi master chưa kích hoạt ready
    reg axi_bvalid_reg;
    reg [1:0] axi_bresp_reg;
    reg axi_rvalid_reg;
    reg [1:0] axi_rresp_reg;
    reg [C_S_AXI_DATA_WIDTH-1:0] axi_rdata_reg;
    reg [C_S_AXI_DATA_WIDTH-1:0] reg_data_out;

    wire write_handshake = s_axi_awvalid && s_axi_wvalid;
    wire read_handshake  = s_axi_arvalid;

    assign s_axi_awready = 1'b1;
    assign s_axi_wready  = 1'b1;
    assign s_axi_arready = 1'b1;

    assign s_axi_bvalid = write_handshake | axi_bvalid_reg;
    assign s_axi_bresp  = axi_bvalid_reg ? axi_bresp_reg : (wr_addr_valid ? AXI_RESP_OKAY : AXI_RESP_SLVERR);

    assign s_axi_rvalid = read_handshake | axi_rvalid_reg;
    assign s_axi_rresp  = axi_rvalid_reg ? axi_rresp_reg : (rd_addr_valid ? AXI_RESP_OKAY : AXI_RESP_SLVERR);
    assign s_axi_rdata  = axi_rvalid_reg ? axi_rdata_reg : reg_data_out;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            axi_bvalid_reg <= 1'b0;
            axi_bresp_reg  <= AXI_RESP_OKAY;
            axi_rvalid_reg <= 1'b0;
            axi_rresp_reg  <= AXI_RESP_OKAY;
            axi_rdata_reg  <= {C_S_AXI_DATA_WIDTH{1'b0}};
        end else begin
            // Hold bvalid until bready arrives if master did not accept in same cycle
            if (write_handshake && !s_axi_bready) begin
                axi_bvalid_reg <= 1'b1;
                axi_bresp_reg  <= wr_addr_valid ? AXI_RESP_OKAY : AXI_RESP_SLVERR;
            end else if (s_axi_bready) begin
                axi_bvalid_reg <= 1'b0;
            end

            // Hold rvalid and sampled data until rready arrives if master did not accept in same cycle
            if (read_handshake && !s_axi_rready) begin
                axi_rvalid_reg <= 1'b1;
                axi_rresp_reg  <= rd_addr_valid ? AXI_RESP_OKAY : AXI_RESP_SLVERR;
                axi_rdata_reg  <= reg_data_out;
            end else if (s_axi_rready) begin
                axi_rvalid_reg <= 1'b0;
            end
        end
    end

    reg signed [IN_WIDTH-1:0]          reg_mac_a;
    reg signed [IN_WIDTH-1:0]          reg_mac_b;
    reg signed [OUT_WIDTH-1:0]         reg_mac_c;
    reg                                reg_mac_start;
    reg signed [OUT_WIDTH-1:0]         reg_anomaly_threshold;

    // Sticky status registers
    reg                                status_done_sticky;
    reg                                status_fault_sticky;
    reg                                status_rollback_sticky;

    // MAC Core Signals
    wire signed [OUT_WIDTH-1:0]        mac_core_out;
    wire                               mac_core_fault;
    wire                               mac_core_valid;
    wire                               mac_core_rollback;

    wire slv_reg_wren = s_axi_awvalid && s_axi_wvalid && s_axi_awready && s_axi_wready;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            reg_mac_a             <= {IN_WIDTH{1'b0}};
            reg_mac_b             <= {IN_WIDTH{1'b0}};
            reg_mac_c             <= {OUT_WIDTH{1'b0}};
            reg_mac_start         <= 1'b0;
            reg_anomaly_threshold <= {1'b0, {(OUT_WIDTH-2){1'b1}}, 1'b0};
        end else begin
            // Start pulse is active for exactly 1 clock cycle
            reg_mac_start <= 1'b0;

            if (slv_reg_wren && wr_addr_valid) begin
                case (s_axi_awaddr[5:0])
                    ADDR_MAC_A: begin
                        if (s_axi_wstrb[0]) reg_mac_a <= s_axi_wdata[IN_WIDTH-1:0];
                    end
                    ADDR_MAC_B: begin
                        if (s_axi_wstrb[0]) reg_mac_b <= s_axi_wdata[IN_WIDTH-1:0];
                    end
                    ADDR_MAC_C: begin
                        if (s_axi_wstrb[0]) reg_mac_c[7:0] <= s_axi_wdata[7:0];
                        if (OUT_WIDTH > 8) begin
                            if (s_axi_wstrb[1]) reg_mac_c[OUT_WIDTH-1:8] <= s_axi_wdata[OUT_WIDTH-1:8];
                        end
                    end
                    ADDR_MAC_CTRL: begin
                        if (s_axi_wstrb[0]) reg_mac_start <= s_axi_wdata[0];
                    end
                    ADDR_MAC_CONFIG: begin
                        if (s_axi_wstrb[0]) reg_anomaly_threshold[7:0] <= s_axi_wdata[7:0];
                        if (OUT_WIDTH > 8) begin
                            if (s_axi_wstrb[1]) reg_anomaly_threshold[OUT_WIDTH-1:8] <= s_axi_wdata[OUT_WIDTH-1:8];
                        end
                    end
                    default: ;
                endcase
            end
        end
    end

    wire [C_S_AXI_DATA_WIDTH-1:0] status_word = {
        {(C_S_AXI_DATA_WIDTH-3){1'b0}},
        (status_rollback_sticky | mac_core_rollback),
        (status_done_sticky     | mac_core_valid),
        (status_fault_sticky    | mac_core_fault)
    };

    always @(*) begin
        case (s_axi_araddr[5:0])
            ADDR_MAC_A:      reg_data_out = {{(C_S_AXI_DATA_WIDTH-IN_WIDTH){reg_mac_a[IN_WIDTH-1]}}, reg_mac_a};
            ADDR_MAC_B:      reg_data_out = {{(C_S_AXI_DATA_WIDTH-IN_WIDTH){reg_mac_b[IN_WIDTH-1]}}, reg_mac_b};
            ADDR_MAC_C:      reg_data_out = status_done_sticky ? 
                                            {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){mac_core_out[OUT_WIDTH-1]}}, mac_core_out} :
                                            {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){reg_mac_c[OUT_WIDTH-1]}}, reg_mac_c};
            ADDR_MAC_CTRL:   reg_data_out = {{(C_S_AXI_DATA_WIDTH-1){1'b0}}, reg_mac_start};
            ADDR_MAC_OUT:    reg_data_out = {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){mac_core_out[OUT_WIDTH-1]}}, mac_core_out};
            ADDR_MAC_STATUS: reg_data_out = status_word;
            ADDR_MAC_CONFIG: reg_data_out = {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){reg_anomaly_threshold[OUT_WIDTH-1]}}, reg_anomaly_threshold};
            default:         reg_data_out = {C_S_AXI_DATA_WIDTH{1'b0}};
        endcase
    end

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            status_done_sticky     <= 1'b0;
            status_fault_sticky    <= 1'b0;
            status_rollback_sticky <= 1'b0;
        end else begin
            if (reg_mac_start) begin
                status_done_sticky     <= 1'b0;
                status_fault_sticky    <= 1'b0;
                status_rollback_sticky <= 1'b0;
            end else begin
                if (mac_core_valid)    status_done_sticky     <= 1'b1;
                if (mac_core_fault)    status_fault_sticky    <= 1'b1;
                if (mac_core_rollback) status_rollback_sticky <= 1'b1;
            end
        end
    end

    assign irq = mac_core_fault | status_fault_sticky;

    secure_mac #(
        .IN_WIDTH          (IN_WIDTH),
        .OUT_WIDTH         (OUT_WIDTH)
    ) u_secure_mac_core (
        .clk               (aclk),
        .rst_n             (aresetn),
        .test_mode         (1'b0),
        .a                 (reg_mac_a),
        .b                 (reg_mac_b),
        .c                 (reg_mac_c),
        .start             (reg_mac_start),
        .context_reset     (1'b0),
        .alpha_sel         (1'b1),
        .out               (mac_core_out),
        .fault_detected    (mac_core_fault),
        .valid             (mac_core_valid),
        .rollback          (mac_core_rollback)
    );

`ifndef SYNTHESIS
    secure_mac_axi_sva u_axi_sva (
        .aclk          (aclk),
        .aresetn       (aresetn),
        .s_axi_awvalid (s_axi_awvalid),
        .s_axi_awready (s_axi_awready),
        .s_axi_wvalid  (s_axi_wvalid),
        .s_axi_wready  (s_axi_wready),
        .s_axi_bvalid  (s_axi_bvalid),
        .s_axi_bready  (s_axi_bready),
        .s_axi_bresp   (s_axi_bresp),
        .s_axi_arvalid (s_axi_arvalid),
        .s_axi_arready (s_axi_arready),
        .s_axi_rvalid  (s_axi_rvalid),
        .s_axi_rready  (s_axi_rready),
        .s_axi_rresp   (s_axi_rresp)
    );
`endif

endmodule
