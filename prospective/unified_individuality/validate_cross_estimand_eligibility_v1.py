#!/usr/bin/env python3
"""Original data-free audit: source-V/S versus co-use-I bat n are not paired.

Matches the exact original immutable source-native V/S panel counts to the
source's corrected original co-use result sheet and integration figure summary.
Does NOT infer ID intersection or access raw third-party GPS or tag records.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIG=HERE/"figures"
HIST=HERE/"source_recovery"/"co_use_centered_history"
FINE=HERE/"source_recovery"/"fine500_history"/"result_summary_v1.json"
ORIGINAL_MD=HIST/"COUSE_VERTICAL_SEPARATION_RESULT_V1.md"
LEDGER=FIG/"FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json"
SOURCE={
    FIG/"FROZEN_FIGURE_DATA_V1.json":"b3f7b20136d028021a3c33a43c256e40ce91f677",
    FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json":"c1d37e42f72f59e5aba364daec9aef68b47778b6",
    ORIGINAL_MD:"d7b6054d95e7a6c27baf8e35a2f7377f628fe818",
    FINE:"a2960b45a1a7ea1e0e3beebe6eb799a47f114bed",
}
IDS=("hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016")
SOURCE_LABELS=("Hypsignathus monstrosus","Phyllostomus hastatus 2022","P. hastatus 2023","P. hastatus 2016")


def sha(path: Path) -> str:
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def original_md_rows() -> dict:
    source=ORIGINAL_MD.read_text(encoding="utf-8")
    rows={}
    for line in source.splitlines():
        if not line.startswith("| *"):
            continue
        v=[x.strip().strip("*") for x in line.strip().split("|")[1:-1]]
        if not v or v[0] not in SOURCE_LABELS:
            continue
        assert len(v)==11,(v,"Original 11-column co-use result row drift")
        label=v[0]
        assert label not in rows
        rows[label]={
            "time_tolerance_s":int(v[2].removesuffix(" s")),
            "scope":"all_space" if v[1]=="all-space" else "endpoint_excluded",
            "n":int(v[3]),
            "dyads":int(v[4]),
            "encounters":int(v[5].replace(",","")),
        }
    assert set(rows)==set(SOURCE_LABELS)
    return rows


def check():
    ledger=read_json(LEDGER)
    native=read_json(FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json")["panels"]
    fine=read_json(FINE)["panels"]
    figs=read_json(FIG/"FROZEN_FIGURE_DATA_V1.json")["terrain"]
    orig=original_md_rows()
    assert ledger["schema_version"]==2
    assert len(ledger["source"])==4
    expected={x["path"]:x["git_blob_sha1"] for x in ledger["source"]}
    assert expected=={
      "figures/FROZEN_FIGURE_DATA_V1.json":SOURCE[FIG/"FROZEN_FIGURE_DATA_V1.json"],
      "figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json":SOURCE[FIG/"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json"],
      "historical_release/post_freeze_extensions/3d_niche_partition/COUSE_VERTICAL_SEPARATION_RESULT_V1.md":SOURCE[ORIGINAL_MD],
      "historical_release/post_freeze_extensions/fine_place_kinematic_500m/result_summary_v1.json":SOURCE[FINE],
    }
    for f,originalsha in SOURCE.items():
        assert sha(f)==originalsha,(str(f),"source original Git blob drift")
    assert [r["panel"] for r in ledger["panels"]]==list(IDS)
    assert [x["panel"] for x in figs]==list(IDS)
    mismatches=0
    for k,panel in enumerate(IDS):
        row=ledger["panels"][k]
        data=figs[k]
        n_geom=native[panel]["eligible_individuals"]
        n_fine=fine[panel]["n"]
        n_i=data["couse_n_bats"]
        raw=orig[SOURCE_LABELS[k]]
        assert n_geom==row["native_or_terrain_V_S_evaluable_n"]
        assert n_fine==row["fine500_place_speed_turn_usable_n"]
        assert row["same_individual_id_set_verified_across_fine500_vs_geometry_vs_I"] is False
        assert n_i==row["fixed_event_couse_I_usable_n"]==raw["n"]
        assert data["couse_n_dyads"]==row["reported_I_dyads"]==raw["dyads"]
        assert data["couse_encounters"]==row["reported_I_matched_encounter_pairs"]==raw["encounters"]
        assert data["couse_tolerance_s"]==row["primary_time_tolerance_s"]==raw["time_tolerance_s"]
        assert data["couse_scope"]==row["primary_scope"]==raw["scope"]
        assert n_i-n_geom==row["n_co_use_minus_n_geometry"]
        assert row["same_individual_id_set_verified"] is False
        assert row["individual_level_joint_V_S_I_analysis_reported"] is False
        mismatches+=n_i!=n_geom
    assert mismatches==ledger["summary"]["count_panels_with_different_n"]==3
    assert ledger["summary"]["count_panels_with_same_n_but_unverified_identity"]==1
    assert ledger["summary"]["geometry_bat_n_vector"]==[8,5,6,9]
    assert ledger["summary"]["co_use_bat_n_vector"]==[11,6,6,5]
    assert ledger["summary"]["species"]==2
    assert ledger["summary"]["fine500_bat_n_vector"]==[19,23,11,9]
    assert ledger["summary"]["fine500_vs_geometry_n_different_panel_count"]==3
    assert ledger["summary"]["fine500_vs_couse_n_different_panel_count"]==4
    print("PASS exact original V/S vs corrected I numerical sources, 4 panels: 8/5/6/9 vs 11/6/6/5")
    print("PASS 3 original sample frames: matched-place speed×turn n=19/23/11/9, native V/S n=8/5/6/9, co-use I n=11/6/6/5")
    print("PASS 3/4 differing geometry/I n, 3/4 differing fine/geometry n, 4/4 differing fine/I n; no ID intersections reported")
    print("NOT ID-level linkage, per-bat V/I correlation, independent GPS/DEM rerun, or evidence of no physical avoidance")


if __name__=="__main__":
    check()
