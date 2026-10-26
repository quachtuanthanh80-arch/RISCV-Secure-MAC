import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os

def search_and_download_arxiv(search_terms, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    all_results = {}
    
    for term in search_terms:
        url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(term)}&max_results=15"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                tree = ET.fromstring(resp.read().decode())
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in tree.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                pdf_link = None
                for link in entry.findall('atom:link', ns):
                    if link.attrib.get('title') == 'pdf':
                        pdf_link = link.attrib.get('href')
                pub = entry.find('atom:published', ns).text[:10]
                summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                all_results[title] = {
                    'title': title,
                    'authors': authors,
                    'pdf': pdf_link,
                    'pub': pub,
                    'summary': summary
                }
        except Exception as e:
            print(f"Error searching {term}: {e}")

    print(f"Total found from arXiv: {len(all_results)}")
    
    # Filter for Vietnamese authors / affiliations
    vn_surnames = {'Tran', 'Nguyen', 'Bui', 'Pham', 'Le', 'Vu', 'Hoang', 'Dang', 'Do', 'Vo', 'Dinh', 'Trinh'}
    
    selected = []
    for title, info in all_results.items():
        authors = info['authors']
        has_vn_author = any(any(part in a for part in vn_surnames) for a in authors)
        if has_vn_author and info['pdf']:
            selected.append(info)
            
    print(f"Filtered {len(selected)} papers with Vietnamese authors.")
    
    for idx, item in enumerate(selected, 1):
        clean_title = "".join(c for c in item['title'] if c.isalnum() or c in (' ', '_', '-')).rstrip()
        clean_title = "_".join(clean_title.split()[:8])
        first_author = item['authors'][0].split()[-1]
        year = item['pub'][:4]
        filename = f"{first_author}_{year}_{clean_title}.pdf"
        filepath = os.path.join(out_dir, filename)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            print(f"[ALREADY EXISTS] {filename}")
            continue
            
        pdf_url = item['pdf']
        if not pdf_url.endswith('.pdf'):
            pdf_url += '.pdf'
            
        try:
            req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 1000 and data[:5] == b'%PDF-':
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    print(f"[DOWNLOADED] {filename} ({len(data):,} bytes)")
                else:
                    print(f"[INVALID PDF] {filename}")
        except Exception as e:
            print(f"[FAIL] {filename}: {e}")

queries = [
    'au:"Khanh N. Dang"',
    'au:"Xuan-Tu Tran"',
    'au:"Duy-Hieu Bui"',
    'au:"Akram Ben Ahmed" AND au:"Tran"',
    'all:"3D-NoC" AND (all:"fault-tolerant" OR all:"soft-error") AND all:"Dang"',
    'all:"neuromorphic" AND all:"fault-tolerant" AND all:"NoC"',
    'all:"RISC-V" AND all:"accelerator" AND all:"Tran"',
    'all:"RISC-V" AND all:"FPGA" AND all:"Nguyen"',
    'all:"fault injection" AND all:"RISC-V"'
]

search_and_download_arxiv(queries, 'd:/NCKH/tailieuthamkhao_vietnamese_authors')
