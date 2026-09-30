# Post-freeze mechanism synthesis v8 — integrity-corrected

## Scope

This synthesis supersedes `MECHANISM_SYNTHESIS_V7.md` for all post-freeze interpretation.

It does not alter the frozen JAE v0.3.8 submission on `main`.

The correction is inferential rather than numerical: the first prospective *Nyctalus noctula* validation is restored as the authoritative confirmatory result, while later analyses on the same source are retained as post-outcome sensitivity/mechanism evidence.

## Evidence hierarchy

The programme now uses three explicit evidence classes:

1. **submission-confirmed** — frozen v0.3.8 analyses on `main`;
2. **post-freeze exploratory/stress-test evidence** — frozen-before-each-test archive extensions generated after the original result family was known;
3. **prospective external validation** — a genuinely new source whose response had not previously been opened under the tested protocol.

A frozen contract inside an already outcome-informed analysis family improves reproducibility but does not by itself make the family independent confirmation.

---

## 1. Submission-confirmed ecological result

Across the original six paper panels, identity-matched vertical profiles retain more held-out information than expected under whole-session exchangeability after self and other predictors are standardized to the same tested coarse horizontal occupancy.

After session-median centering removes absolute altitude level, the centered vertical-distribution shape result passes in the five comparative panels:

- *Eidolon helvum*
- *Hypsignathus monstrosus*
- *Phyllostomus hastatus* 2022
- *P. hastatus* 2023
- *P. hastatus* 2016

The motivating *Tadarida teniotis* panel does not retain centered-shape identity and remains the required boundary case.

Thus the strongest submission-level ecological statement is:

> **Repeatable individual organization of vertical space use extends beyond coarse horizontal occupancy, and in five comparative panels the repeatable information remains in the shape of the centered vertical distribution after absolute altitude level is removed.**

The submission does not identify the causal mechanism.

---

## 2. Post-freeze mechanism localization in the original archive

These analyses are informative stress tests and mechanism-localization results, not independent replications of the original discovery.

### Broad movement-state composition

Centered identity remains after:
- horizontal-speed conditioning: **5/5** comparative panels;
- speed × turning conditioning: **5/5**.

Therefore broad kinematic-state mixture is insufficient as a general explanation in the original comparative archive.

These states are derived kinematic proxies, not independently observed foraging/commuting/social labels.

### Horizontal place × state

Where structural support permits, identity remains after matching:
- 2-km place × speed×turn: **4/4**;
- 500-m place × speed×turn: **4/4**;
- 250-m place × speed×turn: **3/3**.

A common 100-m test is structurally unavailable.

Therefore, in the structurally evaluable systems, persistent allocation among patches/routes at scales >=250–500 m is insufficient by itself. Exact resource identity, narrow corridors, feeding trees, canopy gaps, microtopography and other sub-grid structure remain live explanations.

### Temporal persistence

Where structurally evaluable, centered identity remains when self-history is separated from the target by:
- >=1 day: **4/4**;
- >=3 days: **3/3**;
- >=7 days: **2/2**.

This supports a multi-day stable individual component in the tested systems and a week-scale component in two systems. It does not establish lifetime personality, genetic determination or memory as the cause.

### Same-night context

At 2-km place × kinematic state, same-individual history remains more informative than contemporaneous other individuals in **3/4** evaluable panels. The fourth panel has a positive but threshold-missing result.

Thus broad shared calendar-night context is insufficient as a general explanation, while exact local atmospheric context remains unresolved.

---

## 3. Mechanism candidates that did not receive support

### Simple body mass

A donor-target body-mass similarity gradient is supported in **0/4** evaluable panels.

Conclusion:

> simple body mass is not supported as the common stable trait generating the centered-identity signal.

Wing loading, aspect ratio and other morphology remain unmeasured.

### Relative tag burden

The frozen cross-panel relation between tag mass / animal mass and calibrated centered identity is unsupported (p=0.1399).

Relative payload is therefore not a general monotonic technical explanation.

### Fine horizontal patch fidelity

The primary 1-km patch-fidelity relationship is positive on average but misses the frozen criterion (p=0.05731). The 500-m and 2-km sensitivities also do not pass.

Thus a simple universal pathway

`persistent horizontal patch fidelity -> stronger vertical individuality`

is not established.

### Temporal-phase attribution

The support-matched *P. hastatus* 2023 phase-attribution test fails (p=0.3774).

The wet-season / temporal-allocation interpretation remains hypothesis-generating only.

### Individual uplift reaction norm

The archived *Tadarida* uplift-reaction endpoint has only two structurally evaluable repeat individuals and fails (p=0.3337).

A universal individually repeatable response to modeled vertical wind is therefore not established.

---

## 4. Nyctalus external evidence — corrected chronology

All *Nyctalus* analyses use the same source:

- Zenodo DOI `10.5281/zenodo.7535030`
- `Observed_GPS_locations.csv`
- SHA256 `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9`

The complete chronology is recorded in `NYCTALUS_VALIDATION_HISTORY_V1.md`.

### 4.1 Authoritative prospective primary test

The first frozen external protocol required >=50 presence-qualified fixes per retained source track.

