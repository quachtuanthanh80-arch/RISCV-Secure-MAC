# TCL Script to create full Vivado GUI Project (.xpr)
set proj_dir "D:/NCKH/synth/vivado_project"
set proj_name "RV32I_Secure_MAC"

# Create project
create_project -force $proj_name $proj_dir -part xc7z020clg400-1

# Add SystemVerilog / Verilog Sources
add_files -fileset sources_1 [glob "D:/NCKH/rtl/cpu/*.sv"]
add_files -fileset sources_1 [glob "D:/NCKH/rtl/mac/*.v"]
add_files -fileset sources_1 [glob "D:/NCKH/rtl/top/*.v"]
add_files -fileset sources_1 [glob "D:/NCKH/rtl/top/*.sv"]

# Set Top Module
set_property top top_module [current_fileset]
set_property file_type {SystemVerilog} [get_files "D:/NCKH/rtl/cpu/*.sv"]
set_property file_type {SystemVerilog} [get_files "D:/NCKH/rtl/top/alu_top.sv"]

# Add Constraints (XDC)
add_files -fileset constrs_1 "D:/NCKH/synth/constraints/top_module.xdc"

# Update compile order
update_compile_order -fileset sources_1

puts "================================================================="
puts " [SUCCESS] Created Vivado Project at: $proj_dir/$proj_name.xpr"
puts "================================================================="
