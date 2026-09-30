# Post-freeze mechanism synthesis v10 — external boundary and orthogonal spatial individuality

## Scope

This document supersedes `MECHANISM_SYNTHESIS_V9.md` for post-freeze interpretation.

The frozen JAE v0.3.8 submission on `main` remains unchanged.

v10 integrates the first genuinely response-unopened *Hipposideros* external validation. That validation failed under its frozen source-level criterion. The failure is retained without rescue and changes the generality claim.

---

## 1. Evidence hierarchy

Three evidence classes remain strictly separated.

1. **Submission-confirmed**
   - frozen v0.3.8 analyses on `main`.

2. **Post-freeze localization**
   - original archive stress tests;
   - same-source Nyctalus mechanism-localization analyses;
   - synthesis across those frozen follow-ups.

3. **Prospective external validation**
   - response-unopened external sources with source admission, structural eligibility, estimator, null, calibration and PASS rule frozen before numeric vertical outcomes.

Only class 3 can establish independent external replication.

---

## 2. Submission-confirmed result

Across the original six paper panels, individual identity carries held-out information about vertical use after self and other predictors are standardized to the same tested coarse horizontal occupancy.

After session-median centering removes absolute altitude level, centered vertical-distribution shape identity is supported in the five comparative panels:

- *Eidolon helvum*
- *Hypsignathus monstrosus*
- *Phyllostomus hastatus* 2022
- *P. hastatus* 2023
- *P. hastatus* 2016

The motivating *Tadarida teniotis* panel remains the boundary case: strong absolute vertical identity, but no centered-shape identity.

Thus the submission-level statement remains:

> **Repeatable individual vertical organization extends beyond coarse horizontal occupancy, and in five comparative panels the repeatable information remains in centered distribution shape rather than absolute altitude level alone.**

---

## 3. Original-archive post-freeze localization

These results localize, but do not independently replicate, the original pattern.

### Broad movement state

Centered identity remains after:
- speed conditioning: **5/5**
- speed × turning conditioning: **5/5**

### Horizontal place × state

Where structurally evaluable:
- 2 km: **4/4**
- 500 m: **4/4**
- 250 m: **3/3**

A common 100-m family is structurally unavailable.

### Temporal persistence

Where structurally evaluable:
- >=1 day: **4/4**
- >=3 days: **3/3**
- >=7 days: **2/2**

### Other candidate explanations

Not supported as general explanations:
- body-mass donor similarity: **0/4**
- relative tag burden: unsupported
- primary 1-km patch-fidelity relation: p = **0.05731**, FAIL
- fixed 500-m and 2-km patch-fidelity sensitivities: also FAIL
- *P. hastatus* 2023 phase attribution: p = **0.3774**, FAIL
- focal *Tadarida* uplift reaction norm: structurally sparse and unsupported

These results already suggested that horizontal fidelity and centered vertical organization need not be the same biological property.

---

## 4. Nyctalus external evidence

All Nyctalus analyses use the same Zenodo source (DOI `10.5281/zenodo.7535030`).

### 4.1 First prospective primary

Frozen >=50-fixes/source-track protocol:

- n = **27**
- calibrated excess = **+0.051747**
- p = **0.1224**
- verdict = **FAIL**

The direction is concordant, but the independent confirmatory criterion is not met.

### 4.2 Eligibility robustness

Later post-outcome sensitivity showed calibrated excess positive at **7/7** frozen session-length thresholds:

- min = **+0.03390**
- median = **+0.06086**
- max = **+0.08600**

Thus Nyctalus provides directionally robust convergent evidence, not successful prospective replication.

### 4.3 Same-source mechanism localization

On support-matched target events, centered identity was not attenuated by:

- source HMM movement state:
  - null-centered paired increment **+0.00222**
  - attenuation p = **0.5431**

- distance from track start / radial flight stage:
  - null-centered paired increment **+0.01551**
  - attenuation p = **0.6886**

- source-defined potential-roost distance × local 50-m land cover:
  - n = **20**
  - null-centered paired increment **+0.02871**
  - attenuation p = **0.8204**

The Nyctalus same-source programme is closed.

Within that source, measured context allocation does not explain the identity signal away. This remains post-outcome localization, not external confirmation.

---

## 5. Hipposideros — genuinely response-unopened prospective external validation

Source:
- Dryad DOI `10.5061/dryad.j0zpc86r1`
- source field: native AGL `height`
- paper reports **9 H. armiger** and **8 H. pratti**

### 5.1 Outcome-blind source resolution

Raw GPS contained 19 ID strings:
- D prefix = 11
- H prefix = 8

