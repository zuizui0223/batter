# Individual organization remains detectable across acute perturbations in bats

**Article type:** Research / comparative public-data reanalysis  
**Working target:** Behavioral Ecology / Proceedings of the Royal Society B  
**Status:** full manuscript draft v1  
**Author metadata:** to be completed before submission

## Abstract

Behavioral individuality is commonly defined by consistent differences among individuals, but consistency alone does not distinguish persistent individual organization from the context-specific behavior through which it is expressed. We reanalysed independent public bat experiments using source-level endpoints and null models frozen before numerical outcome opening. Across four controlled current-context manipulations—external sensory masking, graded acoustic masking, reversible auditory-midbrain perturbation, and altered navigation conditions—the true same-individual correspondence remained supported after shared condition shifts were removed. Cross-task analyses further showed that coarse individual movement organization could transfer where detailed realized trajectory geometry did not. Developmental evidence showed a different pattern. In two randomized bat experiments, environmental enrichment and access to auditory feedback altered behavioral phenotype in the source studies but did not produce a supported change in the total amount of multivariate individual differentiation under frozen reanalyses. A frozen laboratory-to-wild carrier bridge also failed, showing that persistent individual organization cannot be assumed to imply wild spatial niche differentiation. Together, these results support a layered view of behavioral individuality in which maintenance, developmental allocation, context-specific expression, and ecological consequence are empirically distinct. The strongest remaining uncertainty is formation: what determines which behavioral dimensions and historical trajectories become individualized for particular animals?

**Keywords:** animal personality; behavioral individuality; bats; development; individual specialization; perturbation; plasticity; public data

---

# Introduction

Individuals of the same species often differ repeatedly in how they move, forage, explore, communicate, or respond to environmental challenge. Such differences are central to research on animal personality, behavioral syndromes, individual specialization, and movement ecology. Yet "individuality" is often treated as if it were a single biological property: individuals differ, those differences are repeatable, and environmental change then either strengthens or weakens that repeatability.

That framing collapses several distinct questions.

First, there is a **formation** problem: how do between-individual differences arise, and how are they refined by developmental and personal history? Second, there is a **maintenance** problem: once an individual-specific organization exists, does it survive substantial changes in the current environment? Third, there is an **expression** problem: how is the persistent individual organization mapped into context-specific behavior? Finally, there is an **ecological consequence** problem: when do individual differences in behavior create measurable differences in habitat use, niche position, or spatial partitioning?

These layers need not move together.

Recent work makes the point increasingly clear. Environmental context can alter the covariance structure of behavior and thereby change the apparent structure of behavioral syndromes. Multivariate personality studies distinguish total among-individual variation from the orientation and geometry of that variation. Experimental work has also shown that population-level plasticity can coexist with relatively stable among-individual organization. More recently, Mathejczyk et al. showed that some behavioral individuality persists across large environmental-context changes in *Drosophila*, while Gallagher et al. showed that developmental predation stress in clonal Amazon mollies can shift mean behavior without changing the overall magnitude of individuality. Thus neither context-resistant individuality nor mean behavioral change without a corresponding change in individuality is, by itself, a new general principle.

The remaining challenge is to connect these ideas across causal layers.

Bats provide an unusual opportunity because multiple independent public experiments manipulate current sensory conditions, navigation context, developmental environment, and access to sensory feedback while retaining repeated individual measurements. At the same time, public tracking datasets allow tests of cross-task portability and wild spatial consequences. These systems are heterogeneous in species, endpoint, and sample size, but that heterogeneity can be informative if the inferential object is kept fixed: does biological identity remain predictive after a controlled change in context, and does a developmental treatment change the amount or allocation of individual differentiation?

We therefore assembled a comparative reanalysis programme based entirely on public bat data. Source-level endpoints, support rules, and null models were frozen before numerical outcomes were opened. We did not treat the programme as a prospectively preregistered meta-analysis; dataset discovery and the cross-study synthesis developed iteratively. Instead, we used prospective freezing within each source to prevent feature, subset, or endpoint selection after outcome inspection.

We asked four linked questions.

1. **History:** does personal history become more informative about later individual organization?
2. **Maintenance:** does individual correspondence remain detectable across controlled sensory or navigational perturbations?
3. **Portability:** does coarse individual organization transfer across tasks more robustly than detailed realized geometry?
4. **Development and consequence:** do developmental manipulations predict the amount of individual differentiation, and does laboratory individual organization map directly to wild spatial individuality?

