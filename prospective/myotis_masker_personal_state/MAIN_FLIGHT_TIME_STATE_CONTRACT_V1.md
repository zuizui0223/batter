# Myotis landing-time cross-noise personal-state contract v1

## Status

**FROZEN BEFORE NEW NUMERICAL OUTCOME OPENING.**

## Biological question

Does individual landing-performance organization persist across strong changes in masking-noise level?

This is the direct behavioral/movement endpoint in the public Myotis source.

## Source endpoint

Use only time_flight_s from dataset_tc.csv.

One row is one source-defined trial.

## Frozen transformation

Because flight time is positive and right-tailed by construction:

y = log(time_flight_s).

No alternative transformation after opening.

## Equal-day bat-condition summary

For each bat i, noise condition c and source day d:

m_i,c,d = median(y).

Then:

m_i,c = equal-day mean of m_i,c,d.

## Noise-condition centering

r_i,c = m_i,c - mean across retained bats of m_i,c.

This removes the shared slowing caused by masking and retains relative individual organization.

## Cross-noise self-history advantage

For a target condition c:

h_i,-c = mean of r_i,c' over all other retained noise conditions.

For donor j define h_j,-c analogously.

A_i,c =
mean over j != i of abs(r_i,c - h_j,-c)
minus abs(r_i,c - h_i,-c).

Aggregate equally across conditions within bat, then equally across bats.

Statistic: A_flighttime.

## Exact null

Let B be the frozen common-support bat count and C=5 source noise conditions.

Fix the no-noise label mapping.

Independently permute complete bat labels within each of the other four conditions.

If B=3:
(3!)^4 = 1296 assignments.

If B=4:
(4!)^4 = 331,776 assignments.

Enumerate the full legal null.

One-sided exact p =
fraction of null statistics greater than or equal to observed.

## Primary support within this source

Support requires:
- A_flighttime > 0;
- exact p <= 0.05.

Because the source paper indicates common support may be only three bats, any positive result is labelled:

CONTROLLED_SMALL_N_MOVEMENT_SUPPORT

rather than broad replication.

## Claim ceiling

Positive result supports:

relative individual landing-performance organization persists across masking-noise levels after the shared noise response is removed.

It does not establish broad prevalence across Myotis, a two-axis I/M carrier, route memory, formation mechanism, or wild vertical individuality.
