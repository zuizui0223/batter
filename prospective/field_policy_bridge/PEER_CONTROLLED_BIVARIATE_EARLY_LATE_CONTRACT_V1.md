# Peer-controlled bivariate early-to-late policy persistence contract v1

## Status

**POST-OUTCOME STABLE-POLICY FALSIFICATION DIAGNOSTIC.**

Frozen after:
- the fixed-bin 2-D horizontal × vertical field carrier was supported in P. hastatus 2022 and 2023;
- the 1-D allocation axis showed strict-past self-prediction;
- short-term allocation-state autocorrelation disappeared after contemporaneous peer correction;
- peer-controlled 1-D allocation early-to-late persistence did not meet the predeclared support rule.

No peer-controlled **2-D** early-to-late identity result has yet been calculated.

## Question

After removing movement-policy shifts shared with contemporaneous conspecifics, does the full two-dimensional personal policy remain stable from the early to the late part of an individual's record?

## Data

Use exactly the fixed-bin 360-s P. hastatus sessions and the source-frozen two-dimensional policy

`P=(H,V)`

from `PHYLLOSTOMUS_FIXED_BIN_BIVARIATE_CARRIER_CONTRACT_V1.md`.

Analyse 2022 and 2023 separately.

## Contemporaneous peer correction

For each focal session q of individual i, cohort c, start time t:

1. consider policy-valid sessions from other biological individuals only in c;
2. retain sessions with start time within ±12 h of t;
3. average 2-D policy vectors within each donor individual first;
4. average donor-individual vectors equally;
5. require at least 2 donor individuals.

Define residual policy vector:

`P*_{iq}=P_{iq}-mean_peer(P)`.

No focal observation contributes to its peer control.

## Individual support

Require at least 4 peer-controlled sessions for an individual.

Sort by source start time.

Split after floor(n/2):
- early = first floor(n/2);
- late = remaining.

Require at least 2 early and 2 late sessions.

Early personal centroid:

`theta_i^early = mean(P* early sessions)`.

## Primary held-out late identity advantage

For every late target vector of focal i:

- self distance = Euclidean distance to focal early centroid;
- donor distance = equal-donor mean Euclidean distance to early centroids of other eligible individuals in the same frozen cohort.

Require at least 2 donor individuals.

`K_q = D_other - D_self`.

Aggregate:
- equal late targets within biological individual;
- equal biological individuals within year.

Primary statistic:
`K_2D_early_to_late`.

## Null

Within each frozen cohort:
- keep every early 2-D centroid fixed;
- keep every late target vector and target identity fixed;
- permute the mapping of early centroids to biological individual labels.

Thus the null preserves:
- cohort structure;
- contemporaneous peer correction;
- early centroid distribution;
- late target distribution;
- sample support.

It destroys only early-to-late biological identity correspondence.

9,999 permutations.

Seeds:
- 2022: `202610051611`
- 2023: `202610051612`.

One-sided positive p.
Require >=9,500 valid permutations.

## Support rule

A year supports stable peer-controlled 2-D policy persistence if:
- K > 0;
- p <= 0.05;
- >=70% evaluable biological individuals have positive individual K.

## Secondary descriptive quantities

Report by cohort:
- Spearman correlation of early vs late H residual centroids;
- Spearman correlation of early vs late V residual centroids;
- Procrustes-free Euclidean early-to-late centroid error.

No secondary p-values and no rescue.

## Interpretation

### Supported

The strongest field carrier survives removal of shared short-term environmental shifts.

This supports a persistent individual-specific movement-policy offset, even though short-term within-individual deviations themselves do not show robust autonomous state propagation.

### Unsupported

The field 2-D carrier may be substantially entangled with shared temporal context, and the field data do not independently establish a stable personal policy after peer correction.

## Ceiling

Support does not identify whether the persistent policy originates from morphology, physiology, development, or long-term learning.
