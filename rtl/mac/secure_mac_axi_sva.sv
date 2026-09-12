`timescale 1ns/1ps

module secure_mac_axi_sva (
    input logic        aclk,
    input logic        aresetn,
    input logic        s_axi_awvalid,
    input logic        s_axi_awready,
    input logic        s_axi_wvalid,
    input logic        s_axi_wready,
    input logic        s_axi_bvalid,
    input logic        s_axi_bready,
    input logic [1:0]  s_axi_bresp,
    input logic        s_axi_arvalid,
    input logic        s_axi_arready,
    input logic        s_axi_rvalid,
    input logic        s_axi_rready,
    input logic [1:0]  s_axi_rresp
);

    always @(negedge aresetn) begin
        #1;
        assert (s_axi_bvalid == 1'b0)
            else $error("[SVA-AXI FAIL] bvalid asserted during reset!");
        assert (s_axi_rvalid == 1'b0)
            else $error("[SVA-AXI FAIL] rvalid asserted during reset!");
    end

    // Protocol check: response codes must be OKAY (2'b00) or SLVERR (2'b10)
    always @(posedge aclk) begin
        if (aresetn && s_axi_bvalid) begin
            assert (s_axi_bresp == 2'b00 || s_axi_bresp == 2'b10)
                else $error("[SVA-AXI FAIL] Invalid bresp code: %b", s_axi_bresp);
        end
        if (aresetn && s_axi_rvalid) begin
            assert (s_axi_rresp == 2'b00 || s_axi_rresp == 2'b10)
                else $error("[SVA-AXI FAIL] Invalid rresp code: %b", s_axi_rresp);
        end
    end

endmodule
