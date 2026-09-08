"""
Master Cocotb 2.1 Runner for Comparative MAC Architectures.
Builds and executes functional verification on:
  1. dmr_mac    (Dual Modular Redundancy)
  2. tmr_mac    (Triple Modular Redundancy)
  3. approx_mac (Approximate Computing)
  4. reso_mac   (Time-Redundancy RESO)
"""

import sys
from pathlib import Path
from cocotb_tools.runner import get_runner


def run_comparative_mac_tests():
    test_dir = Path(__file__).resolve().parent
    root_dir = test_dir.parent.parent.parent

    test_configs = [
        {
            "name": "dmr_mac",
            "sources": [root_dir / "rtl" / "mac" / "dmr_mac.v"],
            "toplevel": "dmr_mac",
            "test_module": "test_dmr_mac",
        },
        {
            "name": "tmr_mac",
            "sources": [root_dir / "rtl" / "mac" / "tmr_mac.v"],
            "toplevel": "tmr_mac",
            "test_module": "test_tmr_mac",
        },
        {
            "name": "approx_mac",
            "sources": [root_dir / "rtl" / "mac" / "approx_mac.v"],
            "toplevel": "approx_mac",
            "test_module": "test_approx_mac",
        },
        {
            "name": "reso_mac",
            "sources": [root_dir / "rtl" / "mac" / "reso_mac.v"],
            "toplevel": "reso_mac",
            "test_module": "test_reso_mac",
        },
    ]

    all_passed = True
    print("\n" + "="*70)
    print("  RUNNING COMPARATIVE MAC ARCHITECTURE VERIFICATION SUITE")
    print("="*70)

    for cfg in test_configs:
        print(f"\n>>> Running Verification for: {cfg['name']}...")
        runner = get_runner("icarus")
        try:
            runner.build(
                sources=cfg["sources"],
                hdl_toplevel=cfg["toplevel"],
                parameters={"IN_WIDTH": 8, "OUT_WIDTH": 32},
                build_args=["-g2012"],
                waves=True,
                always=True,
            )
            runner.test(
                hdl_toplevel=cfg["toplevel"],
                test_module=cfg["test_module"],
                waves=True,
            )
            print(f">>> [PASS] {cfg['name']} passed all verification tests!")
        except Exception as e:
            print(f">>> [FAIL] {cfg['name']} encountered failure: {e}", file=sys.stderr)
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("  ALL COMPARATIVE MAC ARCHITECTURES PASSED VERIFICATION (100% SUCCESS)")
    else:
        print("  SOME MAC ARCHITECTURE TESTS FAILED!")
    print("="*70 + "\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_comparative_mac_tests())
