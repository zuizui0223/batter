# Reversible sensory perturbation source-design freeze v1

## Status

**PUBLISHED-DESIGN FREEZE BEFORE ANY NEW PUBLIC-DATA OUTCOME OPENING.**

Parent:
`SOURCE_RECEIPT_V1.md`

Source:
Taub & Yovel (2020), *Segregating signal from noise through movement in echolocating bats*,
Scientific Reports 10:382, DOI `10.1038/s41598-019-57346-2`.

No public trajectory or acoustic numeric value from the source-declared Dropbox has been opened by this programme.

## Source-defined experimental sequence

The published Methods/Results establish the following ordered within-individual design for six *Pipistrellus kuhlii* bats:

1. **Baseline A — styrofoam target, no masker**
   - approximately one week of training;
   - at least 40 recorded no-masker landings per bat before masker introduction.

2. **Masker 30 cm — styrofoam target**
   - acoustically reflective masker 30 cm behind target.

3. **Masker 10 cm — styrofoam target**
   - stronger masking challenge.

4. **Recovery/control B — foam target, no masker**
   - after the 10-cm condition and before the final masker condition;
   - bats were trained for four days on the weaker foam target with **no masking board**.

5. **Re-perturbation — foam target + masker**
   - masker reintroduced behind the foam target;
   - source comparison is against the immediately preceding foam/no-masker condition.

The target change from styrofoam to foam means block 4 is **not a return to the identical original baseline**.
It is, however, a source-defined **masker-removal recovery/control block** followed by masker re-addition under the same foam target.

## Biological leverage

This sequence separates two experimentally manipulated objects:

- acoustic masking state;
- target reflectivity.

The source paper reports that the masking manipulation changes movement geometry.
That published direction is inherited background and must not be used to tune any new individual-policy estimator.

## Prospective questions

### Q1 — policy identity through sensory perturbation

After removing source-condition mean/scale using a representation frozen before new outcomes,
does biological identity remain predictive across the masker manipulation?

This is the primary causal-maintenance question.

### Q2 — masker-removal reversibility

If public files reproducibly identify block 4 and block 5:

> does the population operating state move when the masker is removed and move again when the masker is re-added, while personal identity remains detectable across the transition?

This is stronger than a simple condition contrast because the same bats provide the repeated biological units.

### Q3 — baseline-to-recovery retrieval

Because target material changes, do **not** test literal equality between original styrofoam/no-masker and foam/no-masker.

A permissible bounded test is only:
- whether personal identity estimated under earlier conditions predicts the recovery/control block after source-condition normalization.

Do not call this exact baseline recovery.

## Hard interpretation boundary

Even a successful Q1/Q2 supports:

> a persistent personal movement-policy component survives a reversible sensory perturbation.

It does **not** establish:
- that the personal component is learned;
- that masker responses are social/environmental reaction norms in the wild;
- that the exact same policy axes apply without a separately frozen representation;
- a universal bat control law.

## Structural continuation rule

Before any movement value is opened, the public archive must expose reproducibly:

- biological bat ID;
- source condition/block identity;
- repeated movement units per bat;
- time + 3-D coordinates or a source-documented equivalent.

If the recovery/control block cannot be distinguished from the final masker block using filenames/schema/metadata alone, Q2 stops.

No phase may be inferred from the observed movement response.
