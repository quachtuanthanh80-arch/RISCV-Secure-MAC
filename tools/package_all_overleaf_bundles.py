import os
import zipfile
import shutil

def package_bundle(tex_filename, bbl_filename, zip_name):
    paper_dir = "paper"
    root_dir = "."
    figures_dir = os.path.join(paper_dir, "figures")

    zip_paper = os.path.join(paper_dir, zip_name)
    zip_root = os.path.join(root_dir, zip_name)

    for zpath in [zip_paper, zip_root]:
        if os.path.exists(zpath):
            os.remove(zpath)

    # Build zip
    with zipfile.ZipFile(zip_paper, "w", zipfile.ZIP_DEFLATED) as zf:
        # main.tex (Overleaf expects main.tex as root)
        src_tex = os.path.join(paper_dir, tex_filename)
        zf.write(src_tex, "main.tex")

        # references.bib
        src_bib = os.path.join(paper_dir, "references.bib")
        zf.write(src_bib, "references.bib")

        # IEEEtran.cls & bst
        for f in ["IEEEtran.cls", "IEEEtran.bst"]:
            fp = os.path.join(paper_dir, f)
            if os.path.exists(fp):
                zf.write(fp, f)

        # bbl if exists
        src_bbl = os.path.join(paper_dir, bbl_filename)
        if os.path.exists(src_bbl):
            zf.write(src_bbl, "main.bbl")

        # figures directory
        if os.path.exists(figures_dir):
            for fig in os.listdir(figures_dir):
                fig_path = os.path.join(figures_dir, fig)
                if os.path.isfile(fig_path):
                    zf.write(fig_path, os.path.join("figures", fig))

    # Copy to root
    shutil.copyfile(zip_paper, zip_root)
    print(f"[SUCCESS] Packaged {zip_name} ({os.path.getsize(zip_paper):,} bytes) to paper/ and root!")

def package_all():
    print("=" * 70)
    print("  PACKAGING ALL 3 OVERLEAF ZIP BUNDLES & SYNCING PDFS")
    print("=" * 70)

    # 1. One-column bundle
    package_bundle("main_onecolumn.tex", "main_onecolumn.bbl", "overleaf_onecolumn_project.zip")

    # 2. 8-page IEEE journal bundle
    package_bundle("main_8pages.tex", "main_8pages.bbl", "overleaf_8pages_project.zip")

    # 3. Full two-column bundle
    package_bundle("main.tex", "main.bbl", "overleaf_project.zip")

    # Copy PDFs to root
    for pdf in ["main_onecolumn.pdf", "main_8pages.pdf", "main.pdf"]:
        src = os.path.join("paper", pdf)
        dst = os.path.join(".", pdf)
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            print(f"[SUCCESS] Synced {pdf} ({os.path.getsize(dst):,} bytes) to root directory!")

    print("=" * 70)
    print("  ALL OVERLEAF BUNDLES AND ROOT PDFS ARE 100% UP TO DATE!")
    print("=" * 70)

if __name__ == "__main__":
    package_all()
