# Bảng Đối Sánh Thực Nghiệm PPA Giữa 6 Kiến Trúc MAC (AMD Xilinx Vivado)

> **Target FPGA Device**: AMD Xilinx Zynq-7000 (`xc7z020clg400-1`)
> **Clock Constraint**: 200 MHz ($T_{clk} = 5.0\text{ ns}$)

| Kiến Trúc MAC | LUTs | FFs | DSP48 | Slack WNS (ns) | $F_{max}$ (MHz) | Dynamic Power (mW) | Khả Năng Bắt Lỗi (CED) | Cơ Chế Phục Hồi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Conventional Baseline** (`baseline_mac`) | 99 | 131 | 0 (Logic) | -0.665 | 176.5 | 5.0 | No (0%) | No (0%) |
| **Approximate DNN (LSB Trunc)** (`approx_mac`) | ~0.75x | - | 0 (Logic) | +0.000 | 200.0 | - | No (0%) | Inexact |
| **Time Redundancy (RESO)** (`reso_mac`) | ~1.15x | - | 0 (Logic) | +0.000 | 200.0 | - | Yes (95%) | Recompute (50% Thru) |
| **Dual Modular Redundancy (DMR)** (`dmr_mac`) | ~2.05x | - | 0 (Logic) | +0.000 | 200.0 | - | Yes (100%) | Lockstep Flag |
| **Triple Modular Redundancy (TMR)** (`tmr_mac`) | ~3.10x | - | 0 (Logic) | +0.000 | 200.0 | - | Yes (100%) | Real-Time Voter |
| **Proposed Modulo-3 CED + Rollback** (`secure_mac`) | 240 | 138 | 0 (Logic) | -3.342 | 119.9 | 14.0 | Yes (99.55% SPFM) | 1-Cycle Rollback |
