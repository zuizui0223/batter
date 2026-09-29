# Mechanism synthesis v1 — what generates repeatable vertical organization?

## Scope

This file summarizes **post-freeze exploratory mechanism work**. It does not modify the frozen JAE v0.3.8 submission package.

## Starting empirical rule

Across the five comparative panels, individual identity predicts the centered vertical-distribution shape after:
- coarse 5-km horizontal occupancy is standardized; and
- session-specific absolute altitude level is removed.

The mechanistic question is therefore why individuals remain non-exchangeable in how vertical-use probability is organized around their typical session altitude.

## Hypothesis tree and tests

### 1. Simple persistent fine-scale patch fidelity as the general driver

Prediction: individuals with stronger x-y-only fine-scale patch-fidelity excess should show stronger individually null-calibrated centered vertical identity.

Frozen test:
- 1-km movement-patch proxy;
- equal-panel mean Spearman rho = **+0.1759**;
- one-sided stratified permutation p = **0.05731**;
- positive association in 4/5 panels;
- *Eidolon* rho = **-0.5218**;
- verdict: **FAIL**.

Conclusion: a simple universal pathway
`persistent horizontal patch fidelity -> stronger vertical individuality`
is not supported.

This does not exclude resource-linked behaviour, because resource use can change behavioural allocation without producing fidelity to the same x-y patch.

### 2. Broad behavioural-mixture individuality

Hypothesis: whole-session vertical identity is generated mainly because individuals spend different fractions of time in broad movement-intensity states.

Outcome-blind preflight selected three cohort-relative horizontal-speed states using steps <=1,800 s.

Frozen state-conditioned test then forced self and other profiles to use the same **5-km cell × movement-state weights**.

Result: **5/5 comparative panels PASS**.

| panel | n | calibrated excess | p |
|---|---:|---:|---:|
| *Eidolon* | 14 | +0.316 | 0.0002 |
| *Hypsignathus* | 24 | +0.135 | 0.0002 |
| *P. hastatus* 2022 | 33 | +0.128 | 0.0002 |
| *P. hastatus* 2023 | 14 | +0.060 | 0.0002 |
| *P. hastatus* 2016 | 10 | +0.547 | 0.0076 |

Conclusion: **broad movement-state mixture alone is insufficient as a general explanation**. Vertical individuality persists within this x-y-time movement-intensity proxy.

Descriptively, state conditioning reduced calibrated excess in *Eidolon*, *Hypsignathus* and *P. hastatus* 2023, changed little in 2016, and increased it slightly in 2022. This suggests that movement-state composition may contribute in some systems, but is not sufficient to generate the comparative pattern.

### 3. Fine-scale route/habitat allocation versus within-route flight organization

Next prediction: if the remaining within-state individuality is generated only by different fine-scale routes or patches, it should weaken after matching place more finely than 5 km.

An x-y-time-only support preflight tested 500 m, 1 km, 2 km and 2.5 km cells while keeping the three-state movement definition fixed.

No candidate met the frozen all-panel support gate because *Eidolon* collapsed to only 2–4 evaluable individuals.

Per the stop rule, **no vertical fine-route result was opened**.

Conclusion: the present datasets cannot distinguish fine-scale route/habitat allocation from within-route flight organization across the full comparative set.

## What has been ruled down

The current evidence makes the following simple explanations increasingly inadequate:

- different occupancy among coarse 5-km cells;
- additive absolute-altitude/tag zero-point differences in the five comparative panels;
- only different proportions of broad horizontal movement-intensity states;
- a universal monotonic link between fine-scale x-y patch fidelity and vertical individuality.

For focal *Tadarida*, a separate same-night control also showed that another night from the same individual generally outpredicted other bats observed on the same night, weakening the simplest shared-night-environment explanation for its absolute vertical signature. *Tadarida* remains a boundary case because centered-shape identity itself is unsupported there.

## Live ecological hypotheses

The remaining mechanisms are narrower and biologically sharper:

1. **context-dependent resource/social allocation**  
   Individuals may use different resource types, social sites or route classes without repeatedly occupying the same fine x-y patches. This could organize vertical use within the same broad speed state.

2. **fine-scale route/habitat specialization**  
   Individuals may repeatedly select different routes, canopy/terrain contexts or local vertical opportunities inside the same 5-km cell and movement-intensity state.

3. **within-route flight phenotype**  
   Morphology, body condition, experience, memory, learned route geometry or individual environmental reaction norms may produce different vertical organization even under closely matched place and behavioural state.

## Strongest new ecological statement from the exploratory work

> **Individual bats can retain repeatable vertical organization within the same broad horizontal movement-intensity state; the comparative pattern is therefore not reducible to coarse place use or to a simple mixture of fast versus slow movement states.**

This statement is stronger mechanistically than the submission result, but remains post-freeze exploratory and should not be inserted into v0.3.8 before submission.

## Decisive next data design

The clean next experiment requires:
- repeated tracking of the same individuals;
- high-frequency 3-D positions;
- independently validated behavioural states;
- fine-scale route matching;
- terrain/canopy and atmospheric covariates measured simultaneously;
- tag swapping or common calibration;
- morphology/body-condition covariates where possible.

The decisive contrast is then:
`identity within behavioural state + fine route + environmental opportunity`.

Persistence at that level would support a genuinely individual flight phenotype; disappearance would identify the ecological context that generates the observed vertical organization.
