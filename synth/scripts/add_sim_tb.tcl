# TCL script to add simulation testbenches to Vivado project
open_project "D:/NCKH/synth/vivado_project/RV32I_Secure_MAC.xpr"

# Add Testbench sources to sim_1 fileset
add_files -fileset sim_1 "D:/NCKH/tb/sv_tb/tb_secure_mac.sv"
add_files -fileset sim_1 "D:/NCKH/tb/sv_tb/tb_top_module.sv"

set_property file_type {SystemVerilog} [get_files "D:/NCKH/tb/sv_tb/*.sv"]

# Set default simulation top to tb_secure_mac (or tb_top_module)
set_property top tb_secure_mac [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]

# Set simulation runtime to 1000ns
set_property -name {xsim.simulate.runtime} -value {1000ns} -objects [get_filesets sim_1]

update_compile_order -fileset sim_1
close_project

puts "================================================================="
puts " [SUCCESS] Added simulation testbenches to Vivado project!"
puts "================================================================="
