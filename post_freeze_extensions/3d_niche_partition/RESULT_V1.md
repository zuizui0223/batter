# 3D niche-partition result v1

## Status

**POST-OUTCOME GENERATED ANALYSIS, PRE-SPECIFIED BEFORE THE FIRST 3D-OVERLAP OUTPUT.**

Contract:
- `post_freeze_extensions/3d_niche_partition/CONTRACT_V1.md`
- `post_freeze_extensions/3d_niche_partition/contract_v1.json`

Authoritative workflow:
- run: `36881187913`
- head: `676ae76aec952a38410766577d51c5eca438a6c1`
- conclusion: success

The integrated JAE submission branch remains unchanged.

## Primary question

Within horizontally shared 500-m cells, is a session's centered vertical configuration more similar to other sessions of the same individual than to sessions of other individuals?

Primary statistic:
`D = self O_Z|XY - other O_Z|XY`, aggregated equally by session within individual and then equally among individuals.

## Results

| panel | evaluable individuals | self O_Z|XY | other O_Z|XY | D | calibrated excess | p | decision |
|---|---:|---:|---:|---:|---:|---:|---|
| *Tadarida teniotis* | 4 | 0.513 | 0.623 | -0.110 | — | — | structurally non-evaluable (<5) |
| *Eidolon helvum* | 0 | — | — | — | — | — | structurally non-evaluable at 500 m |
| *Hypsignathus monstrosus* | 8 | 0.727 | 0.556 | +0.171 | +0.170 | 0.0001 | supported |
| *Phyllostomus hastatus* 2022 | 5 | 0.832 | 0.766 | +0.066 | +0.066 | 0.0001 | supported |
| *Phyllostomus hastatus* 2023 | 6 | 0.834 | 0.779 | +0.054 | +0.055 | 0.00183 | supported |
| *Phyllostomus hastatus* 2016 | 9 | 0.703 | 0.558 | +0.145 | +0.144 | 0.0251 | supported |

All four panels that met the pre-specified structural gate supported the primary 3D-overlap endpoint. This is **not** a 4/4 prevalence estimate: the fine-scale support gate excluded the two remaining original panels and sharply reduced the evaluable individual set in 2022 and 2023.

Permutation-valid replicate counts were 9,999 (*Hypsignathus*), 9,999 (*P. hastatus* 2022), 9,854 (2023; 145 structurally invalid permutations), and 9,991 (2016; 8 invalid).

## What the primary result means

The result is stronger than merely showing different marginal height distributions. In the four evaluable panels, the same individual's vertical distribution within pairwise-shared 500-m cells is more similar across sessions than the vertical distribution of another individual using shared cells.

This is consistent with **repeatable individual-specific 3D spatial solutions**.

It does **not** establish intentional avoidance or competition. The shared-cell set is defined separately for each session pair, so self and other comparisons can involve different subsets of the landscape. A positive D therefore shows repeatable individual 3D configuration within shared horizontal support, not exact co-occurrence at the same resource point.

## Horizontal versus vertical geometry

The new decomposition separates two related but distinct patterns.

### Horizontal fidelity is strong

Self-session horizontal overlap exceeded other-individual horizontal overlap in every panel with usable estimates:

- *Hypsignathus*: 0.619 vs 0.322
- *P. hastatus* 2022: 0.549 vs 0.334
- *P. hastatus* 2023: 0.547 vs 0.202
- *P. hastatus* 2016: 0.511 vs 0.208

Thus individual 3D niches are not purely vertical; they contain a strong horizontal component.

### Stable vertical solution reuse is also present

Despite that horizontal fidelity, common-horizontal conditional vertical overlap was higher within than between individuals in all four evaluable panels. This is the primary result above.

### Additional vertical segregation is strongest in two panels

The descriptive normalized fraction of horizontal overlap lost when height was added, R_3D = 1 - O_XYZ/O_XY, was:

- *Hypsignathus*: self 0.156, other 0.259
- *P. hastatus* 2016: self 0.185, other 0.315
- *P. hastatus* 2022: self 0.075, other 0.058
- *P. hastatus* 2023: self 0.067, other 0.063

Therefore *Hypsignathus* and *P. hastatus* 2016 show the clearest descriptive signature that adding the vertical dimension separates different individuals more than repeated sessions of the same individual. In 2022 and 2023, the main signal is instead **repeatability of the vertical configuration within shared cells**, not a large extra drop in raw 3D overlap.

These R_3D comparisons are descriptive secondary quantities and are not promoted to additional hypothesis tests.

## Structural boundaries

### Tadarida

Only four individuals met the fixed 500-m shared-support rule, below the pre-specified five-individual gate. Its horizontal overlap was already low between individuals (other O_XY = 0.083), so this dataset is poorly suited to asking whether bats partition the vertical dimension *within* fine-scale shared space.

### Eidolon

No individual met the complete primary structural rule at 500 m. Across several cohorts there were almost no session pairs with >=50 fixes from each session inside shared 500-m cells. This is a structural property of the available tracks, not evidence for or against 3D niche partitioning.

## Biological interpretation

The results suggest a useful distinction between two ecological phenomena:

1. **individual strategy reuse** — the same animal repeatedly uses a similar vertical configuration when it returns to horizontally shared space;
2. **individual niche segregation** — different animals occupy sufficiently different vertical configurations that adding height materially reduces their spatial overlap.

The first is supported in all four evaluable panels. The second is clearest descriptively in *Hypsignathus* and *P. hastatus* 2016.

This distinction is important for the emerging ecological story. A persistent resource landscape may allow an individual to learn and reuse a characteristic 3D solution without requiring individuals to actively avoid one another. Strong niche segregation would be an additional outcome, potentially produced by resource partitioning, competition, morphology, learning or social organization.

## Claim ceiling

Supported:
- repeatable individual-specific 3D spatial geometry exists in the structurally evaluable panels;
- vertical configuration can remain individual-specific within pairwise-shared 500-m horizontal cells;
- horizontal and vertical components of individual spatial specialization can be separated descriptively.

Not established:
- deliberate spatial avoidance;
- competition-driven partitioning;
- different diets or resource species;
- adaptation;
- exact resource-point co-occurrence;
- a universal 3D-partitioning rule across bats.

## Artifact receipts

- *Tadarida*: artifact `11170563498`, sha256 `4d39fca104ca42e0068386f5828116873354792fea8771f29fe54d0c52b4ef81`
- *Eidolon*: artifact `11170888333`, sha256 `c03c783338a4d219b26dffe447c0b0d2c7f0a2f85c7d729d85c81686b1a30d84`
- *Hypsignathus*: artifact `11171378681`, sha256 `5574b295ecfd187e320f8d2446d78e0709033d0680b5f461967f5d199ffa901e`
- *P. hastatus* 2022: artifact `11171412894`, sha256 `a53300e84bd01802e5f093f95e4e38bb4a531a3ae72638e65968ef2293acc4a2`
- *P. hastatus* 2023: artifact `11171482385`, sha256 `a21dee1d503fac249e93333ee6bf064cdef068b70939c19f012ac8346da5f447`
- *P. hastatus* 2016: artifact `11170783704`, sha256 `d57aec0fb76959a5ecfb8b5910b8932f55c0936d943604941f6f780f233a01c3`
