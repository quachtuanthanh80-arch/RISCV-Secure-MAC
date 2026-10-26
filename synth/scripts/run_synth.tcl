# ==============================================================================
# Vivado TCL Script for Synthesizing secure_mac.v
# Run using: vivado -mode batch -source run_synth.tcl
# ==============================================================================

# 1. Configuration
# Target a popular Edge AI FPGA (Zynq-7000 series, e.g., PYNQ-Z2 board)
set part "xc7z020clg400-1"
set top_module "secure_mac"

set proj_dir [file normalize [file dirname [info script]]/../..]

puts "========================================================"
puts "  STARTING SYNTHESIS FOR: $top_module"
puts "  TARGET PART: $part"
puts "  PROJECT ROOT: $proj_dir"
puts "========================================================"

# 2. Read Source Files
read_verilog -sv "$proj_dir/rtl/mac/ewma_tracker.sv"
read_verilog -sv "$proj_dir/rtl/mac/secure_mac.v"

# 3. Synthesis
puts ">>> Running Synthesis..."
synth_design -top $top_module -part $part -mode out_of_context

# 4. Constraints (Clock definition for Timing and Power analysis)
# Define a 200 MHz clock (5.0 ns period) to challenge the critical path
# This must be done AFTER synth_design when no project is created
create_clock -name clk -period 5.0 [get_ports clk]

file mkdir "$proj_dir/synth/checkpoints"
write_checkpoint -force "$proj_dir/synth/checkpoints/secure_mac_post_synth.dcp"

# 5. Implementation (Place & Route for accurate Area and Power estimates)
puts ">>> Running Implementation..."
opt_design
place_design
route_design
write_checkpoint -force "$proj_dir/synth/checkpoints/secure_mac_post_route.dcp"

# 6. Generate PPA Reports
puts ">>> Generating Reports..."
file mkdir "$proj_dir/synth/fpga_reports"
report_utilization -file "$proj_dir/synth/fpga_reports/secure_mac_utilization.txt"
report_timing_summary -file "$proj_dir/synth/fpga_reports/secure_mac_timing.txt"
report_power -file "$proj_dir/synth/fpga_reports/secure_mac_power.txt"

puts "========================================================"
puts "  BUILD COMPLETE!"
puts "  Check secure_mac_utilization.txt, secure_mac_timing.txt, and secure_mac_power.txt in fpga_reports/"
puts "========================================================"
