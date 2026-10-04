# Post-primary absolute-position diagnostic contract v1

## Status

**POST-PRIMARY DIAGNOSTIC. NOT CONFIRMATORY.**

This contract was frozen after:
- Primary A PASS;
- start-centered A1 FAIL;
- chord-residual A2 FAIL.

It cannot rescue Primary A.

## Question

Did the original within-configuration route identity primarily reflect stable absolute entry/exit geometry rather than repeatable route shape?

## Source and support

Use exactly the authoritative *Rhinolophus nippon* route-valid trajectories from Primary A and environments Env1–Env3.

Use the same target-bat eligibility, donor weighting, environment weighting and within-environment trajectory-label permutation as Primary A.

## Diagnostic S1 — start position identity

For each route, retain only:

`s_q = r_q(0)`

the first point of the frozen 101-point route.

Distance:
3-D Euclidean distance between start points.

Compute the same self-vs-other identity advantage and equal-weight species statistic.

9,999 permutations.
Seed:
`202610042221`.

## Diagnostic S2 — end position identity

Use only:

`e_q = r_q(1)`.

Same estimator and null.

9,999 permutations.
Seed:
`202610042222`.

## Diagnostic S3 — displacement-vector identity

Use:

`d_q = r_q(1)-r_q(0)`.

This removes absolute coordinate offset while retaining overall flight displacement vector.

Same estimator and null.

9,999 permutations.
Seed:
`202610042223`.

## Diagnostic S4 — start+end joint identity

Use the six-dimensional vector:

`g_q = [r_q(0), r_q(1)]`.

Within each environment, z-score each of the six coordinates across trajectories before Euclidean distance so no axis dominates by scale.

Same self/donor weighting and identity-label permutation.

9,999 permutations.
Seed:
`202610042224`.

## Interpretation

- S1 strong + S3 weak: original A is mainly absolute entry-position identity.
- S1 and S2 strong but S3 weak: a stable absolute spatial offset/entry-exit corridor explains A better than route shape.
- S3 strong: individuals also differ in gross displacement direction/extent.
- all weak: Primary A may depend on distributed absolute trajectory position rather than endpoints alone.

These diagnostics do not establish whether absolute-position identity is behavioural or an experimental/session/calibration effect.

## No rescue

Do not:
- change environments;
- select individuals;
- alter route trimming;
- add alignment;
- reinterpret any S diagnostic as evidence for learned route memory.

