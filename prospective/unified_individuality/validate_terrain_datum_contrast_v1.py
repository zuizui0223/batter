#!/usr/bin/env python3
"""Pure source-hash-guarded arithmetic audit of native and terrain-relative geometry.

Uses only existing 500m source result JSON and original source-input metadata.
No GPS, DEM, numerical permutation, animal analysis or inferential resampling.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
SRC = ROOT / "source_recovery"
NAMES = ("hypsignathus", "phyllostomus_2022",
         "phyllostomus_2023", "phyllostomus_2016")
SOURCE_BLOBS = {
    "ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json": "08631a0dce61cc47e12b2d32642c46b5759fe872",
    "ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json": "c1d37e42f72f59e5aba364daec9aef68b47778b6",
    "ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json": "e969698e2a594d2eeca2631d7473e598a8a8f371",
}


def data(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    buf = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(buf)).encode("ascii") + b"\x00" + buf).hexdigest()


def exact(a: float, b: float, label: str, *, tolerance: float = 1e-12) -> None:
    assert math.isclose(float(a), float(b), rel_tol=0, abs_tol=tolerance), (label, a, b)


def run() -> None:
    locked = data(FIG / "FROZEN_TERRAIN_DATUM_CONTRAST_V1.json")
    inputs = data(SRC / "terrain_replay_input_manifest_v1.json")
    manifest = data(SRC / "terrain_source_closure_manifest_v1.json")
    assert locked["schema_version"] == 1
    assert locked["panel_order"] == list(NAMES)
    assert locked["claim_status"].startswith("Descriptive sensitivity")
    assert locked["geometry"]["XY_grid_m"] == 500
    assert inputs["geometry"]["horizontal_grid_m"] == 500
    assert locked["historical_phase1"]["workflow_run"] == 36946126004
    assert locked["historical_phase2_S_rel_calibration"]["workflow_run"] == 36992380946
    assert locked["historical_phase1"]["commit"] == manifest["historical_success_commit"]

    source = {}
    for entry in locked["data_sources"]:
        name = Path(entry["path"]).name
        assert name in SOURCE_BLOBS, name
        path = FIG / name
        assert git_blob(path) == SOURCE_BLOBS[name] == entry["original_git_blob_sha1"]
        source[name] = data(path)
    assert set(source) == set(SOURCE_BLOBS)
    terrain = source["ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json"]["panels"]
    native = source["ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json"]["panels"]
    calibration = source["ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json"]["panels"]
    assert set(terrain) == set(calibration) == set(NAMES)
    assert [p["panel"] for p in locked["panels"]] == list(NAMES)

    original_sha = {row["path"]: row["git_blob_sha1"] for row in manifest["files"]}
    totals = {"Vplus": 0, "Vminus": 0, "Splus": 0, "Sminus": 0}
    for row in locked["panels"]:
        p = row["panel"]
        orig = native[p]
        terr = terrain[p]
        sci = calibration[p]
        inp = inputs["panels"][p]
        assert row["source_contract_blob_sha1"] == inp["contract_git_blob_sha1"]
        assert original_sha[inp["contract_path"]] == row["source_contract_blob_sha1"]
        assert row["source_vertical_field"] == inp["source_vertical_field"]
        assert row["source_vertical_field"] in ("height_above_msl", "height_above_ellipsoid")
        assert row["structurally_evaluable_animals"] == orig["eligible_individuals"]
        exact(row["native"]["horizontal_self_minus_other"], terr["H"], p + " H")
        exact(terr["H"], orig["self_oxy"] - orig["other_oxy"], p + " horizontal support")
        exact(row["native"]["conditional_vertical_self_minus_other"], orig["d_panel"], p + " native V")
        exact(row["native"]["conditional_vertical_self_minus_other"], terr["V_native"], p + " terrain-recorded native V")
        exact(row["terrain_relative"]["conditional_vertical_self_minus_other"], terr["V_rel"], p + " V_rel")
        exact(row["native"]["normalized_added_segregation_other_minus_self"], orig["other_r3d"]-orig["self_r3d"], p + " native S")
        exact(row["native"]["normalized_added_segregation_other_minus_self"], terr["S_native"], p + " terrain-recorded native S")
        exact(row["terrain_relative"]["normalized_added_segregation_other_minus_self"], terr["S_rel"], p + " S_rel")
        exact(row["terrain_relative"]["normalized_added_segregation_other_minus_self"], sci["S_rel"], p + " source calibrated S", tolerance=0.00002)
        exact(row["terrain_relative"]["fidelity_p_source"], terr["p_upper"], p+" V p")
        exact(row["terrain_relative"]["segregation_two_sided_p_source"], sci["S_p_two_sided"], p+" S p")
        dV = terr["V_rel"] - terr["V_native"]
        dS = terr["S_rel"] - terr["S_native"]
        exact(row["arithmetic_change_terrain_minus_native"]["conditional_vertical_fidelity"], dV, p+" delta V")
        exact(row["arithmetic_change_terrain_minus_native"]["added_segregation"], dS, p+" delta S")
        totals["Vplus" if dV > 0 else "Vminus"] += 1
        totals["Splus" if dS > 0 else "Sminus"] += 1
    assert totals == {"Vplus": 2, "Vminus": 2, "Splus": 2, "Sminus": 2}
    summary = locked["summary"]
    assert summary["vertical_fidelity_increases_after_terrain"] == 2
    assert summary["vertical_fidelity_decreases_after_terrain"] == 2
    assert summary["segregation_increases_after_terrain"] == 2
    assert summary["segregation_decreases_after_terrain"] == 2
    assert summary["source_S_rel_positive_supported_panels"] == 0
    assert summary["source_V_rel_supported_panels"] == 4
    assert summary["original_field_species"] == 2
    # No raw tracking-data event, height or terrain raster access.
    print("PASS source Git blobs, matched horizontal support and four original native/terrain V and S contrasts")
    print("PASS two increases / two decreases in V and S; altitude datum caveats identified")
    print("NOT a measured above-ground altitude, null-calibrated delta, ecological cause or new numerical rerun")


if __name__ == "__main__":
    run()
