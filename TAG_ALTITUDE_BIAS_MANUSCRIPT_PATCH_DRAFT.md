# Manuscript patch draft for v0.3.6 — tag altitude-bias audit

**Do not apply until the stationary-correction secondary output is complete.**

## Abstract replacement logic

Replace the current focal metre-scale headline with the final tag-bias statement:

> When every retained session was translated to zero median before vertical binning, calibrated
> vertical-distribution shape identity remained in five of six panels (upper-tail p=0.0002–0.0076)
> but not focal *Tadarida teniotis* (p=0.5121). Thus additive tag/device altitude offsets cannot
> explain the cross-panel pattern generally, although the focal signal contains a substantial
> absolute vertical-location component that the archive cannot separate from possible device
> offset.

Retain the endpoint-neighbourhood result, but do not headline the raw 256-m AGL translation.

## Methods — new subsection

### Additive tag/device altitude-bias audit

GPS altitude can contain tag- or device-specific additive offsets. Because one biological
individual is commonly associated with one tag within a deployment, a stable additive offset can
mimic repeatable absolute vertical position.

We therefore froze a final audit before opening its outcomes. The primary test was deliberately
independent of any external calibration location. Within every already-retained session, we
subtracted that session's median primary vertical coordinate from every fix before vertical
binning. Centered residual heights were assigned to fixed bins
(-inf, -400, -200, -100, -50, 0, 50, 100, 200, 400, inf m), while horizontal cells, cohort
definitions, self/other weighting, minimum scored fixes and whole-session identity permutations
were unchanged. Session centering removes any additive constant device offset exactly and also
removes session-specific constant altitude shifts. Each panel was required to retain exactly its
original evaluable-individual count. Support required a positive observed-minus-null common-cell
shape score and one-sided P(null >= observed) <=0.05.

Before opening numeric height for a separate empirical correction, we also froze an x-y/time-only
stationary preflight. Candidate stationary fixes required both adjacent gaps <=20 min and both
adjacent horizontal speeds <=0.5 m/s. Candidates were assigned to 100-m cells. A cell was shared
when >=3 individuals contributed >=5 candidate fixes each; an individual was supported with >=10
candidate fixes across >=1 shared cell. A panel was eligible for stationary-height correction only
when supported individuals numbered at least max(5, ceil(0.5 × original evaluable n)) and an
admitted cohort retained >=3 supported repeat individuals. This gate admitted only
*Hypsignathus monstrosus* and *Phyllostomus hastatus* 2016.

For eligible panels, [INSERT FINAL STATIONARY-CORRECTION SENTENCE AFTER OUTPUT].

The same x-y/time-only preflight summarized overlap in tracking windows between repeat individuals
within cohort. This timing analysis was descriptive only; no additional time-block permutation
family was opened.

## Results — primary tag-offset result

### Additive altitude offsets do not explain the cross-panel result generally

Median-centering every session removed absolute vertical location before prediction. Five of six
panels nevertheless retained calibrated common-cell identity in vertical-distribution shape.

*Eidolon helvum* retained observed centered identity +0.372 nats/fix versus a null mean of -0.071
(calibrated excess +0.443; p=0.0002). *Hypsignathus monstrosus* retained +0.074 versus -0.103
(+0.177; p=0.0002). *Phyllostomus hastatus* 2022 retained -0.039 versus -0.151
(+0.111; p=0.0002), the 2023 panel +0.045 versus -0.073 (+0.118; p=0.0002), and the 2016 panel
-0.008 versus -0.582 (+0.574; p=0.0076).

Focal *Tadarida teniotis* did not retain calibrated centered-shape identity: observed -0.263
versus null -0.241, calibrated excess -0.022, p=0.5121. Thus its previously detected vertical
identity is not supported once individual/session-specific absolute height location is removed.
Because session centering removes genuine mean-height specialization together with any additive
device offset, this failure does not demonstrate tag bias. It means that biological absolute
height preference and device offset cannot be separated for the focal signal with the archived
data.

