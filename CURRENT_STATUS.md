# Current scientific status

Date: 2026-10-03

## Current v0.4.0 submission state

The active candidate is **v0.4.0**, titled:

> **Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species**

Frozen release candidate:
`release/jae-v0.4.0-rc2`

Current synthesis:
- centered vertical-distribution identity persists in all five comparative panels;
- terrain-relative personal strategy fidelity persists in 4/4 evaluable *H. monstrosus*/*P. hastatus* panels;
- positive terrain-relative added segregation is supported in 0/4;
- synchronous local co-use separation is supported in 1/4;
- self-history remains predictive across the longest structurally evaluable multi-day lags;
- individuality survives 500-m place × speed × turning matching in 4/4 evaluable *H. monstrosus*/*P. hastatus* panels;
- same-individual history generally outpredicts same-night conspecifics after 2-km place × kinematic matching.

Previously frozen external boundary tests also constrain generality: *Nyctalus*, *Hipposideros* and *M. vivesi* failed their frozen primaries, whereas *Pteropus* passed under a separate n=4 programme and was strongly terrain-sensitive. These tests are boundary evidence, not a prevalence sample. The `need not partition` inference is based on four terrain/co-use panels from **two species**, *H. monstrosus* and *P. hastatus*.

Preferred ecological interpretation:

> **Persistent personal movement solutions can remain predictive without requiring mutually exclusive vertical niches.**

This separates the **origin of individual specialization** from the **maintenance of specialization**. Personal solution reuse is a bounded synthesis, not direct evidence that memory or learning is the cause.

The continuous ERA5-wind reaction-norm family was stopped **before numeric vertical opening** when the all-three structural gate failed (*P. hastatus* 2023: 7 evaluable vs 8 required). No threshold relaxation, reduced-panel rescue or alternate weather-variable rescue is authorized.

Validation:
- submission workflow **37123936286** — PASS;
- CI manuscript count **7,995 / 8,500**;
- anonymous review workflow **37123738669** — PASS;
- review PDF **27 pages**;
- synthetic metadata pipeline **37123738694** — PASS;
- synthetic pre-release combined count **8,175 / 8,500**;
- synthetic post-DOI combined count **8,170 / 8,500**.

Remaining blockers are non-scientific: explicit human author/declaration metadata, software licence, release date, Zenodo version DOI and journal upload.

**Scientific stop rule:** no further same-data mechanism fishing is authorized for v0.4.0.

The sections below are retained as historical provenance and may describe superseded v0.3.x states.

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

> **Across six tracking panels from four bat taxa, identity-matched vertical profiles retain more
> held-out predictive information than expected under session-level exchangeability after self
> and other profiles are standardized to the same occupancy among the tested 5-km horizontal
> cells.**

This rejects the explanation that the cross-panel vertical signal is only a consequence of
different occupancy among those coarse cells. It does not remove fine-scale within-cell horizontal
or central-place structure.

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

Use calibrated pairwise self-identification for biological interpretation. The focal 256-m
metre-scale value is descriptive only after the tag-bias audit because *Tadarida* does not retain
identity after session-centering.

Retain nats/fix for exact statistical reporting. Entropy-normalized calibrated gains are
Supporting Information only because the ratio is not mutual information, is not variance
explained and can exceed one.

## Cross-panel confound audit v1

The rc3 package was placed on scientific hold before two additional result families were opened.
Both families were frozen before output and are now complete.

### Endpoint-neighbourhood exclusion

At the predeclared 1-km radius, four of five comparative panels pass. *Eidolon* retains a strong
calibrated excess (+0.390; p=0.0002) but fails because n=11 is below the frozen minimum 15.
The earlier focal *Tadarida* result remains FAIL (p=0.1109).

Across the six paper panels, the endpoint audit therefore passes in 4/6, fails inferentially in
*Tadarida*, and fails by sample-size gate in *Eidolon*. Central-place/end-point structure is not a
general explanation, but it is not universally excluded.

### Effect-translation null calibration

Pairwise self-identification exceeds its own whole-session exchangeability null in five panels:
*Tadarida* p=0.0189 and *Eidolon*, *Hypsignathus*, *P. hastatus* 2022 and 2023 p=0.0002.
*P. hastatus* 2016 does not pass (p=0.1168).

The focal AGL raw mean absolute separation of 256.459 m has a non-zero null mean of 133.733 m.
The calibrated excess is 122.727 m, p=0.0297, so the metre-scale translation survives when
reported against its correct baseline.

### Scientific revision

The audit is incorporated in `manuscript/MANUSCRIPT_DRAFT_V0_3_5.md`.

Working title:

> **Repeatable vertical identity in bat airspace persists after coarse horizontal occupancy is
> standardized**

v0.3.4 rc3 remains the immutable pre-audit packaging baseline. At that historical stage, v0.3.5
was the scientific candidate; it has since been superseded by the current v0.3.6 package.

### Submission-readiness consequence

The v0.3.5 manuscript/figure gate passed (7,047 words; 271-word abstract; Figures 1–6 generated),
the double-anonymous review gate passed, and the 24-page review PDF plus all six figures were
visually inspected. A Figure 6 verdict-label overlap found during visual QA was corrected and
re-inspected.

