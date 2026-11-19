# H1 — can social cues update personal knowledge across bats?

**2026-11-19, v3: prospective external validation design + source-backed aggregates + known-truth estimator falsification. No novel multi-species biological effect is claimed.**

All work remains separate from frozen batter JAE inferential results and from `main`.

## Completed / independently auditable work

1. **Theory seed, not an external test:** 2022 review Table 2 extracted into 35 rows, 29 explicitly named bat species plus one pooled-taxonomy row. Twenty rows have one of four strategies; the subset of 25 with measurable persistence and information-use site matches the review's framework by construction. Do NOT count this as replication.
2. **Original paper ledger:** 12 targeted context/receiver observations, eight named taxa, six original-study clusters from 2024–2026. No new independent fully measured cases yet meet the classical four-strategy global phylogenetic response test. No systematic worldwide sampling frame/absence denominator.
3. **New prior-art guardrail:** 2019 experimental study (Lewanzik et al.) already tested 24 emitted-signal×recipient group combinations at 12 lakes, not 24 independent recipient species, and ecological context modulated cue responses. Four recipient groups had negative coefficients of pre-playback activity on the response defined as playback-minus-pre-playback activity; 3 species + one mixed NEV group, not four separate studies.
4. **Known-truth mathematical gate:** In a stationary no-social-effect world, fitting (during-pre) ~ pre yields slope rho-1; all 128 simulation replicates at each of rho=0,0.5,0.9 had negative slopes, reproducing the negative-baseline *sign* with true social competition=0. The observed 2019 negative signs therefore cannot alone identify an actual social-cost effect; this does not disprove the published interpretation or invalidate cue-specific results.
5. **Sex-specific actual published model contrasts:** 2026 Glossophaga paper reported male/female playback-vs-silent flower-visit RRs 0.17/6.57 for alert and 0.73/2.58 for benign calls (16 biological bats; 8 each). Descriptive female/male ratio-of-rate-ratios =38.65 alert, 3.53 benign. Both effects belong to ONE prior study, not novel bat evidence or independent replicated species.
6. **2024 author-original data QA:** Rousettus odor intervention 10 naive visitor IDs out of 56 naive bats (17.86%); source total cell 22 rather than 23 on 19 July 2020, no effect on naive denominator. This was a count verification, not new cue information/memory mechanism.
7. **Automated validation:** isolated GitHub Action checks source-unit boundaries, deterministic 2019/2026 reconstruction, known-truth null, and analysis STOP gates (6 unit tests PASS).
   - [Latest validated negative-control run](https://github.com/zuizui0223/batter/actions/runs/44449278361)
   - [Source tracking](https://doi.org/10.1111/1365-2656.12989) and [2026 original](https://doi.org/10.1111/nyas.70427)

## Primary scientific decision

The publication-grade novelty cannot be merely 'social information is context dependent' or 'fruits mean personal knowledge and insects mean social knowledge'. Those are prior art or overly restrictive, respectively.

**Testable next question**: Does the *causal* effect of a given acoustic or social cue on foraging decisions change with independently measured baseline resource/social context (receiver sex, competitive ability and actual alternative patch opportunity), beyond regression-to-the-mean and method-specific observation effects?

Valid proposed treatment interaction: difference in during-cue and randomized time-matched silent-control response, conditional on a pre-treatment activity stratum; the raw baseline shared with a difference-score outcome must not be confused with actual crowding moderation. A 0-buzz playback that contains search calls is **not** a true silent control.

**STOP** global H1 effect fit / H3 individual memory tradeoff: sources have incompatible outcome units (activity change in bat-seconds/min vs flower-visit RR vs tree visitation), and no controlled multi-study comparable summary/detection-negative frame yet.

## Files

- `H1_PREREG_AND_FEASIBILITY_V1.md` — initial hypotheses, gates, source selection
- `H1_CODING_DICTIONARY_V1.md` — independent blinded coding dictionary
- `H1_V2_INFORMATION_CHANNEL_AMENDMENT.md` — when-versus-where hypothesis, source provenance
- `REVIEW_TABLE2_BASELINE_V1.csv` — 35 legacy review cases
- `POST2022_PRIMARY_EVIDENCE_V1.csv` — 12 targeted ecological context rows
- `PUBLISHED_LEWANZIK_2019_DENSITY_V1.csv` — four published baseline coefficients and 95% CrIs
- `PUBLISHED_GLOSSOPHAGA_CONTRASTS_V1.csv` — eight published rate-ratio/z pairs; no invented raw data
- `CROSS_STUDY_SIGN_AND_BASELINE_COUPLING_AUDIT_V1.md` — identification proof, estimator compatibility, ecology limits
- `published_contrast_and_change_score_audit_v1.py` — deterministic aggregate and simulated-null receipt
- `test_published_contrast_and_change_score_audit_v1.py` — 3 dedicated tests
- `ROUSETTUS_ORIGINAL_SOURCE_QA_V1.md` — author original CSV QA
- `run_h1_feasibility.py` and `test_h1_feasibility.py` — primary feasibility and 3 tests
- `.github/workflows/h1-social-information-evidence.yml` — 2 JSON receipts in CI artifact

## Next empirical gate, not yet executed

Original Lewanzik 2019 Dryad source is an ~84 KB XLSX (https://datadryad.org/dataset/doi:10.5061/dryad.gp65g2t). Public metadata was verified, but binary download via this environment was blocked. Do not claim a raw reanalysis. Current Dryad access may require tokenized API downloads. Source-provenance gate must precede any computation or ingestion. The 2026 individual-bat data are in supplementary files/requested from the corresponding author and were not ingested. A genuine held-out across-study test is not yet possible.

**Branch/claim firewall:** proposal and source QA only. No `main` merge or change to frozen 3D individuality outcome.


## 2026-11-19 source/identifiability gate update (v4)

**Empirical Dryad source acquisition: STOP.** The original 2019 XLSX is listed by Dryad, but the fresh GitHub Actions runner got HTTP403 (published file_stream) and HTTP401 (both documented API routes). No source workbook or biological results were retrieved; the dedicated source-gate CI intentionally FAILED with JSON receipt. See [source attempt run](https://github.com/zuizui0223/batter/actions/runs/44452289881), `LEWANZIK_2019_ORIGINAL_SOURCE_ACCESS_STOP_V1.md` and `source_schema_lewanzik_gate_v1.py`. Do not claim the original 2019 data were re-fitted.

**New prospective response estimand frozen before opening any 2019 outcomes:** evaluate the buzz-information signal, 0/12/24/48/96 feeding buzzes/min *within acoustic caller identity*, against baseline activity using absolute Y_playback as response, with `buzz×X_pre` moderation and lake-blocked transfer. 0 buzz includes bat search-phase calls and is not a no-social-acoustic control; pre/post silent controls are phase-confounded. This source is 12 lakes, 30 randomized blocks per lake, not 24 independent recipient bat species. See `LEWANZIK_2019_FROZEN_ANALYSIS_AND_SOURCE_GATE_V1.md`.

**Synthetic-only estimator positive/negative control: PASS** (12 lakes×30 blocks×128 replicates per world):
- Known truth cue×baseline interaction=0.0: recovered mean +0.008619, while naive difference-score baseline slope mean -0.346658.
- Known truth cue×baseline interaction=+0.8: recovered mean +0.808944, while naive difference-score baseline slope mean -0.048503; 128/128 estimated interactions positive.
- Source-code-only tests and all pre-existing H1 tests: **7/7 PASS** with [CI and JSON receipt](https://github.com/zuizui0223/batter/actions/runs/44452894981). No real bat effect estimate is identified by this simulation.

**Scientific decision:** strong *methodological* reason to separate receiver baseline density from baseline-subtracted response, but the original empirical source is inaccessible via verified interfaces. STOP empirical density-context interaction and H3 cognitive-memory/social-information generality until authenticated original row-level source or independently eligible other experiment is available. Frozen batter JAE/BE claims stay unchanged.
