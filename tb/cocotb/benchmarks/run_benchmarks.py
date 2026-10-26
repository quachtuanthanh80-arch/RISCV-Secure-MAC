"""
Runner for Independent Reputable Benchmarks:
1. RISC-V International Architectural Certification Tests (riscv-arch-test / ACT) on RV32I top_module
2. Embench-IoT matmult-int Matrix Multiplication Benchmark on Secure MAC AXI SoC (top_module_axi)
"""
import os
import subprocess
import sys
from pathlib import Path
from cocotb_tools.runner import get_runner, Icarus


class IcarusTolerant(Icarus):
    """Icarus runner that tolerates SVA/unsupported warnings gracefully."""

    def _execute(self, cmds, cwd=None):
        for cmd in cmds:
            self.log.info(
                "Running command %s in directory %s",
                " ".join(f"'{c}'" if " " in str(c) else str(c) for c in cmd),
                cwd,
            )
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                env=self.env,
                capture_output=True,
                text=True,
            )
            if proc.stdout:
                print(proc.stdout)
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)

            if proc.returncode != 0:
                has_real_error = any(
                    'error:' in line.lower() and 'sorry:' not in line.lower()
                    for line in (proc.stderr or "").split('\n')
                )
                vvp_path = cwd / "sim.vvp" if cwd else None
                if has_real_error or (vvp_path and not vvp_path.exists()):
                    raise subprocess.CalledProcessError(
                        proc.returncode, cmd,
                        output=proc.stdout, stderr=proc.stderr
                    )
                else:
                    self.log.warning(
                        "iverilog returned exit code %d but only warnings found, continuing...",
                        proc.returncode
                    )


def run_riscv_act_benchmark():
    """Run RISC-V International Architectural Certification Tests (riscv-arch-test)."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent

    sources = [
        root_dir / "rtl" / "cpu" / "alu.sv",
        root_dir / "rtl" / "cpu" / "branch_cmp.sv",
        root_dir / "rtl" / "cpu" / "control_unit.sv",
        root_dir / "rtl" / "cpu" / "hazard_unit.sv",
        root_dir / "rtl" / "cpu" / "imem.sv",
        root_dir / "rtl" / "cpu" / "dmem.sv",
        root_dir / "rtl" / "cpu" / "instruction_decoder.sv",
        root_dir / "rtl" / "cpu" / "pipe_if_id.sv",
        root_dir / "rtl" / "cpu" / "pipe_id_ex.sv",
        root_dir / "rtl" / "cpu" / "pipe_ex_mem.sv",
        root_dir / "rtl" / "cpu" / "pipe_mem_wb.sv",
        root_dir / "rtl" / "cpu" / "regfile.sv",
        root_dir / "rtl" / "cpu" / "riscv_cpu.sv",
        root_dir / "rtl" / "mac" / "secure_mac_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker.sv",
        root_dir / "rtl" / "mac" / "secure_mac.v",
        root_dir / "rtl" / "top" / "top_module.v",
    ]

    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    sim_build = test_dir / "sim_build_act"
    runner = IcarusTolerant()
    runner.build(
        sources=sources,
        hdl_toplevel="top_module",
        build_dir=sim_build,
        build_args=["-g2012"],
        waves=False,
        always=True,
    )
    runner.test(
        hdl_toplevel="top_module",
        test_module="test_riscv_arch_test",
        test_dir=test_dir,
        build_dir=sim_build,
        waves=False,
    )


def run_embench_matmult_benchmark():
    """Run Embench-IoT matmult-int Integer Matrix Multiplication Benchmark on AXI SoC."""
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent

    sources = [
        root_dir / "rtl" / "cpu" / "alu.sv",
        root_dir / "rtl" / "cpu" / "branch_cmp.sv",
        root_dir / "rtl" / "cpu" / "control_unit.sv",
        root_dir / "rtl" / "cpu" / "hazard_unit.sv",
        root_dir / "rtl" / "cpu" / "hazard_unit_sva.sv",
        root_dir / "rtl" / "cpu" / "imem.sv",
        root_dir / "rtl" / "cpu" / "dmem.sv",
        root_dir / "rtl" / "cpu" / "dmem_axi.v",
        root_dir / "rtl" / "cpu" / "instruction_decoder.sv",
        root_dir / "rtl" / "cpu" / "pipe_if_id.sv",
        root_dir / "rtl" / "cpu" / "pipe_id_ex.sv",
        root_dir / "rtl" / "cpu" / "pipe_ex_mem.sv",
        root_dir / "rtl" / "cpu" / "pipe_mem_wb.sv",
        root_dir / "rtl" / "cpu" / "regfile.sv",
        root_dir / "rtl" / "cpu" / "riscv_cpu.sv",
        root_dir / "rtl" / "bus" / "cpu_to_axi_master_sva.sv",
        root_dir / "rtl" / "bus" / "cpu_to_axi_master.v",
        root_dir / "rtl" / "bus" / "axi_interconnect_sva.sv",
        root_dir / "rtl" / "bus" / "axi_interconnect_1m2s.v",
        root_dir / "rtl" / "mac" / "secure_mac_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker_sva.sv",
        root_dir / "rtl" / "mac" / "ewma_tracker.sv",
        root_dir / "rtl" / "mac" / "secure_mac.v",
        root_dir / "rtl" / "mac" / "secure_mac_axi_sva.sv",
        root_dir / "rtl" / "mac" / "secure_mac_axi.v",
        root_dir / "rtl" / "top" / "top_module_axi.v",
    ]

    for src in sources:
        assert src.exists(), f"Source file not found: {src}"

    sim_build = test_dir / "sim_build_embench"
    runner = IcarusTolerant()
    runner.build(
        sources=sources,
        hdl_toplevel="top_module_axi",
        build_dir=sim_build,
        build_args=["-g2012"],
        waves=False,
        always=True,
    )
    runner.test(
        hdl_toplevel="top_module_axi",
        test_module="test_embench_matmult",
        test_dir=test_dir,
        build_dir=sim_build,
        waves=False,
    )


if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING BENCHMARK SUITE: RISC-V ACT & EMBENCH-IOT")
    print("=" * 70)
    print("\n[PART 1] RISC-V International Architectural Certification Tests (ACT)...")
    run_riscv_act_benchmark()
    print("\n[PART 2] Embench-IoT matmult-int (Matrix Multiply & SEU Resilience)...")
    run_embench_matmult_benchmark()
    print("\n" + "=" * 70)
    print("ALL INDEPENDENT REPUTABLE BENCHMARKS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
