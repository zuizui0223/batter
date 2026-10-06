# Geometry identity beyond transparent I/M result v1

## Status

**UNSUPPORTED — THE TRANSPARENT I/M SPAN ABSORBS THE PORTABLE GEOMETRY IDENTITY SIGNAL.**

Authoritative workflow:
- run: **37403403893**
- job: **112075462251**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS_CONTRACT_V1.md`

This is a post-primary falsification diagnostic.

## Question

The original transparent two-axis result showed that FlightIntensity (I) and ManeuveringExtent (M) approximately exhaust calibrated identity **within the original eight movement-summary features**.

A later scale-free geometry representation also carried portable identity.

The question was:

> does scale-free geometry contain additional identity beyond both I and M?

## Parent geometry signal

- geometry-only K = **+0.38857**
- 5/5 positive
- p = **0.0153**

## FlightIntensity removal alone

Recomputed geometry identity after label-free linear removal of I:

- K = **+0.30775**
- K / parent = **0.792**
- 5/5 positive
- p = **0.0029**

Thus FlightIntensity alone does not explain the geometry carrier.

## I + M removal

Within each environment, each geometry feature was regressed on the transparent I and M coordinates without using bat identity.

Residual geometry identity:

- K = **-0.01467**
- K / parent = **-0.038**
- positive bats = **1/5**
- 9,999 / 9,999 valid permutations
- null mean = **-0.01540**
- null 95% interval = **[-0.1011,+0.1041]**
- one-sided p = **0.4509**

Verdict:

**UNSUPPORTED_GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS**

## Individual residual means

- A: **+0.1197**
- B: **-0.0731**
- C: **-0.0228**
- D: **-0.0078**
- E: **-0.0894**

No individual is removed.

## Geometry association with I/M

Median within-environment linear R² from geometry ~ I + M:

- path efficiency: **0.905**
- horizontal displacement ratio: **0.514**
- absolute vertical displacement ratio: **0.648**
- vertical range ratio: **0.845**
- median horizontal turn angle: **0.296**
- p90 horizontal turn angle: **0.785**
- median vertical slope: **0.824**
- p90 vertical slope: **0.685**

Thus the transparent pair spans a large fraction of variation in most route-geometry features, even though FlightIntensity alone does not.

## Interpretation

The geometry-only and family-ablation results remain valid:
- G-only identity is supported;
- H-only identity is supported;
- the geometry signal survives family deletions and target-normalization restrictions.

But those results do **not** imply an additional independent geometry dimension beyond the transparent policy pair.

The stronger current interpretation is:

> **Within the Rhino obstacle-flight system, FlightIntensity + ManeuveringExtent organize both coarse movement magnitude and the identity-bearing scale-free route geometry.**

Therefore the two-axis model survives a harder feature-space challenge than originally claimed.

## Important scope boundary

This residualization is fit within each environment and is label-free.

It shows statistical alignment of geometry identity with I/M inside environments.

It does not by itself prove that one universal linear map from I/M predicts exact route geometry in an unseen environment.

The held-out I/M coordinate prediction and fully training-only geometry-transfer tests provide separate portability evidence.

## Cross-species boundary

The fixed Rhino geometry representation is unsupported in independent *Carollia perspicillata*, whereas the earlier fixed low-dimensional I/M programme is supported, especially FlightIntensity.

Therefore do not claim:
> one universal bat geometry policy.

A better hierarchy is:

[
oxed{
	ext{recurrent coarse personal policy}
ightarrow
	ext{system-specific route-geometry realization}
}
]

## Claim ceiling

Supported:
- no calibrated geometry identity remains after linear I/M removal in Rhino;
- FlightIntensity alone is insufficient;
- ManeuveringExtent is necessary for the transparent pair to absorb geometry identity.

Not established:
- anatomical two-dimensionality;
- nonlinear sufficiency;
- universal two-axis law across species;
- motor degeneracy as causal origin.

## JAE firewall

No change to JAE v0.4.0.
