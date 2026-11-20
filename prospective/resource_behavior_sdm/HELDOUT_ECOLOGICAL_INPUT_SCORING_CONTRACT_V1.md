# A runnable, biology-safe grouped conditional-height model (2026-11-20)

Source-free implementation; it does not fit the original 2026 *Chrotopterus auritus* source or true-food Ducke plot data, both of whose original contents remain unavailable through the official Dryad file API (HTTP 401).

`grouped_resource_vertical_validation_v1.py` takes already-qualified source observations with independently determined categorical height bins, original GPS fix flags, night identifier, original bat identity, study site, time, x-y-only kinematic state, measured habitat class, and optional independently/time-matched *true food availability*. It fits and compares three progressively augmented conditional height distributions:

1. `kinematic_time`: p(height class | time, x-y kinematic state)
2. `add_habitat`: + 10-m measured/classified vegetation context (habitat NOT prey)
3. `add_true_food`: + external timed food-source class, only if every source event carries independently verified food and matched sampling dates.

Source rows are validated fail-closed; interpolated points are not treated as new measured GPS fixes. A full **individual**, full source **site** or **bat-night** is held out, while no individual identifier enters the trained predictor. Categorical tables are fit using Jeffreys 0.5 global prior and a fixed conditional shrinkage constant 1. Training bats each contribute equal total weight; nights are equal within bat; frames are equal only within each night. All model comparisons evaluate identical heldout observations; unseen categorical contexts back off to the training-only marginal and their support fraction is reported, not silently skipped.

The scorer returns group-equal predictive log-score differences, total eligible biological groups, and diagnostic context support. **It does not report a fix-level p-value, treat autocorrelated fixes as independent animals, or imply causal resource choice.** Raw bat IDs should not be persisted in public output receipts; the returned fold detail includes original heldout group labels in memory for inspection by an authorized data steward. For publication only aggregate/source-redacted outputs are allowed.

Source-free tests demonstrate that habitat genuinely predictive of the target height in a constructed world improves heldout prediction, while absent independently measured food refuses the trophic model. Synthetic test success is not new animal evidence.

## Next original source admission

- *Chrotopterus auritus* 2026: publisher original metadata 5/5 PASS at [Actions #44729699721](https://github.com/zuizui0223/batter/actions/runs/44729699721); original raw ZIP file HTTP401 at [Actions #44729946430](https://github.com/zuizui0223/batter/actions/runs/44729946430). Need genuine source raw height; height is MSL, **not above-ground flight altitude**; use source geography and sensor QC and an independently supplied terrain reference before making AGL interpretations.
- Ducke 2018: publisher original metadata 1/1 PASS in same Actions; direct 67.7-kB resource-bat XLSX also HTTP401. **No individual 3D flight height** so its food data can test a different local resource-dependent capture model once independently obtained, not enter this height scorer.

Do not fit true-food and high-dimensional resource-height values by joining these two incompatible studies or by substituting source GBIF recording intensity for independently measured flowers/fruit/insect biomass.
