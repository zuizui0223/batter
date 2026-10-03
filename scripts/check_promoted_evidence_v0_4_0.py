#!/usr/bin/env python3
"""Guard the promoted post-freeze evidence bundled with JAE v0.4.0."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

REQUIRED=[
    "manuscript/PROMOTED_EVIDENCE_PROVENANCE_V0_4_0.md",
    "manuscript/promoted_evidence_provenance_v0_4_0.json",

    "post_freeze_extensions/3d_niche_partition/ORIGINAL_TERRAIN_GEOMETRY_CONTRACT_V1.md",
    "post_freeze_extensions/3d_niche_partition/ORIGINAL_TERRAIN_GEOMETRY_RESULT_V1.md",
    "post_freeze_extensions/3d_niche_partition/original_terrain_dem_preflight_receipt_v1.json",
    "post_freeze_extensions/3d_niche_partition/original_terrain_geometry_contract_v1.json",
    "post_freeze_extensions/3d_niche_partition/original_terrain_geometry_summary_v1.json",
    "post_freeze_extensions/3d_niche_partition/run_original_terrain_dem_preflight_v1.py",
    "post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py",

    "post_freeze_extensions/3d_niche_partition/COUSE_VERTICAL_SEPARATION_CONTRACT_V1.md",
    "post_freeze_extensions/3d_niche_partition/COUSE_VERTICAL_SEPARATION_RESULT_V1.md",
    "post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json",
    "post_freeze_extensions/3d_niche_partition/couse_vertical_separation_summary_v1.json",
    "post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py",
    "post_freeze_extensions/3d_niche_partition/COUSE_RUN_CORRECTION_AUDIT_V1.md",
    "post_freeze_extensions/3d_niche_partition/COUSE_NULL_AMENDMENT_V1.md",
    "post_freeze_extensions/3d_niche_partition/COUSE_PREFLIGHT_RECEIPT_V1.md",
    "post_freeze_extensions/3d_niche_partition/couse_preflight_receipt_v1.json",
    "post_freeze_extensions/3d_niche_partition/COUSE_PRIMARY_ENCOUNTER_RECEIPT_V1.md",
    "post_freeze_extensions/3d_niche_partition/couse_primary_encounter_receipt_v1.json",
    "post_freeze_extensions/3d_niche_partition/COUSE_SHIFTABILITY_RECEIPT_V1.md",
    "post_freeze_extensions/3d_niche_partition/couse_shiftability_receipt_v1.json",

    "post_freeze_extensions/3d_niche_partition/PARTITIONING_CALIBRATION_CONTRACT_V1.md",
    "post_freeze_extensions/3d_niche_partition/PARTITIONING_CALIBRATION_RESULT_V1.md",
    "post_freeze_extensions/3d_niche_partition/PARTITIONING_I_COMPATIBILITY_RESULT_V1.md",
    "post_freeze_extensions/3d_niche_partition/partitioning_calibration_contract_v1.json",
    "post_freeze_extensions/3d_niche_partition/partitioning_calibration_summary_v1.json",
    "post_freeze_extensions/3d_niche_partition/partitioning_i_compatibility_summary_v1.json",
    "post_freeze_extensions/3d_niche_partition/run_partitioning_s_calibration_v1.py",

    "post_freeze_extensions/temporal_persistence_1d_four_panel/RESULT_V1.md",
    "post_freeze_extensions/temporal_persistence_3d_three_panel/RESULT_V1.md",
    "post_freeze_extensions/temporal_persistence_7d_two_panel/RESULT_V1.md",
    "post_freeze_extensions/fine_place_kinematic_500m/RESULT_V1.md",
    "post_freeze_extensions/fine_place_same_night_four_panel/RESULT_V1.md",
    "post_freeze_extensions/movement_state_conditioning/RESULT_V1.md",
    "post_freeze_extensions/resource_patch_fidelity/RESULT_V1.md",

    "post_freeze_extensions/strategy_maintenance/CONTRACT_V1.md",
    "post_freeze_extensions/strategy_maintenance/WIND_SUPPORT_PREFLIGHT_RESULT_V1.md",
    "post_freeze_extensions/strategy_maintenance/REACTION_NORM_CONTRACT_V1.md",
    "post_freeze_extensions/strategy_maintenance/REACTION_NORM_STRUCTURAL_PREFLIGHT_RESULT_V2.md",
    "post_freeze_extensions/strategy_maintenance/STRATEGY_MAINTENANCE_SYNTHESIS_V1.md",
    "post_freeze_extensions/strategy_maintenance/wind_support_summary_v1.json",
    "post_freeze_extensions/strategy_maintenance/reaction_norm_structural_preflight_summary_v2.json",
    "post_freeze_extensions/strategy_maintenance/source_schema_preflight_v1.py",
    "post_freeze_extensions/strategy_maintenance/wind_support_preflight_v1.py",
    "post_freeze_extensions/strategy_maintenance/reaction_norm_structural_preflight_v1.py",

    "post_freeze_extensions/NYCTALUS_VALIDATION_HISTORY_V1.md",
    "post_freeze_extensions/HIPPOSIDEROS_PRIMARY_CLOSEOUT_V1.md",
    "post_freeze_extensions/small_panel_generality/PRIMARY_RESULT_V1.md",
    "post_freeze_extensions/small_panel_generality/primary_result_v1.json",
    "post_freeze_extensions/small_panel_generality/contract_v1.json",
    "post_freeze_extensions/pteropus_terrain_audit/TERRAIN_AUDIT_RESULT_V1.md",
    "post_freeze_extensions/pteropus_terrain_audit/terrain_audit_result_v1.json",
    "post_freeze_extensions/pteropus_terrain_audit/contract_v1.json",
    "results/external_boundary_v0_4_0.csv",
]

REQUIRED_WORKFLOWS=[
    ".github/workflows/original-terrain-dem-preflight-v1.yml",
    ".github/workflows/original-terrain-geometry-v1.yml",
    ".github/workflows/couse-preflight-v1.yml",
    ".github/workflows/couse-shiftability-v1.yml",
    ".github/workflows/couse-vertical-separation-v1.yml",
    ".github/workflows/partitioning-s-calibration-v1.yml",
    ".github/workflows/strategy-maintenance-source-schema-preflight-v1.yml",
    ".github/workflows/strategy-maintenance-wind-support-preflight-v1.yml",
    ".github/workflows/strategy-maintenance-reaction-norm-structural-preflight-v1.yml",
]

FORBIDDEN_GLOBS=[
    "post_freeze_extensions/3d_niche_partition/P2023_*",
    "post_freeze_extensions/3d_niche_partition/p2023_*",
    "post_freeze_extensions/3d_niche_partition/EXTERNAL_*",
    "post_freeze_extensions/3d_niche_partition/external_*",
    "post_freeze_extensions/3d_niche_partition/PTEROPUS_*",
    "post_freeze_extensions/3d_niche_partition/pteropus_*",
    "post_freeze_extensions/3d_niche_partition/ECOLOGY_TO_GEOMETRY_*",
    "post_freeze_extensions/3d_niche_partition/SPATIAL_SOLUTION_*",
    "post_freeze_extensions/3d_niche_partition/SPECIALIZATION_PARTITIONING_PHASE_SPACE_*",
    "post_freeze_extensions/3d_niche_partition/RESOURCE_BEHAVIOUR_*",
]

FORBIDDEN_EXACT=[
    "post_freeze_extensions/strategy_maintenance/run_reaction_norm_v1.py",
    "post_freeze_extensions/strategy_maintenance/reaction_norm_results",
]

def main()->int:
    failures=[]
    for p in REQUIRED+REQUIRED_WORKFLOWS:
        if not (ROOT/p).is_file():
            failures.append(f"missing promoted evidence file: {p}")

    for pat in FORBIDDEN_GLOBS:
        hits=list(ROOT.glob(pat))
        if hits:
            failures.append(f"excluded exploratory family leaked into RC: {pat} -> {[str(x.relative_to(ROOT)) for x in hits[:5]]}")

    for p in FORBIDDEN_EXACT:
        if (ROOT/p).exists():
            failures.append(f"reaction-norm numeric outcome path must remain absent: {p}")

    idx_path=ROOT/"manuscript"/"promoted_evidence_provenance_v0_4_0.json"
    if idx_path.is_file():
        idx=json.loads(idx_path.read_text(encoding="utf-8"))
        if idx.get("numeric_vertical_reaction_norm_opened") is not False:
            failures.append("provenance index does not record numeric_vertical_reaction_norm_opened=false")
        rn=idx.get("promoted_families",{}).get("continuous_reaction_norm_structural",{})
        if rn.get("run_id")!=37090689460:
            failures.append("reaction-norm structural run id drifted")

    rn_summary=ROOT/"post_freeze_extensions"/"strategy_maintenance"/"reaction_norm_structural_preflight_summary_v2.json"
    if rn_summary.is_file():
        x=json.loads(rn_summary.read_text(encoding="utf-8"))
        if x.get("numeric_vertical_opened") is not False:
            failures.append("reaction-norm structural summary says numeric vertical was opened")
        if x.get("vertical_outcome_may_open") is not False:
            failures.append("reaction-norm structural summary unexpectedly allows vertical opening")
        if x.get("decision")!="STOP":
            failures.append("reaction-norm structural summary decision is not STOP")

    terrain=(ROOT/"post_freeze_extensions/3d_niche_partition/ORIGINAL_TERRAIN_GEOMETRY_RESULT_V1.md")
    if terrain.is_file() and "36946126004" not in terrain.read_text(encoding="utf-8"):
        failures.append("terrain result missing authoritative workflow 36946126004")
    couse=(ROOT/"post_freeze_extensions/3d_niche_partition/COUSE_VERTICAL_SEPARATION_RESULT_V1.md")
    if couse.is_file() and "36953712597" not in couse.read_text(encoding="utf-8"):
        failures.append("co-use result missing authoritative corrected workflow 36953712597")
    ny=(ROOT/"post_freeze_extensions/NYCTALUS_VALIDATION_HISTORY_V1.md")
    if ny.is_file():
        t=ny.read_text(encoding="utf-8")
        if "p = **0.1224**" not in t or "frozen verdict = **FAIL**" not in t:
            failures.append("Nyctalus first prospective FAIL is not preserved")
        if "authoritative prospective external-validation result" not in t:
            failures.append("Nyctalus history does not identify first result as authoritative")

    hip=(ROOT/"post_freeze_extensions/HIPPOSIDEROS_PRIMARY_CLOSEOUT_V1.md")
    if hip.is_file():
        t=hip.read_text(encoding="utf-8")
        if "p(null >= observed): **0.8616**" not in t or "frozen verdict: **FAIL**" not in t:
            failures.append("Hipposideros prospective FAIL drifted")

    small=(ROOT/"post_freeze_extensions/small_panel_generality/primary_result_v1.json")
    if small.is_file():
        x=json.loads(small.read_text(encoding="utf-8"))
        txt=json.dumps(x)
        if "0.4419" not in txt or "0.0001" not in txt:
            failures.append("small-panel Myotis/Pteropus primary results drifted")

    pter=(ROOT/"post_freeze_extensions/pteropus_terrain_audit/terrain_audit_result_v1.json")
    if pter.is_file():
        txt=pter.read_text(encoding="utf-8")
        if "0.03231" not in txt or "0.0023" not in txt:
            failures.append("Pteropus terrain-adjusted diagnostic drifted")

    ext=(ROOT/"results/external_boundary_v0_4_0.csv")
    if ext.is_file():
        t=ext.read_text(encoding="utf-8")
        for phrase in ("0.1224","0.8616","0.4419","0.0001","0.0023"):
            if phrase not in t:
                failures.append(f"external boundary CSV missing frozen value {phrase}")

    part=(ROOT/"post_freeze_extensions/3d_niche_partition/PARTITIONING_CALIBRATION_RESULT_V1.md")
    if part.is_file() and "36992380946" not in part.read_text(encoding="utf-8"):
        failures.append("partitioning result missing authoritative workflow 36992380946")

    if failures:
        print("Promoted-evidence provenance guard: BLOCKED")
        for x in failures: print(f" - {x}")
        return 1

    print("Promoted-evidence provenance guard: PASS")
    print(f"Required evidence files: {len(REQUIRED)}")
    print(f"Required workflows: {len(REQUIRED_WORKFLOWS)}")
    print("Excluded exploratory 3-D families: absent")
    print("Reaction-norm numeric vertical outcome: unopened / absent")
    print("External boundary sequence retained: Nyctalus/Hipposideros/Myotis FAIL; Pteropus PASS + terrain diagnostic")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
