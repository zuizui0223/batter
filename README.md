# batter

Ecological follow-up on individual signatures in the three-dimensional movement niche of the European free-tailed bat (*Tadarida teniotis*).

## Current result

The preceding ODSP analysis found a vertically thick population-level support (4.022 effective vertical states) but no transfer of the pooled location-conditioned vertical map to two sealed bats.

This repository decomposes that non-transferability across all eight tracked individuals.

### Strong result

Chronologically early individual maps were scored against all individuals' later observations.

The correctly identity-matched diagonal was much better than random assignment of individual maps:

- diagonal mean conditional gain: **+0.1682 nats/event**;
- exact 8! permutation **P = 0.000174**;
- 6/8 bats had positive own-map gain over the population cell-specific model.

Thus individual identity carries repeatable information about later conditional vertical-state use.

### Important boundary

The stronger claim of a stable individual-by-location vertical reaction map was **not** supported after individual marginal altitude preference was controlled:

- residual diagonal gain: +0.0240;
- exact permutation P = 0.160;
- 5/8 positive.

Altitude-only and horizontal-only identity assignments were each better matched than random permutations, but each improved on the pooled population baseline for only 4/8 individuals under the frozen support rule.

## Current ecological interpretation

> **The population vertical niche is thick and individual identities leave repeatable movement-state signatures, but those signatures are not reducible to one simple altitude offset, horizontal site fidelity, or stable individual-by-location vertical map.**

The strongest current paper framing is partial individual specialization / non-exchangeability within a population niche, not eight fully separate vertical strategies.

See:
- `results/individual_vertical_strategy_result_v1.json`
- `results/spatial_interaction_refinement_result_v2.json`
- `results/identity_component_decomposition_result_v3.json`
- `manuscript/MANUSCRIPT_SPINE_V2.md`
