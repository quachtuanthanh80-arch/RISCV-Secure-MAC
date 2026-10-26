`timescale 1ns / 1ps

module secure_mac_axi #(
    parameter integer IN_WIDTH             = 8,
    parameter integer OUT_WIDTH            = 16,
    parameter integer C_S_AXI_DATA_WIDTH   = 32,
    parameter integer C_S_AXI_ADDR_WIDTH   = 32,
    parameter integer USE_ADAPTIVE_THRESHOLD = 0
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

    output wire                                 irq,
    output wire                                 mac_valid_out,
    output wire                                 mac_rollback_out,
    output wire signed [OUT_WIDTH-1:0]          mac_data_out
);

    localparam [5:0] ADDR_MAC_A         = 6'h00; // Toan hang A (signed 8-bit)
    localparam [5:0] ADDR_MAC_B         = 6'h04; // Toan hang B (signed 8-bit)
    localparam [5:0] ADDR_MAC_C         = 6'h08; // Ghi: toan hang C, Doc: ket qua MAC
    localparam [5:0] ADDR_MAC_CTRL      = 6'h0C; // Bit 0: START, 1: CTX_RST, 2: ALPHA_SEL, 3: TEST_MODE, 4: FLT_CLR, 5: CNT_RST
    localparam [5:0] ADDR_MAC_OUT       = 6'h10; // Ket qua MAC sau rollback
    localparam [5:0] ADDR_MAC_STATUS    = 6'h14; // Bit 0: fault, Bit 1: valid, Bit 2: rollback (W1C bit 0 clears fault)
    localparam [5:0] ADDR_MAC_CONFIG    = 6'h18; // Nguong di thuong dong ANOMALY_THRESHOLD
    localparam [5:0] ADDR_MAC_INTR_EN   = 6'h1C; // Mat na ngat: Bit 0: Fault IRQ En, Bit 1: Done IRQ En
    localparam [5:0] ADDR_MAC_FAULT_CNT = 6'h20; // Bo dem loi: [31:16]=Rollback Cnt, [15:0]=Fault Cnt
    localparam [5:0] ADDR_MAC_EWMA_STAT = 6'h24; // Giam sat EWMA truc tuyen: [31:16]=Mean, [15:0]=MAD
    localparam [5:0] ADDR_MAC_OP_CNT    = 6'h28; // Tong so phep tinh MAC thanh cong

    localparam [1:0] AXI_RESP_OKAY   = 2'b00;
    localparam [1:0] AXI_RESP_SLVERR = 2'b10;

    // Write Protection: Read-only registers (OUT, FAULT_CNT, EWMA_STAT, OP_CNT) bi tu choi ghi (SLVERR)
    wire wr_addr_valid = (s_axi_awaddr[1:0] == 2'b00) && 
                         (s_axi_awaddr[5:0] == ADDR_MAC_A ||
                          s_axi_awaddr[5:0] == ADDR_MAC_B ||
                          s_axi_awaddr[5:0] == ADDR_MAC_C ||
                          s_axi_awaddr[5:0] == ADDR_MAC_CTRL ||
                          s_axi_awaddr[5:0] == ADDR_MAC_STATUS ||
                          s_axi_awaddr[5:0] == ADDR_MAC_CONFIG ||
                          s_axi_awaddr[5:0] == ADDR_MAC_INTR_EN);

    wire rd_addr_valid = (s_axi_araddr[1:0] == 2'b00) && (s_axi_araddr[5:0] <= ADDR_MAC_OP_CNT);

    // Chot phan hoi AXI de giu valid/resp khi master chua kich hoat ready
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
    reg                                reg_context_reset;
    reg                                reg_alpha_sel;
    reg                                reg_test_mode;
    reg                                reg_fault_clr;
    reg                                reg_cnt_rst;
    reg signed [OUT_WIDTH-1:0]         reg_anomaly_threshold;
    reg [1:0]                          reg_intr_en;

    // Hardware Telemetry Event Counters
    reg [15:0]                         fault_event_cnt;
    reg [15:0]                         rollback_event_cnt;
    reg [31:0]                         op_success_cnt;

    // Sticky status registers
    reg                                status_done_sticky;
    reg                                status_fault_sticky;
    reg                                status_rollback_sticky;

    // MAC Core Signals
    wire signed [OUT_WIDTH-1:0]        mac_core_out;
    wire                               mac_core_fault;
    wire                               mac_core_valid;
    wire                               mac_core_rollback;
    wire signed [OUT_WIDTH-1:0]        mac_ewma_mean;
    wire signed [OUT_WIDTH-1:0]        mac_ewma_mad;
    wire signed [OUT_WIDTH-1:0]        mac_active_threshold;

    wire slv_reg_wren = s_axi_awvalid && s_axi_wvalid && s_axi_awready && s_axi_wready;

    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            reg_mac_a             <= {IN_WIDTH{1'b0}};
            reg_mac_b             <= {IN_WIDTH{1'b0}};
            reg_mac_c             <= {OUT_WIDTH{1'b0}};
            reg_mac_start         <= 1'b0;
            reg_context_reset     <= 1'b0;
            reg_alpha_sel         <= 1'b1;
            reg_test_mode         <= 1'b0;
            reg_fault_clr         <= 1'b0;
            reg_cnt_rst           <= 1'b0;
            reg_anomaly_threshold <= {1'b0, {(OUT_WIDTH-2){1'b1}}, 1'b0};
            reg_intr_en           <= 2'b01; // Default: Fault IRQ enabled, Done IRQ disabled
            fault_event_cnt       <= 16'd0;
            rollback_event_cnt    <= 16'd0;
            op_success_cnt        <= 32'd0;
        end else begin
            // Self-clearing pulses
            reg_mac_start     <= 1'b0;
            reg_context_reset <= 1'b0;
            reg_fault_clr     <= 1'b0;
            reg_cnt_rst       <= 1'b0;

            // Telemetry Counters
            if (reg_cnt_rst) begin
                fault_event_cnt    <= 16'd0;
                rollback_event_cnt <= 16'd0;
                op_success_cnt     <= 32'd0;
            end else begin
                if (mac_core_fault && (fault_event_cnt != 16'hFFFF))
                    fault_event_cnt <= fault_event_cnt + 1'b1;
                if (mac_core_rollback && (rollback_event_cnt != 16'hFFFF))
                    rollback_event_cnt <= rollback_event_cnt + 1'b1;
                if (mac_core_valid && (op_success_cnt != 32'hFFFFFFFF))
                    op_success_cnt <= op_success_cnt + 1'b1;
            end

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
                        if (s_axi_wstrb[0]) begin
                            reg_mac_start     <= s_axi_wdata[0];
                            reg_context_reset <= s_axi_wdata[1];
                            reg_alpha_sel     <= s_axi_wdata[2];
                            reg_test_mode     <= s_axi_wdata[3];
                            reg_fault_clr     <= s_axi_wdata[4];
                            reg_cnt_rst       <= s_axi_wdata[5];
                        end
                    end
                    ADDR_MAC_STATUS: begin
                        // W1C: writing 1 to bit 0 clears fault and rollback sticky flags
                        if (s_axi_wstrb[0] && s_axi_wdata[0]) begin
                            reg_fault_clr <= 1'b1;
                        end
                    end
                    ADDR_MAC_CONFIG: begin
                        if (s_axi_wstrb[0]) reg_anomaly_threshold[7:0] <= s_axi_wdata[7:0];
                        if (OUT_WIDTH > 8) begin
                            if (s_axi_wstrb[1]) reg_anomaly_threshold[OUT_WIDTH-1:8] <= s_axi_wdata[OUT_WIDTH-1:8];
                        end
                    end
                    ADDR_MAC_INTR_EN: begin
                        if (s_axi_wstrb[0]) reg_intr_en <= s_axi_wdata[1:0];
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
            ADDR_MAC_A:         reg_data_out = {{(C_S_AXI_DATA_WIDTH-IN_WIDTH){reg_mac_a[IN_WIDTH-1]}}, reg_mac_a};
            ADDR_MAC_B:         reg_data_out = {{(C_S_AXI_DATA_WIDTH-IN_WIDTH){reg_mac_b[IN_WIDTH-1]}}, reg_mac_b};
            ADDR_MAC_C:         reg_data_out = status_done_sticky ? 
                                                {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){mac_core_out[OUT_WIDTH-1]}}, mac_core_out} :
                                                {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){reg_mac_c[OUT_WIDTH-1]}}, reg_mac_c};
            ADDR_MAC_CTRL:      reg_data_out = {{(C_S_AXI_DATA_WIDTH-4){1'b0}}, reg_test_mode, reg_alpha_sel, reg_context_reset, reg_mac_start};
            ADDR_MAC_OUT:       reg_data_out = {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){mac_core_out[OUT_WIDTH-1]}}, mac_core_out};
            ADDR_MAC_STATUS:    reg_data_out = status_word;
            ADDR_MAC_CONFIG:    reg_data_out = {{(C_S_AXI_DATA_WIDTH-OUT_WIDTH){reg_anomaly_threshold[OUT_WIDTH-1]}}, reg_anomaly_threshold};
            ADDR_MAC_INTR_EN:   reg_data_out = {{(C_S_AXI_DATA_WIDTH-2){1'b0}}, reg_intr_en};
            ADDR_MAC_FAULT_CNT: reg_data_out = {rollback_event_cnt, fault_event_cnt};
            ADDR_MAC_EWMA_STAT: reg_data_out = {mac_ewma_mean[15:0], mac_ewma_mad[15:0]};
            ADDR_MAC_OP_CNT:    reg_data_out = op_success_cnt;
            default:            reg_data_out = {C_S_AXI_DATA_WIDTH{1'b0}};
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
            end else if (reg_fault_clr) begin
                status_fault_sticky    <= 1'b0;
                status_rollback_sticky <= 1'b0;
            end else begin
                if (mac_core_valid)    status_done_sticky     <= 1'b1;
                if (mac_core_fault)    status_fault_sticky    <= 1'b1;
                if (mac_core_rollback) status_rollback_sticky <= 1'b1;
            end
        end
    end

    wire fault_irq = (mac_core_fault | status_fault_sticky) & reg_intr_en[0];
    wire done_irq  = (mac_core_valid | status_done_sticky)  & reg_intr_en[1];
    assign irq = fault_irq | done_irq;

    assign mac_valid_out    = mac_core_valid;
    assign mac_rollback_out = mac_core_rollback;
    assign mac_data_out     = mac_core_out;

    secure_mac #(
        .IN_WIDTH               (IN_WIDTH),
        .OUT_WIDTH              (OUT_WIDTH),
        .USE_ADAPTIVE_THRESHOLD (USE_ADAPTIVE_THRESHOLD)
    ) u_secure_mac_core (
        .clk                    (aclk),
        .rst_n                  (aresetn),
        .test_mode              (reg_test_mode),
        .a                      (reg_mac_a),
        .b                      (reg_mac_b),
        .c                      (reg_mac_c),
        .start                  (reg_mac_start),
        .context_reset          (reg_context_reset),
        .alpha_sel              (reg_alpha_sel),
        .cfg_anomaly_threshold  (reg_anomaly_threshold),
        .out                    (mac_core_out),
        .fault_detected         (mac_core_fault),
        .valid                  (mac_core_valid),
        .rollback               (mac_core_rollback),
        .ewma_mean_out          (mac_ewma_mean),
        .ewma_mad_out           (mac_ewma_mad),
        .active_threshold_out   (mac_active_threshold)
    );

`ifndef SYNTHESIS
    secure_mac_axi_sva #(
        .C_S_AXI_ADDR_WIDTH (C_S_AXI_ADDR_WIDTH),
        .C_S_AXI_DATA_WIDTH (C_S_AXI_DATA_WIDTH)
    ) u_axi_sva (
        .aclk          (aclk),
        .aresetn       (aresetn),
        .s_axi_awaddr  (s_axi_awaddr),
        .s_axi_awprot  (s_axi_awprot),
        .s_axi_awvalid (s_axi_awvalid),
        .s_axi_awready (s_axi_awready),
        .s_axi_wdata   (s_axi_wdata),
        .s_axi_wstrb   (s_axi_wstrb),
        .s_axi_wvalid  (s_axi_wvalid),
        .s_axi_wready  (s_axi_wready),
        .s_axi_bresp   (s_axi_bresp),
        .s_axi_bvalid  (s_axi_bvalid),
        .s_axi_bready  (s_axi_bready),
        .s_axi_araddr  (s_axi_araddr),
        .s_axi_arprot  (s_axi_arprot),
        .s_axi_arvalid (s_axi_arvalid),
        .s_axi_arready (s_axi_arready),
        .s_axi_rdata   (s_axi_rdata),
        .s_axi_rresp   (s_axi_rresp),
        .s_axi_rvalid  (s_axi_rvalid),
        .s_axi_rready  (s_axi_rready)
    );
`endif

endmodule