The first frozen mapping rule correctly failed because raw prefix counts were not 9/8.

No numeric Height had been opened.

An outcome-blind tracking-structure audit then showed:
- D21: zero nights with >=50 fixes
- D22: zero nights with >=50 fixes
- every other raw ID: at least one >=50-fix night

Using the already-frozen >=50-fix session threshold, source-effective tracked IDs therefore became:
- D = **9**
- H = **8**
- total = **17**

This exactly matches the source paper's published tracked counts:
- 9 *H. armiger*
- 8 *H. pratti*

Mapping v2 was frozen before Height:
- D -> *H. armiger*
- H -> *H. pratti*

The original failed mapping rule remains in history.

### 5.2 Frozen structural gate

Before numeric Height was opened, the exact 5-km common-support preflight was frozen and executed.

Estimator-evaluable individuals:
- *H. armiger*: **8**
- *H. pratti*: **5**
- total: **13**

Both species panels passed the frozen species gate.

The exact:
- raw SHA
- species mapping
- training nights
- target nights
- 5-km cells
- target supported-event counts
- primary design SHA

were pinned in commit `75bbbf1` before Height opened.

### 5.3 Frozen primary result

Authoritative run:
- workflow `36717769795`
- artifact `11096159784`
- result-record commit `7cc95c92c7a256fa33652436fe045ee19bd5b1aa`

Source-level equal-species statistic:

- observed centered identity = **-0.075746**
- null mean = **-0.031062**
- calibrated excess = **-0.044684**
- null SD = **0.041894**
- p(null >= observed) = **0.8616**
- frozen verdict = **FAIL**

This is not a low-power positive result. The source-level point estimate is in the opposite direction from the predicted identity advantage.

The frozen external replication therefore fails.

### 5.4 Predeclared secondary species diagnostics

#### Hipposideros armiger

- n = **8**
- calibrated excess = **+0.01929**
- p_upper = **0.3721**

Weakly concordant direction, no support.

#### Hipposideros pratti

- n = **5**
- calibrated excess = **-0.10866**
- p_upper = **0.9678**
- descriptive lower-tail p = **0.0323**

This is secondary only and is not promoted to a new anti-identity hypothesis.

One *H. pratti* individual (H32) has a strongly negative one-target-night diagnostic score, but no exclusion, leave-one-out test, threshold change or subgroup rescue is opened.

The Hipposideros prospective programme is closed.

---

## 6. Prospective external generality after Hipposideros

There are now two prospective external sources outside the original comparative archive:

### Nyctalus
- calibrated excess **+0.05175**
- p = **0.1224**
- positive direction, FAIL

### Hipposideros source
- calibrated excess **-0.04468**
- p = **0.8616**
- opposite direction, FAIL

Therefore:

> **Successful prospective external replication of the centered-shape rule is not established.**

More importantly, the external evidence no longer supports treating centered vertical individuality as a universal bat property.

The appropriate generality statement is now:

> **Repeatable centered vertical organization occurs in multiple original bat systems, but its presence and strength are context- or taxon-dependent across independent tracking programmes.**

This is stronger and more defensible than either:
- "all bats have individual vertical shape", or
- "the original result was an artefact".

The original five comparative panels remain internally supported; the independent external programmes define the boundary of generality.

---

## 7. New ecological synthesis: horizontal fidelity and vertical individuality are orthogonal axes

The Hipposideros system is especially informative because the source paper reports pronounced horizontal site fidelity:
- individuals generally used a single foraging site per night;
- specific sites were maintained for **7–10 consecutive nights**;
- only two foraging-site changes were recorded during the observation period, both <1 km.

Yet centered vertical identity did not replicate.

This external boundary agrees with the original archive's failed patch-fidelity mechanism family.

Together, these results support a broader spatial-ecology distinction:

> **Stable horizontal site fidelity is not sufficient to generate stable centered vertical individuality.**

Individual spatial organization therefore has at least separable axes:

1. **horizontal location fidelity**
   - repeated use of the same site / route / home-range region;

2. **absolute vertical level**
   - individual tendency to occupy higher or lower absolute altitudes;

3. **centered vertical-distribution shape**
   - repeatable organization of vertical use after absolute level is removed.

The original *Tadarida* boundary separates axes 2 and 3.

The Hipposideros boundary separates axis 1 from axis 3.

This makes the central ecological insight broader than a simple "individuality exists" claim:

> **different dimensions of individual spatial specialization can vary independently.**

---

## 8. Context-residual individuality remains a local mechanism synthesis, not a universal rule

Within the original comparative systems and Nyctalus, measured individuality survives increasingly rich matching of:
- coarse horizontal place
- broad kinematic state
- 250–500-m place × state
- multi-day separation
- HMM movement state
- radial flight stage
- potential-roost distance × local habitat

