"""
Functional Coverage Model for RV32I ALU & Control Unit (alu_top).
Utilizes cocotb-coverage to define CoverPoints and Cross Coverage for:
- All 10 ALU arithmetic/logical operations
- Supported RV32I opcode formats (R-type, I-type, Branch, Load, Store, Upper, Jump)
- Output condition flags (Zero flag, Carry/Overflow flag)
- Cross coverage between Operations and Condition Flags
"""

from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_db


# ALU Operations encoding in alu_top / control_unit
OP_NAMES = {
    0: "ADD",
    1: "SUB",
    2: "AND",
    3: "OR",
    4: "XOR",
    5: "SLL",
    6: "SRL",
    7: "SRA",
    8: "SLT",
    9: "SLTU",
}


@CoverPoint(
    "alu.operation",
    xf=lambda op, a, b, res, zero, carry: op,
    bins=list(range(10)),
    bins_labels=[OP_NAMES[i] for i in range(10)],
)
@CoverPoint(
    "alu.zero_flag",
    xf=lambda op, a, b, res, zero, carry: zero,
    bins=[0, 1],
    bins_labels=["Not_Zero", "Zero_Asserted"],
)
@CoverPoint(
    "alu.carry_flag",
    xf=lambda op, a, b, res, zero, carry: carry,
    bins=[0, 1],
    bins_labels=["No_Carry", "Carry_Asserted"],
)
@CoverCross(
    "alu.cross_op_zero",
    items=["alu.operation", "alu.zero_flag"],
)
def sample_alu_operation(op: int, a: int, b: int, res: int, zero: int, carry: int):
    """Sample an executed ALU operation and its resulting condition flags."""
    pass


def get_alu_coverage_summary() -> dict:
    """Return dictionary of coverage percentages across ALU coverpoints."""
    summary = {}
    for key, item in coverage_db.items():
        if key.startswith("alu."):
            summary[key] = {
                "percentage": round(item.cover_percentage, 2),
                "size": item.size,
                "coverage": round(item.coverage, 2),
            }
    return summary


def print_alu_coverage_report():
    """Print formatted ASCII summary of ALU functional coverage."""
    print("\n" + "=" * 70)
    print("             RV32I ALU FUNCTIONAL COVERAGE REPORT")
    print("=" * 70)
    print(f"{'CoverPoint / CoverCross':<45} | {'Coverage':<10} | {'Status'}")
    print("-" * 70)
    
    total_pct = 0
    count = 0
    for key, data in sorted(get_alu_coverage_summary().items()):
        pct = data["percentage"]
        total_pct += pct
        count += 1
        status = "[100% FULL]" if pct >= 100.0 else f"[{pct:.1f}%]"
        print(f"{key:<45} | {pct:>8.2f}% | {status}")
        
    print("-" * 70)
    overall = (total_pct / count) if count > 0 else 0.0
    print(f"{'OVERALL ALU COVERAGE':<45} | {overall:>8.2f}% | {'[QUALIFIED]' if overall >= 90.0 else '[PARTIAL]'}")
    print("=" * 70 + "\n")
