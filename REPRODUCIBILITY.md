# 🔬 Artifact Evaluation & Scientific Reproducibility Guide

> **Paper Title**: *Fault-Resilient RISC-V SoC with Modulo-3 Secure Neural MAC Accelerator for Edge AI Inference*  
> **Repository**: [https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC](https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC)  
> **Target Conferences / Journals**: IEEE Transactions on Computers (TC), IEEE TCAD, IEEE Micro, ACM TODAES, DAC, DATE, ISCAS.  
> **Artifact Badges Targeted**:  
> [![Artifacts Available](https://img.shields.io/badge/Artifacts-Available-blue.svg)](#)
> [![Artifacts Evaluated & Functional](https://img.shields.io/badge/Artifacts-Functional-brightgreen.svg)](#)
> [![Results Reproduced](https://img.shields.io/badge/Results-Reproduced-success.svg)](#)

---

## 1. Overview & Artifact Description

This artifact contains the complete, open-source, synthesizable System-on-Chip (SoC) combining an RV32I 5-stage RISC-V processor core with a fault-tolerant Multiply-Accumulate (MAC) accelerator via an industrial ARM AMBA AXI4-Lite interconnect. 

The artifact enables scientific reviewers and researchers to independently replicate:
1. **RTL Synthesizability & Linting**: 100% clean PySlang AST analysis across all 38 SystemVerilog/Verilog modules and SVA files.
2. **Hardware Fault Resilience Claims**:
   - Single-Point Fault Metric ($\text{SPFM} \ge 99.88\%$) and $0.00\%$ Silent Data Corruption (SDC) under 4,400+ Single-Event Upset (SEU) trials.
   - Multi-Bit Upset (MBU) coverage elevated from $76.27\%$ to $98.49\%$ via the zero-DSP hardware EWMA anomaly tracker.
   - Dual-rail control-path SEU interception adhering to ISO 26262 ASIL D and IEC 61508.
3. **End-to-End Real-World AI Workload Resilience**: Digits MLP quantized INT8 inference over AXI4-Lite with continuous SEU fault injection.
4. **Independent Benchmark Compliance**:
   - **RISC-V International Architectural Certification Tests (`riscv-arch-test`)**: Complete RV32I corner-case instruction compliance.
   - **Embench-IoT `matmult-int`**: $3 \times 3$ integer matrix multiplication bit-exact accuracy and real-time fault recovery.
5. **FPGA Post-Implementation PPA**: Vivado 2026.1 PPA metrics ($F_{max} = 108.21\text{ MHz}$, $124\text{ mW}$ on AMD Xilinx Zynq-7000).

---

## 2. System Requirements & Dependencies

### Hardware Requirements
- **Host CPU**: Any x86_64 or ARM64 processor (Intel Core / AMD Ryzen / Apple Silicon).
- **RAM**: Minimum 4 GB (8 GB recommended).
- **Disk Space**: ~500 MB for repository and simulation artifacts.

### Software Requirements
- **Operating System**: Linux (Ubuntu 20.04/22.04/24.04), macOS, or Windows 10/11 (PowerShell or WSL).
- **Python**: Version 3.10, 3.11, 3.12, or 3.13.
- **Simulator**: [Icarus Verilog (`iverilog`)](https://github.com/steveicarus/iverilog) v11 or v12 (default open-source simulator).
- **Synthesis Tool (Optional for PPA)**: AMD Xilinx Vivado (2020.1 through 2026.1).

### Quick Environment Setup
```bash
git clone https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC.git
cd RISCV-Secure-MAC
pip install cocotb cocotb-tools pyslang matplotlib
```

---

## 3. One-Click Full Verification & Regression (~2.5 minutes)

To execute the entire 18-step master verification suite and generate the comprehensive scientific markdown dashboard:

```bash
python run_all_tests.py
```

### Expected Output Summary:
```text
================================================================================
                      SUMMARY TEST DASHBOARD
================================================================================
Test Suite                                                     | Status   | Time    
--------------------------------------------------------------------------------
1. PySlang RTL Linter & Elaboration Check                      | [PASS]   |   0.37s
2. Cocotb ALU Top Tests & Functional Coverage (30 Cases)       | [PASS]   |   1.78s
3. Cocotb Hazard Unit Tests & SVA Invariants (13 Cases)        | [PASS]   |   1.33s
4. Cocotb CPU Core Sub-Units (Branch & Regfile)                | [PASS]   |   2.43s
5. Cocotb RV32I ISA Compliance Suite (7 Micro-Programs)        | [PASS]   |   1.47s
6. Cocotb Secure MAC Tests & Modulo-3 Coverage (10 Cases)      | [PASS]   |   1.47s
7. Cocotb EWMA Adaptive Anomaly & Corner Cases (8 Cases)       | [PASS]   |   1.47s
8. Cocotb Dual-Rail Control-Path Fault Injection (5 Cases)     | [PASS]   |   1.56s
9. Cocotb SoC System Integration Tests (4 End-to-End Cases)    | [PASS]   |   1.41s
10. Traditional SystemVerilog Self-Checking Testbenches        | [PASS]   |   0.33s
11. Cocotb Fault Injection Campaign (4,400 Trials & Coverage)  | [PASS]   |  52.43s
12. Cocotb AI Inference Resilience Benchmark (INT8 FC Layer)   | [PASS]   |   1.70s
13. Cocotb CPU-to-AXI Master Bridge Suite (6 Cases)            | [PASS]   |   1.55s
14. Cocotb Secure MAC AXI4-Lite IP Suite (10 Cases)            | [PASS]   |   1.52s
15. Cocotb AXI4-Lite Crossbar Interconnect Suite (6 Cases)     | [PASS]   |   1.49s
16. Cocotb Full AXI-Lite SoC Integration Suite (6 Cases)       | [PASS]   |   1.74s
17. Cocotb Digits MLP AXI Resilience Benchmark (2 Cases)       | [PASS]   |  71.51s
18. Independent Benchmarks (Embench-IoT & RISC-V ACT)          | [PASS]   |   2.72s
================================================================================
[SUCCESS] ALL 18 COMPREHENSIVE VERIFICATION SUITES PASSED (100% SUCCESS)!
```

---

## 4. Mapping Paper Claims to Experimental Evidence

| Scientific Claim in Paper | Theoretical Foundation | Test Suite / Script | Verification Evidence |
| :--- | :--- | :--- | :--- |
| **Claim 1: 100% Single-Bit Fault Detection (Zero SDC)** | Modulo-3 ring-homomorphism: $(2^k \bmod 3) \neq 0$ for all $k \ge 0$. | Suite 6 & Suite 11: `tb/cocotb/secure_mac/run_fault_campaign.py` | 4,400 Monte Carlo bit-flips; 0 undetected faults ($SDC = 0.00\%$). |
| **Claim 2: 1-Cycle Autonomous State Rollback** | Shadow Accumulator captures prior state and restores on CED trigger. | Suite 6, 8, 14, 18: `tb/cocotb/benchmarks/test_embench_matmult.py` | Verified in hardware waveform; 0 clock cycle CPU stall overhead. |
| **Claim 3: EWMA Dynamic Anomaly Tracking** | Recursive leaky integrator $\tau_t = \mu_t + k \cdot \text{MAD}_t$ elevates MBU coverage to $98.49\%$. | Suite 7 & Suite 14: `tb/cocotb/secure_mac/test_adaptive_threshold.py` | Zero DSP multiplier usage; adaptive threshold adjusts within 8 cycles. |
| **Claim 4: Dual-Rail Control SEU Immunity (ISO 26262 ASIL D)** | Complementary active-high / active-low encoding of pipeline control signals. | Suite 8: `tb/cocotb/secure_mac/test_control_fault.py` | Intercepts invalid states $\{00, 11\}$; triggers immediate hardware alarm. |
| **Claim 5: AMBA AXI4-Lite Interconnect Correctness** | Formal handshaking invariants on all 5 channels (`AW`, `W`, `B`, `AR`, `R`). | Suite 13, 14, 15, 16: `tb/cocotb/top_module_axi/test_top_module_axi.py` | 0 SVA violations; DECERR on unmapped addresses; backpressure stability. |
| **Claim 6: RISC-V International Architecture Compliance** | Official RISC-V International Architectural Certification Tests (ACT). | Suite 18 (Part 1): `tb/cocotb/benchmarks/test_riscv_arch_test.py` | `I-ADD-01`, `I-SUB-01`, `I-SLT-01`, `I-SLL/SRL/SRA-01`, `I-BRANCH-01` pass 100%. |
| **Claim 7: Embench-IoT Matrix Multiplication Compliance** | Prof. David Patterson's embedded benchmark workload `matmult-int`. | Suite 18 (Part 2): `tb/cocotb/benchmarks/test_embench_matmult.py` | Bit-exact $3 \times 3$ product; seamless rollback under active SEU. |
| **Claim 8: Real-World Deep Learning Resilience** | Quantized INT8 multi-layer perceptron digit recognition forward pass. | Suite 12 & Suite 17: `tb/cocotb/secure_mac_axi/run_ml_inference_test.py` | 50 test samples; $100\%$ inference accuracy under active SEU barrage. |

---

## 5. FPGA Synthesis & Implementation Reproduction (Vivado)

To reproduce the FPGA Post-Implementation PPA figures reported in the manuscript:

```powershell
# Synthesize and route the Secure MAC AXI4-Lite IP on Xilinx Zynq-7000 (xc7z020clg400-1)
vivado -mode batch -source synth/scripts/run_synth_secure_mac_axi.tcl

# Synthesize and route the Complete SoC Top (CPU + Interconnect + Secure MAC)
vivado -mode batch -source synth/scripts/run_synth_top.tcl

# Synthesize comparative architectures (Baseline, DMR, TMR, Approx, RESO)
vivado -mode batch -source synth/scripts/run_synth_comparative_macs.tcl
```

All resulting timing, utilization, and power reports are output to `synth/fpga_reports/`.

---

## 6. Citation

If you use this artifact in your research, please cite:

```bibtex
@article{quach2026securemac,
  title     = {Fault-Resilient RISC-V SoC with Modulo-3 Secure Neural MAC Accelerator for Edge AI Inference},
  author    = {Quach, Tuan Thanh},
  journal   = {IEEE Transactions on Computers / Repository Release},
  year      = {2026},
  url       = {https://github.com/quachtuanthanh80-arch/RISCV-Secure-MAC}
}
```
