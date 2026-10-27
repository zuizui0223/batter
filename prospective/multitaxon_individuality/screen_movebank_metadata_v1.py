#!/usr/bin/env python3
"""Deterministic METADATA-only Movebank screening of all 437 published packages.

DO NOT call metadata-pass rows biologically eligible, species-level replicates,
actual raw GPS, 3D niche partitions, or ecological results. Flags are only
source-DOI preflight invitations to inspect identity and positional data files.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CENSUS = ROOT / "MOVEBANK_PUBLISHED_DATAPACKAGES_CENSUS_2026_10_18.json"
SCREEN = ROOT / "MOVEBANK_METADATA_SCREEN_V1.json"
SOURCE_SHA1 = "fc69fc259c641f813848a819a4eb736886acba58"
LATIN = re.compile(r"^[A-Z][a-z]{2,} [a-z]{2,}(?:-[a-z]+)?$")
POSITION_TAG = re.compile(r"\bGPS\b|\bArgos\b|satellite telemetry|GSM telemetry|radio telemetry|\bVHF\b|FastLoc", re.I)
LICENSE = {
    "CC0 1.0 Universal": "CC0",
    "Attribution 4.0 International": "CC-BY",
    "Attribution-NonCommercial 4.0 International": "CC-BY-NC",
}
EXPECTED = {
    "PRIORITY_METADATA_PREFLIGHT": 227,
    "PENDING_SENSOR_FILE_REVIEW": 135,
    "PENDING_TAXON_RESOLUTION": 50,
    "NC_RIGHTS_REVIEW": 25,
}


def git_blob_sha1(p: Path) -> str:
    b = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\0" + b).hexdigest()


def metadata_screen(row: dict) -> dict:
    subjects = row.get("subjects") or []
    spatial = [s for s in subjects if POSITION_TAG.search(s)]
    taxa = list(dict.fromkeys(s for s in subjects if LATIN.fullmatch(s)))
    license_name = row.get("license")
    right = LICENSE.get(license_name, "rights_review")
    if not spatial:
        tier = "PENDING_SENSOR_FILE_REVIEW"
    elif len(taxa) != 1:
        tier = "PENDING_TAXON_RESOLUTION"
    elif right == "rights_review":
        tier = "PENDING_RIGHTS"
    elif right == "CC-BY-NC":
        tier = "NC_RIGHTS_REVIEW"
    else:
        tier = "PRIORITY_METADATA_PREFLIGHT"
    return {
        "doi": row["doi"], "uuid": row["uuid"], "license": license_name,
        "source_subject_geoposition_tags": spatial,
        "source_subject_latin_labels": taxa,
        "position_source_metadata": (
            "metadata_explicit_geoposition_sensor" if spatial
            else "sensor_unknown_or_non_GPS_from_metadata"
        ),
        "taxon_from_subjects_only": (
            "one_latin_binomial_label" if len(taxa) == 1
            else "multispecies_or_multiple_labels" if len(taxa) > 1
            else "taxon_unresolved_from_subjects"
        ),
        "stage1_preflight_tier": tier,
        "actual_track_file_format_verified": False,
        "actual_biological_n_verified": False,
        "individual_time_block_eligibility_verified": False,
        "independent_site_cohort_verified": False,
    }


def main() -> None:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    assert git_blob_sha1(CENSUS) == SOURCE_SHA1 == screen["input_census_git_blob_sha1"]
    assert census["schema_version"] == screen["schema_version"] == 1
    assert len(census["records"]) == len(screen["records"]) == 437
    assert census["summary"]["total_count"] == 437
    assert all(r.get("entity_type") == "Datapackage" for r in census["records"])
    candidates = [metadata_screen(r) for r in census["records"]]
    assert candidates == screen["records"], "Metadata screening differs from committed machine receipt"
    counts = Counter(r["stage1_preflight_tier"] for r in candidates)
    assert dict(counts) == EXPECTED
    assert screen["summary"]["categories"] == EXPECTED
    assert screen["summary"]["total_packages"] == 437
    assert screen["summary"]["metadata_priority_count"] == 227
    assert screen["summary"]["with_spatial_sensor_subject_tag"] == 302
    assert screen["summary"]["with_exactly_one_subject_latin_label"] == 344
    assert screen["summary"]["actual_biologically_eligible_packages_confirmed"] == 0
    rights = Counter(r["license"] for r in census["records"])
    assert dict(rights) == census["summary"]["license_counts"] == {
        "CC0 1.0 Universal": 376,
        "Attribution 4.0 International": 27,
        "Attribution-NonCommercial 4.0 International": 34,
    }
    print("PASS Movebank published Datapackages metadata census: 437 DOI/UUID records")
    print("PASS stage1 PRELIMINARY flags only: 227 priority, 25 NC rights, 50 unresolved taxa, 135 unresolved sensor")
    print("NOT verified: raw GPS tracks, ≥8 repeated individuals, independent contexts, valid inference, or any biological effect")


if __name__ == "__main__":
    main()
