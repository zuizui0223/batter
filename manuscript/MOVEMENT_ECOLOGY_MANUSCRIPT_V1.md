# Repeatable individual signatures limit exchangeability of vertical movement-state maps in European free-tailed bats

**PUBLICATION STATUS: RETIRED AS A SEPARATE SUBMISSION.**

The central Tadarida V1/V2 early-to-late identity analyses in this draft are the same frozen analyses now incorporated into the JAE v0.4.0 comparative manuscript as the motivating/boundary case. Submitting both manuscripts as independent research articles would duplicate the same numerical result. This file is retained as an analytical precursor/provenance record only. See `prospective/public_causal_synthesis/PUBLICATION_OVERLAP_AUDIT_V1.md` on the public-causal-synthesis branch.

**Article type:** Research  
**Target:** Movement Ecology  
**Status:** submission-facing draft v1  
**Author metadata:** TODO

## Abstract

### Background
Population-level movement niches are often estimated by pooling tracked individuals, implicitly treating conspecific movement-state distributions as exchangeable. Individual specialization is well documented in horizontal space use, but less is known about whether three-dimensional movement structure transfers among individuals. A previous frozen analysis of European free-tailed bats (*Tadarida teniotis*) found a vertically thick population representation—4.02 effective altitude states after horizontal location was known—yet the pooled location-conditioned vertical map failed to improve prediction for two independently sealed bats. We asked whether this non-transferability reflected repeatable individual movement-state signatures.

### Methods
We reanalysed 10,335 publicly archived GPS records from eight bats using the same 18 frozen 5-km horizontal cells and fixed altitude-above-mean-sea-level bins as the preceding endpoint. Each individual was split chronologically into early and late observations. Early individual maps were scored against every individual's late observations, forming an 8 × 8 transfer matrix. Identity matching was tested exactly against all 8! permutations. Sequentially frozen follow-ups then asked whether the identity signal reduced to marginal altitude preference, horizontal space use, or an individual-by-location vertical interaction.

### Results
Correct identity matching improved conditional vertical-state prediction by 0.168 nats per event on average relative to the population cell-specific model (exact permutation P=0.000174); six of eight bats had positive own-map gains. However, after individual marginal altitude preference was absorbed into the baseline, the individual-by-location interaction was unsupported (P=0.160). Altitude-only and horizontal-only identity assignments were each more repeatable than random reassignment (P=0.0224 and P=0.00233), but each outperformed the corresponding population baseline for only four of eight bats.

### Conclusions
A vertically thick population movement niche contained repeatable individual signatures, but these signatures were composite rather than reducible to one stable altitude offset, horizontal distribution, or location-specific vertical map. Pooling conspecific tracking data can therefore preserve population breadth while obscuring partial individual non-exchangeability in three-dimensional movement structure.

**Keywords:** animal movement; bats; individual specialization; movement niche; repeatability; three-dimensional movement; vertical space use; *Tadarida teniotis*

## Background

Ecological populations are often represented as if conspecific individuals draw from one shared resource-use distribution. Individual-specialization theory instead emphasizes that a population niche can be a mixture of narrower and only partly overlapping individual niches [1,2]. This distinction matters because pooling individuals can preserve the apparent breadth of a population while concealing stable among-individual differences in resource use, habitat use or movement.

Movement data provide a particularly direct setting for this problem. Tracking studies have shown that bats can be individually specialized in their horizontal use of foraging areas and habitats. Kerches-Rogeri et al. [3], for example, showed substantial individual specialization in space use by frugivorous bats. Natterer's bats can repeatedly exploit individual-specific foraging areas and differ in habitat use [4], and seasonal tracking of great evening bats has linked changes in individual spatial specialization to population-level space-use niches [5]. These studies establish that individual specialization can be spatial, not only dietary.

Three-dimensional movement introduces an additional niche axis. For flying animals, altitude is not merely an annotation on a two-dimensional home range: it can reflect the atmospheric energy landscape, terrain, movement mode and access to different aerial environments. European free-tailed bats (*Tadarida teniotis*) provide a striking example. O'Mara et al. [6] showed that these bats exploit orographic uplift and can climb to very high altitudes during nocturnal flight. Their study demonstrated predictable environmental mechanisms of high-altitude movement at the population level.

