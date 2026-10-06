# Geometry-only policy diagnostic result v1

## Status

**SUPPORTED — POST-PRIMARY EXPLORATORY ROBUSTNESS.**

Authoritative workflow:
- run: **37392776769**
- job: **112041531100**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md`

## Question

Does individual movement identity transfer across obstacle configurations after removing:

- elapsed-time scale;
- speed magnitude;
- turn rate per unit time;
- absolute path length;
- absolute vertical range;
- absolute spatial offset?

Each trajectory was:
- start-centered;
- divided by its own total 3-D path length;
- represented only by dimensionless/angular route-geometry features.

## Retained geometry features

All 8 frozen features passed support across Env1–Env7:

1. 3-D path efficiency;
2. horizontal displacement ratio;
3. absolute vertical displacement ratio;
4. vertical range ratio;
5. median absolute horizontal turn angle;
6. p90 absolute horizontal turn angle;
7. median absolute vertical slope;
8. p90 absolute vertical slope.

Dropped features:
**0**

Trajectories:
**45**

## Cross-configuration identity

Observed:

[
K_{geometry}=+0.38857.
]

Individual means:
- A: **+0.3456**
- B: **+0.1996**
- C: **+0.8902**
- D: **+0.2129**
- E: **+0.2946**

Positive:
**5/5**

Permutation calibration:
- 9,999 / 9,999 valid;
- null mean = **-0.0188**;
- null 95% interval = **[-0.2569,+0.3428]**;
- one-sided `p = 0.0153`.

Verdict:

**SUPPORTED_GEOMETRY_IDENTITY**

## Interpretation

A transferable personal movement signature remains even after stripping away explicit time, speed and absolute spatial scale.

Thus the adult portable policy is not adequately explained as only:

> some bats are consistently faster, slower, larger-scale or more vertically extensive.

Individuality also resides in **scale-free route organization**:
- relative displacement;
- route efficiency;
- turning geometry;
- vertical trajectory shape.

This strengthens the interpretation of the portable state as a movement-control bias rather than a single performance-magnitude trait.

## Relation to the functional-abundance hypothesis

This result is **compatible** with personal selection among multiple coordinative solutions because different individuals retain different geometry-level organizations across tasks.

It is **not direct evidence** that:
- multiple feasible solutions exist in each tested arena;
- history selects one solution from a measured feasible-set manifold;
- solution abundance causes individual specialization.

Those require independent obstacle/constraint geometry or an experimental manipulation of the feasible solution set.

Do not infer abundance from realized trajectory dispersion.

## Claim ceiling

Supported:
- portable individuality survives removal of performance magnitude and absolute scale.

Not established:
- neural control state;
- learning as the unique source;
- motor degeneracy as the direct causal mechanism;
- solution-abundance effect.

## JAE firewall

No change to JAE v0.4.0.
