# ==============================================================================
# Vivado TCL Script for Synthesizing secure_mac_axi.v (AXI4-Lite IP Core)
# Run using: vivado -mode batch -source run_synth_secure_mac_axi.tcl
# ==============================================================================

set part "xc7z020clg400-1"
set top_module "secure_mac_axi"
set proj_dir [file normalize [file dirname [info script]]/../..]

puts "========================================================"
puts "  STARTING SYNTHESIS FOR AXI4-LITE IP: $top_module"
puts "  TARGET PART: $part"
puts "  PROJECT ROOT: $proj_dir"
puts "========================================================"

# Read RTL Sources
read_verilog -sv "$proj_dir/rtl/mac/ewma_tracker.sv"
read_verilog -sv "$proj_dir/rtl/mac/secure_mac.v"
read_verilog -sv "$proj_dir/rtl/mac/secure_mac_axi.v"

# Synthesis out-of-context (OOC) IP core
puts ">>> Running Synthesis..."
synth_design -top $top_module -part $part -mode out_of_context

# Constraints: 100 MHz target for AXI bus (10.0 ns)
create_clock -name aclk -period 10.0 [get_ports aclk]

file mkdir "$proj_dir/synth/checkpoints"
write_checkpoint -force "$proj_dir/synth/checkpoints/secure_mac_axi_post_synth.dcp"

# Place & Route
puts ">>> Running Implementation..."
opt_design
place_design
route_design
write_checkpoint -force "$proj_dir/synth/checkpoints/secure_mac_axi_post_route.dcp"

# Generate PPA Reports
puts ">>> Generating Reports..."
file mkdir "$proj_dir/synth/fpga_reports"
report_utilization -file "$proj_dir/synth/fpga_reports/secure_mac_axi_utilization.txt"
report_timing_summary -file "$proj_dir/synth/fpga_reports/secure_mac_axi_timing.txt"
report_power -file "$proj_dir/synth/fpga_reports/secure_mac_axi_power.txt"

puts "========================================================"
puts "  BUILD COMPLETE FOR SECURE MAC AXI4-LITE IP!"
puts "========================================================"