A separate question is whether the resulting vertical-state organization is exchangeable among individuals. If all individuals use a common location-conditioned vertical distribution, pooling tracking data should produce a transferable population map. Conversely, if individual identity carries stable movement-state information, a population map may be descriptively broad yet transfer poorly to new individuals. This is a different question from whether population-level movement mechanisms exist: shared environmental responses and individual heterogeneity can coexist.

A preceding frozen analysis of the same public *T. teniotis* dataset provided the starting observation for this study. Using a prespecified 5-km horizontal grid, fixed altitude-above-mean-sea-level bins and equal weighting among model individuals, the population model retained 1.392 nats of vertical entropy conditional on horizontal location, equivalent to 4.02 effective vertical states. Thus the fitted population representation was vertically thick. However, its location-conditioned vertical distribution did not improve held-out log score relative to the population marginal altitude distribution for either of two independently sealed bats. That analysis therefore established population-level vertical thickness but not transferable population-level vertical organization.

Here we ask whether this apparent contradiction can be understood through individual heterogeneity. We test three nested questions. First, does an individual's earlier conditional vertical-state map predict that same individual's later observations better than maps learned from other conspecifics? Second, if identity matching is present, does it persist after each individual's overall altitude distribution is already represented, implying a stable individual-by-location vertical interaction? Third, can the identity signal be reduced to either marginal altitude preference or horizontal site use alone?

We use predictive exchangeability as the organizing concept. Rather than defining individual specialization solely by overlap indices, we ask whether individual labels can be exchanged without loss of out-of-time predictive information. This approach connects population niche heterogeneity to a concrete forecasting consequence: when is a map learned from one individual a defensible predictor for another?

## Methods

### Study system and public tracking data

We analysed the publicly archived GPS tracking dataset associated with O'Mara et al. [6], available from the Movebank Data Repository under DOI 10.5441/001/1.52nn82r9 [7]. The checksum-pinned primary event stream contained 10,335 GPS locations from eight European free-tailed bats. The original tracking design recorded latitude, longitude, timestamp and GPS height above mean sea level on the same event.

This study is a secondary reanalysis. No new animals were captured, handled or tracked. We use the native GPS height-above-mean-sea-level field. We do not interpret this variable as height above ground, canopy-relative flight height, or a direct measure of habitat preference.

### Frozen horizontal and vertical state representation

To preserve separation from outcome-dependent tuning, the follow-up inherited the exact spatial and vertical representation of the preceding ODSP endpoint.

Horizontal positions were projected to EPSG:3035 and assigned to 5-km cells. We retained the 18 cells frozen by the preceding model-pool support criterion. The vertical axis used the same fixed altitude bands:

<0, 0–50, 50–100, 100–200, 200–400, 400–800, 800–1600, 1600–3200, and ≥3200 m above mean sea level.

No cells or altitude thresholds were selected from the individual-identity results reported here.

Across all individuals, 5,473 events fell within the 18 frozen cells and entered the individual follow-up.

### Chronological within-individual split

For each of the eight bats, eligible events were sorted chronologically. The first floor(n/2) observations formed the early period and the remaining observations formed the late period. Every individual retained at least 100 observations in each half.

The late-period sample sizes were 187, 143, 276, 288, 238, 476, 525 and 276 events across the eight individuals.

The early period was used to construct predictive distributions; the late period was used only for scoring. This split tests temporal repeatability of individual differences rather than resubstitution to the same observations.

### Population and individual vertical-state distributions

All categorical distributions used a Jeffreys pseudocount of 0.5. Individual distributions were regularized toward population distributions using a fixed equivalent sample size λ=20 in the primary analysis, with λ=5 and λ=50 as prespecified sensitivities.

For each horizontal cell c, the population conditional distribution P_pop(z|c) was the equal-individual mean of early, smoothed within-cell vertical distributions among individuals represented in that cell. The population marginal P_pop(z) was the equal-individual mean of each bat's smoothed early marginal altitude distribution.

