# Foskolos 2025 Mendeley v3 — **real source gate executed** (2026-10-14)

**STATUS: ORIGINAL FILE STRUCTURE VERIFIED; PREVIOUS SIX-TREATMENT ACOUSTIC GATE FAILS ON THE PUBLIC LAB CSV.** This is a **source eligibility result only**, not a new bat personality, speed-response, motion-delay, flight-law, positive/negative effect, p-value, or result of a preregistered endpoint. Frozen JAE and BE manuscripts are unchanged.

## Access breakthrough and provenance

A previous `batter` external-data programme (PR #75) established the **anonymous public Mendeley frontend API** that differs from the protected `api.data.mendeley.com` gateway. The published record is https://doi.org/10.17632/8b57pz6bpj.3 (Foskolos et al. 2025, BMC Biology 23:21).

The public manifest `https://data.mendeley.com/api/datasets/8b57pz6bpj/files?version=3` exposes **18** source files with original file IDs, sizes, SHA256 and `https://data.mendeley.com/public-files/...` download URLs. The seven targeted **original deposited files** were downloaded in isolated GitHub Actions and their complete bytes independently checked against the manifest SHA256:

| Original file | SHA256 prefix | Original purpose |
|---|---|---|
| `lData.csv` | `cb6a35d22913` | laboratory analyses, grouped treatment codes |
| `wData.csv` | `04a0fb92104e` | field/wild analyses, distinct cohort |
| `statistical_analysis.R` | `7da887a8e037` | authors' R modeling code |
| `fig2_lData.mat` | `4d1786517700` | MATLAB v7.3/HDF5 figure source |
| `fig2_wData.mat` | `873a2ec8b9a9` | MATLAB v7.3/HDF5 figure source |
| `fig3_lData.mat` | `24a47604ffe2` | MATLAB v7.3/HDF5 figure source |
| `fig3_wData.mat` | `5ebaf71c89d8` | MATLAB v7.3/HDF5 figure source |

The GitHub Actions job **[38493203267](https://github.com/zuizui0223/batter/actions/runs/38493203267)** finished successfully, with original-file SHA and MAT top-level structure. [Official public categorical receipt, artifact 11863245061](https://github.com/zuizui0223/batter/actions/runs/38493203267/artifacts/11863245061). The standalone audit code does not parse numeric buzz/pursuit magnitudes. **However**, a separate initial public-text retrieval in this same research continuation displayed the CSV's numerical outcome columns before the programme-level eligibility outcome was frozen. Therefore this is **not** a genuinely blind pre-outcome programme, and any later within-dataset numerical analysis must be explicitly exploratory/post hoc.

## Genuine categorical source structure

Original `lData.csv` columns:

```text
treat_code, bat_num, tag_depl_num, chase, buzz1_dur_ms, buzz2_dur_ms
```

- **606 data rows**; **four labelled laboratory bats**, not 606 biological individuals.
- **18 bat×tag-deployment labels**, comprising six under source bat 1 and four each under source bats 2, 3 and 4.
- Treatment code **1:150 rows**, **2:306 rows**, **3:150 rows**; these are **three grouped treatment categories**. The CSV omits individual motor `distance_m`, `speed_m_s`, observed physical onset/end times, calendar `session_date` and unique `trial_id` columns.
- Original R scripts model pursuit with `chase ~ factor(treat_code) + (1|bat_num/tag_depl_num)` and Buzz-II duration with `factor(bat_num) + factor(treat_code) + (1|tag_depl_num)`. That confirms the use of aggregate treatment codes and tag-deployment as a repeated-measure grouping; it does **not** prove the code-to-physical-stimulus mapping or calendar dates for each deployment.
- The source field `bat_num` assigns **six** deployments to label 1, whereas the published Methods describes six daily sessions for bat #4 and four for bats #1–3. This mismatch may simply reflect different identifier numbering between figure R data and narrative, but it must be **explicitly reconciled**, not silently assumed. No inference about which source bat matches named manuscript bat 4 is approved.
- `wData.csv`: **471 rows, 11 distinct wild-bat labels**, with `bat_num,hunt_success,buzz1_dur_ms,buzz2_dur_ms`; no joined laboratory individual ID, challenges or dates. The paper's own wild case count differs due to endpoint-specific eligibility. **Do not join wild and laboratory rows as same bats**.
- Figure MAT sources are MATLAB v7.3/HDF5. The metadata audit successfully recovered outer variables without numeric values; `fig2_lData.mat` exposes outer `chaseRate` and `lData`; `fig3_lData.mat` exposes `lData`, `labBuzz`, `meanLab`. The metadata does **not yet prove** recovery of the six original motor treatments; do not promote HDF figure arrays to verified unaggregated trial records without variable-level mapping.

## Fixed eligibility assessment of the existing acoustic programme

The PR #98 original scalar model and secondary 2×2 speed/distance and nominal-duration pair require **all six physical motor treatment regimes separately identified within every bat×dated session**, and **>=2 valid measured Buzz-II values in each physical regime** for each bat's first four eligible dates. The actual `lData.csv` exposes **only three aggregate codes** and cannot satisfy this gate regardless of observed acoustic means: **STOP_ORIGINAL_SIX_REGIME_LAB_CSV**.

As an additional **nonconfirmatory source support diagnostic** (not a relaxation of the gate), group code 2 versus group code 3 have the following usable Buzz-II counts in the **first four tag-deployment IDs sorted numerically within each original bat label**:

| source bat | first two code-3 usable counts | third/fourth code-3 usable counts | `>=2` each of these 4 deployments? |
|---|---|---|---|
| 1 | 7, 8 | 7, 6 | yes |
| 2 | 5, 5 | **1, 0** | **NO** |
| 3 | 3, **1** | **1, 0** | **NO** |
| 4 | 2, 3 | 3, 3 | yes |

All four original bats have source code 2/3 events, but only **two of four** clear the analogous per-aggregate-code `>=2` Buzz-II retention rule at all four tag deployments. Most importantly, this is **not** the original six-motor-regime gate and it provides **no** evidence of a stable individual response slope. No missing buzz outcome is replaced with zero, and no source bat is removed to manufacture apparent support.

The data contain the **chase** binary variable across grouped treatments. It could support a distinct, **post-data exploratory** group-contrast analysis if physical cohort, deployment-to-day mapping and missingness were separately validated, but this does **not** rescue the pre-specified four-bat individual Buzz-II motor-law test. Cherry-picking a surviving endpoint or two positive bats as a confirmatory replacement is prohibited.

## Source verdict

- **SOURCE ACQUISITION:** SUCCESS — public original file list and seven original deposited files accessed using the anonymous frontend; exact SHA256 verified.
- **INDEPENDENT IDENTIFIED BAT / RECORDER RECORDS:** 4 source bat labels, 18 tag-deployment labels. Calendar dates for each deployment not verified from CSV.
- **SIX PHYSICAL CONDITIONS / INDIVIDUAL SPEED×DISTANCE COEFFICIENTS:** **STOP_FROM_LDATA_CSV** — original detailed stimuli collapsed to 3 codes. MATLAB aggregate figure data do not establish independent physical per-trial stimuli.
- **FOUR-BAT HELD-OUT BUZZ-II RESPONSE:** **STOP_CURRENT_ELIGIBILITY** — 2 of 4 bats fail even relaxed three-group valid-buzz support on the selected four deployments.
- **INDIVIDUAL TIME-RESOLVED FEEDBACK GAIN/LATENCY, 3D TRAJECTORY, FIELD ECOLOGICAL PAYOFF:** **NOT IDENTIFIED**.
- **PRE-OUTCOME INFERENCE CLAIM:** **NOT AUTHORIZED** — some original CSV physiological values were already exposed during source retrieval, and the proposal was designed iteratively.

This is not an absence-of-individuality finding. It is a clear end to the specific public-source identification attempt. **Do not switch to post hoc treatment contrasts, remove nonresponders, or call artifact CI success a biological effect.** Future personal control-law claims require a different **verified, finer-grained** source or genuinely new data. Keep PR #98 isolated and draft; do not modify frozen JAE, synthetic gate, or other study outcomes.
