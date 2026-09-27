# batter

Ecological analysis of repeatable individual identity in three-dimensional bat airspace.

## Biological question

Do individual bats carry repeatable information about **vertical airspace use** across sessions,
and does that information persist after differences in horizontal space use are standardized?

The project began from an ODSP result in *Tadarida teniotis*: the population retained substantial
vertical thickness after x-y was known, but a pooled location-conditioned vertical distribution
did not transfer to sealed individuals.

## Core result

Across six tracking panels from four bat taxa, the same individual's vertical use is more
predictable than expected under whole-session identity exchangeability.

Crucially, this remains true after self and other vertical profiles are integrated under the
**same horizontal cell-use weights**.

Therefore the main ecological conclusion is:

> **Repeatable individual vertical identity in bat airspace persists after self and other
> profiles are standardized to the same occupancy among the tested coarse 5-km horizontal cells.
> It therefore cannot be reduced to occupancy differences among those cells alone, although
> endpoint/central-place-associated structure remains a panel-dependent contributor.**

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

## Submission status

The v0.3.4 rc3 package is retained as the pre-audit baseline and must not be submitted as the final
scientific version.

The current manuscript is `manuscript/MANUSCRIPT_DRAFT_V0_3_5.md`, titled **“Repeatable vertical
identity in bat airspace persists after coarse horizontal occupancy is standardized.”** The
v0.3.5 manuscript/figure and anonymous-review workflows have passed on the diagnostic branch and
are revalidated on main before the release candidate is frozen.

## Claim boundary

The analyses concern vertical flight/airspace use and predictive individual identity. Common-cell
weighting removes occupancy differences among the tested horizontal cells, not all fine-scale
horizontal fidelity. The analyses do not by themselves establish independence from central-place
structure, foraging, personality, learning, optimality, stable learned routes or a universal
causal environmental mechanism.
