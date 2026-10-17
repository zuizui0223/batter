#!/usr/bin/env python3
"""Check exact source identity for the *second* (S_rel) historical calibration.

Default mode is network-free and checks both pinned manifests and the
byte-identical frozen result summary. --verify-source-bytes requests ONLY the
historical calibration Python source and its JSON contract from public GitHub,
hash-verifies their Git blobs and inspects their definitions; it does not
download GPS/tag data, DEM elevations, or rerun the empirical null distribution.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "partitioning_s_calibration_provenance_v1.json"
CLOSURE = HERE / "terrain_source_closure_manifest_v1.json"
RESULT = ROOT / "figures" / "ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json"
STAGE_B_COMMIT = "d0193c1a0da93cda2d1e711039d0eb3b93eafce7"
S_RESULT_BLOB = "e969698e2a594d2eeca2631d7473e598a8a8f371"
PANELS = {"hypsignathus", "phyllostomus_2022", "phyllostomus_2023", "phyllostomus_2016"}


def git_blob(b: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\x00" + b).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metadata_gate() -> dict:
    p, a, result = load(SOURCE), load(CLOSURE), load(RESULT)
    assert p["schema_version"] == 1
    assert p["stage_a"]["source_commit"] == a["historical_success_commit"]
    assert p["stage_a"]["workflow_run"] == a["historical_terrain_workflow_run_id"] == 36946126004
    b = p["stage_b"]
    assert b["source_commit"] == STAGE_B_COMMIT
    assert b["workflow_run"] == 36992380946
    assert b["permutations_requested_per_panel"] == 9999
    assert b["resulting_frozen_calibration_blob_sha1"] == S_RESULT_BLOB
    assert len(b["new_source_files"]) == 2
    assert len(b["source_dependencies_reused_unchanged_from_stage_a"]) == 5
    expected = {entry["path"]: entry["git_blob_sha1"] for entry in a["files"]}
    extra = {entry["path"]: entry["git_blob_sha1"] for entry in b["new_source_files"]}
    assert extra == {
        "post_freeze_extensions/3d_niche_partition/run_partitioning_s_calibration_v1.py":
            "9aba94c6a08a289db50f21d553da866f7641feb2",
        "post_freeze_extensions/3d_niche_partition/partitioning_calibration_contract_v1.json":
            "1dfc8625de021f5a7bc02167fba59650b0e29b19",
    }
    assert not (set(extra) & set(expected)), "Post-outcome S-calibration sources must not be misdated as stage A"
    for x in b["source_dependencies_reused_unchanged_from_stage_a"]:
        assert expected[x["path"]] == x["git_blob_sha1"], x["path"]
    assert git_blob(RESULT.read_bytes()) == S_RESULT_BLOB
    assert result["workflow_run"] == b["workflow_run"]
    assert set(result["panels"]) == PANELS
    assert all("S_p_two_sided" in x and "S_null_mean" in x for x in result["panels"].values())
    assert sum(r["S_rel"] > 0 and r["S_p_two_sided"] <= 0.05 for r in result["panels"].values()) == 0
    assert result["panels"]["hypsignathus"]["S_p_two_sided"] == 0.0362
    assert p["current_evidence"]["historical_rerun_not_performed"] is True
    assert p["current_evidence"]["original_GPS_DEM_inputs_not_retrieved"] is True
    print("PASS source-metadata/provenance: stage A terrain geometry and separate stage B S_rel calibration")
    print("PASS original stage B frozen result Git blob, 4-panel S_rel null summary and boundaries")
    print("NOT CHECKED: current source bitstreams, 9,999-permutation replay, independent GPS/DEM rerun")
    return p


def source_byte_gate(p: dict) -> None:
    got = {}
    for record in p["stage_b"]["new_source_files"]:
        rel = record["path"]
        url = "https://raw.githubusercontent.com/zuizui0223/batter/" + STAGE_B_COMMIT + "/" + rel
        req = urllib.request.Request(url, headers={"User-Agent": "batter-s-calibration-source-check/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            assert response.status == 200
            raw = response.read()
        assert len(raw) < 100000
        assert git_blob(raw) == record["git_blob_sha1"], ("Original stage B Git blob drift", rel)
        if rel.endswith(".py"):
            ast.parse(raw.decode("utf-8"), filename=rel)
            text = raw.decode("utf-8")
            assert "null_s" in text and "rng.permutation" in text
            assert "p_two_sided_about_null_mean" in text
        else:
            contract = json.loads(raw)
            assert contract["s_calibration"]["B"] == 9999
            assert "label permutation" in contract["s_calibration"]["null"]
            assert contract["s_calibration"]["two_sided_center"] == "null_mean"
        got[rel] = record["git_blob_sha1"]
    print("PASS exact original phase B 2 code/contract Git blobs fetched and structurally checked")
    print("NO field data, DEM elevations or empirical nulls downloaded/re-executed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-source-bytes", action="store_true", help="Fetch only 2 original PUBLIC GitHub source files")
    args = ap.parse_args()
    manifest = metadata_gate()
    if args.verify_source_bytes:
        source_byte_gate(manifest)
