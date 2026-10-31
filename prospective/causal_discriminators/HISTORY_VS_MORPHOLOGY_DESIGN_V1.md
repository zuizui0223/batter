# Prospective discriminator v1: learned history versus flight morphology

**Status:** DESIGN ONLY; no new empirical endpoint opened. This document is a prospective proposal, not an existing preregistration or evidence of a completed field experiment.

**Isolation:** based on `prospective/public-causal-synthesis-v1`. Do not modify the frozen JAE v0.3.8 submission or the later v0.4.0 synthesis. No reopened exploratory archive test is authorized by this document.

## 1. Decision

**First discriminate personal learning/history from stable morphology by randomizing prior task experience while holding the test geometry constant.** Measure wing morphology at the same time, rather than treating mass as a complete proxy or merely re-running a cross-sectional mass correlation.

This is more informative than an uncontrolled fruit-phenology correlation: a tree or location turnover changes the task and available resources, and cannot alone separate memory from fine-scale microhabitat selection, wind, competition and flight-mechanical demands.

## 2. Evidence motivating the test (not causal proof)

- Original bat tracking: five comparative panels retain centered vertical-shape individuality after session-median centering; focal `Tadarida` is the failed boundary panel.
- After speed-by-turning state matching, 5/5 retained calibrated centered identity.
- After matching 500-m horizontal place and broad kinematic state, 4/4 *evaluable* panels retained calibrated identity. This does **not** condition on exact trees, approach trajectories or sub-500-m microtasks.
- A frozen four-panel body-mass donor-gradient analysis supported the predicted morphology-proxy transfer in 0/4 panels. Wing loading, wing shape, physiological condition and developmental morphology remain unresolved.
- Field temporal persistence is supported within the predeclared evaluable 1-, 3-, and 7-day panel sets, but is observational.
- Wild synchronous vertical segregation is not generally supported. This does not falsify competition acting through food, time, social access or behavior.
- Lab `Rhinolophus` results support a portable low-dimensional personal policy across tested obstacle settings, but the field policy-to-vertical-shape carrier predeclared gate failed (2/4). The lab policy should not be assumed to cause the wild centered vertical shape.

Evidence locations: `post_freeze_extensions/MECHANISM_SYNTHESIS_V1.md`; `post_freeze_extensions/body_mass_gradient_four_panel/RESULT_V1.md`; `post_freeze_extensions/strategy_maintenance/STRATEGY_MAINTENANCE_SYNTHESIS_V1.md`; `prospective/task_reset_lockin/SELF_MAINTAINING_SPECIALIZATION_SYNTHESIS_V17.md`.

## 3. Causal contrasts and hypotheses

The causal object is **how a measured individual's conditional vertical flight distribution changes when training history is assigned**, for the *same independently defined physical test task*.

### H_history: experience-dependent individual solution

Assignment to repeated experience with one of two behaviorally meaningful but physically matched approach solutions causes a change in the bat's later vertical profile **under the same standardized test geometry**. After a randomized reward/cue reversal, the response may reorganize or show hysteresis, with a different rate of adaptation for familiar versus unfamiliar solutions.

### H_morph: persistent biomechanical matching

Measured wing loading, wing aspect ratio, wingspan, body condition and age/reproductive class predict conditional vertical profiles across contexts. At the standardized test, randomized prior training produces no systematic between-assignment difference beyond the prespecified equivalence bound. **Failure to detect H_history is not, by itself, evidence for morphology.**

### H_microtask: unmeasured route/resource allocation

Within the same 500-m cell, individuals actually sample different fine routes, exact trees, approach directions or activity states. Their apparent shape identity disappears after exact microtask, speed/turning and time-window matching.

### H_environment / H_social: alternative explanations

Individual responses to localized wind/updrafts or conspecific presence can produce vertical identity or route-use changes. Record and condition on measured airflow, season/night/time, competitor occupancy and resource quality; do not claim these mechanisms excluded when support is sparse.

## 4. Study design

### Phase 0 — feasibility, welfare and independent preflight

Use an authorized bat research facility and a species already habituated to repeated non-depriving foraging or obstacle tasks, with all applicable capture, animal-care and ethics approvals. Do not select species because its centered-shape outcome is already positive. Prefer multiple independent colonies or cohorts for external validity.

Set up two geometrically comparable, counterbalanced routes/approach tasks, A and B. Calibrate 3-D tracking and fixed device/stationary offset. Use independent ground truth for source/target resource, behavioral phase and route identity. **Before viewing vertical outcomes**, verify that sufficient individuals and repeated sessions share exact route × task × measured environmental support. Build power by simulation from predeclared minimally relevant effects and actual within-bat variance, not by picking an arbitrary large fix count.

### Phase 1 — baseline and randomized experience

- Before training, measure each bat's body mass, wing area, wingspan, wing aspect ratio / loading proxy, age class, reproductive condition and body condition; repeat measurements when condition may change.
- Randomly assign individuals *within cohort and morphology strata* to train on A or B; counterbalance geometry, reward, trainer, task order and times. Provide equivalent accessible food/reward and a sham/control schedule; avoid food deprivation.
- Record repeated high-frequency 3-D trajectories, exact approach geometry, flight state, individual ID, environmental conditions, resource/cue access and co-presence.
- Keep experimenter handling and tag placement calibrated, with independent tag swap or cross-device checks if sensors differ.

