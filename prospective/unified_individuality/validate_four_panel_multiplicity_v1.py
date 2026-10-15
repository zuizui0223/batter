#!/usr/bin/env python3
"""Recompute only a post-outcome Holm arithmetic sensitivity on frozen p-values.

No GPS/DEM inputs, no permutations, no new hypothesis tests, and no change to
original source-level inferential gates. Holm families are four original
study panels each for V_rel, S_rel and encounter co-use (three distinct
families). They were *not* prospectively declared as multisystem families.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
PANELS = ("hypsignathus", "phyllostomus_2022", "phyllostomus_2023", "phyllostomus_2016")


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def read(name: str) -> dict:
    return json.loads((FIG / name).read_text(encoding="utf-8"))


def holm_adjust(p_values: list[float]) -> list[float]:
    """Independent simple Holm step-down definition, arbitrary-dependence valid."""
    m = len(p_values)
    assert m == 4
    assert all(math.isfinite(p) and 0 <= p <= 1 for p in p_values)
    by_rank = sorted(range(m), key=lambda i: (p_values[i], i))
    corrected = [0.0] * m
    maximum_so_far = 0.0
    for rank, orig_index in enumerate(by_rank):
        maximum_so_far = min(1.0, max(maximum_so_far, (m - rank) * p_values[orig_index]))
        corrected[orig_index] = maximum_so_far
    return corrected


def validate() -> None:
    stored = read("FROZEN_FOUR_PANEL_MULTIPLICITY_V1.json")
    figure_path = FIG / "FROZEN_FIGURE_DATA_V1.json"
    v_path = FIG / "ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json"
    s_path = FIG / "ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json"
    assert stored["schema_version"] == 1
    assert tuple(stored["study_panels"]) == PANELS
    assert stored["family_size"] == len(PANELS) == 4
    expected_hashes = {
        figure_path: "b3f7b20136d028021a3c33a43c256e40ce91f677",
        v_path: "08631a0dce61cc47e12b2d32642c46b5759fe872",
        s_path: "e969698e2a594d2eeca2631d7473e598a8a8f371",
    }
    for path, blob in expected_hashes.items():
        assert git_blob(path) == blob, f"Source statistical values changed: {path}"
    pinfo = stored["generated_from_exact_source"]
    assert pinfo["figure_git_blob_sha1"] == expected_hashes[figure_path]
    assert pinfo["V_git_blob_sha1"] == expected_hashes[v_path]
    assert pinfo["S_git_blob_sha1"] == expected_hashes[s_path]

    terrain = read("FROZEN_FIGURE_DATA_V1.json")["terrain"]
    v_source = read("ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json")["panels"]
    s_source = read("ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json")["panels"]
    assert [r["panel"] for r in terrain] == list(PANELS)
    assert set(v_source) == set(s_source) == set(PANELS)
    families = {
        "V_rel_one_sided": [t["v_p_upper"] for t in terrain],
        "S_rel_two_sided": [t["s_p_two_sided"] for t in terrain],
        "co_use_one_sided": [t["couse_p_upper"] for t in terrain],
    }
    assert set(stored["families"]) == set(families)
    for i, panel in enumerate(PANELS):
        assert math.isclose(families["V_rel_one_sided"][i], v_source[panel]["p_upper"], abs_tol=1e-12)
        assert math.isclose(families["S_rel_two_sided"][i], s_source[panel]["S_p_two_sided"], abs_tol=1e-12)

    counts = {}
    for family, original_p in families.items():
        recalculated = holm_adjust(original_p)
        source_records = stored["families"][family]
        assert set(source_records) == set(PANELS)
        for panel, p_raw, p_holm in zip(PANELS, original_p, recalculated):
            row = source_records[panel]
            assert math.isclose(row["source_p"], p_raw, abs_tol=1e-12)
            assert math.isclose(row["holm_p"], p_holm, abs_tol=1e-12)
            assert row["nominal_p_le_0_05"] is (p_raw <= 0.05)
            assert row["holm_p_le_0_05"] is (p_holm <= 0.05)
        counts[family] = (sum(x <= .05 for x in original_p), sum(x <= .05 for x in recalculated))
    assert counts == {
        "V_rel_one_sided": (4, 4),
        "S_rel_two_sided": (1, 0),
        "co_use_one_sided": (1, 0),
    }
    summ = stored["summary"]
    assert (summ["V_rel_nominal_p_le_0_05"], summ["V_rel_holm_p_le_0_05"]) == (4, 4)
    assert (summ["S_rel_two_sided_nominal_p_le_0_05"], summ["S_rel_two_sided_holm_p_le_0_05"]) == (1, 0)
    assert (summ["co_use_nominal_p_le_0_05"], summ["co_use_holm_p_le_0_05"]) == (1, 0)
    assert summ["S_rel_positive_direction_nominal_support"] == 0
    assert math.isclose(stored["families"]["S_rel_two_sided"]["hypsignathus"]["holm_p"], .1448, abs_tol=1e-12)
    assert math.isclose(stored["families"]["co_use_one_sided"]["phyllostomus_2023"]["holm_p"], .0924, abs_tol=1e-12)
    print("PASS frozen original source hashes and independent Holm arithmetic for V_rel, S_rel and co-use")
    print("Within four displayed panels: V_rel 4/4 Holm<=.05; two-sided S_rel 0/4; co-use 0/4")
    print("NOT preregistration, a new animal-data analysis, an across-family adjustment, or proof of absent segregation")


if __name__ == "__main__":
    validate()
