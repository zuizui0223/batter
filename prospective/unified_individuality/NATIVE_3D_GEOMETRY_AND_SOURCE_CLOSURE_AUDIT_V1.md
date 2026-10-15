# Original native 3D overlap and historical workflow recovery

**Audit date:** 2026-10-15. **Tier:** historical result/source recovery and source-bound ecological interpretation; no new GPS data opening, numerical hypothesis test or independent replication.

## Original 500-m native 3D overlap

The authoritative original JAE native geometry analysis was successful in workflow run **36881187913**, commit **676ae76aec952a38410766577d51c5eca438a6c1**. We recovered the original summary without modification from the subsequent successful terrain workflow commit **819acc829d615485b57033f1ddcbebf64b4b49a0**; its original Git blob is **c1d37e42f72f59e5aba364daec9aef68b47778b6**. It is now byte-identically included as [original native overlap summary](figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json).

For each source-eligible repeated tracking-session pair using 500-m horizontal cells and session-centered native-height bins, the archived analysis defined

- O_XY = sum over horizontal cells c of min[P_a(c),P_b(c)];
- O_XYZ = sum over joint cells c,z of min[P_a(c,z),P_b(c,z)];
- O_Z|XY = horizontal-common-support-weighted vertical distribution overlap, used in the original self-versus-other identity primary;
- R_3D = 1 − O_XYZ/O_XY for each eligible session pair;
- S_native = other-animal mean R_3D − same-animal mean R_3D.

Original per-pair R_3D was averaged within animals. **Do not substitute one minus the ratio of pooled O_XYZ/O_XY means** for the original mean of ratios.

| Source panel | Eligible biological n | Self O_XY | Self O_XYZ | Other O_XY | Other O_XYZ | Self mean R_3D | Other mean R_3D | Native S |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H. monstrosus | 8 | 0.619 | 0.523 | 0.322 | 0.240 | 0.156 | 0.259 | +0.103 |
| P. hastatus 2022 | 5 | 0.549 | 0.507 | 0.334 | 0.309 | 0.075 | 0.058 | −0.017 |
| P. hastatus 2023 | 6 | 0.547 | 0.508 | 0.202 | 0.190 | 0.067 | 0.063 | −0.004 |
| P. hastatus 2016 | 9 | 0.511 | 0.425 | 0.208 | 0.181 | 0.185 | 0.315 | +0.130 |

The numbers are rounded for reading; complete original precision is stored in the recovered summary. The source-defined 500-m structural rule excluded Tadarida (n=4, below n=5 requirement) and Eidolon (no eligible individual). Four panels represent **two species**, not four independent taxa.

These source values are direct *joint-gridded* native-height 3D overlap of eligible session pairs; they are different from the **103 source-panel-record**, 684-dyad Figure S1 centered-height **one-dimensional profile-shape** intersection, which uses different individual sets and different self-derived horizontal weighting. They are also different from real-time same-cell co-use I and different from 3D space used by one lifetime individual. Do not subtract S1 O values from O_XYZ or call either the fraction of dietary niche shared.

## Link to terrain-corrected ecological inference

The original native geometry suggested descriptive additional vertical partitioning for H. monstrosus (S_native +0.103) and P. hastatus 2016 (S_native +0.130). After source-defined terrain elevation subtraction, original S_rel values were **−0.015806** and **+0.028895** in these respective panels; positive S_rel was not supported under its original label-permutation null in any of the four panels. Terrain-relative individual fidelity V_rel remained supported in 4/4. One 2023 co-use positive test remained an exception under its distinct 600-s all-space design. Terrain sensitivity is an observed geometric difference, **not** causal proof that terrain creates the strategy or that ecological competition is absent.

Original native workflow: https://github.com/zuizui0223/batter/actions/runs/36881187913

Original native result source: https://github.com/zuizui0223/batter/blob/676ae76aec952a38410766577d51c5eca438a6c1/post_freeze_extensions/3d_niche_partition/summary_v1.json

Original terrain workflow: https://github.com/zuizui0223/batter/actions/runs/36946126004

## Critical frozen-branch source-closure problem

The JAE rc2 frozen tree includes the original terrain runner (post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py) but does **not** include the imported same-directory modules run_v1.py and run_external_geometry_v1.py. Its directory also lacks the referenced native contract_v1.json and native summary_v1.json. Both source modules, the source contract, and original summary exist in the historical successful workflow commits.

