# Crowd-learning personal-offset audit contract v1

## Status

**OUTCOME-BLIND STRUCTURAL AUDIT. NO PUP LD COORDINATES OR F0 VALUES OPENED.**

## Source

Prat, Azoulay, Dor & Yovel (2017), Crowd vocal learning induces vocal dialects in bats.
PLOS Biology 15:e2002556. DOI 10.1371/journal.pbio.2002556.

Public numeric supplement: S1 Data, DOI 10.1371/journal.pbio.2002556.s011.

Published design:
- pregnant females randomly assigned to three identical acoustically isolated chambers;
- resulting pup groups: 5 / 5 / 4;
- Control / Low-F0 / High-F0 playback;
- playback from day 1 for about one year;
- same pups recorded at four developmental sessions;
- Figure 2 coordinates use two LDA axes derived from playback calls, not pup outcomes.

## New biological question

> While the learned group dialect changes across development, does each pup retain a stable personal vocal offset relative to its own group?

This is a within-group repeated-individual identity test during a shared developmental learning process, not a new playback-treatment effect test.

## Stage 1 structural opening only

Report only workbook sheet names, dimensions, string labels, merged ranges and numeric-cell counts. Do not report LD1, LD2, F0, distances, treatment effects or identity statistics.

## Figure-2 proceed gate

Proceed only if the Figure-2 sheet structurally recovers 14 pups, group sizes 5/5/4, four sessions, two coordinates per pup-session, and a freezeable missingness pattern.

## Planned primary if structure passes

1. Use Figure-2 2-D coordinates only.
2. Subtract group x session centroid.
3. Target = session 4 residual position.
4. History = equal mean residual position across sessions 1-3.
5. Compare target to own versus other pups' histories within the same group.
6. Equal pup weighting.

Exact null: independently permute session-4 labels within each group.
If support is 5/5/4, exact assignments = 5! x 5! x 4! = 345,600.

## Claim ceiling

A positive result supports coexistence of a learned shared dialect with persistent individual vocal offsets. It does not show that playback creates individuality or identify a neural carrier.

## No rescue

After Figure-2 opening do not switch to F0 distributions, sessions, group subsets, new axes, or call-level pseudoreplication.
