#!/usr/bin/env python3
"""Build double-anonymized review archive for the public causal synthesis."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYN = ROOT / "prospective" / "public_causal_synthesis"
FIG = ROOT / "figures" / "public_causal"
SUPFIG = ROOT / "figures" / "public_causal_supplement"
OUTDIR = ROOT / "review_build"
ZIP = OUTDIR / "PUBLIC_CAUSAL_ANONYMIZED_REVIEW_ARCHIVE_V1.zip"
SHA = OUTDIR / "PUBLIC_CAUSAL_ANONYMIZED_REVIEW_ARCHIVE_V1.sha256"

FILES = [
    (SYN / "MANUSCRIPT_ANONYMIZED_BEHAVIORAL_ECOLOGY_V1.md", "manuscript/MANUSCRIPT_ANONYMIZED.md"),
    (SYN / "SUPPLEMENTARY_MATERIAL_DRAFT_V1.md", "supplement/SUPPLEMENTARY_MATERIAL.md"),
    (SYN / "FIGURE_CAPTIONS_V1.md", "manuscript/FIGURE_CAPTIONS.md"),
    (SYN / "FIGURE_ALT_TEXT_V1.md", "manuscript/FIGURE_ALT_TEXT.md"),
    (SYN / "LAY_SUMMARY_V1.md", "manuscript/LAY_SUMMARY.md"),
    (SYN / "MASTER_RESULTS_TABLE_V1.md", "provenance/MASTER_RESULTS_TABLE.md"),
    (SYN / "EVIDENCE_MATRIX_V1.md", "provenance/EVIDENCE_MATRIX.md"),
    (SYN / "MANUSCRIPT_NUMERICAL_AUDIT_V1.md", "provenance/MANUSCRIPT_NUMERICAL_AUDIT.md"),
    (SYN / "REVIEWER_RISK_AUDIT_V1.md", "provenance/REVIEWER_RISK_AUDIT.md"),
    (SYN / "PUBLICATION_OVERLAP_AUDIT_V1.md", "provenance/PUBLICATION_OVERLAP_AUDIT.md"),
    (SYN / "PUBLIC_DATA_CAUSAL_CEILING_V1.md", "provenance/PUBLIC_DATA_CAUSAL_CEILING.md"),
    (SYN / "PUBLIC_FORMATION_SOURCE_SCREEN_CLOSEOUT_V1.md", "provenance/PUBLIC_FORMATION_SOURCE_SCREEN_CLOSEOUT.md"),
    (SYN / "plot_synthesis_figures_v1.py", "code/plot_synthesis_figures_v1.py"),
    (SYN / "figure_evidence_guard_v1.py", "code/figure_evidence_guard_v1.py"),
    (SYN / "manuscript_evidence_guard_v1.py", "code/manuscript_evidence_guard_v1.py"),
    (FIG / "FIGURE_1_CAUSAL_LAYERS_V1.svg", "figures/FIGURE_1_CAUSAL_LAYERS.svg"),
    (FIG / "FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg", "figures/FIGURE_2A_FIRST_FLIGHT_FORMATION.svg"),
    (FIG / "FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg", "figures/FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION.svg"),
    (FIG / "FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg", "figures/FIGURE_3_ACUTE_PERTURBATION_IDENTITY.svg"),
    (FIG / "FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg", "figures/FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY.svg"),
    (SUPFIG / "FIGURE_S1_PROVENANCE_TIMELINE_V1.svg", "supplement/FIGURE_S1_PROVENANCE_TIMELINE.svg"),
    (SUPFIG / "FIGURE_S2_DEVELOPMENTAL_DECOMPOSITIONS_V1.svg", "supplement/FIGURE_S2_DEVELOPMENTAL_DECOMPOSITIONS.svg"),
    (SUPFIG / "FIGURE_S3_EXACT_NULL_RESOLUTION_V1.svg", "supplement/FIGURE_S3_EXACT_NULL_RESOLUTION.svg"),
]

FORBIDDEN = [
    "zuizui0223",
    "github.com/zuizui0223",
    "github.com\\/zuizui0223",
]

SOURCE_INDEX = """# Source data and frozen result index

All source datasets were public before this reanalysis programme.

