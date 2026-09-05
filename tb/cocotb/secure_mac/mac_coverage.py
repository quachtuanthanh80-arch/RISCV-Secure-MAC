"""
Functional Coverage Model for Secure MAC Accelerator.
Utilizes cocotb-coverage to define CoverPoints and CoverCrosses for:
- Input operands A, B (INT8) and C (INT32)
- Modulo-3 Residue code space (0, 1, 2)
- Fault injection bit positions (16-bit multiplier, 32-bit accumulator)
- Fault types (Single-bit, Double-bit, Stuck-at, Multi-bit burst)
- State Rollback verification
"""

from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_db
from collections import OrderedDict
from pathlib import Path


def _in_bin_range(val, b):
    """Matcher supporting discrete values or (min_val, max_val) inclusive tuples."""
    if isinstance(b, tuple):
        return b[0] <= val <= b[1]
    return val == b


# ==============================================================================
# 1. INPUT DATA SPACE & RESIDUE COVERAGE
# ==============================================================================
@CoverPoint(
    "secure_mac.operand_a",
    xf=lambda a, b, c: a,
    bins=[-128, (-127, -1), 0, (1, 126), 127],
    bins_labels=["INT8_MIN", "Negative", "Zero", "Positive", "INT8_MAX"],
    rel=_in_bin_range,
)
@CoverPoint(
    "secure_mac.operand_b",
    xf=lambda a, b, c: b,
    bins=[-128, (-127, -1), 0, (1, 126), 127],
    bins_labels=["INT8_MIN", "Negative", "Zero", "Positive", "INT8_MAX"],
    rel=_in_bin_range,
)
@CoverPoint(
    "secure_mac.residue_a",
    xf=lambda a, b, c: (a % 3 + 3) % 3,
    bins=[0, 1, 2],
    bins_labels=["Residue_0", "Residue_1", "Residue_2"],
)
@CoverPoint(
    "secure_mac.residue_b",
    xf=lambda a, b, c: (b % 3 + 3) % 3,
    bins=[0, 1, 2],
    bins_labels=["Residue_0", "Residue_1", "Residue_2"],
)
@CoverPoint(
    "secure_mac.residue_c",
    xf=lambda a, b, c: (c % 3 + 3) % 3,
    bins=[0, 1, 2],
    bins_labels=["Residue_0", "Residue_1", "Residue_2"],
)
@CoverCross(
    "secure_mac.cross_residue_ab",
    items=["secure_mac.residue_a", "secure_mac.residue_b"],
)
def sample_mac_operands(a: int, b: int, c: int):
    """Sample input operands and their residue representations."""
    pass


# ==============================================================================
# 2. FAULT INJECTION SPACE COVERAGE
# ==============================================================================
@CoverPoint(
    "secure_mac.fault_stage",
    xf=lambda stage, bit, ftype, recovered: stage,
    bins=["pipe_product", "pipe_c"],
    bins_labels=["Stage1_Multiplier", "Stage2_Accumulator"],
)
@CoverPoint(
    "secure_mac.fault_bit_accumulator",
    xf=lambda stage, bit, ftype, recovered: bit if stage == "pipe_c" else -1,
    bins=[-1] + list(range(32)),
    rel=lambda val, b: val == b,
)
@CoverPoint(
    "secure_mac.fault_bit_multiplier",
    xf=lambda stage, bit, ftype, recovered: bit if stage == "pipe_product" else -1,
    bins=[-1] + list(range(16)),
    rel=lambda val, b: val == b,
)
@CoverPoint(
    "secure_mac.fault_type",
    xf=lambda stage, bit, ftype, recovered: ftype,
    bins=["single_bit", "double_bit", "stuck_at_0", "stuck_at_1", "burst"],
)
@CoverPoint(
    "secure_mac.rollback_recovered",
    xf=lambda stage, bit, ftype, recovered: recovered,
    bins=[True, False],
    bins_labels=["Rollback_Success", "Rollback_Failed"],
)
def sample_fault_injection(stage: str, bit: int, ftype: str, recovered: bool):
    """Sample fault injection trial parameters and state recovery."""
    pass


# ==============================================================================
# 3. COVERAGE REPORT GENERATION
# ==============================================================================
def get_coverage_summary() -> dict:
    """Return dictionary of coverage percentages across all defined coverpoints."""
    summary = {}
    for key, item in coverage_db.items():
        if key.startswith("secure_mac."):
            summary[key] = {
                "percentage": round(item.cover_percentage, 2),
                "size": item.size,
                "coverage": round(item.coverage, 2),
            }
    return summary


def print_coverage_report():
    """Print formatted ASCII summary of functional coverage."""
    print("\n" + "=" * 70)
    print("           SECURE MAC FUNCTIONAL COVERAGE REPORT")
    print("=" * 70)
    print(f"{'CoverPoint / CoverCross':<45} | {'Coverage':<10} | {'Status'}")
    print("-" * 70)
    
    total_pct = 0
    count = 0
    for key, data in sorted(get_coverage_summary().items()):
        pct = data["percentage"]
        total_pct += pct
        count += 1
        status = "[100% FULL]" if pct >= 100.0 else f"[{pct:.1f}%]"
        print(f"{key:<45} | {pct:>8.2f}% | {status}")
        
    print("-" * 70)
    overall = (total_pct / count) if count > 0 else 0.0
    print(f"{'OVERALL FUNCTIONAL COVERAGE':<45} | {overall:>8.2f}% | {'[QUALIFIED]' if overall >= 90.0 else '[PARTIAL]'}")
    print("=" * 70 + "\n")
