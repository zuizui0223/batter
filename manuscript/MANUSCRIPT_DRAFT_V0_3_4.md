# Manuscript draft v0.3.4

## Working title

**Repeatable vertical identity in bat airspace persists after horizontal occupancy is standardized**

## Abstract

1. Individual specialization can occur along the vertical dimension, but apparent vertical differences may arise simply because individuals repeatedly occupy different horizontal locations. We asked whether individual identity remains informative about bat vertical airspace use when self and other individuals are evaluated under the same horizontal occupancy distribution.

2. We analysed six public three-dimensional tracking panels spanning four bat taxa. For held-out sessions, self and other vertical profiles were integrated using identical horizontal-cell weights. Whole-session identity permutations preserved within-session movement, sample size and horizontal coverage, providing a panel-specific finite-sample exchangeability baseline. Source selection and subsequent calibration algorithms were frozen before their respective comparison outputs were opened.

3. Identity-matched common-cell vertical scores exceeded permutation expectations in all six panels (upper-tail p = 0.0002–0.0422). Under the same horizontal weighting, the same individual's vertical profile outpredicted a specific alternative individual in 0.77–0.86 of pairwise comparisons in five panels; a 2016 *Phyllostomus hastatus* panel was weaker (0.594, individual-bootstrap 95% interval 0.495–0.704).

4. In focal *Tadarida teniotis*, terrain-relative height above ground retained calibrated vertical identity at 5 km (p = 0.0161) and 2.5 km (p = 0.011), but not 10 km (p = 0.1018). A predeclared exclusion around an x-y-only night-endpoint proxy also did not pass (1-km radius p = 0.1109), leaving central-place structure as a possible contributor. A stronger frozen test of a stable individual-specific cell-by-height residual map remained unsupported (p = 0.160).

5. Bat vertical airspace use therefore contains repeatable individual structure that is not reducible to differences in occupancy among the tested horizontal cells alone. The effect is scale dependent in the focal species, may include central-place structure and has unresolved behavioural mechanisms. Separating horizontal occupancy from vertical identity provides a tractable way to study individuality in three-dimensional animal niches.

**Keywords:** bats; individual specialization; movement ecology; non-exchangeability; three-dimensional movement; vertical niche; vertical space use

## Introduction

Individual specialization can make a population niche a mixture of non-exchangeable individuals rather than a single strategy shared by all members of a population (Bolnick et al. 2003). In movement ecology, such heterogeneity appears as repeated differences in home ranges, habitat use, routes and foraging locations. Bats provide clear examples: individuals can specialize in horizontal space use and foraging areas, and the magnitude of spatial specialization can change among ecological contexts or seasons (Kerches-Rogeri et al. 2020; Wang et al. 2023). These findings matter because population-level movement surfaces are routinely interpreted as if they describe interchangeable individuals.

Animals move in three dimensions, however, and the vertical axis is not simply a graphical extension of a horizontal map. Vertical position changes microclimate, energetic opportunity, resource access, exposure and interaction environments over distances that can be far shorter than horizontal environmental gradients (Gámez & Harris 2022; Xing et al. 2023). Individual differences in vertical behaviour are already well established. Brünnich's guillemots show repeatable individual differences in dive depth, dive shape and flight time over periods extending from hours to years (Woo et al. 2008). South Georgia shags partition foraging-depth niches, with substantial dive-depth variation attributable to individuals (Ratcliffe et al. 2013). Southern elephant seals show long-term fidelity to three-dimensional foraging habitats (McIntyre et al. 2017). In the aerosphere, free-flying swallows and martins also differ among individuals in flight altitude (Dreelin et al. 2018). Thus neither vertical specialization nor individual altitude differences are, by themselves, novel phenomena.

The unresolved problem is that horizontal and vertical specialization can be confounded. A diving individual may appear depth-specialized because it repeatedly visits a patch with a characteristic bathymetry. Ratcliffe et al. (2013) explicitly noted that individual dive-depth specialization can arise when animals repeatedly use subsets of patches that differ in water depth, while other systems show depth strategies that differ even over the same patch. The same problem applies in airspace. A bat that repeatedly follows a ridge, valley, commuting corridor or roost approach can acquire a repeatable height distribution even if it has no independent vertical preference. In absolute altitude coordinates, horizontal fidelity to terrain can be converted directly into apparent vertical identity.

This creates a counterfactual question that ordinary repeatability does not answer: **if the same individual and its conspecifics were evaluated under the same horizontal occupancy distribution, would individual identity still carry information about vertical state?** A positive answer would not prove an intrinsic vertical strategy, because fine-scale position within cells, behavioural state and central-place structure could still contribute. It would, however, reject the simpler explanation that vertical individuality is only a consequence of occupying different coarse horizontal areas.

We address this question using held-out prediction. For each target session we learn a vertical distribution from other sessions of the same bat and compare it with vertical distributions learned from other bats. Crucially, self and other vertical profiles are integrated using an identical horizontal-cell weighting. We then calibrate the score against whole-session identity permutations that retain each session's x-y-z observations, sample size and horizontal coverage. This matters because finite cell counts and probability smoothing make the exchangeability expectation of a self-versus-other log-score contrast non-zero. Rather than assuming zero as a universal null, each panel is judged against its own prediction-pipeline null.

