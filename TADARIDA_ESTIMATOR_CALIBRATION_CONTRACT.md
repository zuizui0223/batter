# Tadarida estimator calibration v1 — frozen diagnostic contract

Frozen: 2026-09-27

## Why this exists

A post-freeze audit identified two estimator-level risks in the comparative architecture score:

1. finite conditional cell counts plus Jeffreys smoothing can make
   `G_adv = G_cond - G_marg` have a non-zero null expectation;
2. the ordinary marginal score can inherit horizontal specialization because each individual's
   marginal height distribution is integrated over its own cell-use distribution.

This calibration is therefore **post hoc with respect to the original biological result**, but
the calibration algorithm below is frozen before its real-data output is opened.

It cannot redefine or rescue the frozen primary endpoint. It is allowed to weaken the paper.

## Exact target

The target is the paper-facing *Tadarida teniotis* MSL panel:

- checksum-pinned annotated Movebank table;
- `animal-id × BatDay` sessions;
- EPSG:3035;
- 5-km cells;
- MSL bins `[-inf,0,50,100,200,400,800,1600,3200,inf]`;
- Jeffreys alpha 0.5;
- >=50 fixes per retained session and >=50 scored target fixes;
- equal-session self predictor;
- equal-individual other predictor.

Before any calibration result is accepted, the implementation must reproduce exactly:

- G_cond = 0.42804057006673096
- G_marg = 0.052484319998149565
- G_adv = 0.37555625006858145
- 6 evaluable individuals

Absolute tolerance: 1e-12.

## A. Session-label permutation calibration

Permute **whole session blocks**, never fixes.

For each of 9,999 Monte Carlo replicates, using NumPy PCG64 seed 20260927:

- retain every session's x-y-z observations unchanged;
- retain session size and coverage unchanged;
- retain the original number of sessions assigned to every individual label;
- randomly assign the label slots to the fixed session blocks;
- rerun the frozen scoring algorithm without changing any threshold.

Report the null mean, SD, 2.5/50/97.5% quantiles, observed-minus-null-mean and one-sided
Monte Carlo tail probability `P(null >= observed)` for G_cond, G_marg and G_adv.

The null distribution of the number of evaluable pseudo-individuals is also reported rather than
conditioned away.

## B. Common-cell-weighted marginal

For a held-out target, use the cells supported by both conditional predictors.

Within those cells, construct a self cell-use weighting by:

1. calculating cell frequencies separately for every self-training session;
2. averaging those frequency vectors equally across self sessions;
3. renormalizing over common supported cells.

Apply the **same** weights to both conditional vertical profiles:

`M_self^w(z) = sum_c w_self(c) P_self(z|c)`

`M_other^w(z) = sum_c w_self(c) P_other(z|c)`.

Score the held-out target using `log M_self^w(z) - log M_other^w(z)`.

This is the common-cell-weighted marginal identity. Also report:

`G_adv^w = G_cond - G_marg^w`.

This diagnostic cannot replace the frozen marginal endpoint.

## C. Individual bootstrap

Using the frozen observed evaluable individuals, run 20,000 individual-level bootstrap
replicates with PCG64 seed 20260928 and report percentile 95% intervals for all five metrics.

## Stop rule

Once the real-data output is opened, nothing above may be retuned.

A null-compatible result weakens the paper. A strong calibrated result is reported as a
post-freeze robustness check, not retrospectively labelled confirmatory.

Roost exclusion is deliberately not bundled into v1 because no outcome-independent roost
definition/radius has yet been frozen.