The resulting evidence is strongly asymmetric. Maintenance under acute perturbation is repeatedly supported. Developmental manipulations alter phenotype but do not map simply onto the total amount of individualization. Coarse individual organization can transfer where detailed realized geometry does not. And the direct laboratory-to-wild bridge fails its frozen gate.

We use these contrasts to argue for a layered empirical view of behavioral individuality (Fig. 1).

---

# Methods

## Overview and evidence architecture

We reanalysed independent public datasets from multiple bat species. Each source was assigned to one primary causal layer before numerical analysis:

- developmental or history-dependent refinement;
- maintenance under controlled current-context perturbation;
- cross-task portability and expression;
- ecological consequence / wild spatial bridge.

Within each source, the biological unit was the individual bat. Trial-level, call-level, or GPS-level observations were used to estimate individual states or predictive summaries but were not treated as independent biological replicates.

Source-level endpoint definitions, support requirements, scaling rules, and permutation/randomization nulls were frozen before numerical outcome opening. Sequential mechanism decompositions performed after a primary result were explicitly labelled descriptive or exploratory and were not allowed to rescue failed primaries.

## Juvenile first-flight history

We used the public first-flight dataset associated with Harten et al. 2020 to test whether personal spatial history became progressively more informative over early independent movement.

The frozen primary was deliberately stronger than a simple test that own history predicts later movement.

For each of 14 structurally eligible juveniles, the primary statistic was the Spearman relationship between prior valid-day count and daily own-history predictive advantage over target valid-day ordinals 3–20.

The programme-level statistic was the equal-individual mean of these slopes.

The frozen support rule required:
- programme-level excess over the whole-history identity-permutation null > 0;
- one-sided permutation P <= 0.05;
- at least 70% of juveniles with positive individual slopes.

The primary null used 9,999 whole-history identity permutations within cohort.

A predeclared late-history secondary asked whether, over target ordinals 11–20, true recent personal history predicted later spatial use better than experience-matched conspecific histories.

A post-primary diagnostic, explicitly excluded from rescuing the primary, compared two equally sized two-day histories:
- the earliest two structurally valid movement days;
- the two immediately preceding the late target.

This diagnostic separated weak early seed persistence from later identity-specific updating.

## Randomized early-environment enrichment

We reanalysed the public dataset from Rachum et al. 2025.

The confirmatory cohort comprised Season-2 bats with complete Trials 1–3:
- 29 bats total;
- 14 enriched;
- 15 impoverished;
- City origin: 9 enriched / 10 impoverished;
- Country origin: 5 / 5.

The frozen multivariate behavioral vector contained exactly:
- Boldness;
- Exploration;
- Activity.

For bat (i), pre-treatment baseline was the mean of Trials 1 and 2. Post-treatment change was Trial 3 minus baseline.

All three traits were standardized using pooled pre-treatment Trials 1–2 only, without treatment labels. Trial 3 therefore never contributed to its own measurement scale.

To isolate individualization beyond a common treatment shift, we removed the mean change vector separately within the enriched and impoverished groups. Residual multivariate change-vector dispersion was then calculated within each treatment.

The primary contrast was:

[
D = V_{enriched} - V_{impoverished}.
]

Randomization preserved the observed treatment counts within origin strata. We used 199,999 PCG64 assignments with frozen seed 202610070817 and a +1 Monte Carlo convention.

Support required:
- (D>0);
- one-sided randomized (P le 0.05).

A post-primary descriptive decomposition allocated the observed total contrast across the three frozen traits. No trait-wise p-values were calculated.

A second descriptive secondary compared leave-one-out predictions of Trial 3 from:
- own baseline only;
- treatment-group post state only;
- own baseline plus a shared treatment-associated shift estimated from peers.

This secondary was not allowed to alter the primary verdict.

## Randomized developmental auditory-feedback manipulation

We reanalysed the public adult-vocal dataset associated with Elie et al. 2024.

Ten pups had been randomly assigned shortly after birth:
- 5 hearing / saline controls;
- 5 deafened / kanamycin;
- each treatment contained 3 females and 2 males.

The frozen adult representation used:
- all 28,091 good-microphone-quality vocalizations;
- exactly 28 source acoustic features;
- all 10 bats;
- whole repertoire.