For individual i and cell c, an individual-specific conditional distribution P_i(z|c) was obtained by shrinking i's early within-cell altitude counts toward P_pop(z|c). If individual i had no early observation in cell c, the individual prediction equalled the population cell distribution. The corresponding individual marginal P_i(z) shrank the bat's early all-cell altitude counts toward P_pop(z).

This construction prevents sparse individual cell histories from generating zero probabilities and ensures that individual predictions retreat to the population model where individual information is unavailable.

### V1: identity transfer of conditional vertical-state maps

For every early source individual i and every late target individual j, we calculated the mean late-event log-score gain

G_ij = mean_j [ log P_i(z|c) - log P_pop(z|c) ].

The eight-by-eight G matrix is a transfer matrix: diagonal elements evaluate temporally matched individual prediction, while off-diagonal elements evaluate transfer of one bat's early map to another bat's later observations.

The primary statistic was the unweighted mean of the eight diagonal elements. We compared it with the exact null distribution generated by all 8! = 40,320 permutations assigning the eight early maps to the eight late individual identities. The one-sided P value was the fraction of assignments with mean gain at least as large as the observed identity-matched diagonal.

Before execution, support required P≤0.05 and positive diagonal gain for at least six of eight individuals. We also recorded how often the correct individual's early map was the strict best of the eight maps for that target.

### Sequential mechanism follow-ups

The following analyses were frozen sequentially after the preceding result was known. They should therefore be interpreted as transparent mechanism decomposition, not as independent replication of V1.

#### V2: individual-by-location interaction after marginal altitude control

A positive V1 result could arise because individuals simply occupy different overall altitude distributions. We therefore constructed an individual-marginal-adjusted cell baseline:

P_i,add(z|c) ∝ P_pop(z|c) × P_i(z) / P_pop(z).

This model combines the population cell-specific pattern with individual i's overall altitude distribution but contains no fitted individual-by-cell interaction.

The full individual model P_i,full(z|c) then shrank the individual's raw early cell-specific counts toward P_i,add(z|c).

For every source i and target j we scored

R_ij = mean_j [ log P_i,full(z|c) - log P_i,add(z|c) ].

The same exact 8! identity-assignment test was applied. Support required P≤0.05 and positive diagonal residual gain for at least six of eight individuals.

#### V3: marginal altitude and horizontal identity components

After V2, we separately tested two simpler identity components.

For marginal altitude identity, early P_i(z) was scored on each late target's altitude states relative to P_pop(z).

For horizontal identity, each individual's early distribution over the 18 frozen cells, P_i(c), was scored on each late target's horizontal cells relative to the population cell distribution P_pop(c).

Each component used the exact 8! identity assignment. The frozen support rule required P≤0.05 and positive diagonal gain relative to the population baseline for at least six of eight individuals. This dual requirement distinguishes relative identity matching from a claim that individual models generally outperform the population model.

### Reproducibility and analysis provenance

The V1, V2 and V3 contracts, executable analysis code, result records and exact-permutation logic are version controlled in the public `zuizui0223/batter` repository. All three analyses were rebuilt successfully in continuous integration before the paper branch was created.

V1 result fingerprint: `cab07a8f804143637362cd6a634333e9814864d12a6dda895c8893a718b3724b`.

V2 result fingerprint: `ba552559a73071d00a60bfe84e3b5a93f78ed0faa07845f89fd21a98dbac4c20`.

V3 result fingerprint: `e9f695ba284834981372b6232e8b0095607c5dc35b3413454927c0298b7f6b5e`.

### Use of generative AI

A generative AI system was used to assist with code review, repository organization and manuscript drafting from author-controlled analyses. All scientific decisions, source selection, interpretation and final responsibility remain with the human author(s). This statement should be reconciled with the journal's current disclosure requirements at submission.

## Results

### Population-level vertical thickness did not imply cross-individual exchangeability

The preceding frozen population analysis had estimated H(Z|X,Y)=1.3919 nats, equivalent to 4.022 effective vertical states after horizontal cell was known. Thus the population model was vertically broad rather than effectively one-dimensional.

