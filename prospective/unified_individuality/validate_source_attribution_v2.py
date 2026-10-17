#!/usr/bin/env python3
"""Fail if the fixed three-panel wild-data DOI identity mapping drifts.

Expected mapping is source-frozen in JAE rc2, confirmed in:
  manuscript/MANUSCRIPT_DRAFT_V0_4_0.md, comparative panels section
  scripts/preflight_new_panel_context.py, id-to-doi source handles

This checks source attribution, not new source/raw observations.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
YEARS = {
    "2016": "10.5441/001/1.282",
    "2022": "10.5441/001/1.321",
    "2023": "10.5441/001/1.322",
}
OTHER = {
    "Tadarida teniotis": "10.5441/001/1.52nn82r9",
    "Eidolon helvum": "10.5441/001/1.k8n02jn8",
    "Hypsignathus monstrosus": "10.5441/001/1.278",
}

def extract_register(text: str, table_label: str) -> dict[str,str]:
    anchor = f"## Supplementary Table {table_label}. "
    start = text.index(anchor)
    region = text[start:]
    end = region.index("\n## ",len(anchor))
    table = region[:end]
    rows = {}
    for line in table.splitlines():
        if not line.startswith("| *"):
            continue
        cells = [a.strip(" *") for a in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        name,doi = cells[0],cells[1]
        if not doi.startswith("10.5441/"):
            continue
        if name in rows:
            raise AssertionError(f"Duplicate source label {name}")
        rows[name]=doi
    return rows

def run() -> None:
    for f,table in [
        ("SUPPORTING_INFORMATION_DRAFT_V1.md","U3"),
        ("SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md","S3")
    ]:
        s=(ROOT/f).read_text(encoding="utf8")
        rows=extract_register(s,table)
        assert len(rows)==6,(f,"expected six panels",rows)
        for year,expected_doi in YEARS.items():
            key=f"Phyllostomus hastatus {year}"
            assert rows.get(key)==expected_doi,(f,key,rows.get(key),expected_doi)
        for key,doi in OTHER.items():
            assert rows.get(key)==doi,(f,key,rows.get(key),doi)
        # Additional attrition and inference constraints remain visible.
        assert "31.1%" in s,(f,"2016 temporal overlap warning missing")
        assert "post-outcome" in s.lower(),(f,"ecological outcome status missing")
        assert "0.0362" in s and "0.0231" in s,(f,"S and co-use boundary numbers missing")
        print("PASS",f,"six source-to-panel DOIs, exact study-year identities")

    manuscript=(ROOT/"INTEGRATED_MANUSCRIPT_V1.md").read_text(encoding="utf8")
    bibliography=manuscript.split("## Consolidated working references",1)[1]
    assert "doi:10.7554/eLife.98171.5." in bibliography, "Version-of-record citation omitted"
    assert "293(2076):20261463" in bibliography, "2026 Teshima metadata omitted"
    assert "212:995–1008" in bibliography, "2026 Eveland pagination omitted"

    anon=(ROOT/"COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md").read_text(encoding="utf8")
    for key in ("doi:10.7554/eLife.98171.5.",
                "293(2076):20261463",
                "212:995–1008"):
        assert key in anon,("anonymized reference copy stale",key)
    for secret in ("zuizui0223","release/jae","prospective/public-causal-synthesis"):
        assert secret not in anon,("source identity leak",secret)
    print("PASS: targeted high-risk 2026 references, anonymous manuscript")

if __name__=="__main__":
    run()
