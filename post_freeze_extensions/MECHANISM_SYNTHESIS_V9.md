# Post-freeze mechanism synthesis v9 — context-localized vertical individuality

## Scope

This document supersedes `MECHANISM_SYNTHESIS_V8.md` for post-freeze interpretation.

The frozen JAE v0.3.8 submission on `main` remains unchanged.

The purpose of v9 is to integrate the integrity-corrected Nyctalus history with the completed same-source mechanism-localization programme. The programme is now closed by the frozen stop rule.

---

## 1. Evidence hierarchy remains unchanged

Three evidence classes are kept separate.

1. **Submission-confirmed**
   - frozen v0.3.8 analyses on `main`.

2. **Post-freeze exploratory / mechanism-localization**
   - archive stress tests and all same-source Nyctalus mechanism analyses opened after the original outcomes were known.

3. **Prospective external validation**
   - only a genuinely response-unopened external source tested under a fully frozen protocol qualifies.

A frozen contract improves reproducibility but does not convert outcome-informed follow-up into independent confirmation.

---

## 2. Submission-confirmed ecological result

Across the six paper panels, identity-matched vertical profiles contain more held-out information than expected under whole-session exchangeability after coarse horizontal occupancy is standardized.

After session-median centering removes absolute altitude level, centered vertical-distribution shape identity is supported in the five comparative panels:

- *Eidolon helvum*;
- *Hypsignathus monstrosus*;
- *Phyllostomus hastatus* 2022;
- *P. hastatus* 2023;
- *P. hastatus* 2016.

The motivating *Tadarida teniotis* panel is the boundary case and does not retain centered-shape identity.

The submission-level conclusion therefore remains:

> **Repeatable individual organization of vertical space use extends beyond coarse horizontal occupancy, and in five comparative panels the repeatable information remains in the shape of the centered vertical distribution after absolute altitude level is removed.**

No causal mechanism is established by the submission itself.

---

## 3. Original-archive mechanism localization

These are post-freeze exploratory stress tests, not independent confirmation.

### Broad movement state

Centered identity remains after:
- speed conditioning: **5/5** comparative panels;
- speed × turning conditioning: **5/5**.

Thus broad kinematic-state composition is insufficient as a general explanation in the original comparative archive.

### Horizontal place × movement state

Where structural support permits, centered identity remains after matching:
- 2-km place × speed×turn: **4/4**;
- 500-m place × speed×turn: **4/4**;
- 250-m place × speed×turn: **3/3**.

A common 100-m family is structurally unavailable.

Thus >=250–500-m route/patch allocation is insufficient by itself in the evaluable systems.

### Temporal persistence

Where structurally evaluable, identity remains when self-history is separated from the target by:
- >=1 day: **4/4**;
- >=3 days: **3/3**;
- >=7 days: **2/2**.

This supports a stable multi-day component and week-scale persistence in two systems.

### Shared night context

At 2-km place × kinematic state, same-individual history remains more informative than contemporaneous other individuals in **3/4** evaluable panels.

Broad shared calendar-night context is therefore insufficient as a general explanation.

---

## 4. Mechanism candidates not supported as general explanations

### Simple body mass

Donor-target body-mass similarity predicts vertical-profile transfer in **0/4** evaluable panels.

### Relative tag burden

The cross-panel monotonic association between tag mass / animal mass and calibrated centered identity is unsupported (p=0.1399).

### Fine horizontal patch fidelity

The primary 1-km patch-fidelity relationship misses its frozen criterion (p=0.05731), and the fixed 500-m and 2-km sensitivities do not pass.

### Temporal-phase attribution

The support-matched *P. hastatus* 2023 phase-attribution family fails (p=0.3774).

### Focal uplift reaction norm

The archived *Tadarida* uplift-reaction endpoint is structurally sparse and unsupported (p=0.3337).

These negative results narrow the candidate space without establishing the remaining mechanisms.

---

## 5. Nyctalus external evidence — confirmatory status

All Nyctalus analyses use the same Zenodo source:

- DOI `10.5281/zenodo.7535030`;
- file `Observed_GPS_locations.csv`;
- SHA256 `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`.

### First prospective primary test

Frozen >=50-fixes/source-track protocol:

