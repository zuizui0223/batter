# Manuscript draft v0.3.3

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

Individuals within the same population often use only subsets of the resources, habitats or behaviours represented by the population as a whole. This individual specialization can change population niche structure, alter the intensity of intraspecific interactions and determine how faithfully a pooled population distribution represents the animals that compose it (Bolnick et al. 2003). Movement data have extended this idea from diets and resource categories to spatial ecology: individuals can differ consistently in where they move, which habitats they use and how faithfully they return to particular areas (Kerches-Rogeri et al. 2020; Mordue et al. 2023). Such differences need not be fixed. In bats, for example, spatial individual specialization can change across seasons as resource distributions and movement demands change (Wang et al. 2023). A central problem is therefore not only whether a population contains repeatable individual variation, but also how that variation is spatially organized.

Most empirical studies of spatial individual specialization still describe movement on a horizontal plane. That simplification is increasingly difficult to justify for animals that fly, climb or dive. Vertical position can alter access to resources, microclimates, competitors and energetic opportunities, and a growing ecological literature treats the vertical dimension as a distinct component of niche space (Gámez & Harris 2022; Xing et al. 2023). For mobile animals, movement trajectories themselves can also be repeatable without being identical, because repeated paths are continually perturbed by environmental conditions and state-dependent decisions (Carrasco 2024). Three-dimensional tracking therefore creates a specific ecological question: when an individual's vertical use is repeatable, what aspect of that use is carrying the individual information?

At least two forms of repeatable vertical identity are possible. First, individuals may differ mainly in their overall distribution of heights. Under this architecture, knowing which animal is being observed is informative even before horizontal location is considered: one individual may consistently use a different portion of the vertical axis from another. We call this **marginal identity**. Second, individual information may become substantially stronger once horizontal place is known. Under this architecture, the same animal need not have a globally distinctive height distribution, but its vertical state is more predictable when evaluated within horizontal context. We call this **conditional identity**. Their difference, the **conditional advantage**, asks whether horizontal context increases predictive information about individual identity. These quantities describe predictive organization; they do not, by themselves, identify the behavioural mechanism that generated it.

This distinction is important because a pooled three-dimensional population distribution can hide non-exchangeability among individuals. A population may occupy many vertical states at the same horizontal locations, yet no single pooled location-conditioned distribution need be a good predictor of a new individual. Conversely, poor transfer of a pooled distribution does not necessarily mean that vertical organization is absent. It can arise because repeated individual structure is averaged away. This problem is especially relevant when animal movement models are interpreted as population-level niches, habitat-use surfaces or general movement rules.

The present study originated from precisely such a pattern in European free-tailed bats, *Tadarida teniotis*. O'Mara et al. (2021) showed that these bats use topography and nocturnal uplift during high and fast flights. A later frozen analysis of the same public tracking data found that the population retained substantial vertical thickness after horizontal position was known—approximately 4.02 effective altitude states—while a pooled location-conditioned vertical distribution failed to transfer to two sealed individuals. We treat that previous result only as motivation. Here we ask a different biological question: does vertical information repeat more successfully within individuals than across individuals, and if so, is that repeatability marginal or conditional?

A predictive contrast alone could be overinterpreted. A positive conditional advantage does not prove that an animal carries one stable cell-by-height route map. Horizontal conditioning can increase prediction for several reasons, including combinations of route choice, habitat structure, environmental context and temporal covariance. We therefore retain a stronger, independently frozen focal test that explicitly asks whether an individual-specific cell-by-height residual map remains stable after marginal altitude identity has already been absorbed. This provides a deliberate ceiling on mechanistic interpretation.

We then ask whether the same predictive architecture occurs outside the focal population. Public datasets create a risk of outcome-adaptive selection: once a pattern is seen, researchers can continue searching until a congenial example appears. We therefore used an outcome-blind source screen in which candidate datasets were admitted using only data structure—individual identifiers, timestamps, horizontal locations, vertical-field presence and repeated-session coverage—before numeric vertical outcomes were used for admission. The resulting fixed panel contains four bat taxa and both successful and failed prospective predictions.

We test three broad predictions. First, individual vertical identity should recur across nights in more than one bat system. Second, its predictive architecture should not necessarily be universal: conditional identity may dominate in some systems and marginal identity in others. Third, the balance between these components may itself change across ecological contexts within a species. Together, these tests move the question from whether individual bats differ in vertical use to how individual vertical information is organized within populations (Figure 1).

## Materials and Methods

### Conceptual framework and estimands

Our central unit of evidence is held-out predictive performance. For a target session, the **self** predictor is estimated from other eligible session(s) of the same individual. The **other-individual** predictor is estimated from comparison animals in the same admitted context. We score the observed vertical state z of the target animal either without horizontal conditioning or within horizontal cell (x,y).

Conditional identity is defined as

G_cond = E_target[log P_self(z|x,y) - log P_other(z|x,y)].

Marginal identity is

G_marg = E_target[log P_self(z) - log P_other(z)].

The conditional advantage is

G_adv = G_cond - G_marg.

Positive G_cond means that another session from the same individual predicts target vertical state better than the comparison-individual distribution. Positive G_adv means that horizontal conditioning increases that self-versus-other information relative to marginal height alone. We use **conditional-dominant** when G_cond exceeds G_marg and **marginal-dominant** when marginal identity is stronger. These labels refer to predictive architecture, not to latent behavioural classes.

