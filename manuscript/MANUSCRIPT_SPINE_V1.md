# Individual-specific vertical-state use in European free-tailed bats

## Scientific question

Why did the species-average x-y-conditioned vertical map fail to transfer among *Tadarida teniotis* individuals despite substantial vertical thickness?

## Starting observation

The preceding ODSP analysis established:

1. species-level vertical support was descriptively thick: 4.022 effective vertical states;
2. the pooled species-level `P(z|x,y)` failed to improve prediction for either sealed bat relative to the pooled marginal `P(z)`.

That species-level transfer endpoint remains negative.

## v1 identity-transfer result

All eight tracked bats were divided chronologically into early and late halves inside the exact 18 five-kilometre cells and fixed MSL-altitude bins inherited from ODSP.

Early individual maps were scored on every individual's later observations.

The identity-matched diagonal mean gain over the species-level cell-specific map was:

- **+0.1682 nats/event**;
- exact 8! permutation **P = 0.000174**;
- 6/8 individual diagonal gains positive;
- own map strict top-1 for 5/8 individuals.

Thus individual identity carried strong temporally persistent information about later vertical state.

## v2 refinement: does identity operate through location-specific vertical strategy?

A stricter preregistered refinement first absorbed each individual's marginal altitude distribution. The baseline for individual i became

`P_i_add(z|cell) ∝ P_species(z|cell) × P_i(z)/P_species(z)`.

The only remaining benefit available to the full individual model was the individual-by-cell interaction.

Primary v2 result:

- residual diagonal gain **+0.0240 nats/event**;
- exact 8! permutation **P = 0.1605**;
- 5/8 individual residual gains positive;
- own map strict top-1 for only 1/8.

Frozen sensitivities were also non-supportive:

- λ=5: gain -0.0330, P=0.2485;
- λ=50: gain +0.0422, P=0.0651.

Therefore **location-specific individual vertical strategy is not supported after marginal altitude preference is controlled**.

## Updated ecological interpretation

The evidence now supports a narrower but cleaner biological statement:

> Vertical-state use is temporally repeatable and individual-specific, but the present data do not show that this individuality is primarily a stable individual-by-location vertical map.

This means the species-average map can fail cross-individual transfer because individuals differ in their vertical-state distributions, even though the detailed spatial interaction is not independently identified.

The next decomposition asks whether the individual-specific signal is concentrated in the **marginal altitude distribution itself**. That analysis is explicitly explanatory/post-v2, not a new independent confirmation.

## Claim ceiling

Allowed:
- temporally repeatable individual-specific vertical-state use;
- poor exchangeability of individual vertical-state distributions;
- failure of the stricter individual-by-location refinement.

Not allowed:
- stable individual-specific location-conditioned vertical strategy as a confirmed mechanism;
- height above ground;
- causal habitat preference;
- personality, cognition or learned route use;
- fitness consequences;
- species-wide universality;
- reinterpretation of the original ODSP species-level transfer endpoint as positive.
