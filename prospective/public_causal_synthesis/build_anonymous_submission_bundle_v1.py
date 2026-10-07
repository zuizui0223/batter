#!/usr/bin/env python3
"""Build one anonymous Behavioral Ecology submission bundle.

Inputs must already have passed their own builders/guards in this workflow.
"""

from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SYN=ROOT/"prospective"/"public_causal_synthesis"
FIG=ROOT/"figures"/"public_causal"
SUB=ROOT/"submission"/"public_causal"
DIST=ROOT/"dist"

STAGE=ROOT/"submission_bundle"/"behavioral_ecology_anonymous_v1"
OUT=DIST/"behavioral_ecology_anonymous_submission_bundle_v1.zip"

FILES=[
    (SYN/"COMPLETE_ANONYMOUS_TEXT_V1.md","MANUSCRIPT_COMPLETE_ANONYMOUS.md"),
    (SYN/"FIGURE_ALT_TEXT_V1.md","FIGURE_ALT_TEXT.md"),
    (SUB/"SUPPLEMENTARY_MATERIAL_V1.pdf","SUPPLEMENTARY_MATERIAL_V1.pdf"),
    (FIG/"FIGURE_1_CAUSAL_LAYERS_V1.svg","FIGURE_1_CAUSAL_LAYERS_V1.svg"),
    (FIG/"FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg","FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg"),
    (FIG/"FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg","FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg"),
    (FIG/"FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg","FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg"),
    (FIG/"FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg","FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg"),
    (DIST/"behavioral_ecology_anonymous_review_archive_v1.zip","ANONYMOUS_REPRODUCIBILITY_ARCHIVE_V1.zip"),
]

BANNED=[
    "zuizui0223",
    "github.com/zuizui0223",
    "ZHANG Ruiqi",
    "張瑞琪",
]

README="""# Behavioral Ecology anonymous submission bundle v1

This bundle contains the reviewer-facing anonymous submission objects:

- complete anonymous manuscript text;
- main figures;
- figure alt text;
- verified single Supplementary Material PDF;
- sanitized full reproducibility review archive.

The manuscript intentionally contains [ANONYMIZED_REVIEW_ARCHIVE_URL] until the
reproducibility archive is uploaded to an anonymous review-capable host or the
journal's anonymous file mechanism.

This bundle contains no author metadata, cover letter, funding statement,
CRediT statement, or identified working-repository URL.

Before actual journal upload:
1. place ANONYMOUS_REPRODUCIBILITY_ARCHIVE_V1.zip on the chosen anonymous host
   or journal file mechanism;
2. replace [ANONYMIZED_REVIEW_ARCHIVE_URL] in the manuscript if a URL is required;
3. do not expose the identified development-repository workflow URL to reviewers.
"""

TEXT_SUFFIXES={".md",".txt",".svg",".json",".csv",".py",".yml",".yaml"}

def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def scan_text(path:Path):
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    text=path.read_text(encoding="utf-8",errors="strict")
    low=text.lower()
    for token in BANNED:
        if token.lower() in low:
            raise SystemExit(f"STOP identifying token {token!r} in {path}")

def scan_pdf(path:Path):
    import pymupdf
    doc=pymupdf.open(path)
    text="\n".join(page.get_text() for page in doc)
    low=text.lower()
    for token in BANNED:
        if token.lower() in low:
            raise SystemExit(f"STOP identifying token {token!r} in PDF {path}")
    if doc.page_count != 7:
        raise SystemExit(f"STOP expected 7-page Supplementary PDF, got {doc.page_count}")

def main():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    DIST.mkdir(parents=True,exist_ok=True)

    for src,rel in FILES:
        if not src.exists():
            raise SystemExit(f"STOP missing bundle input: {src}")
        dst=STAGE/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)

    (STAGE/"README.md").write_text(README+"\n",encoding="utf-8")

    for p in STAGE.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower()==".pdf":
            scan_pdf(p)
        else:
            scan_text(p)

    manifest=[]
    for p in sorted(x for x in STAGE.rglob("*") if x.is_file()):
        manifest.append({
            "path":p.relative_to(STAGE).as_posix(),
            "bytes":p.stat().st_size,
            "sha256":sha256(p),
        })

    (STAGE/"BUNDLE_MANIFEST.json").write_text(
        json.dumps({"version":1,"files":manifest},indent=2)+"\n",
        encoding="utf-8"
    )

    sums=[]
    for p in sorted(x for x in STAGE.rglob("*") if x.is_file()):
        sums.append(f"{sha256(p)}  {p.relative_to(STAGE).as_posix()}")
    (STAGE/"SHA256SUMS.txt").write_text("\n".join(sums)+"\n",encoding="utf-8")

    scan_text(STAGE/"README.md")
    scan_text(STAGE/"BUNDLE_MANIFEST.json")
    scan_text(STAGE/"SHA256SUMS.txt")

    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(x for x in STAGE.rglob("*") if x.is_file()):
            z.write(p,p.relative_to(STAGE))

    print(f"bundle={OUT}")
    print(f"bytes={OUT.stat().st_size}")
    print(f"sha256={sha256(OUT)}")
    print(f"files={len(list(x for x in STAGE.rglob('*') if x.is_file()))}")

if __name__=="__main__":
    main()
