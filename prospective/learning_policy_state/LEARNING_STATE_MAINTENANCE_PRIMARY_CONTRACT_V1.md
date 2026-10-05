# Learning-state maintenance primary contract v1

## Status

**PROSPECTIVE OUTCOME CONTRACT — frozen before max-flight-speed or meandering-width row values are opened.**

Branch:
`prospective/learning-policy-state-v1`

Parent gates:
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- `XLSX_HEADER_OPENING_ALLOWLIST_V1.md`
- `STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md`

Structural result:
- 14 biological subjects;
- condition 1: 7 subjects;
- condition 2: 7 subjects;
- every subject has exactly one trial-1 row and one trial-12 row;
- no duplicated subject × trial rows.

## Biological question

Published work already establishes that repeated experience changes flight behaviour.

The new question is:

> **after removing the condition-specific common learning shift, does an individual remain closer to its own earlier policy state than to the states of other individuals?**

This tests maintenance of **relative personal policy position during learning**, not whether learning occurs.

## Source table

File:
`raw_analysis_data_by_yamada.xlsx`

Sheet:
`1st_table`

Authorized outcome columns:

- K: `max_flight_speed [m/s]`
- L: `meandering width [cm]`

Design/linkage columns:
- C condition;
- D bats_id;
- E trial.

No pulse outcome is authorized in this primary.

## Complete-case support

A subject is evaluable only if:

- condition is 1 or 2;
- trial 1 and trial 12 are both present;
- max flight speed is finite at both trials;
- meandering width is finite at both trials.

Primary opens only if:
- >=12 evaluable subjects total;
- >=5 evaluable subjects per condition.

Otherwise STOP without changing endpoint or threshold.

---

# Common-learning removal

For each endpoint separately and within every:

`condition × trial`

cell:

- subtract the arithmetic mean across evaluable subjects;
- divide by the sample SD.

Require finite positive SD in all four cells for both endpoints.

This removes:
- the mean learning shift;
- condition-specific scale;
- any global difference between trial 1 and trial 12.

It retains each individual's relative position within its own acoustic condition and learning stage.

For subject i at trial t define the 2-D residual policy state:

[
u_{it} =
(z^{speed}_{it}, z^{width}_{it}).
]

No sign reversal is applied to width; Euclidean identity is sign-invariant.

---

# Primary P1 — early-to-late personal-state identity

For each subject i:

- `D_self(i) = ||u_i1 - u_i12||`;
- `D_other(i)` = mean Euclidean distance from `u_i1` to trial-12 states of all **other subjects in the same condition**.

Define:

[
K_i = D_{other}(i)-D_{self}(i).
]

Positive K_i means the individual's late state is closer to its own early state than to other same-condition individuals.

Aggregate:

1. mean K_i equally within condition;
2. average the two condition means equally.

This is `K_policy`.

## Null

Independently within each acoustic condition:

- permute trial-12 subject labels among complete 2-D trial-12 vectors;
- keep trial-1 labels fixed;
- preserve all outcome values, condition membership and trial structure.

Permutations:
**9,999**

Seed:
`202610050941`.

One-sided p:
`(1 + #null >= observed)/(1 + 9999)`.

## Support rule

P1 is supported only if:

- `K_policy > 0`;
- p <= 0.05;
- >=70% of evaluable subjects have `K_i > 0`.

With 14 evaluable subjects, this requires at least 10 positive subjects.

No condition pooling rescue after outcome opening.

---

# Secondary P2 — endpoint-specific rank/offset persistence

For each endpoint separately:

- use the same condition × trial standardized values;
- correlate trial-1 z with trial-12 z across all evaluable subjects using Pearson r.

Calibration:

- permute trial-12 subject labels independently within condition;
- 9,999 permutations.

Seeds:
- speed: `202610050942`
- meandering width: `202610050943`

One-sided positive p.

These are secondary mechanism descriptors and cannot rescue P1.

Also report condition-specific Pearson r descriptively without inferential claims.

---

# Published-learning validation

After outcome opening, report condition means at trial 1 and trial 12 for:

- max flight speed;
- meandering width.

These are source-validation/descriptive quantities only because the learning effects were already published.

Do not count them as new inferential support.

---

# Interpretation

## P1 supported

Allowed claim:

> despite a large experience interval and condition-specific behavioural updating, individuals retained relative positions in a two-dimensional speed–route policy space.

This directly supports maintenance of a personal policy state during learning.

It does not prove that the same axes as the Teshima 2026 obstacle-policy manifold are identical.

## P1 unsupported

Do not infer that individuality is absent.

Possible bounded interpretations:
- learning reorganizes relative individual positions;
- speed and meandering width are insufficient policy coordinates;
- only finer trajectory features retain identity.

The raw-trajectory replication may still be evaluated under its separately frozen contract.

## Ceiling

This primary does not identify whether persistent offsets arise from:
- morphology;
- physiology;
- prior experience;
- learned control;
- developmental history.
