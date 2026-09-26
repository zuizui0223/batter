# Focal analysis reconciliation — predictive architecture versus residual map stability

Date: 2026-09-27

## Why this reconciliation is necessary

Two frozen analysis families in `batter` ask related but non-identical questions about the
*Tadarida teniotis* focal dataset.

The later cross-night comparative programme uses

`G_cond = log P_self(z|x,y) - log P_other(z|x,y)`

and

`G_marg = log P_self(z) - log P_other(z)`

with the descriptive contrast

`G_cond - G_marg`.

The earlier identity-refinement programme instead asks whether an **individual-specific
cell-by-height residual map** remains stable after each individual's marginal altitude preference
has already been absorbed into a fixed additive baseline.

These are not the same estimand.

## Frozen results that must all be retained

### Early/late identity assignment V1

Supported:

- diagonal conditional identity gain = +0.1682;
- exact 8! identity-assignment p = 0.000174;
- 6/8 own-map gains positive.

Thus individual identity carries temporally repeatable information about later conditional
vertical state.

### Residual cell-by-height stability V2

Not supported:

- residual diagonal gain = +0.0240;
- exact permutation p = 0.160;
- 5/8 residual gains positive;
- frozen lambda sensitivities also fail.

Therefore the focal dataset does **not** establish a stable individual-specific cell × height map
after marginal altitude identity is explicitly absorbed.

### Session-level conditional-versus-marginal prediction

At 5 km, the separate leave-one-session-out analysis gives:

- conditional MSL identity = +0.428;
- marginal MSL identity = +0.052;
- conditional-minus-marginal = +0.376.

AGL gives the same qualitative conditional dominance:

- conditional AGL identity = +0.337;
- marginal AGL identity = -0.255;
- conditional-minus-marginal = +0.591.

These results show that horizontal location **increases predictive individual information** under
that scoring architecture. They do not override V2 and cannot be relabelled as proof that a
specific individual cell × height map is temporally stable.

## Correct terminology

Use:

- **conditional-dominant vertical identity** when `G_cond > G_marg`;
- **marginal-dominant vertical identity** when `G_marg > G_cond`;
- **conditional advantage** for `G_cond - G_marg`;
- **repeatable vertical identity / non-exchangeability** for the general biological phenomenon.

Do not use as a demonstrated mechanism:

- stable place-specific route;
- stable individual-by-location vertical strategy;
- fixed place × height rule.

“Place-coupled” may be used only as shorthand for the predictive conditional contrast if it is
immediately defined and explicitly separated from residual-map stability. The preferred paper
language is **conditional-dominant**.

## Cross-taxon consequence

The comparative result survives this correction.

At 5 km:

- *Tadarida*: conditional +0.428 > marginal +0.052;
- *Eidolon*: conditional +0.219 > marginal +0.002;
- *Hypsignathus*: conditional +0.029 > marginal -0.021;
- *Phyllostomus* 2022: marginal +0.176 > conditional +0.056.

Therefore the supported comparative statement is:

> Cross-night vertical identity can be **conditional-dominant** or **marginal-dominant** across
> bat systems, and that balance can vary across temporal contexts within a species.

This is a predictive ecological architecture, not proof of the latent behavioural mechanism that
generates it.

## Status

This is a claim-boundary correction only. No data, score, bin, scale, source, admission rule or
negative result is changed.
