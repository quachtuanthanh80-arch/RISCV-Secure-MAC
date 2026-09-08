`timescale 1ns/1ps
// =============================================================================
// RESO_MAC – Time-Redundancy MAC (Recomputing with Shifted Operands)
// =============================================================================
// Architecture:
//   - Single hardware MAC datapath executing two time-multiplexed phases:
//       Phase 1 (Direct Calculation):
//           R1 = A * B + C
//       Phase 2 (Shifted Operand Recomputation):
//           A_shift = A << 1
//           C_shift = C << 1
//           R2_raw  = (A_shift * B) + C_shift = 2 * (A * B + C)
//           R2      = R2_raw >>> 1
//   - Temporal Comparator: Verifies that R1 == R2.
//       If a transient fault (SEU / single-cycle glitch) hit during either phase,
//       R1 != R2, asserting fault_detected.
//   - Trade-off: Saves hardware area (1 MAC core) at the cost of 50% throughput
//     (requires 2 compute rounds per MAC operation).
// =============================================================================

module reso_mac #(
    parameter IN_WIDTH  = 8,
    parameter OUT_WIDTH = 32
)(
    input  wire                         clk,
    input  wire                         rst_n,
    input  wire signed [IN_WIDTH-1:0]   a,
    input  wire signed [IN_WIDTH-1:0]   b,
    input  wire signed [OUT_WIDTH-1:0]  c,
    input  wire                         start,
    output reg  signed [OUT_WIDTH-1:0]  out,
    output reg                          valid,
    output reg                          fault_detected
);

    // =========================================================================
    // FSM State Machine for 2-Phase Time-Redundancy Execution
    // =========================================================================
    localparam S_IDLE     = 2'd0;
    localparam S_PHASE1   = 2'd1; // Direct computation
    localparam S_PHASE2   = 2'd2; // Shifted recomputation
    localparam S_COMPARE  = 2'd3; // Compare R1 and R2

    reg [1:0] state;

    reg signed [IN_WIDTH:0]    op_a;     // 1 extra bit for left shift
    reg signed [IN_WIDTH-1:0]  op_b;
    reg signed [OUT_WIDTH:0]   op_c;     // 1 extra bit for left shift
    reg signed [IN_WIDTH-1:0]  saved_a, saved_b;
    reg signed [OUT_WIDTH-1:0] saved_c;

    reg signed [OUT_WIDTH-1:0] res_phase1;
    reg signed [OUT_WIDTH:0]   res_phase2_raw;

    // Shared multiplier & adder
    wire signed [2*IN_WIDTH:0]  shared_product = op_a * $signed({op_b[IN_WIDTH-1], op_b});
    wire signed [OUT_WIDTH+1:0] shared_prod_ext = {{ (OUT_WIDTH+1 - 2*IN_WIDTH){shared_product[2*IN_WIDTH]} }, shared_product};
    wire signed [OUT_WIDTH+1:0] shared_mac      = shared_prod_ext + op_c;
    wire signed [OUT_WIDTH-1:0] res_phase2_norm = $signed(res_phase2_raw[OUT_WIDTH:1]);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state          <= S_IDLE;
            op_a           <= '0;
            op_b           <= '0;
            op_c           <= '0;
            saved_a        <= '0;
            saved_b        <= '0;
            saved_c        <= '0;
            res_phase1     <= '0;
            res_phase2_raw <= '0;
            out            <= '0;
            valid          <= 1'b0;
            fault_detected <= 1'b0;
        end else begin
            case (state)
                S_IDLE: begin
                    valid          <= 1'b0;
                    fault_detected <= 1'b0;
                    if (start) begin
                        // Latch original operands and prepare Phase 1
                        saved_a <= a;
                        saved_b <= b;
                        saved_c <= c;
                        op_a    <= $signed({a[IN_WIDTH-1], a}); // Sign-extended normal
                        op_b    <= b;
                        op_c    <= $signed({c[OUT_WIDTH-1], c});
                        state   <= S_PHASE1;
                    end
                end

                S_PHASE1: begin
                    // Store normal result R1
                    res_phase1 <= shared_mac[OUT_WIDTH-1:0];
                    // Setup Phase 2: Shifted operands (A << 1, C << 1)
                    op_a       <= $signed({saved_a, 1'b0});
                    op_b       <= saved_b;
                    op_c       <= $signed({saved_c, 1'b0});
                    state      <= S_PHASE2;
                end

                S_PHASE2: begin
                    // Store raw shifted result R2_raw
                    res_phase2_raw <= shared_mac[OUT_WIDTH:0];
                    state          <= S_COMPARE;
                end

                S_COMPARE: begin
                    // Normalize Phase 2 result (arithmetic right shift by 1)
                    // and compare against Phase 1
                    if (res_phase1 == res_phase2_norm) begin
                        out            <= res_phase1;
                        fault_detected <= 1'b0;
                        valid          <= 1'b1;
                    end else begin
                        out            <= res_phase1;
                        fault_detected <= 1'b1; // Temporal discrepancy detected!
                        valid          <= 1'b0;
                    end
                    state <= S_IDLE;
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