- n = **27**;
- calibrated excess = **+0.051747**;
- p = **0.1224**;
- verdict = **FAIL**.

This remains the authoritative prospective external-validation result.

### Later relaxed-eligibility analysis

- n = **36**;
- calibrated excess = **+0.086005**;
- p = **0.0115**.

Because the same source Height response had already been opened, this is post-outcome sensitivity evidence.

### Eligibility robustness

Across frozen session-length thresholds 0 / 20 / 30 / 40 / 50 / 75 / 100 fixes, calibrated excess is positive at **7/7** thresholds:

- minimum = **+0.03390**;
- median = **+0.06086**;
- maximum = **+0.08600**.

Therefore Nyctalus supplies **directionally robust convergent external evidence**, but not a successful prospective replication.

---

## 6. Nyctalus mechanism localization

The Nyctalus same-source programme was designed to ask whether increasingly ecological context variables explain away the centered individual signal.

The key inferential quantity is a **support-matched paired increment**:

`identity gain with richer context - identity gain with simpler context`

Both models are scored on the same target events. A sufficiently negative null-calibrated increment would support attenuation by the added context.

### 6.1 Independently generated HMM movement state

Support-matched comparison on the same ARM/COM event pool and the same 27 individuals:

- collapsed 5-km-cell calibrated excess = **+0.04821**, p=0.0652;
- 5-km-cell × HMM-state calibrated excess = **+0.05044**, p=0.0707;
- paired state increment = **+0.01191**;
- null-centered paired increment = **+0.00222**;
- attenuation p = **0.5431**.

Result:

> **Adding the source HMM movement-state label does not attenuate centered vertical individuality.**

The earlier loss of conventional significance from n=36 to n=27 therefore cannot be interpreted as evidence that behavioural-state mixture explains the signal. On identical support, the effect is essentially unchanged.

### 6.2 Distance from track start / central-place flight stage

A nonvertical audit established that source `dist_start` is distance from the first x-y position of each track:

- best conversion: source units ×1000 = metres;
- Pearson r = **0.9999959**;
- median absolute error = **0.463 m**;
- 93.46% of track first records have dist_start=0.

This is a central-place / flight-stage proxy, not verified roost distance.

The structurally supported 4-bin context was:
- 0–0.5 km;
- 0.5–2 km;
- 2–5 km;
- >5 km from track start.

Support-matched n = **22**:

- HMM-state base calibrated excess = **+0.04103**, p=0.1466;
- + track-start-distance context = **+0.05654**, p=0.1232;
- paired context increment = **+0.02927**;
- null-centered paired increment = **+0.01551**;
- attenuation p = **0.6886**.

Result:

> **Repeated allocation to different radial stages of a central-place flight is not supported as a sufficient explanation.**

### 6.3 Source-defined potential-roost distance × local land cover

The source RSF dataset was linked deterministically to all observed GPS events.

Linkage audit:
- observed GPS rows = **8,129**;
- RSF used rows = **8,129**;
- tracks = **107/107** matched;
- bijective trackwise linkage = **107/107**;
- nearest-link median = **0.187 m**;
- 95th percentile = **0.467 m**;
- maximum = **0.502 m**;
- fraction <=1 m = **1.000**.

Available source ecological context included:
- `DistanceAssumedRoostsInKm`;
- `main_clc2_ratrel` local 50-m land-cover class;
- forest context and additional turbine/resource fields.

Before opening the vertical paired result, structural preflight selected the finest supported context:

> 5-km cell × HMM state × potential-roost-distance 4-bin × detailed local 50-m land-cover class.

Exact n = **20**.

Result:
- HMM-state base calibrated excess = **+0.04355**, p=0.1228;
- + potential-roost distance × land cover calibrated excess = **+0.07226**, p=0.0768;
- paired context increment = **+0.04223**;
- null-centered paired increment = **+0.02871**;
- attenuation p = **0.8204**.

Result:

> **Measured potential-roost distance plus local 50-m land-cover context does not attenuate centered vertical individuality.**

The richer context estimate is numerically larger, not smaller.

This does not prove that resource context strengthens individuality; the family was designed as an attenuation test, and the positive paired increment is not promoted to a new causal claim. It does show that these measured context-mixture explanations fail to explain the signal away.

