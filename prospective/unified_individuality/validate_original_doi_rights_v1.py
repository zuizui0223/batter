#!/usr/bin/env python3
"""Validate the PUBLIC original-data DOI rights snapshot, NOT derived ZIP rights.

Checks static, original Movebank DSpace 8 Full item source URL/field provenance,
the exact four published bat source DOIs, and the unchanged hard boundary that
individually identified historical GitHub Actions ZIPs have not been granted
redistribution or permanent archival permissions.
No live HTTP, raw animal records, tracking/tag IDs or unpublished data.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "figures" / "VERIFIED_MOVEBANK_ORIGINAL_DOI_RIGHTS_V1.json"
CROSS = HERE / "figures" / "FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json"
PANELS = ("hypsignathus", "phyllostomus_2022",
          "phyllostomus_2023", "phyllostomus_2016")
DOIS = ("10.5441/001/1.278", "10.5441/001/1.321",
        "10.5441/001/1.322", "10.5441/001/1.282")
UUIDS = ("a51b51e0-fbf2-43e2-86ae-bc41c9f53a98",
         "9ce236cf-c0a7-41c4-bbf6-eaf802b2ae92",
         "6749e3ab-1625-445c-bd42-9feac301dedf",
         "5259147d-04a1-471d-a65c-240cd3d7071d")


def check() -> None:
    x = json.loads(SOURCE.read_text(encoding="utf8"))
    cross = json.loads(CROSS.read_text(encoding="utf8"))
    assert x["schema_version"] == 1
    assert x["verification_date_utc"] == "2026-10-18"
    assert x["summary"]["number_with_verified_CC0_1_0_rights"] == 4
    assert x["summary"]["number_of_original_doi_datasets"] == 4
    assert x["summary"]["independent_rights_for_saved_source_per_individual_derived_zip_outputs_verified"] is False
    assert x["summary"]["authorized_access_controlled_permanent_original_zip_archive_established"] is False
    assert x["summary"]["raw_tracking_replay_completed"] is False
    assert x["summary"]["coauthor_paper_approval_obtained"] is False
    assert cross["schema_version"] == 3
    assert [r["panel"] for r in cross["panels"]] == list(PANELS)
    assert len(x["source_datasets"]) == 4
    for i, r in enumerate(x["source_datasets"]):
        assert r["panel"] == PANELS[i]
        assert r["doi"] == DOIS[i]
        assert r["doi_url"] == "https://doi.org/" + DOIS[i]
        assert r["repository_landing_page"] == "https://datarepository.movebank.org/entities/datapackage/" + UUIDS[i]
        assert r["full_metadata_page"] == r["repository_landing_page"] + "/full"
        license = r["published_dataset_rights"]
        assert license["source_metadata_key"] == "dc.rights"
        assert license["license_name"] == "CC0 1.0 Universal"
        assert license["source_license_uri_field"] == "dc.rights.uri"
        assert license["source_license_url"] == "http://creativecommons.org/publicdomain/zero/1.0/"
        assert license["status"].startswith("verified in official")
        assert r["context_keywords"] and len(r["context_keywords"]) == 3
    for record in cross["panels"]:
        assert len(record["original_result_artifact_sources"]) == 4
        assert not record["individual_level_joint_V_S_I_analysis_reported"]
    print("PASS original four Movebank published bat data packages have CC0 1.0 metadata field receipts")
    print("PASS separate downstream per-ID Actions artifact redistribution, permanent archive, and human approval are NOT claimed")
    print("Source metadata was examined externally on 2026-10-18; offline CI does NOT recheck live DOI changes")


if __name__ == "__main__":
    check()
