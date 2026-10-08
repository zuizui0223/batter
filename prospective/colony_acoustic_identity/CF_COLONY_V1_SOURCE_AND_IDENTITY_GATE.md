# CF-colony individual acoustic history — source-only preflight v1

STATUS: PRE-OUTCOME / STRUCTURAL ONLY. This is a new, independent source and must NOT reopen the five-bat Rhinolophus flight trajectories, change JAE or reuse its preregistered endpoints. The protocol is frozen before opening any numerical call frequencies.

PUBLIC SOURCE:
- Dataset: Mendeley Data 10.17632/4y98p5y8fc.1, published 29 April 2026; dataset id 4y98p5y8fc, version 1.
- Publisher: https://data.mendeley.com/datasets/4y98p5y8fc/1
- Paper: Matsumoto, Yoshida & Hiryu 2026, Journal of Comparative Physiology A, DOI 10.1007/s00359-026-01821-5.
- Documented public API: https://api.data.mendeley.com/datasets/4y98p5y8fc?version=1 and files endpoints of the dataset and /datasets/publics/4y98p5y8fc/files?version=1. Official API docs: https://data.mendeley.com/api/docs/

PRIOR ART, NOT NEW RESULT: The paper already documents 101 unique bats, 177 bat×capture-event observations, 15 colony-mixing events and up to 30 days of acoustic monitoring. Captured bats typically had lower initial CF2 than residents and increased it over time as means converged. Seven events had significantly lower newcomer CF2, eight did not. Multiple individuals recur in several events. The authors ALREADY propose FM spectral separation versus CF shared silent spectral window as a mechanistic interpretation. The data do not randomize acoustic interference, social group membership, colony condition or capture stress. No claim of flight-space substitution follows from these at-rest CF2 data.

NEW BIOLOGICAL QUESTION CONDITIONAL ON SOURCE SUPPORT: Does individual acoustic history remain useful for predicting a bat's relative CF2 phenotype across distinct colony-mixing events after event-level group shift and captured/resident status are considered? Alternative mechanisms: complete group-driven reset; stable colony-relative individual bias; captive acclimation, age, sex, repeated role and recording-era confounding. A numerical finding of residual rank stability would not prove causal genetic/personality or sonar-sensing advantage.

GATE 0 — PUBLIC METADATA / AUTHORIZED RETRIEVAL:
1. Record exact ID/DOI/version, reported file UUID/name/size/SHA256 and HTTP response of the documented official public dataset metadata and BOTH officially documented file-list endpoint variants (do not invent or silently substitute any source).
2. Download only public small tabular data files up to 15 MiB via Mendeley-provided download_url or documented file_downloaded redirect. Refuse unknown/signed non-HTTPS URLs, audio files, large archives, and all numeric analysis.
3. Record SHA256 of every local raw source, but do not re-upload or disclose raw data.
4. If API endpoints all reject access (including 403), status STOP_SOURCE_API_INACCESSIBLE. Do not assert that the publicly catalogued data do not exist.

GATE 1 — SCHEMA ONLY:
- Inspect CSV/TSV column names, Excel workbook sheet names and first-row headers, MAT headers (whosmat or HDF5 keys/shapes), without opening CF2 magnitudes.
- Identify explicitly documented *stable physical animal ID* across events, mixing/capture event ID, date/recording session, captured-versus-resident state and CF2 column/unit.
- Trial-local bat numbers, file indexes or sheet rows are NOT cross-event animal IDs. If persistent individual identity is not verifiable from the documentation: STOP_NO_CROSS_EVENT_STABLE_ID.
- No numeric source CF2 values opened during Gate 1.

GATE 2 — CATEGORICAL COUNTS ONLY:
Gate 1 must pass. May read ONLY categorical ID, event, session/date and role columns and structural missingness of CF2, without its values.
Require ALL of the following, frozen *before* these counts:
  * at least 12 unique physical individuals appearing in at least two distinct mixing events each;
  * at least 3 distinct events containing eligible held-out observations;
  * at least 2 separate recording dates for each retained bat×event unit;
  * captured/resident classification or documented equivalent group state;
  * at least 30 eligible bat×event pairs after all restrictions.
If any requirement fails, STOP_CROSS_EVENT_BAT_IDENTITY_SUPPORT. Do not conduct posthoc within-event identity significance as rescue.

GATE 3 — NEW EXACT NUMERICAL CONTRACT LATER:
Only after passing Gate 2, freeze in a SEPARATE pre-result commit the target scale, first/last session definition, cohort-and-group standardization excluding held-out bat target, longitudinal training vs test split at whole event, bat-level interval, role/acclimation controls, identity-label-null exchangeability, and a single decision rule. Do not call baseline-adjusted correlation a causal self-maintenance effect; regression to mean and collider effects require explicit consideration.

CRITICAL MEASUREMENT DIFFERENCES:
- 2018 Hase et al Miniopterus group-flight terminal FM frequency vs 2026 resting Rhinolophus CF2, different species, acoustic function, crowd context and time scales.
- 2018 public Dryad sound file of ~614.45MB does not list synchronized 3D coordinates. The 2018 and 2026 sources cannot independently establish a within-individual spatial-frequency compensation tradeoff.
- The 2026 paper's silent-window account and CF-vs-FM difference ARE PUBLISHED HYPOTHESES, not a new discovery from this project.

OUTPUT: machine-readable JSON of metadata/status, files and header types, dataset-digest receipts, structural eligibility or stop reasons. NO CF2 values, statistics or p-values.
