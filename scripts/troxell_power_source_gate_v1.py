"""Original-source admission only; never print or fit numeric observations."""
import hashlib
import json
import pathlib
import urllib.request
import xlrd

URL = "https://datadryad.org/downloads/file_stream/82541"
DOI = "10.5061/dryad.1476d70"
OUTPUT = pathlib.Path("results/troxell_power_source_gate_v1.json")
OLE = bytes.fromhex("d0cf11e0a1b11ae1")


def schema(raw):
    if not raw.startswith(OLE):
        raise ValueError("Not an original legacy Excel workbook")
    wb = xlrd.open_workbook(file_contents=raw, on_demand=True)
    sheets = []
    for name in wb.sheet_names():
        sh = wb.sheet_by_name(name)
        # Only text labels in the first four rows. No numeric values or outcome statistics.
        header = []
        for i in range(min(4, sh.nrows)):
            labels = []
            for j in range(sh.ncols):
                c = sh.cell(i, j)
                if c.ctype == xlrd.XL_CELL_TEXT:
                    labels.append({"column": j, "label": str(c.value)[:200]})
            header.append({"row": i, "text_labels": labels})
        sheets.append({"sheet": name, "rows": sh.nrows, "columns": sh.ncols, "header_candidates": header})
    return sheets


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result = {"doi": DOI, "source_url": URL, "scope": "source_schema_only_no_numeric_outcomes"}
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "batter-research-source-audit/1.0", "Accept": "application/vnd.ms-excel,application/octet-stream,*/*"})
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read(2_000_001)
            result["http_status"] = response.status
            result["content_type"] = response.headers.get("Content-Type")
        result.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), md5=hashlib.md5(raw).hexdigest())
        # Metadata lists 52.74 KB, consistent with 54,016 bytes when displayed in KiB.
        # Size range is only an HTML/incorrect-object check, NOT checksum authentication.
        if not 50_000 <= len(raw) <= 56_000:
            raise ValueError("Unexpected size vs published 52.74 KB")
        result["sheets"] = schema(raw)
        result["status"] = "SCHEMA_READ_PASS_PROVENANCE_DIGEST_RECORDED"
    except Exception as exc:
        result["status"] = "SOURCE_STOP"
        result["error"] = f"{type(exc).__name__}: {exc}"
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUTPUT.read_text())
    if result["status"] == "SOURCE_STOP":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
