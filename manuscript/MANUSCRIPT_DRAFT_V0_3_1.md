# Manuscript draft v0.3.1

## Working title

**Individual vertical identity has multiple predictive architectures across bat systems**

## Abstract

1. Individual specialization is commonly quantified through horizontal space or resource use, but flying animals also occupy a vertical axis. We asked whether individual identity in bat vertical airspace is repeatable across nights and whether that identity is expressed mainly in an animal-wide height distribution or becomes more informative when vertical state is conditioned on horizontal place.

2. We analysed repeated three-dimensional tracking in a focal population of European free-tailed bats (*Tadarida teniotis*) and applied prospectively frozen replication designs to public tracking panels spanning three additional bat taxa. For held-out sessions we quantified self-versus-other predictive information in location-conditioned vertical distributions (conditional identity), in marginal vertical distributions (marginal identity), and their difference (conditional advantage).

3. In *T. teniotis*, an independent early/late identity-assignment test showed repeatable conditional identity (exact permutation p = 0.000174). Session-level identity was conditional-dominant at 5 km (conditional = 0.428 nats/fix; marginal = 0.052), and the same qualitative pattern persisted using height above ground. However, a stronger frozen test of a stable individual-specific cell-by-height residual map after marginal altitude adjustment did not pass (p = 0.160).

4. Conditional-dominant identity replicated prospectively in *Eidolon helvum* (0.219 versus 0.002 nats/fix) and *Hypsignathus monstrosus* (0.029 versus -0.021). In contrast, a prospectively frozen *Phyllostomus hastatus* 2022 panel was marginal-dominant (0.056 versus 0.176). An untouched 2016 dry-season panel failed to reproduce that 2022 architecture.

5. Individual vertical identity therefore has multiple predictive architectures: horizontal context can substantially increase individual information in some systems, whereas animal-wide height is more informative in another. This architecture can vary across ecological contexts, while the behavioural mechanism producing it remains unresolved.

**Keywords:** bats; individual specialization; movement ecology; non-exchangeability; predictive identity; three-dimensional movement; vertical space use

## Introduction

Individual specialization is a fundamental source of population niche structure. Conspecific
animals may differ consistently in resources, habitats, routes or activity, such that a pooled
population distribution represents a mixture of non-exchangeable individuals rather than a
single strategy. In bats, repeated horizontal space use and foraging-site fidelity have provided
clear examples of this phenomenon. Three-dimensional tracking now makes it possible to ask a
parallel question in the vertical dimension.

Vertical individuality can take several forms that are biologically distinct but easily
confounded in pooled analyses. One animal may simply use a higher or lower overall range of
flight heights than another. Alternatively, individual identity may become informative only when
height is evaluated in horizontal context: the same height can have different predictive
relevance in different parts of the landscape. These possibilities correspond to different
predictive architectures even before their behavioural mechanism is known.

