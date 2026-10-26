import re
import os
import sys

def verify_8pages():
    print("=" * 70)
    print("  VERIFICATION SUITE: 8-PAGE IEEE MANUSCRIPT (main_8pages.tex)")
    print("=" * 70)

    target_tex = r'd:/NCKH/paper/main_8pages.tex'
    target_bib = r'd:/NCKH/paper/references.bib'

    with open(target_tex, 'r', encoding='utf-8') as f:
        tex = f.read()
    with open(target_bib, 'r', encoding='utf-8') as f:
        bib = f.read()

    errors = []
    warnings = []

    # 1. Check environments balance
    begins = re.findall(r'\\begin\{([a-zA-Z0-9_*]+)\}', tex)
    ends = re.findall(r'\\end\{([a-zA-Z0-9_*]+)\}', tex)
    
    from collections import Counter
    cb = Counter(begins)
    ce = Counter(ends)
    all_envs = set(cb.keys()).union(set(ce.keys()))
    for env in all_envs:
        if cb[env] != ce[env]:
            errors.append(f"Environment mismatch: \\begin{{{env}}} ({cb[env]}) vs \\end{{{env}}} ({ce[env]})")
    if not any("Environment mismatch" in e for e in errors):
        print(f"[PASS] All {len(begins)} LaTeX environments are perfectly balanced!")

    # 2. Check Documentclass
    if r'\documentclass[journal]{IEEEtran}' in tex:
        print("[PASS] Documentclass is [journal]{IEEEtran} (Standard IEEE 2-column)")
    else:
        errors.append("Documentclass is not [journal]{IEEEtran}")

    # 3. Check Images referenced
    imgs = re.findall(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}', tex)
    print(f"[INFO] Found {len(imgs)} figures/subfigures referenced in main_8pages.tex")

    search_dirs = [r'd:/NCKH/paper/figures', r'd:/NCKH/paper', r'd:/NCKH/reports/figures']
    missing_imgs = []
    for img in imgs:
        found = any(os.path.exists(os.path.join(d, img)) for d in search_dirs)
        if not found:
            missing_imgs.append(img)
    if missing_imgs:
        errors.append(f"Missing image files: {missing_imgs}")
    else:
        print(f"[PASS] All {len(imgs)} referenced image files exist on disk!")

    # 4. Check Citations in bib
    cites = set()
    for m in re.finditer(r'\\cite\{([^}]+)\}', tex):
        for key in m.group(1).split(','):
            cites.add(key.strip())

    bib_keys = set(re.findall(r'@\w+\s*\{\s*([^,]+),', bib))
    missing_bib = cites - bib_keys
    if missing_bib:
        errors.append(f"Citations missing from references.bib: {missing_bib}")
    else:
        print(f"[PASS] All {len(cites)} cited keys exist in references.bib!")

    # 5. Check Theorem Labels and Refs
    if r'\label{thm:pairwise}' in tex and r'\ref{thm:pairwise}' in tex:
        print("[PASS] Theorem 1 label and cross-reference present")
    else:
        errors.append("Theorem 1 label or ref missing")

    if r'\label{thm:masking}' in tex and r'\ref{thm:masking}' in tex:
        print("[PASS] Theorem 2 label and cross-reference present")
    else:
        errors.append("Theorem 2 label or ref missing")

    # 6. Check Core Empirical Metrics Preserved
    checks = [
        ("WNS", "WNS metric present"),
        ("108.2", "Fmax 108.2 MHz present"),
        ("+43", "+43 LUTs overhead present"),
        ("+5.14", "+5.14% SoC overhead present"),
        ("81.000", "81,000 fault injection trials present"),
        ("98.49", "EWMA MBU FDR 98.49% present"),
        ("96.00", "MLP 96.00% accuracy preserved"),
        ("Clopper-Pearson", "Clopper-Pearson confidence interval present"),
        ("42.6", "42.6x area efficiency vs TMR present")
    ]
    for pattern, desc in checks:
        if pattern in tex:
            print(f"[PASS] {desc}")
        else:
            errors.append(f"Missing critical metric: {pattern}")

    print("=" * 70)
    if errors:
        print(f"VERIFICATION FAILED: {len(errors)} errors found:")
        for e in errors:
            print(f"  - [FAIL] {e}")
        return False
    else:
        print("ALL CHECKS PASSED PERFECTLY (0 ERRORS) FOR 8-PAGE MANUSCRIPT!")
        print("=" * 70)
        return True

if __name__ == '__main__':
    ok = verify_8pages()
    sys.exit(0 if ok else 1)
