# batter

Ecological analysis of how persistent individual vertical strategies are maintained in three-dimensional bat airspace without necessarily partitioning it into exclusive vertical niches.

## Biological question

Do bats carry persistent individual **solutions to recurring three-dimensional movement problems**, and does maintaining those solutions require ongoing spatial partitioning?

The paper distinguishes the **origin of individual specialization** from its **maintenance**. Processes such as competition or ecological opportunity may generate individual differences, while repeated expression can persist for other reasons—experience, stable flight performance, fine resource knowledge or environmental response rules.

## Core result

Across six tracking panels from four bat taxa, same-individual vertical profiles retain more held-out predictive information than expected under whole-session identity exchangeability after coarse horizontal occupancy is standardized. Five comparative panels also retain centered vertical-distribution shape identity after session-median centering removes additive altitude level.

The post-freeze maintenance synthesis adds a second layer:

- terrain-relative vertical-strategy fidelity persists in **4/4** structurally evaluable fruit-bat panels at 500 m;
- **0/4** supports positive terrain-relative added segregation;
- synchronous local co-use adds vertical separation in only **1/4** panels;
- self-history remains predictive at >=1 day in **4/4**, >=3 days in **3/3**, and >=7 days in **2/2** structurally evaluable panels;
- individuality survives **500-m place × speed × turning** matching in **4/4** evaluable fruit-bat panels;
- under 2-km place × kinematic matching, self-history outpredicts same-night conspecifics in **3/4** panels, with 2016 unresolved at its frozen threshold.

Therefore the current ecological conclusion is:

> **Persistent individual vertical strategies need not partition three-dimensional space into mutually exclusive niches.**

A bounded mechanistic synthesis is **personal solution reuse**: an individual's previous movement solution can remain predictive across bouts even when conspecific strategies overlap. This is not direct evidence that memory or learning is the cause.

The motivating *Tadarida* panel remains the explicit boundary case: it retains repeatable absolute vertical-location identity but not centered-shape identity.

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

## What may maintain the persistent strategies

The current evidence rules out several simple general explanations: immediate carryover, coarse patch use, broad kinematic-state composition, common nightly context and ongoing vertical avoidance are each insufficient on their own.

The proximate carrier of persistence remains unresolved. Viable classes are:

- **information reuse / experience** — previously learned routes, approach geometries or search solutions;
- **stable performance matching** — morphology, wing loading or other persistent individual constraints;
- **sub-500-m task/resource fidelity** — trees, canopy gaps, prey layers, corridors or social destinations inside the present spatial matching scale;
- **fine environmental reaction norms** — individual-specific responses to airflow or microclimate.

A predeclared ERA5-wind reaction-norm family stopped before any numeric vertical outcome was opened because *P. hastatus* 2023 retained 7 evaluable individuals against 8 required. It is therefore **unadjudicated**, not a negative reaction-norm result.

The decisive future question is: **what information must travel with an individual for its previous vertical solution to remain predictive?**

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

Current scientific manuscript:
`manuscript/MANUSCRIPT_DRAFT_V0_3_8.md`

Current title:

> **Persistent individual vertical strategies need not partition three-dimensional space in bats**

Frozen release candidate:
`release/jae-v0.4.0-rc1`

Authoritative validation:
- JAE submission gate run **37092713865** — PASS;
- CI manuscript count **8,039 / 8,500** before title-page metadata;
- anonymous review run **37092621932** — PASS;
- anonymity guard PASS;
- review PDF **27 pages**;
- final Figure 1 and representative PDF pages visually inspected.

Synthetic metadata pipeline run **37093159799** also passes end-to-end:
- pre-release combined manuscript + generated title page **8,216 / 8,500**;
- post-DOI combined count **8,211 / 8,500**;
- final synthetic upload gate READY.

No final tag or GitHub Release has been created. Remaining work is explicit human metadata, software licence, release date, Zenodo version DOI and final upload.

## Claim boundary

Supported:
- repeatable centered vertical-distribution identity in the five comparative panels;
- terrain-relative personal vertical-strategy fidelity in 4/4 structurally evaluable fruit-bat panels;
- persistence across the longest structurally evaluable temporal lags;
- persistence after fine place × broad kinematic matching;
- empirical separation of persistent individual specialization from strong contemporaneous spatial partitioning.

Not established:
- memory or learning as the cause;
- adaptive benefit or optimality;
- morphology / wing loading as the cause;
- exact resource or task identity;
- fine environmental reaction norms;
- absence of historical competition;
- complete removal of sub-500-m horizontal or central-place structure.

Scientific stop rule: **no further same-data mechanism fishing is authorized for v0.4.0.**
