# Individual recall identifiability stop v1

## Status

**STOP — a confirmatory individual-identity recall test cannot attain the predeclared 0.05 level while preserving the source stage-4 environment assignment.**

This stop is issued **before any IPI or other acoustic outcome value is opened in this programme**.

Parent programme:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- `SCHEMA_OPENING_CONTRACT_V1.md`

Outcome status:
- schema only has been opened;
- structural A–D / A–H support counting may complete for provenance;
- acoustic outcome columns, including IPI, remain closed.

## Source design constraint

The source experiment contains five biological individuals in the long-term second clutter encounter.

The published/source design assigns stage-4 environment as:

- **3 individuals**: return to the same clutter chamber;
- **2 individuals**: enhanced clutter chamber / new-box condition.

The new programme's intended endpoint was an individual-identity recall test:

> is a bat's stage-4 learned-state observation closer to its own late stage-2 learned state than to the corresponding learned states of other bats?

A valid identity-exchangeability null must not assign a target observation to a donor history from an environment class that the biological target did not receive if environment itself can alter the endpoint.

Therefore stage-4 environment assignment must be preserved under label exchange.

## Exact randomization ceiling

With 3 targets in one environment class and 2 in the other, the complete condition-preserving identity-permutation space contains:

[
3!\times2! = 12
]

possible label mappings.

Even if the observed identity mapping is uniquely the most favorable mapping, the smallest attainable exact one-sided probability is:

[
p_{min}=\frac{1}{12}=0.08333.
]

Therefore a conventional exact `p <= 0.05` confirmatory individual-identity endpoint is **mathematically unattainable** under the source design.

This is an identifiability/design limitation, not a negative biological result.

## Why not pool all 5 targets?

Pooling stage-4 targets across the same and enhanced chambers would create `5! = 120` permutations, but those permutations exchange individual identity together with experimental environment.

That null would confound:
- identity recall;
- same-versus-enhanced chamber response.

It is not an admissible confirmatory test of personal recall.

## Why not standardize the two stage-4 environments first?

The enhanced group contains only two individuals.

Any outcome-based centering/scaling or fitted environment adjustment would be estimated from the same tiny target set and would not restore a clean untouched individual-exchangeability null.

No such rescue was frozen before outcome opening.

## Why not use a five-bat sign test?

A separate within-bat sign endpoint could in principle attain a one-sided minimum of `1/32 = 0.03125`.

However:
- it would answer retention of a common learned direction, not individual-identity recall;
- the source paper already reports the group-level long-term recall pattern;
- designing a new directional sign endpoint after knowing that published result would not provide an untouched independent confirmation.

It is therefore not substituted for the stopped identity primary.

## Scientific consequence

Do not open IPI merely to obtain a weak or post-hoc new p-value.

The Taub & Yovel experiment should instead enter the mechanism synthesis as **external causal triangulation**:

- clutter experience changes sensorimotor behavior;
- the learned strategy can be expressed after a six-month interval;
- some individuals also express it in an enhanced clutter scene.

Those published perturbation results are highly relevant to the learned scene/task layer, but the public design does not support a new 5%-level individual-identity recall primary under condition-preserving randomization.

## What remains useful from the structural workflow

The already-frozen structural support workflow may finish and report:
- stage-2 / stage-4 dates;
- landing/file replication;
- source new-box assignment.

Its output is provenance only.

It must not trigger acoustic outcome opening for the stopped individual-identity primary.

## Programme decision

`STOP_INDIVIDUAL_RECALL_IDENTIFIABILITY`

Do not:
- pool same/enhanced stage-4 targets;
- lower alpha above 0.05;
- use asymptotic p-values to evade the 12-permutation ceiling;
- switch to a known-positive published group contrast and relabel it as a new primary;
- open multiple acoustic endpoints and select one.

Future progress requires either:
- more independently treated individuals per stage-4 environment class; or
- a source/design in which the same individuals are crossed through reset conditions, allowing within-individual causal contrasts without confounding identity and environment.
