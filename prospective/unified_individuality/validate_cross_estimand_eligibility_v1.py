#!/usr/bin/env python3
"""Audit *aggregate* bat-ID intersections across three historical study-family assays.

Default CI: immutable original source-summary Git blobs, archived 16 artifact IDs
and digest declarations, and the 4-panel count crosswalk; **no private animal
IDs are downloaded or printed**.

Opt-in offline --artifact-dir: rehash 16 operator-supplied, historically original
GitHub Actions ZIPs (available only if access and retention permit), then
recompute cross-analysis membership of exact (original cohort, bat identifier)
tuples. No raw GPS/DEM required. Do not upload original ID-bearing ZIPs, copy
tag IDs into issue/PR comments, or mistake overlapping identity for new
within-animal V-I association.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
HIST = HERE / "source_recovery" / "co_use_centered_history"
FINE = HERE / "source_recovery" / "fine500_history" / "result_summary_v1.json"
COUSE = HIST / "COUSE_VERTICAL_SEPARATION_RESULT_V1.md"
LEDGER = FIG / "FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json"
ORIG = {
    FIG / "FROZEN_FIGURE_DATA_V1.json":
        "b3f7b20136d028021a3c33a43c256e40ce91f677",
    FIG / "ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json":
        "c1d37e42f72f59e5aba364daec9aef68b47778b6",
    COUSE: "d7b6054d95e7a6c27baf8e35a2f7377f628fe818",
    FINE: "a2960b45a1a7ea1e0e3beebe6eb799a47f114bed",
}
PANEL_ORDER = (
    "hypsignathus", "phyllostomus_2022",
    "phyllostomus_2023", "phyllostomus_2016"
)
ORIG_LABELS = (
    "Hypsignathus monstrosus", "Phyllostomus hastatus 2022",
    "P. hastatus 2023", "P. hastatus 2016"
)
ROLES = ("fine500", "native3d", "terrain3d", "co_use")
RUNS = {"fine500": 36519747717, "native3d": 36881187913,
        "terrain3d": 36946126004, "co_use": 36953712597}
EXPECTED_COUNTS = (
    # fine, native/terrain geometry, I, fine∩geom, fine∩I, geom∩I, all3
    (19, 8, 11, 8, 10, 5, 5),
    (23, 5, 6, 5, 6, 3, 3),
    (11, 6, 6, 6, 6, 5, 5),
    (9, 9, 5, 9, 5, 5, 5),
)


def git_blob_sha1(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\0" + b).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_couse_rows() -> dict:
    """Only original aggregate counts, never print original source animal names."""
    rows = {}
    for line in COUSE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| *"):
            continue
        cells = [x.strip().replace("*", "") for x in line.strip().split("|")[1:-1]]
        if not cells or cells[0] not in ORIG_LABELS:
            continue
        assert len(cells) == 11, "Unexpected original co-use table column count"
        rows[cells[0]] = {
            "n": int(cells[3]), "dyads": int(cells[4]),
            "encounters": int(cells[5].replace(",", "")),
            "time": int(cells[2].removesuffix(" s")),
            "scope": "all_space" if cells[1] == "all-space" else "endpoint_excluded",
        }
    assert set(rows) == set(ORIG_LABELS)
    return rows


def metadata_gate() -> dict:
    ledger = read_json(LEDGER)
    figure = read_json(FIG / "FROZEN_FIGURE_DATA_V1.json")["terrain"]
    geom = read_json(FIG / "ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json")["panels"]
    fine = read_json(FINE)["panels"]
    couse = source_couse_rows()
    assert ledger["schema_version"] == 3
    assert ledger["artifact_crosswalk_provenance"]["source_archive_sha256_matched_zips"] == 16
    assert ledger["artifact_crosswalk_provenance"]["original_bat_ID_values_committed"] is False
    assert ledger["artifact_crosswalk_provenance"]["independent_native_vs_terrain_ID_set_match"]
    assert ledger["artifact_crosswalk_provenance"]["successful_original_workflow_run_ids"] == RUNS

    expected_source = {
        "figures/FROZEN_FIGURE_DATA_V1.json": ORIG[FIG / "FROZEN_FIGURE_DATA_V1.json"],
        "figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json":
            ORIG[FIG / "ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json"],
        "historical_release/post_freeze_extensions/3d_niche_partition/COUSE_VERTICAL_SEPARATION_RESULT_V1.md":
            ORIG[COUSE],
        "historical_release/post_freeze_extensions/fine_place_kinematic_500m/result_summary_v1.json":
            ORIG[FINE],
    }
    assert {r["path"]: r["git_blob_sha1"] for r in ledger["source"]} == expected_source
    for p, digest in ORIG.items():
        assert git_blob_sha1(p) == digest, "Historical source summary Git blob drift"
    assert [x["panel"] for x in ledger["panels"]] == list(PANEL_ORDER)
    assert [x["panel"] for x in figure] == list(PANEL_ORDER)

    artifacts = set()
    counts = []
    for i, panel in enumerate(PANEL_ORDER):
        row = ledger["panels"][i]
        fig = figure[i]
        old_couse = couse[ORIG_LABELS[i]]
        n_fine = fine[panel]["n"]
        n_geometry = geom[panel]["eligible_individuals"]
        n_I = fig["couse_n_bats"]
        overlap = row["ID_membership_overlap_counts"]
        tup = (
            n_fine, n_geometry, n_I, overlap["fine500_geometry"],
            overlap["fine500_I"], overlap["geometry_I"], overlap["all_three"]
        )
        assert tup == EXPECTED_COUNTS[i], f"Stored aggregate count drift in source panel index {i}"
        counts.append(tup)
        assert row["fine500_place_speed_turn_usable_n"] == n_fine
        assert row["native_or_terrain_V_S_evaluable_n"] == n_geometry
        assert row["fixed_event_couse_I_usable_n"] == n_I == old_couse["n"]
        assert row["reported_I_dyads"] == fig["couse_n_dyads"] == old_couse["dyads"]
        assert row["reported_I_matched_encounter_pairs"] == fig["couse_encounters"] == old_couse["encounters"]
        assert row["primary_time_tolerance_s"] == fig["couse_tolerance_s"] == old_couse["time"]
        assert row["primary_scope"] == fig["couse_scope"] == old_couse["scope"]
        assert row["cohort_qualified_ID_sets_crosschecked_in_original_artifacts"] is True
        assert row["native_and_terrain_geometry_identical_ID_sets"] is True
        assert row["set_inclusions"]["geometry_subset_of_fine500"] is True
        assert row["set_inclusions"]["I_subset_of_geometry"] is (i == 3)
        assert row["set_inclusions"]["I_subset_of_fine500"] is (i != 0)
        assert row["individual_level_joint_V_S_I_analysis_reported"] is False
        assert len(row["original_result_artifact_sources"]) == 4
        assert [x["analysis_role"] for x in row["original_result_artifact_sources"]] == list(ROLES)
        for original in row["original_result_artifact_sources"]:
            assert original["run_id"] == RUNS[original["analysis_role"]]
            assert isinstance(original["artifact_id"], int) and original["artifact_id"] not in artifacts
            artifacts.add(original["artifact_id"])
            assert re.fullmatch(r"[0-9a-f]{64}", original["artifact_zip_sha256"])
            assert original["artifact_name"] and original["expires_at"]

    summary = ledger["summary"]
    assert len(artifacts) == summary["original_artifact_zips_integrity_matched"] == 16
    assert summary["native_and_terrain_source_ID_sets_match_in_all_four_panels"]
    assert summary["geometry_ID_set_is_subset_of_fine500_in_all_four_panels"]
    assert summary["geometry_and_co_use_ID_intersection_by_panel"] == [5,3,5,5]
    assert summary["fine500_and_geometry_ID_intersection_by_panel"] == [8,5,6,9]
    assert summary["fine500_and_co_use_ID_intersection_by_panel"] == [10,6,6,5]
    assert summary["all_three_ID_intersection_by_panel"] == [5,3,5,5]
    assert summary["geometry_and_co_use_panel_indexed_overlap_total"] == 18
    assert summary["all_three_panel_indexed_overlap_total"] == 18
    assert summary["ID_level_effect_linkage_or_association_tested"] is False
    print("PASS source summary bytes and 16 source Actions artifact digest declarations")
    print("PASS stored original cohort-qualified aggregate overlaps: V/S ∩ I = [5,3,5,5]; all three = [5,3,5,5]")
    print("NOT VERIFIED BY DEFAULT: original ID-bearing ZIP bytes; use --artifact-dir for independent opt-in source cross-check")
    return ledger


def identity_from_individual_rows(individual_results: dict) -> set[tuple[str, str]]:
    result = set()
    for source_id, row in individual_results.items():
        assert isinstance(row["cohorts"], list) and len(row["cohorts"]) >= 1
        for cohort in row["cohorts"]:
            result.add((str(cohort), str(source_id)))
    return result


def zip_source(folder: Path, record: dict) -> dict:
    art_id = record["artifact_id"]
    name = folder / f"bat_source_{art_id}.zip"
    if not name.is_file():
        name = folder / f"{art_id}.zip"
    assert name.is_file(), f"Original source artifact {art_id} unavailable; no source-bat ID substitution permitted"
    assert hashlib.sha256(name.read_bytes()).hexdigest() == record["artifact_zip_sha256"], (
        "Original source artifact ZIP digest mismatch", art_id
    )
    with zipfile.ZipFile(name) as z:
        members = [x for x in z.namelist() if x.endswith(".json")]
        assert len(members) == 1, f"Expected exactly one original JSON member in ZIP {art_id}"
        obj = json.loads(z.read(members[0]))
    return obj


def source_zip_gate(folder: Path, ledger: dict) -> None:
    if not folder.is_dir():
        raise ValueError("Operator-provided artifact directory does not exist")
    matched = 0
    for i, row in enumerate(ledger["panels"]):
        source = {
            rec["analysis_role"]: zip_source(folder, rec)
            for rec in row["original_result_artifact_sources"]
        }
        panel = PANEL_ORDER[i]
        assert all(x["panel"] == panel for x in source.values()), "Original panel mismatch"
        fine = identity_from_individual_rows(source["fine500"]["observed"]["individual_results"])
        native = identity_from_individual_rows(source["native3d"]["observed"]["individual_results"])
        terrain = identity_from_individual_rows(source["terrain3d"]["observed"]["individual_results"])
        pairs = source["co_use"]["observed"]["dyads"]
        I = {(str(d["cohort"]), str(d[key])) for d in pairs
             for key in ("individual_a", "individual_b")}
        assert native == terrain, "Original native/terrain individual sets differ"
        assert len(I) == source["co_use"]["usable_individuals"]
        o = row["ID_membership_overlap_counts"]
        recalculated = (
            len(fine), len(terrain), len(I), len(fine & terrain),
            len(fine & I), len(terrain & I), len(fine & terrain & I)
        )
        assert recalculated == EXPECTED_COUNTS[i], f"Original ID intersection changed in panel {i}"
        assert o == {
            "fine500_geometry": len(fine & terrain),
            "fine500_I": len(fine & I),
            "geometry_I": len(terrain & I),
            "all_three": len(fine & terrain & I),
        }, f"Stored source overlap mismatch panel {i}"
        assert row["set_inclusions"] == {
            "geometry_subset_of_fine500": terrain <= fine,
            "I_subset_of_fine500": I <= fine,
            "I_subset_of_geometry": I <= terrain,
        }
        matched += len(terrain & I)
    assert matched == 18
    print("PASS ALL 16 exact original ZIP digests + source cohort-qualified individual-ID intersections [5,3,5,5]")
    print("NO source IDs or original position data printed, exported, copied into the repository or used for new hypothesis tests")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path,
                        help="Optional, authorized folder of 16 original ZIPs bat_source_<artifact_id>.zip; never redistributed")
    args = parser.parse_args()
    ledger = metadata_gate()
    if args.artifact_dir:
        source_zip_gate(args.artifact_dir, ledger)
