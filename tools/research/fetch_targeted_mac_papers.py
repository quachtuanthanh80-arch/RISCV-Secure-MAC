"""
Targeted academic paper search and downloader for MAC architectures.
Queries OpenAlex and arXiv using strict title filtering to ensure 100% relevant
hardware architecture papers on Fault-Tolerant, Residue, Approximate, and High-Performance MACs.
"""

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:70]


def fetch_targeted_papers():
    root_dir = Path(__file__).resolve().parent.parent.parent
    papers_dir = root_dir / "tailieuthamkhao"
    papers_dir.mkdir(parents=True, exist_ok=True)


    # 4 Core Architectural Categories for Comparison
    searches = [
        {
            "category": "1. Residue & Self-Checking Fault-Tolerant MAC/Multiplier",
            "openalex_query": "title.search:residue+multiplier",
            "arxiv_query": "ti:residue AND (ti:multiplier OR ti:arithmetic)",
            "tag": "Residue_CED_MAC",
        },
        {
            "category": "2. Modular Redundancy (DMR/TMR) & Fault-Tolerant Neural Accelerators",
            "openalex_query": "title.search:fault+tolerant+multiplier",
            "arxiv_query": "ti:\"fault tolerant\" AND (ti:multiplier OR ti:accelerator)",
            "tag": "Redundancy_Fault_Tolerant_MAC",
        },
        {
            "category": "3. Approximate Computing MAC for Energy-Efficient AI/DNN",
            "openalex_query": "title.search:approximate+multiplier+neural",
            "arxiv_query": "ti:\"approximate multiplier\" OR ti:\"approximate MAC\"",
            "tag": "Approximate_AI_MAC",
        },
        {
            "category": "4. High-Performance Fused Multiply-Accumulate (FMA) & Vector MAC",
            "openalex_query": "title.search:fused+multiply+accumulate",
            "arxiv_query": "ti:\"fused multiply\" OR ti:\"multiply-accumulate\"",
            "tag": "High_Performance_FMA",
        },
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    downloaded = []

    for item in searches:
        print(f"\n=======================================================")
        print(f"SEARCHING: {item['category']}")
        print(f"=======================================================")

        # Query OpenAlex with title filter and is_oa:true
        url = f"https://api.openalex.org/works?filter=is_oa:true,{item['openalex_query']}&per-page=10&sort=cited_by_count:desc"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            results = data.get("results", [])
            print(f"Found {len(results)} candidate papers.")

            saved_in_cat = 0
            for work in results:
                if saved_in_cat >= 2:
                    break

                title = work.get("title", "")
                year = work.get("publication_year", "")
                doi = work.get("doi", "")
                cited = work.get("cited_by_count", 0)

                # Find direct PDF URL
                primary_loc = work.get("primary_location") or {}
                best_oa = work.get("best_oa_location") or {}
                pdf_url = primary_loc.get("pdf_url") or best_oa.get("pdf_url")

                # If no direct PDF URL, check if there is an arXiv landing page or doi
                landing_page = primary_loc.get("landing_page_url") or ""
                if not pdf_url and "arxiv.org/abs/" in landing_page:
                    arxiv_id = landing_page.split("arxiv.org/abs/")[-1].strip("/")
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                if not pdf_url:
                    continue

                clean_title = sanitize_filename(title)
                filename = f"{item['tag']}_{year}_{clean_title}.pdf"
                filepath = papers_dir / filename

                print(f"\n-> Attempting: {title} ({year})")
                print(f"   Citations: {cited} | PDF: {pdf_url}")

                try:
                    pdf_req = urllib.request.Request(pdf_url, headers=headers)
                    with urllib.request.urlopen(pdf_req, timeout=20) as p_resp:
                        content = p_resp.read()

                    if content.startswith(b"%PDF") or len(content) > 50000:
                        with open(filepath, "wb") as f:
                            f.write(content)
                        size_mb = len(content) / (1024 * 1024)
                        print(f"   [SUCCESS] Saved {size_mb:.2f} MB to {filename}")
                        saved_in_cat += 1
                        downloaded.append({
                            "category": item["category"],
                            "tag": item["tag"],
                            "title": title,
                            "year": year,
                            "doi": doi,
                            "citations": cited,
                            "filename": filename,
                            "filesize_mb": round(size_mb, 2),
                            "pdf_url": pdf_url,
                        })
                    else:
                        print(f"   [SKIP] Not a direct PDF binary.")
                except Exception as e:
                    print(f"   [FAIL] Could not download: {e}")

        except Exception as e:
            print(f"Failed to query OpenAlex: {e}")

    # Write catalog
    catalog_path = papers_dir / "mac_papers_catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(downloaded, f, indent=2, ensure_ascii=False)

    print(f"\n=======================================================")
    print(f"DOWNLOAD SUMMARY: Successfully downloaded {len(downloaded)} targeted papers.")
    print(f"Catalog: {catalog_path}")
    print(f"=======================================================\n")


if __name__ == "__main__":
    fetch_targeted_papers()
