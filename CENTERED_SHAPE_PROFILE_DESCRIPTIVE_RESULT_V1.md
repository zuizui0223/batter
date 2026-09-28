# Descriptive centered-shape profiles v1 — result

Canonical run: **36375056204**  
Head: `09b03f7f7bc1f2c8a523ab8008b22af4ade08810`  
Artifact: `10950667566`  
Digest: `sha256:ad4aaca53d5027946fe3b90a57bd51169fc558dfccc9c40badb25f49e0a977d5`

## Status

**Descriptive visualization only. No new hypothesis test or inferential endpoint was added.**

The displayed profiles are the identity-matched common-cell self profiles used by the already
completed session-centered shape estimator, averaged equally over each individual's evaluable
target sessions.

The evaluable individual counts exactly reproduce the frozen audit:

| panel | n |
|---|---:|
| *Eidolon helvum* | 20 |
| *Hypsignathus monstrosus* | 24 |
| *Phyllostomus hastatus* 2022 | 33 |
| *P. hastatus* 2023 | 16 |
| *P. hastatus* 2016 | 10 |

## What the descriptive figure shows

After every session is translated to zero median and profiles are integrated under the frozen
common horizontal weights, the displayed individual profile estimates are visibly heterogeneous.
The inferential evidence for non-exchangeable centered shape comes from the separately calibrated
whole-profile test, not from the component ranges summarized below.

Visible features of the displayed estimates include:

- how strongly probability is concentrated in the central -50 to +50 m bins;
- how much mass extends into the upper tail at >=100 m;
- how much mass extends into the lower tail at <=-100 m;
- asymmetry in the two tails for some individuals.

No cluster or strategy type is assigned.

### Descriptive ranges among individuals

| panel | central mass (-50 to +50 m) | upper tail (>=100 m) | lower tail (<=-100 m) |
|---|---:|---:|---:|
| *E. helvum* | 0.123–0.926 | 0.022–0.215 | 0.022–0.566 |
| *H. monstrosus* | 0.458–0.910 | 0.012–0.151 | 0.014–0.121 |
| *P. hastatus* 2022 | 0.438–0.850 | 0.037–0.157 | 0.039–0.165 |
| *P. hastatus* 2023 | 0.333–0.863 | 0.038–0.250 | 0.032–0.250 |
| *P. hastatus* 2016 | 0.548–0.994 | 0.0009–0.0686 | 0.0009–0.0408 |

These ranges are descriptive summaries of the plotted profiles, not confidence intervals or new
tests. They were not calibrated against session-label exchangeability. Because each profile is
estimated from a finite number of leave-one-session-out training sets, part of the displayed
between-individual spread can arise from profile-estimation noise even when identities are
exchangeable.

In the displayed estimates, the 2016 panel appears especially centrally concentrated overall,
whereas the other four comparative panels show broader apparent variation in tail use. *Eidolon*
includes the strongest displayed lower-tail extension, while the 2023 *P. hastatus* panel includes
the largest displayed upper-tail mass. These are visual descriptions only; no component-wise
inferential comparison is made.

## Ecological interpretation

The previously reported "shape individuality" is therefore not only an abstract classification
score. Figure 6 illustrates plausible visible dimensions of the estimated profile heterogeneity,
including **vertical concentration and tail use around the session-specific median altitude**.
However, those component-wise summaries were not separately null-calibrated, so this descriptive
layer does not establish that concentration or either tail specifically carries the validated
whole-profile identity signal.

This remains a statement about vertical space use. The figure does not distinguish commuting,
foraging, exploration or other behavioural states, and it does not establish vertical-niche
strategy classes.

## Claim boundary

- no new p-values;
- no new permutation family;
- component ranges not separately exchangeability-calibrated;
- component-wise spread may include finite-session profile-estimation noise;
- no claim that concentration or tail use specifically carries the whole-profile identity signal;
- no clustering;
- no strategy/type classification;
- no behavioural-state assignment;
- no claim that additive centering removes tag-specific error variance;
- no reopening of the final scientific-audit stop rule.
