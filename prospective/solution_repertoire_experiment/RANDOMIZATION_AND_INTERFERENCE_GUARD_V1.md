# Randomization and interference guard v1

## Purpose

Protect the matched-family experiment from:
- family confounding;
- period/order confounding;
- cross-family learning spillover;
- incorrect sign-flip inference;
- post-outcome subset rescue.

## Restricted block randomization

Randomize eligible bats after the capability audit in complete blocks of four.

Each block contains exactly one animal in each cell:

| Cell | OPEN family | acquisition starts |
|---|---|---|
| 1 | A | A |
| 2 | A | B |
| 3 | B | A |
| 4 | B | B |

The four cells are randomly assigned to the four opaque animal IDs in that block.

This guarantees orthogonality between environment family receiving OPEN acquisition and which family is experienced first.

Acquisition sessions then alternate A/B, so first-family order is a small schedule perturbation rather than a complete block-order difference.

## Why not a naive paired sign flip

The primary self-history statistic uses donor histories.

Changing OPEN/CONSTRAINED assignment changes both focal treatment labels and which donor histories belong to each treatment pool.

Therefore the full statistic must be recomputed for each allowed treatment assignment.

A sign flip applied after computing individual contrasts is not the correct randomization null.

## Conditional assignment space

Condition on the randomized starting-family order.

Within each four-bat block:
- among the two A-start animals, exactly one receives A-open and one B-open;
- among the two B-start animals, exactly one receives A-open and one B-open.

That gives 2 × 2 = 4 compatible treatment assignments per complete block.

With B complete blocks:
- assignment count = 4^B.

This is the confirmatory permutation space.

## Spillover / interference

The same bat experiences both task families.

Possible organism-level spillover includes:
- generic obstacle-learning skill;
- exploration tendency;
- altered motivation;
- fatigue/habituation;
- learned movement scaling.

The design minimizes temporal imbalance by interleaving families.

A generic spillover shared across families tends to reduce the OPEN-versus-CONSTRAINED contrast and is therefore expected to be conservative for a family-specific effect.

Asymmetric spillover can still complicate interpretation.

Therefore:
- report the effect by starting-family stratum;
- report the effect by A-open/B-open assignment;
- never select the favorable stratum;
- if signs reverse across a randomized factor, narrow interpretation to context/order dependence.

## No washout rescue

Do not inspect the data and then invent:
- a washout interval;
- first-period-only analysis;
- later-trial-only analysis;
- one-family analysis.

If a washout period is biologically required, it must be inserted before confirmatory collection and the contract refrozen.

## Future clean replication

If cross-family interference appears substantial, the strongest independent replication is a parallel-group design in naive animals:
- OPEN acquisition group;
- CONSTRAINED acquisition group;
- identical common-OPEN probe.

That future design is not a rescue analysis for the paired experiment.