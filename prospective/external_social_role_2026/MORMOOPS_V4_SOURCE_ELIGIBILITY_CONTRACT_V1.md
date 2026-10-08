# Independent public Mormoops 3D flight dataset — source-only eligibility contract v1

## Purpose and evidence status
**PUBLIC EXTERNAL SOURCE ELIGIBILITY ONLY; NO BEHAVIOURAL OUTCOME OPENING.** This is a separate branch from the synthetic sentinel/practice chain, not a replacement for frozen JAE nor a relabeling of PR #72–87 synthetic results.

A genuinely new independent archive was published on 14 Sep 2026, Mendeley Data DOI **10.17632/mrnvkzrdsd.4**, associated with Pradhan, Mazar, Guillén-Servent & Yovel (2026), *Sensorimotor strategies for rapid leadership takeover in flying echolocating bats*, Communications Biology, published **22 Sep 2026**, DOI **10.1038/s42003-026-10966-7**. It studies `Mormoops megalophylla`, not the previously analyzed `Rhinolophus` or `P. hastatus`.

**Public repository claims (not yet verified within numeric files):**
- `TrackTable_All.mat`: raw tracks (~2.19 MB).
- `Switch_AnalysisTable.mat`: switch and non-switch kinematics.
- `RelativeTurningStartTime_AnalysisTable.mat`: temporal switching offsets.
- `Echolocation_AnalysisTable.mat`: sonar measures.
- Three .m scripts and an Audio Data folder.

Source pages:
- https://data.mendeley.com/datasets/mrnvkzrdsd/4
- https://www.nature.com/articles/s42003-026-10966-7
- Mendeley public API documentation: https://api.data.mendeley.com/datasets/{id}?version=4 and /datasets/{id}/files?version=4.

## New biological question: identity versus social role
The published paper finds followers turning earlier and flying faster before switching into the lead. That published result is **PRIOR ART, not the desired new result**. A different question is whether a bat's movement policy carries stable, individual-specific information after the instantaneous **lead/follow role** and partner geometry are accounted for. Specifically, does the same biological individual show portable kinematics across both social roles? Or does an apparently characteristic flight style follow the social role and surrounding geometry more than individual identity?

This requires genuine persistent individual IDs **across separate bouts**; one tracking-ID per flight is insufficient. In data without stable IDs, no individual-identity analysis is authorized. Even with IDs, a positive identity conditional association would be descriptive; social role is not randomized and role switching can depend on hidden performance or state.

A separate exploratory biologically important consequence would be whether the *same* individual modulates sonar output and turning speed simultaneously across role changes; this requires acoustic and 3D timestamps and a trustworthy emitter-to-track correspondence, not merely two separate published summary matrices.

## Sequential eligibility (FAIL CLOSED)
**Gate 0:** Exact dataset ID/DOI/version, file names, sizes and native SHA256 if published. Retrieve only publisher public metadata using a source-pinned API. Do not silently switch to older v1–v3 versions to obtain favorable support. API failure => `STOP_SOURCE_INACCESSIBLE`.

**Gate 1:** Raw .mat header structural check only (e.g. `scipy.io.whosmat` for MATLAB v5 or HDF5 dataset names/shapes for v7.3). If file access forbidden, `STOP_RAW_TRACK_UNAVAILABLE`. No scalar coordinate/velocity values are opened at Gate 1.

**Gate 2:** Confirm with variable/table metadata or published code documentation:
- exact track and event key join between `TrackTable_All.mat` and `Switch_AnalysisTable.mat`;
- timestamp resolution and coordinate units;
- within-recording bat index versus persistent across-recording individual identity;
- whether the same physical bat is identified in both Lead and Follow across at least two independent bouts;
- independent biological N and whether each bat has usable cross-role replicates;
- whether sonar calls are attributable to a known physical bat and time-aligned with its 3D track.

Strings such as 'Bat ID', 'TrackID' or 'bat1' in one trial **do not prove individual persistence**. If no documented stable identity mapping, immediately label `STOP_NO_STABLE_BAT_ID` and prohibit reinterpretation of within-event track index as individual.

**Gate 3 (only if all structural gates pass):** prospective outcome contract in a new, versioned branch, *before* opening new numeric role-switching values. Require at least **4 distinct stable physical bats**, each with **>=3 bouts leading and >=3 following** separated in time, and at least **16 held-out bouts total**. Split at whole-bout or whole-day level (never use adjacent overlapping position frames as independent replicates). Additional per-bat repeated-bout support if warranted MUST be set at the structural metadata stage only, before values. Compare within-identity vs donor forecasts after accounting for role, partner distance/bearing and session; identity labels permuted as whole biological units under a justified exchangeability design, not track frames. No direction/p/effect thresholds chosen after opening outcomes.

No claim of prospective confirmation for an earlier publication's already reported switching effects. No independent learning assignment, no path motor-module practice, and no adaptive fitness test here.

## Immediate script output
Machine report: source URL status, v4 receipt, file names/hash/size if accessible, .mat variable names/shapes only, published code filename/header field-name metadata, and an explicit three-valued eligibility: `PASS_SOURCE_STRUCTURAL_ONLY` / `STOP_NO_STABLE_BAT_ID` / `STOP_SOURCE_INACCESSIBLE`. Never infer biological identity from anonymous coordinates, trial numbers or audio recording names.

Do not use TinyFish, speculative URL substitutions, inaccessible file fallbacks or an unlogged prior version. JAE manuscript and the previously frozen 2026 lab paper remain untouched.
