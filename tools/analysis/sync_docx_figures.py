#!/usr/bin/env python3
import zipfile, io
from pathlib import Path

def sync_figures():
    root_dir = Path(__file__).resolve().parent.parent.parent
    docx_path = root_dir / 'docs' / 'Bao_cao_NCKH_2026_Da_chinh_sua_v2.docx'
    figures_dir = root_dir / 'reports' / 'figures'

    updates = {
        'word/media/image7.png': figures_dir / 'fig3_1_fpga_ppa_implementation.png',
        'word/media/image8.png': figures_dir / 'fig3_2_single_bit_fdr.png',
        'word/media/image9.png': figures_dir / 'fig3_3_bit_distance_parity_spectrum.png',
        'word/media/image10.png': figures_dir / 'fig3_4_fault_classification_breakdown.png',
        'word/media/image11.png': figures_dir / 'fig3_5_multibit_burst_scaling.png',
    }

    for zip_entry, file_path in updates.items():
        if not file_path.exists():
            raise FileNotFoundError(f'Missing source figure: {file_path}')

    with open(docx_path, 'rb') as f:
        docx_data = f.read()

    in_zip = zipfile.ZipFile(io.BytesIO(docx_data), 'r')
    out_buffer = io.BytesIO()
    out_zip = zipfile.ZipFile(out_buffer, 'w', compression=zipfile.ZIP_DEFLATED)

    replaced_count = 0
    for item in in_zip.infolist():
        if item.filename in updates:
            new_data = updates[item.filename].read_bytes()
            out_zip.writestr(item.filename, new_data)
            print(f'[REPLACED] {item.filename} with {updates[item.filename].name} ({len(new_data)} bytes)')
            replaced_count += 1
        else:
            out_zip.writestr(item, in_zip.read(item.filename))

    in_zip.close()
    out_zip.close()

    try:
        docx_path.write_bytes(out_buffer.getvalue())
        print(f"[SUCCESS] Successfully updated {replaced_count} figures directly in: {docx_path.resolve()}")
    except PermissionError:
        synced_path = docx_path.parent / "Bao_cao_NCKH_2026_Da_chinh_sua_v2_synced.docx"
        synced_path.write_bytes(out_buffer.getvalue())
        print(f"[NOTE] {docx_path.name} is currently open in Word. Saved synced copy to: {synced_path.name}")


if __name__ == '__main__':
    sync_figures()