The result meets the predeclared 5/6-PASS category: additive tag/device offsets are not a general
explanation for the comparative result, but the non-passing focal panel requires an explicit
absolute-location/device-offset limitation.

### Stationary-height correction

[INSERT FINAL SECONDARY RESULT FOR H. MONSTROSUS AND P. HASTATUS 2016.]

The stationary calibration is corroborative only because it is available for two panels and
shared stationary cells are not verified equal-height roost/perch references.

### Tracking-window overlap

Repeat-individual tracking windows overlapped for 71.4% of focal *Tadarida* pairs, 86.0% of
*Eidolon* pairs, 91.7% of *Hypsignathus* pairs, 76.6% of *P. hastatus* 2022 pairs and all
*P. hastatus* 2023 pairs. The 2016 *P. hastatus* panel was less contemporaneous, with positive
window overlap for 31.1% of repeat-individual pairs and a median start-date difference of 4.0 d.
Individual identity and short-term temporal context can therefore remain partly confounded,
especially in the 2016 panel.

## Existing focal metre-scale result — required downgrade

Replace language treating 256 m as biological evidence with:

> The focal common-cell AGL profiles differed by a raw 256 m in expected height, against a
> 134-m session-label exchangeability mean. Although the calibrated excess was 123 m (p=0.0297),
> focal identity did not survive the stronger shift-invariant session-centering audit. We
> therefore treat this metre-scale quantity as a raw translation of the absolute vertical-location
> signal, which may include both biological mean-height differences and additive device offset,
> rather than as independent evidence of biological separation.

Remove 256 m from the Abstract and cover-letter headline.

## Discussion — new interpretation

### Additive device offsets are not a general explanation, but matter for the focal claim ceiling

A stable tag-specific altitude offset is a particularly important confound for individual-level
vertical tracking because tag and individual are often aligned. The shift-invariant audit gives a
direct answer without requiring knowledge of the true tag error: translating each session to zero
median removes every additive constant offset exactly.

Five panels retain identity after this transformation. The cross-panel conclusion therefore does
not depend generally on individuals carrying different altitude zero points. The result is also
biologically narrower and more informative than the raw-height analysis: in these five systems,
individuals differ in the shape of the vertical distribution after absolute level is removed.

*Tadarida* is the exception. Its centered-shape score is indistinguishable from its permutation
null. Consequently the focal result should be interpreted as repeatable absolute vertical-location
identity rather than evidence for a distinct distributional shape after translation. The absolute
component may reflect genuine mean flight-height specialization, additive tag offset, or both.
AGL transformation does not solve this problem because subtracting a common terrain model does not
remove tag-specific altitude bias.

[INSERT FINAL STATIONARY-CORRECTION DISCUSSION SENTENCE.]

### Temporal context remains a limitation

Most panels contain substantial overlap in individual tracking windows, reducing but not
eliminating individual-versus-time confounding. The 2016 *Phyllostomus* panel has notably weaker
overlap. We therefore cannot exclude stable short-term weather or seasonal context as a contributor
to individual identity in that panel. Because the present audit was predeclared as the stopping
point, we report this limitation rather than opening an additional outcome-driven time-block
permutation family.

## Final conclusion wording

> Across six bat tracking panels, identity-matched vertical profiles exceed session-label
> exchangeability expectations after coarse horizontal occupancy is standardized. In five panels,
> the signal also survives removal of every session's absolute altitude level, showing repeatable
> individual structure in vertical-distribution shape that cannot be generated by a constant
> additive tag offset. Focal *Tadarida* does not survive that transformation, so its absolute
> vertical-location component remains inseparable from possible device bias. Central-place and
> temporal context also remain panel-dependent limitations.

Methodological conclusion remains unchanged and strengthened:

> Prediction-based individual identity requires calibration of the complete analysis pipeline;
> intuitive zero and 0.5 references are not universal exchangeability nulls.