| Source | Public archive | Biological n used here | Frozen manuscript-facing result | Evidence tier |
|---|---|---:|---|---|
| Harten et al. 2020 | Mendeley Data 10.17632/n9d8gbz3xr.1 | 14 | monotonic formation primary FAIL; late-history secondary supported | primary fail + predeclared secondary |
| Rachum et al. 2025 | Mendeley Data 10.17632/wh7c636y3t.1 | 29 | D=+0.734699, p=0.167785 | unsupported individualization |
| Elie et al. 2024 | Mendeley Data 10.17632/h5ff9vv5pc.1 | 10 | D=-1.425497, exact p=0.716667 | no difference in total individualization |
| Taub & Yovel 2020 | source-public Dropbox archive cited in manuscript | 6 / 5 contrasts | K=+4.941, p=0.04028; K=+6.779, p=0.025 | supported |
| Foskolos et al. 2022 | Zenodo 10.5281/zenodo.4946256; Dryad 10.5061/dryad.ngf1vhhv3 | 3 | A=+0.377542, exact p=1/1296 | supported, small n |
| Diebold et al. 2024 | Zenodo 10.5281/zenodo.13857870 | 4 | K=+1.004452, rank 1/24, p=1/24 | supported, small n |
| Aharon et al. 2017 | Mendeley Data 10.17632/f6mvhj5gj9.3 | 4 | K=+3.695264, rank 2/576, p=0.00347222 | supported |
| Teshima et al. 2026 | Figshare article 29209493 | 5 | fixed transparent I/M K=+0.55428, p=0.0001 | supported, small n |
| Eveland et al. 2026 | public Tunnel_2026 source cited in manuscript | 7 | fixed I/M K=+0.34758, p=0.0007; detailed geometry K=-0.0350, p=0.2144 | coarse supported; geometry unsupported |
| Wild field carrier programme | public source panels cited in associated manuscript | 4 panels | frozen carrier gate 2/4 FAIL | failed confirmatory bridge |

The cross-study synthesis is iterative. Source-level endpoints and null models were frozen before numerical outcome opening within each analysis, but the source search and programme-level synthesis were not prospectively preregistered as one multi-study meta-analysis.
"""

README = """# Anonymous review archive

This package supports double-anonymized review of the manuscript
"Individual organization remains detectable across acute perturbations in bats."

It contains:
- anonymized manuscript;
- manuscript supplement;
- manuscript figures/captions/alt text;
- manuscript-level result/evidence ledgers;
- numerical transcription audit;
- source-data/result index;
- manuscript-level figure and evidence guard code.

It intentionally excludes:
- author names and affiliations;
- acknowledgements/funding/CRediT;
- cover letter;
- Git history;
- identified working-repository links.

The source datasets are public and identified by DOI/archive identifier in
SOURCE_DATA_AND_RESULT_INDEX.md and in the manuscript Data Availability section.

The archive is a curated reviewer package rather than a full clone of the
working development repository.
"""

def is_text(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".py", ".txt", ".json", ".csv", ".svg", ".yml", ".yaml"}

def scan_forbidden(path: Path) -> None:
    if not is_text(path):
        return
    text = path.read_text(encoding="utf-8", errors="strict")
    low = text.lower()
    for token in FORBIDDEN:
        if token.lower() in low:
            raise SystemExit(f"STOP: identifying token {token!r} in packaged file {path}")

def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        stage = Path(td) / "review_archive"
        stage.mkdir(parents=True)

        for src, rel in FILES:
            if not src.exists():
                raise SystemExit(f"STOP: required review file missing: {src}")
            dst = stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        (stage / "README.md").write_text(README + "\n", encoding="utf-8")
        (stage / "SOURCE_DATA_AND_RESULT_INDEX.md").write_text(SOURCE_INDEX + "\n", encoding="utf-8")

        for path in stage.rglob("*"):
            if path.is_file():
                scan_forbidden(path)

        manifest = []
        for path in sorted(p for p in stage.rglob("*") if p.is_file()):
            data = path.read_bytes()
            manifest.append({
                "path": str(path.relative_to(stage)),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })

        (stage / "ARCHIVE_MANIFEST.json").write_text(
            json.dumps({"version": 1, "files": manifest}, indent=2) + "\n",
            encoding="utf-8",
        )
        scan_forbidden(stage / "ARCHIVE_MANIFEST.json")

        if ZIP.exists():
            ZIP.unlink()
        with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for path in sorted(p for p in stage.rglob("*") if p.is_file()):
                zf.write(path, arcname=str(path.relative_to(stage)))

    digest = hashlib.sha256(ZIP.read_bytes()).hexdigest()
    SHA.write_text(f"{digest}  {ZIP.name}\n", encoding="utf-8")
    print(f"PASS anonymized review archive build: {ZIP}")
    print(f"sha256 {digest}")

if __name__ == "__main__":
    main()
