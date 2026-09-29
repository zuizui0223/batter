# Post-freeze mechanism synthesis v4

## Scope

All analyses here are **post-freeze exploratory extensions**. The frozen v0.3.8 JAE submission on `main` is unchanged.

## Starting rule

Five comparative panels retain calibrated individual identity in the centered shape of vertical space use after coarse 5-km horizontal occupancy and additive altitude level are controlled.

The mechanism question is:

> **Why do individuals remain non-exchangeable in how vertical-use probability is organized around their typical altitude?**

## What is no longer a sufficient general explanation

### 1. Broad horizontal kinematic mixture

Speed-only conditioning: **5/5 panels retain identity**.

Speed × turning conditioning: **5/5 panels retain identity**:
- *Eidolon*: +0.335, p=0.0002
- *Hypsignathus*: +0.148, p=0.0002
- *P. hastatus* 2022: +0.110, p=0.0002
- *P. hastatus* 2023: +0.061, p=0.0002
- *P. hastatus* 2016: +0.526, p=0.0064

**Inference:** stable individual differences in the fraction of time spent in broad slow/fast and straight/tortuous movement modes are insufficient as a general explanation.

### 2. Horizontal route/patch allocation at >=2 km

A corrected x-y-time-only preflight reproduced the exact frozen speed×turn baseline counts and showed that *Eidolon* lacks enough cross-individual fine-place overlap. Four other panels are structurally evaluable at 2 km.

Those four panels all retain centered identity after simultaneous 2-km place × speed×turn matching:
- *Hypsignathus*: +0.286, p=0.0002
- *P. hastatus* 2022: +0.187, p=0.0002
- *P. hastatus* 2023: +0.072, p=0.0022
- *P. hastatus* 2016: +0.545, p=0.0120

**Inference:** 2-km route/patch allocation is insufficient in this subset.

### 3. Horizontal route/patch allocation at >=500 m

The same matched preflight had established 500-m support before any 500-m vertical outcome. The 500-m follow-up was opened after the positive 2-km result and is therefore a robustness stress test, not independent confirmation.

**4/4 structurally evaluable panels pass at 500 m**:
- *Hypsignathus*: +0.384, p=0.0002
- *P. hastatus* 2022: +0.0868, p=0.0002
- *P. hastatus* 2023: +0.1015, p=0.0006
- *P. hastatus* 2016: +0.451, p=0.0286

**Inference:** in these four panels, route/patch allocation at scales >=500 m plus broad speed×turning composition is insufficient.

The unresolved spatial mechanism is now pushed below 500 m: exact flight corridors, feeding trees, canopy gaps, local topographic exposure, microclimate and other fine resource/microhabitat differences remain possible.

### 4. Simple fine-patch fidelity strength

Frozen primary prediction:
- equal-panel mean Spearman rho = +0.176
- p=0.05731
- 4/5 panel associations positive
- primary verdict FAIL

**Inference:** stronger repeated use of the same fine horizontal patches is not supported as a general driver of stronger vertical individuality.

### 5. Relative biologger burden

Relative tag burden = tag mass / animal mass was tested against individually permutation-null-calibrated centered identity.

Cross-panel result:
- equal-panel mean |rho| = 0.268
- permutation p=0.1399
- primary verdict FAIL

Only 2022 showed an isolated association (rho=-0.401, p=0.0274), with inconsistent signs among panels.

**Inference:** simple monotonic payload burden is not a general technical explanation.

## Shared-night environmental context

A structurally frozen four-panel comparison asked whether the same individual's history remained more informative than **other bats tracked on the same shifted night**, while also matching 2-km horizontal place and speed×turn state.

Result:
- *Hypsignathus*: +0.302 calibrated excess, p=0.0002 — PASS
- *P. hastatus* 2022: +0.169, p=0.0002 — PASS
- *P. hastatus* 2023: +0.0822, p=0.0286 — PASS
- *P. hastatus* 2016: +0.564, p=0.0544 — FAIL

**3/4 panels PASS.**

The 2016 excess is large and positive but misses the frozen tail threshold, so it remains inferentially unresolved rather than counted as support.

