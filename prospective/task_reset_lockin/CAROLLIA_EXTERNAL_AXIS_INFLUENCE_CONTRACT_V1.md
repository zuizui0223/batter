# Carollia external axis decomposition and influence contract v1

## Status

**POST-EXTERNAL-PRIMARY ROBUSTNESS / BOUNDARY DIAGNOSTIC.**

Frozen after the prospectively fixed 2-D representation passed external validation in *Carollia perspicillata*.

No component-specific permutation p-value or leave-one-trial influence result has yet been calculated.

Parent:
- `CAROLLIA_FIXED_TWO_AXIS_VALIDATION_CONTRACT_V1.md`

## Why this diagnostic is needed

The supported fixed 2-D external result was:

- K_2D = 0.34758;
- 6/7 bats positive;
- both date blocks positive;
- p = 0.0007.

Descriptive component statistics were:

- I_K = 0.36775;
- M_K = 0.08933.

Thus the 2-D external result could be carried mostly or entirely by FlightIntensity.

In addition, one valid public track has a very large reported 3-D path length relative to the other trials. The frozen primary correctly retained it because no plausibility filter was preregistered. Robustness to any one removable trial must therefore be checked transparently.

---

# D1 — external FlightIntensity component

Use the exact already-computed fixed standardized axis:

`I = mean(z1,z2,z3,z4)`.

Use the exact Carollia identity statistic and date-block aggregation from the external primary.

Calibrate with the same date-block label permutation architecture.

9,999 permutations.
Seed:
`202610051201`.

Report:
- I_K;
- date-block means;
- bat means;
- positive fraction;
- one-sided p.

Diagnostic support:
- K > 0;
- p <= 0.05;
- >=70% bat means positive;
- both date-block means positive.

---

# D2 — external ManeuveringExtent component

Use exactly:

`M = mean(-z1,z5,z6,z7,z8)`.

Same statistic, weighting and null.

9,999 permutations.
Seed:
`202610051202`.

Same diagnostic support rule.

---

# D3 — incremental value of adding M to I

For every observed/permuted labeling calculate:

`DeltaK = K_2D - K_I`.

9,999 permutations using the same label permutation within each date block.

Seed:
`202610051203`.

Report:
- observed DeltaK;
- null mean and 95% interval;
- one-sided p for DeltaK > null.

Interpretation:
- positive supported DeltaK: M adds externally transferable individual information beyond I under this Euclidean identity statistic;
- zero/negative unsupported DeltaK: external validation is carried by I; do not claim cross-species support for the second axis.

No alternative metric may be substituted after seeing DeltaK.

---

# D4 — leave-one-removable-trial influence audit

Use the exact original feature extraction and date-block z-standardization.

A trial is **removable** only when deleting it leaves its bat with >=3 valid trials, preserving the original structural minimum.

For every removable trial independently:

1. delete exactly that one trial;
2. recompute date-block mean/SD standardization from the remaining trials;
3. recompute fixed I and M;
4. recompute observed K_2D, K_I and K_M;
5. record date-block and bat means.

No permutation p-values are required for each jackknife replicate; this is an influence diagnostic.

Report:
- number of removable trials;
- min/median/max K_2D;
- min/median/max K_I;
- min/median/max K_M;
- the deletion causing minimum K_2D;
- the deletion causing minimum K_I;
- the result obtained when deleting `C3_2_20231216_traj_bat_pos_RESULTS.mat`, if structurally removable;
- whether K_2D remains >0 in every removable-trial deletion;
- whether both block means remain >0 in every removable-trial deletion.

## Interpretation

If fixed 2-D support remains directionally positive under every removable deletion, the external result is not a single-trial artifact.

If the extreme track deletion materially collapses K, explicitly bound the external claim.

## Claim ceiling

This diagnostic can refine which axis generalizes and how influential individual trials are.

It cannot retroactively change the prospective external PASS criterion.
