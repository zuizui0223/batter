# Biological effect-translation null calibration v1 — frozen contract

Frozen: 2026-09-27, before any new effect-null output.

## Principle

The paper's own estimator audit established that finite-sample pipeline nulls need not equal the
intuitive zero baseline. The same standard now applies to the two headline biological
translations.

## Pairwise self-identification

For all six panels, retain the exact observed pairwise self-win definition already frozen in
`biological_effect_translation_v1`.

Re-run that entire statistic under the **same whole-session label permutation design and seed**
already used for that panel's estimator calibration.

Report, per panel:

- observed self-win fraction;
- permutation-null mean and SD;
- 2.5%, 50%, 97.5% null quantiles;
- observed minus null mean;
- one-sided P(null >= observed).

The panel-specific permutation-null mean becomes the inferential baseline. **0.5 is only an
intuitive reference.**

A pairwise rate may remain a main-text calibrated biological translation only when its excess
above the panel-specific null is positive and the one-sided tail is <=0.05. Otherwise it is
descriptive/SI and cannot serve as independent evidence.

## *Tadarida* AGL metre separation

Frozen observed consistency target:

- equal-individual mean absolute separation = 256.4593439137133 m;
- median individual separation = 144.5732455509692 m;
- 12 evaluable target sessions.

Keep the existing statistic:
`|self_expected_AGL - other_expected_AGL|` under common self-session horizontal weights.

Use the exact focal AGL session-label null already frozen for AGL calibration:

- B = 9,999;
- seed = 2026092901;
- whole session blocks;
- exact label-slot multiset preserved.

Report the raw 256.459 m, the null mean, calibrated excess, null quantiles, and one-sided tail.

If calibrated excess is not positive or p>0.05, **256 m is removed as a headline main-text
magnitude** and retained only as raw descriptive context with its non-zero null.

Do not switch after output to a target-error statistic or any other metre-scale definition.

## Figure rule

Pairwise figures use panel-specific null means as the inferential baseline. A 0.5 line, if shown,
must be visually secondary and labelled intuitive only.