The scientific hold created for the cross-panel confound audit is therefore resolved. Remaining
blockers are non-scientific: software licensing, final author/declaration metadata, archival DOI
and journal upload.

## Final tag altitude-bias audit v1

The v0.3.5 package entered one final, predeclared audit for additive tag/device altitude offsets.

### Primary shift-invariant result

Every retained session was translated to zero median before vertical binning, removing any
additive constant tag offset exactly and also removing session-specific constant altitude shifts.

**Five of six panels pass** their frozen calibrated shape-identity rule:

- *Eidolon*: calibrated excess +0.443, p=0.0002;
- *Hypsignathus*: +0.177, p=0.0002;
- *P. hastatus* 2022: +0.111, p=0.0002;
- *P. hastatus* 2023: +0.118, p=0.0002;
- *P. hastatus* 2016: +0.574, p=0.0076;
- focal *Tadarida*: -0.022, p=0.5121 — **FAIL**.

Under the predeclared decision matrix this is the **5/6 PASS** category.

Therefore a constant additive tag/device altitude offset is not a general explanation for the
cross-panel result. Five panels retain individual identity in vertical-distribution shape after
absolute altitude level is removed.

Focal *Tadarida* is the required exception. Its evidence does not survive session centering, so
its absolute vertical-location component may contain genuine mean-height specialization, additive
device offset, or both. This does not prove tag bias because centering removes both possibilities.

The focal raw 256-m AGL translation is consequently demoted from headline biological evidence.

### Stationary-height correction

The x-y/time-only preflight opened no numeric height values and permitted stationary correction
only for two panels.

- *Hypsignathus*: 12 offset-estimated individuals, 10 evaluable after correction, median absolute
  offset 4.64 m; calibrated excess +0.0671, p=0.0002.
- *P. hastatus* 2016: 11 offset-estimated individuals, 7 evaluable after correction, median
  absolute offset 2.00 m; calibrated excess +0.3808, p=0.0002.

Thus **2/2 structurally eligible panels retain calibrated identity after empirical stationary
offset correction**. The stationary analysis is corroborative only and cannot alter the 5/6
primary decision.

### Tracking-window overlap

Positive overlap among repeat-individual tracking windows is 71.4% (*Tadarida*), 86.0%
(*Eidolon*), 91.7% (*Hypsignathus*), 76.6% (*P. hastatus* 2022), 100% (*P. hastatus* 2023), and
31.1% (*P. hastatus* 2016).

Temporal context therefore remains a limitation, especially for 2016. No new time-block
permutation family is authorized.

### Stop rule

This tag-bias v1 family is complete and is the final new scientific audit before submission. No
further scientific analysis family is opened.

## Submission status

**JAE v0.3.3 rc2 is scientifically superseded and must not be submitted.**

Current scientific candidate: `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`.

The v0.3.4 rc3 package is retained as the pre-audit baseline and must not be submitted as the final scientific version.

Main-side validation at scientific-content commit `29c18a9f3c29ee2f561e0f7d28cd340fcc55aa22`:

- manuscript CI estimate: 6,384 words;
- abstract: 286 words in five numbered statements;
- calibrated Figures 1–6: workflow success;
- anonymous double-spaced line-numbered review PDF: workflow success, 22 pages;
- all figure and review-PDF pages visually inspected.

The v0.3.4 scientific content remains frozen at `29c18a9f3c29ee2f561e0f7d28cd340fcc55aa22`.
The rc1 provenance baseline is `1f28e833402d3fdd7dd6ce274e5392bf253fee84`.
A packaging-only rc2 added a strict final-upload metadata/DOI guard and retired the superseded
Movement Ecology PR without changing the manuscript's scientific content.

Packaging-only **rc3** additionally fixes double-anonymous review leakage of the repository owner,
adds an anonymity CI guard, makes the title-page data-availability statement enumerate all six
Movebank source DOIs, and adds a Zenodo release-readiness gate. RC3 still points to the same
scientific-content commit.

## v0.3.6 automated validation

- manuscript CI estimate: **7,932 words**;
- abstract: **273 words**, five numbered statements;
- keywords: **7**;
- Figures 1–7: generated and visually inspected;
- anonymous review PDF: **26 pages**;
- anonymity gate: **PASS**;
- final PDF visual diff from the prior full-inspection build is confined to page 26; Figure 7 legend placement and anonymous repository wording were re-inspected.

The final tag-bias audit is complete. No further new scientific analysis is required or authorized
before submission.

### v0.3.6 rc2 packaging

The scientific v0.3.6 package is unchanged. A packaging-only rc2 corrects the title-page
word-count field from the superseded v0.3.5 value to the current 7,932-word manuscript estimate.
The corrected package passes main submission CI (run 36330015862).

### v0.3.6 rc3 metadata infrastructure

The scientific package is unchanged. Final human/archive metadata now use one explicit source:
`submission/jae_v0_3_6_metadata.json`.

