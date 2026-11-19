# H1: signed responses, estimand compatibility and regression-to-the-mean audit

Date: 2026-11-19. Status: published-result reconstruction and **known-truth mathematical negative control**, NOT a novel ecological effect. This report is prospective relative to the frozen JAE batter manuscript and does not revise old observed vertical niche claims.

## 1. The two strongest openly inspectable quantitative originals

**Lewanzik et al. (2019), J Anim Ecol; DOI 10.1111/1365-2656.12989; Dryad 10.5061/dryad.gp65g2t.**
12 lakes; six emitter bat species x four receiver taxon/species groups (24 combinations, NOT 24 independent bat species). Analysis used 250 *Myotis daubentonii*, 94 pooled NEV (Nyctalus/Eptesicus/Vespertilio), 110 *Pipistrellus nathusii*, and 180 *P. pipistrellus* eligible playback blocks, across the same experimental study. The published Table 1 models report four negative coefficients for baseline conspecific activity on change in bat-seconds/min, with 95% credible intervals entirely below zero (see source CSV). Coefficients were estimated with species-specific standardized baseline predictors: numerical differences are NOT raw common-scale interspecific effect sizes and not four independent experiments.

**Knörnschild & Russo (2026), Ann NY Acad Sci; DOI 10.1111/nyas.70427.**
One study, 16 biological *Glossophaga mutica handleyi* bats: 8 males, 8 females, reused across two playback experiments. Published negative-binomial GLMM playback/silent-flower visit ratios:
- Alert calls: male 0.17 (z=-6.43), female 6.57 (z=6.05).
- Benign calls: male 0.73 (z=-1.72), female 2.58 (z=4.48).
- White noise paired with alert design: male 0.60 (z=-1.75), female 1.12 (z=0.75).
- White noise paired with benign design: male 1.16 (z=0.82), female 0.94 (z=-0.22).

Reconstructed *descriptive* female/male ratio-of-rate-ratios: **38.6471 alert**, **3.53425 benign**, **1.86667 noise-alert**, **0.81034 noise-benign**. These are ALREADY the authors' reported directional response, expressed on a common multiplicative contrast. They are not independent field experiments, and they do not causally identify the cognitive interpretation of a cue. Summary-based approximate Wald ranges are in the JSON only under the strong assumption that male and female separately fitted log-contrast estimates are independent; repeated trials, shared sources, rounding and unknown full covariance make formal cross-signal interaction tests from these summaries inappropriate. The paper reports Table S1 and Data S2 as supplementary material; raw individual behavior was NOT ingested/re-fitted in this audit.

## 2. A decisive estimator warning in the 2019 comparison

The source's primary response is
```
D = Y_during_playback - Y_pre_playback
X = Y_pre_playback
D ~ X + cue_buzz_rate + cue_species + site + other predictors
```
Using X in both the response and predictor creates **mathematical coupling**. The simple-regression population coefficient under ANY process is:

```
Cov(X,D)/Var(X) = Cov(Y_pre,Y_during)/Var(Y_pre) - 1
                = rho * SD(Y_during)/SD(Y_pre) - 1.
```

If the two measurements have the same stationary marginal variance, **b = rho - 1**. If rho < 1, the baseline coefficient is negative even when there is *no biological effect of social competition and no actual playback response*.

Under true no-effect simulations with 12 independent sites, 30 paired observations per site, Gaussian within-site activity noise, and within-site correlations rho=0/0.5/0.9, the exact expected slopes are respectively -1/-0.5/-0.1. The deterministic code implements 128 simulations for each rho and verifies this; see JSON artifact in isolated CI.

**Interpretive consequence:** The 2019 observation that all four baseline-density coefficients are negative is REAL as published, but their sign alone cannot establish that crowding biologically reduces the payoff of social information. This is NOT a claim that the published observations are false, that all the estimates are artifacts, or that buzz-rate and playback-species contrasts are invalid. The source has additional cue-specific predictions and experiments. Without source-specific pre/during autocorrelation, baseline SD, and a properly constructed randomized silent-control contrast, the size of the mechanical component cannot be removed from these 4 reported coefficients.

This is a methodological counterexample/identification boundary, not an empirical refutation or a new bat-effect discovery.