For each bat we calculated a 28-D centroid from all finite calls. Every bat × feature cell required at least 100 finite calls; the actual minimum was 1,037.

Feature scaling was treatment-blind across the 10 bat centroids.

To separate individuality from shared sex and treatment state, we removed the sex × treatment centroid. The amount of residual individualization within treatment was the average squared norm of each bat's residual 28-D state.

The primary contrast was:

[
D = V_{hearing} - V_{deaf}.
]

The exact randomization preserved sex balance:
- choose 3 of 6 females as hearing;
- choose 2 of 4 males as hearing;
- 120 legal assignments.

The primary used a two-sided exact test.

A post-primary descriptive decomposition allocated the total frozen (D) across all 28 features without feature-wise tests or feature selection.

## Pipistrellus sensory-masker perturbation

We used a public *Pipistrellus kuhlii* sensory-perturbation experiment in which individuals experienced a masker manipulation.

The primary source-native movement endpoint was individual angle of approach / movement bias under baseline and masker conditions.

The inferential object was same-individual retention:
after a shared treatment shift, was the manipulated state closer to that individual's own baseline state than to the states of other bats?

A second independent foam no-masker to foam+masker contrast was treated as a separate perturbation check.

## Myotis graded acoustic masking

We reanalysed the public *Myotis daubentonii* masking experiment.

The frozen endpoint was log flight time.

Only bats meeting the source-defined support architecture across all five noise conditions entered the confirmatory test. Three bats satisfied that frozen support rule.

For every noise level, the shared condition mean was removed. The primary then tested whether an individual's held-out state was better predicted by its own states in the other conditions than by other bats' histories.

The exact null permuted biological identity across conditions, yielding 1,296 legal assignments.

## Eptesicus reversible auditory-midbrain perturbation

We reanalysed Diebold, Lawlor et al. 2024.

Four DREADD-treated bats had public audio data in both saline and ligand conditions:
- jane;
- bea;
- jason;
- stella.

The frozen per-trial vocal vector was:
- mean call duration;
- mean bandwidth;
- mean inter-pulse interval;
- call rate.

Within each treatment × trialtype cell, pooled feature means were removed without using bat identity. Residuals were scaled by a common pooled residual SD.

For every bat, we calculated one 4-D saline centroid and one 4-D ligand centroid.

The primary statistic compared each ligand centroid with:
- its own saline centroid;
- the other three saline centroids.

All (4! = 24) saline-to-ligand identity mappings formed the exact null.

## Aharon navigation-context manipulation

We reanalysed Figure 1 from Aharon, Sadot & Yovel 2017.

The frozen first-eligible-figure rule selected Figure 1 before numerical values were opened.

The public source contained:
- 4 bats: 500, 503, 505, 510;
- 3 source-defined conditions: con, 75, 300;
- 10–15 trial columns per bat × condition.

All 12 bat × condition matrices passed the structural, finite-support, and zero-sentinel gates.

For each trial, the frozen bilateral turning-location vector contained:
- median finite turning position from odd-numbered source rows;
- median finite turning position from even-numbered source rows.

The bat × condition state was the equal-trial mean bilateral vector.

The shared condition mean was removed across the four bats.

For every target condition, a bat's history was the mean of its residual states in the other two conditions. Identity advantage was the difference between:
- average distance to other bats' histories;
- distance to its own history.

The exact null anchored con and independently permuted complete bat labels in the 75 and 300 conditions:

[
(4!)^2 = 576
]

legal identity mappings.

## Rhinolophus cross-task portability and Carollia external transfer

The controlled *Rhinolophus nippon* programme used a frozen transparent two-axis movement representation:
- FlightIntensity;
- ManeuveringExtent.

The cross-context question was whether individual organization in this low-dimensional policy space predicted held-out obstacle contexts.

A fixed representation was then transferred to an independent *Carollia perspicillata* dataset.

We also transferred a more detailed scale-free trajectory-geometry representation.

The contrast between coarse policy transfer and detailed-geometry transfer was treated as an expression/portability comparison rather than a universal latent-state claim.

## Wild field bridge

The frozen wild FlightIntensity carrier programme required support in at least 3 of 4 panels.

The frozen outcome was:
- PASS;
- PASS;
- FAIL;
- structural STOP.

Thus the field carrier gate failed at 2/4.