Thus **the current frozen JAE rc2 checkout alone cannot replay that historic terrain runner unchanged**. This is a source-packaging gap, not evidence its recorded prior successful outputs are false. The correct full rerun baseline is the **historical successful execution commit with its original source data/bitstream/DEM checksums**, not source snippets reconstructed from memory.

Four exact historical source snapshots, without modifying either authoritative source branch, were archived under the integration-only source_recovery/native_3d_history directory:

| Historical source file | Git source commit | Exact Git blob SHA |
|---|---|---|
| run_v1.py | 676ae76aec952a38410766577d51c5eca438a6c1 | c08b442f97940eac3e90c1dac6e2de6d26010a7a |
| contract_v1.json | 676ae76aec952a38410766577d51c5eca438a6c1 | 5c76d0432e53ea7733216245f229d68ae0df1f77 |
| run_external_geometry_v1.py | 819acc829d615485b57033f1ddcbebf64b4b49a0 | c869a25c062b4bf5dc6b22e9f3e7fe03b69aeb30 |
| external_geometry_prediction_contract_v1.json | 819acc829d615485b57033f1ddcbebf64b4b49a0 | e1047891ab37cd0b46cdd180cc7ed8d815abce4b |

These historical snapshots are **not** themselves an asserted full successful rerun or licence for mixing code from different historical pipeline stages. CI checks only source integrity, statistical definitions and figure provenance. Source-data permissions, Python dependency/environment closure and full GPS/DEM rerun remain review tasks.

### Cross-study animal IDs

Official Movebank documentation (https://github.com/movebank/movebank-api-doc) states that animal and tag identifiers are unique only within a study, *not necessarily across separate studies*. Hence the exact two 2016/2022 repeated literal Phyllostomus labels in the Figure 5B profile archive do not prove two bats were re-identified across six years. Within-panel identity tests and same-original-cohort Figure S1 dyads are unaffected by this caution.

## One-commit historical source closure, audited 2026-10-15

The earlier four-file rescue has now been expanded to **21 exact historical source-code, configuration, panel-contract and checksum receipt files from one Git commit**, `819acc829d615485b57033f1ddcbebf64b4b49a0`, which generated the successful original terrain workflow 36946126004. No mixing of successive workflow versions is required for this new recovered source bundle.

The original JAE rc2 branch still holds byte-identical historical original driver `run_original_terrain_geometry_v1.py`, its terrain contract, DEM receipt, and core calibration/tag-source modules. Exactly the three required native-3D same-directory files `run_v1.py`, `run_external_geometry_v1.py` and `contract_v1.json` are absent from the frozen rc2 tree but present in the original success commit and this verified recovery package. The standalone historical recovery Python script reconstructs the full original relative file paths and checks all 21 original Git blob SHA-1 values. It also statically checks Python/JSON syntax and local script import closure, not the biological outcome.

- [Source closure manifest](source_recovery/terrain_source_closure_manifest_v1.json) and [recoverable source-only script](source_recovery/recover_terrain_source_closure_v1.py).
- [Full source closure and limitations](HISTORICAL_TERRAIN_SOURCE_CLOSURE_V1.md).
- [Successful code-only recovery CI 38685340549](https://github.com/zuizui0223/batter/actions/runs/38685340549).
- Independently checked source-only ZIP: 21 original files + manifest, SHA256 `27e1f7cd44e3aa367f150aef8f608a7cec35a73a8ef922c0f2950d0059f13ce1`, with no Movebank raw observations or DEM tiles.

**Inference limit unchanged:** this resolves a **Git/source-code packaging gap** only. There is **no claim** that an independent full GPS/DEM and 9,999-permutation rerun has passed, that raw third-party data may be redistributed, or that the original inference changed. Such a rerun requires original source data and DEM checksum access and a historically comparable Python environment.

## Scope of new presentation

[Figure S2](figures/FIGURE_S2_NATIVE_HORIZONTAL_AND_JOINT_3D_OVERLAP_V1.svg) illustrates the recovered original native O_XY and O_XYZ source comparisons only. Its reproducible [source renderer](figures/render_original_native_3d_overlap_s2_v1.cjs) rejects a change in the pinned original source blob. It has **no new inferential p-values, confidence intervals, independent samples or ecological mechanism assignments**.
