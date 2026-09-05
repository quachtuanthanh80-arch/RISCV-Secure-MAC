# ==============================================================================
# Constraints for top_module (SoC Integration) on Xilinx Zynq-7000 (xc7z020clg400-1)
# Compatible with PYNQ-Z2 / Arty-Z7 / Zybo-Z7 FPGA Development Boards
# ==============================================================================

# 1. Primary Clock Definition (100 MHz, Period = 10.0 ns)
create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports clk]

# 2. Pin Location (LOC) & I/O Standards (IOSTANDARD) Constraints
# Pin mappings for Xilinx Zynq-7000 (xc7z020clg400-1):
#   - clk   : 125 MHz / 100 MHz Oscillator (Pin H16)
#   - rst_n : Active-low Push Button BTN0 (Pin D19) with internal pull-up
#   - irq   : Status LED LD0 (Pin R14)

set_property PACKAGE_PIN H16 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]

set_property PACKAGE_PIN D19 [get_ports rst_n]
set_property IOSTANDARD LVCMOS33 [get_ports rst_n]
set_property PULLUP true [get_ports rst_n]

set_property PACKAGE_PIN R14 [get_ports irq]
set_property IOSTANDARD LVCMOS33 [get_ports irq]

# 3. Asynchronous Signals False Path
set_false_path -from [get_ports rst_n]
set_false_path -to   [get_ports irq]

# 4. Output Load
set_load 5.000 [get_ports irq]

# 5. DRC Severity Waivers (For PL-Only Soft RISC-V Core & Bitstream Generation)
# Allows standalone FPGA bitstream generation without instantiating the ARM PS7 hard core
set_property SEVERITY {Warning} [get_drc_checks NSTD-1]
set_property SEVERITY {Warning} [get_drc_checks UCIO-1]
set_property SEVERITY {Warning} [get_drc_checks ZYNQ-1]
set_property SEVERITY {Warning} [get_drc_checks ZYNQ-2]
set_property SEVERITY {Warning} [get_drc_checks AVAL-46]
set_property SEVERITY {Warning} [get_drc_checks AVAL-4]