All subsequent H/V decomposition and carrier-positive-panel analyses were treated as post-outcome exploratory diagnostics and were not allowed to reopen the bridge.

## Cross-study synthesis rules

We did not calculate a pooled meta-analytic effect because endpoints differed fundamentally among sources.

Instead, the common object in the acute perturbation analyses was:

> same-individual correspondence after shared context effects were removed.

For every such source we report:
- biological n;
- direction of the programme statistic;
- positive-individual count;
- exact/randomization support.

The cross-study synthesis was developed iteratively as public datasets were audited and should not be interpreted as a preregistered meta-analysis.

---

# Results

## Late personal history was strongly informative, but the monotonic formation primary failed

The frozen first-flight primary showed a positive programme-level experience slope:

- B_obs = **+0.16733**;
- null mean = **-0.06936**;
- calibrated excess = **+0.23669**;
- one-sided permutation P = **0.0102**.

However, only **8/14 juveniles (57.1%)** had positive individual slopes, below the frozen requirement of **10/14 (70%)**.

Therefore the primary verdict was:

**FAIL_PRIMARY_FORMATION_RULE**

The data do not support one common gradual increase in personal-history advantage across juveniles.

The predeclared late-history secondary was strongly positive:

- L_obs = **+112.5554**;
- null mean = **-0.1814**;
- one-sided permutation P = **0.0001**;
- **12/14 juveniles** had positive late-history advantage.

Thus, by later early ontogeny, a juvenile's own recent movement history was substantially more informative about its next spatial use than experience-matched conspecific histories.

The post-primary early-seed versus recent-history diagnostic further showed:

- earliest two valid days: E = **+15.19**, P = **0.1655**, 8/14 positive — unsupported;
- recent two versus earliest two: Q = **+144.079**, P = **0.0001**, 10/14 positive.

This diagnostic suggests identity-specific updating beyond a weak early seed, but it cannot rescue the failed monotonic formation primary.

A separate randomized early-environment history-carrier test using nightly outdoor strategy also failed to detect a treatment effect:

- enriched mean H = **1.1476**;
- impoverished mean H = **0.4395**;
- T = **+0.7081**;
- randomized two-sided P = **0.3244**.

Thus broad enriched versus impoverished early experience did not detectably alter the later strength of personal-history dependence in that endpoint (Fig. 2A).

## Randomized enrichment did not confirm increased total individualization

The Season-2 enrichment primary included all 29 complete bats:
- enriched = 14;
- impoverished = 15.

Residual multivariate change-vector dispersion was:
- (V_{enriched}=2.656639);
- (V_{impoverished}=1.921940).

The observed contrast was:

[
D=+0.734699.
]

Although the direction was enriched > impoverished, the origin-stratified randomization test was unsupported:
- 199,999 randomizations;
- (P=0.167785).

Thus the frozen primary did not establish that environmental enrichment increased the total amount of individual differentiation beyond the shared treatment-group shift.

The descriptive three-trait decomposition was directionally coherent:
- Boldness: +0.465792;
- Exploration: +0.250837;
- Activity: +0.018070.

All three traits pointed enriched > impoverished, and the cancellation ratio was zero. This shows that the unsupported multivariate result was not generated by opposing trait directions.

The descriptive state-rewriting analysis gave mean squared errors:
- baseline only: 3.137006;
- group state only: 4.189011;
- baseline + shared shift: 2.628609.

Thus the best simple overall description was retention of personal baseline plus a common treatment-associated shift.

## Developmental auditory feedback changed phenotype without changing total adult vocal individualization

The adult whole-repertoire vocal analysis included all 10 randomized bats.

Residual adult vocal individualization was:
- (V_{hearing}=15.766760);
- (V_{deaf}=17.192257).

The signed contrast was:

[
D=-1.425497.
]

Across all 120 exact sex-conditioned assignments:
- 86 were at least as extreme in absolute value;
- exact two-sided (P=0.716667).

Thus the frozen primary found no difference in the total amount of adult whole-repertoire vocal individualization.

The descriptive feature decomposition showed strong opposing contributions:
- positive contribution sum = +3.746740;
- negative contribution sum = −5.172237;
- positive / negative feature counts = 15 / 13;
- cancellation ratio = 0.840173.

The null total therefore did not imply uniform invariance across acoustic dimensions (Fig. 2B).

## Individual correspondence survived external sensory masking

In the *Pipistrellus kuhlii* masker experiment:

