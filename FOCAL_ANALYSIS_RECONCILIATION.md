# Reconciliation of focal *Tadarida* analysis generations

Date: 2026-09-26

Two analysis families in this repository ask related but non-identical questions about the same
*Tadarida teniotis* tracking study. Both are retained because they provide different evidence
about individual non-exchangeability.

## Legacy early/late identity-assignment family

This family was added independently on `main` before the v0.3 synthesis branch was merged.

### V1 — conditional identity assignment

Each bat's early individualized `P_i(z|cell)` map was scored against every bat's later events
inside the same 18 frozen 5-km cells, with fixed shrinkage toward the species distribution.

Result:

- observed diagonal mean gain: **+0.1682 nats/event**;
- exact 8! identity-permutation **p = 0.000174**;
- 6/8 own-map gains positive;
- strict top-1 own map: 5/8.

This is strong evidence that individual identity contains temporally repeatable vertical-state
information.

### V2 — residual individual-by-location assignment

The same early/late identity test was repeated after constructing a marginal-altitude-adjusted
cell baseline.

Result:

- observed residual diagonal: **+0.0240**;
- exact permutation **p = 0.160**;
- 5/8 diagonal residuals positive.

Under that frozen assignment test, a stable source-identity-specific cell interaction was **not**
supported.

### V3 — simple component decomposition

Altitude-only and horizontal-only identity assignments were each more identity-matched than
random permutation, but each beat its pooled baseline for only 4/8 bats under the frozen rule.
The terminal mechanistic category was therefore unresolved.

## v0.3 cross-session architecture family

The later ecological programme uses a different validation target:

`same animal on another discrete tracking session > other animals`.

Important design differences are:

| Dimension | Early/late family | v0.3 session family |
|---|---|---|
| Temporal unit | first versus second half of each individual's eligible fixes | leave-one-BatDay/session-out |
| Focal support | same 18 frozen cells | target fixes on common support of self and alternative predictors |
| Individual model | fixed lambda shrinkage toward species | equal-session/individual probabilities with Jeffreys smoothing |
| Main contrast | exact identity assignment permutation | predictive self-versus-other log-score gain |
| Data stream | raw native MSL tracking stream | matched annotated stream for MSL/AGL/terrain decomposition |
| Inference emphasis | strict global identity assignment | ecological architecture and independent replication |

At 5 km, the session family gives:

- MSL conditional identity +0.428;
- MSL marginal identity +0.052;
- MSL place × height increment +0.376;
- AGL place × height increment +0.591.

## Why these results are not interchangeable

A positive mean `conditional - marginal` prediction gain does not imply that an 8×8
source-to-target interaction matrix must pass the exact permutation test used in legacy V2.

The legacy V2 null asks whether the correctly labelled set of eight individual interaction maps
is unusually well aligned relative to **all identity permutations** under a fixed shared-cell
and shrinkage architecture.

The v0.3 endpoint asks whether, for a held-out session, **that same animal's other session(s)**
carry more predictive information than alternatives on jointly supported target fixes.

The first is a stricter global identity-map assignment statement; the second is a
cross-session ecological repeatability statement.

## Synthesis

The two families agree on the core result:

> individual bats are not exchangeable in vertical-state use across time.

They differ on how strongly one can claim a single stable individual-by-cell map in the focal
eight-bat sample.

Accordingly, the v0.3 paper should **not** claim that legacy V2 was positive. The stronger
place-coupled interpretation rests on the session-based MSL/AGL/terrain decomposition, same-night
control, direct pairwise tests and prospective independent taxa.

The legacy negative remains useful: it motivates the current conclusion that individual
specialization is an **architecture of predictive information**, not necessarily one immutable
3-D reaction map.
