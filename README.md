# batter

Ecological analysis of repeatable individual shapes of vertical space use in three-dimensional bat airspace.

## Biological question

Do bat populations contain repeatable **individual-specific organizations of vertical space use**—
that is, different probability distributions around their session-specific typical altitude—and do
those differences persist after coarse horizontal occupancy and additive altitude level are controlled?

The project began from an ODSP result in *Tadarida teniotis*, but the current paper is comparative:
the strongest ecological result comes from five non-*Tadarida* panels that retain centered
vertical-distribution shape identity.

## Core result

Across six tracking panels from four bat taxa, same-individual vertical profiles retain more
held-out predictive information than expected under whole-session identity exchangeability after
self and other profiles are integrated under the **same 5-km horizontal cell-use weights**.

More importantly, all five comparative panels retain vertical-distribution shape identity after
every session is translated to zero median, removing any additive constant altitude offset.

The descriptive reconstruction of those already-tested profiles visually illustrates candidate
dimensions of shape heterogeneity: estimated profiles vary in **central concentration and
upper/lower tail use** around their session-specific median altitude. Those component-wise ranges
were not separately null-calibrated and may include finite-session profile-estimation noise; the
inferential result applies to the full centered distribution shape.

Therefore the main ecological conclusion is:

> **Bat populations can contain repeatable individual shapes of vertical space use that persist
> beyond coarse horizontal occupancy and additive altitude zero point.**

The motivating *Tadarida* panel is the explicit boundary case: it retains repeatable absolute
vertical-location identity but not centered-shape identity.

## What the shape individuality looks like

The final descriptive Figure 6 is frozen as a visualization-only layer. It reconstructs the exact
leave-one-session-out common-cell self profiles used by the centered-shape estimator and averages
them equally within biological individual.

Across the five comparative panels, the displayed profile estimates vary visibly in:
- central mass around -50 to +50 m;
- upper-tail use at >=100 m;
- lower-tail use at <=-100 m;
- tail asymmetry.

These component summaries are descriptive only. They were not calibrated against exchangeability,
so the figure does not identify which component carries the validated whole-profile identity
signal. No cluster, strategy class, behavioural state or additional p-value is inferred.

See `CENTERED_SHAPE_PROFILE_DESCRIPTIVE_RESULT_V1.md`.

## What could generate the repeatable shapes

The calibrated result is distribution-level: individual identity predicts how vertical-use probability
is organized around the session median. Two non-exclusive mechanisms could generate that result:

- **behavioural-mixture individuality** — individuals repeatedly allocate different fractions of a
  night to commuting, feeding-patch use, social-site visits or other behavioural states;
- **within-state individuality** — individuals differ in vertical movement even within the same
  behavioural state because of morphology, route memory, experience, resource choice or atmospheric
  response.

The present public datasets do not contain a harmonized behavioural-state classifier, so these are
prospective mechanisms, not inferred causes. A decisive next test is whether identity disappears or
persists after conditioning on independently classified behavioural state.

## Why the claim changed

Earlier versions of this repository classified panels as “conditional-dominant” or
“marginal-dominant” using the raw sign of

`G_adv = G_cond - G_marg`.

A post-freeze diagnostic calibration showed that this classifier was not valid:

- the exchangeability null of G_adv is negative and panel-specific;
- ordinary marginal identity is sensitive to horizontal cell-use weighting;
- the apparent marginal-dominant *Phyllostomus hastatus* 2022 panel changes from
  G_adv = -0.120 to a common-cell advantage of +0.0066.

The old multiple-architecture synthesis is therefore superseded.

## Calibrated 5-km result

