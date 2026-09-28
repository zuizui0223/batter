#!/usr/bin/env python3
"""Assemble final JAE v0.3.8 human metadata from one JSON source.

This script never infers authorship, licensing, funding, conflicts, or DOI metadata.
It fails closed until every required human field is explicit.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "MANUSCRIPT_DRAFT_V0_3_8.md"
TITLE_OUT = ROOT / "manuscript" / "TITLE_PAGE_V0_3_8.md"
CFF_OUT = ROOT / "CITATION.cff"
SUMMARY_OUT = ROOT / "submission" / "jae_v0_3_8_metadata_summary.json"

EXPECTED_VERSION = "v0.3.8"
EXPECTED_TITLE = "Repeatable individual shapes of vertical space use persist beyond coarse horizontal occupancy in bats"
WORD_LIMIT = 8500
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", re.IGNORECASE)
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_RE = re.compile(r"\[INSERT\b|\bTBD\b|\bTODO\b", re.IGNORECASE)

CREDIT_ROLES = {
    "Conceptualization", "Data curation", "Formal analysis", "Funding acquisition",
    "Investigation", "Methodology", "Project administration", "Resources", "Software",
    "Supervision", "Validation", "Visualization", "Writing – original draft",
    "Writing – review & editing"
}


def fail(msg: str, failures: list[str]) -> None:
    failures.append(msg)


def words(text: str) -> list[str]:
    text = re.sub(r"`{1,3}.*?`{1,3}", " ", text, flags=re.S)
    text = re.sub(r"[*_#>[]()]", " ", text)
    return re.findall(r"\b[\w.+−-]+\b", text, flags=re.UNICODE)


def q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def author_name(author: dict) -> str:
    return f"{author['given_names'].strip()} {author['family_names'].strip()}".strip()


def validate(payload: dict, stage: str) -> list[str]:
    failures: list[str] = []

    if payload.get("schema_version") != 1:
        fail("schema_version must be 1", failures)
    if payload.get("package_version") != EXPECTED_VERSION:
        fail(f"package_version must be {EXPECTED_VERSION}", failures)
    if payload.get("manuscript_title") != EXPECTED_TITLE:
        fail("manuscript_title does not match frozen v0.3.8 title", failures)

    raw = json.dumps(payload, ensure_ascii=False)
    if PLACEHOLDER_RE.search(raw):
        fail("metadata JSON still contains placeholder text", failures)

    release_date = str(payload.get("release_date", "")).strip()
    if not DATE_RE.match(release_date):
        fail("release_date must be YYYY-MM-DD", failures)
    else:
        try:
            date.fromisoformat(release_date)
        except ValueError:
            fail("release_date is not a valid calendar date", failures)

    license_id = str(payload.get("software_license_spdx", "")).strip()
    if not license_id:
        fail("software_license_spdx is required", failures)
    if not any((ROOT / x).is_file() for x in ("LICENSE", "LICENSE.md", "LICENSE.txt")):
        fail("repository LICENSE file is missing; license choice must be explicit before assembly", failures)

    authors = payload.get("authors")
    if not isinstance(authors, list) or not authors:
        fail("authors must be a non-empty list in final author order", failures)
        authors = []

    affiliations = payload.get("affiliations")
    if not isinstance(affiliations, dict) or not affiliations:
        fail("affiliations must be a non-empty object keyed by affiliation ID", failures)
        affiliations = {}

    corresponding = []
    for i, author in enumerate(authors, start=1):
        given = str(author.get("given_names", "")).strip()
        family = str(author.get("family_names", "")).strip()
        if not given or not family:
            fail(f"author {i} needs given_names and family_names", failures)

        orcid = str(author.get("orcid", "")).strip()
        if orcid and not ORCID_RE.match(orcid):
            fail(f"author {i} ORCID must be empty or formatted 0000-0000-0000-0000", failures)

        aff_ids = author.get("affiliation_ids")
        if not isinstance(aff_ids, list) or not aff_ids:
            fail(f"author {i} needs at least one affiliation_id", failures)
        else:
            for aff_id in aff_ids:
                if str(aff_id) not in affiliations:
                    fail(f"author {i} references unknown affiliation_id {aff_id}", failures)

        roles = author.get("credit_roles")
        if not isinstance(roles, list) or not roles:
            fail(f"author {i} needs at least one CRediT role", failures)
        else:
            for role in roles:
                if role not in CREDIT_ROLES:
                    fail(f"author {i} has unsupported CRediT role: {role}", failures)

        if author.get("corresponding") is True:
            corresponding.append(i - 1)

    if len(corresponding) != 1:
        fail("exactly one author must have corresponding=true", failures)

    corr = payload.get("corresponding_author")
    if not isinstance(corr, dict):
        fail("corresponding_author object is required", failures)
        corr = {}
    email = str(corr.get("email", "")).strip()
    postal = str(corr.get("postal_address", "")).strip()
    if not EMAIL_RE.match(email):
        fail("corresponding_author.email is missing or invalid", failures)
    if not postal:
        fail("corresponding_author.postal_address is required", failures)

    for key in ("acknowledgements", "funding", "conflict_of_interest"):
        value = str(payload.get(key, "")).strip()
        if not value:
            fail(f"{key} is required; write 'None' explicitly if applicable", failures)

    doi = str(payload.get("archive_doi", "")).strip()
    if stage == "post-doi":
        if not DOI_RE.match(doi):
            fail("post-doi stage requires archive_doi beginning with 10.", failures)
    elif doi and not DOI_RE.match(doi):
        fail("archive_doi must be empty before minting or be a valid DOI beginning with 10.", failures)

    if corresponding:
        corr_author = authors[corresponding[0]]
        if not str(corr_author.get("orcid", "")).strip():
            fail("corresponding author ORCID is required for this submission package", failures)

    return failures


def render_title_page(payload: dict) -> str:
    authors = payload["authors"]
    affiliations = payload["affiliations"]
    corr_i = next(i for i, a in enumerate(authors) if a.get("corresponding") is True)
    corr = authors[corr_i]
    corr_meta = payload["corresponding_author"]

    author_line = ", ".join(
        f"{author_name(a)} ({', '.join(str(x) for x in a['affiliation_ids'])})"
        for a in authors
    )
    affiliation_lines = "\n".join(
        f"{key}. {value}" for key, value in sorted(affiliations.items(), key=lambda x: x[0])
    )
    contributions = "\n".join(
        f"- {author_name(a)}: {', '.join(a['credit_roles'])}."
        for a in authors
    )

    corr_orcid = corr["orcid"].strip()
    corr_block = (
        f"{author_name(corr)}  \n"
        f"{corr_meta['postal_address'].strip()}  \n"
        f"Email: {corr_meta['email'].strip()}  \n"
        f"ORCID: https://orcid.org/{corr_orcid}"
    )

    doi = payload.get("archive_doi", "").strip()
    archive_sentence = (
        f"Analysis code, frozen contracts, calibration history and source provenance are archived "
        f"at https://doi.org/{doi}."
        if doi
        else "A versioned Zenodo DOI for the analysis code and provenance will be inserted here after the final GitHub release is archived."
    )

    return f"""# Title page v0.3.8

