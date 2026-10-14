# Myotis 2025 external-data gate: runbook (v1, 2026-10-13)

**Current scientific status (2026-10-14): SOURCE_ORIGINAL_FILES_VERIFIED / STOP_SIX_REGIME_AND_FOUR_BAT_BUZZ_GATE.** The anonymous frontend enabled seven original v3 files to be retrieved and SHA256 verified (GitHub Actions 38493203267, artifact 11863245061). The author's laboratory `lData.csv` has 606 rows, four bat labels, 18 tag-deployment labels and only THREE grouped treatment codes; the six physical distance×speed regimes are missing from that CSV. Additionally only 2/4 bats have >=2 valid Buzz II trials in BOTH groups 2/3 across first four tag-deployments. **DO NOT run `analyse` on the original grouped lData or invent a distance/speed lookup.** The rest of this guide is a conditional workflow if finer-grained original files become independently verified; it is NOT approved for this source as currently deposited. No new observed individual response parameters, biological p-values, 3-D XYZ coordinates or flight rules have been recovered. This is an executable **post-publication exploratory** gate, not a new preregistration, and does not alter the JAE release.

**Original article:** Foskolos et al., BMC Biology 23:21 (2025), https://doi.org/10.1186/s12915-024-02106-6

**Dataset:** Mendeley Data *v3*, https://doi.org/10.17632/8b57pz6bpj.3 (landing page advertises Download All; API file listings returned 401 in this environment). The dataset page lists CC BY 4.0; verify any individual file licensing.

## New executed real-source support result (supersedes original ZIP-access blocker)

Original author files have been directly downloaded and checked via the public `/api/datasets/8b57pz6bpj/files?version=3` endpoint. Full details: [original file support and strict STOP result](MYOTIS_2025_V3_ORIGINAL_CATEGORICAL_ELIGIBILITY_RESULT_2026_10_14.md). **Dataset acquisition is no longer the bottleneck; the source's aggregation and informative Buzz-II missingness are.**

The trial-level `lData.csv` is a *different table structure* from this code's required canonical 6-regime input. The original grouped `treat_code` **must not** be converted into fictitious individual physical speed/displacement values. A separate post-outcome exploratory chase-probability contrast is possible in principle but is **not** an authorized rescue of the originally locked four-bat acoustic coefficient test.

### Latest source closure: Figure 3 does not restore individual dates (2026-10-14)

A further SHA-verified original MAT/HDF5 audit recovered **only four** Figure-3 table field names: `treat_code`, `trial_id`, `time_t0_ms`, `norm_ci`. The separate laboratory `lData.csv` has bat/deployment categories but **no matching trial ID**. There is no verified trialwise individual/date bridge between the available original data products. The six-regime coefficients are additionally non-identifiable from the 3-group treatment aggregation. Read [the original Figure-3 schema gate](MYOTIS_FIG3_INDIVIDUAL_JOIN_GATE_VERIFIED_2026_10_14.md) and [exact algebra certificate](MYOTIS_GROUPED_CONDITIONS_EXACT_NONIDENTIFIABILITY_CERTIFICATE_V1.md). **Do not promote the conditional forecast code in this guide to an observed bat-policy result.**

## 1. Inventory original data before opening numerical outcomes

Download the author's original ZIP **unchanged**. Then from the repository root run:

```bash
python prospective/reaction_norm_gate/myotis_source_gate_v1.py inventory /path/to/original.zip --out inventory.json
```

The inventory lists filenames, SHA256 for ZIPs <=100 MB, CSV/TSV column headers, and flags MATLAB/Excel/R binary files as **not parsed**. It never passes the source gate automatically. If original files are binary or aggregated, examine them with trusted MATLAB/R and verify that trial IDs, physical bat ID, date and the treatment inputs can be recovered. Never invent unavailable source values.

## 2. Required *verified* canonical CSV fields

One row per real trial (not one row per pulse/1-ms interpolation):
- **bat_id**: independently confirmed physical individual;
- **session_date**: ISO `YYYY-MM-DD`, not assumed independent due to mere separation by a calendar day;
- **trial_id**: unique within bat and date;
- **distance_m** and **speed_m_s**: original physical stimulus in m and m/s (stationary 0/0, moving 0.08m×0.5/1/1.3m/s and 0.24m×0.5/1/1.5m/s);
- **buzz_ii_valid**: 0/1 from documented original eligibility, no outcome-dependent manual omissions;
- **buzz_ii_ms**: *recorded* positive duration in milliseconds if valid; otherwise **blank**.