### Phase 2 — common held-out probe (PRIMARY)

All individuals experience the **same physically matched, standardized probe task**, with reward availability and local conditions standardized. Score each bat's centered vertical use over independent held-out probes. Compare randomized training assignments under the same probe context; analyze whole individual sessions, not fixes as independent replicates.

Primary causal estimand: the intention-to-treat effect of assigned A versus B history on a prespecified conditional centered vertical profile at the common probe, with paired within-individual baseline adjustment. Choose the scalar test (e.g., cross-fitted log predictive density or a distributional distance with a prespecified direction/threshold) **before vertical data opening**. Hierarchical assignment inference must randomize at the individual level and preserve all within-session spatiotemporal structure.

A positive randomized training effect under identical probe geometry demonstrates a history effect on expressed vertical organization, but **does not alone identify a neural memory mechanism**; motor adaptation, learning, motivation and habituation still need separation.

### Phase 3 — reversal / reacquisition (SECONDARY)

Randomize cue/reward contingency reversal while holding corridor geometry constant. Retest after repeated exposures, then reintroduce original contingency. Measure latency, profile change, retention/recovery and whether changes follow the assigned experience. Use counterbalanced reversal timing and parallel sham-reversal controls. A recovery/hysteresis signature strengthens history dependence but does not prove an internal cognitive map.

### Phase 4 — ecological bridge (INDEPENDENT VALIDATION)

In wild fruit/flower users, map exact resource individuals, phenology and approach sectors, measure terrain-relative calibrated altitude and concurrent localized airflows, and follow individual transitions during natural resource turnover. Use previously defined study-level sampling gates. This phase tests whether the controlled history-dependent pattern generalizes to free-ranging 3-D use; a natural turnover association alone remains observational.

## 5. Primary outcome, matching and inference

- Primary outcome: session-median-centered vertical **distribution conditional on exact physical probe route, independently scored movement state, time window and environmental strata**. Centering handles additive height zero-points, but separately check noise-scale and sensor properties.
- Primary unit: biological individual, with repeated sessions nested within individual and cohort. Avoid pseudoreplication from millions of fixes.
- Primary comparison: assigned-history effect on held-out conditional vertical shape at an identical test context, adjusted for baseline and design strata. Use a single predeclared measurement scale and leave-whole-session-out prediction.
- Secondary mechanism tests: among matched non-self donors, wing-loading similarity versus transfer score; response-to-airflow interactions; conditioning on exact tree/route; reversals; policy-to-profile mediation only when explicitly identified.
- Negative claim criterion: failure of a significance test is not mechanistic exclusion. Report compatible effect sizes, prespecified smallest meaningful effect and uncertainty; use equivalence only with justified power and bounds.
- Null calibration: preserve whole-session correlations, individual treatment assignment, source cohort, sampling opportunities and nuisance fitting. Never use a zero-centered estimator null by assumption; simulate the complete prediction and matching pipeline under proper assignment/exchangeability nulls.
- **Structural STOP:** If cross-individual common-probe support, independent state labels, reliable altitude, true training randomization or enough independent individuals fail a frozen gate, do not interpret a vertical endpoint as a mechanism test.

## 6. Predicted result signatures

| Observation under matched probe | H_history | H_morph | H_microtask / other |
|---|---|---|---|
| Assignment-specific shape difference after matched training | predicted | not explained by fixed traits alone | possible if actual probe task differs; audit |
| Reversal-specific change with reacquisition/history dependence | predicted | not sufficient alone | could reflect altered reward or task state |
| Stable trait–shape donor transfer with no training effect | not primary prediction | consistent, not causal proof | alternative traits may confound |
| Individual identity disappears after exact route/state conditioning | not required | not required | supports microtask composition as sufficient under measured support |
| Individual identity persists with no competitive co-presence | possible | possible | does not rule out indirect competition |

## 7. Existing public-data bridge: 2-D only, not a substitute

Lourie & Nathan 2024 Dryad dataset (DOI `10.5061/dryad.51c59zwgp`) documents fruit-odor information manipulation and individual tracks of *Rousettus aegyptiacus*. The official archive lists `TAG`, `TIME`, `X`, `Y`, speed and 2-D location uncertainty, **not numeric altitude**. It can be used separately for preregistered 2-D navigation/route-memory outcomes. It cannot validate causal effects on centered 3-D vertical shape. Verify source files and experimental grouping before any quantitative reuse.

Relevant prior evidence:
- Toledo et al. 2020, *Science*, DOI `10.1126/science.aax6904` (spatial navigation, mapped fruit resources, translocations).
- Harten et al. 2024, *Current Biology*, DOI `10.1016/j.cub.2024.05.046` (experience-dependent spatiotemporal resource use).
- Iriarte-Diaz et al. 2012, *PLOS ONE* (individual-dependent kinematic responses to loading; verify citation on literature import).

## 8. Publication/claim boundary

A **positive randomized history effect** would establish that stable morphology alone is insufficient to explain the change in measured 3-D vertical organization in the tested task. A complementary trait-transfer effect could show persistent biomechanical contribution. Neither result by itself proves fitness benefit, reproductive specialization, competition release, cognitive-map navigation, or universal prevalence across bat species.

Do not merge this design into the frozen JAE paper as a completed result. On new data, register the hypotheses, structural sampling gates, estimands, error control and data-analysis code prior to outcome access.