## 3. Valid prospectively testable estimand

Define pre-period resource/control state C, randomized playback treatment T, and observed during-period activity Y, using genuinely randomized *silent and cue* conditions, a stable site, effort and time protocol:

```
H1*: E[Y | T=cue, C=c, x] - E[Y | T=silent, C=c, x]
```

This is a cue effect at baseline c, rather than a regression of `Y-X` on `X`. Its dependence on c is a treatment × pre-density interaction. Randomization/control construction and bat detection must support causal interpretation. If only zero-buzz SEARCH-call versus feeding-buzz treatments exist, the identified contrast is food-rate information **conditional on conspecific acoustic presence**, not cue-versus-silence.

The related existing 2019 study did not explicitly include baseline-conspecific-density × playback-cue interaction in the displayed Table 1 model; therefore the reported negative baseline main effect alone is not a test of this new contrast. If data are usable, the first independent empirical task is a checked blocked reanalysis of original stimuli/baselines, with whole-site holdout for transfer and no data-dependent cue threshold selection.

## 4. Do not combine outcomes with different biological units

| Source | Outcome | Direct respondent unit | Trial/study independence | Can pool log effect as is? |
|---|---|---|---|---|
| Lewanzik 2019 | delta bat-seconds per min | detected receiver species/species-group at lake; no stable bat IDs | one 12-lake study | NO: additive Gaussian change, source self-baseline coupling |
| Knörnschild & Russo 2026 | playback/silent flower visit rate ratio | 16 tagged captive bats across repeated trials | one study, sex and call reuses animals | NO: multiplicative GLMM ratio |
| Wilson et al. 2026 | activity during/after playback | acoustically detected species at creek | one study, 4 taxa | NO: comparable only with original event denominators, controls, baseline count and effect intervals |
| Lourie et al. 2024 | proportion visiting familiar unfruiting trees after socially borne odor | 56 naive tagged bats exposed by roost/date; 10 visitors | one experiment with shared group exposure | NO: time-dependent visiting probability, not acoustic approach |
| Fujioka et al. 2026 | buzz-identified prey attack attempt rate under pond co-use | visits/times, stable animal ID unverified | one study | NO: encounter costs, NOT response to randomized social cue |

A multi-species sign test is not yet possible: even the two sources with numeric coefficients do not share measurement scale or matched treatment/control. A qualitative evidence synthesis is possible, but must include published falsifiers, unresolved response signs and search effort.

## 5. Link to individual 3D strategy without overreach

Existing batter result: repeatability in individual-centered vertical-use probability shapes under its frozen controls. This is NOT measured private information, cognitive memory, social cue detection, payoff or actual prey capture. Separately, Schabacker et al. (2025), DOI 10.1098/rspb.2024.2217, demonstrated repeatable personality-associated social-call production in 60 wild male *Glossophaga soricina handleyi* bats. The 2026 receiver study labels *Glossophaga mutica handleyi*, a different taxonomic usage and different biological individuals. Without verified cross-taxonomic ID mapping, no co-measured identity × cue-response dataset exists. Do not promote 'sender personality' as direct individual memory-use or the cross-study taxonomy as repeated independent support in a meta-analysis.

**Source URLs:**
- https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/1365-2656.12989
- https://datadryad.org/dataset/doi:10.5061/dryad.gp65g2t
- https://onlinelibrary.wiley.com/doi/10.1111/nyas.70427
- https://www.sciencedirect.com/science/article/pii/S0003347225003331
- https://doi.org/10.1098/rspb.2024.2217

## 6. Decision

Structural source negative control should be mandatory **before** any cross-species ecology interpretation of a baseline-density coefficient. The published 4/4 negative density effects and 2026 sex-specific signal effects may motivate a hypothesis, but neither is novel evidence from this project and neither justifies a species-wide causal information law.

**STOP (present):** any pooled numerical social-info response coefficient, H3 negative tradeoff, causal density effect from 2019 published baseline coefficient, or universal social-foraging rule.

**Next genuine observed-data step:** obtain/source-verify original 2019 Dryad workbook, separate the acoustic treatment indicator from baseline activity, construct valid matched control contrasts and whole-site holdout. If only published aggregates remain accessible, stop at this falsification/identifiability report.