Result:
- n = **27**
- calibrated excess = **+0.051747**
- p = **0.1224**
- frozen verdict = **FAIL**

The effect direction agrees with the original comparative result, but the preregistered inferential threshold is not met.

Therefore:

> **A successful prospective external replication is not established.**

### 4.2 Later revised-eligibility result

A later analysis on the same source omitted the previous >=50-fixes-per-track filter while retaining >=50 scored common-support target events.

Result:
- n = **36**
- calibrated excess = **+0.086005**
- p = **0.0115**

Because the same source Height response had already been opened in the first validation, this result is **post-outcome sensitivity evidence**, not a second prospective primary test.

### 4.3 Eligibility robustness

A subsequently frozen diagnostic varied only the minimum source-track length:

| minimum fixes/track | n | calibrated excess | p |
|---:|---:|---:|---:|
| 0 | 36 | +0.08600 | 0.0115 |
| 20 | 36 | +0.06423 | 0.0370 |
| 30 | 34 | +0.06777 | 0.0323 |
| 40 | 31 | +0.06028 | 0.0676 |
| 50 | 27 | +0.05175 | 0.1224 |
| 75 | 16 | +0.03390 | 0.2649 |
| 100 | 5 | +0.06086 | 0.1559 |

Calibrated excess is positive at **7/7** thresholds, with range +0.03390 to +0.08600 and median +0.06086.

The correct interpretation is:

> **Nyctalus provides directionally robust convergent external evidence: the estimated calibrated effect stays positive across the entire frozen session-length sensitivity curve. However, the first prospective primary test remains non-significant and governs the confirmatory replication verdict.**

The sensitivity curve shows that the later positive result is not created by a sign reversal at one relaxed eligibility cutoff. It does not convert the source into a successful prospective replication.

### 4.4 Source-HMM state analysis

The later 5-km × source HMM-state analysis gives:
- n = **27**
- calibrated excess = **+0.05074**
- p = **0.0707**

Because it was opened after the first primary external failure and under a later analysis family on the same source, it is classified as **post-outcome exploratory mechanism evidence**.

It neither establishes nor refutes a universal within-state mechanism.

The 500-m × HMM-state and >=1-day × HMM-state families lacked structural support and were not opened.

---

## 5. What currently generalizes

### Strongest established result

> **Repeatable vertical individual organization is supported across multiple bat tracking systems after coarse horizontal occupancy is standardized; in the five original comparative panels, it persists in centered distribution shape.**

### External generality

The independent *Nyctalus* source is **directionally concordant**, and its calibrated effect is positive across all tested session-length eligibility thresholds.

What is not yet established is a successful independent confirmatory replication outside the original source universe.

Therefore do not state that centered shape “now spans four taxa with prospective independent support.”

---

## 6. Current causal interpretation

The archive narrows the causal space but does not identify one universal mechanism.

### Explanations substantially weakened in the original archive

- coarse horizontal occupancy;
- additive absolute-altitude/tag offset as a general explanation;
- broad speed-state allocation;
- broad speed × turning allocation;
- >=250–500-m route/patch allocation in evaluable systems;
- simple body mass;
- relative tag burden;
- simple horizontal patch-fidelity strength;
- broad shared calendar-night context.

### Live explanations

1. **sub-250–500-m resource/route/microhabitat allocation**
   - exact feeding trees or patches;
   - narrow corridors;
   - canopy gaps;
   - microtopography;

2. **unmeasured stable morphology**
   - wing loading;
   - aspect ratio;
   - other flight morphology;

3. **learned routines / memory / experience**

4. **individual environmental reaction norms**
   - local wind;
   - uplift;
   - boundary-layer structure;
   - fine temperature/pressure exposure;

5. **behavioural allocation under independently observed states**
   - the original archive lacks a harmonized direct behavioural-state label.

These mechanisms may coexist and may differ among taxa or ecological contexts.

---

## 7. Next decisive evidence

### External generality

A successful prospective external replication requires a source whose vertical response has not previously been opened under the new programme.

The pre-existing outcome-blind external-candidate ledger contains candidate sources that were identified before the Nyctalus result. A new validation must:
1. freeze source admission and structural eligibility;
2. preserve negative results;
3. freeze the complete estimator before any numeric vertical response is opened;
4. not retune thresholds after outcome.

### Mechanism

The archive is support-limited below ~250–500 m. Decisive field data should deliberately create cross-individual overlap within:

`exact route/resource × independent behavioural state × local environment × time window`

and measure wing morphology plus synchronized local atmospheric conditions.

Only then can fine resource allocation be separated cleanly from within-context individual flight organization.

---

## Final position

The corrected programme supports three distinct statements:

1. **Established:** bats in multiple original systems retain repeatable individual vertical organization beyond coarse horizontal occupancy; five comparative panels retain centered-shape identity.
2. **Strong exploratory localization:** in evaluable original systems that individuality survives broad kinematic matching, 250–500-m place matching and multi-day separation.
3. **External convergence but not confirmation:** *Nyctalus* shows a positive calibrated effect across all seven eligibility thresholds, but the original prospective external test did not pass its frozen inferential criterion.

This hierarchy preserves all numerical evidence while keeping confirmatory and post-outcome evidence distinct.