Converting the original deposited files into these fields is an auditable human-reviewed mapping step. This script **cannot infer those columns from a file name**. The published 631 attempts, 606 chase observations, 474 buzz-I, 479 buzz-II and 391 figure-3 time series have different eligibility. Do not force them into a fictional complete table.

## 3. Held-out sensory-response calculation, only after the source gate passes

```bash
python prospective/reaction_norm_gate/myotis_source_gate_v1.py analyse /path/to/verified_trials.csv --out forecast_exploratory.json
```

Requires exactly four physical bats; at least four dated occasions per bat; all six moving conditions attempted on every bat's first four dates; **at least two valid Buzz-II observations separately in each of the six regimes per bat×day**, not merely two per pooled easy/difficult group; no duplicate trial IDs or guessed units. If any fail, script exits **2** with `HOLD_SOURCE_GATE`.

For each bat i, day d and **individual physical stimulus regime** c, define `L_i,d,c` as the mean of `log(1 + measured buzz-II-duration-ms)` **among valid recorded buzzes in that exact regime**. The easy group contains four physically distinct distance/speed regimes; the difficult group contains two. All regimes receive equal weight within their respective groups, regardless of differential buzz eligibility. Primary scalar contrast:

```text
Delta_i,d  = (1/2) * sum_c_in_difficult L_i,d,c
             - (1/4) * sum_c_in_easy L_i,d,c
beta_i     = mean(Delta_i,day1, Delta_i,day2)
beta_group = mean_i(beta_i)              # equal physical-bat weights
pred_M0    = beta_group
pred_M1_i  = beta_group + 0.5 * (beta_i - beta_group)
```

The fixed shrink factor **0.5** is set before viewing new outcomes; no tuning on test days. Score both predictors on dates 3-4, **equally across days and bats**, using MSE. Always publish individual signs and losses, including deterioration. This estimates a **scalar conditional acoustic response**, not the dynamic gain/latency `g_i,tau_i`, and not spatial 3-D flight. No p-value is generated: n=4, correlated repeated days, non-random missing buzz selection, possible heteroscedasticity and device effects.

The original stationary trials assign response-derived **mock t0**, not an observed stimulus motion onset. Therefore stationary aligned CI cannot serve as a causal time-resolved control. This implementation **ignores that time-series endpoint** and uses easy versus difficult **moving** conditions only. The author's motor-only sham does not supply independently repeated stationary baselines.

### Method repair / pre-outcome regression audit (2026-10-13)

The earlier code pooled all valid Buzz-II trials into broad `easy` and `difficult` categories, weighting each physical treatment by its number of eligible buzzes. This was a **methodological defect**: unequal trial eligibility can change a bat's contrast even if its per-treatment responses are fixed. Before this external dataset was acquired, we added red-green synthetic tests confirming the bug: for one fabricated dataset, simply replicating one easy treatment's trial records changed the pooled training group contrast from **+0.081740 to −0.475416**, despite no change to treatment-level means. **These are synthetic failure demonstrations, not measured bat effects.**

The amended estimator gives every physical regime fixed equal weight within its published class and refuses to calculate a day if any of the six moving regimes has fewer than 2 valid Buzz-II trials. The endpoint is **a grouped difficulty contrast involving changes in BOTH displacement and target speed**; it does not independently isolate either physical dimension. All these decisions remain post-publication exploratory, despite being made before our access to new individual outcome values.

## 3b. Independent physical factors: fixed 2×2 supplementary response-surface test

The published six moving-target treatments include a complete **2×2 factorial subset** with target displacement `0.08 m / 0.24 m` and movement speed `0.5 m/s / 1.0 m/s`. The other two treatments remain in the original six-treatment source-eligibility gate and the prespecified main easy-versus-difficult contrast. The secondary calculations do **not** replace or choose among the original main outcomes.

Let `A=mean(log1p(BuzzII_ms)|0.08m,0.5m/s)`, `B=...(0.08m,1.0m/s)`, `C=...(0.24m,0.5m/s)` and `D=...(0.24m,1.0m/s)` within each physically identified bat×day. Each average is based on >=2 actually valid Buzz II trials. The exact effect-coded reparameterization is

