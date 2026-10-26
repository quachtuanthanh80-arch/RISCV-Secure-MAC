# ==============================================================================
# Vivado Batch DRC & Methodology Check Script for RISC-V Secure MAC SoC
# Run using: vivado -mode batch -source run_methodology.tcl
# ==============================================================================

set proj_dir [file normalize [file dirname [info script]]/../..]
set dcp_file "$proj_dir/synth/checkpoints/post_route.dcp"

if {![file exists $dcp_file]} {
    puts "Checkpoint not found at $dcp_file. Synthesizing first..."
    source "$proj_dir/synth/scripts/run_synth_top.tcl"
} else {
    puts ">>> Opening routed checkpoint: $dcp_file"
    open_checkpoint $dcp_file
}

puts ">>> Running Vivado Methodology Check..."
file mkdir "$proj_dir/synth/fpga_reports"
report_methodology -file "$proj_dir/synth/fpga_reports/top_module_methodology.txt"

puts ">>> Running Design Rule Check (DRC)..."
report_drc -file "$proj_dir/synth/fpga_reports/top_module_drc.txt"

puts ">>> Generating Timing Slack Analysis..."
report_timing_summary -file "$proj_dir/synth/fpga_reports/top_module_timing.txt"

puts "========================================================"
puts "  METHODOLOGY & DRC CHECK COMPLETED!"
puts "  Reports: $proj_dir/synth/fpga_reports/"
puts "========================================================"
