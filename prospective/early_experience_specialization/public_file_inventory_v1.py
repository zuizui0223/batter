#!/usr/bin/env python3
"""Browser-download the public Mendeley dataset and inventory files only.

No research-data values are opened.
"""

from pathlib import Path
import json, zipfile

from playwright.sync_api import sync_playwright

URL="https://data.mendeley.com/datasets/wh7c636y3t/1"
HERE=Path(__file__).resolve().parent
ZIP=HERE/"mendeley_download_all.zip"
OUT=HERE/"PUBLIC_FILE_INVENTORY_V1.json"
OUTMD=HERE/"PUBLIC_FILE_INVENTORY_V1.md"

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(accept_downloads=True)
        page.goto(URL,wait_until="networkidle",timeout=120000)
        button=page.get_by_role("button",name="Download All")
        with page.expect_download(timeout=120000) as di:
            button.click()
        download=di.value
        download.save_as(str(ZIP))
        browser.close()

    if not zipfile.is_zipfile(ZIP):
        raise SystemExit("STOP: Download All did not return a ZIP archive")

    rows=[]
    with zipfile.ZipFile(ZIP) as z:
        for info in z.infolist():
            rows.append({
                "name":info.filename,
                "size":info.file_size,
                "compressed_size":info.compress_size,
                "is_dir":info.is_dir(),
            })

    result={
        "source":URL,
        "archive_size":ZIP.stat().st_size,
        "n_members":len(rows),
        "members":rows,
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Early-experience public file inventory v1","",
        "**FILE INVENTORY ONLY — NO RESEARCH VALUES OPENED.**","",
        f"- archive size: {result['archive_size']}",
        f"- members: {len(rows)}","",
        "| file | bytes |",
        "|---|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['name']} | {row['size']} |")
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

    ZIP.unlink(missing_ok=True)

if __name__=="__main__":
    main()
