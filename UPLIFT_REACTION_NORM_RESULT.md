# Uplift reaction norm v1 — terminal mechanism result

Date: 2026-09-26  
Workflow: `uplift-reaction-norm-v1`  
Source: checksum-pinned `TadaridaHighFast_annotated.csv`

## Frozen question

Does a bat's own other-night slope in `climb.rate ~ W.Component` predict a target night's
uplift-response slope better than slopes from other bats?

## Result

The primary mechanism endpoint was estimable for only two repeat-tracked individuals under the
predeclared requirement of at least 50 finite rows and within-session SD(W.Component) >= 0.05 m/s.

- Bat7: self slope-error improvement = +0.7903
- Bat8: self slope-error improvement = -0.5517
- equal-individual mean = +0.1193
- positive individuals = 1/2
- event-level MSE improvement mean = -0.0000423
- slope-identity permutation p = 0.3337

This does **not** support a population-wide claim of repeatable individual uplift reaction norms.

## Why coverage was low

There were 16 sessions and 5 passed the frozen W-variation gate. Most excluded sessions were only
slightly below the fixed threshold (SD(W) approximately 0.035–0.049 m/s). The threshold is not
changed after seeing this result.

## Scientific interpretation

The already-established fine-scale place-by-height self-transfer is not explained, on this
endpoint, by one universal pattern of individually repeatable response to modeled vertical wind.
Bat7 and Bat8 themselves also differ strongly.

The next analysis is therefore not a rescue of this endpoint. It asks a distinct semantic
question enabled by the archived annotated data: whether individual self-transfer persists when
vertical state is defined as **height above ground level (AGL)** rather than height above mean
sea level.
