#!/usr/bin/env python3
"""Offline replay-input integrity gate for archived original terrain 3D analysis.

Default: validate committed source-only metadata, NOT the original GPS/DEM bytes.
Optional --source-root: validate every recovered historical Git blob and reconcile
four original source contracts and DEM preflight against the inventory.
Optional --input-dir: stream-and-hash 4 GPS + 4 reference + 2 DEM bitstreams
supplied by a properly authorized operator. Never downloads, copies, decodes,
redistributes, or analyses GPS data or DEM elevations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LEDGER = HERE / "terrain_replay_input_manifest_v1.json"
CLOSURE = HERE / "terrain_source_closure_manifest_v1.json"
TERRAIN = ROOT / "figures" / "ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json"
NATIVE = ROOT / "figures" / "ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json"
RECEIPT_REL = "post_freeze_extensions/3d_niche_partition/original_terrain_dem_preflight_receipt_v1.json"
CONTRACT_REL = "post_freeze_extensions/3d_niche_partition/original_terrain_geometry_contract_v1.json"
PANELS = ("hypsignathus", "phyllostomus_2022", "phyllostomus_2023", "phyllostomus_2016")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\x00" + b).hexdigest()


def stream_hash(path: Path, algorithm: str) -> tuple[int, str]:
    h = hashlib.new(algorithm)
    size = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


def expected_bitstreams(d: dict) -> list[tuple[str, str, int, str, str]]:
    files = []
    for panel in d["panel_order"]:
        for role in ("gps", "reference"):
            r = d["panels"][panel][role]
            files.append((panel + "/" + role, r["expected_local_name"], r["size_bytes"], "md5", r["md5"]))
    for t in d["dem_tiles"]:
        files.append((t["tile"], t["expected_local_name"], t["gzip_bytes"], "sha256", t["gzip_sha256"]))
    return files


def validate_metadata(d: dict, closure: dict) -> None:
    assert d["schema_version"] == 1
    p = d["provenance"]
    assert p["repository"] == closure["original_repository"] == "zuizui0223/batter"
    assert p["source_commit"] == closure["historical_success_commit"]
    assert p["source_workflow"] == closure["historical_terrain_workflow_run_id"] == 36946126004
    assert p["native_workflow"] == 36881187913
    assert d["panel_order"] == list(PANELS)
    assert set(d["panels"]) == set(PANELS)
    expected = {x["path"]: x["git_blob_sha1"] for x in closure["files"]}
    assert len(expected) == len(closure["files"]) == 21
    assert p["contract_git_blob_sha1"] == expected[CONTRACT_REL]
    assert p["dem_preflight_receipt_git_blob_sha1"] == expected[RECEIPT_REL]
    assert d["geometry"]["permutation_B"] == 9999
    assert d["geometry"]["horizontal_grid_m"] == 500
    assert d["geometry"]["dem_grid_n"] == 3601
    assert d["geometry"]["panel_min_evaluable_individuals"] == 5
    assert d["geometry"]["pair_common_support_min_fixes_each"] == 50

    counts = {"gps": 0, "reference": 0}
    for panel in PANELS:
        row = d["panels"][panel]
        assert expected[row["contract_path"]] == row["contract_git_blob_sha1"]
        assert row["original_coordinate_row_count"] > 0
        assert row["original_target_session_count"] > 0
        assert len(row["dem_tiles"]) == 1
        for role in ("gps", "reference"):
            r = row[role]
            assert r["size_bytes"] > 0 and len(r["md5"]) == 32
            assert r["url"].startswith("https://datarepository.movebank.org/")
            assert r["expected_local_name"] == panel + "_" + role + ".csv"
            counts[role] += r["size_bytes"]
    tiles = d["dem_tiles"]
    assert [t["tile"] for t in tiles] == ["N00E014", "N09W083"]
    assert len(set(t["tile"] for t in tiles)) == 2
    for t in tiles:
        assert len(t["gzip_sha256"]) == 64
        assert t["url"].startswith("https://s3.amazonaws.com/elevation-tiles-prod/skadi/")
        assert t["grid_n"] == 3601
        assert t["expected_local_name"] == t["tile"] + ".hgt.gz"
    known = {t["tile"] for t in tiles}
    assert all(set(d["panels"][panel]["dem_tiles"]) <= known for panel in PANELS)
    total = d["expected_totals"]
    assert (total["gps_file_count"], total["reference_file_count"], total["dem_file_count"]) == (4, 4, 2)
    assert total["gps_bytes"] == counts["gps"] == 69505395
    assert total["reference_bytes"] == counts["reference"] == 43818
    assert total["dem_gzip_bytes"] == sum(t["gzip_bytes"] for t in tiles) == 19365315
    assert total["coordinate_rows"] == sum(d["panels"][p]["original_coordinate_row_count"] for p in PANELS) == 240042
    assert total["target_sessions"] == sum(d["panels"][p]["original_target_session_count"] for p in PANELS) == 521
    assert len(expected_bitstreams(d)) == 10
    status = d["status"]
    assert status["source_metadata_copied_from_exact_git_blobs"]
    assert not any(status[k] for k in ("downloaded_input_bytes_verified_in_this_audit",
                                      "download_permissions_verified",
                                      "historical_runtime_recreated",
                                      "full_empirical_replay_completed"))

    frozen = read_json(TERRAIN)
    native = read_json(NATIVE)
    assert frozen["workflow"]["run_id"] == p["source_workflow"]
    assert frozen["workflow"]["head_sha"] == p["source_commit"]
    assert native["workflow"]["run_id"] == p["native_workflow"]
    assert set(frozen["panels"]) == set(PANELS)
    assert set(native["panels"]) >= set(PANELS)
    print("PASS metadata: 4 panel contracts, 8 Movebank bitstreams, 2 DEM tiles; historical Git/provenance declarations consistent")
    print("NOT VERIFIED: actual GPS/DEM byte availability, original runtime and numerical replay")


def validate_source_tree(root: Path, d: dict, closure: dict) -> None:
    for entry in closure["files"]:
        file = root / entry["path"]
        assert file.is_file(), "Historical source file missing: " + str(file)
        assert git_blob_sha1(file) == entry["git_blob_sha1"], "Source blob drift: " + str(file)
    historical_contract = read_json(root / CONTRACT_REL)
    receipt = read_json(root / RECEIPT_REL)
    g = d["geometry"]
    assert historical_contract["geometry"]["horizontal_grid_m"] == g["horizontal_grid_m"]
    assert historical_contract["geometry"]["centered_height_edges_m"] == g["height_bin_edges_m"]
    assert historical_contract["geometry"]["alpha"] == 0.5
    assert historical_contract["geometry"]["panel_min_evaluable_individuals"] == g["panel_min_evaluable_individuals"]
    assert historical_contract["permutation"]["B"] == g["permutation_B"]
    assert historical_contract["dem"]["grid_n"] == g["dem_grid_n"]
    assert historical_contract["dem"]["interpolation"] == g["dem_interpolation"]
    assert receipt["status"] == "DEM_MAY_OPEN"
    assert receipt["numeric_dem_elevation_values_decoded"] is False
    assert receipt["unique_tiles"] == [
        {k: t[k] for k in ("tile", "url", "gzip_bytes", "gzip_sha256", "grid_n")}
        | {"decoded_elevation_values": False} for t in d["dem_tiles"]
    ]
    assert receipt["contract_sha256"] == hashlib.sha256((root / CONTRACT_REL).read_bytes()).hexdigest()
    for name in PANELS:
        row = d["panels"][name]
        con = read_json(root / row["contract_path"])
        src = con["source"]
        for role in ("gps", "reference"):
            for key in ("url", "bitstream_id", "size_bytes", "md5"):
                assert src[role][key] == row[role][key], (name, role, key)
        assert receipt["panels"][name]["source_gps_md5"] == row["gps"]["md5"]
        assert receipt["panels"][name]["coordinate_row_count"] == row["original_coordinate_row_count"]
        assert receipt["panels"][name]["target_session_count"] == row["original_target_session_count"]
        assert [t["tile"] for t in receipt["panels"][name]["tiles"]] == row["dem_tiles"]
    print("PASS original historical source tree: all 21 Git blobs + raw-input metadata crosswalk")


def validate_binary_directory(root: Path, d: dict) -> None:
    for label, filename, nbytes, algorithm, digest in expected_bitstreams(d):
        path = root / filename
        assert path.is_file(), "Missing authorized local input: " + str(path)
        size, observed_digest = stream_hash(path, algorithm)
        assert size == nbytes, f"{label} byte count mismatch: {size} != {nbytes}"
        assert observed_digest.lower() == digest.lower(), f"{label} {algorithm} mismatch"
    print("PASS supplied local source bitstreams: all 10 original size/checksum declarations match")
    print("NOT VERIFIED: legal redistribution, numerical GPS/DEM processing, environment equivalence or paper results")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", type=Path, help="Recovered exact historical repository tree (optional)")
    ap.add_argument("--input-dir", type=Path, help="Operator-provided permitted raw bytes, checked offline and never copied")
    ns = ap.parse_args()
    d, closure = read_json(LEDGER), read_json(CLOSURE)
    validate_metadata(d, closure)
    if ns.source_root is not None:
        validate_source_tree(ns.source_root, d, closure)
    if ns.input_dir is not None:
        validate_binary_directory(ns.input_dir, d)


if __name__ == "__main__":
    main()
