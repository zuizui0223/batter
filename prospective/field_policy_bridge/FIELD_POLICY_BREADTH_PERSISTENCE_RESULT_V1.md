# Field policy breadth persistence result v1

## Status

- **2022: UNSUPPORTED under the frozen primary rule.**
- **2023: STRUCTURAL STOP before a breadth-persistence statistic.**

**Evidence provenance:** all H/V statements in this file are conditional on a post-outcome component representation opened after the frozen scalar field gate failed. They characterize exploratory field structure; they do not rescue or replace the 2/4 frozen carrier result. See `FIELD_EVIDENCE_PROVENANCE_GUARD_V1.md`.

Authoritative workflow:
- run: **37304532819**
- job: **111744917325**
- head: `87825504a1f57e47d45c7d8d547a44d2044fc809`
- workflow conclusion: **success**.

Parent:
`FIELD_POLICY_BREADTH_PERSISTENCE_CONTRACT_V1.md`

## Question

Do individuals retain a repeatable degree of within-individual H/V policy breadth after peer-day adjustment?

The primary compares each individual's early log-breadth with:
- its own late log-breadth;
- other individuals' late log-breadths in the same cohort.

Frozen support required:
- (K_W>0);
- p <= 0.05;
- >=70% positive individuals.

## 2022

Evaluable individuals:
**16**

Primary:
- (K_W = +0.18142)
- positive individuals: **11/16 = 68.75%**
- null mean: **-0.00240**
- null 95% interval: **[-0.24365, +0.25510]**
- one-sided p: **0.0899**
- verdict: **UNSUPPORTED_POLICY_BREADTH_PERSISTENCE**

Both inferential gates fail:
- p > 0.05;
- positive fraction is below the frozen 70% threshold.

### Frozen secondary descriptive result

Early-versus-late log-breadth:
- Spearman rho = **+0.6294**
- two-sided p = **0.0090**

Median policy breadth:
- early: **0.2380**
- late: **0.4089**

This correlation is not promoted because the primary failed, exactly as specified by the contract.

The pattern may motivate independent work on behavioural predictability, but it is not current evidence for a confirmed persistent breadth phenotype.

## 2023

No individual had the frozen minimum of six eligible peer-day policy days.

Therefore:
- candidate individuals = **0**;
- verdict = **STOP_STRUCTURAL_SUPPORT**.

The six-day threshold is not lowered.

This is not a negative biological result.

## Main inference

The field evidence currently supports a persistent **location/bias in policy space** more strongly than a persistent full personal distribution.

Specifically:
- low-dimensional H/V identity is repeatable;
- stable individual variance remains after source-day effects are partitioned;
- peer-day residual identity remains;
- but individual reaction slopes are unsupported;
- prior-centroid forecasting is not majority-consistent;
- repeatable policy breadth fails its frozen primary in the only evaluable year.

Therefore do not write:

> each individual has a stable personal probability distribution with a fixed center and width.

The stronger defensible statement is:

> **each individual carries a persistent low-dimensional policy bias/center, while the breadth and context-dependent realization around that center remain substantially variable and are not yet shown to be stable individual traits.**

## Boundary on behavioural predictability

The 2022 secondary rho is compatible with persistent differences in behavioural predictability, but the primary identity-matching test does not clear its predeclared threshold.

Do not:
- call breadth repeatable;
- lower 70% to 68.75%;
- switch to the secondary Spearman test as the primary;
- lower the six-day gate in 2023;
- select H-only or V-only after seeing the 2-D result.

## JAE firewall

No change to JAE v0.4.0.
