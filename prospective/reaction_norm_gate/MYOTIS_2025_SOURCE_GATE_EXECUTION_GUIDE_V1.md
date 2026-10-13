# Myotis 2025 external-data gate: runbook (v1, 2026-10-13)

**Status: HOLD_SOURCE_ZIP_NOT_ACQUIRED.** No raw v3 dataset files accessed; no observed individual bat parameters, novel biological p-values, 3-D XYZ coordinates or flight rule have been recovered. This is an executable **post-publication exploratory** gate, not a new preregistration, and does not alter the JAE release.

**Original article:** Foskolos et al., BMC Biology 23:21 (2025), https://doi.org/10.1186/s12915-024-02106-6

**Dataset:** Mendeley Data *v3*, https://doi.org/10.17632/8b57pz6bpj.3 (landing page advertises Download All; API file listings returned 401 in this environment). The dataset page lists CC BY 4.0; verify any individual file licensing.

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

Requires exactly four physical bats; at least four dated occasions per bat; all six moving conditions attempted on every bat's first four dates; >=2 valid buzz-II observations in each day's easy/difficult class; no duplicate trial IDs or guessed units. If any fail, script exits **2** with `HOLD_SOURCE_GATE`.

For each bat i, day d, treatment class c, define `L_i,d,c` as the mean of `log(1 + measured buzz-II-duration-ms)` **among valid recorded buzzes**. Primary scalar contrast:

```text
Delta_i,d  = L_i,d,difficult - L_i,d,easy
beta_i     = mean(Delta_i,day1, Delta_i,day2)
beta_group = mean_i(beta_i)              # equal physical-bat weights
pred_M0    = beta_group
pred_M1_i  = beta_group + 0.5 * (beta_i - beta_group)
```

The fixed shrink factor **0.5** is set before viewing new outcomes; no tuning on test days. Score both predictors on dates 3-4, **equally across days and bats**, using MSE. Always publish individual signs and losses, including deterioration. This estimates a **scalar conditional acoustic response**, not the dynamic gain/latency `g_i,tau_i`, and not spatial 3-D flight. No p-value is generated: n=4, correlated repeated days, non-random missing buzz selection, possible heteroscedasticity and device effects.

The original stationary trials assign response-derived **mock t0**, not an observed stimulus motion onset. Therefore stationary aligned CI cannot serve as a causal time-resolved control. This implementation **ignores that time-series endpoint** and uses easy versus difficult **moving** conditions only. The author's motor-only sham does not supply independently repeated stationary baselines.

## 4. Tests and reporting limits

```bash
cd prospective/reaction_norm_gate
python -m unittest -v test_myotis_source_gate_v1.py
python -m py_compile myotis_source_gate_v1.py
```

All tests use **fabricated synthetic values only**, including deliberately missing buzz, misleading units, source ZIP file header and strict train/test leakage checks. Passing tests is not evidence that any real bat has a personal feedback rule.

**Scientific next step:** obtain and audit v3 source; then if eligible, report **exploratory** person-specific held-out contrast. If raw data lacks day or a comparable physical stimulus, stop, do not silently relax source restrictions. Independently identified 3-D free-flight control laws and functional hunting payoffs remain untested.

## Source/branch firewall

PR #98 is a DRAFT child of PR #95, **not** main or JAE. The script has no network access, does not download any data and does not mutate external files other than an explicitly requested JSON output. Do not merge a simulated result as biological evidence.
