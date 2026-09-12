`timescale 1ns/1ps

module top_module (
    input  wire        clk,
    input  wire        rst_n,
    output wire        irq
);
    // MMIO & Memory Interface Wires
    wire [31:0] mem_addr;
    wire        mem_write;
    wire [31:0] mem_wdata;
    wire        mem_valid;
    wire        mem_ready = 1'b1;
    wire [31:0] mem_rdata;

    // MAC interface
    wire               mac_start;
    wire signed [7:0]  mac_a;
    wire signed [7:0]  mac_b;
    wire signed [15:0] mac_c;

    // CPU debug signals
    wire        reg_write;
    wire [4:0]  rd_addr;
    wire [4:0]  rs1_addr;
    wire [4:0]  rs2_addr;
    wire [31:0] alu_out;
    wire [31:0] pc;
    wire        mem_read;
    wire [31:0] pc_next;

    // MMIO register pipeline
    (* dont_touch = "true" *) reg signed  [7:0] mac_a_reg, mac_b_reg;
    (* dont_touch = "true" *) reg signed [15:0] mac_c_reg;
    (* dont_touch = "true" *) reg               mac_start_reg;

    reg [31:0] mem_addr_reg;
    reg        mem_write_reg;
    reg [31:0] mem_wdata_reg;
    reg        mem_valid_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mem_addr_reg   <= 0;
            mem_write_reg  <= 0;
            mem_wdata_reg  <= 0;
            mem_valid_reg  <= 0;
        end else begin
            mem_addr_reg   <= mem_addr;
            mem_write_reg  <= mem_write;
            mem_wdata_reg  <= mem_wdata;
            mem_valid_reg  <= mem_valid;
        end
    end

    // Decode MMIO addresses and drive the MAC inputs
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mac_a_reg   <= 0;
            mac_b_reg   <= 0;
            mac_c_reg   <= 0;
            mac_start_reg <= 0;
        end else begin
            // Default: no action
            mac_start_reg <= 0;

            if (mem_write_reg && mem_valid_reg) begin
                case (mem_addr_reg)
                    32'h8000_0000: mac_a_reg <= mem_wdata_reg[7:0];   // A
                    32'h8000_0004: mac_b_reg <= mem_wdata_reg[7:0];   // B
                    32'h8000_0008: mac_c_reg <= mem_wdata_reg[15:0];  // C (16-bit)
                    32'h8000_000C: mac_start_reg <= mem_wdata_reg[0]; // start pulse
                    default:       ;
                endcase
            end
        end
    end

    assign mac_start = mac_start_reg;
    assign mac_a     = mac_a_reg;
    assign mac_b     = mac_b_reg;
    assign mac_c     = mac_c_reg;

    (* dont_touch = "true" *) wire        mac_fault_int;
    (* dont_touch = "true" *) wire        mac_valid_int;
    (* dont_touch = "true" *) wire signed [15:0] mac_out_int;
    (* dont_touch = "true" *) wire        mac_rollback_int;

    (* dont_touch = "true" *)
    secure_mac #(.IN_WIDTH(8), .OUT_WIDTH(16)) u_mac (
        .clk            (clk),
        .rst_n          (rst_n),
        .a              (mac_a),
        .b              (mac_b),
        .c              (mac_c),
        .start          (mac_start_reg),
        .out            (mac_out_int),
        .fault_detected (mac_fault_int),
        .valid          (mac_valid_int),
        .rollback       (mac_rollback_int)
    );

    assign irq = mac_fault_int;
    
    wire [31:0] dmem_rdata;
    dmem u_dmem (
        .clk   (clk),
        .we    (mem_write & mem_valid & (~mem_addr[31])),
        .wstrb (4'b1111),
        .a     (mem_addr),
        .wd    (mem_wdata),
        .rd    (dmem_rdata)
    );

    // Sticky MAC status flags for software polling
    reg mac_done_reg;
    reg mac_fault_sticky;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mac_done_reg     <= 1'b0;
            mac_fault_sticky <= 1'b0;
        end else begin
            if (mac_start_reg) begin
                mac_done_reg     <= 1'b0;
                mac_fault_sticky <= 1'b0;
            end else begin
                if (mac_valid_int) begin
                    mac_done_reg <= 1'b1;
                end
                if (mac_fault_int) begin
                    mac_fault_sticky <= 1'b1;
                end
            end
        end
    end

    // MMIO Read Decoding
    reg [31:0] mmio_rdata;
    always @(*) begin
        case (mem_addr)
            32'h8000_0008: mmio_rdata = {16'b0, mac_out_int};
            32'h8000_0014: mmio_rdata = {30'b0, (mac_done_reg | mac_valid_int), (mac_fault_sticky | mac_fault_int)};
            default:       mmio_rdata = 32'b0;
        endcase
    end
    assign mem_rdata = mem_addr[31] ? mmio_rdata : dmem_rdata;

    (* dont_touch = "true" *)
    riscv_cpu u_cpu (
        .clk            (clk),
        .rst_n          (rst_n),

        .mem_addr       (mem_addr),
        .mem_write      (mem_write),
        .mem_wdata      (mem_wdata),
        .mem_valid      (mem_valid),
        .mem_ready      (mem_ready),
        .mem_rdata      (mem_rdata),

        .mac_start      (),
        .mac_a          (),
        .mac_b          (),
        .mac_c          (),
        .mac_out        (mac_out_int),
        .mac_fault      (mac_fault_int),
        .mac_valid      (mac_valid_int),
        .mac_rollback   (mac_rollback_int),

        .irq            (irq),

        .reg_write      (reg_write),
        .rd_addr        (rd_addr),
        .rs1_addr       (rs1_addr),
        .rs2_addr       (rs2_addr),
        .alu_out        (alu_out),
        .pc             (pc),
        .mem_read       (mem_read),
        .pc_next        (pc_next)
    );

endmodule