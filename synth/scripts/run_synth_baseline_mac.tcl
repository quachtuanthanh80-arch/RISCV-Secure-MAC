# ==============================================================================
# Vivado TCL Script for Synthesizing and Implementing baseline_mac.v
# Run using: vivado -mode batch -source run_synth_baseline_mac.tcl
# ==============================================================================

# 1. Configuration
set part "xc7z020clg400-1"
set top_module "baseline_mac"
set proj_dir [file normalize [file dirname [info script]]/../..]

puts "========================================================"
puts "  STARTING SYNTHESIS FOR BASELINE MAC: $top_module"
puts "  TARGET PART: $part"
puts "  PROJECT ROOT: $proj_dir"
puts "========================================================"

# 2. Read Source Files
read_verilog "$proj_dir/rtl/mac/baseline_mac.v"

# 3. Synthesis (Out of context)
puts ">>> Running Synthesis..."
synth_design -top $top_module -part $part -mode out_of_context

# 4. Timing Constraints (Clock 200 MHz / 5.0 ns period)
create_clock -name clk -period 5.0 [get_ports clk]

file mkdir "$proj_dir/synth/checkpoints"
write_checkpoint -force "$proj_dir/synth/checkpoints/baseline_mac_post_synth.dcp"

# 5. Implementation (Place & Route for accurate PPA)
puts ">>> Running Implementation..."
opt_design
place_design
route_design
write_checkpoint -force "$proj_dir/synth/checkpoints/baseline_mac_post_route.dcp"

# 6. Generate PPA Reports
puts ">>> Generating PPA Reports..."
file mkdir "$proj_dir/synth/fpga_reports"
report_utilization -file "$proj_dir/synth/fpga_reports/baseline_mac_utilization.txt"
report_timing_summary -file "$proj_dir/synth/fpga_reports/baseline_mac_timing.txt"
report_power -file "$proj_dir/synth/fpga_reports/baseline_mac_power.txt"

puts "========================================================"
puts "  BUILD COMPLETE FOR BASELINE MAC!"
puts "  Reports saved in synth/fpga_reports/baseline_mac_*.txt"
puts "========================================================"
