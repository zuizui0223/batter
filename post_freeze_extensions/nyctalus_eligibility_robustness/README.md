# Nyctalus eligibility robustness v1

This branch contains a **post-outcome sensitivity diagnostic**, not a new prospective validation.

Purpose: quantify how the centered vertical-identity estimate changes when only the minimum number of presence-qualified fixes required per source track is varied.

Frozen thresholds: 0, 20, 30, 40, 50, 75, 100 fixes/track.

Everything else is fixed to the existing 5-km centered-identity estimator:
- Year × field_period cohorts;
- full-track median centering;
- frozen residual-height bins;
- >=50 scored common-support target events;
- identical common-cell weighting for self and other profiles;
- whole-track identity permutations within cohort;
- B=9,999, seed=2026093001.

The 0-fix and 50-fix endpoints are already-opened anchors. They are used only as regression checks:
- 0 reproduces the later revised-eligibility analysis (n=36);
- 50 reproduces the original prospective primary analysis (n=27).

No threshold may be promoted because of its p-value. The original >=50-fix test remains the confirmatory external result.
