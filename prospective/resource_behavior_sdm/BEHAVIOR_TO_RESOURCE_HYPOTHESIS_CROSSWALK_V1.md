# From supported bat behavior to testable resource-conditioned SDM

2026-11-20 | prospective evidence crosswalk; no new empirical model outcomes.

## 1. What the observed behavior really supports

| Evidence source | Actual result | Transferable role in the new model | Not proved |
|---|---|---|---|
| batter main six bat panels | Same-individual centered vertical distribution shape is supported in 5 comparative panels; Tadarida is a boundary case with absolute-level identity rather than centered-shape identity | Predictive personal vertical probability distribution conditional on place | Food selection, personality, stable movement force, causality |
| batter prospective unified manuscript PR #99 | Terrain-relative individual vertical fidelity is observed in 4/4 tropical 500-m panels (two species); positive excess physical vertical segregation 0/4 | Separate identity fidelity from competitive spatial partition | Resource partition or exclusion, absolute altitude policy |
| batter individual vertical strategy source test (main) | 8 individuals, 5,473 eligible events; identity map reassignment p=0.000173611 in predeclared source test | Stable conditional map/policy component possible | Transfer to another species, resource dependence |
| batter post-freeze resource-patch fidelity | 5-panel primary mean Spearman rho +0.1759, p=0.05731, 4/5 panel correlations positive: **FAIL**. Eidolon pooled cohort association negative | Avoid identifying resource dependence with same horizontal patch reuse | Horizontal patch fidelity as general mechanism of vertical individuality |
| batter exploratory field policy variance decomposition | 2022: vertical individual REML variance fraction 0.7338, horizontal 0.3171 (228 sessions, 34 bats, 39 source days); 2023 vertical 0.3913, horizontal 0.2810 (43 sessions, 11 bats, 9 source days) | Model stable individual intercept PLUS variable source-day/session context | Stable width/policy slope, independent resource cause, inferential difference test |
| batter field policy breadth persistence | 2022 frozen primary p=0.0899, 11/16 positive (<70% required); 2023 **STRUCTURAL STOP** | Do not assume each individual has invariant behavioral variance | Persistent personal full policy distribution |
| boids synthetic v11 resource/social ablation | Assigned target contrasts create niche axes even with social off; personal targets can impose individuality | Require resource-only and identity-target negative controls | Observed resource-driven bat niche partition |

Source verification: [main behavior results](https://github.com/zuizui0223/batter/blob/main/README.md), [individual vertical strategy](https://github.com/zuizui0223/batter/blob/main/results/individual_vertical_strategy_result_v1.json), [PR #99](https://github.com/zuizui0223/batter/pull/99), [resource patch fidelity](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/post_freeze_extensions/resource_patch_fidelity/RESULT_V1.md), [field policy variance](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/prospective/field_policy_bridge/FIELD_POLICY_VARIANCE_DECOMPOSITION_RESULT_V1.md), [breadth test](https://github.com/zuizui0223/batter/blob/prospective/unified-be-jae-individuality-v1/prospective/field_policy_bridge/FIELD_POLICY_BREADTH_PERSISTENCE_RESULT_V1.md), [boids v11](https://github.com/zuizui0223/boids/blob/main/docs/RESOURCE_AND_SOCIAL_DRIVER_ABLATION_V11.md). The source files are not copied or rewritten.

## 2. Two rival, distinguishable behavioral resource pathways

**A — State allocation:** independently measured food availability R(x,t) changes the share of verified behavioral states pi_i(b | x,t,R); each state has approximately stable p_i(z | x,t,b). Repeated individual vertical distributions result from persistent personal *mixture proportions*.

**B — Within-state selection:** resource opportunity changes the vertical choice kernel phi_i(z | x,t,b,R), even after independently annotated commute/forage/rest states are held constant. This is stable individual within-state use rather than just allocation.

These mechanisms can coexist. A third alternative is **neither**: sensor errors, roost/travel task mix, unmeasured forest structure or source-day effort explains the observed height profiles. No current resource × tagged behavior joint dataset resolves them.

Under either pathway, individual 3-D use can be persistent while actual spatial overlap remains high. Vertical individuality need not be between-animal segregation. Resource-driven *height* differences do not require a positive horizontal range AUC increment.

## 3. Different predictions and nulls

| Trial | Test target on heldout sessions | A state allocation predicts | B within-state selection predicts |
|---|---|---|---|
| B1: baseline | p(z | individual, XY, time) | Identity may persist | Identity may persist |
| B2: independently annotated state | p(z | individual, XY, time, b) | Residual individual contrast attenuates if allocation fully explains identity | Residual individual contrast persists |
| B3: independently measured fruit opportunity | p(b,z | individual, XY,time,R) compared on same event support | Gain mainly through p(b|R) | Gain mainly through p(z|b,R) |
| RN1: rewired partners | Same B3 score but source-linked resource identities degree-preserving rewired | True resource identity must beat N1 to claim trophic specificity | Same criterion |
| O: sensor and effort | Exact identical use versus detection-stratified event sampling | Detectability can mimic activity | Height error can mimic within-state policy |

Use paired out-of-sample log-score ablations, not only raw mutual-information differences. In general I(individual;Z | X,T) minus I(individual;Z | X,T,B) is **not** a causal mediation effect: conditioning can increase or decrease association. Task annotations must be independent of the heldout height endpoint.

## 4. Current hard eligibility boundary

NeoBat original fruit-source cohorts and batter tracked tropical bats are not matched at individual × species × site × time. Source/raster qualified 36/84 bat-country folds concern **prefit 2-D source support**, not the needed time-aligned resource plus 3-D tracking join. Therefore both A and B remain hypotheses; do not reuse the negative 49-fold source-rank shadow to declare resource irrelevance to behavior.

Immediate empirical admission requires original fruit phenology or quantified prey resources measured independently within the movement-available area and dates of tagged bats, validated state labels, standardized height reference, source- and geography-disjoint heldouts, independent effort/detection model, and actual vs rewired resource predictors. Until then: JOINT_HIGHDIM_ECOLOGICAL_GAIN = NOT_ESTIMATED.
