# ==============================================================================
# AMD Xilinx Vivado Automated Comparative Batch Synthesis Script
# Benchmarking 6 MAC Architectures for Scientific Research Publication:
#   1. Baseline MAC        (Conventional 3-stage signed INT8 MAC)
#   2. Approximate MAC     (Truncated LSBs for energy-efficient DNN)
#   3. RESO MAC            (Time-Redundancy recomputing with shifted operands)
#   4. DMR MAC             (Dual Modular Redundancy Lockstep)
#   5. TMR MAC             (Triple Modular Redundancy Majority Voting)
#   6. Secure MAC          (Proposed Modulo-3 CED + Rollback + Dual-Rail)
#
# Usage:
#   vivado -mode batch -source synth/scripts/run_synth_comparative_macs.tcl
# ==============================================================================

set proj_dir [file normalize [file dirname [info script]]/../..]
set report_dir "$proj_dir/synth/fpga_reports"
file mkdir $report_dir

# Configuration: Target Part & Clock Constraint (200 MHz / 5.0 ns period)
set target_part "xc7z020clg400-1"
set clk_period  5.0

set mac_list {
    {"baseline_mac" "rtl/mac/baseline_mac.v" "Baseline Conventional"}
    {"approx_mac"   "rtl/mac/approx_mac.v"   "Approximate DNN"}
    {"reso_mac"     "rtl/mac/reso_mac.v"     "Time Redundancy (RESO)"}
    {"dmr_mac"      "rtl/mac/dmr_mac.v"      "Dual Modular Redundancy (DMR)"}
    {"tmr_mac"      "rtl/mac/tmr_mac.v"      "Triple Modular Redundancy (TMR)"}
    {"secure_mac"   "rtl/mac/secure_mac.v"   "Proposed Secure MAC (Residue CED)"}
}

puts "======================================================================"
puts "  STARTING COMPARATIVE MAC ARCHITECTURE PPA BENCHMARK (VIVADO)"
puts "  Target FPGA Device: $target_part"
puts "  Clock Constraint   : 200 MHz ($clk_period ns period)"
puts "  Report Directory   : $report_dir"
puts "======================================================================"

set summary_results [list]

foreach mac_entry $mac_list {
    set mac_name [lindex $mac_entry 0]
    set mac_file [lindex $mac_entry 1]
    set mac_desc [lindex $mac_entry 2]

    puts "\n>>> Processing Architecture: $mac_name ($mac_desc)..."

    # Close previous in-memory design if open
    catch {close_design -quiet}

    # 1. Read Verilog Source
    read_verilog "$proj_dir/$mac_file"

    # 2. Out-of-Context Synthesis
    puts "    [1/3] Running synth_design..."
    synth_design -top $mac_name -part $target_part -mode out_of_context

    # 3. Apply Clock Timing Constraints
    create_clock -name clk -period $clk_period [get_ports clk]

    # 4. Implementation (Place & Route for precise PPA)
    puts "    [2/3] Running Implementation (opt, place, route)..."
    opt_design
    place_design
    route_design

    # 5. Generate Individual Reports
    puts "    [3/3] Generating PPA reports..."
    set util_rpt   "$report_dir/${mac_name}_utilization.txt"
    set timing_rpt "$report_dir/${mac_name}_timing.txt"
    set power_rpt  "$report_dir/${mac_name}_power.txt"

    report_utilization -file $util_rpt
    report_timing_summary -file $timing_rpt
    report_power -file $power_rpt

    puts "    Done: $mac_name completed successfully."
}

puts "\n======================================================================"
puts "  ALL 6 MAC ARCHITECTURES SYNTHESIZED AND IMPLEMENTED SUCCESSFULLY!"
puts "  Reports generated in: $report_dir"
puts "======================================================================"