GPS fixes are not treated as independent biological replicates. Fixes estimate within-session probability distributions and log scores; session results are summarized within individuals, and individuals are the biological summary unit. This distinction prevents dense tracking schedules from being interpreted as large independent sample sizes.

### Public-data discovery and outcome-blind admission

We searched the Movebank Data Repository through DataCite records under the Movebank DOI prefix and identified 23 parent bat datasets with plausible movement records. Nineteen parent packages exposed raw event CSV files directly. Four legacy packages required child-handle recovery. Before opening numeric height outcomes for candidate selection, event sources were checksum-pinned and screened using a common structural gate.

Structural admission could use field names, source checksums, taxon identity, individual identifiers, timestamps, finite horizontal coordinates, source outlier flags, and presence or absence of a native vertical field as a string. Numeric vertical values were forbidden for source admission. A source had to contain a native vertical coordinate on the same event as horizontal position and time, at least eight individuals with x-y-height presence, and at least five individuals with two or more eligible sessions containing at least 50 fixes. Explicit source-marked outliers were excluded when such flags were provided. Once comparative outcomes had been observed, the public-data search was closed.

Six sources from four taxa passed this gate: *Tadarida teniotis*, *Eidolon helvum*, *Hypsignathus monstrosus*, and three temporal datasets for *Phyllostomus hastatus*. Other otherwise relevant bat datasets failed structurally because the public event table lacked a native height field or too few individuals had repeated vertical tracking. This admission process determines the comparative panel used here; we did not lower gates or add later datasets after observing results.

### Focal *Tadarida teniotis* dataset

The focal data are from the public Movebank archive associated with O'Mara et al. (2021), DOI 10.5441/001/1.52nn82r9. The original tracking bitstream and archived annotated table were checksum-pinned before the present analyses. The raw panel contains eight tracked individuals. The primary vertical coordinate is GPS height above mean sea level (MSL).

A separately archived annotated table enabled two semantic controls. Terrain elevation was derived in the source workflow from a 30-m ASTER digital elevation model, and height above ground level (AGL) was calculated relative to that terrain surface. These fields allowed us to ask whether individual predictive information persisted relative to local ground and whether apparent vertical identity could instead be explained by repeatedly crossing the same sub-cell terrain elevations.

For the session-level analysis, consecutive records were divided into sessions using a frozen four-hour gap rule. Sessions containing fewer than 50 usable fixes were excluded. Horizontal locations were projected to EPSG:3035 and assigned to fixed grid cells. The primary horizontal cell size was 5 km, with 2.5- and 10-km analyses retained as frozen scale sensitivities. Vertical state was discretized using the fixed edges <0, 0–50, 50–100, 100–200, 200–400, 400–800, 800–1600, 1600–3200 and >3200 m. Jeffreys smoothing with alpha = 0.5 was applied to discrete probability estimates.

For each held-out session, the self conditional distribution was estimated from other sessions of the same individual with equal session weighting. The other-individual conditional distribution was estimated with equal individual weighting. Target fixes were scored only in horizontal cells supported by both predictors. At least 50 scored target fixes were required. The same target fixes were also scored under marginal self and other-individual height distributions, permitting direct calculation of G_cond, G_marg and G_adv.

### Independent focal identity-assignment test

The focal dataset also contains a separate frozen analysis family that predates the cross-taxon synthesis and provides stronger evidence for temporal identity matching. Within each individual, eligible records inside 18 fixed 5-km cells were ordered by time and split into early and late halves. An individualized early P_i(z|cell) map was shrunk toward the equal-individual species distribution using a fixed equivalent sample size of 20 events.

Each source individual's early map was scored against every target individual's later events, producing an 8 × 8 source-by-target gain matrix relative to the population conditional baseline. The observed statistic was the unweighted mean of the eight identity-matched diagonal gains. Its null distribution was the complete set of 8! = 40,320 assignments of source identities to later target identities. Support required a one-sided permutation probability <=0.05 and at least six of eight diagonal gains to be positive.

This early/late analysis asks whether the correct individual identity carries temporally repeatable conditional information. It is complementary to, but not numerically identical with, the session-level self-versus-other analysis.

### Residual cell-by-height refinement

To distinguish predictive conditional dominance from a stronger claim about a stable individual-specific map, we retained a separately frozen residual analysis. For each focal bat, its early marginal altitude distribution was first absorbed into a marginal-adjusted cell baseline proportional to the species P(z|cell) multiplied by the ratio of individual to species marginal height probabilities. The individual-specific cell-by-height model was then estimated by shrinking early individual cell counts toward this marginal-adjusted baseline.

The primary score was the late-event gain of the full individual cell model over its own marginal-adjusted baseline. As above, identity matching was tested using all 8! assignments. The preregistered support rule required p<=0.05 and at least six of eight positive diagonal residual gains. Equivalent-event shrinkage values of 5 and 50 were frozen sensitivities and could not replace the primary lambda = 20 result.

This test has a stronger interpretation than G_adv. If it passes, it supports temporal stability of an individual-specific cell-by-height residual after marginal altitude identity is controlled. If it fails, conditional dominance can still be a predictive property, but it should not be relabelled as proof of a stable individual route map.

### Focal ecological controls

