# H1 prospective programme — ecological controls on social information use in bats

Status: PROSPECTIVE PROTOCOL / EVIDENCE-ELIGIBILITY GATE. Created 2026-11-19. No fitted model, effect estimate, extracted systematic case table, or claim of preregistration with an independent registry. This is a new methodological programme; the frozen batter JAE manuscript, its data, and its inference remain unchanged.

## Scientific question

When do bats gain useful knowledge by revisiting personally familiar resources, discovering food opportunistically from conspecific cues, or coordinating with others? Do changes in resource persistence, patch search difficulty, and shareability alter the *mode and timing* of information use across species and populations?

The candidate evolutionary contrast is not a forced tradeoff between individuality and sociality. Individual movement identity, individual information use, stable social bonds, simultaneous group movements, and causal information transfer are distinct estimands. They may co-occur.

### Prospective predictions, not supported outcomes

- H1a (comparative): Among *independently documented* social-information-use cases, resource persistence measured relative to an animal's typical foraging bout predicts *near-patch* information use versus *away-from-patch* following/recruitment, after study methods, phylogeny, and repeated studies of a taxon are accounted for.
- H1b (population/seasonal): Within a species, variation in food-patch predictability and shareability predicts switching in the frequency or form of social information use. Document only when matched populations or seasonal replications are supported.
- H1c (novel, potentially testable): Within the same persistence class, sensory detectability, spatial predictability and competition/patch divisibility modify the *realized* use of social information. Test this only if covariates have direct measurement independent of the social response.
- H2/H3 bridge: Frozen batter confirms repeatable individual-centered vertical use in comparative bat panels and a boundary Tadarida panel. It does NOT independently establish personal memory or resource prediction, so it cannot be treated as a behavioral personal-information response. There are only four bat taxa in the current panels, not 10–20 independently eligible species. No species-level negative social-vs-individual correlation is currently established.

## Prior-art firewall

- Safi & Kerth (2007), DOI:10.1086/520116, linked resource ecology/flight morphology to *male social roosting* in temperate bats, not direct causal exchange of foraging information.
- Kohles, O'Mara & Dechmann (2022), DOI:10.1111/brv.12881, explicitly formulated the resource-persistence/social-information-strategy framework. Their review covered 52 cases in 34 species; 35 ephemeral/shareable cases and 20 strategy-resolved cases. Merely finding these links again is NOT novel.
- Dechmann et al. (2010), DOI:10.1371/journal.pone.0009012, showed above-chance coordinated foraging in Molossus molossus. This is observational coordination, not necessarily proof of the proximate cue used.
- Krivoruchko et al. (2024), DOI:10.1073/pnas.2321724121, had already documented a nonmonotone conspecific-acoustic-density/capture-success relationship. Do not claim the hump-shaped curve as a new discovery.
- Phyllostomus hastatus has reported recruiting foraging groups in one ecological setting and more individual foraging in other populations; ecological context must not be collapsed to a fixed species-level absence/presence.
- Reciprocity (e.g., repeated blood meal sharing in vampire bats) is a separate outcome with its own relationship histories, opportunities and fitness claims. Do not place it at the high end of a single unvalidated social-foraging scale.

## Data provenance and assembly

Primary observational unit: source publication × independent species-population × site × season-year × empirical social foraging situation; retain record-level study_id, individual case_id, source DOI, and quoted evidence location (under fair use). Never count recordings, feeding buzzes, conspecific contacts, or repeated case studies as independent species.

Candidate predictor sources:
- EltonTraits 1.0 mammal diet / foraging guild: DOI:10.1890/13-1917.1; diet is only a coarse proxy for resource predictability, not a substitute for measured patch persistence.
- Conenna et al. (2021) global bat flight and echolocation trait compilation, Dryad DOI:10.5061/dryad.tmpg4f4xm. Check original trait coverage, species synonyms and literature-derived missingness before use.
- Upham et al. (2019) mammal phylogenetic posterior/credible trees: integrate tip names, multiple tree uncertainty and taxonomy updates. Do not equate a 103-taxon phylogenomic backbone with species-level complete sampling.
- Kohles 2022 Table 2 and Table S1 are a *prior-art seed and source-discovery index*, not an independent holdout validation and not a list of absent species.
- Independent 2023–2026 literature should be searched systematically with a frozen query and reproducible screening ledger, rather than selecting favorable published cases.

## Blinded coding and audit

1. Independently compile all eligible bat taxa and publication records from the systematic search. Record full-text accessible / inaccessible / screened-out statuses; keep all exclusion reasons.
2. Predictor coders classify resources and ecological setting from natural-history evidence WITHOUT looking at observed social-foraging outcome classifications. Outcome coders separately code behavior and cue evidence; ideally two coders in each task.
3. Freeze the coding rubric, taxonomic crosswalk, conflicts and arbitration protocol before running comparative association tests. Publish disagreements and unresolved NAs instead of filling them by guild assumptions.
4. Construct species/population/study sampling effort indicators and exact denominators. Distinguish unstudied (NA), genuine adequately tested non-detection, co-presence, demonstrated social information use, and confirmed strategy.
5. Run source overlap and repeated-use checks; a synthesis paper and its underlying primary experiments count once as evidence, not twice.

## Data sufficiency and stop gates

No automatic 'hundreds of species' primary response. First calculate:
- number of independent taxa with directly coded *foraging* social-information response;
- number of distinct families/geographic regions with comparable source and outcome methods;
- number of tested negative cases under explicit observation effort;
- measured versus inferred resource-persistence contrasts;
- number of independent groups for a genuine blocked external prediction.

If there are fewer than 30 independent species with classifiable response and predictors, do NOT market the analysis as a global phylogenetic response model; report feasibility/structured evidence only. If only positive reports exist with no valid sampled zeros, do NOT fit a species-level probability-of-use model. If following and recruitment remain single-case categories, report them descriptively rather than fitting unstable four-class multinomial effects.

A post-2022 external species/population test is a priority ONLY if independent holdout study groups are available. Hold out whole study + species + region where possible, not individual records from the same study.

## Primary modeling targets (only after admissibility)

- Among independently confirmed social information-use observations, estimate P(information used away from patch | persistence relative to bout, spatial predictability, source-design covariates) with study and species/clade random effects. This is a *conditional strategy* model and must not be interpreted as P(social foraging).
- For a sampled set with explicit tested negatives, fit a hierarchical detection-and-occurrence model (positive behavior vs sufficiently tested absence), with effort and methods included. This model can estimate association with evidence-supported social-information occurrence.
- Account for taxon phylogeny with phylogenetic mixed models across a posterior tree sample; a PGLS treating all cases as species-independent is invalid.
- Compare models using leave-one-study/taxon or region-out prediction, predictive log score and calibration, reporting group-level uncertainty and failure cases. Do not use same studies for theory building and independent out-of-sample evidence.
- Treat ecology as correlational; a phylogenetic path diagram cannot itself identify a causal direction.

## Interpretation boundary

The achievable first product is a transparent, negative-aware comparative evidence matrix and a predeclared test of context and strategy. H1 positive estimates, generalization, causal social exchange, and links to individual vertical memory remain OPEN until independent original observations pass the above gates.

Sources: https://doi.org/10.1111/brv.12881 ; https://doi.org/10.1086/520116 ; https://doi.org/10.1371/journal.pone.0009012 ; https://doi.org/10.1073/pnas.2321724121 ; https://doi.org/10.1890/13-1917.1 ; https://doi.org/10.5061/dryad.tmpg4f4xm