**Inference:** broad calendar-night context is insufficient as a general explanation in the structurally evaluable subset. Exact local wind, uplift, temperature and microclimate remain unmeasured.

The same-night pipeline was independently reimplemented using cached session-level cell×z counts and reproduced all four panel statistics exactly.

The focal *Tadarida* result points in the same direction: another night from the same individual can outperform contemporaneous other bats. A common *Tadarida* uplift-response slope was also not supported (permutation p=0.334).

## Temporal allocation: apparent panel attenuation, but causal attribution FAILS

A pre-outcome x-y-time-only screen selected early/middle/late relative tracked-session phase for four structurally evaluable panels.

Panel-level phase conditioning:
- *Hypsignathus*: +0.156, p=0.0002 — PASS
- *P. hastatus* 2022: +0.0896, p=0.0002 — PASS
- *P. hastatus* 2023: +0.0221, p=0.1068 — FAIL
- *P. hastatus* 2016: +0.483, p=0.0214 — PASS

The 2023 wet-season panel was therefore initially suggestive of a temporal-allocation mechanism.

However, a support-matched attribution test was frozen **after** that observation to distinguish phase information from sparsity/support loss. Both the phase-conditioned and phase-collapsed predictors were scored on exactly the same phase-supported target endpoints.

2023 paired-support result:
- support-matched collapsed gain: -0.02482
- phase-conditioned gain: -0.07041
- paired phase increment: -0.04560
- null-centered increment: -0.00481
- one-sided p(null <= observed)=0.3774
- attribution verdict: FAIL

**Inference:** the 2023 phase3 attenuation is not established as a true temporal-phase mechanism. Reduced support, estimator variance and finite-sample effects remain viable explanations.

The dry-versus-wet season narrative is therefore **hypothesis-generating only**, not a supported mechanism.

A prospective 2021 wet-season validation was attempted outcome-blind, but the 2021 source contained only four individuals and two repeat individuals and failed the original frozen cohort admission gate. No 2021 vertical outcome was opened.

## Structural identifiability boundary: Eidolon

*Eidolon* repeatedly limits the strongest cross-individual mechanism tests:
- matched 500 m / 1 km / 2 km place × speed×turn: only 1/12 evaluable;
- five-panel same-night preflight: 8/12 where 9 required;
- temporal phase3: 4/12; phase2: 7/12;
- close/far body-mass transfer: 3 targets where 9 required;
- continuous body-mass gradient transfer: 1/12 where 9 required.

This is not solved by dropping *Eidolon* from the five-panel claim. Instead, *Eidolon* marks the archival identifiability boundary: strong vertical individuality coexists with sparse cross-individual fine-scale horizontal overlap.

## Current causal fork

For the four structurally evaluable non-*Eidolon* panels, the evidence now argues against:

`coarse place + broad movement mode + >=500-m route allocation + broad shared-night context`

as a sufficient explanation.

The strongest live mechanisms are:

1. **sub-500-m resource/route/microhabitat allocation** — exact feeding trees, local corridors, canopy gaps, topographic exposure or microclimate;
2. **within-context individual flight organization** — morphology/wing loading, experience, memory, learned routines, resource choice or stable individual response functions;
3. **fine-scale environmental reaction norms** — individual-specific responses to local wind/uplift/microclimate not captured by calendar-night matching.

Temporal-phase allocation remains a possible context-dependent contributor, but the current support-matched test does not establish it.

## Strongest current statements

Five-panel level:

> **Broad horizontal kinematic-state composition alone is insufficient to explain the comparative vertical-individuality pattern.**

Four-panel structurally evaluable subset:

> **Individual vertical organization persists after simultaneously matching horizontal place to 500 m and broad speed × turning state. In three of four panels it also remains stronger than contemporaneous other individuals on the same night under 2-km place × kinematic matching.**

These statements do not generalize to *Eidolon* for the fine-place/same-night mechanism tests.

## Claim ceiling

Not established:
- exact resource/feeding-tree causation;
- sub-500-m route causation;
- body mass or wing-loading causation;
- learning, memory or personality;
- season causation;
- temporal-phase causation in 2023;
- individual atmospheric reaction norms;
- any fine-place mechanism generalization from the four-panel subset to *Eidolon*.
