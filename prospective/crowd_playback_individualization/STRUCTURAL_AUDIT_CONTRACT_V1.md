# Crowd-playback developmental convergence structural audit v1

## Status

**OUTCOME-BLIND STRUCTURAL AUDIT. PUP ACOUSTIC COORDINATES REMAIN CLOSED.**

## Source

Prat, Azoulay, Dor & Yovel (2017),
*Crowd vocal learning induces vocal dialects in bats: Playback of conspecifics shapes fundamental frequency usage by pups*,
PLOS Biology 15:e2002556.
DOI: `10.1371/journal.pbio.2002556`.

Supporting data:
- S1 Data: `10.1371/journal.pbio.2002556.s011` (XLSX);
- S2 Table: `10.1371/journal.pbio.2002556.s007` (PDF; call-count support).

## Verified design facts

Pregnant females were randomly assigned to three identical acoustic chambers:

- High-F0 playback;
- Low-F0 playback;
- control playback.

Initial assignment:
- 5 mothers per group.

Post-birth cohort:
- one High-F0 pup died;
- one control pup died;
- one mother + ~1.5-month-old pup was later added to the control chamber.

Final pup counts in Fig. 2:
- High-F0 = 4;
- Low-F0 = 5;
- Control = 5.

Recording sessions:
1. 12–18 weeks;
2. 31–35 weeks;
3. 40–43 weeks;
4. 48–51 weeks.

Fig. 2 uses a fixed 2-D LDA space trained **only on the playback calls**, then projects pup calls into those pre-defined axes.

Thus the coordinate system itself is independent of the pup outcomes.

## Biological question

The published paper establishes group-level learned dialect separation.

The new individual-specialization question is:

> **As a shared social-acoustic history drives group dialect formation, do pups within the same playback history converge toward one another, or do they retain comparable within-group individuality while the group mean moves?**

This is a formation/canalization question, not another group-mean test.

## Structural opening authorized now

Open S1 Data only for:

- workbook sheet names;
- sheet dimensions;
- header / label strings;
- pup IDs;
- playback-group labels;
- sex labels if present;
- session labels;
- names of Fig. 2 coordinate columns;
- number of pup-level rows per group × session.

Do not report:
- LD1/LD2 numeric values;
- F0 values;
- entropy values;
- group centroids;
- dispersions;
- treatment differences;
- p-values.

## Original-randomization boundary

A clean original-randomization analysis is authorized only if the late-added control pup can be structurally identified in the public source.

If identifiable:
- primary cohort = original randomized surviving pups:
  - High-F0 4;
  - Low-F0 5;
  - Control 4;
  - total 13.

If not identifiable:
- use final 14-pup cohort;
- inference is explicitly **conditioned final-cohort permutation**, not a clean original randomization test.

No individual may be selected by its acoustic values.

## Preferred endpoint architecture if schema passes

Use only the source-defined Fig. 2 pup averages in fixed playback-derived coordinates:

[
z_{i,s}=(LD1,LD2).
]

No re-fitting of LDA.

No F0-only rescue.

No entropy-only rescue.

No feature selection.

## Candidate formation statistic

For every session s and playback group g:

[
W_{g,s}
=
rac{1}{n_g}
sum_i ||z_{i,s}-ar z_{g,s}||_2^2.
]

Equal-group aggregate:

[
W_s
=
rac{1}{3}sum_g W_{g,s}.
]

Primary developmental convergence contrast is intended to compare the earliest session against later sessions, but the exact late-session combination and permutation null will be frozen only **after schema structure is known and before coordinate values are opened**.

## Claim ceiling

Even a supported convergence result would establish only:

> shared developmental social-acoustic history can canalize / reduce within-history vocal differentiation in the fixed dialect coordinate space.

It would not establish:
- movement-policy formation;
- broad individuality across the whole repertoire;
- one universal social-learning mechanism;
- wild spatial specialization.

A null result would mean dialect mean separation does not require detectable reduction of within-group individual differentiation.
