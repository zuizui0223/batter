# Yamada personal speed-state persistence result v1

## Status

**PROSPECTIVE SCALAR PRIMARY — SUPPORTED.**

Branch:
`prospective/learning-state-theta-v1`

Source:
Yamada et al. 2020, *Scientific Reports* 10:10751.

Public row dataset:
`10.6084/m9.figshare.19102712.v1`

Frozen parent:
`PERSONAL_SPEED_STATE_CONTRACT_V1.md`

Authoritative workflow:
- run: **37245335080**
- artifact: **11318159879**
- artifact ZIP SHA256: `71c482f0facb7faaf9bda352859bab29b71f708eeec4ed4a20b71c7eead369b2`

## Provenance

The source structure was opened before the speed outcome:
- 14 unique bats;
- 7 in condition 1;
- 7 in condition 2;
- exactly one trial-1 and one trial-12 row per bat.

The 28 source rows were crosswalked to the 28 raw trajectory sheets under a separate outcome-blind provenance gate.

The planned eight-dimensional raw-coordinate analogue was stopped before an identity outcome because no bat cleared the frozen >=100-row support rule. That failure was not rescued.

This result therefore uses the separately frozen **source-native maximum-flight-speed scalar** only.

## Published learning shift reproduced

Raw maximum speed means:

| condition | trial 1 | trial 12 | mean within-bat change |
|---|---:|---:|---:|
| 1 — permeable/chain | 2.4640 m/s | 3.3565 m/s | +0.8925 m/s |
| 2 — reflective/acrylic | 2.5481 m/s | 2.8215 m/s | +0.2734 m/s |

The larger speed shift in the permeable condition reproduces the published learning result.

These mean shifts are inherited/source-reproduction quantities, not the new primary.

## Frozen personal-state calculation

Within each acoustic condition and trial, the trial mean was subtracted.

The resulting residuals were divided by a frozen pooled within-state scale.

For a trial-12 target bat i:

[
K_i =
mean_{j\ne i}|z_{i,12}-z_{j,1}|
-
|z_{i,12}-z_{i,1}|.
]

Positive K means the familiar-flight speed state is closer to that bat's own naive-flight state than to other bats' naive states after the common learning shift has been removed.

Programme statistic:
equal-condition mean of condition-specific equal-bat K.

## Primary result

[
K = +0.527710.
]

Frozen 9,999 within-condition trial-1 label permutations:
- null mean: +0.00126;
- null 95% interval: [-0.37825, +0.40356];
- one-sided p: **0.0052**.

Individual direction:
- condition 1: **5/7 positive**;
- condition 2: **7/7 positive**;
- overall: **12/14 positive**.

All frozen support rules were satisfied.

Verdict:
**SUPPORTED_PERSONAL_SPEED_STATE_PERSISTENCE**

## Individual K

Condition 1:
- bat 1: +1.07449
- bat 2: +0.84797
- bat 3: +0.07273
- bat 4: -0.61733
- bat 5: -1.87349
- bat 6: +1.07559
- bat 7: +0.65039

Condition 2:
- bat 8: +0.86485
- bat 9: +1.31068
- bat 10: +1.42787
- bat 11: +0.96345
- bat 12: +0.41339
- bat 13: +0.05229
- bat 14: +1.12505

## Secondary diagnostics

Across both conditions after state-specific centering/scaling:
- pooled Pearson trial-1 -> trial-12 residual correlation: `r=0.4551`, one-sided permutation `p=0.0586`;
- through-origin magnitude slope: `beta=0.3775`, `p=0.0586`;
- equal-pair order accuracy: **0.7619**, null approximately 0.50, `p=0.0114`.

Condition-specific order accuracy:
- condition 1: 0.5714;
- condition 2: 0.9524.

These secondary quantities do not replace the supported frozen self-versus-other primary.

## Biological interpretation

The same individual can change its absolute speed substantially with spatial learning while retaining information about its personal faster/slower state.

The supported statement is:

> **a shared learning shift occurs on top of a persistent personal speed-state component.**

This directly argues against both extremes:
- individuality requires a fixed exclusive spatial niche;
- individuality is completely overwritten whenever the animal learns a new task state.

It is consistent with:

[
behaviour =
shared\ learning\ state
+
personal\ control\ prior
+
residual\ task\ response.
]

## Ceiling

This result does not establish that:
- maximum speed is the full personal flight policy;
- the Yamada speed scalar is numerically identical to the Teshima FlightIntensity axis;
- the stable component is genetic, morphological or physiological;
- individual ordering is equally persistent under both acoustic learning conditions.

The condition asymmetry is examined separately in
`CONDITION_PERSISTENCE_DIAGNOSTIC_RESULT_V1.md`.

## JAE firewall

No change to JAE v0.4.0.