Baseline → masker:
- (K=+4.941^circ);
- 5/6 individuals positive;
- exact (P=0.04028).

Foam no-masker → foam+masker:
- (K=+6.779^circ);
- 5/5 positive;
- exact (P=0.025).

Thus individual movement bias remained detectable while current sensory conditions were experimentally altered.

## Individual flight-performance organization persisted across a graded masking gradient

In the *Myotis daubentonii* experiment, three bats met the complete frozen support rule across five noise levels.

The programme identity advantage was:
- (A=+0.377542).

The exact cross-condition identity null contained 1,296 assignments. The true biological mapping was uniquely most extreme:
- exact (P=1/1296=0.00077160).

All three bats had positive individual mean advantages, and all five noise contexts had positive condition-level mean advantages.

This is strong within-experiment identity correspondence, but biological n=3 limits population-level generality.

## Individual vocal organization survived reversible central auditory perturbation

The four *Eptesicus fuscus* DREADD bats all retained positive identity advantage across saline and ligand conditions:
- jane: +0.826821;
- bea: +1.411613;
- jason: +0.119224;
- stella: +1.660151.

The programme statistic was:
- (K=+1.004452).

The true same-bat saline-to-ligand mapping ranked first among all 24 identity assignments:
- exact (P=1/24=0.041667).

Thus reversible central auditory perturbation altered common vocal expression without erasing all individual-specific multivariate organization.

## Navigation turning organization persisted across experimentally altered conditions

In Aharon Figure 1, all four bats and all three navigation conditions contributed positive mean identity advantage.

Bat-level mean advantages:
- 500: +1.931476;
- 503: +6.438521;
- 505: +3.265457;
- 510: +3.145604.

Condition-level means:
- con: +2.752794;
- 75: +4.109808;
- 300: +4.223191.

Programme:
- (K=+3.695264).

Among 576 exact cross-condition identity assignments:
- true biological mapping rank = 2;
- exact (P=0.00347222).

Thus bilateral turning-location organization remained individually identifiable across altered navigation conditions after population-level condition shifts were removed. Together with the three independent sensory-manipulation datasets, this yields repeated support for same-individual correspondence under acute perturbation (Fig. 3).

## Coarse movement organization transferred more broadly than detailed geometry

In *Rhinolophus nippon*, the transparent I/M representation retained strong individual identity across obstacle contexts:
- (K=+0.55428);
- 5/5 positive;
- (P=0.0001).

When the fixed Rhino I/M representation was transferred to *Carollia perspicillata*:
- (K=+0.34758);
- (P=0.0007).

By contrast, fixed detailed scale-free Rhino trajectory geometry did not transfer:
- (K=-0.0350);
- (P=0.2144).

Thus coarse individual organization generalized where detailed realized trajectory geometry did not.

## The laboratory-to-wild carrier bridge failed its frozen gate

The frozen wild FlightIntensity carrier gate required support in at least three of four panels.

Observed:
- PASS;
- PASS;
- FAIL;
- structural STOP.

Overall:
- 2/4;
- FAIL.

Therefore the laboratory-style carrier-to-wild-vertical-individuality bridge remains unconfirmed.

Post-outcome H/V component analyses are exploratory only (Fig. 4).

---

# Discussion

## Individual organization is more persistent than its expressed form

Across the controlled acute perturbation experiments, current context changed while information identifying individuals remained detectable.

The perturbations were not equivalent:
- external sensory masking;
- graded acoustic masking;
- reversible central auditory manipulation;
- altered navigation conditions.

The behavioral endpoints were also different:
- approach/movement bias;
- flight time;
- vocal organization;
- turning-location organization.

We therefore do not infer one universal latent bat personality axis.

What is shared is the inferential pattern: after removing population-level condition shifts, the same biological individual remained more similar to its own history than to other individuals' histories.

This is stronger than ordinary repeatability because the current environment was experimentally manipulated.

At the same time, the result should not be interpreted as population-wide invariance. Several systems contain only three to five biological individuals. Exact permutation p-values quantify how extreme the true identity mapping is within the frozen experiment; they do not provide precise prevalence estimates for a species.

## Development and maintenance show different empirical signatures

The developmental results differ sharply from the acute perturbation results.

