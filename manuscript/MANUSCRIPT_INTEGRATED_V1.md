# Integrated manuscript draft v1

## Working title

**Repeatable vertical individuality in bats persists beyond horizontal occupancy but varies among ecological systems**

## Abstract

1. Apparent individual differences in vertical space use can arise from stable behaviour, but also from repeated horizontal-area use, terrain or device-specific altitude reference. We asked whether individual identity predicts the organization of vertical use after these alternatives are reduced, and whether the phenomenon is general across bat systems.

2. We analysed a closed archive of six public three-dimensional bat tracking panels. Same- and other-individual vertical profiles were evaluated under identical 5-km horizontal-cell weights and whole-session identity permutations, then session-median centered to remove absolute altitude level. Pre-specified secondary stress tests localized broad place, movement-state and temporal explanations. Four external source systems were evaluated under source-specific designs fixed before their vertical outcomes were examined, and a post-outcome terrain audit was specified before digital-elevation values were decoded for the only external source meeting its primary criterion.

3. Centered vertical-distribution shape identity was supported in all five original comparative panels but not in the motivating *Tadarida teniotis* boundary case. Where present, it survived broad movement-state, 250–500-m place × state and multi-day stress tests where structurally evaluable. Externally, *Nyctalus noctula*, *Hipposideros armiger/pratti* and *Myotis vivesi* did not meet their pre-specified primary criteria, whereas *Pteropus poliocephalus* met the criterion under a separate four-individual design fixed before either admitted vertical outcome was examined (n=4; calibrated excess +0.169).

4. In *Pteropus*, subtracting DEM terrain reduced the calibrated excess to +0.032, but the terrain-adjusted endpoint remained above its pre-specified permutation null (p=0.0023); terrain use itself was individually repeatable (+0.379, p=0.0034). Thus the MSL-scale result was strongly terrain-sensitive, yet sampled terrain did not fully account for the retained terrain-relative signal. The external sources are not a prevalence sample.

5. The opened systems generate, rather than confirm, a falsifiable ecological hypothesis: stable centered vertical individuality should be strongest where animals repeatedly solve vertically structured foraging problems around persistent spatial resources, and weaker where prey is mobile or feeding is constrained near a surface. More generally, the expression of individual specialization may depend on ecological opportunity as well as individual attributes.

**Keywords:** bats; ecological opportunity; individual specialization; movement ecology; non-exchangeability; three-dimensional movement; vertical space use

## Introduction

Individual specialization means that a population niche can be a mixture of non-exchangeable individuals rather than a single strategy shared by all members of a population (Bolnick et al. 2003). In movement ecology, this heterogeneity is familiar in home ranges, routes, habitat use and foraging locations. Bats likewise show repeated individual differences in horizontal space use, with the degree of specialization varying among ecological contexts and seasons (Kerches-Rogeri et al. 2020; Wang et al. 2023). Such differences matter because population-level movement surfaces are often interpreted as if they describe an interchangeable representative individual.

Animals also partition space vertically, and vertical gradients can structure terrestrial niches and ecological processes (Gámez & Harris 2022; Xing et al. 2023). Repeatable individual differences in dive depth, flight altitude and three-dimensional foraging habitat are already known in seabirds, marine mammals and aerial vertebrates (Woo et al. 2008; Ratcliffe et al. 2013; McIntyre et al. 2017; Dreelin et al. 2018). The novelty problem is therefore not whether vertical individuality exists. It is whether apparent vertical individuality remains when alternative explanations tied to where an animal moves, or how its device measures altitude, are removed.

Two confounds are especially important. First, horizontal fidelity can generate a repeatable height distribution when animals repeatedly use ridges, valleys, bathymetric patches, commuting corridors or central-place approaches with characteristic vertical opportunity. Ratcliffe et al. (2013), for example, noted that individual dive-depth specialization can arise through repeated use of patches with different water depths. The airborne analogue is direct: terrain and route choice can convert horizontal fidelity into apparent altitude identity. Second, GPS altitude can contain device-specific offsets. If one animal repeatedly carries one tag, a stable altitude zero point can be mistaken for a stable individual mean height. These problems motivate a stricter counterfactual: **when individuals are compared under the same coarse horizontal occupancy, and when additive altitude level is removed, does identity still predict the shape of vertical use?**

We test this counterfactual with held-out prediction. For each target session, vertical use learned from other sessions of the same individual is compared with profiles learned from conspecifics. Self and other profiles are integrated under identical horizontal-cell weights, so differences in occupancy among the tested 5-km cells cannot by themselves create the comparison. We then judge the resulting identity score against whole-session label permutations that preserve within-session x-y-z structure, sample size and horizontal coverage. This calibration is necessary because finite training data, smoothing and eligibility filters can shift a prediction statistic's exchangeability expectation away from intuitive values such as zero or 0.5.

