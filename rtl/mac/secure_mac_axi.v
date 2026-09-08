`timescale 1ns/1ps
//=============================================================================
// secure_mac_axi.v – ARM AMBA AXI4-Lite Slave Wrapper for Secure MAC IP
//
// Compliant with ARM AXI4-Lite Specification (IHI 0022E).
// Standard 5-channel AXI4-Lite Slave interface:
//   - Write Address Channel (AW)
//   - Write Data Channel (W)
//   - Write Response Channel (B)
//   - Read Address Channel (AR)
//   - Read Data Channel (R)
//
// Register Map (Base: 0x8000_0000, 32-bit aligned):
//   Offset 0x00: REG_MAC_A      [R/W] [7:0]  Toán hạng A (signed 8-bit)
//   Offset 0x04: REG_MAC_B      [R/W] [7:0]  Toán hạng B (signed 8-bit)
//   Offset 0x08: REG_MAC_C/OUT  [R/W] Ghi: C (tích lũy), Đọc: Kết quả MAC
//   Offset 0x0C: REG_MAC_CTRL   [W]   Bit 0: START pulse (tự động xóa sau 1 chu kỳ)
//   Offset 0x10: REG_MAC_OUT    [R]   [OUT_WIDTH-1:0] Kết quả MAC (sau rollback nếu lỗi)
//   Offset 0x14: REG_MAC_STATUS [R]   Bit 0: fault_detected (kết hợp sticky)
//                                     Bit 1: valid / done (kết hợp sticky)
//                                     Bit 2: rollback
//   Offset 0x18: REG_MAC_CONFIG [R/W] Ngưỡng dị thường ANOMALY_THRESHOLD động
//
// Interrupt:
//   irq: Kích hoạt khi phát hiện lỗi (fault_detected) hoặc hoàn thành phép tính
//=============================================================================

module secure_mac_axi #(
    parameter integer IN_WIDTH             = 8,
    parameter integer OUT_WIDTH            = 16,
    parameter integer C_S_AXI_DATA_WIDTH   = 32,
    parameter integer C_S_AXI_ADDR_WIDTH   = 32
)(
    // AXI4-Lite Clock and Active-Low Reset
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
    input  wire                                 s_axi_rready,

    // External Fault Interrupt
    output wire                                 irq
);

    //-------------------------------------------------------------------------
    // Local Parameters for Register Offsets
    //-------------------------------------------------------------------------
    localparam [5:0] ADDR_MAC_A      = 6'h00; // 0x00
    localparam [5:0] ADDR_MAC_B      = 6'h04; // 0x04
    localparam [5:0] ADDR_MAC_C      = 6'h08; // 0x08
    localparam [5:0] ADDR_MAC_CTRL   = 6'h0C; // 0x0C
    localparam [5:0] ADDR_MAC_OUT    = 6'h10; // 0x10
    localparam [5:0] ADDR_MAC_STATUS = 6'h14; // 0x14
    localparam [5:0] ADDR_MAC_CONFIG = 6'h18; // 0x18

    localparam [1:0] AXI_RESP_OKAY   = 2'b00;
    localparam [1:0] AXI_RESP_SLVERR = 2'b10;

    // Address Alignment and Range Validation (ARM AXI4-Lite Standard)
    wire wr_addr_valid = (s_axi_awaddr[1:0] == 2'b00) && 
                         (s_axi_awaddr[5:0] == ADDR_MAC_A ||
                          s_axi_awaddr[5:0] == ADDR_MAC_B ||
                          s_axi_awaddr[5:0] == ADDR_MAC_C ||
                          s_axi_awaddr[5:0] == ADDR_MAC_CTRL ||
                          s_axi_awaddr[5:0] == ADDR_MAC_CONFIG);

    wire rd_addr_valid = (s_axi_araddr[1:0] == 2'b00) && (s_axi_araddr[5:0] <= ADDR_MAC_CONFIG);

    // Immediate handshake lines
    assign s_axi_awready = 1'b1;
    assign s_axi_wready  = 1'b1;
    assign s_axi_bvalid  = s_axi_awvalid & s_axi_wvalid;
    assign s_axi_bresp   = wr_addr_valid ? AXI_RESP_OKAY : AXI_RESP_SLVERR;

    assign s_axi_arready = 1'b1;
    assign s_axi_rvalid  = s_axi_arvalid;
    assign s_axi_rresp   = rd_addr_valid ? AXI_RESP_OKAY : AXI_RESP_SLVERR;

    //-------------------------------------------------------------------------
    // Internal Registers for MAC Operands & Control
    //-------------------------------------------------------------------------
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

    // Register Write Execution
    wire slv_reg_wren = s_axi_awvalid & s_axi_wvalid;

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
                        if (s_axi_wstrb[0]) reg_mac_c[7:0]            <= s_axi_wdata[7:0];
                        if (s_axi_wstrb[1]) reg_mac_c[OUT_WIDTH-1:8]  <= s_axi_wdata[OUT_WIDTH-1:8];
                    end
                    ADDR_MAC_CTRL: begin
                        if (s_axi_wstrb[0]) reg_mac_start <= s_axi_wdata[0];
                    end
                    ADDR_MAC_CONFIG: begin
                        if (s_axi_wstrb[0]) reg_anomaly_threshold[7:0]           <= s_axi_wdata[7:0];
                        if (s_axi_wstrb[1]) reg_anomaly_threshold[OUT_WIDTH-1:8] <= s_axi_wdata[OUT_WIDTH-1:8];
                    end
                    default: ;
                endcase
            end
        end
    end

    //-------------------------------------------------------------------------
    // Read Data Multiplexer
    //-------------------------------------------------------------------------
    reg [C_S_AXI_DATA_WIDTH-1:0] reg_data_out;

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

    assign s_axi_rdata = reg_data_out;

    //-------------------------------------------------------------------------
    // Sticky Status Management & Interrupt Generation
    //-------------------------------------------------------------------------
    always @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            status_done_sticky     <= 1'b0;
            status_fault_sticky    <= 1'b0;
            status_rollback_sticky <= 1'b0;
        end else begin
            if (reg_mac_start) begin
                // Reset status when new computation starts
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

    // Interrupt line triggers on fault
    assign irq = mac_core_fault | status_fault_sticky;

    //-------------------------------------------------------------------------
    // Instantiate Verified Secure MAC Core
    //-------------------------------------------------------------------------
    secure_mac #(
        .IN_WIDTH          (IN_WIDTH),
        .OUT_WIDTH         (OUT_WIDTH)
    ) u_secure_mac_core (
        .clk               (aclk),
        .rst_n             (aresetn),
        .a                 (reg_mac_a),
        .b                 (reg_mac_b),
        .c                 (reg_mac_c),
        .start             (reg_mac_start),
        .out               (mac_core_out),
        .fault_detected    (mac_core_fault),
        .valid             (mac_core_valid),
        .rollback          (mac_core_rollback)
    );

endmodule
