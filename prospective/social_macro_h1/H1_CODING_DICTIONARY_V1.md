# H1 evidence coding dictionary v1

Status: Protocol only. NO completed independent double-coding or harmonized dataset yet. Primary table grain: one source-specific ecological/behavioral *case*, usually study × taxon × independently defined population × site × season/context. Secondary table will aggregate by species ONLY with multiple populations retained and uncertainty propagated.

## Required identifiers and observation safeguards

| Column | Type / allowed states | Operational rule |
|---|---|---|
| case_id | unique text | Stable provenance identifier; never use one ID across distinct populations |
| study_id | DOI or repository reference | Primary source, not a review citation used as replacement |
| study_year | integer or NA | Publication year; not collection year |
| species_verbatim | text | Name as author wrote it |
| species_accepted | taxonomic canonical or NA | Synonym crosswalk with authority and confidence |
| population_id | text or NA | Distinct breeding/social community when validated |
| site_region | text or NA | Exact or coarse location from source; do not infer coordinates |
| season_or_year | text or NA | Observation window; study can contribute repeated contexts |
| source_kind | field_tracking / playback / experimental_manipulation / observation / review_only / other | Review-only cases cannot be counted as independent empirical replicates |
| source_access | full_text / abstract_only / metadata_only / not_accessible | May not classify precise foraging behavior from a title alone |
| independence_cluster | text | Group tied to same tagged bats/dataset/publication group to avoid pseudo-replication |

## Ecological predictors (code independently of behavioral outcome)

| Column | Type / allowed states | Operational rule |
|---|---|---|
| resource_taxon | insects_flying / insects_nonflying / fruit / nectar_pollen / fish_aquatic / vertebrate / blood / mixed / NA | Main consumed item in study, not global species default |
| patch_persistence_bout | shorter / longer / spans_boundary / NA | Patch remains profitable for < or > one typical foraging bout; preserve actual quantitative interval when known |
| patch_persistence_duration_h | nonnegative numeric / NA | Source-measured productive patch life, not inferred from body size/diet |
| bout_duration_h | positive numeric / NA | Source-measured typical individual foraging bout; note if linked to the same population |
| patch_spatial_predictability | low / intermediate / high / NA | Repeatable location *between bouts*, independent of material permanence |
| patch_detection_difficulty | low / intermediate / high / NA | Experimental/measured findability; do not automatically infer from diet |
| resource_shareability | verified_shareable / verified_nonshareable / uncertain | Divisible food relative to simultaneously searching bats; independent patch-capacity evidence preferred |
| patch_temporal_variability | low / high / NA | New food availability at same site vs truly persistent use |
| resource_predictor_quality | measured / independently_cited / guild_proxy / unknown | Guild-only values NOT promoted to direct patch measurements |
| diet_eltontraits | structured trait / NA | Source-specific coarse covariate; never used to manufacture patch duration |
| wing_aspect_ratio | measured numeric / NA | Normalize units/sex and identify imputed values |
| wing_loading | numeric with units / NA | Include measurement-source and sex-specific uncertainty |
| bat_body_mass_g | numeric / NA | Source-specific log covariate |
| phylogeny_tip | text / NA | Canonical tip in a documented set of posterior phylogenies |

## Behavioral response and evidence categories (never collapse without a registered rule)

| Column | Type / allowed states | Operational rule |
|---|---|---|
| colony_presence | observed / tested_absent / unknown | Roost aggregation alone is NOT social foraging |
| synchronized_forage | above_null / observed_uncontrolled / tested_not_above_null / unknown | Same-place or synchronous movements, with null and effort noted |
| cue_transfer | experimentally_demonstrated / behaviorally_supported / suggestive / unknown | Specific cue: echolocation, contact call, visual, smell or followed departure; synchrony does not establish causal information flow |
| use_location | near_patch / away_from_patch / both / unknown | Location where a social cue informs movement relative to feeding patch |
| coordination | coordinated / opportunistic / unknown | Preplanned/paired departure or ongoing group movement vs exploiting encountered cues |
| strategy | local_enhancement / group_facilitation / following / recruitment / mixed / unknown | Code only with source evidence meeting 2022 framework criteria |
| social_use_tested_negative | yes / no / unknown | yes only if explicit suitable behavioral test, adequate time/follow-up, method and detection effort; missing paper = unknown |
| verified_behavior | causal_information / evidence_consistent_social_use / coforaging_only / roost_association_only / negative_suitably_tested / unavailable | Primary evidence ladder; MUST preserve distinct mechanisms |
| response_grade | A / B / C / D | A intervention/cue manipulation; B matched tracking with independent null; C descriptive; D review-only or inference by diet/colony |
| study_effort | numeric / NA | Original observation animal-nights, tracked independent bats, bouts and duration separately |
| literature_effort | numeric / NA | Species-specific study-count proxy using predeclared reproducible search, publication and year bounds |
| measurement_visibility | direct / proxy / missing | Was the proposed mechanism actually observed, not only inferred? |
| coder_predictor_id | text | Coder for ecological predictors, blinded to behavioral labels |
| coder_outcome_id | text | Coder for behavioral observations, blinded to predictor classifications |
| disagreement_status | agree / arbitrated / unresolved | Audit trail; unresolved coding retained as unknown |
| extraction_quote_location | source section/table/page | Short traceable pointer, do not republish long copyrighted content |
| coding_notes | text | Contradictions, site differences, competing explanations |

## Stratified model expectations

Primary 1 (conditional strategy): restricted to direct or plausible social-information-use evidence, where use location, relative persistence and exact study/population are recorded. Avoid absence claims.

Primary 2 (occurrence/detection): only studies with measured positive AND suitably tested negative information use are eligible. Detection heterogeneity is modeled, not replaced by zero-filling.

Sensitivity 1: strict grade A/B only; 2: drop all review-only or ambiguous strategies; 3: exclude surrogate diet-coded persistence; 4: collapse one population/species at a time; 5: separate experimental playback versus field telemetry; 6: fit multiple phylogenetic trees and study-level cluster resampling.

## Reproducibility and failure tests

- Unit checks: no duplicate case_id, DOI normalized, organism names accepted, populations not assumed equal across countries, measures with units.
- Leakage check: ecological predictors not extracted based on an observed social strategy; review theory does not act as independent 2023+ confirmation.
- Measurement check: no use of 3D vertical identity or overlap as observed personal memory or social information.
- Core falsifiers: shorter-than-bout patches frequently support directly documented away-patch recruitment; long-lived patch strategies remain exclusively short-range under adequate independent methods; out-of-study predictive gain does not exceed guild-only baseline; within-population changes cannot be replicated.
- Only after feasibility gate and blind coding: model fit, effect interval and prediction-interval estimates may be reported.
