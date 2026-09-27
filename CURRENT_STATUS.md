# Current scientific status

Date: 2026-09-27

## Empirical programme

The public-data source universe remains frozen after the outcome-blind bat search. No new source
mining, lowered admission gates, retuned grids/bins, or rescue of negative endpoints is allowed.

A post-freeze estimator audit has now changed the **paper-level interpretation**, not the frozen
historical endpoints.

## What survives robustly

### Repeatable vertical individual identity

The focal *Tadarida teniotis* early/late identity-assignment test remains strongly positive:

- diagonal gain +0.1682;
- exact 8! permutation p=0.000174;
- 6/8 positive.

The stronger focal residual cell × height stability test remains negative:

- residual gain +0.0240;
- p=0.160;
- 5/8 positive.

Thus repeatable individual identity is supported, but one fixed individual-specific cell × height
map is not.

## Estimator calibration

The session-level architecture scores were audited because finite conditional estimates plus
Jeffreys smoothing can shift the exchangeability expectation of G_adv away from zero, and because
ordinary marginal height can inherit horizontal cell-use differences.

The audit used whole-session label permutations preserving within-session x-y-z structure and
exact session-count vectors.

### Focal Tadarida

At 5 km MSL:

- ordinary conditional = +0.428;
- ordinary marginal = +0.052;
- ordinary G_adv = +0.376;
- permutation-null mean G_adv = **-0.317**.

After common horizontal cell-use weighting:

- common-cell marginal = **+0.379**;
- raw common-cell advantage = **+0.049**;
- bootstrap 95% CI for raw common-cell advantage = -0.042 to +0.203;
- permutation-null mean common-cell advantage = -0.233;
- calibrated common-cell advantage = +0.282;
- permutation tail p=0.0127.

Conclusion: strong repeatable vertical identity survives, but the old statement that focal
identity is “primarily conditional on place” is not robust.

## Cross-panel calibration

| Panel | n | Old G_adv | Common-cell marginal | Common-cell advantage | Calibrated common-cell advantage | P(null >= obs) |
|---|---:|---:|---:|---:|---:|---:|
| *Tadarida* | 6 | +0.376 | +0.379 | +0.049 | +0.282 | 0.0127 |
| *Eidolon* | 20 | +0.217 | +0.177 | +0.042 | +0.081 | 0.0060 |
| *Hypsignathus* | 24 | +0.050 | +0.022 | +0.007 | +0.042 | 0.0002 |
| *P. hastatus* 2022 | 33 | -0.120 | +0.049 | +0.0066 | +0.066 | 0.0002 |
| *P. hastatus* 2023 | 16 | +0.020 | +0.033 | +0.0008 | +0.040 | 0.0144 |
| *P. hastatus* 2016 | 10 | +0.041 | -0.0039 | +0.061 | +0.222 | 0.0036 |

The old marginal-dominant *P. hastatus* 2022 result disappears after common-cell weighting.

Therefore the previous “multiple predictive architectures” synthesis is superseded.

## New paper-level synthesis

> **Across six tracking panels from four bat taxa, vertical airspace use contains repeatable
> individual identity that persists after horizontal space-use differences are standardized.**

This directly rejects a simple horizontal-fidelity explanation for the vertical individuality
signal.

A secondary result is that retaining horizontal cell identity adds only a small raw increment,
although that increment is consistently larger than the negatively shifted exchangeability null
of the estimator.

## Focal residual-confound robustness

The remaining focal confounds were frozen before output in
`contract/tadarida_residual_confounds_v1.json`.

### Terrain-relative AGL calibration

PASS at 5 km:

- common-cell AGL marginal identity +0.266;
- permutation-null mean -0.180;
- calibrated difference +0.446;
- permutation p=0.0161;
- n=6.

Thus the focal vertical-identity signal is not restricted to MSL altitude.

### Night-endpoint / roost-proxy exclusion

FAIL under the predeclared 1-km primary rule:

- 602 events removed;
- common-cell AGL marginal +0.099;
- calibrated difference +0.279;
- p=0.1109;
- n=6.

The fixed 500-m and 2,000-m sensitivities also fail (p=0.0978 and 0.1446).

The endpoint proxy is not a verified biological roost. The inference is therefore that
departure/arrival or central-place spatial structure remains a viable contributor; it is not
evidence that a specific roost mechanism is proven.

### Horizontal grain

- 2.5 km: PASS; common-cell AGL marginal +0.603, calibrated +0.712, p=0.011, n=5.
- 10 km: FAIL; common-cell AGL marginal -0.013, calibrated +0.237, p=0.1018, n=7.

The focal terrain-relative result is therefore supported at 2.5–5 km but not established at
10 km.

### Focal claim ceiling

Allowed:

> European free-tailed bats show repeatable terrain-relative vertical identity after horizontal
> cell-use standardization at fine-to-intermediate horizontal grain (2.5–5 km).

Required qualifications:

- central-place departure/arrival structure remains a possible contributor;
- broad 2.5–10-km grain invariance is not supported;
- the stronger stable residual cell × height map remains unsupported (p=0.160).

## Biological effect translation

The calibrated log-score results were translated into descriptive biological-scale quantities
under definitions frozen before output.

### Pairwise self-identification after horizontal standardization

Equal-individual self-win fractions:

- *Tadarida teniotis*: **79.4%** (individual-bootstrap 95% 65.6–93.1%);
- *Eidolon helvum*: **85.8%** (73.2–96.1%);
- *Hypsignathus monstrosus*: **76.7%** (69.9–83.3%);
- *Phyllostomus hastatus* 2022: **84.2%** (80.0–88.3%);
- *P. hastatus* 2023: **78.2%** (65.9–86.5%);
- *P. hastatus* 2016: 59.4% (49.5–70.4%).

Thus five panels show a descriptive self-identification rate around 77–86% after candidate
vertical profiles are placed under identical horizontal cell-use weights.

### Focal metre-scale translation

For *Tadarida* AGL at 5 km, the same-bat and other-bat profiles differ in common-cell-weighted
expected mean height above ground by:

- equal-individual mean absolute separation: **256 m**;
- median individual separation: **145 m**;
- bootstrap 95%: **70–466 m**.

This is heterogeneous among individuals and is not a universal fixed height offset.

### Reporting preference

Use pairwise self-identification and the focal metre-scale effect for biological interpretation.

Retain nats/fix for exact statistical reporting. Entropy-normalized calibrated gains are
Supporting Information only because the ratio is not mutual information, is not variance
explained and can exceed one.

## Submission status

**JAE v0.3.3 rc2 is on scientific hold and must not be submitted.**

The next manuscript version should be rebuilt around:

1. repeatable vertical identity;
2. horizontal-standardization control;
3. estimator-calibrated inference;
4. explicit focal residual-map negative;
5. no qualitative conditional/marginal architecture classes.

## Claim boundary

Allowed:

- repeatable vertical individual identity;
- individual non-exchangeability;
- vertical identity beyond horizontal space-use weighting;
- estimator-calibrated additional conditional information.

Not established:

- conditional-dominant versus marginal-dominant biological classes;
- stable individual-specific place × height maps;
- personality, learning, adaptation or optimality;
- verified foraging specialization;
- one universal causal mechanism.