```text
mean                 = ( A + B + C + D )/4
b_speed              = (-A + B - C + D )/4
b_displacement       = (-A - B + C + D )/4
b_speed_x_distance   = ( A - B - C + D )/4
```

The four means therefore define exactly four numbers; this is **not** a discovered control equation, physiological latent dimension or causal effect. Relative to speed, only the two matched `0.5m/s` and `1.0m/s` levels are contrasted at two fixed displacements. The faster treatment necessarily has shorter travel duration for the same displacement; the design does not isolate speed from stimulation time.

The additional `factorial_2x2_secondary` block in the JSON output:

- learns each bat's three effect-coded non-intercept coefficients from **days 1–2 only**;
- compares the trained cross-bat group mean coefficients with `group + 0.5*(personal - group)` held-out personal estimates;
- evaluates all **three coefficients together** by equal-axis MSE on **days 3–4**, equal day and equal physical bat;
- returns per-bat and bat-day forecasts and their positive/negative gains; produces **no p-value**;
- never selects the best axis after seeing actual bat outcomes, and never adds real field 3-D route, direct target capture, or fitness evidence.

Even when the scalar grouped difficulty slope predicts, the speed/length/interaction coefficients may fail to transfer; the joint test is a stricter examination of whether *how a bat maps opportunity into response* is genuinely personal. With N=4 and conditional Buzz-II observation this remains a highly imprecise **secondary, exploratory, post-publication** test. Individual gains measured under stable recording or nonrandom buzz selection cannot be attributed uniquely to behavior. If the original dataset lacks full bat×day×six-regime observed support, both the primary and secondary source gates remain on HOLD.

### Numeric access status

As of 2026-10-13, **original Mendeley v3 ZIP/file columns are still inaccessible from this tool environment**, including attempts through its official OAuth2-marked API and the HTML landing page. This runbook and four supplementary regression tests were completed **without** opening new trial measurements; all example effects and test outputs are fabricated.

## 3c. Nominal-duration paired-regime falsification diagnostic

There is one physically instructive coincidence in the six original regimes:

```text
easy:      distance=0.08 m, speed=0.5 m/s → nominal D/V = 0.160 s
difficult: distance=0.24 m, speed=1.5 m/s → nominal D/V = 0.160 s
```

This **does not establish equal real motion durations** because acceleration/deceleration, motor onset lag, target interception and acoustic apparatus signals were not checked. Therefore the extra JSON `nominal_duration_pair_diagnostic` is strictly `NOMINAL_ONLY` with `actual_duration_verified=false`; it must NEVER be described as a confirmed time-matched biological contrast.

For each eligible bat×day, the script computes the second regime's mean log-Buzz-II minus the first regime's mean log-Buzz-II and evaluates the bat's first two dated sessions against held-out sessions three and four. It reports equal-bat MSE of shared versus fixed-shrink personal forecasts and individual signed gains; it makes **no** p-value or claim of distinct physiological controllers. This diagnostic is added alongside the unchanged original six-regime primary contrast and 2×2 secondary; no endpoint is to be selected later as 'the true test' based on the numerical outcomes.

A true inference about a duration-only response requires verified target-onset/offset, actual motion profile and motor sound control; if unavailable, do not infer equal exposure or acoustic sensitivity to velocity versus displacement. See [the complete physical identifiability audit](MYOTIS_NOMINAL_DURATION_MATCHED_PHYSICAL_CHALLENGE_V1.md).

## 4. Tests and reporting limits

```bash
cd prospective/reaction_norm_gate
python -m unittest -v test_myotis_source_gate_v1.py
python -m py_compile myotis_source_gate_v1.py
```

All **21** tests use **fabricated synthetic values only**, including deliberately missing buzz, misleading units, source ZIP file header and strict train/test leakage checks. Passing tests is not evidence that any real bat has a personal feedback rule.

**Scientific next step:** obtain and audit v3 source; then if eligible, report **exploratory** person-specific held-out contrast. If raw data lacks day or a comparable physical stimulus, stop, do not silently relax source restrictions. Independently identified 3-D free-flight control laws and functional hunting payoffs remain untested.

## Source/branch firewall

PR #98 is a DRAFT child of PR #95, **not** main or JAE. The script has no network access, does not download any data and does not mutate external files other than an explicitly requested JSON output. Do not merge a simulated result as biological evidence.