## Title

{EXPECTED_TITLE}

## Running title

Individual shapes of bat vertical space use

## Authors

{author_line}

## Affiliations

{affiliation_lines}

## Corresponding author

{corr_block}

## Author contributions

{contributions}

## Acknowledgements

{payload['acknowledgements'].strip()}

## Funding

{payload['funding'].strip()}

## Conflict of interest

{payload['conflict_of_interest'].strip()}

## Data availability statement

Tracking data are publicly archived in the Movebank Data Repository. The datasets analysed are
available at DOIs 10.5441/001/1.52nn82r9 (*Tadarida teniotis*),
10.5441/001/1.k8n02jn8 (*Eidolon helvum*), 10.5441/001/1.278
(*Hypsignathus monstrosus*), and 10.5441/001/1.282, 10.5441/001/1.321 and
10.5441/001/1.322 (the three *Phyllostomus hastatus* panels). {archive_sentence}

## Word count

The repository counting rule reports the manuscript and title page separately and as a combined
submission count. The combined value must remain below the Journal of Animal Ecology 8,500-word
Research Article limit.
"""


def render_cff(payload: dict) -> str:
    authors = payload["authors"]
    affiliations = payload["affiliations"]
    corr_i = next(i for i, a in enumerate(authors) if a.get("corresponding") is True)
    lines = [
        "cff-version: 1.2.0",
        f"message: {q('Please cite the archived release of this software.')}",
        f"title: {q('batter: repeatable individual shapes of vertical space use beyond coarse horizontal occupancy')}",
        "type: software",
        "authors:",
    ]
    for i, a in enumerate(authors):
        lines.append(f"  - family-names: {q(a['family_names'].strip())}")
        lines.append(f"    given-names: {q(a['given_names'].strip())}")
        orcid = a.get("orcid", "").strip()
        if orcid:
            lines.append(f"    orcid: {q('https://orcid.org/' + orcid)}")
        aff_text = "; ".join(affiliations[str(x)] for x in a["affiliation_ids"])
        lines.append(f"    affiliation: {q(aff_text)}")
        if i == corr_i:
            lines.append(f"    email: {q(payload['corresponding_author']['email'].strip())}")
    lines.extend([
        f"version: {q(EXPECTED_VERSION)}",
        f"date-released: {q(payload['release_date'].strip())}",
        f"repository-code: {q('https://github.com/zuizui0223/batter')}",
        f"license: {q(payload['software_license_spdx'].strip())}",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default="submission/jae_v0_3_8_metadata.json",
        help="final metadata JSON (not the template)",
    )
    ap.add_argument(
        "--stage",
        choices=("pre-release", "post-doi"),
        default="pre-release",
        help="pre-release allows archive_doi to be empty; post-doi requires the minted version DOI",
    )
    ap.add_argument(
        "--check-only",
        action="store_true",
        help="validate and report without writing TITLE_PAGE_V0_3_8.md or CITATION.cff",
    )
    args = ap.parse_args()

    path = ROOT / args.input
    if not path.is_file():
        print(f"JAE v0.3.8 metadata assembly: BLOCKED\n - missing {args.input}")
        print("Copy submission/jae_v0_3_8_metadata.template.json to that path and fill every field.")
        return 1

    payload = json.loads(path.read_text(encoding="utf-8"))
    failures = validate(payload, args.stage)
    if failures:
        print("JAE v0.3.8 metadata assembly: BLOCKED")
        for item in failures:
            print(f" - {item}")
        return 1

    title_page = render_title_page(payload)
    cff = render_cff(payload)
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    manuscript_words = len(words(manuscript))
    title_words = len(words(title_page))
    combined_words = manuscript_words + title_words

    if combined_words > WORD_LIMIT:
        print("JAE v0.3.8 metadata assembly: BLOCKED")
        print(
            f" - combined manuscript + title-page count is {combined_words}, "
            f"above the {WORD_LIMIT}-word limit"
        )
        return 1

    summary = {
        "schema_version": 1,
        "package_version": EXPECTED_VERSION,
        "metadata_source": args.input,
        "author_count": len(payload["authors"]),
        "corresponding_author": author_name(
            next(a for a in payload["authors"] if a.get("corresponding") is True)
        ),
        "software_license_spdx": payload["software_license_spdx"],
        "stage": args.stage,
        "archive_doi": payload.get("archive_doi", ""),
        "archive_doi_status": "minted" if payload.get("archive_doi", "").strip() else "pending_zenodo",
        "release_date": payload["release_date"],
        "manuscript_words_ci_estimate": manuscript_words,
        "title_page_words_ci_estimate": title_words,
        "combined_words_ci_estimate": combined_words,
        "jae_word_limit": WORD_LIMIT,
        "headroom_words": WORD_LIMIT - combined_words,
    }

    if not args.check_only:
        TITLE_OUT.write_text(title_page, encoding="utf-8")
        CFF_OUT.write_text(cff, encoding="utf-8")
        SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
        SUMMARY_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"JAE v0.3.8 metadata assembly ({args.stage}): READY")
    print(json.dumps(summary, indent=2))
    if args.check_only:
        print("check-only mode: no generated files were written")
    else:
        print(f"wrote {TITLE_OUT.relative_to(ROOT)}")
        print(f"wrote {CFF_OUT.relative_to(ROOT)}")
        print(f"wrote {SUMMARY_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