Nevertheless, the population cell-specific vertical distribution had failed its original transfer endpoint: relative to the population marginal altitude distribution, the two sealed individuals had mean log-score gains of -0.4354 and -0.02194. The new analyses therefore began from a population representation that was descriptively thick but not demonstrably exchangeable across individuals.

### Correct individual identity strongly improved conditional vertical-state prediction

Under the primary λ=20 model, the identity-matched diagonal mean gain over P_pop(z|c) was +0.1682 nats per late event.

The exact permutation null had mean -0.03666, with its 5th and 95th percentiles at -0.15655 and +0.07073. Only 7 of the 40,320 possible identity assignments produced a mean at least as large as the observed diagonal, giving P=0.0001736.

Six of eight individuals had positive own-map gain over the population cell-specific distribution. The individual gains were +0.0248, +0.1545, -0.0815, -0.0408, +0.4618, +0.3537, +0.1645 and +0.3087 nats per event. For five of eight late individuals, the individual's own early map was the strict best-scoring map among all eight candidate source individuals.

The identity-assignment result was robust to the shrinkage sensitivities. At λ=5, the diagonal mean gain was +0.1297 with P=0.000942 and six of eight positive individual gains. At λ=50, it was +0.1576 with P=0.000149 and seven of eight positive gains.

### A stable individual-by-location vertical interaction was not supported

After each individual's marginal altitude distribution was explicitly absorbed into the baseline, the residual identity-matched individual-by-cell vertical interaction was much weaker.

At λ=20, the observed diagonal residual gain was +0.0240. The exact identity-assignment P value was 0.1605, five of eight individuals had positive residual gains, and the correct individual map was the strict best only once. The frozen support rule therefore failed.

Neither shrinkage sensitivity changed that conclusion. At λ=5, the diagonal residual was -0.0330 (P=0.2485; four of eight positive). At λ=50, the residual was +0.0422 (P=0.0651; five of eight positive).

Thus V1 should not be interpreted as evidence that each bat carries a distinct and stable location-specific vertical reaction map.

### Marginal altitude and horizontal space use retained identity matching but did not generally outperform population baselines

Marginal altitude identity was more repeatable than expected under random reassignment: the matched diagonal mean was -0.0311 compared with a permutation-null mean of -0.2197, with P=0.02245. However, only four of eight bats had positive own-altitude-model gain relative to the population marginal altitude distribution. The frozen support rule therefore failed.

Horizontal space use showed the same qualitative distinction even more strongly. The matched diagonal mean relative to the population horizontal distribution was -0.2980, whereas random identity assignments averaged -1.2793; exact P=0.002331. Yet again only four of eight individual diagonal gains were positive relative to the population baseline, so the component did not pass the support rule.

The sequential decomposition therefore ended with `unresolved_identity_mechanism`: correct identity matching is repeatable, but no single simple component was sufficient to explain the conditional V1 signal while also generally outperforming the population baseline.

## Discussion

### A thick population movement niche can contain non-exchangeable individuals

The main result is a distinction between population breadth and individual exchangeability. The pooled *T. teniotis* representation occupied approximately four effective vertical states conditional on horizontal location, yet the vertical-state map was not equally applicable to every conspecific. Correctly matching early and late individual identity generated substantially better predictions than nearly all possible identity permutations.

This is compatible with the central insight of individual-specialization theory: a broad population niche need not imply that every individual uses the full population niche in the same way [1,2]. Our result extends that logic to a predictive representation of three-dimensional movement. Instead of only asking how much individuals' utilization distributions overlap, we ask whether an individual movement-state map can be exchanged for another individual's map without predictive cost.

That distinction matters for movement models built from pooled telemetry. A pooled model may accurately describe the range of movement states available to a population while still smoothing over repeatable differences in how individual animals combine movement dimensions. Population breadth and transferability are therefore separate properties.

### The identity signature is real but composite

A simpler narrative would be that some bats are consistently high flyers and others low flyers. The decomposition does not support that as a sufficient explanation. Correctly matched marginal altitude distributions were much less poor than randomly mismatched ones, but only half of the bats improved on the population marginal. Likewise, horizontal space-use distributions carried strong identity matching but improved on the population baseline for only half of individuals.

