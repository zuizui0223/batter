# Independent common-noctule centered-shape validation v1

## Status

**PROSPECTIVE EXTERNAL VALIDATION — PRIMARY FAIL.**

The source was discovered outside the previously closed Movebank search universe, passed an outcome-blind structural gate, and had its exact eligibility frozen before numeric `Height` values were opened.

### Provenance

Outcome-blind preflight:
- run: `36650800992`
- exact evaluable individual×cohort units: **27**
- exact evaluable target tracks: **47**

Authoritative vertical workflow:
- run: `36652480017`
- head: `676f6b8be7b170ff3fa05ac741a3817514462fb7`
- artifact: `11070953245`
- digest: `sha256:f45311637d9ad097fb4caaa5c24a749ba557131d2ed61a7e639f191211dc4505`

Source:
- *Nyctalus noctula*
- Zenodo DOI `10.5281/zenodo.7535030`
- independent Brandenburg 2019–2020 tracking programme
- raw file `Observed_GPS_locations.csv`
- frozen SHA256 `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`

## Frozen primary result

The predeclared centered full-distribution identity test used:
- session-median-centered native GPS `Height`;
- fixed residual-height bins;
- 5-km horizontal cells;
- equal-session self profiles;
- equal-individual other profiles;
- identical self-derived common-cell weights;
- whole-session identity permutation within year × field-period cohort;
- B = 9,999, seed = 2026093001.

Result:

- evaluable individual×cohort units: **27 / 27 expected**
- observed common-cell centered identity: **−0.018705 nats/fix**
- permutation-null mean: **−0.070453**
- calibrated excess: **+0.051747**
- null SD: **0.045337**
- standardized deviation above null: **1.141**
- null 2.5–97.5% interval: **−0.164707 to +0.009531**
- one-sided p(null >= observed): **0.1224**
- frozen primary verdict: **FAIL**

The calibrated effect is positive, so the observed statistic is better than the pipeline's negative null mean, but it does not pass the predeclared p <= 0.05 threshold.

## Descriptive cohort pattern

Observed individual-mean common-cell scores, **not separately permutation-calibrated by cohort**:

- 2019 early: n=6, mean **−0.0833**
- 2019 late: n=3, mean **−0.0500**
- 2020 early: n=7, mean **+0.0242**
- 2020 late: n=11, mean **−0.0023**

These values are descriptive only. No cohort is promoted to a new inferential panel after the primary failure.

## Interpretation

The five-panel comparative centered-shape result from the original archive does **not** prospectively replicate under the frozen independent common-noctule protocol.

Therefore the ecological rule is not universal across bat tracking systems. At minimum, the strength of repeatable centered vertical organization is **context- or taxon-dependent**.

This independent failure does not invalidate the original five comparative panels. It changes the generality claim:

> repeatable individual organization of vertical space use occurs in multiple bat systems, but is not a universal property detectable under the same centered-distribution estimator in all bat tracking datasets.

The common-noctule result is compatible with a weaker same-direction effect, but the frozen evidence threshold is not met.

## Programme consequence

Per the prospective contract:

- **do not open** speed×turn mechanism replication;
- **do not open** 500-m fine-place mechanism replication;
- **do not open** >=1-day persistence replication;
- **do not switch** to a different vertical field, cohort subset, grid, or external source as rescue.

The independent-validation programme for this source is closed at the primary result.

Further progress requires a newly prospectively defined independent programme or new field data, not post-hoc rescue of this source.

## Claim boundary

- the independent source uses native GPS `Height` as frozen before outcome;
- derived terrain-relative axes are not substituted after failure;
- cohort-specific values above are descriptive and not separate tests;
- frozen v0.3.8 on `main` remains unchanged.
