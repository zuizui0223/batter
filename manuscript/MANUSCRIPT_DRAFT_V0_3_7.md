# Manuscript draft v0.3.7

## Working title

**Repeatable vertical identity in bat airspace persists after coarse horizontal occupancy is standardized**

## Abstract

1. Individual differences in vertical space use are well documented, but they can arise because animals repeatedly occupy different horizontal areas or because tracking devices differ in altitude zero point. We asked whether individual identity still predicts vertical use after these alternatives are controlled.

2. We analysed six public three-dimensional bat tracking panels. Same-individual and other-individual vertical profiles were evaluated under identical 5-km horizontal-cell weights and calibrated against whole-session identity permutations. We then removed each session's absolute altitude level by median-centering before vertical binning, which eliminates any additive constant tag/device offset.

3. Identity-matched vertically standardized profiles exceeded panel-specific exchangeability expectations in all six panels. More importantly, all five comparative panels—spanning *Eidolon helvum*, *Hypsignathus monstrosus* and three *Phyllostomus hastatus* datasets—retained calibrated vertical-distribution shape identity after session centering (p=0.0002–0.0076). In the two comparative panels with sufficient outcome-blind stationary support, empirical altitude-offset correction also retained identity (both p=0.0002).

4. The motivating *Tadarida teniotis* dataset marked the principal boundary of inference. Its coarse-horizontal standardized identity was repeatable, but centered-shape identity was not supported (p=0.5121), and a predeclared endpoint-neighbourhood exclusion also failed (p=0.1109). Its repeatable absolute-height component therefore remains inseparable from possible device offset or central-place structure.

5. The strongest ecological result is thus comparative: in five panels, individual bats differ repeatably in the shape of their vertical distributions beyond coarse horizontal occupancy and additive altitude zero point. A second general lesson is methodological: individuality scores from finite prediction pipelines require pipeline-specific exchangeability calibration rather than assumed zero or 0.5 nulls.

**Keywords:** bats; individual specialization; movement ecology; non-exchangeability; three-dimensional movement; vertical niche; vertical space use

## Introduction

Individual specialization means that a population niche can be a mixture of non-exchangeable individuals rather than a single strategy shared by all members of a population (Bolnick et al. 2003). In movement ecology, this heterogeneity is familiar in home ranges, routes, habitat use and foraging locations. Bats likewise show repeated individual differences in horizontal space use, with the degree of specialization varying among ecological contexts and seasons (Kerches-Rogeri et al. 2020; Wang et al. 2023). Such differences matter because population-level movement surfaces are often interpreted as if they describe an interchangeable representative individual.

Animals also partition space vertically. Repeatable individual differences in dive depth, flight altitude and three-dimensional foraging habitat are already known in seabirds, marine mammals and aerial vertebrates (Woo et al. 2008; Ratcliffe et al. 2013; McIntyre et al. 2017; Dreelin et al. 2018). The novelty problem is therefore not whether vertical individuality exists. It is whether apparent vertical individuality remains when alternative explanations tied to where an animal moves, or how its device measures altitude, are removed.

Two confounds are especially important. First, horizontal fidelity can generate a repeatable height distribution when animals repeatedly use ridges, valleys, bathymetric patches, commuting corridors or central-place approaches with characteristic vertical opportunity. Ratcliffe et al. (2013), for example, noted that individual dive-depth specialization can arise through repeated use of patches with different water depths. The airborne analogue is direct: terrain and route choice can convert horizontal fidelity into apparent altitude identity. Second, GPS altitude can contain device-specific offsets. If one animal repeatedly carries one tag, a stable altitude zero point can be mistaken for a stable individual mean height. These problems motivate a stricter counterfactual: **when individuals are compared under the same coarse horizontal occupancy, and when additive altitude level is removed, does identity still predict the shape of vertical use?**

We test this counterfactual with held-out prediction. For each target session, vertical use learned from other sessions of the same individual is compared with profiles learned from conspecifics. Self and other profiles are integrated under identical horizontal-cell weights, so differences in occupancy among the tested 5-km cells cannot by themselves create the comparison. We then judge the resulting identity score against whole-session label permutations that preserve within-session x-y-z structure, sample size and horizontal coverage. This calibration is necessary because finite training data, smoothing and eligibility filters can shift a prediction statistic's exchangeability expectation away from intuitive values such as zero or 0.5.

