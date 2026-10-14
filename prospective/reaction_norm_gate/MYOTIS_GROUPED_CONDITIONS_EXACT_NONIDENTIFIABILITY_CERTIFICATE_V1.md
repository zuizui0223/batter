# Exact algebra: original group-coded Myotis data do not identify individual six-regime responses

**Date:** 2026-10-14. **EVIDENCE TYPE:** exact rational mathematical counterexample, **no real bat physiological outcome opened**. Source-structure reference: [original Mendeley v3 file eligibility ledger](MYOTIS_2025_V3_ORIGINAL_CATEGORICAL_ELIGIBILITY_RESULT_2026_10_14.md); [Figure 3 verified individual-join STOP](MYOTIS_FIG3_INDIVIDUAL_JOIN_GATE_VERIFIED_2026_10_14.md).

The original six moving regimes in the published Methods are arranged:

```text
j0:  0.08m, 0.5m/s      easy
j1:  0.08m, 1.0m/s      easy
j2:  0.08m, 1.3m/s      easy
j3:  0.24m, 0.5m/s      easy
j4:  0.24m, 1.0m/s      difficult
j5:  0.24m, 1.5m/s      difficult
```

The public `lData.csv` retains only `treat_code` categories stationary (1), easy (2), difficult (3). Take the **most favorable idealization** of equal physical-regime weights; it is not an assertion that the original unlabelled trials have equal treatment counts. Then individual/day physical-regime means `y=(y0,...,y5)` project to only two moving-group means:

```text
          [ 1/4  1/4  1/4  1/4   0    0 ]     [ y0 ]
mu = A y, A = [                                ]  y=[ y1,...,y5 ]'
          [  0    0    0    0   1/2  1/2]
```

`rank(A)=2`. The linear null space `ker(A)` has dimension **4**. An explicit independent rational basis is:

```text
(-1,+1, 0, 0, 0, 0)
(-1, 0,+1, 0, 0, 0)
(-1, 0, 0,+1, 0, 0)
( 0, 0, 0, 0,-1,+1)
```

**Constructive impossibility:** these two purely fabricated six-regime response vectors produce exactly the same observable group averages:

| SYNTHETIC field | World 1 | World 2 |
|---|---:|---:|
| `y0,...,y5` | `1,2,3,4,5,6` | `0,3,3,4,5,6` |
| Easy-group mean | 2.5 | **2.5** |
| Difficult-group mean | 5.5 | **5.5** |
| 2×2 speed effect `(-y0+y1-y3+y4)/4` | **0.5** | **1.0** |
| Nominal 160ms pair effect `y5-y0` | **5.0** | **6.0** |

The displayed synthetic units are arbitrary; they are *not* observed buzz ms, sound production, or trial outcomes. The original paper's variable- and group-specific inclusion policies and unknown regime-specific eligibility counts can cause **more**, not less, ambiguity. The proof already defeats unique nonparametric recovery under the simplified most-favorable equal-weight mapping.

## Practical inference consequences

1. With only two movement-group categories, more trials can reduce uncertainty about the two group means, **not** reconstruct the four lost response dimensions. Arbitrary machine-learning flexibility cannot invert this rank-deficient observation process.
2. A parametric model could impose assumptions to assign six responses, but these assumptions—not the released observation—would identify a unique solution; this cannot be advertised as personal coefficients empirically recovered from source.
3. Figure-3 pulse-alignment data has the names `treat_code`, `trial_id`, `time_t0_ms`, `norm_ci`, and no bat/date join identifiers. It cannot supply missing six physical treatment IDs or known individual/occasion correspondence.
4. Even the two coarse moving-group responses do not automatically support a repeatable four-bat scalar Buzz-II policy, because the original source's later sessions have sparse/absent usable Buzz II in some bat×condition cells.
5. An externally verified original trial-level `bat_id × date × speed × displacement × physical_motion_onset × acoustic_outcome` archive could reverse this **source** STOP. Do not assume such files exist or mix field and captive animals to complete the design.

**Inference ceiling:** `STOP_NONIDENTIFIABLE_6_REGIME_PERSONAL_FEEDBACK_FROM_PUBLISHED_TABLES`. This is an exact mathematical nonidentifiability claim about the released measurements, **not a proof of biological randomness or impossibility of describing individual bat behavior with equations**.