The juvenile-history results are more constrained. Late personal history is strongly predictive of later spatial use, but the frozen primary does not support one common monotonic increase in that advantage across juveniles. A post-primary diagnostic suggests recent history contains more identity information than the earliest two valid days, but this cannot be promoted into primary formation support.

But the two randomized developmental manipulations do not support a simple scalar rule for the amount of individuality.

Environmental enrichment produced a positive, directionally coherent tendency toward greater multivariate dispersion, but the randomization test was not significant.

Developmental auditory feedback strongly affects learned vocal phenotype in the source study, yet the frozen whole-repertoire analysis found no treatment effect on total adult vocal individualization.

Together, these results argue against the simple expectation:

`more / richer / more informative developmental experience → more individuality`.

They also argue against the opposite expectation that developmental disruption should simply erase individuality.

A more plausible view is that development can change:
- mean behavioral state;
- the dimensions on which individuals differ;
- the historical path by which individual organization becomes refined;

without predictably changing one scalar quantity called "amount of individuality."

This interpretation is consistent with recent work beyond bats. Context-dependent individuality has been demonstrated directly in *Drosophila*, while developmental ecological stress in clonal fish can alter mean behavior without changing individuality magnitude. The contribution here is therefore not the discovery of those general principles, but their placement alongside controlled bat perturbation and portability evidence within one causal hierarchy.

## Individuality may be better understood as allocation across dimensions than scalar variance

The descriptive developmental decompositions point in two different directions.

In the enrichment experiment, all three frozen laboratory personality dimensions contributed toward greater enriched-group dispersion. The tendency was expansion-like but statistically unresolved.

In the auditory-feedback experiment, large positive and negative acoustic-dimension contributions nearly cancelled. That pattern was reallocation-like.

Neither descriptive decomposition is confirmatory at the feature level.

But together they highlight a more specific formation question:

> what determines where individual-specific information is allocated across behavioral dimensions?

This question is distinct from asking whether the total amount of among-individual variation increases or decreases.

It also aligns with the juvenile-history boundary: personal history can carry strong individual information later, yet its ontogenetic build-up is heterogeneous and is not simply strengthened by broad enriched versus impoverished developmental treatment.

## Coarse personal organization is more portable than detailed realization

The Rhino-to-Carollia contrast provides another layer of the same architecture.

A low-dimensional movement representation transferred across contexts and into an independent system, whereas detailed trajectory geometry did not.

This suggests that the persistent object should not be equated with one literal route or one exact geometric realization.

Instead, the data are more consistent with context-specific realization of a coarser personal organization.

This distinction also helps reconcile robust identity mapping with behavioral plasticity. A bat can change its trajectory substantially while preserving enough relative organization for individual identity to remain predictive.

## Persistent laboratory individuality does not automatically imply wild niche differentiation

The failed wild carrier gate is central to the paper's claim boundary.

If persistent personal organization automatically generated stable ecological partition, then a laboratory-style carrier should map cleanly to wild vertical individuality.

It did not.

The frozen field gate failed at 2/4 panels, and later H/V decomposition was explicitly post-outcome.

Thus laboratory individuality, behavioral expression, and wild spatial niche are not interchangeable empirical objects.

This boundary strengthens the layered interpretation.

Individual organization may:
- persist;
- be expressed differently across contexts;
- sometimes influence ecology;

without necessarily producing continuous exclusive spatial partition.

## A layered model of behavioral individuality

The public bat evidence supports a simple empirical hierarchy:

`predisposition + identity-specific history → persistent personal organization → context-specific expression`

with ecological consequence as a separate downstream layer.

This hierarchy is not a claim about one shared neural state across species.

It is a statement about separable inferential levels.

Formation concerns how between-individual organization emerges and is allocated.

Maintenance concerns whether identity-bearing structure survives perturbation.

Expression concerns how the current environment maps organization into behavior.

Ecological consequence concerns whether those expressed differences create measurable spatial or resource partition.

Treating all four as one quantity obscures why a large environmental effect can coexist with stable individual correspondence, why developmental treatment can change phenotype without changing total individualization, and why laboratory organization need not map directly onto wild niche structure.

## Limitations

The most important limitation is biological sample size in several controlled sources.

Myotis contains three complete bats, Eptesicus four, Aharon four, and the adult Rhino mechanism programme five.

Their exact tests are valid for the frozen assignment problems but do not substitute for broader biological replication.

Second, species and endpoints differ among datasets. We therefore deliberately avoid a pooled quantitative meta-analysis.

