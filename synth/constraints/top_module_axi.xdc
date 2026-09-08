# ==============================================================================
# Constraints for top_module_axi (Full AXI4-Lite SoC Integration)
# Target Device: Xilinx Zynq-7000 (xc7z020clg400-1)
# Compatible Boards: PYNQ-Z2, Arty-Z7, Zybo-Z7
# ==============================================================================

# 1. Primary Clock Constraint (100 MHz System Clock)
create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports clk]

# 2. Clock Uncertainty (Jitter & Phase Margin for Industrial STA Closure)
set_clock_uncertainty -setup 0.250 [get_clocks sys_clk]
set_clock_uncertainty -hold  0.100 [get_clocks sys_clk]

# 3. Pin Location (LOC) & I/O Standards (IOSTANDARD)
# clk   : 125 MHz / 100 MHz Ethernet PHY / PL Clock (Pin H16)
# rst_n : Active-low Push Button BTN0 (Pin D19) with internal pull-up
# irq   : Status LED LD0 (Pin R14) for Fault/Interrupt Alert

set_property PACKAGE_PIN H16 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]

set_property PACKAGE_PIN D19 [get_ports rst_n]
set_property IOSTANDARD LVCMOS33 [get_ports rst_n]
set_property PULLUP true [get_ports rst_n]

set_property PACKAGE_PIN R14 [get_ports irq]
set_property IOSTANDARD LVCMOS33 [get_ports irq]

# 4. Asynchronous Timing Exceptions (False Paths)
# Reset button is asynchronous to the clock network
set_false_path -from [get_ports rst_n]
# Status LED output is quasi-static, exclude from synchronous setup/hold timing
set_false_path -to   [get_ports irq]

# 5. Output Capacitive Load
set_load 5.000 [get_ports irq]

# 6. DRC Severity Waivers for Standalone PL Flow
set_property SEVERITY {Warning} [get_drc_checks NSTD-1]
set_property SEVERITY {Warning} [get_drc_checks UCIO-1]
set_property SEVERITY {Warning} [get_drc_checks ZYNQ-1]
set_property SEVERITY {Warning} [get_drc_checks ZYNQ-2]
set_property SEVERITY {Warning} [get_drc_checks AVAL-46]
set_property SEVERITY {Warning} [get_drc_checks AVAL-4]
