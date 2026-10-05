# Reversible sensory perturbation source receipt v1

## Status

**PROSPECTIVE EXTERNAL WITHIN-INDIVIDUAL PERTURBATION PROGRAMME. NO NEW SOURCE OUTCOME OPENED.**

Branch:
`prospective/reversible-sensory-perturbation-v2`

This programme is separate from JAE v0.4.0 and from the completed post-JAE field diagnostics.

## Source

Taub, M. & Yovel, Y. (2020).

*Segregating signal from noise through movement in echolocating bats.*

Scientific Reports 10:382.

DOI:
`10.1038/s41598-019-57346-2`

Species:
*Pipistrellus kuhlii*.

Public data source declared by the paper:
`https://www.dropbox.com/sh/met5cvcq9nmvxdd/AAAF4saT9FZl01FwWyRgD1pqa?dl=0`

## Source experimental architecture

Six female bats were trained individually to land on a fixed target in the same flight room.

The source design exposed the same biological individuals to repeated target-approach conditions including:

1. **no masker** baseline;
2. an acoustically masking background **30 cm** behind the target;
3. the masker **10 cm** behind the target.

The masker orientation was defined relative to each bat's own trained preferred approach direction.

The source recorded:
- 3-D flight trajectories at 200 Hz;
- head direction;
- echolocation.

The published result shows a strong condition effect on movement geometry: bats changed their angle of attack under acoustic masking.

## Mechanistic question

The current batter synthesis supports a persistent low-dimensional individual movement-policy bias but shows that:
- persistent policy does not require spatial partitioning;
- individual peer-context reaction slopes are unsupported in the wild archive;
- stable personal breadth is not established;
- learned scene-specific solutions can change.

This source permits a cleaner within-individual perturbation question:

> **When the same bat faces a reversible sensory challenge, does its personal movement-policy bias remain identifiable after the condition-level shift is removed?**

This separates:

- common perturbation response;
- persistent individual policy;
- individual-specific perturbation response.

## Prospective hierarchy

### P1 — condition-residual personal-policy persistence

After defining the movement representation outcome-blind and removing the mean/scale of each source condition, do held-out flights remain closer to the same bat's history than to histories of other bats?

### P2 — recovery / reversibility, only if source order contains a return condition

If the public source contains a genuine post-perturbation return-to-baseline block for the same bats, test whether the pre-perturbation individual policy predicts the recovered block after condition mean removal.

If no source-defined return block exists, STOP P2. Do not invent one from trial order.

### P3 — individual perturbation response

Only after P1 is evaluated, test whether individual-specific condition responses improve held-out prediction beyond a shared condition effect.

This cannot rescue P1.

## Outcome firewall

Before any trajectory/acoustic numeric value is opened:

1. inspect public Dropbox response metadata only;
2. determine downloadable archive/file inventory and sizes;
3. freeze a structural filename/schema allowlist;
4. establish bat identifiers, condition labels and repeated-trial support without reading movement outcomes;
5. freeze the movement representation and support thresholds;
6. only then open numeric trajectories.

## Claim ceiling

A positive P1 would support:

> **persistent individual movement policy survives a controlled within-individual sensory perturbation.**

It would not establish:
- that the policy is learned rather than biomechanical;
- that masker response is the same mechanism as wild vertical individuality;
- a universal bat policy axis;
- adaptation or fitness benefit.

A positive P3 would support individual heterogeneity in response to this manipulation, but not a general reaction norm across environments.