The cross-system conclusion concerns the pattern of identity correspondence, not a shared effect-size scale.

Third, the public-source programme was iterative. Source-level endpoints and nulls were frozen before numerical opening, but the dataset search and final synthesis developed as evidence accumulated.

The work should therefore be described as provenance-controlled comparative reanalysis, not as a preregistered multi-study experiment.

Fourth, the developmental null results should not be interpreted as proof that development is irrelevant to individuality. The source experiments clearly alter phenotype, and the descriptive decompositions suggest changes in the structure or allocation of individual differences.

Finally, the wild ecological bridge remains unresolved. The laboratory results do not justify assuming that persistent personal organization automatically creates ecological niche partition.

## Conclusions

Across independent public bat experiments, individual-specific organization repeatedly remains detectable after acute sensory or navigational perturbation.

Developmental manipulations tell a different story: they can alter behavioral phenotype without a simple corresponding change in the total amount of individual differentiation.

Cross-task analyses further show that coarse personal organization can transfer more broadly than detailed realized geometry, while the direct laboratory-to-wild niche bridge remains unconfirmed.

Together, these results support a layered empirical view of behavioral individuality.

The strongest remaining question is no longer whether environment matters or whether late personal history can be informative.

It is:

> **what determines which behavioral dimensions and historical trajectories become individualized for particular animals?**

---

# Data and code availability

All analyses use previously published public datasets.

Key public sources include:

- Harten et al. first-flight data: Mendeley Data `10.17632/n9d8gbz3xr.1`;
- Rachum et al. developmental-enrichment data: Mendeley Data `10.17632/wh7c636y3t.1`;
- Elie et al. auditory-feedback data: Mendeley Data `10.17632/h5ff9vv5pc.1`;
- Diebold et al. auditory-midbrain data: Zenodo `10.5281/zenodo.13857870`;
- Aharon et al. navigation data: Mendeley Data `10.17632/f6mvhj5gj9.3`;
- Foskolos et al. graded-masking data: Zenodo `10.5281/zenodo.4946256` and Dryad `10.5061/dryad.ngf1vhhv3`;
- Eveland et al. corridor data and code: public repository `00keveland/Tunnel_2026`, pinned for the external validation at commit `59928a71887d521fec143080b0b187736c046a0e`.

Source-level analysis contracts, structural audit records, executable scripts, exact/randomization logic, result receipts, synthesis files and figure-generation code are version controlled in `zuizui0223/batter`.

The authoritative manuscript-level numeric ledger is:

`prospective/public_causal_synthesis/MASTER_RESULTS_TABLE_V1.md`.

The authoritative evidence-tier map is:

`prospective/public_causal_synthesis/EVIDENCE_MATRIX_V1.md`.

Manuscript-facing figures are generated from frozen summary values by:

`prospective/public_causal_synthesis/plot_synthesis_figures_v1.py`.

Generated SVG files are stored under:

`figures/public_causal/`.

## Analysis provenance

This study is a comparative secondary reanalysis of public data.

For each source-level analysis, the endpoint, biological support rule, aggregation hierarchy and null/randomization procedure were fixed before the corresponding numerical outcome was opened in this programme. Structural and schema audits were used to determine whether a frozen analysis was executable without inspecting biological effect values.

The cross-study synthesis itself was iterative. Public sources were discovered and audited sequentially, and the programme-level biological framing developed as positive and negative source results accumulated. The work is therefore best described as **provenance-controlled comparative reanalysis**, not as a prospectively preregistered multi-study meta-analysis.

Post-primary analyses are labelled explicitly as:
- predeclared secondary;
- post-primary diagnostic;
- or descriptive/exploratory.

Such analyses are not allowed to rescue a failed frozen primary.

## Ethics

No new animals were captured, handled or experimentally manipulated for this study. All analyses use public data from previously published studies. Ethical approvals and animal-care procedures for the original experiments are reported in the respective source publications.

## Figure files

- Fig. 1: `figures/public_causal/FIGURE_1_CAUSAL_LAYERS_V1.svg`
- Fig. 2A: `figures/public_causal/FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg`
- Fig. 2B: `figures/public_causal/FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg`
- Fig. 3: `figures/public_causal/FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg`
- Fig. 4: `figures/public_causal/FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg`

Full legends are in `prospective/public_causal_synthesis/FIGURE_CAPTIONS_V1.md`.