At the other extreme, we found no robust evidence for eight distinct location-specific vertical reaction maps. Once each bat's marginal altitude tendency was already represented, the individual-by-location interaction failed the exact identity permutation test.

The individual signature therefore appears composite. Individual identity predicts the joint arrangement of states well enough to break exchangeability, while the population model remains a strong shrinkage target and no one low-dimensional component dominates the effect. This intermediate outcome is ecologically plausible: partial specialization need not partition a population into completely isolated individual niches.

### Relationship to bat individual-specialization studies

Previous bat studies have demonstrated individual specialization in planar space and habitat use. Frugivorous bats can specialize on different foraging locations and habitats [3], Natterer's bats show repeated use of individual foraging areas [4], and great evening bats show individual and seasonal structure in population space-use niches [5].

Our analysis adds a different question: whether a vertical movement-state representation, conditional on horizontal location, is exchangeable among individuals. The answer is only partly. That contribution is especially relevant for three-dimensional tracking because adding altitude creates more state space but not necessarily a single, transferable population distribution.

The present result also complements rather than challenges the environmental mechanism identified in the source *T. teniotis* study [6]. O'Mara et al. showed that topography and nocturnal uplift can predict high-altitude ascents. Shared response to those landscape and atmospheric opportunities can coexist with individual heterogeneity. Our analysis does not estimate those mechanisms again and cannot determine whether the repeatable signatures arise from sex, reproductive state, colony structure, prey fields, weather exposure, energetic condition, route learning or other causes.

### Predictive exchangeability as a measure of individual specialization

Individual specialization is often quantified through within-individual versus between-individual variance or overlap in utilization distributions. Predictive exchangeability provides a complementary criterion.

If individuals are exchangeable with respect to a niche representation, permuting individual-specific training maps among held-out individuals should not systematically reduce predictive performance. If correct identity matching performs unusually well, individual labels carry persistent ecological information.

The approach has two practical advantages. First, it separates descriptive difference from temporal repeatability: the model must predict later data. Second, it can be applied to multivariate movement-state distributions for which a single specialization index may obscure which axes matter.

At the same time, identity matching should not be equated with an individual model being universally preferable to a population model. Our V3 results illustrate why. Altitude and horizontal identities were strongly non-random in assignment tests, but the population distributions often gave better absolute predictions. A population model can therefore be an efficient statistical shrinkage target even when individuals are not fully exchangeable.

### Limitations

The most important limitation is the number of individuals. Eight bats permit an exact individual-label permutation test, but they provide limited information about population-level prevalence of specialization. This is one tracked system, and the same public dataset motivated the preceding population-level result. The present analyses are mechanism follow-ups, not independent replication.

Second, the vertical variable is height above mean sea level. Horizontal conditioning reduces some confounding by geographic position, but it does not transform altitude into height above local terrain. The original source study explicitly modelled topography and atmospheric conditions; our analysis intentionally does not substitute for that work.

Third, the early-late split tests repeatability over the available tracking interval, which was short relative to seasonal or lifetime movement. We therefore infer short-term temporal repeatability, not long-term individual specialization.

Fourth, V2 and V3 were designed sequentially after the earlier result was observed. Their value is transparent falsification of simpler mechanistic explanations, not an independent confirmatory family. The strongest preregistered-style evidence in the follow-up is the frozen V1 identity-transfer test.

Finally, we cannot identify the biological cause of individual differences. Repeated signatures can result from multiple mechanisms and should not be labelled personality, learning, adaptation or resource partitioning without additional data.

### Implications for three-dimensional movement ecology

Tracking technology increasingly resolves movement in more than two dimensions. As vertical, behavioural and environmental-state axes are added to movement models, an implicit choice becomes more consequential: should observations be pooled across individuals, or should individual state distributions be retained?

Our results suggest that this choice cannot be made from population niche breadth alone. A movement-state axis can be information-rich at the population level while its organization is only partly transferable among individuals.

