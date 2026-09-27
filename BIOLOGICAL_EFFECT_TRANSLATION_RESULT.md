# Biological effect translation v1 — result

Date: 2026-09-27

These are descriptive translations of the already-calibrated identity results. No new
significance gate was introduced.

## Pairwise self-identification

After integrating candidate vertical profiles under identical horizontal cell-use weights, the
same individual's profile outpredicted a specific alternative individual at the following rates:

| Panel | Pairwise self-win | Individual-bootstrap 95% |
|---|---:|---:|
| *Tadarida teniotis* | **79.4%** | 65.6–93.1% |
| *Eidolon helvum* | **85.8%** | 73.2–96.1% |
| *Hypsignathus monstrosus* | **76.7%** | 69.9–83.3% |
| *Phyllostomus hastatus* 2022 | **84.2%** | 80.0–88.3% |
| *P. hastatus* 2023 | **78.2%** | 65.9–86.5% |
| *P. hastatus* 2016 | 59.4% | 49.5–70.4% |

This is the clearest biological-scale translation of the cross-panel result.

Five of six panels show a point estimate near 77–86% and bootstrap intervals entirely above the
50% intuitive chance reference. The 2016 *Phyllostomus* panel is weaker and its interval includes
50%.

This remains descriptive; the inferential evidence is the separately frozen session-label
calibration.

## Likelihood scale

Observed common-cell marginal identity corresponds to these geometric per-fix self-versus-other
likelihood multipliers:

| Panel | Observed multiplier | Null-calibrated excess scale |
|---|---:|---:|
| *Tadarida* | 1.46× | 1.83× |
| *Eidolon* | 1.19× | 1.30× |
| *Hypsignathus* | 1.02× | 1.08× |
| *P. hastatus* 2022 | 1.05× | 1.22× |
| *P. hastatus* 2023 | 1.03× | 1.13× |
| *P. hastatus* 2016 | 1.00× | 1.31× |

The calibrated multiplier is a scale for the excess log score above the finite-sample null, not a
literal biological odds ratio.

## Relative to vertical-state entropy

The calibrated common-cell identity divided by target-session empirical vertical-bin entropy is:

- *Tadarida*: 1.14;
- *Eidolon*: 1.04;
- *Hypsignathus*: 0.60;
- *P. hastatus* 2022: 0.32;
- *P. hastatus* 2023: 0.10;
- *P. hastatus* 2016: 0.47.

Because this ratio can exceed one, it must **not** be called “percent entropy explained.” It is
only an entropy-equivalent normalization of the calibrated log-score contrast.

For the main manuscript, pairwise identification is more intuitive and less likely to be
misread.

## Focal metre-scale effect

For *Tadarida* AGL only, the same-bat and other-bat vertical profiles were integrated under the
same 5-km self cell-use weights and translated back to expected mean height above ground.

- equal-individual mean absolute separation: **256 m**;
- median individual separation: **145 m**;
- individual-bootstrap 95%: **70–466 m**;
- 12 evaluable target sessions.

The individual values are heterogeneous, so 256 m should not be described as a universal
individual offset. It shows that the distributional identity detected in log-score space can
correspond to biologically substantial vertical separation in the focal system.

## Manuscript use

Recommended main-text translations:

> After horizontal cell use was standardized, the same bat's vertical profile outpredicted a
> particular alternative bat in roughly 77–86% of pairwise comparisons in five of six panels.

and, for the focal species:

> In terrain-relative coordinates, same- versus other-individual profiles differed in expected
> mean flight height by about 256 m on average, although the magnitude varied strongly among bats.

Keep the entropy-equivalent ratio in Supporting Information and retain nats/fix for exact
statistical reporting.
