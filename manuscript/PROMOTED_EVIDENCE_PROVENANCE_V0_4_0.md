# Promoted evidence provenance — JAE v0.4.0

## Purpose

This index identifies the post-freeze evidence families that are **actually promoted into the v0.4.0 manuscript** and therefore must travel with the release candidate.

It is a provenance inventory, not a new analysis.

## Promoted evidence families

### 1. Terrain-relative vertical-strategy fidelity

Canonical files:
- `post_freeze_extensions/3d_niche_partition/ORIGINAL_TERRAIN_GEOMETRY_CONTRACT_V1.md`
- `post_freeze_extensions/3d_niche_partition/ORIGINAL_TERRAIN_GEOMETRY_RESULT_V1.md`
- `post_freeze_extensions/3d_niche_partition/original_terrain_dem_preflight_receipt_v1.json`
- `post_freeze_extensions/3d_niche_partition/original_terrain_geometry_contract_v1.json`
- `post_freeze_extensions/3d_niche_partition/original_terrain_geometry_summary_v1.json`
- `post_freeze_extensions/3d_niche_partition/run_original_terrain_dem_preflight_v1.py`
- `post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py`

Authoritative workflow: **36946126004**.

Promoted claim:
- terrain-relative vertical-strategy fidelity is supported in 4/4 structurally evaluable fruit-bat panels.

### 2. Synchronous co-use vertical separation

Canonical files:
- `COUSE_VERTICAL_SEPARATION_CONTRACT_V1.md`
- `COUSE_VERTICAL_SEPARATION_RESULT_V1.md`
- `couse_vertical_separation_contract_v1.json`
- `couse_vertical_separation_summary_v1.json`
- `run_couse_vertical_separation_v1.py`
- `COUSE_RUN_CORRECTION_AUDIT_V1.md`
- `COUSE_NULL_AMENDMENT_V1.md`
- frozen preflight / encounter / shiftability receipts.

Authoritative corrected workflow: **36953712597**.

Promoted claim:
- three of four panels do not show additional synchronous vertical separation;
- *P. hastatus* 2023 is the sole supported exception under its coarser 600-s/all-space design.

### 3. Partitioning calibration

Canonical files:
- `PARTITIONING_CALIBRATION_CONTRACT_V1.md`
- `PARTITIONING_CALIBRATION_RESULT_V1.md`
- `PARTITIONING_I_COMPATIBILITY_RESULT_V1.md`
- machine-readable contract/summary JSON files;
- `run_partitioning_s_calibration_v1.py`.

Authoritative S-calibration workflow: **36992380946**.

Promoted claim:
- supported **positive** terrain-relative added segregation S_rel occurs in 0/4 panels;
- for the three panels without supported co-use separation, dyad-resampling positive upper compatibility bounds are approximately 1–2 m.

### 4. Temporal maintenance

Already present in the RC:
- `post_freeze_extensions/temporal_persistence_1d_four_panel/`
- `post_freeze_extensions/temporal_persistence_3d_three_panel/`
- `post_freeze_extensions/temporal_persistence_7d_two_panel/`.

Authoritative workflows:
- >=1 day: **36539006089**
- >=3 days: **36539572278**
- >=7 days: **36562703089**

Promoted claim:
- persistence in 4/4, 3/3 and 2/2 structurally evaluable panels at >=1, >=3 and >=7 days, respectively.

### 5. Fine place × kinematic context

Already present:
- `post_freeze_extensions/fine_place_kinematic_500m/`
- `post_freeze_extensions/fine_place_same_night_four_panel/`
- `post_freeze_extensions/movement_state_conditioning/`
- `post_freeze_extensions/resource_patch_fidelity/`.

Authoritative workflows:
- 500-m place × speed × turning: **36519747717**
- 2-km place × kinematic × same-night: **36518735021**
- broad movement-state conditioning: **36509985627**
- simple patch-fidelity driver test: **36508617613**

Promoted interpretation:
- coarse place, broad movement state, common nightly context and simple patch-fidelity strength are each insufficient as general explanations.

### 6. Strategy-maintenance / ERA5 reaction-norm structural stop

Canonical files:
- `post_freeze_extensions/strategy_maintenance/CONTRACT_V1.md`
- `WIND_SUPPORT_PREFLIGHT_RESULT_V1.md`
- `REACTION_NORM_CONTRACT_V1.md`
- `REACTION_NORM_STRUCTURAL_PREFLIGHT_RESULT_V2.md`
- `STRATEGY_MAINTENANCE_SYNTHESIS_V1.md`
- corresponding machine-readable summaries and preflight scripts.

Wind-support workflow: **37090059505**.  
Continuous reaction-norm structural workflow: **37090689460**.

Promoted claim:
- the broad ERA5-wind reaction-norm mechanism is **unadjudicated**;
- the continuous structural gate failed because 2023 retained 7 evaluable individuals versus 8 required;
- **no numeric vertical reaction-norm outcome was opened**.

## Explicitly not promoted into the RC

The following exploratory families are intentionally excluded from the release candidate because they are not needed for the manuscript claim:

- P2023 co-use localization refinements;
- P2023 microplace / temporal-gradient follow-ups;
- external geometry candidate panels;
- Pteropus terrain-geometry contrast;
- ecology-to-geometry synthesis drafts;
- spatial phase-space exploratory figures;
- resource/social-metadata follow-up searches.

Their absence is deliberate and prevents the submission package from silently broadening the evidence base after the claim was frozen.

## Claim boundary

The RC contains all files necessary to audit the promoted post-freeze evidence, but it does not convert those diagnostics into independent preregistered confirmation.

The final synthesis remains:

> **Persistent individual vertical strategies can remain predictive without requiring mutually exclusive vertical niches.**

Personal solution reuse is a bounded explanatory framework, not a directly identified proximate mechanism.
