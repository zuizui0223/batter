# H1 v2 coding addendum — WHERE / WHEN / WHO / RISK, 2026-11-19

This addendum complements (does not replace) \`H1_CODING_DICTIONARY_V1.md\`. It operationalizes the prospective value-of-information model in \`H1_TWO_CHANNEL_DECISION_RULE_AND_FALSIFIERS_V1.md\`. NO independent double-blind coding or new biological effect estimate is claimed.

## Source grain and neutral evidence layers

Primary case = paper × original experiment × species × independently justified physical population × food/context × stimulus. A row remains a *source case*, not a bat/species replicate, and one study may supply multiple cue categories but not multiple independent geographic samples. Use source DOI / exact file checksum and observation unit.

| Field | Allowed states / units | Meaning / exclusion |
|---|---|---|
| \`cue_channel\` | who / where / when / payoff / risk / compound / unresolved | **Content of experimentally available cue**. 'Who' identifies sender; 'when' predicts resource activation; 'where' changes location knowledge; 'payoff' predicts benefits/cost of sharing; 'risk' signals predation or cost of emission. Code "compound" when identification is impossible |
| \`cue_provenance\` | emitted_acoustic / received_acoustic / carried_odor / following / conspecific_location / visual / other | What physical evidence was actually delivered or detected |
| \`spatial_resource_repeatable\` | directly_measured / independently_cited / guild_proxy_only / unknown | A fixed tree or pond is not automatically independently measured spatial memory |
| \`resource_available_prior\` | numeric probability (0,1) / NA | Food present before cue, measured at the same field site with period coverage, not guessed from frugivory |
| \`resource_cue_sensitivity\` | numeric (0,1) / NA | P(cue positive | resource available) **independently measured** |
| \`resource_cue_false_positive\` | numeric (0,1) / NA | P(cue positive | resource absent) **independently measured** |
| \`memory_navigation_success\` | numeric 0–1 / NA | Tagged bat re-finds a familiar patch in a *no-social-cue* test with physical identity and effort |
| \`resource_payoff_observed\` | verified capture/reward / attack_proxy / visitation_proxy / movement_only / none | Never relabel buzzes/head waggles as captures |
| \`travel_cost_measured\` | measured / only_modeled / NA | Reward-commensurate cost in same species/site |
| \`cue_cost_measured\` | measured / only_modeled / NA | Receiver investment to sample social cue |
| \`signal_emission_risk\` | direct_predator_manipulation / predator_cue_only / indirectly_cited / unknown | Predator playback induces caller suppression, not direct fitness cost or actual predation hazard |
| \`receiver_individual_key\` | stable / momentary_pass / missing | Serial playback phases linked to physical bat IDs? |
| \`population_key\` | verified / unresolved / missing | Repeat sessions nested by physical community? |
| \`cue_control\` | genuine_silent / different_conspecific_signal / heterospecific_signal / noise / before_phase / none | Zero-buzz search calls ≠ no-social-cue silence |
| \`private_and_social_in_same_bats\` | yes / no / unknown | Both independently measured in same bats, not ecological story inferred from species diet |
| \`identifies_bayesian_VOI\` | yes / no | Needs independently identified \`m, p, cue TPR/FPR, reward, visit cost, cue cost\` **and actual visit policies**; a signed playback effect alone is not enough |
| \`observation_or_response_selection\` | all_exposed / responder_only / outcome_excluded / unknown | 38 responsive Costa Rica animals not interchangeable with 117 exposed; 2019 pre=0 and during=0 exclusion posttreatment |
| \`new_external_study\` | verified / repeated_prior_art / unknown | Independent source for a *matching estimand*, not merely distinct year/region |

## Statistical target (future, not computed here)

For **timing-only** social information at familiar patches, estimate
\[
E[\text{profit from cue}\mid \text{private no-cue memory }m,
  \pi,a,b,R,c_v,c_s] -
E[\text{profit with no cue}\mid m] .
\]
Regress externally validated gains on pre-registered decision thresholds, not on guild labels alone. Expect a switch from increasing to decreasing *marginal* cue value when \(m\) crosses the no-cue visitation threshold under the special case in the frozen v1 model. Outside that regime, do not impose a universal inverted-U.

Under weak experimental evidence, fit **no effect model**: report missing design columns/source support and do not fill trait values by natural-history assumptions. The planned source-ledger audit can code the known papers immediately but no rate comparisons can be fitted until an independently measured test.

## Disconfirming outcomes

- If a cue labeled solely "temporal activation" produces accurate spatial discovery in bats experimentally proven to have no prior patch location memory, the cue must actually carry location content or the gating model is false.
- If timing-only cue sensitivity/false-positive rate fails to predict posterior food availability after conditioning on study site, source channel label is unsupported.
- If known risk signals suppress emitting social calls but still make receivers visit familiar food sites, sender/receiver action channels should be modeled independently; do not interpret silence as low capacity to learn.
- Cross-study region portability is evaluated by independent source/population holdout, not by 4 bird- or bat-recording channels in one experiment.

## Prior art and source interpretation

The 2024 Egyptian fruit-bat roost odour field experiment (Lourie et al. DOI 10.1098/rstb.2024.0060) shows a *social temporal-information × existing spatial-place* mechanism as interpreted by the authors. **It did not measure the continuous \(m\) used in the illustrative decision model for all bats.** Gamba-Rios et al. 2025 (DOI 10.1098/rsbl.2025.0042) directly manipulated predator calls and measured selected individual social-calling suppression; **it did not directly measure the payoff of cue emission nor a resource-reward decision**. Treat the 2022 social-information review (DOI 10.1111/brv.12881) as prior art, not held-out source.
