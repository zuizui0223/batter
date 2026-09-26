# batter

Ecological analysis of individual specialization in three-dimensional bat airspace.

## Biological question

When a bat repeats its vertical use across nights, **what exactly is repeatable**?

Two different architectures can produce an individual vertical signature:

1. **altitude-wide identity** — an animal repeats an overall vertical distribution;
2. **place-coupled identity** — an animal repeats which vertical layer it uses at particular
   horizontal places.

The predictive decomposition is:

```text
conditional identity gain
= marginal-height identity gain
+ identity × location increment
```

All main tests are cross-night. GPS fixes estimate distributions; the biological summary unit is
the individual.

## Origin

The project began from an ODSP result in *Tadarida teniotis*: the fitted population was vertically
thick (`exp(H(Z|X,Y)) ≈ 4.02` effective states) but its pooled `P(z|x,y)` failed to transfer
to held-out individuals.

`batter` asks whether that failure reflects **individual specialization**, rather than absence of
vertical structure. The frozen ODSP endpoint is not retuned or reopened.

## Current result

### *Tadarida teniotis* — focal 3-D validation

At 5-km horizontal conditioning:

- conditional MSL identity: **+0.428 nats/fix**, 5/6 bats positive;
- marginal MSL identity: +0.052;
- place × MSL identity: **+0.376**;
- conditional AGL identity: +0.337;
- marginal AGL identity: −0.255;
- place × AGL identity: **+0.591**;
- terrain-elevation conditional identity: +0.007.

The focal signature is therefore primarily place-coupled rather than a simple preferred height
or repeated microtopographic elevation.

Orthogonal controls strengthen that interpretation:

- another night from the same bat beats contemporaneous other bats on the target night
  (+0.484 AGL; +0.436 MSL);
- direct pairwise self-win fractions are 0.736 for AGL and 0.776 for MSL;
- a frozen common uplift-reaction mechanism was not supported.

### *Eidolon helvum* — independent prospective replication

Before numeric height was opened, source identity, cohorting and the pass rule were frozen.

At 5 km within site × year cohorts:

- **20 evaluable individuals**;
- conditional identity: **+0.219**;
- marginal identity: +0.002;
- place × height: **+0.217**;
- **17/20** individuals positive.

All frozen place-coupled replication criteria passed.

### *Hypsignathus monstrosus* — second independent species replication

At 5 km:

- 24 evaluable individuals;
- conditional identity: **+0.029**;
- marginal identity: −0.021;
- place × height: **+0.050**;
- 13/24 positive.

Its frozen replication rule passed. The signature is clearest at 2.5 km
(conditional +0.131; place × height +0.152).

### *Phyllostomus hastatus* — a different architecture

The prospectively frozen 2022 panel did **not** replicate place-coupled specialization.

At 5 km:

- 33 evaluable individuals;
- conditional identity: +0.056;
- marginal identity: **+0.176**;
- place × height: **−0.120**.

This is biologically informative: vertical identity is concentrated in an animal-wide height
distribution rather than in a local routing rule.

The architecture is not a stable species or simple seasonal property:

- 2023: conditional +0.033, marginal +0.013, interaction +0.020;
- an untouched 2016 dry-season panel was prospectively frozen to replicate the 2022
  altitude-wide architecture, but **failed**:
  conditional +0.058, marginal +0.016, interaction +0.041.

So the data do not support a simple “dry season → altitude-wide” explanation.

## Main ecological statement

> **Individual specialization in bat airspace has multiple spatial architectures. Cross-night
> identity can reside in a bat-wide altitude distribution, in repeatable place-specific vertical
> routing, or in a mixture of both; the balance need not be fixed even within a species.**

That is now the center of the project.

## Outcome-blind source screen

A fixed checksum-pinned search covered 23 public Movebank bat parent datasets. Nineteen exposed
raw event CSVs directly; four legacy packages were recovered through child handles. Numeric height
values were not used for admission.

Only six sources from four taxa passed all structural requirements:

- native vertical state on the same event as x-y and time;
- >=8 individuals with x-y-height presence;
- >=5 repeat-tracked individuals with >=50-fix sessions.

Many otherwise interesting bat datasets were excluded because a native same-event height field
was absent. The Brazilian free-tailed bat dataset, for example, contains seven animals and no
native height column in the public GPS table.

## Key files

- `MANUSCRIPT_SPINE.md` — current paper logic
- `SPECIALIZATION_ARCHITECTURE_SYNTHESIS.md` — architecture table and interpretation
- `CROSS_SPECIES_SYNTHESIS.md` — cross-taxon synthesis
- `RESULTS_V1.md` — focal *Tadarida* self-transfer
- `AGL_SELF_TRANSFER_RESULT.md` — terrain-relative validation
- `THREE_COMPONENT_RESULT.md` — terrain/AGL/MSL decomposition
- `NIGHT_CONTEXT_CONTROL_RESULT.md` — contemporaneous-night control
- `PAIRWISE_VERTICAL_FINGERPRINT_RESULT.md` — direct individual-to-individual comparison
- `EIDOLON_INDEPENDENT_REPLICATION_RESULT.md` — first independent species replication
- `UPLIFT_REACTION_NORM_RESULT.md` — closed mechanism test
- `REPLICATION_CANDIDATE_LEDGER.md` — outcome-blind candidate decisions

## Claim boundary

The analyses concern repeatable **vertical flight/airspace use**. They do not by themselves
establish foraging state, personality, learning, optimality or a causal environmental mechanism.

Vertical reference systems differ among source datasets (AGL, MSL, ellipsoid). Cross-species
comparisons therefore concern the architecture of predictive identity, not equality of absolute
flight heights.
