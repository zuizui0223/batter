# batter

Ecological analysis of repeatable individual identity in three-dimensional bat airspace.

## Biological question

When a bat carries vertical information across nights, **where is that individual information
predictively expressed**?

Two non-equivalent predictive architectures are compared:

1. **marginal identity** — the same animal repeats an informative overall vertical distribution;
2. **conditional identity** — individual identity becomes more informative when vertical state is
   predicted conditional on horizontal place.

We summarize

```text
conditional advantage
= conditional identity gain - marginal identity gain
```

A positive conditional advantage is called **conditional-dominant**. A negative value with
stronger marginal identity is **marginal-dominant**.

This is predictive terminology. It is not automatically evidence for a stable latent
individual-specific cell × height route.

## Origin

The project began from an ODSP result in *Tadarida teniotis*: the fitted population was
vertically thick (~4.02 effective MSL states after x-y was known), but the pooled
`P(z|x,y)` did not transfer to two held-out individuals.

`batter` asks whether this non-transfer reflects within-population individual
non-exchangeability.

## Focal *Tadarida teniotis*

Several frozen analyses must be read together.

### Repeatable conditional identity

An early/late identity-assignment test passed:

- diagonal conditional gain +0.1682;
- exact permutation p=0.000174;
- 6/8 own-map gains positive.

Thus individual identity predicts later conditional vertical state.

### Stronger residual-map claim does not pass

After each bat's marginal altitude preference was absorbed into the baseline, the frozen
individual-specific cell × height residual test did **not** pass:

- residual gain +0.0240;
- exact permutation p=0.160;
- 5/8 positive.

Therefore this dataset does not demonstrate a stable individual-specific place × height map.

### Session-level predictive architecture

At 5 km:

- MSL conditional identity +0.428;
- MSL marginal identity +0.052;
- conditional advantage +0.376;
- AGL conditional identity +0.337;
- AGL marginal identity -0.255;
- conditional advantage +0.591;
- terrain-elevation conditional identity +0.007.

The defensible interpretation is **conditional-dominant vertical identity**: horizontal location
adds substantial predictive identity information.

Controls show that this contrast is not simply terrain elevation, a shared calendar-night state
or averaging heterogeneous alternative bats. A frozen common uplift-reaction mechanism was not
supported.

## Independent comparative panels

At 5 km:

| Taxon/context | Conditional | Marginal | Conditional advantage |
|---|---:|---:|---:|
| *Tadarida teniotis* | +0.428 | +0.052 | +0.376 |
| *Eidolon helvum* | +0.219 | +0.002 | +0.217 |
| *Hypsignathus monstrosus* | +0.029 | -0.021 | +0.050 |
| *Phyllostomus hastatus* 2022 | +0.056 | +0.176 | -0.120 |

*Eidolon* and *Hypsignathus* prospectively reproduce conditional-dominant identity.
*Phyllostomus* 2022 instead produces a marginal-dominant architecture.

Within *P. hastatus*, the architecture is not fixed:

- 2023: conditional +0.033, marginal +0.013, advantage +0.020;
- untouched 2016 dry-season prospective test: +0.058, +0.016, +0.041 and failure of the
  preregistered 2022-like marginal-dominant prediction.

## Central ecological statement

> **Individual vertical identity in bat airspace has multiple predictive architectures. Across
> nights, identity can be more informative in a location-conditioned vertical distribution than
> in an animal-wide height distribution, or vice versa, and that balance can vary across
> ecological contexts.**

## Public-data search

The source universe is closed. An outcome-blind search covered 23 Movebank bat parent datasets
plus legacy child-handle recovery. Six sources from four taxa passed the fixed requirements for
same-event x-y-height data and repeated tracking. Numeric height values were not used for source
admission.

## Key files

- `FOCAL_ANALYSIS_RECONCILIATION.md` — reconciles the conditional architecture with the frozen
  residual-map negative result
- `PAPER_FREEZE_V0_3_1_CLAIM_AMENDMENT.md` — claim-only amendment; empirical freeze unchanged
- `MANUSCRIPT_SPINE.md` — current paper logic
- `SPECIALIZATION_ARCHITECTURE_SYNTHESIS.md` — comparative architecture synthesis
- `BAT_PANEL_SEARCH_CLOSEOUT.md` — outcome-blind public-data closeout

## Claim boundary

The analyses concern vertical flight/airspace use and predictive individual identity. They do
not by themselves establish foraging, personality, learning, optimality, stable learned routes
or a causal environmental mechanism.
