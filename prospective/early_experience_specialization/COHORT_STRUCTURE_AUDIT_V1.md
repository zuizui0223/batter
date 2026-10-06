# Early-experience cohort structure audit v1

## Status

**OUTCOME-BLIND COHORT / ROW-GRAIN AUDIT.**

No Boldness, Exploration, or Activity values may be reported at this stage.

## Source table

`All seasons personality data.xlsx`
sheet:
`Full_Data`.

## Authorized design columns

Values may be read and reported only for:
- Bat_no;
- Individual;
- Season;
- Origin;
- Colony;
- Colony type;
- Trial name;
- Trial.

These fields define biological identity, randomization strata, treatment, and repeated-measure structure.

## Authorized outcome structure checks

For:
- Boldness;
- ExpuNIQUE;
- AllActivityNormed;

the audit may report only:
- finite/nonmissing counts;
- whether values are structurally constant within a Bat_no × Trial unit;
- number of Bat_no × Trial units with one usable value;
- no actual numeric trait value.

## Primary structural gate

Proceed only if Season 2 can recover:

- the randomized Enriched / Impoverished treatment labels;
- Beit Guvrin and Herzliya origins or equivalent source labels;
- Trials 1, 2, and 3;
- one structurally well-defined Boldness, Exploration, and Activity value per bat × trial;
- a complete-case cohort with all three traits in Trials 1–3.

Expected source design:
- Season 2 Enriched: 14 total source animals;
- Season 2 Impoverished: 15 total source animals;
- origin balance documented in publication:
  - Beit Guvrin 5 / 5;
  - Herzliya 9 / 10.

The exact complete-case primary cohort may be smaller if source rows are structurally missing, but any discrepancy must be recorded before numerical outcome opening.

## Trait mapping

Prospectively map source columns:

- Boldness -> `Boldness`;
- Exploration -> `ExpuNIQUE`;
- Activity -> `AllActivityNormed`.

This mapping is fixed from source method definitions and column semantics before values are opened.

If structural checks show one of these columns is not a bat × trial summary, return:
`STOP_TRAIT_GRAIN_MISMATCH`.

Do not switch to another column after seeing outcomes.