A deterministic assembler generates the journal title page, `CITATION.cff`, and a combined
word-count summary. The workflow is split into pre-release and post-Zenodo-DOI stages so it does
not require a DOI before Zenodo has minted one. Release and journal-upload gates cross-check
version, license, release date, DOI and the 8,500-word limit.

The entire path has passed an end-to-end synthetic Actions self-test. No human identity,
authorship, license choice or DOI is inferred.

### v0.3.6 rc4 active-reference integrity

RC4 is packaging-only. The scientific v0.3.6 manuscript and all audit results are unchanged.
Active submission documents now consistently identify v0.3.6/rc4, the generated final title page,
and the one-source metadata JSON. A CI guard blocks stale current-package references.

## v0.3.7 comparative-first editorial revision

The scientific analyses and claim ceiling are unchanged. The manuscript narrative now leads with
the five comparative panels that retain centered vertical-distribution shape identity. *Tadarida*
is treated as the motivating boundary case.

Validated main package:
- manuscript CI estimate: **6,548 words**;
- abstract: **255 words**;
- Introduction: **723 words**;
- main figures: **5**;
- Supporting Figures: **2**;
- anonymous review PDF: **22 pages**;
- anonymity gate: **PASS**.

Detailed amendment history and the former Tadarida/architecture figures are now Supporting
Information.

## v0.3.7 rc2 release preflight

RC2 is packaging-only. Scientific content and the comparative-first v0.3.7 manuscript are unchanged.
A manual, fail-closed GitHub/Zenodo release preflight now verifies the final candidate commit,
metadata/CITATION/LICENSE completeness, pending pre-mint DOI state, release-note placeholders,
and absence of an existing target tag/release before publication.

The preflight never creates a tag or publishes a release. Release-preflight self-test: run 36373116328 — PASS.

## v0.3.8 ecology-first shape interpretation

The inferential scientific programme is unchanged and remains closed.

v0.3.8 adds one frozen **descriptive-only** layer to visualize the already-tested centered-shape
profiles. The inferential result remains the calibrated whole-profile identity test.

The exact common-cell leave-one-session-out self profiles were reconstructed for all evaluable
individuals in the five comparative panels. Evaluable n exactly matches the frozen audit:

- *Eidolon*: 20;
- *Hypsignathus*: 24;
- *P. hastatus* 2022: 33;
- *P. hastatus* 2023: 16;
- *P. hastatus* 2016: 10.

Visible features of the displayed estimates include:
- central concentration around the session-specific median;
- upper-tail use;
- lower-tail use;
- tail asymmetry.

These component-wise ranges were not separately calibrated against exchangeability and can include
finite-session profile-estimation noise. They therefore illustrate candidate dimensions of shape
heterogeneity but do not identify which component carries the validated whole-profile identity
signal. No cluster, strategy type, behavioural state or new p-value is inferred.

The current manuscript is ecology-first:

> **Repeatable individual shapes of vertical space use persist beyond coarse horizontal occupancy in bats**

Validated main package:
- manuscript CI estimate: **7,887 words**;
- abstract: **282 words**;
- Introduction: **685 words**;
- Results: **1,328 words**;
- Discussion: **1,602 words**;
- main figures: **6**;
- Supporting Figures: **2**;
- anonymous review PDF: **26 pages**;
- anonymity gate: **PASS**.

Descriptive Figure 6 provenance:
- canonical Linux run: `36375056204`;
- independent macOS run: `36375120545`;
- identical panel n and upper-tail ranges.

### Working mechanism decomposition

The current data establish non-exchangeability of the full centered vertical distribution, which
can be interpreted as repeatable **organization of vertical space use** around each session's
typical altitude. They do not identify its mechanism.

The Discussion now separates two non-exclusive routes:

1. **behavioural-mixture individuality** — individuals repeatedly allocate different fractions of
   time among commuting, feeding-patch, social-site or other behavioural states;
2. **within-state individuality** — individuals retain different vertical distributions even while
   performing the same broad behaviour, potentially through morphology, route memory, experience,
   resource choice or atmospheric response.

Resource specialization can operate upstream of either route. The prospective discriminator is
state conditioning: disappearance of identity after independent behavioural classification would
support the mixture explanation as sufficient, whereas persistence within state would show a
deeper level of movement individuality. No behavioural-state mechanism is inferred from the
current data.

## Claim boundary

Allowed:

- repeatable vertical individual identity;
- individual non-exchangeability;
- vertical identity beyond occupancy differences among the tested coarse horizontal cells;
- estimator-calibrated additional conditional information;
- descriptive pairwise vertical self-identification under common horizontal weighting.

Not established:

- complete removal of fine-scale horizontal fidelity;
- independence from central-place departure/arrival structure;
- conditional-dominant versus marginal-dominant biological classes;
- stable individual-specific place × height maps;
- personality, learning, adaptation or optimality;
- verified foraging specialization;
- which Figure 6 component specifically carries the calibrated whole-profile identity signal;
- inferential between-individual or between-panel differences in the uncalibrated central/tail ranges;
- one universal causal mechanism.
