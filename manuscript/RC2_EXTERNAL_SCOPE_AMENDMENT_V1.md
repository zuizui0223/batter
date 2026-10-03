# JAE v0.4.0 rc2 amendment — external generality and title scope

Date: 2026-10-03

## Trigger

Pre-submission audit of `release/jae-v0.4.0-rc1` identified two reporting/scope problems:

1. previously frozen external boundary tests present on `revision/integrated-ecological-contingency-v1` had disappeared from the v0.4.0 submission manuscript;
2. the title phrase “in bats” exceeded the empirical scope of the terrain-relative segregation/co-use result, which is structurally supported in four panels from two species.

No new same-data mechanism analysis was opened in response.

## Amendment 1 — restore external boundary evidence

Restored to the main Results / Discussion and Supporting Information:

- *Nyctalus noctula*, **first frozen prospective primary**: calibrated excess +0.05175, p=0.1224, n=27, FAIL;
- *Hipposideros armiger/pratti*: -0.04468, p=0.8616, n=13, FAIL;
- *Myotis vivesi*: +0.00470, p=0.4419, n=4, FAIL;
- *Pteropus poliocephalus* centered MSL: +0.16873, p=0.0001, n=4, PASS;
- *Pteropus* centered MSL-minus-DEM: +0.03231, p=0.0023, post-outcome diagnostic;
- *Pteropus* terrain-only individuality: +0.37887, p=0.0034.

The later revised-eligibility positive *Nyctalus* result does not replace the first frozen prospective FAIL.

These tests are reported as **boundary evidence**, not “1/4 prevalence”.

Supporting Information now contains Supporting Table S1 and restores the integrated manuscript's former external **Figure 4** as Supporting Figure S3.

## Amendment 2 — narrow partitioning claim to its empirical scope

Old title:

> Persistent individual vertical strategies need not partition three-dimensional space in bats

rc2 title:

> **Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species**

The two species are:
- *Hypsignathus monstrosus*;
- *Phyllostomus hastatus*.

The four structurally evaluable terrain/co-use panels comprise one *H. monstrosus* panel and three temporal *P. hastatus* panels.

References to “fruit-bat panels” were removed because *P. hastatus* is omnivorous.

## Task-level ecological opportunity

The integrated manuscript's **task-level ecological opportunity** idea is restored only as a post-hoc generated hypothesis:

> repeatable vertical individuality may be more likely when the same ecological task recurs and permits multiple reusable vertical solutions.

It is explicitly not treated as:
- a frugivory-versus-insectivory effect;
- a fitted cross-species explanation;
- a confirmed causal mechanism.

## Word-count control

External boundary evidence was not omitted to meet the word limit. Instead, secondary estimator-method sections already reproduced in Supporting Information were shortened in the main manuscript.

## Evidence guard

`scripts/check_promoted_evidence_v0_4_0.py` now requires the external FAIL/PASS provenance and external-boundary CSV. The rc2 promoted-evidence workflow must fail if these are selectively removed or if the authoritative first *Nyctalus* result is overwritten.

## Scientific stop rule

This amendment changes reporting completeness and claim scope. It does not reopen same-data mechanism search.