---

## 7. The main mechanistic synthesis: context-residual individuality

Across the original comparative archive and the completed Nyctalus localization programme, a common pattern emerges.

Individual vertical organization persists after standardizing progressively richer contextual information:

1. coarse horizontal occupancy;
2. broad speed / speed×turning state;
3. 250–500-m horizontal place in evaluable systems;
4. same-night context in most evaluable systems;
5. independent source HMM movement state in Nyctalus;
6. central-place / flight-stage distance in Nyctalus;
7. source-defined potential-roost distance × local 50-m land-cover context in Nyctalus.

The strongest mechanistic statement now supported by the post-freeze programme is:

> **The observed individuality is not well explained as a simple mixture of where an individual goes, which broad movement state it occupies, or which measured central-place/resource context it experiences. A substantial component resides within the measured contexts themselves.**

This is **context-residual individuality**.

It is stronger than merely saying that individuals occupy different contexts repeatedly. The same individual retains predictive information after self and other histories are evaluated within increasingly matched contexts.

This is still a distribution-level inference. It does not identify the biological substrate of the within-context component.

---

## 8. What remains unresolved

The remaining live mechanisms are now narrower.

### 1. Exact sub-context resource / route specialization

Still unresolved:
- actual occupied roost identity;
- exact feeding tree or prey patch;
- narrow flight corridor;
- sub-50-m habitat structure;
- canopy gap / microtopography.

The source land-cover variable is local habitat context, not exact food-resource identity.

### 2. Fine local atmosphere and individual reaction norms

Still unresolved:
- local wind;
- uplift;
- boundary-layer structure;
- pressure / thermal conditions at the route scale;
- individual-specific environmental slopes.

Broad same-night context is insufficient, but exact local atmospheric exposure is not measured comparably.

### 3. Stable morphology

Still unresolved:
- wing loading;
- aspect ratio;
- wing shape;
- muscle / body condition.

Simple body mass is unsupported and is not an adequate substitute.

### 4. Memory, experience and learned routines

Multi-day and week-scale persistence is compatible with these mechanisms, but does not identify them causally.

---

## 9. Important boundary: what the programme does not prove

Do not claim:
- a universal intrinsic personality;
- a genetic vertical-flight phenotype;
- learning or memory as the demonstrated cause;
- exact resource independence;
- local atmospheric independence;
- successful prospective Nyctalus replication;
- that richer ecological context causally increases individuality.

The post-freeze programme establishes **failure of several measured context-mixture explanations**, not the unique identity of the residual mechanism.

---

## 10. Stop rule and next decisive evidence

The Nyctalus same-source mechanism programme is now **closed**.

Do not open:
- alternate roost-distance bins;
- forest-only or roost-only rescue analyses;
- sex/age subgroups;
- continuous HMM probabilities;
- turbine-distance variants;
- alternate land-cover groupings;
- new grids;
- new target-event minima;
- alternate vertical endpoints or bins.

The next scientific step must be one of:

1. **a genuinely new external source under a separately frozen prospective programme**, or
2. **new field data designed to force cross-individual overlap in exact contexts**.

The decisive field stratum is:

`exact route/resource × independently observed behavioural state × local environment × time window`

with individual wing morphology and repeated tag calibration measured simultaneously.

---

## Final position

The completed evidence hierarchy supports four statements.

1. **Established in the frozen submission:** repeatable vertical individual organization persists beyond coarse horizontal occupancy; five comparative panels retain centered distribution-shape identity.

2. **Strong post-freeze localization in the original archive:** individuality survives broad kinematic matching, 250–500-m place matching where testable, and multi-day separation.

3. **Directionally robust external convergence:** Nyctalus calibrated excess remains positive across all seven frozen eligibility thresholds, although the first prospective primary test does not meet its frozen inferential threshold.

4. **Mechanistic narrowing:** in Nyctalus, identity is not attenuated by independent HMM state, radial flight-stage context, or source-defined potential-roost-distance × local-land-cover context. Together with the original archive, this supports a **context-residual individual organization** that remains after several increasingly ecological context-mixture explanations are controlled.

Further progress now requires genuinely new information rather than additional same-source model variants.
