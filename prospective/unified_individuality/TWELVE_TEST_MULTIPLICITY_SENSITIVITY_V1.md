# Twelve displayed field tests: an expanded Holm-family sensitivity audit

**Date:** 2026-10-15  
**Status:** Additional **post-outcome arithmetic sensitivity**. No primary GPS/DEM source records, 9,999-permutation outputs, biological eligibility rules, source nulls, species units, treatment outcomes or source-frozen inferential declarations were modified or rerun.

## The reviewer question

Does the statement "terrain-relative flight-height individuality is still 4/4 significant after Holm" depend on placing **only the four V_rel tests** in one family, when the same four study panels were also assessed for added segregation (S_rel) and contemporaneous co-use separation (I)?

**Yes.** The original 4-test Holm result remains true for that specific *within-V_rel* family, but it should not be described as an unqualified robust four-panel finding across the entire displayed field-test suite.

## Contrasting two post-outcome families (same original p-values)

We apply the **standard step-down Holm procedure** in two *illustrative, retrospectively selected* ways:
1. **Within endpoint:** three separate four-panel families, one each for V_rel (one-sided individual-fidelity upper-tail), S_rel (two-sided deviation around its own permutation-null mean) and co-use I (upper-tail phase-shift test). This reproduces the earlier [four-panel arithmetic audit](FOUR_PANEL_MULTIPLICITY_SENSITIVITY_V1.md).
2. **Across displayed field suite:** one combined twelve-test family containing those same **3 × 4 original source p-values**. We add no other hypothesis or outcome, and no p-values are changed.

| Source panel | Endpoint | Original source p | Holm within 4 | Holm across all 12 |
|---|---|---:|---:|---:|
| *H. monstrosus* | V_rel | 0.000100 | 0.000400 | **0.001200** |
| *P. hastatus* 2022 | V_rel | 0.000100 | 0.000400 | **0.001200** |
| *P. hastatus* 2023 | V_rel | 0.0001016 | 0.000400 | **0.001200** |
| *P. hastatus* 2016 | V_rel | 0.034528 | 0.034528 | **0.276221** |
| *H. monstrosus* | S_rel (two-sided; negative observed) | 0.036200 | 0.144800 | 0.276221 |
| *P. hastatus* 2022 | S_rel (two-sided) | 0.363900 | 0.811338 | 1.000000 |
| *P. hastatus* 2023 | S_rel (two-sided) | 0.270446 | 0.811338 | 1.000000 |
| *P. hastatus* 2016 | S_rel (two-sided) | 0.479584 | 0.811338 | 1.000000 |
| *H. monstrosus* | co-use I | 0.904500 | 1.000000 | 1.000000 |
| *P. hastatus* 2022 | co-use I | 0.918600 | 1.000000 | 1.000000 |
| *P. hastatus* 2023 | co-use I (positive observed) | 0.023100 | 0.092400 | **0.207900** |
| *P. hastatus* 2016 | co-use I | 0.861100 | 1.000000 | 1.000000 |

### Counts using the uncorrected vs two illustrative correction families

| Endpoint | Original nominal p ≤ 0.05 | Within-endpoint 4-test Holm | 12-test Holm |
|---|---:|---:|---:|
| Terrain-relative vertical individuality V_rel | 4/4 | 4/4 | **3/4** |
| Added terrain-relative segregation S_rel, two-sided | 1/4 (negative H direction) | 0/4 | 0/4 |
| Extra co-use separation I, one-sided | 1/4 (positive P2023 direction) | 0/4 | 0/4 |

**Key arithmetic:** among twelve ordered raw p-values, the fourth is co-use P2023 (0.0231) and the fifth is V_rel P2016 (0.034527622...). The Holm step-down maximum gives an adjusted **0.27622098** to P2016, while the three small V_rel p-values become **0.0012**. The nominally positive co-use P2023 becomes **0.2079**.

## The valid ecological interpretation

There is **stronger and more resilient evidence for individual-predictive terrain-relative flight-height use in three of the four displayed panels** than for additional vertical segregation under either displayed multiple-testing sensitivity. Under the originally defined source-specific per-panel tests, the fourth V_rel result **was supported** (raw p = 0.03453), so it must not be retroactively called an original failure; rather, its apparent robustness is more sensitive to the post-hoc choice of multiplicity family. All four studies cover only **two species**, not four independently sampled taxa.

This is a **difference in patterns of detectable evidence**, not a statistically established comparison between effect magnitudes, power or causation. Failed detection of positive S_rel or co-use I is not proof that competition, spatial partitioning, social interactions or resource differences do not exist. Native O_XY within-individual overlap was descriptively greater than between-individual overlap, so no absence of horizontal differentiation may be inferred.

## Why 12 tests are still NOT comprehensive multiplicity control

- Both the within-endpoint four-test families and the twelve-test display suite were **defined after the original outcomes were observed**. Neither should be described as a prospectively registered familywise test.
- The twelve selected p-values are **not all tests conducted in the programme**. The broader 23-parent source screening, six original wild panels, additional matching/lag tests, multiple experimental systems, different null architectures, source treatment choices and post-outcome analyses are not included.
- The three *P. hastatus* years are separate panels but not three independent bat species. Holm is mathematically valid under arbitrary test dependence **when each input p-value is valid and a family is properly defined**; statistical validity and ecological generalization cannot be presumed from a correction alone.
- Different sampling windows (60/600 s), all-space versus endpoint-excluded co-use definitions, device-height datums and support denominators remain.
- The exercise does **not** justify a new broad "bat individuality is universally robust" claim, nor a "zero segregation" equivalence statement, nor an independently tested universal mechanistic law.

## Reproducibility

Original-source hashes are unchanged. All values come from [source-locked original field summary](figures/FROZEN_FIGURE_DATA_V1.json) and [the prior 4-test correction ledger](figures/FROZEN_FOUR_PANEL_MULTIPLICITY_V1.json). A new machine-readable [12-test ledger](figures/FROZEN_TWELVE_TEST_MULTIPLICITY_V1.json) stores exact source p-values, the four-test and twelve-test adjusted values, the field-test family definitions and all interpretation limits. The [extended independent verifier](validate_four_panel_multiplicity_v1.py) recomputes both corrections from byte-pinned original source p-values in GitHub Actions. None of these documents is an original animal-data analysis or a standalone prospective statistical test.

**Recommended publication wording:** "Terrain-relative individual vertical fidelity was detected in four original field panels; all four retained support under a post-outcome within-endpoint four-panel Holm check, whereas three remained below 0.05 when all twelve displayed terrain-fidelity, added-segregation and co-use tests were treated as one illustrative family. No positive added terrain-relative vertical segregation result was supported under the original panel-specific nulls, but equivalence to zero was not established."
