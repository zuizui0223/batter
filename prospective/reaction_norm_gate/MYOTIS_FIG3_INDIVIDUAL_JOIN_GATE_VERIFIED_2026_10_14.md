# Exact original Figure 3 table-identity gate — source-verified STOP

**Date:** 2026-10-14. **Result class:** Real, public-original-file *schema evidence*, NOT an observed bat-response effect. This closes only the specific 2025 public-file route for a four-bat independent-day acoustic gain/latency test. Do not alter frozen JAE or treat a data STOP as a biological null.

## Original source and independent provenance

- Foskolos et al. (2025), *Fast vocal-motor tracking of escaping prey in echolocating bats*, *BMC Biology* 23:21, https://doi.org/10.1186/s12915-024-02106-6.
- Author data v3, https://doi.org/10.17632/8b57pz6bpj.3.
- Unmodified deposited binary **`fig3_lData.mat`**, public file UUID `9c19d9a7-a23f-4e0a-8a30-e19c485babf4` and SHA256 **`24a47604ffe2a034162f7b64d6fa0a49ae96e0086e8a00c6bf84fcd0561fe75c`**.
- [Executed source-hash-pinned, outcome-blind GitHub Actions run 38499671754](https://github.com/zuizui0223/batter/actions/runs/38499671754), uploaded raw structural JSON [artifact 11865356966](https://github.com/zuizui0223/batter/actions/runs/38499671754/artifacts/11865356966).
- New audit implementation [`audit_myotis_fig3_identifiers_v1.py`](audit_myotis_fig3_identifiers_v1.py) reads HDF5 object paths, MATLAB class attributes and **only character-class schema labels**. It does NOT read numeric call interval, buzz, speed, position, physiology, or individual scores.

Original 179,865-byte file was retrieved and SHA matched on attempt **1 of 5**. The HDF5 structure comprises **59** named objects under roots `#refs#`, `#subsystem#`, `colors2`, `lData`, `labBuzz`, `meanLab`.

## Decisive source-level schema fields

MATLAB-character field names recovered for `lData`:

```text
treat_code
trial_id
time_t0_ms
norm_ci
```

- `treat_code` holds **3 original analysis groups**: stationary, easy, difficult.
- `trial_id` differentiates trials *within the Figure 3 file*.
- `time_t0_ms` and `norm_ci` define normalized pulse-interval trajectories in those plotted trials.
- **None of the recovered four MATLAB table variable names is** `bat_num`, `tag_depl_num`, `session_date`, `date`, `day`, actual `distance_m`, actual `speed_m_s`, or 3-D `x/y/z`.

The original `fig3.m` plotting code iterates `unique(A.trial_id)` after `A=lData(lData.treat_code == 1/2/3,:)` and reads `time_t0_ms` / `norm_ci`; it does not make an observed individual/date join. This independently corroborates the extracted table schema.

Important scope: an HDF5 MATLAB `MATLAB_fields` attribute for an underlying structural object and MATLAB metadata were also present, but no other **bat/date-join schema field** was recovered in the character-label audit. Absence of a recovered field is a **source-verified limitation of the currently exposed Figure 3 analysis table**, not proof no unshared source mapping exists elsewhere.

## Why the public original tables cannot be losslessly joined

| Source | Preserved identifiers and independent time | Missing for planned predictor |
|---|---|---|
| `lData.csv` (606 lab trials) | 4 `bat_num` labels; 18 `tag_depl_num` source recording labels; 3 grouped `treat_code` categories; conditional Buzz II | No `trial_id`; no six physical motion levels; no explicit `session_date` or motion onset/offset |
| `fig3_lData.mat` | `trial_id`, `time_t0_ms`, `norm_ci`, grouped `treat_code` | No `bat_num`, no `tag_depl_num`, no dates, and no six physical motion levels |
| `fig1_lData.mat` | Exemplary selected stationary/moving source bouts `cTrial`, `ncTrial` | Not a complete bat-by-day-by-treatment trial archive |

**No common, independently verified trial key connects the two data products.** Guessing source order, matching buzz duration or shared treatment-code counts would be an unregistered and potentially many-to-many/impossible join; the raw table row order can change after editorial reprocessing. Do not make these joins to recover a personal 4-bat response law.

The original stationary Fig. 3 origin is a response-dependent mock t0, not physically observed target-motion onset, so a moving-minus-stationary normalized-CI curve is not a clean dynamic motion-kernel contrast.

## Exact inferential verdict

- **PASS:** genuine source acquired; source checksum verified; laboratory 4 bat ID labels and 18 tag-deployment records; plotted laboratory 3-category pulse trajectories with trial ID; no numeric outcomes used in this gate.
- **STOP:** 4-bat **held-out personal delay/gain** from Figure 3 — no direct individual×independent-occasion key to `norm_ci`.
- **STOP:** originally proposed 6-regime personal speed/distance/interaction and 160ms nominal pair from the available group-coded archive — no original trialwise speed/displacement IDs.
- **HOLD (external source only):** Any unshared, more finely annotated source archive may restore this estimand, but must be separately verified. Do not claim a hypothetical archive exists.
- **NOT TESTED:** personal flight-control equation; individual learning/fitness benefits; field 3D vertical niche; per-bat 3D ecological reaction norm.

This validates a **negative data-identifiability result**, not a negative biological finding. Do not retrospectively change the source eligibility criterion, assign output values to fabricated individual trajectories, or count repeated trials as independent animals. The previously completed JAE and behavioral evidence are unchanged.