The study was motivated by European free-tailed bats, *Tadarida teniotis*, whose source study linked high-altitude flight to topography and nocturnal uplift (O'Mara et al. 2021). That dataset first revealed strong repeatable individual identity but also supplied several cautionary results, including failure of a stronger stable cell-by-height residual map. We therefore treat *Tadarida* as the motivating and boundary case rather than the centre of the comparative claim. The main comparative test uses five additional panels from three taxa—*Eidolon helvum*, *Hypsignathus monstrosus* and *Phyllostomus hastatus*—selected through a previously closed, outcome-blind public-data screen. This design reduces the opportunity to keep adding favourable examples after results are known.

The analysis history also imposed an important methodological correction. An initial conditional-versus-marginal decomposition appeared to divide panels into different predictive architectures, but a frozen estimator audit showed that its finite-sample null was negative and that the ordinary marginal score inherited horizontal occupancy differences. We therefore replaced that classification with common-cell horizontal standardization and panel-specific permutation calibration, retained failed robustness tests, and froze each later audit before opening its outcome. The full amendment sequence is documented in Supporting Information rather than repeated here.

Our primary ecological question is whether repeatable vertical identity persists beyond coarse horizontal occupancy in the comparative panels. We then ask whether that signal survives removal of any additive altitude zero point by translating each retained session to zero median before vertical binning. Secondary checks quantify endpoint-neighbourhood robustness, stationary-height correction where an outcome-blind support gate permits it, and temporal overlap among tracked individuals. Together these tests distinguish a cross-panel result about vertical-distribution shape from the more limited motivating *Tadarida* result, while preserving explicit limits from central-place structure, temporal context and unmeasured device error.

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

To translate the result into an intuitive biological magnitude, we froze a separate pairwise analysis before opening its output. For each held-out target session and each specific alternative individual within the same cohort, we compared the same-bat and alternative-bat vertical profiles using identical self-derived horizontal cell weights. A self win occurred when the target's mean log probability was higher under the same individual's profile.

Alternative comparisons were averaged within target session, sessions were averaged within biological individual across admitted cohorts, and individuals were weighted equally. We report the equal-individual self-win fraction and a 20,000-replicate individual-bootstrap percentile interval.

Because the prediction pipeline itself can shift the exchangeability baseline away from 0.5, we subsequently froze a null-calibration family before opening any pairwise-null output. For each panel, the entire pairwise statistic was recomputed under the same whole-session label-permutation design, permutation count and seed already used for that panel's estimator calibration. We report the observed self-win fraction, panel-specific permutation-null mean, observed-minus-null excess and one-sided P(null >= observed). A 0.5 line is retained only as an intuitive visual reference.

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

Within each retained BatDay, the first five and last five finite projected fixes were selected using timestamps only. These endpoint fixes were pooled within individual, and the observed endpoint minimizing summed Euclidean distance to all other pooled endpoints was selected as that individual's proxy centre. The primary analysis removed every event strictly within 1,000 m of its own individual's proxy, symmetrically from training and target data. Sessions retained their original identities but had to contain at least 50 remaining events. Fixed descriptive radii of 500 and 2,000 m were also frozen. The focal primary endpoint was calibrated common-cell AGL identity, not the conditional increment.

After the focal 1-km test failed, we froze a separate cross-panel endpoint-exclusion contract before opening any non-*Tadarida* exclusion output. The same first-five/last-five x-y/time-only logic was applied within each originally admitted cohort and individual, using each cohort's already-frozen UTM projection. The 1-km radius was the sole primary radius; 500 m and 2,000 m were descriptive sensitivities only. Sessions falling below 50 remaining numeric-scored events were removed, no new cohorts were admitted, and the 5-km common-cell marginal identity was recalibrated by whole-surviving-session label permutations within cohort. Panel-specific minimum evaluable-individual gates were frozen in advance.

### Biological-scale translation in focal *Tadarida*

For focal AGL only, we calculated an expected-height separation in metres. Within common supported cells, self training-session cell means were averaged equally across self sessions and other-individual cell means were averaged equally across other individuals. Both were then integrated under identical self cell-use weights. For each target session we recorded the absolute difference between the self and other expected AGL; sessions were averaged within individuals and individuals equally. This is a mean-height translation and does not capture distribution-shape differences.

Absolute separation is positive even under exchangeability. We therefore froze a second effect-null calibration before opening its output and recomputed the full metre-scale statistic under the exact focal AGL whole-session label-permutation design (9,999 permutations; the previously frozen AGL seed). We report the raw separation, permutation-null mean, calibrated excess and one-sided upper-tail probability.

### Additive tag/device altitude-bias audit

GPS altitude can contain device-specific additive offsets, so a stable tag zero point could mimic repeatable individual vertical location. We therefore froze one final audit before output and declared it the stopping point for new scientific analyses.

For the primary test, each retained session was translated to zero median before vertical binning, using fixed residual-height edges of -∞, -400, -200, -100, -50, 0, 50, 100, 200, 400 and +∞ m. Horizontal cells, cohort definitions, weighting, scoring thresholds and whole-session permutations were unchanged. This removes any additive constant tag/device offset, as well as session-specific constant height shifts. Panels had to retain their original evaluable-individual counts; support required positive observed-minus-null common-cell shape identity and one-sided P(null >= observed) <=0.05.

A separate x-y/time-only preflight defined stationary candidates by both adjacent gaps <=20 min and both adjacent horizontal speeds <=0.5 m/s. Shared 100-m cells required at least three individuals with >=5 candidate fixes each; supported individuals required >=10 candidate fixes. Stationary correction was allowed only when supported individuals numbered at least max(5, ceil(0.5 × original evaluable n)) and an admitted cohort retained >=3 supported repeat individuals. Only *Hypsignathus monstrosus* and *Phyllostomus hastatus* 2016 passed this gate.

For those panels, individual-by-cohort offsets were estimated relative to the median individual height in each shared stationary cell, subtracted from all primary-height observations, and the original vertical bins and 5-km calibration were rerun. This correction was corroborative only. The same preflight summarized tracking-window overlap descriptively; no time-block permutation family was opened.

### Source-study ethics

This study conducted no new capture, handling or instrumentation. The focal *T. teniotis* source study reports ICNF Portugal permit 665/2017/CAPT (O'Mara et al. 2021). The *E. helvum* programme reports approvals from relevant wildlife and veterinary authorities in Ghana, Zambia and Burkina Faso (O'Mara et al. 2019). The *H. monstrosus* study reports approval by the Ministry of Agriculture, Livestock and Fisheries of the Republic of Congo and the VetAgro Sup ethics committee, approval 1805-V2 (Schloesing et al. 2023). The *P. hastatus* programmes report Ministerio del Ambiente Panamá permits and Smithsonian Tropical Research Institute Animal Care and Use Committee approvals detailed in the source papers (O'Mara & Dechmann 2023; Calderón-Capote et al. 2024). Full source-by-source permit provenance is archived with the analysis.

## Results

### A closed public-data screen yielded six repeated 3-D bat panels

The outcome-blind source screen considered 23 Movebank parent bat datasets and admitted six sources spanning four taxa. The six paper panels were *Tadarida teniotis*, *Eidolon helvum*, *Hypsignathus monstrosus*, and three temporal *Phyllostomus hastatus* datasets. The source universe was closed before estimator calibration and was not expanded after comparative outcomes were observed.

### Five comparative panels retain vertical-distribution shape after absolute altitude level is removed

The strongest ecological result came from the five comparative panels. Median-centering every retained session removed absolute vertical location before vertical binning and therefore removed any additive constant tag/device altitude offset. All five comparative panels nevertheless retained calibrated common-cell identity in vertical-distribution shape (Figure 5).

*E. helvum* retained observed centered identity +0.372 nats/fix versus a null mean of -0.071 (calibrated excess +0.443; p=0.0002). *H. monstrosus* retained +0.074 versus -0.103 (+0.177; p=0.0002). *P. hastatus* 2022 retained -0.039 versus -0.151 (+0.111; p=0.0002), the 2023 panel +0.045 versus -0.073 (+0.118; p=0.0002), and the 2016 panel -0.008 versus -0.582 (+0.574; p=0.0076).

The motivating *T. teniotis* panel was the exception: observed centered-shape identity was -0.263 versus a null mean of -0.241 (calibrated excess -0.022; p=0.5121). Thus the cross-panel result falls in the predeclared 5/6-PASS category. Additive altitude zero-point differences cannot explain the comparative five-panel pattern, whereas the absolute vertical-location component in *Tadarida* remains inseparable from biological mean-height differences, device offset, or both.

### Coarse-horizontal standardized identity exceeds exchangeability expectations in all six panels

Before altitude centering, the identity-matched common-cell vertical score exceeded the panel-specific session-label permutation expectation in every panel after self and other profiles were integrated under identical 5-km horizontal weights (Figure 2).

Observed-minus-null common-cell identity was +0.602 nats/fix in *T. teniotis* (p=0.0005), +0.265 in *E. helvum* (p=0.0002), +0.076 in *H. monstrosus* (p=0.0002), +0.200 in *P. hastatus* 2022 (p=0.0002), +0.120 in *P. hastatus* 2023 (p=0.0002), and +0.270 in *P. hastatus* 2016 (p=0.0422). The 2016 panel had a raw common-cell score near zero (-0.0039), but its exchangeability expectation was substantially lower (-0.274). The relevant result is therefore identity matching relative to the finite-sample prediction-pipeline null, not positivity relative to zero.

### Stationary-height correction corroborates the two structurally eligible comparative panels

The x-y/time-only preflight permitted empirical stationary-height correction only in *H. monstrosus* and *P. hastatus* 2016. In *H. monstrosus*, offsets were estimated for 12 individuals, 10 remained evaluable after correction, and the median absolute offset was 4.64 m; corrected identity retained calibrated excess +0.0671 (p=0.0002). In *P. hastatus* 2016, 11 offsets were estimated, seven remained evaluable, and the median absolute offset was 2.00 m; calibrated excess was +0.3808 (p=0.0002).

Thus both structurally eligible comparative panels retained identity after empirical offset correction. Shared stationary 100-m cells are calibration locations rather than verified equal-height roost or perch references, so this analysis is corroborative rather than a universal device calibration.

### Endpoint-neighbourhood exclusion is robust in four comparative panels but not universal

Four of five comparative panels passed the predeclared 1-km endpoint-neighbourhood exclusion (Figure 4). *H. monstrosus* retained calibrated excess +0.308 (p=0.0002; n=19), *P. hastatus* 2022 +0.219 (p=0.0002; n=30), the 2023 panel +0.152 (p=0.0002; n=12), and the 2016 panel +0.358 (p=0.0002; n=10).

*E. helvum* retained a strong signal after exclusion (calibrated excess +0.390; p=0.0002) but fell to 11 evaluable individuals, below the frozen minimum of 15, and therefore failed the predeclared gate. The motivating *Tadarida* panel also failed its corresponding 1-km inferential criterion (p=0.1109). Endpoint-associated structure therefore does not generally erase the comparative signal, but it is not universally excluded.

### Pairwise self-identification exceeds its pipeline-specific null in five panels

Direct same-individual versus specific-alternative comparisons gave an intuitive translation of the common-cell result (Figure 3). The same individual's profile won 0.794 of comparisons in *T. teniotis* versus a null mean of 0.508 (calibrated excess +0.286; p=0.0189), 0.858 in *E. helvum* versus 0.583 (+0.275; p=0.0002), 0.767 in *H. monstrosus* versus 0.541 (+0.226; p=0.0002), 0.842 in *P. hastatus* 2022 versus 0.532 (+0.310; p=0.0002), and 0.782 in the 2023 panel versus 0.535 (+0.247; p=0.0002).

The 2016 *P. hastatus* panel did not retain independent pairwise support: observed self-win was 0.594 versus a null mean of 0.498 (calibrated excess +0.096; p=0.1168). Across panels, pairwise null means ranged from 0.498 to 0.583, showing that 0.5 is an intuitive reference rather than a universal exchangeability null.

### Tracking windows overlap strongly in five panels but less in the 2016 panel

Positive overlap among repeat-individual tracking windows was 71.4% in *Tadarida*, 86.0% in *Eidolon*, 91.7% in *Hypsignathus*, 76.6% in *P. hastatus* 2022, 100% in 2023 and 31.1% in 2016. The 2016 panel also had a median start-date difference of 4.0 d, leaving the strongest residual individual-versus-time limitation in that dataset.

### *Tadarida* is a motivating boundary case rather than the comparative template

The motivating *T. teniotis* dataset contains repeatable individual information but repeatedly defines the claim ceiling. Its earlier early/late assignment test strongly rejected individual exchangeability (diagonal gain +0.1682 nats/event; exact p=0.000174), whereas a stronger residual cell-by-height stability test failed (p=0.160; Supporting Figure S1).

Terrain-relative AGL identity remained supported at 5 km (calibrated +0.446; p=0.0161) and 2.5 km (+0.712; p=0.011), but not at 10 km (+0.237; p=0.1018). The 1-km endpoint-neighbourhood exclusion also failed (p=0.1109), and session-centering eliminated calibrated shape identity (p=0.5121).

The raw common-cell AGL separation averaged 256.459 m, compared with a session-label null mean of 133.733 m (calibrated excess 122.727 m; p=0.0297). Because centered-shape identity failed, we treat this metre-scale quantity only as a descriptive translation of repeatable absolute vertical location, which can contain genuine biological mean-height differences, additive device bias, or both.

### Pipeline calibration changed the inferential baseline

The estimator audit altered interpretation rather than merely changing p-values. The original conditional-minus-marginal contrast had a negative panel-specific exchangeability expectation, and the ordinary marginal score inherited horizontal occupancy differences. Most visibly, *P. hastatus* 2022 changed from an apparent marginal-dominant value of G_adv = -0.120 to a common-cell conditional increment of approximately +0.0066 after horizontal standardization (Supporting Figure S2).

The same principle appeared in the biological translations: pairwise null means ranged from 0.498 to 0.583 rather than being fixed at 0.5, and the focal absolute AGL separation had a positive null mean rather than zero. These results motivate pipeline-specific exchangeability calibration as a general methodological conclusion.

## Discussion

### Comparative vertical-distribution shape persists beyond coarse horizontal occupancy and additive altitude level

The clearest ecological result is comparative. All five non-*Tadarida* panels retained calibrated identity in vertical-distribution shape after self and other profiles were standardized to the same coarse horizontal occupancy and every session was translated to zero median. The result spans *Eidolon helvum*, *Hypsignathus monstrosus* and three *Phyllostomus hastatus* datasets. It therefore goes beyond the already established observation that individuals can differ in flight altitude, dive depth or three-dimensional habitat use: in these five panels, identity persists after two simpler alternatives—different coarse horizontal occupancy and additive altitude zero point—are removed.

This distinction matters for population movement niches. A broad three-dimensional population distribution can arise because each animal is individually broad, because individuals occupy different horizontal places, or because individuals retain distinctive vertical distributions within comparable horizontal opportunity. The comparative results support the third component. Population-level vertical structure therefore need not describe an exchangeable representative individual.

The stationary correction provides narrower but concordant evidence. Both comparative panels that passed the outcome-blind support gate retained identity after estimated individual-by-cohort altitude offsets were removed. Because four panels lacked sufficient shared stationary support, this is corroboration rather than a universal calibration.

### Pipeline-specific nulls are part of the biological inference

The second major result is methodological. Prediction-based individuality statistics did not share universal intuitive nulls. The original conditional-minus-marginal contrast had a negative panel-specific expectation, pairwise self-identification nulls ranged from about 0.50 to 0.58, and an absolute height-separation statistic had a positive null mean rather than zero.

These shifts arise from finite training structure, smoothing, eligibility rules, repeated-session geometry and transformations such as absolute differences. Consequently, a raw score of zero, a pairwise rate of 0.5 or an absolute separation of zero should not automatically be treated as the inferential baseline. Recomputing the complete statistic under biologically appropriate label exchangeability changed one qualitative architecture interpretation and removed one weak pairwise translation without requiring post hoc retuning. The detailed amendment sequence is retained in Supporting Information.

This is more than a technical correction. The baseline determines which apparent ecological differences can be attributed to individual identity rather than to the geometry of the estimator itself.

### Horizontal and central-place structure are reduced, not eliminated

Common-cell weighting removes differences in occupancy among the tested 5-km cells, but it does not force individuals to share identical continuous x-y positions. Fine-scale fidelity within a cell can therefore still translate into vertical differences through terrain, resources or central-place routes.

The endpoint-neighbourhood audit narrows this concern. Four comparative panels retain calibrated identity after the same fixed 1-km exclusion, and *Eidolon* retains a strong signal but fails the frozen post-exclusion sample-size gate. Endpoint-associated structure is therefore not a sufficient general explanation for the comparative result. At the same time, the failure in *Tadarida* and the lack of verified roost, colony or lek coordinates prevent a universal claim of central-place independence.

We therefore describe the result as vertical individuality beyond **coarse-grained horizontal occupancy at the tested 5-km scale**, not as complete removal of horizontal fidelity.

### Additive tag offsets are not a general explanation, but other device error remains possible

Session centering removes every additive altitude zero-point difference without requiring knowledge of the device-specific error. The persistence of calibrated shape identity in all five comparative panels therefore rules out a constant tag offset as a general explanation for those results.

The audit is not a proof against every form of measurement error. Tag-specific differences in altitude-error variance, antenna orientation, reception quality or other state-dependent error could in principle broaden or narrow an individual's apparent vertical distribution. Tracking windows overlap strongly in most panels, so many animals shared broad atmospheric and satellite contexts, but heteroscedastic device error remains unresolved. Future prospective work should therefore include repeated device calibration or tag-swapping designs where feasible.

### *Tadarida* defines the boundary of the current evidence

The motivating *Tadarida* dataset is informative precisely because it does not reproduce the strongest comparative result. Its identity signal is repeatable, persists in AGL at 2.5–5 km, and is not reducible to terrain elevation alone. Yet it fails the 10-km grain test, the endpoint-neighbourhood exclusion and the shift-invariant centered-shape test. The archived data therefore support repeatable absolute vertical-location identity in this system, but not device-independent vertical-distribution shape.

This distinction also changes how the focal 256-m AGL translation should be read. Although the raw separation exceeds its own finite-sample null, it is not independent biological evidence once centered-shape identity fails. Genuine mean flight-height specialization and additive device offset remain inseparable in this panel.

The stronger residual cell-by-height test also remains negative, so repeatable identity should not be interpreted as one rigid three-dimensional route map. Morphology, resource use, atmospheric response, social routines and learned spatial histories remain plausible mechanisms rather than demonstrated causes.

### Comparative generality is encouraging but still limited

The admitted panels span four taxa, multiple regions and several tracking programmes, and the public-data source universe was closed before calibration. That consistency reduces the chance that the comparative pattern was created by repeatedly adding favourable examples.

Nevertheless, this is not a phylogenetic comparative study. Only four taxa passed the fixed data gate, vertical datums differ among source programmes, and harmonized AGL was available only for *Tadarida*. We therefore compare within-panel predictive identity rather than absolute altitude among taxa.

Temporal comparability is also uneven. Repeat-individual tracking windows overlap strongly in five panels but only 31.1% of pairs in *P. hastatus* 2016. Stable short-term weather or seasonal context could therefore contribute to identity in that panel. Behavioural state is another limitation: no harmonized classifier was imposed across studies, so we refer to vertical airspace or flight use rather than foraging-height specialization. Observational repeatability also does not establish personality, learning, adaptation or optimality.

### A prospective test of vertical individuality

The next decisive study should track the same individuals repeatedly with harmonized terrain-relative altitude, known roost locations, high-frequency horizontal positions, simultaneous atmospheric measurements and explicit device calibration. Fine horizontal matched strata could then test whether an individual's vertical distribution predicts held-out nights when horizontal opportunity is nearly identical.

Tag swapping or repeated calibration against common stationary references would help separate biological distribution shape from device-specific variance. Repeating the design across seasons would distinguish persistent identity from temporal context, while behavioural-state classification could separate commuting, foraging and departure/arrival phases.

Such a design would move beyond the present result—repeatable comparative vertical-distribution shape after coarse horizontal and additive-offset controls—to the stronger mechanistic question of which traits or experiences generate that individuality.

## Conclusion

Individual bats are not fully exchangeable in the vertical dimension of their movement. Across six tracking panels from four taxa, correct individual identity retained more information about held-out vertical state than expected under session-level exchangeability after self and other profiles were evaluated under the same coarse 5-km horizontal occupancy weights.

A fixed endpoint-neighbourhood audit shows that central-place-associated structure is not a general explanation but remains a panel-dependent contributor. The final device-bias audit further narrows the result: after every retained session was translated to zero median, five of six panels still retained calibrated individual identity in vertical-distribution shape. Constant additive tag/device altitude offsets therefore cannot explain the cross-panel pattern generally.

Focal *Tadarida* is the explicit exception. Its identity signal does not survive removal of absolute altitude level, so its repeatable vertical-location component remains inseparable from possible additive device bias. The previously reported 256-m AGL translation is consequently descriptive rather than independent biological evidence.

In the two panels with sufficient outcome-blind stationary support, empirical altitude-offset correction also retained calibrated identity. Tracking-window overlap is substantial in most panels but weaker in the 2016 *Phyllostomus* panel, leaving temporal context as a residual limitation.

The ecological conclusion is therefore bounded but substantive: **repeatable individual structure in bat vertical use persists beyond coarse horizontal occupancy and, in five systems, beyond additive altitude zero point.** More broadly, prediction-based tests of individuality should calibrate the complete analysis pipeline under biologically appropriate exchangeability rather than assume intuitive null values.

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

**Figure 2. Horizontally standardized vertical identity across six bat tracking panels.** Points show observed common-cell vertical identity with individual-bootstrap intervals; crosses show panel-specific whole-session permutation-null means. Identity-matched scores exceed exchangeability expectation in all six panels.

**Figure 3. Pairwise vertical self-identification after coarse horizontal standardization.** The y-axis is the equal-individual fraction of direct self-versus-specific-alternative comparisons won by the same individual's vertical profile. Error bars are individual-bootstrap 95% intervals. Panel-specific whole-session permutation-null means are the inferential baselines; a 0.5 line, if shown, is an intuitive reference only. Five panels exceed their calibrated pairwise null, whereas *P. hastatus* 2016 does not.

**Figure 4. Endpoint-neighbourhood robustness across six bat tracking panels.** Points show common-cell vertical identity remaining after the predeclared 1-km endpoint-neighbourhood exclusion; crosses show corresponding whole-session permutation-null means. Four comparative panels pass the frozen rule. *Eidolon* retains a strong calibrated signal but fails the minimum-evaluable-individual gate, while *Tadarida* fails its inferential tail criterion.

**Figure 5. Shift-invariant vertical-distribution identity after removal of absolute altitude level.** Every retained session was median-centered before vertical binning, so any additive constant tag/device altitude offset was removed exactly. All five comparative panels exceed their calibrated null; the motivating *Tadarida teniotis* panel does not (p=0.5121).

### Supporting figure legends

**Supporting Figure S1. Motivating *Tadarida teniotis* repeatable identity and mechanistic ceiling.** Early individual conditional maps contain strongly repeatable identity information (exact assignment p=0.000174), whereas a stronger residual cell-by-height stability test after marginal-altitude adjustment is not supported (p=0.160).

**Supporting Figure S2. Why the original architecture classification was superseded.** Original conditional advantage and common-cell conditional increment are shown for each panel. In *P. hastatus* 2022, the apparent marginal-dominant value changes from -0.120 to +0.0066 after common horizontal weighting, demonstrating that raw conditional-minus-marginal signs cannot be interpreted as biological architecture classes.

## Ethics statement

This study is a secondary analysis of publicly archived animal-tracking data and involved no new capture, handling or experimental manipulation of animals. The original tracking programmes were conducted under the permits and institutional approvals detailed in Materials and Methods and in the repository's source-ethics provenance ledger. The present analyses use only published tracking measurements and source animal identifiers.

## Data and code availability

All tracking data analysed here are publicly archived in the Movebank Data Repository. The focal *Tadarida teniotis* data are available at DOI 10.5441/001/1.52nn82r9. Independent comparative sources include *Eidolon helvum* (10.5441/001/1.k8n02jn8), *Hypsignathus monstrosus* (10.5441/001/1.278), and *Phyllostomus hastatus* panels archived under 10.5441/001/1.282, 10.5441/001/1.321 and 10.5441/001/1.322. Exact source bitstreams and checksums are recorded in the repository contracts and provenance files.

All analysis code, frozen contracts, source-screen records, calibration history, result summaries and figure-generation scripts are maintained in the public GitHub repository `zuizui0223/batter`. A permanent versioned archive DOI should be minted from the final submission release before journal submission.