We used four additional controls to delimit interpretation of the focal conditional signal.

First, we reran session-level identity scoring with AGL rather than MSL. Persistence in AGL would show that conditional identity was not solely an artefact of absolute terrain elevation.

Second, we treated terrain elevation itself as the vertical state under the same horizontal conditioning and scoring design. A strong terrain-only signal would indicate repeated selection of local ridges, valleys or other sub-cell elevation bands without requiring repeatable height above ground.

Third, we constructed a same-night environmental-context baseline. Nocturnal sessions were assigned to a calendar night using timestamp minus 12 hours. For each target session, the self predictor from the same bat on another night was compared directly against other bats flying during the target night. This tests the simple alternative that shared nightly conditions explain the apparent individual signal.

Fourth, we removed the pooled comparison distribution. The self predictor was compared directly with each alternative individual on common horizontal support, producing conditional and marginal pairwise self-versus-alternative gains. If architecture direction survives this analysis, it cannot be attributed simply to averaging heterogeneous comparison animals.

Finally, an independently frozen mechanism analysis tested whether cross-night differences could be summarized by one repeatable response to modelled vertical wind. For each eligible bat-night, climb rate was regressed on the archived vertical wind component. The target-night slope was predicted from the same bat's other sessions and from other individuals. A predeclared within-session wind-variation gate was retained regardless of result.

### Independent comparative panels