The present study originated from an apparent paradox in European free-tailed bats,
*Tadarida teniotis*. The source study showed that these bats use topography and nocturnal
updrafts during high and fast flight (O'Mara et al. 2021). A later projection-loss analysis found
that the fitted population distribution remained vertically thick after horizontal position was
known, retaining approximately 4.02 effective altitude states, but the pooled
location-conditioned vertical distribution failed to transfer to two held-out bats. Rather than
interpreting this failure as absence of vertical structure, we asked whether it reflected
individual non-exchangeability.

We separate two predictive quantities. The first is marginal identity: whether a bat's other
session predicts its overall vertical state better than other bats do. The second is conditional
identity: whether the same comparison improves when vertical state is predicted conditional on
horizontal place. Their difference, which we call the conditional advantage, describes whether
horizontal context adds predictive individual information.

Importantly, this contrast is predictive rather than mechanistic. A positive conditional
advantage does not by itself demonstrate a stable latent individual-by-location interaction.
For the focal *Tadarida* dataset we therefore retain a separate, prospectively frozen residual-map
test that explicitly asks whether an individual-specific cell-by-height map remains stable after
marginal altitude preference is absorbed. That stronger test provides a claim boundary for the
comparative architecture analysis.

We then evaluated whether the conditional-versus-marginal architecture generalized beyond the
focal species. An outcome-blind search of public Movebank bat datasets was structurally frozen
before numeric vertical outcomes were used for admission. Six sources from four taxa met fixed
requirements for same-event x-y-height data and repeated individual tracking. We used these data
to test three predictions: (1) vertical individual identity should recur across nights in
multiple systems; (2) its predictive architecture need not be universal; and (3) architecture
may vary across temporal contexts within a species.

## Methods

### Focal dataset and vertical semantics

The focal dataset comprises GPS tracks of *T. teniotis* from O'Mara et al. (2021). The original
Movebank tracking stream was checksum-pinned before analysis. The primary vertical coordinate is
GPS height above mean sea level. A separate archived annotated table provides terrain elevation
from a 30-m ASTER DEM and height above ground, allowing a terrain-relative validation without
redefining the original endpoint.

### Session-level predictive identity

For each eligible held-out session, we estimated a self distribution from other session(s) of the
same bat and an other-individual distribution from comparison bats within the relevant cohort.
Horizontal space was discretized prospectively; the focal primary grid was 5 km. Vertical state
used fixed physically interpretable bins. Jeffreys smoothing was applied upstream of held-out
scoring.

Conditional identity was

[
G_{cond} = E_{target}[\log P_{self}(z|x,y)-\log P_{other}(z|x,y)].
]

Marginal identity was

[
G_{marg} = E_{target}[\log P_{self}(z)-\log P_{other}(z)].
]

The conditional advantage was

[
G_{adv}=G_{cond}-G_{marg}.
]

Positive values indicate that horizontal context increases predictive self-information. GPS fixes
estimate session distributions, but session results are aggregated with individuals as the
biological summary unit.

### Focal residual-map refinement

A distinct frozen focal analysis split each individual's eligible records into early and late
halves. Each bat's early marginal altitude distribution was incorporated into a
marginal-adjusted cell baseline. A shrunk individual-specific cell-by-height map was then compared
with that baseline on late events. An exact 8! identity-assignment permutation test evaluated
whether residual individual-specific cell-by-height organization remained stable. This endpoint
is stronger than the session-level conditional advantage and was not redefined after results were
opened.

### Focal controls

We used four orthogonal controls. First, we repeated the session-level analysis using height above
ground. Second, terrain elevation itself was treated as the added vertical state to test whether
repeatability was reducible to repeated microtopographic route choice. Third, each target session
was compared with other bats tracked during the same calendar night, asking whether
contemporaneous shared conditions outpredicted the same bat on another night. Fourth, we removed
population averaging by comparing the self predictor directly with each alternative individual.

A separately frozen reaction-norm analysis tested whether one repeatable response to modelled
vertical wind explained focal individuality. That endpoint was retained regardless of outcome.

### Outcome-blind comparative panel

Public candidate discovery used Movebank/DataCite metadata under the Movebank DOI prefix.
Candidate event streams were checksum-pinned before structural screening. Admission could inspect
schema, individual identifiers, timestamps, x-y availability, outlier flags, taxon identity and
presence/missingness of a native vertical field, but not numeric vertical outcomes.

The common gate required a native vertical coordinate on the same event as x-y and time, at least
eight individuals with x-y-height presence and at least five individuals with two or more
eligible repeated sessions. The search universe was then closed before comparative outcomes were
used to expand the panel.

Prospective independent panels were evaluated within source-appropriate cohorts so that site or
year identity could not substitute for individual identity. Vertical reference semantics remain
source-specific; cross-taxon comparison concerns predictive architecture, not equality of
absolute flight height.

## Results

### Individual identity predicts later vertical state in the focal species

The focal early/late identity-assignment analysis strongly rejected exchangeability of
individualized conditional vertical maps. The observed diagonal gain was +0.1682 nats per event,
with six of eight own-map gains positive, and the exact identity-assignment permutation
probability was p = 0.000174. Thus an early map from the correct bat contained information about
that bat's later vertical state.

### Focal identity is conditional-dominant at the session level

At 5 km, held-out session scoring in MSL coordinates gave conditional identity +0.428 nats/fix
and marginal identity +0.052, a conditional advantage of +0.376. Five of six evaluable bats had
positive conditional self-transfer.

Terrain-relative analysis gave the same qualitative architecture. Conditional AGL identity was
+0.337, whereas marginal AGL identity was -0.255, producing a conditional advantage of +0.591.
Terrain elevation alone produced only +0.007 conditional identity at 5 km. Thus the predictive
contrast was not reducible to repeatedly occupying the same local ground elevations.

The same-bat predictor also generally outperformed bats experiencing the target calendar night:
mean self-versus-same-night gain was +0.484 in AGL and +0.436 in MSL, with four of five evaluable
individuals positive in each coordinate frame. Pairwise comparisons likewise favored the correct
bat conditionally more strongly than marginally.

### A stronger residual-map interpretation is not supported

When each individual's marginal altitude preference was explicitly absorbed into a frozen
cell-specific baseline, adding the early individual-specific cell-by-height residual map did not
pass the preregistered test. The residual diagonal gain was +0.0240, exact permutation p = 0.160,
with five of eight residuals positive; fixed shrinkage sensitivities also failed. Accordingly,
the focal results establish repeatable conditional identity but not a stable latent
individual-specific cell-by-height map.

The frozen vertical-wind reaction-norm analysis also failed to identify one common mechanism.
Only two repeated individuals met the preregistered wind-variation requirement, their signs
conflicted and the permutation probability was p = 0.334.

### Conditional dominance replicates in independent species

In *Eidolon helvum*, candidate identity, site-year cohorting and the pass rule were frozen before
numeric height outcomes were opened. Twenty individuals were evaluable at 5 km. Conditional
identity was +0.219, marginal identity +0.002 and conditional advantage +0.217; 17 of 20
individuals had positive conditional gain. All frozen replication criteria passed.

*Hypsignathus monstrosus* provided a second independent conditional-dominant system. Among 24
evaluable individuals, conditional identity was +0.029, marginal identity -0.021 and conditional
advantage +0.050. Direct pairwise comparison strengthened the same qualitative contrast:
+0.115 conditional versus +0.008 marginal.

### *Phyllostomus hastatus* shows a marginal-dominant architecture

A prospectively frozen 2022 *P. hastatus* panel did not replicate conditional dominance.
Conditional identity was +0.056, whereas marginal identity was +0.176, yielding a conditional
advantage of -0.120 across 33 evaluable individuals. Direct pairwise scoring preserved this
direction (+0.285 conditional versus +0.323 marginal), showing that the result was not produced by
averaging heterogeneous alternative bats.

Architecture was not stable across temporal panels of the same species. In 2023, conditional
identity was +0.033 and marginal identity +0.013. After the 2022 marginal-dominant pattern was
known, an untouched 2016 dry-season panel was prospectively frozen as a test of whether that
architecture represented a stable dry-season property. It failed: conditional identity was
+0.058, marginal identity +0.016 and conditional advantage +0.041. Thus a simple dry-season
explanation is not supported.

## Discussion

Across the admitted bat systems, vertical individual identity is repeatable but not organized
through one universal predictive geometry. In three systems, horizontal context substantially
increases self-information relative to an overall height distribution. In the 2022
*P. hastatus* panel, the opposite pattern occurs: the animal-wide vertical distribution is more
informative than the additional location-conditioned contrast.

This distinction matters for how population three-dimensional space use is interpreted. A pooled
vertical distribution can be thick even when individuals are non-exchangeable. Conversely,
failure of a population-conditioned map to transfer need not mean that vertical organization is
absent. It can indicate that the pooled surface combines individuals whose vertical identity is
organized differently.

Our focal analyses also show why conditional dominance should not be overinterpreted. Several
controls establish that the focal contrast is not simply terrain elevation, night-wide shared
conditions or a pooled-baseline artefact. Yet the stronger residual-map test does not support a
stable individual-specific cell-by-height map after marginal altitude identity is controlled.
Conditional architecture is therefore best treated as a predictive ecological property whose
underlying behavioural mechanism remains open.

The *Phyllostomus* results further suggest that predictive architecture itself can vary with
ecological context. The 2022 marginal-dominant pattern was not recovered in an untouched 2016
dry-season panel, and the 2023 panel was weakly conditional-dominant. This prospective failure is
important because it rules out an attractive but overly simple seasonal narrative. Resource
geography, colony state, route structure, social environment, atmospheric conditions and
instrumentation remain possible contributors.

The study has several limitations. Vertical reference systems differ among source datasets; the
comparison therefore concerns the organization of predictive identity, not absolute height.
Behavioural state is not harmonized across datasets, so the paper concerns flight and airspace
use rather than validated foraging specialization. Finally, repeatability is observational and
does not imply personality, learning, adaptation or optimality.

The main empirical opportunity now lies outside this frozen public-data programme. Repeated
three-dimensional tracking of the same individuals across experimentally or naturally contrasting
contexts would allow direct testing of whether conditional-versus-marginal architecture is itself
a plastic individual trait.

## Conclusion

Individual vertical identity in bat airspace has multiple predictive architectures. Across nights,
identity can be more informative in a location-conditioned vertical distribution than in an
animal-wide height distribution, or vice versa, and that balance can vary among systems and over
time. Treating vertical individuality as a predictive architecture rather than a single
specialization score exposes heterogeneity that is hidden when three-dimensional movement is
collapsed into one pooled population map.
