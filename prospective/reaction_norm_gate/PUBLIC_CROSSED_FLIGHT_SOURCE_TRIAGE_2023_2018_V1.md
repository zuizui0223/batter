# 2023 group-flight / 2018 3D-obstacle public source eligibility audit v1

**2026-10-08. Source literature/availability audit only. No new animal measurement values opened, downloaded, extracted or statistically analyzed.**

## Forli & Yartsev 2023 — potentially rich biological replication, but full source on request

Citation: Forli, A. & Yartsev, M.M. (2023), *Nature* 621, 796–803. doi: 10.1038/s41586-023-06478-7.
Official published article: https://www.nature.com/articles/s41586-023-06478-7

The authors report:
- **13 bats across 87 behavioural sessions**, free group flights monitored with RTLS.
- ~**57,806 flights** reported in the paper; substantial social vs non-social landing and variation in one vs multiple food-site opportunities.
- Daily structure and individual co-location/space preferences are already **published prior-art results**, not independent evidence discovered by `batter`.
- Source Data Fig. 1–4 XLSX files are publicly linked, but **full dataset and custom MATLAB analysis code are explicitly available from the corresponding author only upon reasonable request**.

Eligibility decision for our specific *independent repeatable personal 3D challenge-response* estimand:
**STOP_FULL_CROSSED_3D_TRAJECTORIES_NOT_PUBLIC**.
The public article's session count does not establish independently matched **within-occasion** obstacle-reference/challenge manipulations, calibrated apparatus crossover, or raw trajectory-level outcome release. Published XLSX figure source data are **not assumed equivalent** to the full RTLS archive. Do not assume 87 independent bats, or assume that individual task response can be identified by comparing food sites across group compositions.

This source remains a *high-value conditional data-request candidate*, but not a currently executable confirmatory public test.

## Wohlgemuth, Yu & Moss 2018 — repeated obstacles but biological n=3 and noncrossed contexts

Citation: Wohlgemuth, M.J., Yu, C. & Moss, C.F. (2018), *Frontiers in Cellular Neuroscience* 12:270. doi:10.3389/fncel.2018.00270.
Official article: https://www.frontiersin.org/journals/cellular-neuroscience/articles/10.3389/fncel.2018.00270/full

Source reports:
- **Three distinct `Eptesicus fuscus` bats** flew 11, 11 and 16 sessions (38 total).
- Obstacles placed in 8/11, 6/11, and 8/16 sessions; each session included >=30 flight trials.
- Subjects had different flight spaces/geometry, including a restricted corridor for bat 3; this is *not* a common cross-bat obstacle contrast.
- No independently verified open original bat-ID×session×condition×flight-XYZ numerical archive identified from the published page in this audit.

The source shows repeated obstacle exposure, but **not** the required >=4 independent occasions **each** containing controlled challenge/reference conditions across adequately replicated and comparable individuals. Moreover, n=3 bats cannot support population-general personal reaction-norm inference.

Decision: **STOP_NONCROSSED_CONDITIONS_AND_LOW_BIOLOGICAL_N** for this particular frozen estimator. This is not a negative result about the paper's published 3D place-field/sonar questions.

## Decision matrix

| Published source | Verified persons / episodes | Raw 3D open as needed? | Exact crossed challenge+reference on repeated independent occasions? | Status |
|---|---|---|---|---|
| Nishiumi et al. 2024 | 7 bats, 18 sessions, max 3 distinct dates per bat | Named 3D/audio CSVs public | No, not verified, date support fails | STOP (#95 earlier gate) |
| Forli & Yartsev 2023 | 13 bats, 87 sessions | Full dataset and code request-only; public figure source tables insufficient by default | Not verified | STOP |
| Wohlgemuth et al. 2018 | 3 bats, 38 sessions | Original session 3D archive not verified public | Obstacles vary *between* sessions; bat geometry differs | STOP |

**Scientific conclusion:** public research papers with abundant flight records may still lack the crossing and raw-data access needed to estimate *replicable individual response slopes*. Do not replace a failed data gate by treating repeated trials as extra individuals or stretching a task-specific design into a new causal result.

This audit does not authorize emailing authors, starting animal experiments, or relaxing predeclared eligibility merely to obtain a positive outcome.