The study was motivated by European free-tailed bats, *Tadarida teniotis*, whose source study linked high-altitude flight to topography and nocturnal uplift (O'Mara et al. 2021). That dataset first revealed strong repeatable individual identity but also supplied several cautionary results, including failure of a stronger stable cell-by-height residual map. We therefore treat *Tadarida* as the motivating and boundary case rather than the centre of the comparative claim. The main comparative test uses five additional panels from three taxa—*Eidolon helvum*, *Hypsignathus monstrosus* and *Phyllostomus hastatus*—selected through a previously closed, outcome-blind public-data screen. This design reduces the opportunity to keep adding favourable examples after results are known.

The analysis history also imposed an important methodological correction. An initial conditional-versus-marginal decomposition appeared to divide panels into different predictive architectures, but an estimator audit specified before its output was examined showed that its finite-sample null was negative and that the ordinary marginal score inherited horizontal occupancy differences. We therefore replaced that classification with common-cell horizontal standardization and panel-specific permutation calibration, retained robustness tests that did not meet their pre-specified criteria, and specified each later audit before examining its outcome. The full amendment sequence is documented in Supporting Information rather than repeated here.

Our primary ecological question is not simply whether individuals occupy different mean heights, but whether individual identity predicts the **organization of vertical space use**: how probability is distributed among vertical states around an individual's session-specific typical altitude. We first ask whether repeatable vertical identity persists after self and other profiles are evaluated under the same coarse horizontal occupancy. We then ask whether identity still predicts the centered distribution after each session is translated to zero median, removing any additive altitude level. Secondary checks quantify endpoint-neighbourhood robustness, stationary-height correction where an outcome-blind support gate permits it, and temporal overlap among tracked individuals. Together these tests distinguish repeatable organization of vertical use from simple horizontal fidelity or absolute-height differences while preserving explicit limits from central-place structure, temporal context and unmeasured device error.

The closed comparative archive addresses whether vertical individuality can survive obvious spatial and measurement alternatives, but it does not by itself establish that the phenomenon is universal. This distinction matters biologically. Stable individual differences can only be expressed along dimensions for which an ecological task repeatedly offers alternative solutions. A vertically complex, spatially persistent resource landscape may permit repeatable individual approach heights, canopy layers or route geometries, whereas mobile prey, rapidly changing atmospheric forcing, or feeding constrained near a surface may reduce such repeatable vertical choice. These possibilities turn external failures from mere non-replications into information about the ecological boundary of the phenomenon.

We therefore organize the study around two linked questions. First, does individual identity predict the organization of vertical space use after coarse horizontal occupancy and additive altitude level are removed, and does that signal persist after broad place, movement-state and temporal matching? Second, when the same centered-shape endpoint is taken to independent external bat systems under pre-specified designs, is the phenomenon recurrent or universal? The ecological contrasts among already-opened positive and negative systems were not specified before those outcomes were known. We consequently treat them only as post-hoc hypothesis generation and reserve causal language for future outcome-blind comparative tests. The four-stage inference structure is summarized in Figure 1.

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

For the focal panel, the calibration design was specified before the focal calibration output was examined. Whole retained session blocks were assigned permuted individual labels while preserving all x-y-z observations within each session, session sizes, horizontal coverage, and the original multiset of session counts assigned to individual labels. We ran 9,999 Monte Carlo permutations using a fixed PCG64 seed.

The focal result established that the pipeline null was materially negative. Before opening any non-*Tadarida* calibration output, we specified one common calibration design for the five remaining panels. Those permutations were conducted within each admitted cohort, retaining cohort membership and the exact number of sessions assigned to each label within that cohort. Each non-focal panel used 4,999 Monte Carlo permutations with pre-specified seeds.

For each panel we report the observed common-cell score, the permutation-null mean and quantiles, the null-centered difference G_cc - mean(null), and the one-sided Monte Carlo tail probability P(null >= observed). The inferential statement is identity matching relative to this panel-specific finite-sample exchangeability distribution, not significance relative to zero.



### Independent comparative panels

For *Eidolon helvum* (O'Mara et al. 2019; Movebank DOI 10.5441/001/1.k8n02jn8), 63 animals had horizontal and vertical presence and 42 had repeated structurally eligible sessions before numeric height was opened. The native vertical field was ellipsoid height. Analyses were stratified within exact study-site × shifted-night-year cohorts.

For *Hypsignathus monstrosus* (Schloesing et al. 2023; DOI 10.5441/001/1.278), 32 animals passed structural presence screening and 24 had repeated eligible sessions. The primary admitted context was Lek Njoukou in 2020; the native vertical field was ellipsoid height.

For *Phyllostomus hastatus*, three source datasets had already been assigned distinct prospective roles before the calibration audit: a 2021–2022 panel (Calderón-Capote et al. 2024; DOI 10.5441/001/1.321), a 2023 temporal panel (DOI 10.5441/001/1.322), and an untouched 2016 panel from DOI 10.5441/001/1.282. The 2022 and 2016 primary vertical coordinates were MSL, whereas the 2023 source used ellipsoid height. We therefore compare predictive information within each panel and do not compare absolute flight heights among taxa or years with different vertical reference systems.









### Additive tag/device altitude-bias audit

To remove additive altitude zero-point differences, each retained session was translated to zero median before vertical binning using fixed residual-height edges of -∞, -400, -200, -100, -50, 0, 50, 100, 200, 400 and +∞ m. Horizontal cells, cohort definitions, weighting, target-support thresholds and whole-session permutations were unchanged. Support required positive observed-minus-null common-cell shape identity and one-sided P(null >= observed) <=0.05 while retaining the original evaluable-individual count.

A separately pre-specified stationary-height correction was allowed only where an x-y/time-only preflight found adequate shared 100-m support. Only *Hypsignathus monstrosus* and *Phyllostomus hastatus* 2016 passed that gate. Full stationary-support rules, tracking-window summaries and correction details are in Supporting Information.

### Supporting robustness and historical estimator analyses

Historical conditional/marginal estimators, pairwise self-identification, focal early/late and AGL analyses, endpoint-neighbourhood exclusion, biological-scale translation, and descriptive individual-profile reconstruction are reported in Supporting Information. These analyses are retained for transparency and robustness but do not replace the session-centered common-cell primary endpoint.

### Sequential mechanism-localization analyses

After the original six-panel centered-shape result family had been established, we ran a sequence of secondary mechanism-localization analyses. Each individual analysis was specified before its output was examined, but the family as a whole was outcome-informed and is therefore treated as stress-test evidence rather than independent confirmation. We asked whether centered identity remained after conditioning on horizontal speed, speed × turning state, and place × state at progressively finer horizontal grains. Structural support determined which panels could be evaluated at 2 km, 500 m and 250 m; a common 100-m test was not supportable. Separate pre-specified analyses required self-training observations to precede target observations by at least 1, 3 or 7 days. These analyses retained the original individual as the biological summary unit and the panel-specific whole-session exchangeability logic.

### Prospective external validation programmes

External tests were kept chronologically distinct rather than pooled as one prevalence sample. The first pre-specified external primary used the public *Nyctalus noctula* source associated with Reusch et al. (2023; Zenodo DOI 10.5281/zenodo.7535030) and required at least 50 presence-qualified fixes per retained source track. Later same-source sensitivity analyses do not alter that first-primary verdict.

A subsequent response-unopened programme evaluated a *Hipposideros armiger / H. pratti* source (Si et al. 2025; Dryad DOI 10.5061/dryad.j0zpc86r1) under a predeclared source-level test and retained failures without species or subset rescue. A broader public-source screen then closed because most candidate archives lacked event-level vertical measurements or sufficient repeated high-resolution sessions. Two sources nevertheless had accepted native vertical fields and exactly four repeat individuals while their numeric vertical values were still unopened: *Myotis vivesi* (Hurme et al. 2019; Movebank DOI 10.5441/001/1.kk3bg2f4) and *Pteropus poliocephalus* (Boardman et al. 2021; Movebank DOI 10.5441/001/1.5bd6pq55). These two sources were admitted together to a separate four-individual programme specified before either vertical outcome was examined.

The four-individual programme retained the same >=50-event session threshold, >4-h session split, 5-km grid, >=50 common-support target-event requirement, whole-session identity permutation, session-median centering, centered-height bins and 9,999 permutations used in its pre-specified analysis plan. Horizontal individuality was quantified and committed before numeric vertical values were opened. The change from a five- to four-individual admission gate therefore defines a distinct prospective programme and does not retroactively relabel earlier structural STOPs. Full citations for all archived tracking datasets used in the study are provided in the **Data sources** section.

### Post-outcome *Pteropus* terrain-confound audit

The *P. poliocephalus* external primary used native height above mean sea level and, before its vertical response was opened, showed extremely strong 5-km horizontal individuality. This combination left a specific alternative explanation: repeatable fine-scale x-y use within a 5-km cell could generate repeatable MSL-distribution shape through terrain. We therefore froze a diagnostic contract after the historical MSL result but before any digital-elevation values were decoded.

All 145,063 events in the original four-individual, 158-session universe were covered by one pinned Mapzen/AWS Skadi HGT tile (S35E138; 3,601 × 3,601; gzip SHA256 recorded in the repository). Terrain elevation was bilinearly interpolated at each event coordinate. The primary diagnostic response was native MSL height minus DEM elevation, then median-centered within the unchanged session and binned using the same centered edges as the small-panel primary. A companion pathway diagnostic applied the same estimator to session-centered DEM terrain itself. Both used identical 5-km common-cell weighting, all four individuals, the pre-specified session universe and 9,999 whole-session permutations with pre-specified seeds. This audit is explicitly post-outcome and cannot change the historical prospective MSL verdict.

### Post-hoc ecological synthesis

After all original and external centered outcomes were known, we compiled independently documented natural-history features at the unique-taxon level. We did not fit a current diet/guild model or calculate a p-value for the ecological split. In particular, the three *Phyllostomus hastatus* panels were treated as repeated panels of one species rather than three independent ecological replicates. We focused on two mechanistic dimensions suggested by the opened pattern: persistence or spatial anchoring of foraging resources, and the degree of vertical opportunity versus constraint in the foraging task. Wing morphology, phylogeny/sensory ecology, habitat vertical complexity, atmospheric forcing, tag technology and vertical reference were retained as competing predictor families. The resulting ecological interpretation is therefore a generated prediction for future outcome-blind tests, not a confirmed cross-species causal effect.

### Source-study ethics

This study conducted no new capture, handling or instrumentation. The focal *T. teniotis* source study reports ICNF Portugal permit 665/2017/CAPT (O'Mara et al. 2021). The *E. helvum* programme reports approvals from relevant wildlife and veterinary authorities in Ghana, Zambia and Burkina Faso (O'Mara et al. 2019). The *H. monstrosus* study reports approval by the Ministry of Agriculture, Livestock and Fisheries of the Republic of Congo and the VetAgro Sup ethics committee, approval 1805-V2 (Schloesing et al. 2023). The *P. hastatus* programmes report Ministerio del Ambiente Panamá permits and Smithsonian Tropical Research Institute Animal Care and Use Committee approvals detailed in the source papers (O'Mara & Dechmann 2023; Calderón-Capote et al. 2024). The external *Nyctalus*, *Hipposideros*, *Myotis vivesi* and *Pteropus poliocephalus* datasets were likewise reused from public archives; their original animal-welfare and field approvals are reported by Reusch et al. (2023), Si et al. (2025), Hurme et al. (2019) and Boardman et al. (2021), respectively. Full source-by-source permit provenance is archived with the analysis.

## Results

### A closed public-data screen yielded six repeated 3-D bat panels

The outcome-blind source screen considered 23 Movebank parent bat datasets and admitted six sources spanning four taxa. The six paper panels were *Tadarida teniotis*, *Eidolon helvum*, *Hypsignathus monstrosus*, and three temporal *Phyllostomus hastatus* datasets. The source universe was closed before estimator calibration and was not expanded after comparative outcomes were observed.

### Five comparative panels retain vertical-distribution shape after absolute altitude level is removed

The strongest ecological result came from the five comparative panels. Median-centering every retained session removed absolute vertical location before vertical binning and therefore removed any additive constant tag/device altitude offset. All five comparative panels nevertheless retained calibrated common-cell identity in vertical-distribution shape (Figure 2).

*E. helvum* retained observed centered identity +0.372 nats/fix versus a null mean of -0.071 (calibrated excess +0.443; p=0.0002). *H. monstrosus* retained +0.074 versus -0.103 (+0.177; p=0.0002). *P. hastatus* 2022 retained -0.039 versus -0.151 (+0.111; p=0.0002), the 2023 panel +0.045 versus -0.073 (+0.118; p=0.0002), and the 2016 panel -0.008 versus -0.582 (+0.574; p=0.0076).

The motivating *T. teniotis* panel was the exception: observed centered-shape identity was -0.263 versus a null mean of -0.241 (calibrated excess -0.022; p=0.5121). Thus the cross-panel result meets the pre-specified category requiring support in four or five of the six panels. Additive altitude zero-point differences cannot explain the comparative five-panel pattern, whereas the absolute vertical-location component in *Tadarida* remains inseparable from biological mean-height differences, device offset, or both.

### Supporting robustness analyses

Supporting analyses were concordant with, but subordinate to, the centered-shape result. Historical coarse-horizontal identity exceeded exchangeability expectations across all six original panels; stationary-height correction retained identity in both panels that met its pre-specified support gate; endpoint-neighbourhood exclusion retained calibrated identity in four comparative panels, with *Eidolon* remaining positive but below its pre-specified post-exclusion sample-size gate; and direct pairwise self-identification exceeded its pipeline-specific null in five panels. Descriptive centered profiles, temporal-overlap summaries and the full pipeline-calibration history are reported in Supporting Information.











### *Tadarida* is a motivating boundary case rather than the comparative template

The motivating *T. teniotis* dataset contains repeatable individual information but repeatedly defines the claim ceiling. Its earlier early/late assignment test strongly rejected individual exchangeability (diagonal gain +0.1682 nats/event; exact p=0.000174), whereas a stronger residual cell-by-height stability test failed (p=0.160; Supporting Information).

Terrain-relative AGL identity remained supported at 5 km (calibrated +0.446; p=0.0161) and 2.5 km (+0.712; p=0.011), but not at 10 km (+0.237; p=0.1018). The 1-km endpoint-neighbourhood exclusion also failed (p=0.1109), and session-centering eliminated calibrated shape identity (p=0.5121).

The raw common-cell AGL separation averaged 256.459 m, compared with a session-label null mean of 133.733 m (calibrated excess 122.727 m; p=0.0297). Because centered-shape identity failed, we treat this metre-scale quantity only as a descriptive translation of repeatable absolute vertical location, which can contain genuine biological mean-height differences, additive device bias, or both.



### Centered individuality persists after broad place, state and time matching where it occurs

The secondary localization analyses narrowed, but did not identify, the mechanism generating the original centered-shape signal. Centered identity remained after horizontal-speed conditioning in 5/5 comparative positive panels and after speed × turning conditioning in 5/5. Where structural support allowed finer matching, identity remained after place × state matching at 2 km in 4/4 panels, at 500 m in 4/4 and at 250 m in 3/3. A common 100-m analysis was structurally unavailable.

The signal was also not restricted to immediate same-session history. It remained with >=1-day separation in 4/4 evaluable panels, >=3-day separation in 3/3 and >=7-day separation in 2/2. These results do not establish a lifetime individual trait, but they make broad kinematic-state mixture, >=250–500-m place allocation and purely transient same-night structure insufficient general explanations for the positive original systems. The complete support pattern, including structurally non-evaluable cells and the unresolved same-night 2016 result, is shown in Figure 3.

### Independent external systems reveal strong heterogeneity rather than universal replication

The first pre-specified external *N. noctula* primary was directionally concordant but did not meet its inferential criterion (calibrated excess +0.05175, p=0.1224, n=27). Later same-source eligibility sensitivities remained positive across all seven pre-specified thresholds but are post-outcome and do not change that verdict.

The response-unopened *Hipposideros* source also did not meet its pre-specified source-level primary criterion (excess -0.04468, p=0.8616; n=13 total), with no permitted species rescue. Under the separate four-individual programme specified before either admitted vertical outcome was examined, *M. vivesi* was essentially null relative to its pipeline-specific expectation (excess +0.00470, p=0.4419), whereas *P. poliocephalus* exceeded its pre-specified criterion (excess +0.16873, p=0.0001). The *Pteropus* source had already shown exceptional horizontal individuality before its vertical response was opened (horizontal excess +3.48659, p=0.0001), while *M. vivesi* showed no corresponding horizontal advantage (excess -0.12378, p=0.5846).

These sources arose from distinct pre-specified programmes and a structurally filtered public-data search, so their pattern of supported and unsupported outcomes is not an estimate of prevalence across bats. Their shared contribution is instead a boundary result: centered vertical individuality is externally reproducible in at least one independent source but is clearly not universal across the tested systems. The pre-specified external sequence and the Pteropus terrain-adjusted diagnostic are summarized in Figure 4.

### The *Pteropus* MSL signal is strongly terrain-sensitive but survives terrain adjustment

The pre-specified *Pteropus* terrain audit exactly reproduced the historical centered-MSL observed statistic (+0.11003; original calibrated excess +0.16873, p=0.0001). Session-centered DEM terrain was itself strongly individualized (observed +0.27630, null mean -0.10257, calibrated excess +0.37887, p=0.0034). Thus the proposed fine-scale topographic leakage pathway is not hypothetical in this source: individuals repeatedly used different terrain distributions even after the 5-km common-cell standardization.

Subtracting DEM elevation from MSL height substantially attenuated the signal. The terrain-adjusted centered endpoint had observed +0.00728 versus a null mean of -0.02503, giving calibrated excess +0.03231; the descriptive ratio to the original calibrated excess was 0.192. This ratio is not a mediation fraction because terrain subtraction changes the response distribution and its pipeline-specific null. Nevertheless the terrain-adjusted endpoint still exceeded the pre-specified permutation null (p=0.0023). The appropriate diagnostic conclusion is therefore dual: the historical MSL individuality is strongly terrain-sensitive and terrain itself carries individual identity, but sampled terrain structure does not fully eliminate centered vertical individuality in this four-individual source. Because DEM subtraction is a terrain-relative proxy rather than source-measured AGL, and because the audit was specified after the MSL result was known, it is corroborative confound diagnosis rather than a second prospective replication.

### The opened systems generate a resource-anchoring × vertical-opportunity hypothesis

At the unique-taxon level, the current positive systems share an ecological feature that was not used to select or code the original outcomes. *Eidolon helvum* and *Hypsignathus monstrosus* use persistent fruit/flower resources; *P. hastatus* is omnivorous but uses repeatable feeding areas and plant resources; and the tracked Adelaide *P. poliocephalus* individuals repeatedly foraged on identifiable urban trees and other plant resources (Fahr et al. 2015; Schloesing et al. 2023; O'Mara & Dechmann 2023; Boardman et al. 2021). By contrast, the current centered boundary/unsupported systems include aerial insectivores such as *Tadarida* and *Nyctalus*, insectivorous *Hipposideros*, and the marine fishing bat *M. vivesi*, whose prey capture is associated with a strongly surface-constrained marine foraging task (Hurme et al. 2019).

This contrast is descriptive and post hoc. Diet, morphology, phylogeny, sensory ecology, habitat and tracking technology covary among these systems, and the current source set was not assembled to separate them. We therefore do not test a plant-feeding effect. Instead the pattern generates a more mechanistic prediction: stable centered vertical individuality should be strongest where persistent spatial resources and vertical habitat structure repeatedly allow individuals to solve the same foraging problem in different ways, and weaker where prey is highly mobile or feeding is constrained close to a single surface or layer. Figure 5 presents this as a non-quantitative hypothesis schematic rather than a fitted retrospective trait relationship.


## Discussion

### Comparative populations contain repeatable individual shapes of vertical space use

All five non-*Tadarida* panels retained calibrated identity in vertical-distribution shape after self and other profiles were standardized to the same coarse horizontal occupancy and every session was translated to zero median. The result spans *Eidolon helvum*, *Hypsignathus monstrosus* and three *Phyllostomus hastatus* datasets. Thus the validated signal is not simply that one individual flies higher than another: it is repeatable identity in how probability is allocated across residual-height states around a session-specific typical altitude.

We use **organization of vertical space use** for this distribution-level property. A broad population distribution can arise because every animal is individually broad, because individuals use different horizontal places, or because the population mixes individuals with different repeatable vertical organizations. The centered-shape test supports this third component. Supporting descriptive profiles suggest differences in central concentration and tail use, but those components were not separately exchangeability-calibrated and are not interpreted as independent effects.

Stationary-height correction provided narrower corroboration in the two panels that met its pre-specified support gate. Full profile visualizations and offset-correction details are in Supporting Information.

### Broad state and place mixtures do not generally absorb individual organization of vertical space use

The original manuscript distinguished two broad explanations: individuals might repeatedly allocate time among behavioural or spatial states, or they might remain non-exchangeable within the same broad state and place. The secondary localization programme moves that distinction forward. Matching horizontal speed and speed × turning state does not remove centered identity in the five original comparative positive panels, and matching place × state at 250–500 m likewise leaves the signal in every structurally evaluable panel. Multi-day separation further shows that the positive pattern is not only a transient carry-over from immediately adjacent sessions.

These analyses do not prove a single within-state biological phenotype. Kinematic states are proxies rather than directly observed foraging, commuting or social behaviour, and exact feeding trees, narrow corridors, canopy gaps, microtopography and atmospheric conditions below the supported spatial grains remain unresolved. The result is therefore one of causal narrowing: broad behavioural composition and coarse-to-intermediate place allocation are insufficient general explanations where centered individuality is detectable.

### Pipeline-specific nulls are part of the biological inference

Prediction-based individuality statistics did not share universal intuitive nulls. Finite training structure, smoothing and eligibility rules shifted exchangeability expectations away from zero or 0.5, and calibration changed one earlier qualitative architecture interpretation. We therefore base inference on the complete statistic recomputed under biologically appropriate whole-session label exchangeability rather than on an assumed reference value. The full amendment and calibration history is retained in Supporting Information.

### Horizontal and central-place structure are reduced, not eliminated

Common-cell weighting removes differences in occupancy among the tested 5-km cells, but it does not force individuals to share identical continuous x-y positions. Fine-scale fidelity within a cell can therefore still translate into vertical differences through terrain, resources or central-place routes.

The endpoint-neighbourhood audit narrows this concern. Four comparative panels retain calibrated identity after the same fixed 1-km exclusion, and *Eidolon* retains a strong signal but does not meet the pre-specified post-exclusion sample-size gate. Endpoint-associated structure is therefore not a sufficient general explanation for the comparative result. At the same time, the failure in *Tadarida* and the lack of verified roost, colony or lek coordinates prevent a universal claim of central-place independence.

We therefore describe the result as vertical individuality beyond **coarse-grained horizontal occupancy at the tested 5-km scale**, not as complete removal of horizontal fidelity.

### Additive tag offsets are not a general explanation, but other device error remains possible

Session centering removes every additive altitude zero-point difference without requiring knowledge of the device-specific error. The persistence of calibrated shape identity in all five comparative panels therefore rules out a constant tag offset as a general explanation for those results.

The audit is not a proof against every form of measurement error. Tag-specific differences in altitude-error variance, antenna orientation, reception quality or other state-dependent error could in principle broaden or narrow an individual's apparent vertical distribution. Tracking windows overlap strongly in most panels, so many animals shared broad atmospheric and satellite contexts, but heteroscedastic device error remains unresolved. Future prospective work should therefore include repeated device calibration or tag-swapping designs where feasible.

### *Tadarida* defines the boundary of the current evidence

The motivating *Tadarida* dataset retains repeatable absolute vertical-location information and AGL identity at 2.5–5 km, but it fails the 10-km grain test, endpoint-neighbourhood exclusion and shift-invariant centered-shape test. Genuine mean-height specialization and additive device offset therefore remain inseparable in this panel, and its earlier 256-m AGL translation is not treated as independent device-free shape evidence. The stronger residual cell-by-height test is also negative, so repeatable identity should not be interpreted as one rigid three-dimensional route map.

### Vertical individuality is recurrent but not a universal bat property

The external programme changes the interpretation of generality. Three prospectively evaluated source systems do not meet their pre-specified primary criteria, whereas *P. poliocephalus* meets its criterion under a separate four-individual design fixed before either admitted vertical outcome was examined. These are not exchangeable replication trials: source admission rules and programme histories differ, public archives are strongly filtered by the availability of repeated high-resolution vertical data, and the convenience-source set cannot estimate population prevalence. The stronger conclusion is qualitative but important: the centered-shape phenomenon can recur independently, yet its expression varies sharply among bat systems.

The failures are therefore biologically informative rather than merely inconvenient. A universal latent “spatial individuality” construct that can accommodate every combination of horizontal and vertical results has little predictive content. The next useful question is instead what ecological or morphological features predict the magnitude of the centered vertical effect in a new source.

### *Pteropus* separates topographic context from residual vertical individuality

The *Pteropus* source provides an unusually informative stress test because strong horizontal individuality, MSL altitude and the supported external vertical result occur in the same four individuals. The terrain audit confirms the alternative pathway: repeatable fine-scale terrain distributions carry individual information, and the terrain-adjusted endpoint has a much smaller calibrated excess than the original MSL endpoint. The 0.192 terrain-adjusted/original excess ratio is descriptive only and cannot be interpreted as a causal percentage mediated. Thus 5-km common-cell weighting should not be interpreted as complete removal of horizontal-topographic structure.

But the same audit also shows that terrain is not the whole signal. The terrain-adjusted endpoint remains above its predeclared permutation null. The resulting biological picture is not “horizontal versus vertical individuality” as mutually exclusive causes. Rather, repeatable fine-scale landscape use and repeatable terrain-relative vertical organization coexist in this source. The panel contains only four individuals, and one has only two evaluable target sessions, so neither the terrain pathway nor the residual terrain-adjusted signal should be described as uniform among individuals.

### Resource anchoring and vertical opportunity provide a falsifiable ecological hypothesis

The currently opened positive and negative systems suggest a more predictive ecological-contingency hypothesis than a generic multidimensional description. Positive systems repeatedly use resources or feeding areas that can be spatially persistent, whereas several current boundaries are dominated by mobile aerial prey or by feeding close to a surface. The relevant mechanism is unlikely to be a crude frugivore/insectivore binary: *P. hastatus* is omnivorous, and horizontal site fidelity can occur in insectivorous systems without supported centered vertical individuality. What matters more plausibly is whether the ecological task repeatedly supplies stable spatial anchors together with enough vertical opportunity for different individuals to adopt repeatable solutions.

This resource-anchoring × vertical-opportunity interpretation was generated after the outcomes were known. It competes with wing loading and aspect ratio, phylogenetic and sensory differences, atmospheric forcing, habitat structure, and source-specific tracking properties. We therefore present it as a falsifiable prediction rather than a fitted explanation of the current panels.

### A prospective test of ecological contingency

The next decisive study should be designed to test heterogeneity rather than search for another favourable replication. Before any new source's vertical outcomes are opened, sources should be coded using independent natural-history information for persistent-resource anchoring, vertical habitat opportunity and competing morphological predictors such as wing loading and aspect ratio. The primary response should be the continuous null-calibrated centered-vertical effect rather than a binary supported/unsupported classification.

The most informative new systems are deliberate contrasts: resource-anchored foragers in vertically simple habitats, mobile-prey foragers in vertically complex habitats, and closely related species that differ in resource persistence. Harmonized terrain-relative altitude, known roost locations, high-frequency horizontal positions, direct behavioural-state classification, synchronized atmospheric measurements and device calibration would allow exact resource/route use to be separated from residual within-context flight organization. A prediction registered before these data are opened is straightforward: centered vertical individuality should increase when animals repeatedly encounter stable, vertically structured foraging opportunities, after morphology and phylogeny are accounted for.

The current public-data screen also exposes a practical limit: repeated high-resolution tracks with event-level vertical measurements are rare, so the >=8-source confirmatory gate may not be reachable from existing archives alone. We therefore treat the pre-specified future prediction plan as a design standard for future accumulation rather than a promise of an immediate follow-up test. Coordinated field studies that deliberately sample contrasting resource regimes and collect terrain-relative altitude, behavioural state, morphology and local environmental data may be required to make the ecological-contingency hypothesis testable at adequate cross-system replication. The contract excludes every currently opened system from confirmation, fixes ecological coding before vertical opening, uses the continuous null-calibrated centered-vertical effect as the response, and predeclares the >=8-source primary test.

## Conclusion

Bat populations can contain repeatable individual organization of vertical space use that is not reducible to coarse horizontal occupancy or a constant altitude zero point. In the original closed archive, all five comparative panels retained identity in session-centered vertical-distribution shape, whereas the motivating *Tadarida* system did not. Secondary stress tests further show that, where the centered signal occurs, broad movement-state mixture, 250–500-m place allocation and short temporal separation do not generally absorb it.

Independent external tests set an equally important boundary. *Nyctalus*, *Hipposideros* and *Myotis vivesi* do not meet their pre-specified source-level criteria, while *Pteropus poliocephalus* provides one prospective external result that meets its criterion under a separate four-individual design specified before outcomes were examined. In that source, fine-scale terrain use carries strong individual identity and the terrain-adjusted calibrated excess is substantially smaller than the original MSL-scale excess, yet a smaller terrain-adjusted centered signal remains. Vertical individuality is therefore recurrent but demonstrably heterogeneous, not a universal property that should be assumed for all bats.

The ecological contrast among currently opened systems generates a testable next hypothesis rather than a retrospective causal conclusion. Stable individual vertical strategies may emerge most strongly when animals repeatedly solve vertically structured foraging problems around persistent spatial resources; mobile prey or surface-constrained feeding may reduce the opportunity for such strategies to be expressed. Under this view, individual specialization is not only a property of individuals. Its observable form can emerge from the interaction between persistent individual tendencies and the ecological opportunities a system repeatedly provides.

## References

Boardman, W.S.J., Roshier, D., Reardon, T., Burbidge, K., McKeown, A., Westcott, D.A., Caraguel, C.G.B. & Prowse, T.A.A. (2021). Spring foraging movements of an urban population of grey-headed flying foxes (*Pteropus poliocephalus*). *Journal of Urban Ecology*, **7**, juaa034. https://doi.org/10.1093/jue/juaa034

Bolnick, D.I., Svanbäck, R., Fordyce, J.A., Yang, L.H., Davis, J.M., Hulsey, C.D. & Forister, M.L. (2003). The ecology of individuals: Incidence and implications of individual specialization. *The American Naturalist*, **161**, 1–28. https://doi.org/10.1086/343878

Calderón-Capote, M.C., van Toor, M.L., O'Mara, M.T., Bayer, T.D., Crofoot, M.C. & Dechmann, D.K.N. (2024). Consistent long-distance foraging flights across years and seasons at colony level in a neotropical bat. *Biology Letters*, **20**, 20240424. https://doi.org/10.1098/rsbl.2024.0424

Dreelin, R.A., Shipley, J.R. & Winkler, D.W. (2018). Flight behavior of individual aerial insectivores revealed by novel altitudinal dataloggers. *Frontiers in Ecology and Evolution*, **6**, 182. https://doi.org/10.3389/fevo.2018.00182

Fahr, J., Abedi-Lartey, M., Esch, T., Machwitz, M., Suu-Ire, R., Wikelski, M. & Dechmann, D.K.N. (2015). Pronounced seasonal changes in the movement ecology of a highly gregarious central-place forager, the African straw-coloured fruit bat (*Eidolon helvum*). *PLOS ONE*, **10**, e0138985. https://doi.org/10.1371/journal.pone.0138985

Gámez, S. & Harris, N.C. (2022). Conceptualizing the 3D niche and vertical space use. *Trends in Ecology & Evolution*, **37**, 953–962. https://doi.org/10.1016/j.tree.2022.06.012

Hurme, E., Gurarie, E., Greif, S., Herrera M., L.G., Flores-Martínez, J.J., Wilkinson, G.S. & Yovel, Y. (2019). Acoustic evaluation of behavioral states predicted from GPS tracking: a case study of a marine fishing bat. *Movement Ecology*, **7**, 21. https://doi.org/10.1186/s40462-019-0163-7

Kerches-Rogeri, P., Niebuhr, B.B., Muylaert, R.L. & Mello, M.A.R. (2020). Individual specialization in the use of space by frugivorous bats. *Journal of Animal Ecology*, **89**, 2584–2595. https://doi.org/10.1111/1365-2656.13339

McIntyre, T., Bester, M.N., Bornemann, H., Tosh, C.A. & de Bruyn, P.J.N. (2017). Slow to change? Individual fidelity to three-dimensional foraging habitats in southern elephant seals, *Mirounga leonina*. *Animal Behaviour*, **127**, 91–99. https://doi.org/10.1016/j.anbehav.2017.03.006

O'Mara, M.T., Scharf, A.K., Fahr, J., Abedi-Lartey, M., Wikelski, M., Dechmann, D.K.N. & Safi, K. (2019). Overall dynamic body acceleration in straw-colored fruit bats increases in headwinds but not with airspeed. *Frontiers in Ecology and Evolution*, **7**, 200. https://doi.org/10.3389/fevo.2019.00200

O'Mara, M.T., Amorim, F., Scacco, M., McCracken, G.F., Safi, K., Mata, V., Tomé, R., Swartz, S., Wikelski, M., Beja, P., Rebelo, H. & Dechmann, D.K.N. (2021). Bats use topography and nocturnal updrafts to fly high and fast. *Current Biology*, **31**, 1311–1316.e4. https://doi.org/10.1016/j.cub.2020.12.042

O'Mara, M.T. & Dechmann, D.K.N. (2023). Greater spear-nosed bats commute long distances alone, rest together, but forage apart. *Animal Behaviour*, **204**, 37–48. https://doi.org/10.1016/j.anbehav.2023.08.001

Ratcliffe, N., Takahashi, A., O'Sullivan, C., Adlard, S., Trathan, P.N., Harris, M.P. & Wanless, S. (2013). The roles of sex, mass and individual specialisation in partitioning foraging-depth niches of a pursuit-diving predator. *PLOS ONE*, **8**, e79107. https://doi.org/10.1371/journal.pone.0079107

Reusch, C., Paul, A.A., Fritze, M., Kramer-Schadt, S. & Voigt, C.C. (2023). Wind energy production in forests conflicts with tree-roosting bats. *Current Biology*, **33**, 737–743.e3. https://doi.org/10.1016/j.cub.2022.12.050

Schloesing, E., Caron, A., Chambon, R., Courbin, N., Labadie, M., Nina, R., Mouiti Mbadinga, F., Ngoubili, W., Sandiala, D., N'Kaya Tobi, Bourgarel, M., De Nys, H.M. & Cappelle, J. (2023). Foraging and mating behaviors of *Hypsignathus monstrosus* at the bat-human interface in a central African rainforest. *Ecology and Evolution*, **13**, e10240. https://doi.org/10.1002/ece3.10240

Si, M., Wang, Z., Liu, Y., Song, Y., Gong, L., Zhu, D., Huang, Z., Feng, J. & Jiang, T. (2025). Individual asymmetric competition responses across multidimensional niches may enable coexistence of closely related species. *Functional Ecology*, **39**, 1957–1971. https://doi.org/10.1111/1365-2435.70088

Wang, Z., Gong, L., Huang, Z., Geng, Y., Zhang, W., Si, M., Wu, H., Feng, J. & Jiang, T. (2023). Linking changes in individual specialization and population niche of space use across seasons in the great evening bat (*Ia io*). *Movement Ecology*, **11**, 32. https://doi.org/10.1186/s40462-023-00394-1

Woo, K.J., Elliott, K.H., Davidson, M., Gaston, A.J. & Davoren, G.K. (2008). Individual specialization in diet by a generalist marine predator reflects specialization in foraging behaviour. *Journal of Animal Ecology*, **77**, 1082–1091. https://doi.org/10.1111/j.1365-2656.2008.01429.x

Xing, S., Leahy, L., Ashton, L.A., Kitching, R.L., Bonebrake, T.C. & Scheffers, B.R. (2023). Ecological patterns and processes in the vertical dimension of terrestrial ecosystems. *Journal of Animal Ecology*, **92**, 538–551. https://doi.org/10.1111/1365-2656.13881

## Data sources

Bayer, T.D., Barría, L.M., Gómez, L.F., Lee, J.P., Aguilar, G. & O'Mara, M.T. (2024). Data from: Consistent long-distance foraging flights across years and seasons at colony level in a Neotropical bat [2023] [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.322

Boardman, W.S.J. & Roshier, D. (2020). Data from: Spring foraging movements of an urban population of grey-headed flying foxes (*Pteropus poliocephalus*) [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.5bd6pq55

Calderón-Capote, M.C., van Toor, M.L., O'Mara, M.T., Bayer, T.D., Crofoot, M.C. & Dechmann, D.K.N. (2024). Data from: Consistent long-distance foraging flights across years and seasons at colony level in a Neotropical bat [2021–2022] [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.321

Hurme, E., Gurarie, E., Greif, S., Herrera M., L.G., Flores-Martínez, J.J., Wilkinson, G.S. & Yovel, Y. (2019). Data from: Acoustic evaluation of behavioral states predicted from GPS tracking: a case study of a marine fishing bat [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.kk3bg2f4

O'Mara, M.T., Amorim, F., McCracken, G.F., Mata, V., Safi, K., Wikelski, M., Beja, P., Rebelo, H. & Dechmann, D.K.N. (2021). Data from: European free-tailed bats use topography and nocturnal updrafts to fly high and fast [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.52nn82r9

O'Mara, M.T. & Dechmann, D.K.N. (2023). Data from: Greater spear nosed bats commute long distances alone, rest together, but forage apart [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.282

Reusch, C., Paul, A.A., Fritze, M., Kramer-Schadt, S. & Voigt, C.C. (2023). Annotated GPS locations [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.7535030

Scharf, A.K., Fahr, J., Abedi-Lartey, M., Safi, K., Dechmann, D.K.N., Wikelski, M. & O'Mara, M.T. (2019). Data from: Overall dynamic body acceleration in straw-colored fruit bats increases in headwinds but not with airspeed [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.k8n02jn8

Schloesing, E., Caron, A., Chambon, R., Courbin, N., Labadie, M., Nina, R., Mouiti Mbadinga, F., Ngoubili, W., Sandiala, D. & N'Kaya Tobi (2024). Data from: Foraging and mating behaviors of *Hypsignathus monstrosus* at the bat-human interface in a central African rainforest [Dataset]. Movebank Data Repository. https://doi.org/10.5441/001/1.278

Si, M., Wang, Z., Feng, J. & Jiang, T. (2025). Data from: Individual asymmetric competition responses across multidimensional niches may enable coexistence of closely related species [Dataset]. Dryad. https://doi.org/10.5061/dryad.j0zpc86r1

## Figure legends

**Figure 1. Identifying vertical individuality and its ecological boundary.** Conceptual workflow showing four inferential stages: identical coarse horizontal-cell weighting of self and other vertical profiles; session centering to remove absolute altitude level; secondary matching of measured place, movement state and temporal separation; and prospective external tests. The final panel distinguishes established results from the post-hoc resource-anchoring × vertical-opportunity hypothesis.

**Figure 2. Centered vertical-distribution individuality in the original closed comparative archive.** Points show observed-minus-null-mean calibrated centered identity for each original panel. Horizontal bars show the central 95% interval (2.5th–97.5th percentiles) of that panel's whole-session permutation null after subtracting its own null mean, so the panel-specific exchangeability expectation is aligned at zero. Circles denote panels meeting the pre-specified one-sided inferential criterion and the cross denotes the *Tadarida teniotis* boundary case. The 95% bars visualize null width but are not themselves the one-sided decision threshold; exact permutation p-values are reported in Results and the source table underlying the figure.

**Figure 3. Localization of the centered-individuality signal within the original positive systems.** Rows summarize pre-specified secondary stress tests for speed, speed × turning state, place × state at supported spatial grains, and increasing temporal separation. Cells distinguish supported retention from structural non-evaluability. These analyses localize what does not generally absorb the signal; they do not identify one causal mechanism.

**Figure 4. Prospective external boundary tests and the *Pteropus* terrain diagnostic.** Points show observed-minus-null-mean calibrated centered identity for each source or diagnostic endpoint. Horizontal bars show the central 95% interval (2.5th–97.5th percentiles) of each source-specific whole-session permutation null after subtracting its own null mean. This makes the large differences in null width among source designs visible. Crosses denote external results that did not meet their pre-specified one-sided criteria and circles denote supported endpoints; the bars are uncertainty displays rather than the exact one-sided decision threshold. *Pteropus poliocephalus* meets its centered-MSL criterion under a separate four-individual design fixed before either admitted vertical outcome was examined, and the post-outcome MSL-minus-DEM diagnostic retains a smaller supported effect. Terrain-only individuality (+0.37887, p=0.0034) is reported in Results but is not plotted on this vertical-response axis because terrain elevation is a different response.

**Figure 5. Ecological hypothesis generated by cross-system heterogeneity.** This is a non-quantitative hypothesis schematic rather than a retrospective trait plot. Persistent spatial resource anchoring and repeated vertical opportunity are proposed to increase the availability of repeatable alternative spatial solutions, whereas mobile or ephemeral prey and surface-constrained feeding are proposed to reduce such opportunity. Current taxa appear only as motivating examples that generated the hypothesis, not as scored predictor observations. Competing explanations include flight morphology, phylogeny/sensory ecology, habitat structure, atmospheric forcing and tracking technology. Future confirmation uses only new sources coded before vertical outcomes are opened.

## Ethics statement

This study is a secondary analysis of publicly archived animal-tracking data and involved no new capture, handling or experimental manipulation of animals. The original tracking programmes were conducted under the permits and institutional approvals detailed in Materials and Methods and in the repository's source-ethics provenance ledger. The present analyses use only published tracking measurements and source animal identifiers.

## Data and code availability

All tracking data are publicly archived under persistent identifiers; full dataset citations are given in **Data sources**. Exact source bitstreams and checksums are recorded in the pre-specified provenance files.

All analysis code, contracts, source-screen records, calibration history, result summaries and figure-generation scripts will be available in a permanent versioned archive. The repository identifier is withheld from the reviewer-facing manuscript for double-anonymized review and will be restored in the public version. Complete source and checksum ledgers are retained in the archived analysis record.