For *Eidolon helvum* (O'Mara et al. 2019; repository DOI 10.5441/001/1.k8n02jn8), 18,154 GPS records from 63 animals passed the initial structural presence screen, and 42 animals had at least two >=50-fix sessions before numeric height was opened. The native vertical field was height above the GPS reference ellipsoid. Analyses were stratified within exact study-site × shifted-night-year cohorts. Cohorts required at least four total individuals and three repeat-tracked individuals. Horizontal projection was selected per cohort from median coordinates before numeric height was parsed.

For *Hypsignathus monstrosus* (Schloesing et al. 2023; repository DOI 10.5441/001/1.278), the structural screen retained 32 animals with native ellipsoid height, including 24 with repeated eligible sessions. The primary admitted context was Lek Njoukou in 2020. The same session, cohort, grid, smoothing and scoring logic was frozen before numeric height outcomes were opened.

For the species-level *Phyllostomus hastatus* replication, the 2021–2022 dataset (Calderón-Capote et al. 2024; repository DOI 10.5441/001/1.321) was selected among three structurally passing *Phyllostomus* sources because it had the largest repeat-individual panel before height outcomes were examined. The primary vertical field was height above MSL. The frozen biological prediction was conditional dominance, using the same four-part direction rule applied to independent replications.

After the 2022 result was known, the 2023 dataset (Calderón-Capote et al. 2024; repository DOI 10.5441/001/1.322) was frozen as a within-species temporal replication before its numeric height outcomes were opened. Its native vertical field was height above ellipsoid.

A further prospective test used an untouched 2016 dry-season panel from O'Mara and Dechmann (2023; repository DOI 10.5441/001/1.282). This test was not a generic retry of the original prediction. Instead, after the 2022 panel had produced a marginal-dominant result, we froze the specific prediction that a similar marginal-dominant architecture would recur in an earlier dry-season panel. The rule required positive mean marginal identity, a majority of marginal-positive individuals, negative mean conditional advantage, a majority of negative individual conditional advantages, and marginal identity greater than conditional identity. Failure was retained without retuning.

Because the source archives use MSL, ellipsoid and, for the focal semantic validation, AGL height, we do not compare absolute flight heights among taxa. Cross-system comparisons concern predictive architecture and sign/direction of information contrasts.

### Replication criteria and scale sensitivities

The independent *Eidolon* and *Hypsignathus* replication rules required at least 15 evaluable individuals, positive mean conditional identity, more than half of individual conditional gains positive, positive mean conditional advantage, and conditional identity greater than marginal identity. The primary cell size was 5 km; 2.5- and 10-km results were frozen sensitivities and could not redefine a failed primary result.

The *Phyllostomus* 2022 panel was evaluated under the same place-conditioned prediction. Its failure is therefore part of the comparative result rather than a basis for changing the rule. The 2023 and 2016 panels were prospectively defined follow-ups with their own frozen roles.

### Ethics provenance of the source tracking datasets

This study conducted no new capture, handling or instrumentation. We nevertheless traced the animal-use approvals reported for each source tracking programme. The focal *T. teniotis* study states that all methods were approved by ICNF—Instituto de Conservação da Natureza e Florestas, Portugal—under permit 665/2017/CAPT (O'Mara et al. 2021).

The *E. helvum* tracking programme followed local requirements and American Society of Mammalogists guidance. Work in Ghana was approved by the Wildlife Division of the Forestry Commission (FCWD/GH-01 24/08/09 and 02/02/11) and the Veterinary Services of the Ghana Armed Forces Medical Directorate; work in Zambia was approved by the Zambia Wildlife Authority (ZAWA 421902, 29/11/13; ZAWA 547649, 26/11/14); and work in Burkina Faso was conducted with approval of the Director of Parc Urbain Bangr-Weoogo, Ouagadougou (O'Mara et al. 2019).

The *H. monstrosus* source study reports approval by the Ministry of Agriculture, Livestock and Fisheries of the Republic of Congo and by the French VetAgro Sup ethics committee (approval 1805-V2, 3 July 2018), noting that no animal ethics committee existed in the Republic of Congo at that time (Schloesing et al. 2023).

For the 2016 *P. hastatus* tracking, work was approved by the Ministerio del Ambiente, Panamá (SE/A-96-15) and the Smithsonian Tropical Research Institute Animal Care and Use Committee (2014-0701-2017), and followed the ASAB/ABS Guidelines for the Use of Animals in Research (O'Mara & Dechmann 2023). The longitudinal 2021–2023 *P. hastatus* programme reports Ministerio del Ambiente permits SE/A-96-15, SE/A-96-18 and SE/A-38-2020 and STRI Animal Care and Use Committee approvals 2014-0701-2017, 2017-0815-2020-A2 and 2020-0212-2023, again under the ASAB/ABS guidelines (Calderón-Capote et al. 2024).

### Reproducibility and analysis freeze

All source identities, bitstreams, checksums, structural screens, analysis contracts and terminal result records are preserved in the public repository. The public bat source search was closed after the fixed source universe had been structurally screened. No new public candidate may enter this manuscript programme after comparative outcomes were observed.

The empirical programme was frozen before manuscript expansion. Post-freeze work is restricted to claim reconciliation, figures, manuscript text, references, provenance, software tests and submission packaging. Negative results—including the focal residual-map endpoint, the focal common-uplift endpoint and the 2016 prospective *Phyllostomus* prediction failure—remain in the main interpretation.

## Results

### Outcome-blind screening yielded four taxa with repeated vertical tracking

The source search identified 23 Movebank parent datasets with plausible bat movement records. Nineteen exposed raw event streams directly, while four legacy packages required recovery through child handles. Six sources from four taxa passed the fixed same-event x-y-height and repeat-tracking gate. The admitted taxa were *T. teniotis*, *E. helvum*, *H. monstrosus* and *P. hastatus*; the latter was represented by three temporal datasets.

The screen excluded many biologically interesting datasets before numeric height outcomes were inspected. Some lacked a native vertical coordinate in the public event stream. Others contained too few repeated individuals. For example, a Brazilian free-tailed bat dataset contained seven reference animals and no native height field in the public GPS table. This constrained the panel by data architecture rather than by favourable vertical outcomes.

### Focal individual identity predicts later conditional vertical state

The focal early/late identity-assignment test strongly rejected exchangeability of individualized conditional maps (Figure 2). The observed identity-matched diagonal mean gain was +0.1682 nats per event. Six of eight bats had positive own-map gains, and the correct source map was the strict top-ranked predictor for five of eight targets. Across all 40,320 identity assignments, the one-sided exact permutation probability was p = 0.000174.

Thus, an early conditional vertical map from the correct bat contained information about that bat's later vertical state beyond the population conditional baseline. The result establishes temporally repeatable individual identity in the focal three-dimensional movement data, while leaving open which component of movement generated that identity.

### Session-level focal identity is conditional-dominant

The separate leave-one-session-out analysis gave a strongly conditional-dominant focal architecture at 5 km (Figure 3). In MSL coordinates, mean conditional identity was +0.428 nats/fix and marginal identity was +0.052, yielding a conditional advantage of +0.376. Five of six evaluable individuals had positive conditional self-transfer.

The terrain-relative analysis returned the same qualitative direction. AGL conditional identity was +0.337, whereas marginal AGL identity was -0.255, producing a conditional advantage of +0.591. Therefore an animal-wide AGL distribution was not, on average, a useful self-signature, but horizontal conditioning increased individual predictive information substantially.

Terrain elevation alone did not reproduce the vertical result. At 5 km, terrain-elevation conditional identity was +0.007, compared with +0.337 for AGL and +0.428 for MSL. At 2.5 km some terrain repeatability appeared, but it remained much smaller than the vertical conditional signals. The focal architecture therefore cannot be reduced to repeatedly crossing the same sub-cell ground elevations.

### The focal conditional signal survives context and comparison controls

The same-night control also favoured individual history over contemporaneous alternatives. In AGL, another night from the same bat outpredicted other bats flying during the target night by +0.484 nats/fix on average, with four of five evaluable individual means positive. The equivalent MSL gain was +0.436, again with four of five positive.

Direct pairwise comparisons removed the pooled alternative distribution (Figure 4). For MSL, the mean conditional self-versus-alternative gain was +0.643, compared with +0.096 marginally, yielding a pairwise conditional advantage of +0.546. The conditional self-win fraction was 0.776. In AGL, the conditional pairwise gain was +0.611, the marginal gain -0.196 and the conditional advantage +0.807; the conditional self-win fraction was 0.736.

These controls show that the session-level architecture is not produced solely by a shared calendar-night state or by averaging heterogeneous comparison individuals.

### The stronger focal residual-map claim is not supported

The independently frozen residual refinement placed a stricter limit on interpretation (Figure 2). After each bat's marginal altitude identity was absorbed into its cell-specific baseline, the identity-matched residual gain was only +0.0240 nats/event. Five of eight diagonal residuals were positive, but the exact identity-assignment permutation probability was p = 0.160. The support rule therefore failed.

The result did not become positive under the frozen shrinkage sensitivities. With lambda = 5, the residual diagonal gain was -0.0330 with p = 0.248; with lambda = 50 it was +0.0422 with p = 0.065. Sensitivities could not replace the primary endpoint.

Accordingly, the focal dataset supports repeatable conditional vertical identity and a positive session-level conditional advantage, but it does not establish one temporally stable individual-specific cell-by-height residual map after marginal altitude identity is controlled.

The common uplift reaction-norm mechanism was also not established. Only Bat7 and Bat8 passed the predeclared within-session wind-variation gate across repeated sessions. Their cross-night slope-prediction results had opposite signs, the equal-individual slope-error improvement was small, and the permutation test for slope identity gave p = 0.334. We therefore retain atmospheric mechanism as open rather than using wind response to explain the focal identity pattern.

### Conditional dominance replicated prospectively in *Eidolon helvum*

The first independent replication was supported under every frozen criterion. Twenty *E. helvum* individuals remained evaluable after cohorting and common-horizontal-support scoring. Mean conditional identity was +0.219 nats/fix, marginal identity was +0.002 and conditional advantage was +0.217 (Figure 3). Seventeen of 20 individual conditional gains were positive.

The qualitative result occurred across the admitted African site-year cohorts rather than being generated by one pooled geographical contrast. Every cohort with at least one evaluable individual had a positive cohort-mean conditional gain. Scale sensitivities were also positive: conditional identity was +0.297 at 2.5 km and +0.173 at 10 km.

Direct pairwise scoring strengthened the same architecture (Figure 4). Conditional self-versus-alternative gain was +0.398, marginal gain +0.013 and conditional advantage +0.385. The conditional self-win fraction was 0.875. Thus the conditional-dominant result does not depend on a pooled comparison distribution.

### A second independent taxon was also conditional-dominant

*Hypsignathus monstrosus* produced a weaker but directionally consistent prospective replication. Twenty-four individuals were evaluable. At 5 km, mean conditional identity was +0.029 nats/fix, marginal identity was -0.021 and conditional advantage was +0.050 (Figure 3). Thirteen of 24 individual conditional gains were positive, satisfying the frozen majority criterion.

The architecture was strongest at finer horizontal conditioning. At 2.5 km, conditional identity was +0.131 and conditional advantage +0.152; at 10 km, conditional identity declined to +0.010 and conditional advantage to +0.030 (Figure 6). Pairwise analysis again retained conditional dominance, with +0.115 conditional gain versus +0.008 marginal gain and a conditional advantage of +0.107 (Figure 4).

The smaller 5-km magnitude relative to *Tadarida* and *Eidolon* cautions against treating conditional dominance as one fixed effect size. The replicated feature is its direction and predictive organization.

### *Phyllostomus hastatus* 2022 was marginal-dominant

The prospectively frozen 2022 *P. hastatus* panel did not replicate the conditional-dominant prediction. Thirty-three individuals were evaluable. Mean conditional identity was +0.056 nats/fix, but marginal identity was substantially larger at +0.176, giving a negative conditional advantage of -0.120 (Figure 3). Only 14 of 33 individual conditional gains were positive, so the frozen place-conditioned replication rule failed.

This failure was not absence of individual vertical information. Direct pairwise comparisons showed strong self-information in both scores, but marginal identity remained stronger: conditional pairwise gain was +0.285 and marginal pairwise gain +0.323, giving a pairwise conditional advantage of -0.038 (Figure 4). Thus the same animal's overall vertical distribution was more informative than the additional location-conditioned contrast.

The direction was also stable across frozen horizontal scales. Conditional advantage was -0.094 at 2.5 km, -0.120 at 5 km and -0.121 at 10 km (Figure 6). *P. hastatus* 2022 therefore provides a clear counterexample to a universal conditional-dominant architecture.

### Architecture varied across *Phyllostomus* temporal panels

A separate 2023 *P. hastatus* panel shifted toward weak conditional dominance. Sixteen individuals were evaluable. Conditional identity was +0.033 nats/fix, marginal identity +0.013 and conditional advantage +0.020 at 5 km (Figures 3 and 5). Pairwise scoring made the contrast more pronounced: conditional gain +0.148, marginal gain +0.028 and conditional advantage +0.120.

However, architecture did not simply correspond to a recurring seasonal state. After the 2022 marginal-dominant outcome had been observed, we froze a specific prediction for an untouched 2016 dry-season panel: if the 2022 pattern represented a stable dry-season architecture, the 2016 panel should again be marginal-dominant.

That prediction failed (Figure 5). Ten individuals were evaluable in the admitted La Gruta 2016 cohort. Conditional identity was +0.058, marginal identity +0.016 and conditional advantage +0.041. Sixty per cent of individuals were marginal-positive, but only half had negative individual conditional advantages, and mean marginal identity did not exceed mean conditional identity. The predefined 2022-like rule therefore failed.

Spatial scale changed the 2016 direction: conditional advantage was -0.050 at 2.5 km but +0.041 at 5 km and +0.097 at 10 km (Figure 6). Because the primary 5-km prediction had been frozen in advance, this sensitivity cannot rescue the failed seasonal prediction. Instead it reinforces the conclusion that predictive architecture can be context- and scale-dependent.

## Discussion

### Vertical individual specialization has more than one predictive architecture

Across the admitted bat systems, the main generality is not one universal form of vertical specialization. Individual vertical identity recurs across nights, but the information can be organized differently. In *Tadarida*, *Eidolon* and *Hypsignathus*, horizontal context increases self-versus-other vertical information: these systems are conditional-dominant. In the 2022 *Phyllostomus* panel, the opposite occurs: an animal-wide vertical distribution is more informative than the additional location-conditioned contrast.

This distinction expands the ecological idea of individual specialization. Individual specialization is often summarized as a magnitude—how narrow an individual's realized niche is relative to the population, how little individuals overlap, or how repeatable a space-use metric becomes. Our results show that two populations can contain repeatable individual vertical information while differing in **where that information is expressed**. Predictive architecture is therefore a complementary dimension of individual specialization, not a replacement for specialization magnitude.

The vertical axis is especially useful for exposing this distinction because horizontal and vertical space are coupled but not redundant. Ecological conditions can change sharply with height, and vertical position can alter energetic costs, microclimate, resource access or exposure to atmospheric structure (Gámez & Harris 2022; Xing et al. 2023). For an animal moving through such a landscape, a repeated vertical distribution may represent one form of individual organization, while repeated context-dependent vertical prediction may represent another. The present study does not identify the underlying process, but it shows that these predictive forms can be empirically separated.

### Population vertical niches can be thick without being individually exchangeable

The study also changes how the motivating focal result should be read. A vertically thick population distribution need not imply one shared broad individual niche. The population can be thick partly because it overlays heterogeneous individuals. If so, averaging across animals may preserve descriptive support while weakening transfer to a new individual.

In *Tadarida*, the earlier pooled population P(z|x,y) failed to transfer to two sealed bats, while the present early/late identity test shows that correct individual identity contains repeatable later information. These statements are not contradictory. The first concerns transferability of a population map; the second concerns within-individual predictability. Their combination demonstrates why population support and individual exchangeability are different ecological properties.

This point generalizes beyond bats. Many movement analyses estimate one utilization distribution, habitat-selection function or movement-state surface for a population or treatment group. Such models can be useful summaries even when individuals differ. But when management or ecological interpretation depends on generalizing to new individuals, population averages can hide structured non-exchangeability. A predictive self-versus-other design offers one way to diagnose this problem.

### Conditional dominance is not evidence for one fixed route mechanism

The focal system is deliberately informative because one tempting interpretation fails. The session-level analyses, AGL control, same-night comparison and pairwise comparisons all show that horizontal context adds predictive information. It would be easy to call this a stable place-specific route strategy. The frozen residual-map test prevents that inference.

After marginal altitude identity was explicitly incorporated into the baseline, the individual-specific cell-by-height residual did not pass the identity-assignment test. The difference between these estimands matters. G_adv asks whether horizontal conditioning improves predictive self-information relative to a marginal score. The residual test asks whether one particular individual-specific cell-by-height deviation is itself temporally stable. The former can be positive while the latter fails.

Several biological configurations could create conditional dominance without one fixed map. Individuals could repeat broad movement corridors while shifting fine-scale altitude with weather; they could use persistent resource regions but vary vertical response within them; or different components of horizontal fidelity, atmospheric conditions and altitude preference could combine predictively. Carrasco (2024) makes a related point for trajectory repeatability: movement paths reflect many repeated decisions under changing intrinsic and extrinsic conditions, so repeatability need not imply literal path duplication or an obvious single cause.

The negative uplift reaction-norm result reinforces this caution. A single repeatable relationship between modelled vertical wind and climb rate did not explain the focal pattern under its predeclared gate. This does not show that wind is irrelevant—indeed the source study demonstrates the ecological importance of topography and nocturnal uplift (O'Mara et al. 2021). It shows only that one common cross-night slope mechanism is insufficient to explain the individual predictive architecture detected here.

### Context dependence occurs within a species

The *Phyllostomus* panels provide the strongest reason not to turn predictive architecture into a species label. The 2022 panel was clearly marginal-dominant under both population-baseline and pairwise analyses. The 2023 panel shifted toward conditional dominance. More importantly, an untouched 2016 dry-season panel failed a prospectively frozen prediction that the 2022 architecture would recur under another dry-season context.

This failed prediction is biologically useful. A post hoc narrative could easily have attributed the 2022 result to dry-season ecology. The prospective 2016 test blocks that simple explanation. Year, colony composition, local resource geography, social context, instrumentation and atmospheric conditions remain potential contributors. Because these factors were not experimentally separated, we do not assign causation among them.

Context-dependent architecture is consistent with a broader literature showing that individual specialization can vary through time. Wang et al. (2023), for example, showed seasonal changes in spatial niche specialization in another bat species. Our result differs in focus: the changing property here is the balance between marginal and conditional predictive identity rather than specialization magnitude alone. That distinction creates a new prospective question: can the same individuals switch architecture when their ecological context changes?

### Scale is part of the architecture, not a nuisance parameter

The frozen scale analyses show that horizontal grain affects how vertical identity is expressed. *Tadarida* AGL and *Hypsignathus* were strongest at 2.5 km and weakened with coarser conditioning. *Eidolon* remained conditional-positive through 10 km. *Phyllostomus* 2022 remained marginal-dominant from 2.5 to 10 km, whereas the 2016 panel changed sign across scales.

With four taxa, these patterns are not sufficient for a comparative trait regression. We therefore treat them as exploratory. Nonetheless, they make an important conceptual point: an individual's predictive architecture is defined relative to spatial grain. Conditioning at a scale coarser than relevant movement decisions can erase local information, whereas excessively fine grids can reduce shared support. Future comparative work should therefore treat the spatial scale of vertical individuality as an ecological trait to be estimated, not merely a technical choice.

Candidate drivers include movement extent, route fidelity, resource patchiness, topographic complexity and flight mode. Testing those drivers will require a larger prospectively assembled panel with harmonized vertical references and enough repeated individuals to estimate scale profiles independently of source-study design.

### Strengths and limitations of the public comparative design

The main strength of the comparative extension is not taxonomic breadth by itself, but its source-selection discipline. The source universe was screened before numeric vertical outcomes were used for admission, and it was closed after the comparative outcomes were observed. The admitted panel therefore contains successful replications, a failed independent prediction and a failed within-species prospective prediction. That pattern would be difficult to interpret if datasets had been added adaptively after every result.

The same design also creates limitations. Only four taxa pass the fixed public-data gate, so this is not a phylogenetic comparative study. Source tracking schedules, regions and vertical reference systems differ. Ellipsoid, MSL and AGL heights cannot be treated as identical physical measurements across taxa. We therefore compare predictive architecture rather than absolute height or effect magnitude.

Behavioural state is also not harmonized. Although several source studies concern foraging or commuting, the central analysis uses GPS vertical state and does not impose a common validated foraging classifier. The appropriate claim is therefore individual specialization in vertical flight or airspace use, not verified foraging-height specialization.

Finally, observational repeatability cannot identify personality, learning, optimality or adaptive benefit. Individual identity can persist because of intrinsic differences, experienced environments, social context, route history or combinations of these. Our framework detects non-exchangeability and predictive organization; it does not determine why individuals differ.

### A prospective research programme

The highest-value next step is not further mining of public bat datasets. The present public source universe is frozen, and continuing to search after seeing the architecture contrast would undermine the outcome-blind comparative logic.

A stronger design would repeatedly track the same individuals across deliberately contrasting contexts. Such a study could estimate G_cond and G_marg within individual across seasons, resource states or atmospheric regimes and ask whether architecture switches within the same animal. Terrain-relative height should be measured directly or with harmonized high-resolution topography, and behavioural classification should distinguish foraging, commuting and other flight modes. Simultaneous atmospheric data would allow environmental reaction norms to be tested without the low within-night wind variation that limited the focal mechanism endpoint.

This design would shift the question from whether architectures differ among available panels to whether predictive architecture is itself a plastic individual trait. It would also permit explicit tests of ecological drivers rather than relying on source-study contrasts.

## Conclusion

Individual vertical identity in bat airspace has multiple predictive architectures. Across nights, identity can be more informative in a location-conditioned vertical distribution than in an animal-wide height distribution, or vice versa, and that balance can vary among systems and over time. The result is not a claim that every bat carries one fixed three-dimensional route map. Instead, it shows that population vertical space use can contain repeatable, non-exchangeable individual information whose spatial organization differs across ecological contexts.

Treating individual specialization only as a single magnitude can miss this distinction. Separating marginal and conditional predictive identity reveals whether individuality is already visible in overall vertical use or emerges only once horizontal context is supplied. That predictive architecture provides a tractable way to study the third spatial dimension of individual ecology while keeping mechanism, repeatability and population generality analytically distinct.

## References

Bolnick, D.I., Svanbäck, R., Fordyce, J.A., Yang, L.H., Davis, J.M., Hulsey, C.D. & Forister, M.L. (2003). The ecology of individuals: Incidence and implications of individual specialization. *The American Naturalist*, **161**, 1–28. https://doi.org/10.1086/343878

Carrasco, J.L. (2024). Assessing repeatability of spatial trajectories. *Methods in Ecology and Evolution*, **15**, 144–152. https://doi.org/10.1111/2041-210X.14266

Gámez, S. & Harris, N.C. (2022). Conceptualizing the 3D niche and vertical space use. *Trends in Ecology & Evolution*, **37**, 953–962. https://doi.org/10.1016/j.tree.2022.06.012

Kerches-Rogeri, P., Niebuhr, B.B., Muylaert, R.L. & Mello, M.A.R. (2020). Individual specialization in the use of space by frugivorous bats. *Journal of Animal Ecology*, **89**, 2584–2595. https://doi.org/10.1111/1365-2656.13339

Mordue, S., Mill, A., Shirley, M. & Aegerter, J. (2023). Foraging fidelity and individual specialisation in a temperate bat *Myotis nattereri*. *European Journal of Wildlife Research*, **69**, 121. https://doi.org/10.1007/s10344-023-01744-5

O'Mara, M.T., Scharf, A.K., Fahr, J., Abedi-Lartey, M., Wikelski, M., Dechmann, D.K.N. & Safi, K. (2019). Overall dynamic body acceleration in straw-colored fruit bats increases in headwinds but not with airspeed. *Frontiers in Ecology and Evolution*, **7**, 200. https://doi.org/10.3389/fevo.2019.00200

O'Mara, M.T., Amorim, F., Scacco, M., McCracken, G.F., Safi, K., Mata, V., Tomé, R., Swartz, S., Wikelski, M., Beja, P., Rebelo, H. & Dechmann, D.K.N. (2021). Bats use topography and nocturnal updrafts to fly high and fast. *Current Biology*, **31**, 1311–1316.e4. https://doi.org/10.1016/j.cub.2020.12.042

O'Mara, M.T. & Dechmann, D.K.N. (2023). Greater spear-nosed bats commute long distances alone, rest together, but forage apart. *Animal Behaviour*, **204**, 37–48. https://doi.org/10.1016/j.anbehav.2023.08.001

Schloesing, E., Caron, A., Chambon, R., Courbin, N., Labadie, M., Nina, R., Mouiti Mbadinga, F., Ngoubili, W., Sandiala, D., N'Kaya Tobi, Bourgarel, M., De Nys, H.M. & Cappelle, J. (2023). Foraging and mating behaviors of *Hypsignathus monstrosus* at the bat-human interface in a central African rainforest. *Ecology and Evolution*, **13**, e10240. https://doi.org/10.1002/ece3.10240

Calderón-Capote, M.C., van Toor, M.L., O'Mara, M.T., Bayer, T.D., Crofoot, M.C. & Dechmann, D.K.N. (2024). Consistent long-distance foraging flights across years and seasons at colony level in a neotropical bat. *Biology Letters*, **20**, 20240424. https://doi.org/10.1098/rsbl.2024.0424

Wang, Z., Gong, L., Huang, Z., Geng, Y., Zhang, W., Si, M., Wu, H., Feng, J. & Jiang, T. (2023). Linking changes in individual specialization and population niche of space use across seasons in the great evening bat (*Ia io*). *Movement Ecology*, **11**, 32. https://doi.org/10.1186/s40462-023-00394-1

Xing, S., Leahy, L., Ashton, L.A., Kitching, R.L., Bonebrake, T.C. & Scheffers, B.R. (2023). Ecological patterns and processes in the vertical dimension of terrestrial ecosystems. *Journal of Animal Ecology*, **92**, 538–551. https://doi.org/10.1111/1365-2656.13881

## Figure legends

**Figure 1. From pooled vertical airspace to predictive individual identity.** Conceptual distinction between a vertically thick pooled population distribution, individual non-exchangeability, marginal vertical identity and location-conditioned vertical identity. Conditional advantage is defined as conditional minus marginal predictive identity. A positive conditional advantage indicates that horizontal context adds self-information; it is not equivalent to proof of a stable latent individual-specific cell-by-height map.

**Figure 2. Repeatable focal identity and the stronger residual-map test in *Tadarida teniotis*.** Individual early-to-late conditional identity gains relative to the population predictor are shown alongside residual cell-by-height gains after each bat's marginal altitude identity is absorbed. The identity-assignment test is strongly supported (exact p = 0.000174), whereas the stronger residual-map test is not (p = 0.160).

**Figure 3. Predictive architectures of cross-night vertical identity.** The x-axis is marginal self-versus-other identity gain; the y-axis is conditional advantage (conditional minus marginal gain). Positive y-values indicate conditional-dominant architecture. The 2022 *Phyllostomus hastatus* panel is marginal-dominant, whereas the focal *Tadarida* and independent *Eidolon* and *Hypsignathus* panels are conditional-dominant.

**Figure 4. Pairwise architecture after removing the pooled alternative-individual baseline.** Each self predictor is compared directly with individual alternative bats on common horizontal support. The qualitative architecture directions persist, showing that conditional- versus marginal-dominance is not created by averaging heterogeneous alternative individuals.

**Figure 5. Temporal variation in *Phyllostomus hastatus* predictive architecture.** Marginal identity and conditional advantage are shown for the 2016, 2022 and 2023 panels. The untouched 2016 dry-season panel was prospectively frozen to reproduce the 2022 marginal-dominant architecture and failed the predefined prediction.

**Figure 6. Exploratory spatial grain of conditional vertical identity.** Conditional identity is shown across 2.5-, 5- and 10-km horizontal conditioning cells. Scale profiles differ among panels and are treated as hypothesis-generating rather than as a four-taxon trait regression.

## Ethics statement

This study is a secondary analysis of publicly archived animal-tracking data and involved no new capture, handling or experimental manipulation of animals. The original tracking programmes were conducted under the permits and institutional approvals detailed in Materials and Methods, including ICNF Portugal, national wildlife authorities in Ghana, Zambia and Burkina Faso, the Republic of Congo and VetAgro Sup, and Ministerio del Ambiente Panamá and the Smithsonian Tropical Research Institute Animal Care and Use Committee. The present analyses use only published tracking measurements and source animal identifiers.

## Data and code availability

All tracking data analysed here are publicly archived in the Movebank Data Repository. The focal *Tadarida teniotis* data are available at DOI 10.5441/001/1.52nn82r9. Independent comparative sources include *Eidolon helvum* (10.5441/001/1.k8n02jn8), *Hypsignathus monstrosus* (10.5441/001/1.278), and *Phyllostomus hastatus* panels archived under 10.5441/001/1.282, 10.5441/001/1.321 and 10.5441/001/1.322. Exact source bitstreams and checksums used by this study are recorded in the repository contracts and provenance files.

All analysis code, frozen contracts, source-screen records, result summaries and figure-generation scripts are maintained in the public GitHub repository zuizui0223/batter. A permanent versioned archive DOI should be minted from the submission release before journal submission.
