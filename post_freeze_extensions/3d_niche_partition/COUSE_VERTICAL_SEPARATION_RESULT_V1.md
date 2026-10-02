# Synchronous co-use vertical-separation result v1

## Status

POST-OUTCOME MECHANISM TEST.

The x-y-time encounter definition, panel-specific synchronization tolerance, endpoint/all-space primary scope, fixed encounter set, terrain-relative endpoint, equal-dyad statistic, phase-shift null, B and seeds were fixed before the corrected analysis reported here.

Authoritative corrected workflow:
- run: `36953712597`
- head: `7d5f310b0ec5337b47202ced4378a78edc3daa66`
- conclusion: success

A historical first-output workflow existed before the final implementation correction. Its comparison with the corrected workflow is documented separately in `COUSE_RUN_CORRECTION_AUDIT_V1.md`.

## Primary question

During actual local co-use, are different individuals farther apart vertically than expected after preserving each individual's site-specific terrain-relative vertical distribution but breaking momentary cross-individual vertical alignment?

Primary statistic:
- terrain-relative, session-centered absolute height difference at fixed observed encounters;
- median within each frozen dyad;
- equal mean across frozen dyads.

## Results

| panel | scope | time window | individuals | dyads | encounters | observed separation | null mean | excess | p(null >= obs) | result |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| *Hypsignathus monstrosus* | endpoint-excluded | 60 s | 11 | 22 | 883 | 21.99 m | 23.97 m | -1.98 m | 0.9045 | not supported |
| *Phyllostomus hastatus* 2022 | endpoint-excluded | 60 s | 6 | 10 | 347 | 6.78 m | 7.73 m | -0.95 m | 0.9186 | not supported |
| *P. hastatus* 2023 | all-space | 600 s | 6 | 8 | 679 | **26.57 m** | **22.99 m** | **+3.57 m** | **0.0231** | **supported** |
| *P. hastatus* 2016 | endpoint-excluded | 600 s | 5 | 8 | 16,096 | 11.36 m | 12.22 m | -0.85 m | 0.8611 | not supported |

Null central 95% intervals:
- *Hypsignathus*: 21.09–27.22 m
- 2022: 6.44–9.20 m
- 2023: 19.81–26.49 m
- 2016: 10.69–13.78 m

## Main inference

Three of four panels show no evidence that synchronous local co-use adds vertical separation beyond each individual's stable site-specific terrain-relative vertical strategy.

This is important because all four of these panels previously showed supported terrain-relative vertical strategy fidelity.

Therefore:

> **repeatable individual vertical strategies are generally not equivalent to active vertical partitioning during co-presence.**

The dominant pattern is stable personal strategy reuse rather than systematic co-presence-dependent separation.

## The 2023 exception

The 2023 *P. hastatus* panel is the only panel in which observed synchronous separation exceeds the fixed phase-shift null.

Observed equal-dyad median separation is 26.57 m, about 3.57 m above the null mean.

The signal is not produced by one high-count dyad because the panel statistic weights dyads equally. Dyad-specific observed median separations span approximately 9.7–42.2 m; the dyad contributing 586 of 679 encounters has a median separation of 31.6 m.

However the interpretation ceiling is low:
- the structural preflight required the maximum 600-s synchronization window;
- the endpoint-excluded universe failed its biological-individual gate, so the frozen primary is all-space;
- approximately 79% of encounters occur in the largest 500-m cell;
- co-presence-dependent separation is not unique evidence for competition.

Thus 2023 supports a **context-dependent interaction/co-presence layer** superimposed on personal strategies, not a general competition-driven vertical-partitioning law.

## Negative-direction results

In *Hypsignathus*, 2022 and 2016, observed synchronous separation is actually below the null mean.

These are not lower-tail tests and should not be relabelled as attraction or convergence. They simply provide no evidence for the predeclared directional hypothesis of additional vertical separation.

## Relation to terrain-relative 3D geometry

Completed terrain-relative geometry showed supported personal vertical strategy fidelity in all four panels:

- *Hypsignathus*: V_rel +0.042
- 2022: +0.100
- 2023: +0.077
- 2016: +0.079

Yet only 2023 shows additional synchronous separation.

This empirically separates two dimensions:

1. **strategy fidelity** — an individual repeatedly reuses its own vertical configuration;
2. **interaction-dependent separation** — individuals alter momentary relative height during local co-use.

The first is recurrent here; the second is not.

## Artifact receipts

Corrected workflow `36953712597`:
- *Hypsignathus*: artifact `11205510244`, digest `sha256:3cae11ab2ee37b966d7d3798f8dc8a370e10ae1e7f449aa896869a0570e3e753`
- 2022: artifact `11204898247`, digest `sha256:9d096a7189d122ae0191a3060d82c5a83c9ef51bc122b6b0d2bda56c3aeb6bc6`
- 2023: artifact `11205525158`, digest `sha256:4e0ecee59e8c4269b1b93fd062cddb0fe87a8b4d0b0c4b18edf186d75a4df80a`
- 2016: artifact `11205780190`, digest `sha256:124bc1c7ee5042f745bd7925b115c4e9a344a16736d91442c4dc0ca9b57796ce`

## Claim ceiling

Supported:
- personal terrain-relative vertical strategies can persist without extra vertical separation during co-presence;
- one 2023 panel shows a co-presence-dependent separation signal under its frozen coarse synchronization design;
- strategy fidelity and interaction-dependent partitioning are distinct axes of individual specialization.

Not established:
- competition as the cause of the 2023 signal;
- intentional avoidance;
- food or resource partitioning;
- instantaneous interaction in the 600-s panels;
- a general bat-wide interaction rule.