The study began with European free-tailed bats, *Tadarida teniotis*. Their source study showed high-altitude flight associated with topography and nocturnal uplift (O'Mara et al. 2021). A previous frozen analysis found a vertically thick population distribution but poor transfer of the pooled location-conditioned vertical model to two held-out bats. Follow-up analyses then showed strong early-to-late individual identity matching, while a stronger test of one stable individual-specific cell-by-height residual map failed. Those results motivated a broader question: whether repeatable vertical individuality survives direct control for horizontal occupancy.

To avoid searching adaptively for supportive examples, we used a previously closed, outcome-blind public-data screen. Six tracking sources from four bat taxa met fixed structural requirements for same-event horizontal and vertical positions and repeated individuals. The comparative panel contains *T. teniotis*, *Eidolon helvum*, *Hypsignathus monstrosus*, and three temporal *Phyllostomus hastatus* datasets. The original analyses of these panels were frozen before a later estimator audit exposed a negative finite-sample null and horizontal leakage into the ordinary marginal score. The focal calibration algorithm was then frozen before its output was opened; after that result showed a material effect, a common cross-panel calibration contract was frozen before any non-*Tadarida* calibration output was opened. We retain that analysis history explicitly rather than presenting the corrected estimand as if it had been the original hypothesis.

Our main question is whether identity-matched vertical profiles contain more held-out predictive information than expected under session-level exchangeability after horizontal occupancy is standardized at the primary 5-km grain. We then translate this information into direct pairwise self-identification rates. In the focal *Tadarida* system we additionally ask whether the result persists in terrain-relative height above ground (AGL), after excluding an independently defined night-endpoint neighbourhood, and at 2.5- and 10-km grains. These focal controls predefine the ceiling of the biological conclusion: evidence for vertical identity beyond tested horizontal occupancy, not proof of personality, learned routes or a scale-invariant causal vertical strategy.

## Materials and Methods

### Study design and inferential unit

The unit of biological replication was the individual. GPS fixes were used to estimate within-session probability distributions and held-out log scores, but were not treated as independent biological replicates. Session scores were averaged within an individual and panel summaries then weighted individuals equally.

The principal design was leave-one-session-out prediction. For a target session of individual i, the self predictor was built from that individual's other eligible session(s). The comparison predictor used eligible sessions of other individuals within the same admitted panel context or cohort. Target fixes were scored only where the required horizontal support was shared.

### Public-data screen and closed source universe

The public source screen searched Movebank Data Repository records and considered 23 parent bat datasets, including legacy packages recovered through child handles. Source admission was determined without using numeric vertical outcomes. The screen could use field names, source checksums, individual identifiers, timestamps, finite horizontal coordinates, source outlier flags, the presence of a vertical field, and repeated-session structure.

A source required a vertical coordinate on the same event as horizontal position and time, at least eight individuals with x-y-height presence, and at least five individuals with two or more sessions containing at least 50 fixes under the common structural rules. Six sources from four taxa passed. Once comparative outcomes had been observed, the source universe was closed and was not reopened during estimator calibration or manuscript revision.

### Focal *Tadarida teniotis*

The focal source is the Movebank archive associated with O'Mara et al. (2021), DOI 10.5441/001/1.52nn82r9. The original tracking bitstream and the archived annotated table were checksum-pinned before analysis. The annotated table contains 9,873 rows after the source workflow's manual exclusions and includes terrain elevation, MSL altitude and terrain-relative height above ground.

The paper-facing session definition in the annotated analysis was animal ID × BatDay. Sessions with fewer than 50 usable fixes were excluded. Horizontal positions were projected to EPSG:3035. The primary horizontal grain was 5 km. Vertical state used fixed bins with edges -infinity, 0, 50, 100, 200, 400, 800, 1600, 3200 and infinity metres. Jeffreys smoothing added 0.5 to each vertical bin. At least 50 target fixes had to remain on common supported horizontal cells.

### Original conditional and marginal scores

For each horizontal cell c, the self conditional predictor P_self(z|c) was the equal-session average of smoothed vertical-bin distributions from the focal animal's other sessions. The other-individual predictor P_other(z|c) was the equal-individual average of the corresponding distributions from other bats.

The original conditional identity score was

G_cond = mean_target [ log P_self(z|c) - log P_other(z|c) ].

The original marginal score separately estimated P_self(z) and P_other(z) from each training set's own horizontal occupancy and calculated

G_marg = mean_target [ log P_self(z) - log P_other(z) ].

Their difference, G_adv = G_cond - G_marg, was initially used to describe conditional- versus marginal-dominant predictive architecture. A later estimator audit showed that G_adv has a panel-specific non-zero exchangeability expectation and that ordinary P(z) can inherit differences in horizontal cell occupancy. We therefore retain these values only as historical endpoints and do not use their sign to classify biological architectures.

### Common-cell horizontal standardization

The corrected primary descriptive vertical score integrates self and other vertical profiles over the same horizontal distribution.

For each target session, let C be the horizontal cells supported by both P_self(z|c) and P_other(z|c). For every self-training session, we calculated its relative frequency of fixes across C. These cell-frequency vectors were averaged equally across self-training sessions and renormalized to define w_self(c).

We then calculated

M_self(z) = sum over c in C of w_self(c) P_self(z|c)

and

M_other(z) = sum over c in C of w_self(c) P_other(z|c).

The common-cell vertical identity score was

G_cc = mean_target [ log M_self(z) - log M_other(z) ].

Because the identical w_self(c) multiplies the self and other vertical profiles, differences in their coarse horizontal occupancy are removed from this comparison. Positive raw G_cc means the identity-matched vertical profile outpredicts the pooled other-individual profile on the scored target fixes. We do not require G_cc itself to be positive for evidence of identity matching, because the finite-sample prediction pipeline has a non-zero exchangeability expectation.

### Whole-session permutation calibration

For the focal panel, the calibration design was frozen before the focal calibration output was opened. Whole retained session blocks were assigned permuted individual labels while preserving all x-y-z observations within each session, session sizes, horizontal coverage, and the original multiset of session counts assigned to individual labels. We ran 9,999 Monte Carlo permutations using a fixed PCG64 seed.

The focal result established that the pipeline null was materially negative. Before opening any non-*Tadarida* calibration output, we froze one common calibration contract for the five remaining panels. Those permutations were conducted within each admitted cohort, retaining cohort membership and the exact number of sessions assigned to each label within that cohort. Each non-focal panel used 4,999 frozen Monte Carlo permutations with predeclared seeds.

For each panel we report the observed common-cell score, the permutation-null mean and quantiles, the null-centered difference G_cc - mean(null), and the one-sided Monte Carlo tail probability P(null >= observed). The inferential statement is identity matching relative to this panel-specific finite-sample exchangeability distribution, not significance relative to zero.

### Direct pairwise self-identification

To translate the result into an intuitive descriptive magnitude, we froze a separate effect-size analysis before opening its output. For each held-out target session and each specific alternative individual within the same cohort, we compared the same-bat and alternative-bat vertical profiles using identical self-derived horizontal cell weights. A self win occurred when the target's mean log probability was higher under the same individual's profile.

Alternative comparisons were averaged within target session, sessions were averaged within biological individual across admitted cohorts, and individuals were weighted equally. We report the equal-individual self-win fraction and a 20,000-replicate individual-bootstrap percentile interval. A 0.5 reference is shown for interpretation only; no new p-value gate was added.

We also report exp(G_cc) as an observed per-fix geometric self-versus-other likelihood multiplier and exp(G_cc - mean(null)) as a null-calibrated effect scale. Because GPS fixes are not independent biological replicates, these multipliers are not compounded across fixes.

### Independent comparative panels

For *Eidolon helvum* (O'Mara et al. 2019; Movebank DOI 10.5441/001/1.k8n02jn8), 63 animals had horizontal and vertical presence and 42 had repeated structurally eligible sessions before numeric height was opened. The native vertical field was ellipsoid height. Analyses were stratified within exact study-site × shifted-night-year cohorts.

For *Hypsignathus monstrosus* (Schloesing et al. 2023; DOI 10.5441/001/1.278), 32 animals passed structural presence screening and 24 had repeated eligible sessions. The primary admitted context was Lek Njoukou in 2020; the native vertical field was ellipsoid height.

For *Phyllostomus hastatus*, three source datasets had already been frozen for distinct prospective roles before the calibration audit: a 2021–2022 panel (Calderón-Capote et al. 2024; DOI 10.5441/001/1.321), a 2023 temporal panel (DOI 10.5441/001/1.322), and an untouched 2016 panel from DOI 10.5441/001/1.282. The 2022 and 2016 primary vertical coordinates were MSL, whereas the 2023 source used ellipsoid height. We therefore compare predictive information within each panel and do not compare absolute flight heights among taxa or years with different vertical reference systems.

### Focal early/late identity assignment and residual-map ceiling

A separate focal analysis predating the comparative calibration split each of eight *Tadarida* individuals into early and late observations within 18 frozen 5-km cells. Early individual conditional maps were scored against every individual's later observations. The observed statistic was the mean identity-matched diagonal gain relative to the population conditional predictor; its null was the complete set of 8! assignments.

A stronger frozen refinement first absorbed each bat's marginal altitude identity into a marginal-adjusted cell baseline and then tested whether an individual-specific cell-by-height residual was stable from early to late. This test sets a mechanistic ceiling: failure means repeatable vertical identity cannot be relabelled as one fixed individual-specific cell-by-height route map.

### Terrain-relative AGL calibration

The focal annotated source provided height above ground, calculated in the original source workflow relative to a 30-m ASTER terrain model. Before opening the AGL common-cell calibration, we froze a decision contract requiring exact reproduction of the previously frozen ordinary AGL scores. We then applied the same common-cell weighting and whole-session calibration used for MSL.

The primary AGL test used 5-km cells and 9,999 permutations. Fixed grain robustness tests used 2.5- and 10-km cells with 4,999 permutations each. The predeclared scale statement required both sensitivity scales to pass if the manuscript were to claim robustness across 2.5–10 km.

### Night-endpoint neighbourhood exclusion

To assess whether departure/arrival or central-place structure could dominate the focal AGL result, we froze an x-y-only endpoint proxy before opening results. This proxy is not claimed to identify the biological roost.

Within each retained BatDay, the first five and last five finite projected fixes were selected using timestamps only. These endpoint fixes were pooled within individual, and the observed endpoint minimizing summed Euclidean distance to all other pooled endpoints was selected as that individual's proxy centre. The primary analysis removed every event strictly within 1,000 m of its own individual's proxy, symmetrically from training and target data. Sessions retained their original identities but had to contain at least 50 remaining events. Fixed descriptive radii of 500 and 2,000 m were also frozen. The primary endpoint was calibrated common-cell AGL identity, not the conditional increment.

### Biological-scale translation in focal *Tadarida*

For focal AGL only, we calculated an expected-height separation in metres. Within common supported cells, self training-session cell means were averaged equally across self sessions and other-individual cell means were averaged equally across other individuals. Both were then integrated under identical self cell-use weights. For each target session we recorded the absolute difference between the self and other expected AGL; sessions were averaged within individuals and individuals equally. This is a mean-height translation and does not capture distribution-shape differences.

### Source-study ethics

This study conducted no new capture, handling or instrumentation. The focal *T. teniotis* source study reports ICNF Portugal permit 665/2017/CAPT (O'Mara et al. 2021). The *E. helvum* programme reports approvals from relevant wildlife and veterinary authorities in Ghana, Zambia and Burkina Faso (O'Mara et al. 2019). The *H. monstrosus* study reports approval by the Ministry of Agriculture, Livestock and Fisheries of the Republic of Congo and the VetAgro Sup ethics committee, approval 1805-V2 (Schloesing et al. 2023). The *P. hastatus* programmes report Ministerio del Ambiente Panamá permits and Smithsonian Tropical Research Institute Animal Care and Use Committee approvals detailed in the source papers (O'Mara & Dechmann 2023; Calderón-Capote et al. 2024). Full source-by-source permit provenance is archived with the analysis.

## Results

### A closed public panel yielded six repeated 3-D bat datasets

The outcome-blind source screen considered 23 Movebank parent bat datasets and admitted six sources spanning four taxa. Datasets were excluded structurally when a native same-event vertical coordinate was absent or too few individuals had repeated eligible tracking. The source universe was closed before the estimator-calibration work and was not expanded after the comparative outcomes.

The six paper panels comprised focal *T. teniotis*, *E. helvum*, *H. monstrosus*, *P. hastatus* 2022, *P. hastatus* 2023 and *P. hastatus* 2016.

### Focal individual identity repeats across time, but a fixed residual map is not established

The focal early/late identity-assignment analysis strongly rejected individual exchangeability. The identity-matched diagonal gain was +0.1682 nats/event; six of eight bats had positive own-map gains and the exact 8! permutation probability was p = 0.000174 (Figure 2).

The stronger residual-map test did not pass. After marginal altitude identity had been absorbed into each bat's cell baseline, the residual cell-by-height gain was +0.0240 nats/event, five of eight diagonal residuals were positive and the exact permutation probability was p = 0.160. The frozen shrinkage sensitivities also failed. Thus correct individual identity contains repeatable vertical information, but the focal dataset does not establish one stable cell-specific vertical route map.

A separately frozen common-uplift reaction-norm analysis also did not establish a shared mechanism (permutation p = 0.334). We therefore retain the mechanism of individual vertical identity as unresolved.

### The raw conditional-versus-marginal architecture was estimator dependent

The original session-level focal decomposition produced conditional identity +0.428, ordinary marginal identity +0.052 and G_adv +0.376 nats/fix. However, the focal whole-session permutation calibration showed that the exchangeability mean of G_adv was -0.317 rather than zero. Common horizontal weighting also shifted the focal marginal score from +0.052 to +0.379 and reduced the raw conditional increment from +0.376 to +0.049.

The same issue affected the comparative interpretation. Most decisively, *P. hastatus* 2022 changed from an original G_adv of -0.120 to a common-cell conditional increment of +0.0066. The previously described marginal-dominant architecture therefore disappeared after horizontal standardization. We consequently do not use the sign of ordinary G_adv as a biological classifier.

### Individual vertical identity exceeds panel-specific exchangeability expectations in all six panels

After horizontal occupancy was standardized, the identity-matched common-cell vertical score exceeded the panel-specific permutation expectation in every panel (Figure 3).

For *T. teniotis*, observed G_cc was +0.379 nats/fix versus a null mean of -0.223 (observed-minus-null +0.602; p = 0.0005). *E. helvum* had observed +0.177 versus null -0.088 (+0.265; p = 0.0002). *H. monstrosus* had +0.022 versus -0.054 (+0.076; p = 0.0002). *P. hastatus* 2022 had +0.049 versus -0.151 (+0.200; p = 0.0002), and the 2023 panel had +0.033 versus -0.088 (+0.120; p = 0.0002).

The 2016 *P. hastatus* panel was the weakest in raw terms: observed G_cc was -0.0039 nats/fix. Nevertheless, its exchangeability expectation was substantially lower at -0.274, yielding observed-minus-null +0.270 and p = 0.0422. Thus the central cross-panel result is not that raw same-individual scores are positive in every dataset, but that correct identity matching preserves more vertical predictive information than expected when session identities are exchangeable under the same analysis pipeline.

### Direct self-versus-individual comparisons show substantial vertical distinguishability in five panels

The descriptive pairwise translation removed the pooled other-individual baseline and compared the same bat with each specific alternative individual under identical horizontal weighting (Figure 4).

The same individual's vertical profile won 0.794 of pairwise comparisons in *T. teniotis* (individual-bootstrap 95% interval 0.656–0.931), 0.858 in *E. helvum* (0.732–0.961), 0.767 in *H. monstrosus* (0.699–0.833), 0.842 in *P. hastatus* 2022 (0.800–0.883), and 0.782 in *P. hastatus* 2023 (0.659–0.865). The 2016 *P. hastatus* panel was weaker at 0.594, with its interval spanning the 0.5 reference (0.495–0.704).

Observed common-cell scores corresponded to geometric per-fix likelihood multipliers of 1.46, 1.19, 1.02, 1.05, 1.03 and 1.00 across the six panels, respectively. These values quantify predictive magnitude but were not compounded over fixes because fixes are not independent biological replicates.

### Terrain-relative identity supports a vertical component in focal *Tadarida*

At 5 km, AGL common-cell identity was +0.266 nats/fix, compared with a session-label permutation mean of -0.180. The null-centered difference was +0.446 and the frozen upper-tail probability was p = 0.0161 (n = 6; individual-bootstrap interval for the raw score -0.021 to +0.598). The result therefore passed the predeclared terrain-relative robustness rule.

At 2.5 km the signal was stronger: common-cell AGL identity was +0.603, the null mean -0.109, the null-centered difference +0.712 and p = 0.011 (n = 5; bootstrap interval +0.046 to +1.357).

At 10 km the result did not pass. Observed common-cell AGL identity was -0.013, the null mean -0.250 and the null-centered difference +0.237, but the upper-tail probability was p = 0.1018 (n = 7). The focal terrain-relative identity is therefore supported at 2.5–5 km but not established at 10 km.

### Removing the night-endpoint neighbourhood weakens focal AGL identity

The x-y-only endpoint proxy removed 602 events at the predeclared 1-km radius while retaining all 16 sessions and 9,227 events. The remaining common-cell AGL identity was +0.099 nats/fix versus a null mean of -0.180. Although the null-centered difference remained positive (+0.279), the upper-tail probability was p = 0.1109 and the frozen primary rule failed.

The 500-m and 2,000-m fixed sensitivities failed in the same direction (p = 0.0978 and p = 0.1446, respectively). These analyses do not identify a biological roost and therefore cannot demonstrate a roost mechanism. They show that the focal terrain-relative identity result is not robust to removing the predeclared departure/arrival neighbourhood. Central-place transition structure consequently remains a viable contributor.

A secondary common-cell conditional increment remained above its estimator null after the 1-km exclusion, but this endpoint was not authorized to rescue the failed primary vertical-identity test.

### Focal vertical differences can be large in metres but are heterogeneous

Under common 5-km horizontal weighting, the absolute difference between same-bat and other-bat expected AGL averaged 256 m across the six evaluable individuals. The median individual separation was 145 m and the individual-bootstrap interval for the equal-individual mean was 70–466 m.

Individual values ranged from 22 and 36 m in the two weakest bats to approximately 493 and 699 m in the strongest. Thus the focal log-score identity can correspond to biologically substantial mean-height separation, but the magnitude is highly heterogeneous and 256 m should not be interpreted as a universal individual offset.

## Discussion

### Vertical individual structure persists after coarse horizontal occupancy is standardized

Across six tracking panels from four bat taxa, identity-matched vertical profiles retained more held-out predictive information than expected under panel-specific session-label exchangeability after self and other individuals were integrated over identical horizontal-cell weights. This is the central ecological result.

The result differs from ordinary demonstrations of individual flight-altitude or dive-depth variation. Vertical individual specialization is already known in diving seabirds and marine mammals, and individual flight-altitude differences are known in aerial insectivorous birds (Woo et al. 2008; Ratcliffe et al. 2013; McIntyre et al. 2017; Dreelin et al. 2018). The unresolved issue is whether a vertical signal merely reflects repeated use of different horizontal patches. Our common-cell comparison attacks that alternative directly at the tested horizontal grain.

This distinction matters for interpreting population movement niches. A pooled three-dimensional niche can be broad because each animal is individually broad, because animals differ mainly in horizontal occupancy, or because individuals retain distinctive vertical distributions even when horizontal occupancy is held common. Our results support the third component in the admitted bat panels. Population-level vertical structure therefore need not describe an exchangeable representative individual.

### The effect is not just a statistically significant number of nats

The direct pairwise analysis provides an intuitive scale for this non-exchangeability. In five panels, the same bat's horizontally standardized vertical profile beat a specific alternative bat in approximately 77–86% of comparisons. This pattern is visible in *Tadarida*, *Eidolon*, *Hypsignathus* and both recent *Phyllostomus* panels. The older 2016 *Phyllostomus* panel is weaker and remains an important limitation rather than a dataset to be discarded.

In the focal AGL analysis, common-cell vertical differences can also correspond to substantial physical separation. The median individual expected-height difference was approximately 145 m, although the mean was pulled upward to 256 m by two bats with much larger differences. The biological magnitude is therefore heterogeneous, consistent with a population containing strong and weak individual vertical signatures rather than one universal separation scale.

### Horizontal standardization resolves one confound but not all spatial structure

The common-cell estimator removes differences in how much self and other predictors occupy the tested 5-km cells. It does not make individuals occupy identical continuous x-y coordinates. Fine-scale horizontal fidelity inside a cell can therefore still be translated into vertical differences through terrain, resource geometry or central-place routes.

The focal controls show both the value and the limit of the current design. AGL identity persists at 5 km and becomes stronger at 2.5 km, arguing against an explanation based only on absolute terrain elevation. However, the result is not established at 10 km, showing clear scale dependence. More importantly, the predeclared night-endpoint exclusion does not pass at 500 m, 1 km or 2 km. Because the endpoint proxy is deliberately not interpreted as a verified roost, this does not identify a roost mechanism. It does mean that departure/arrival or other central-place structure remains a plausible contributor to the focal signal.

For this reason, we describe the comparative result as vertical identity beyond **coarse-grained horizontal occupancy at the tested 5-km scale**, not as complete removal of horizontal fidelity. A stronger causal separation would require known roost locations, substantially finer tracking support shared among individuals, and terrain-relative vertical coordinates across all taxa.

### Estimator calibration changed the biological story

The analysis history is itself informative. The original decomposition classified panels using the sign of G_cond - G_marg and appeared to reveal conditional- and marginal-dominant architectures. A diagnostic audit then showed that the finite-sample null of this difference is negative and panel specific. It also showed that the ordinary marginal vertical distribution inherits each animal's own horizontal occupancy weighting.

The biological consequence was large. The sole strong marginal-dominant counterexample, *P. hastatus* 2022, changed from G_adv = -0.120 to a common-cell increment of only +0.0066 after horizontal standardization. The apparent qualitative architecture contrast therefore disappeared.

We did not retune the original endpoint to preserve its conclusion. Instead, the focal calibration was frozen before its result, the cross-panel calibration was frozen before the non-focal outputs, and the original architecture claim was explicitly superseded. This distinction between historical endpoint and corrected interpretation is important because analytical decompositions can look biologically categorical even when their baselines are shaped by finite-sample prediction geometry.

The corrected result is simpler ecologically: vertical identity matching survives horizontal standardization in all six panels relative to each panel's exchangeability expectation, while any additional benefit from retaining horizontal cell identity is small in raw magnitude.

### Repeatable identity does not imply a fixed route strategy

The focal early/late analysis demonstrates that correct individual identity predicts later vertical state, but the stronger cell-by-height residual test remains negative. This prevents interpreting vertical individuality as a rigid three-dimensional route map.

Several processes could produce repeatable vertical identity. Individuals could differ in morphology or flight performance, repeatedly encounter different resources within shared regions, respond differently to atmospheric conditions, use distinct social or central-place routines, or carry learned spatial histories. The source *Tadarida* study establishes that topography and nocturnal uplift shape flight behaviour at the population level (O'Mara et al. 2021), but our frozen individual uplift-reaction analysis did not identify one repeatable individual slope mechanism. The mechanism therefore remains open.

This unresolved mechanism is not unusual in individual-specialization research. Dive-depth specialization in seabirds can reflect both repeated patch choice and genuinely different depth tactics over similar patches (Ratcliffe et al. 2013). The same conceptual alternatives likely apply to airborne vertical niches. The present study separates one axis of the problem—coarse horizontal occupancy—from vertical identity, but does not identify the causal trait or decision rule.

### Comparative generality and its limits

The consistency of calibrated identity across six panels is notable because the datasets span four taxa, multiple regions and several tracking programmes. The source universe was also closed before calibration, reducing the opportunity to continue adding favourable examples.

This is nevertheless not a phylogenetic comparative study. Only four taxa passed the fixed public-data gate. Tracking schedules, source-study designs and vertical datums differ. MSL and ellipsoid heights are not directly interchangeable, and AGL was available only for the focal source. We therefore compare within-panel predictive identity, not absolute vertical position among taxa.

The 2016 *Phyllostomus* panel is especially useful because it resists a simple universal story. Its raw common-cell score is approximately zero, its pairwise self-identification interval includes 0.5, yet its identity-matched score still exceeds the much lower finite-sample permutation expectation. This combination emphasizes why raw effect magnitude and calibrated evidence are distinct.

Behavioural state is another limitation. Several source papers concern foraging or commuting, but no harmonized behavioural classifier was imposed across datasets. We therefore refer to vertical airspace or flight use, not to foraging-height specialization. Similarly, observational repeatability cannot identify personality, learning, adaptation or optimality.

### A prospective test of vertical individuality

The next decisive study should be designed prospectively rather than assembled from public archives. The same individuals should be tracked repeatedly with harmonized AGL or terrain-relative altitude, known roost locations, high-frequency horizontal positions and simultaneous atmospheric measurements.

A strong design would define fine horizontal matched strata around shared movement corridors and ask whether the same individual's vertical profile predicts held-out nights after exact or near-exact horizontal matching. Repeating that experiment across seasons would distinguish persistent individual identity from context-dependent vertical responses. Behavioural-state classification would also permit separate tests for commuting, foraging and departure/arrival phases.

Such a design would move from the current statement—vertical identity beyond coarse horizontal occupancy—to a stronger mechanistic question: **which individual traits or experiences generate repeatable vertical niche use when horizontal opportunity is genuinely shared?**

## Conclusion

Individual bats are not fully exchangeable in the vertical dimension of their movement. Across six tracking panels from four taxa, correct individual identity retained more information about held-out vertical state than expected under session-level exchangeability after self and other vertical profiles were evaluated under the same 5-km horizontal occupancy weights.

This does not mean that horizontal space is irrelevant. In focal *Tadarida*, terrain-relative identity is supported at 2.5–5 km but not at 10 km, and removing a predeclared night-endpoint neighbourhood causes the primary AGL identity test to fail. Fine-scale horizontal and central-place structure therefore remain viable contributors.

The ecological conclusion is consequently bounded but substantive: **a pooled three-dimensional bat niche contains repeatable vertical individual structure that cannot be reduced to differences in occupancy among the tested coarse horizontal cells alone.** Separating horizontal occupancy from vertical identity turns the vertical axis from a descriptive coordinate into a testable component of individual niche structure.

## References

Bolnick, D.I., Svanbäck, R., Fordyce, J.A., Yang, L.H., Davis, J.M., Hulsey, C.D. & Forister, M.L. (2003). The ecology of individuals: Incidence and implications of individual specialization. *The American Naturalist*, **161**, 1–28. https://doi.org/10.1086/343878

Calderón-Capote, M.C., van Toor, M.L., O'Mara, M.T., Bayer, T.D., Crofoot, M.C. & Dechmann, D.K.N. (2024). Consistent long-distance foraging flights across years and seasons at colony level in a neotropical bat. *Biology Letters*, **20**, 20240424. https://doi.org/10.1098/rsbl.2024.0424

Dreelin, R.A., Shipley, J.R. & Winkler, D.W. (2018). Flight behavior of individual aerial insectivores revealed by novel altitudinal dataloggers. *Frontiers in Ecology and Evolution*, **6**, 182. https://doi.org/10.3389/fevo.2018.00182

Gámez, S. & Harris, N.C. (2022). Conceptualizing the 3D niche and vertical space use. *Trends in Ecology & Evolution*, **37**, 953–962. https://doi.org/10.1016/j.tree.2022.06.012

Kerches-Rogeri, P., Niebuhr, B.B., Muylaert, R.L. & Mello, M.A.R. (2020). Individual specialization in the use of space by frugivorous bats. *Journal of Animal Ecology*, **89**, 2584–2595. https://doi.org/10.1111/1365-2656.13339

McIntyre, T., Bester, M.N., Bornemann, H., Tosh, C.A. & de Bruyn, P.J.N. (2017). Slow to change? Individual fidelity to three-dimensional foraging habitats in southern elephant seals, *Mirounga leonina*. *Animal Behaviour*, **127**, 91–99. https://doi.org/10.1016/j.anbehav.2017.03.006

O'Mara, M.T., Scharf, A.K., Fahr, J., Abedi-Lartey, M., Wikelski, M., Dechmann, D.K.N. & Safi, K. (2019). Overall dynamic body acceleration in straw-colored fruit bats increases in headwinds but not with airspeed. *Frontiers in Ecology and Evolution*, **7**, 200. https://doi.org/10.3389/fevo.2019.00200

O'Mara, M.T., Amorim, F., Scacco, M., McCracken, G.F., Safi, K., Mata, V., Tomé, R., Swartz, S., Wikelski, M., Beja, P., Rebelo, H. & Dechmann, D.K.N. (2021). Bats use topography and nocturnal updrafts to fly high and fast. *Current Biology*, **31**, 1311–1316.e4. https://doi.org/10.1016/j.cub.2020.12.042

O'Mara, M.T. & Dechmann, D.K.N. (2023). Greater spear-nosed bats commute long distances alone, rest together, but forage apart. *Animal Behaviour*, **204**, 37–48. https://doi.org/10.1016/j.anbehav.2023.08.001

Ratcliffe, N., Takahashi, A., O'Sullivan, C., Adlard, S., Trathan, P.N., Harris, M.P. & Wanless, S. (2013). The roles of sex, mass and individual specialisation in partitioning foraging-depth niches of a pursuit-diving predator. *PLOS ONE*, **8**, e79107. https://doi.org/10.1371/journal.pone.0079107

Schloesing, E., Caron, A., Chambon, R., Courbin, N., Labadie, M., Nina, R., Mouiti Mbadinga, F., Ngoubili, W., Sandiala, D., N'Kaya Tobi, Bourgarel, M., De Nys, H.M. & Cappelle, J. (2023). Foraging and mating behaviors of *Hypsignathus monstrosus* at the bat-human interface in a central African rainforest. *Ecology and Evolution*, **13**, e10240. https://doi.org/10.1002/ece3.10240

Wang, Z., Gong, L., Huang, Z., Geng, Y., Zhang, W., Si, M., Wu, H., Feng, J. & Jiang, T. (2023). Linking changes in individual specialization and population niche of space use across seasons in the great evening bat (*Ia io*). *Movement Ecology*, **11**, 32. https://doi.org/10.1186/s40462-023-00394-1

Woo, K.J., Elliott, K.H., Davidson, M., Gaston, A.J. & Davoren, G.K. (2008). Individual specialization in diet by a generalist marine predator reflects specialization in foraging behaviour. *Journal of Animal Ecology*, **77**, 1082–1091. https://doi.org/10.1111/j.1365-2656.2008.01429.x

Xing, S., Leahy, L., Ashton, L.A., Kitching, R.L., Bonebrake, T.C. & Scheffers, B.R. (2023). Ecological patterns and processes in the vertical dimension of terrestrial ecosystems. *Journal of Animal Ecology*, **92**, 538–551. https://doi.org/10.1111/1365-2656.13881

## Figure legends

**Figure 1. Separating vertical individuality from horizontal occupancy.** Conceptual workflow showing that repeated differences in horizontal occupancy can generate apparent vertical specialization when terrain or vertical opportunity varies across space. Self and other conditional vertical profiles are therefore integrated under identical self-derived horizontal-cell weights before vertical identity is evaluated.

**Figure 2. Focal repeatable identity and its mechanistic ceiling in *Tadarida teniotis*.** Early individual conditional maps contain strongly repeatable identity information (exact assignment p = 0.000174), whereas a stronger residual cell-by-height stability test after marginal-altitude adjustment is not supported (p = 0.160).

**Figure 3. Horizontally standardized vertical identity across six bat tracking panels.** Points show observed common-cell vertical identity with individual-bootstrap intervals; crosses show panel-specific whole-session permutation-null means. Identity-matched scores exceed exchangeability expectation in all six panels.

**Figure 4. Pairwise vertical self-identification after horizontal standardization.** The y-axis is the equal-individual fraction of direct self-versus-specific-alternative comparisons won by the same individual's vertical profile. Error bars are individual-bootstrap 95% intervals. The dashed 0.5 line is an intuitive reference only and is not a significance threshold.

**Figure 5. Why the original architecture classification was superseded.** Original conditional advantage and common-cell conditional increment are shown for each panel. In *P. hastatus* 2022, the apparent marginal-dominant value changes from -0.120 to +0.0066 after common horizontal weighting, demonstrating that raw conditional-minus-marginal signs cannot be interpreted as biological architecture classes.

**Figure 6. Focal terrain-relative robustness and its limits.** Common-cell AGL identity is shown relative to its panel-specific permutation expectation at 2.5, 5 and 10 km and after fixed night-endpoint neighbourhood exclusions. The predeclared AGL test passes at 2.5 and 5 km but not 10 km; the primary 1-km endpoint-neighbourhood exclusion also fails.

## Ethics statement

This study is a secondary analysis of publicly archived animal-tracking data and involved no new capture, handling or experimental manipulation of animals. The original tracking programmes were conducted under the permits and institutional approvals detailed in Materials and Methods and in the repository's source-ethics provenance ledger. The present analyses use only published tracking measurements and source animal identifiers.

## Data and code availability

All tracking data analysed here are publicly archived in the Movebank Data Repository. The focal *Tadarida teniotis* data are available at DOI 10.5441/001/1.52nn82r9. Independent comparative sources include *Eidolon helvum* (10.5441/001/1.k8n02jn8), *Hypsignathus monstrosus* (10.5441/001/1.278), and *Phyllostomus hastatus* panels archived under 10.5441/001/1.282, 10.5441/001/1.321 and 10.5441/001/1.322. Exact source bitstreams and checksums are recorded in the repository contracts and provenance files.

All analysis code, frozen contracts, source-screen records, calibration history, result summaries and figure-generation scripts are maintained in the public GitHub repository `zuizui0223/batter`. A permanent versioned archive DOI should be minted from the final submission release before journal submission.