That supports **context-residual individuality where a centered vertical signal exists**.

Hipposideros shows that this should not be generalized as a universal mechanism.

The revised formulation is:

> **When centered vertical individuality is present, it can persist within measured contexts rather than being reducible to context allocation alone; however, not all bat systems exhibit that centered individuality in the first place.**

The next mechanistic question therefore shifts from only:

> What causes vertical individuality?

to two linked questions:

1. **What generates within-context vertical individuality where it occurs?**
2. **What ecological or biological conditions determine whether that individuality emerges at all?**

---

## 9. Remaining live mechanisms

For systems that do show centered vertical individuality:

### Fine resource / route structure
- exact feeding tree or prey patch
- exact occupied roost
- sub-50-m corridor
- canopy gap / microtopography

### Fine local atmosphere
- wind
- uplift
- boundary-layer structure
- individual environmental reaction norms

### Detailed morphology
- wing loading
- aspect ratio
- wing shape

### Experience
- memory
- learned routes
- stable routines

These are candidate generators of the within-context component, not demonstrated causes.

For cross-system heterogeneity, future work must also ask which ecological traits predict whether centered vertical individuality exists at all.

---

## 10. What must not be claimed

Do not claim:
- universal centered vertical individuality across bats;
- successful prospective external replication;
- that Hipposideros disproves the original five-panel result;
- that *H. pratti* has a confirmed anti-individual vertical phenotype;
- that H32 should be excluded;
- that horizontal site fidelity predicts vertical individuality;
- that context-residual individuality is universal;
- that memory, morphology or atmosphere has been identified as the cause.

---

## 11. Programme status

Closed:
- original archival mechanism programme;
- Nyctalus same-source mechanism programme;
- first Nyctalus prospective validation;
- Hipposideros prospective validation.

No Hipposideros rescue analyses are authorized:
- no alternate grids;
- no alternate vertical bins;
- no lower fix/support thresholds;
- no species pooling;
- no *H. armiger*-only promotion;
- no H32 exclusion;
- no absolute-height rescue;
- no temperature/speed/competition mechanism extension.

Further progress requires a new question or new data, not reinterpretation of the frozen FAIL.

---

## 12. External heterogeneity is now the right question — but not yet estimable

The pre-existing external candidate universe now yields:

- *Nyctalus noctula*: structurally evaluable; prospective source-level effect **+0.05175**;
- *Hipposideros* source: structurally evaluable; prospective source-level effect **-0.04468**;
- *Leptonycteris nivalis*: **structural FAIL** under the frozen common estimator, with 0 nights reaching >=50 fixes and numeric altitude unopened;
- *Desmodus rotundus*: sparse external candidate without a comparable source-level effect currently established;
- remaining screened candidates: fail individual-count, native-vertical, raw-event or tagged-track requirements.

Thus only **two independent external systems** currently provide comparable centered-identity effects.

That is enough to reject a simple universality narrative, because the two frozen prospective effects differ in direction.

It is **not** enough to estimate a stable between-system effect distribution or test ecological predictors of heterogeneity.

Therefore do not fit:
- a random-effects meta-analysis and interpret tau as a population estimate;
- source-level meta-regression;
- ecological predictor selection;
- rankings of systems by individuality.

A future heterogeneity programme must first increase the number of independent, structurally comparable systems under a source universe and stopping rule frozen before their vertical outcomes are opened.

The next programme should ask:

> **What predicts whether horizontal fidelity, absolute vertical level, and centered vertical shape become individualized in the same or different ecological systems?**

See `EXTERNAL_HETEROGENEITY_FEASIBILITY_V1.md`.

---

## Final position

The complete programme now supports five levels of inference.

1. **Original evidence:** multiple bat systems show repeatable vertical individual organization beyond coarse horizontal occupancy.

2. **Centered-shape specificity:** five comparative panels retain identity after absolute altitude level is removed, whereas *Tadarida* does not.

3. **Mechanistic localization where the signal exists:** measured context allocation is insufficient to explain the signal in the original comparative archive and Nyctalus.

4. **External boundary:** neither prospective external source passes the frozen centered-shape replication criterion; Nyctalus is directionally positive but non-significant, while Hipposideros has a negative source-level calibrated estimate.

5. **General ecological synthesis:** horizontal fidelity, absolute vertical level, and centered vertical-distribution shape are separable axes of individual spatial organization. Strong horizontal routine does not imply stable vertical shape individuality.

This v10 hierarchy preserves the original discovery while defining its ecological boundary rather than overstating universality.
