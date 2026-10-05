# Naive-learning biological contrast contract v1

## Status

**BIOLOGICAL HYPOTHESES FROZEN BEFORE RAW ROW VALUES ARE OPENED.**

Exact source columns and estimator formulas will be frozen after schema-only inspection.

## Central decomposition

For bat i, flight n and experimental condition c, represent an observed policy quantity or low-dimensional vector as:

`P_icn = condition/common-learning component + stable individual component + individual learning deviation + residual`.

The programme asks which component carries individual identity.

## H1 — naive-to-late personal-prior retention

Primary biological contrast:

> Does an individual's policy measured before meaningful familiarity predict that same individual's late learned policy after removing the condition-level learning shift?

Preferred windows if source support allows:
- naive/early: flight 1;
- late: flights 10–12 averaged equally.

If only flights 1 and 12 are publicly available:
- use flight 1 vs flight 12 exactly.

The source condition is handled separately or removed by condition-specific centering; bats are not compared across conditions as if they faced identical sensing tasks.

Support must be calibrated against permutation of individual correspondence within condition.

## H2 — common learning versus individual divergence

For every bat:

`Delta_i = late_i - early_i`.

Decompose the change into:

- condition mean learning vector;
- residual individual change.

Report the fraction of squared change magnitude attributable to the condition-common shift versus residual individual divergence.

No significance claim is predeclared for the variance fraction until the exact source dimensionality is known.

## H3 — rank / identity persistence across learning

If the endpoint is one-dimensional:

- test whether early individual ranks predict late individual ranks within condition.

If multivariate:

- use held-out own-versus-other early-centroid prediction of late policy.

This must use individual as the biological replication unit.

## H4 — emergence / tightening with experience

If all 12 flights are recoverable:

- predeclare an experience-series test after schema inspection;
- compare early and late within-individual self-predictability without selecting a breakpoint from the observed outcome.

The breakpoint/window must be fixed from source design (for example source-defined first versus twelfth, or first 3 versus last 3), not optimized after viewing data.

## Interpretation matrix

### Strong H1, mostly common Delta
Stable prior + shared learning:
individuals retain their relative policy while all shift with familiarity.

### Weak H1, strong late individuality
Experience-dependent individual lock-in:
personal policy is formed or reorganized during learning.

### Strong H1 plus large individual Delta differences
Stable prior with individual-specific learning reaction norms.

### Weak individuality throughout
The source experiment contains common learning but little stable individual policy in the measured variables.

## Causal ceiling

Because bats were not randomized to individual learning histories, this programme can identify learning-associated within-individual reorganization but cannot uniquely attribute between-individual differences to learning rather than stable morphology/physiology.
