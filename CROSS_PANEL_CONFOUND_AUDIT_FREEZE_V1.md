# Cross-panel confound audit v1 — contract freeze record

Frozen before new outputs: 2026-09-27

- `contract/cross_panel_endpoint_exclusion_v1.json`
  - blob SHA: `84998d2e6daf4f60054be2fc6ba96118396164c8`
- `contract/effect_translation_null_calibration_v1.json`
  - blob SHA: `169caf84fb96db70a937b6ecf14486c6e5eb6e1a`

At this point no new non-*Tadarida* endpoint-exclusion result, pairwise-win permutation null, or
AGL absolute-separation permutation null had been generated or opened.

Subsequent runner code must treat these contracts as read-only. Any change to either contract after
an output exists creates a new analysis family/version and may not overwrite v1.