For applications requiring prediction to new individuals, hierarchical models that explicitly quantify among-individual variation may therefore be preferable to either extreme of complete pooling or fully separate individual models. The population distribution can serve as a shrinkage target, while individual histories update predictions when evidence supports persistent deviations.

A useful next test is independent replication in another population or species with longer individual tracks and an explicit terrain-relative vertical axis. Such a design could estimate how often identity signatures persist across nights, seasons and colonies and could test whether specialization strength covaries with environmental opportunity or energetic context.

## Conclusions

European free-tailed bats occupied a vertically thick population movement niche, but their conditional vertical-state maps were not fully exchangeable. Correctly matched early individual maps predicted later vertical states much better than randomly reassigned conspecific maps, demonstrating short-term repeatable individual signatures in three-dimensional movement.

Those signatures were not explained by a single stable altitude preference, horizontal space-use distribution, or location-specific vertical interaction. The result is therefore best described as partial individual non-exchangeability within a broad population niche.

More generally, three-dimensional movement ecology should distinguish population state-space breadth from the transferability of its organization among individuals. A pooled niche can be broad and ecologically meaningful while still masking repeatable individual structure.

## List of abbreviations

GPS: Global Positioning System  
MSL: mean sea level  
ODSP: original multidimensional niche-geometry analysis from which the frozen state representation was inherited

## Declarations

### Ethics approval and consent to participate

This study is a secondary analysis of publicly archived animal-tracking data and involved no new animal capture, handling or experimentation. Ethical approvals and permits for the original field study are reported by O'Mara et al. [6]. The exact original approval/permit identifiers should be transcribed from the source publication or associated documentation before submission.

### Consent for publication

Not applicable.

### Availability of data and materials

The tracking data analysed in this study are publicly archived in the Movebank Data Repository at https://doi.org/10.5441/001/1.52nn82r9 [7]. Analysis contracts, executable code and frozen result records are maintained in the public `zuizui0223/batter` repository. A permanent archival DOI for the analysis repository should be inserted before submission.

### Competing interests

The authors declare that they have no competing interests. **[Confirm before submission.]**

### Funding

**[Complete funding statement before submission.]**

### Authors' contributions

**[Complete using author initials before submission.]**

### Acknowledgements

**[Complete before submission.]**

### Authors' information

Not applicable.

## References

1. Bolnick DI, Svanbäck R, Fordyce JA, Yang LH, Davis JM, Hulsey CD, Forister ML. The ecology of individuals: incidence and implications of individual specialization. Am Nat. 2003;161:1–28. doi:10.1086/343878.

2. Araújo MS, Bolnick DI, Layman CA. The ecological causes of individual specialisation. Ecol Lett. 2011;14:948–958. doi:10.1111/j.1461-0248.2011.01662.x.

3. Kerches-Rogeri P, Niebuhr BB, Muylaert RL, Mello MAR. Individual specialization in the use of space by frugivorous bats. J Anim Ecol. 2020;89:2584–2595. doi:10.1111/1365-2656.13339.

4. Mordue S, Mill A, Shirley M, Aegerter J. Foraging fidelity and individual specialisation in a temperate bat *Myotis nattereri*. Eur J Wildl Res. 2023;69:121. doi:10.1007/s10344-023-01744-5.

5. Wang Z, Gong L, Huang Z, et al. Linking changes in individual specialization and population niche of space use across seasons in the great evening bat (*Ia io*). Mov Ecol. 2023;11:32. doi:10.1186/s40462-023-00394-1.

6. O'Mara MT, Amorim F, Scacco M, McCracken GF, Safi K, Mata V, Tomé R, et al. Bats use topography and nocturnal updrafts to fly high and fast. Curr Biol. 2021;31:1311–1316.e4. doi:10.1016/j.cub.2020.12.042.

7. O'Mara MT, Amorim F, McCracken GF, Mata V, Safi K, Wikelski M, Beja P, Rebelo H, Dechmann DKN. Data from: European free-tailed bats use topography and nocturnal updrafts to fly high and fast. Movebank Data Repository. 2021. doi:10.5441/001/1.52nn82r9.