---

# References — working list

- Aharon G, Sadot M, Yovel Y. 2017. Bats use path integration rather than acoustic flow to assess flight distance along flyways. *Current Biology* 27:3650–3657.e3. DOI: 10.1016/j.cub.2017.10.012.
- de Bivort BL. 2025. The developmental origins of behavioral individuality. *Annual Review of Cell and Developmental Biology* 41:331–352. DOI: 10.1146/annurev-cellbio-101323-025423.
- Diebold CA, Lawlor J, Allen K, Capshaw G, Humphrey MG, Cintron-De Leon D, Kuchibhotla KV, Moss CF. 2024. Rapid sensorimotor adaptation to auditory midbrain silencing in free-flying bats. *Current Biology* 34:5507–5517.e3. DOI: 10.1016/j.cub.2024.10.045.
- Elie JE, Muroy SE, Genzel D, Na T, Beyer LA, Swiderski DL, Raphael Y, Yartsev MM. 2024. Role of auditory feedback for vocal production learning in the Egyptian fruit bat. *Current Biology* 34:4062–4070.e7. DOI: 10.1016/j.cub.2024.07.053.
- Eveland KE, Finger NM, Jaroszewski JM, Bucio L, Moss CF. 2026. Looking ahead: echolocation and flight behaviors of two fruit bat species navigating a corridor. *Journal of Comparative Physiology A*. DOI: 10.1007/s00359-026-01818-0.
- Foskolos I, Bjerre Pedersen M, Beedholm K, Uebel AS, Macaulay J, Stidsholt L, Brinkløv S, Madsen PT. 2022. Echolocating Daubenton's bats are resilient to broadband, ultrasonic masking noise during active target approaches. *Journal of Experimental Biology* 225:jeb242957. DOI: 10.1242/jeb.242957.
- Gallagher JH, Perkes AD, Chang C-C, Chirila ES, Kacevas K, Laskowski KL. 2026. Born This Way: Individuality Is Seeded Before Birth and Robust to Ecological Stress. *Ecology Letters* 29:e70454. DOI: 10.1111/ele.70454.
- Harten L, Katz A, Goldshtein A, Handel M, Yovel Y. 2020. The ontogeny of a mammalian cognitive map in the real world. *Science* 369:194–197. DOI: 10.1126/science.aay3354.
- Houslay TM, Vierbuchen M, Grimmer AJ, Young AJ, Wilson AJ. 2018. Testing the stability of behavioural coping style across stress contexts in the Trinidadian guppy. *Functional Ecology* 32:424–438. DOI: 10.1111/1365-2435.12981.
- Mathejczyk TF, Knief C, Haidar MA, Freitag F, McClary T, Wernet MF, Linneweber GA. 2026. Individuality across environmental context in *Drosophila melanogaster*. *eLife* 13:RP98171. DOI: 10.7554/eLife.98171.
- Mitchell DJ, Houslay TM. 2021. Context-dependent trait covariances: how plasticity shapes behavioral syndromes. *Behavioral Ecology* 32:25–29. DOI: 10.1093/beheco/araa115.
- Rachum A, Harten LM, Assa R, Goldshtein A, Chen X, Gonceer N, Yovel Y. 2025. Early experience affects foraging behavior of wild fruit bats more than their original behavioral predispositions. *eLife* 14:RP103220. DOI: 10.7554/eLife.103220.
- Taub M, Yovel Y. 2020. Segregating signal from noise through movement in echolocating bats. *Scientific Reports* 10:382. DOI: 10.1038/s41598-019-57346-2.
- Teshima Y, Genda S, Aoki Y, Fujisawa M, Hiryu S, Fujii K. 2026. Evidence for latent regularities in echolocation-guided flight behaviour of bats. *Proceedings of the Royal Society B* 293:20261463. DOI: 10.1098/rspb.2026.1463.
- White SJ, Pascall DJ, Wilson AJ. 2020. Towards a comparative approach to the structure of animal personality variation. *Behavioral Ecology* 31:340–351. DOI: 10.1093/beheco/arz198.

## Disclosure note — draft

Generative AI assisted with code review, repository organization, literature triage, and manuscript drafting from author-controlled analyses. Scientific decisions, source selection, analysis contracts, interpretation, and final responsibility remain with the human author(s). This wording must be reconciled with journal policy before submission.