| Panel | Common-cell marginal | Raw common-cell advantage | Calibrated advantage | Permutation p |
|---|---:|---:|---:|---:|
| *Tadarida teniotis* | +0.379 | +0.049 | +0.282 | 0.0127 |
| *Eidolon helvum* | +0.177 | +0.042 | +0.081 | 0.0060 |
| *Hypsignathus monstrosus* | +0.022 | +0.007 | +0.042 | 0.0002 |
| *Phyllostomus hastatus* 2022 | +0.049 | +0.0066 | +0.066 | 0.0002 |
| *P. hastatus* 2023 | +0.033 | +0.0008 | +0.040 | 0.0144 |
| *P. hastatus* 2016 | -0.0039 | +0.061 | +0.222 | 0.0036 |

“Calibrated advantage” means observed common-cell advantage minus that panel's permutation-null
mean. It is an estimator-calibrated contrast, not an absolute biological effect size.

## Focal claim boundary

*Tadarida* still shows strong repeatable identity, but the stronger frozen residual-map test
remains negative:

- residual gain +0.0240;
- exact permutation p=0.160.

Thus the study does not establish one stable individual-specific cell × height route map.

## Public-data search

The source universe is closed. The original outcome-blind search covered 23 Movebank parent
datasets plus legacy child-handle recovery. Six sources from four taxa met the fixed same-event
x-y-height and repeat-tracking requirements.

No new source search belongs in the current paper programme.

## Key calibration files

- `TADARIDA_ESTIMATOR_CALIBRATION_CONTRACT.md`
- `TADARIDA_ESTIMATOR_CALIBRATION_RESULT.md`
- `CROSS_PANEL_ESTIMATOR_CALIBRATION_CONTRACT.md`
- `CROSS_PANEL_ESTIMATOR_CALIBRATION_RESULT.md`
- `PAPER_FREEZE_V0_3_4_CALIBRATION_AMENDMENT.md`
- `CROSS_PANEL_CONFOUND_AUDIT_FREEZE_V1.md`
- `CROSS_PANEL_CONFOUND_AUDIT_RESULT_V1.md`

## Cross-panel confound audit

The reviewer-facing v1 audit was frozen before output and is complete.

- 1-km endpoint-neighbourhood robustness: 4/5 comparative panels PASS; *Eidolon* fails only its
  frozen n gate, while focal *Tadarida* remains an inferential FAIL.
- calibrated pairwise self-identification: PASS in 5/6 panels; *P. hastatus* 2016 does not pass.
- focal raw AGL separation: 256.459 m; exchangeability null mean 133.733 m; calibrated excess
  122.727 m; p=0.0297.

See `CROSS_PANEL_CONFOUND_AUDIT_RESULT_V1.md`.

## Final tag-altitude-bias audit

The final predeclared scientific audit is complete.

- session-median centering: **5/6 panels PASS**;
- focal *Tadarida*: FAIL, calibrated excess -0.022, p=0.5121;
- stationary-height correction: **2/2 structurally eligible panels PASS** (both p=0.0002);
- timing overlap is weakest in *P. hastatus* 2016 and remains a limitation;
- no further new scientific analysis family is authorized before submission.

See `TAG_ALTITUDE_BIAS_AUDIT_RESULT.md`.

## Submission status

The v0.3.4 rc3 package is retained as the pre-audit baseline and must not be submitted as the final
scientific version.

The current manuscript is `manuscript/MANUSCRIPT_DRAFT_V0_3_8.md`, titled **“Repeatable individual shapes of vertical space use persist beyond coarse horizontal occupancy in bats.”** The v0.3.8
manuscript/figure and anonymous-review workflows pass with 7,953 words, a 282-word five-statement
abstract, six main figures plus two Supporting Figures, and a 27-page anonymous review PDF.

Current release packaging target: `release/jae-v0.3.8-rc1`.

## Claim boundary

The analyses concern vertical space use and repeatable individual distribution shape. Common-cell
weighting removes occupancy differences among the tested horizontal cells, not all fine-scale
horizontal fidelity. Session centering removes additive altitude level, not tag-specific error
variance or behavioural-state composition. The analyses do not establish which visual component of Figure 6 carries the calibrated
whole-profile identity signal, vertical-niche strategy classes, foraging specialization,
personality, learning, optimality, stable learned routes or a universal causal mechanism.
