# Ducke four-guild *joint* resource composition prediction: executed v3

Date: 2026-11-20. **Exploratory single original study**, no preregistered inference or independent external test. Frozen source-open v3 design and full source-free multinomial Newton algorithm: [commit `abec244`](https://github.com/zuizui0223/batter/commit/abec244fb044fcff90f6fe368ebd76c92a2ef2b0). Outcomes only opened subsequently for this v3 test. Original Ducke Dryad ZIP `10.5061/dryad.9rb48c5`, SHA-256 `55c784e2f7b37987e3657d3ba3d5cf6a41bb3554a11904969d1376c977bcdbce`.

## What changes scientifically

The earlier frugivore/gleaner/nectar logistic regressions used **dependent shares of the same captured animals**. We now score their full composition in **one normalized four-category multinomial distribution**. We preserve all 46 exactly same-site/same-date matched plots and the seven source layout blocks. Original captured four major guilds: **573 frugivores**, **132 gleaning animalivores**, **58 nectarivores**, **46 aerial insectivores** = **809** captures. One recorded sanguivore is **excluded and disclosed**, never recoded into another guild. All four-guild outcomes are conditional **mist-net capture composition**, not site occupancy or real plant-foraging choices.

Training shares are scored equally per plot by `Σ_g observed_site_share(g) × log predicted_site_share(g)`. Training-only normalization, same baseline (terrain elevation / additional PO sampling-frame membership / matched nights), and the exact `0.15` L2 penalty on non-intercept logit slopes. Four-guild softmax reference class = aerial insectivores. Candidates: 12 bat-food candidate fruit genera F, 10 other recorded fruit genera O, F+O separate, and pooled 22 genera count G.

## Original-source heldout scores (nats per captured guild-share distribution)

| Paired candidate versus baseline/other | Seven withheld source blocks / 46 plots | Positive blocks | L3–L8-only six withheld blocks / 29 plots | Positive blocks |
|---|---:|---:|---:|---:|
| F+O as separate predictors − baseline | **+0.0287690** | **6/7** | **+0.0228781** | **6/6** |
| F+O as separate − one pooled total fruit score | **+0.0261067** | 5/7 | **+0.0137781** | 5/6 |
| F added after O | +0.0118547 | 4/7 | +0.0029339 | 3/6 |
| O added after F | +0.0115331 | 6/7 | +0.0152388 | 5/6 |
| F alone − baseline | +0.0172359 | 4/7 | +0.0076393 | 3/6 |
| O alone − baseline | +0.0169143 | 6/7 | +0.0199442 | 6/6 |

**The whole-guild prediction agrees with the original single-frugivore challenge in its broad direction:** splitting fruiting-plant composition yields more conditional predictive information than adding a single total fruit count. This survives removing the added PO sampling-frame plots, and is no longer an artifact of treating three compositional guild fractions as independent tests.

**Important narrowing:** F after O is modest and becomes +0.002934 in the 29-plot L-only population. O after F remains +0.015239 in that population. Thus the result **does not uniquely implicate the 12 candidate food genera**. The 10 other observed fruit genera are not guaranteed to be unconsumed; they can capture unmeasured habitat structure/plant assemblage patterns. The two-predictor model also has greater flexibility than the one-total model; out-of-block scoring alone in one reserve does not demonstrate ecological mechanisms.

## Numerical reproducibility

An **independent SciPy L-BFGS-B implementation** was fitted directly to the user-uploaded SHA-verified original, comparing exactly the same heldout plots and model contracts. Repeating all primary and six-band contrasts with a separate **pure-stdlib full-Hessian Newton implementation**, mathematically matching the frozen GitHub source-free engine, gave maximum absolute difference **3.0808079×10⁻⁸ nats** across all reported contrast estimates. The current GitHub [source-free CI](https://github.com/zuizui0223/batter/actions/workflows/resource-behavior-higher-dimensional-sdm-v1.yml) validates source-free known-truth properties, NOT an independent GitHub replay of original GPS/fruit data. Original bat-identity or plot-level location values are never committed.

## Claim tier and hard limits

- **Supported at this tier:** Within the single original Ducke sampling universe, independently surveyed fruiting-plant **composition** contains heldout predictive information for **captured bat guild composition** beyond the limited baseline, sometimes despite a non-positive total fruit-score model.
- **Not supported:** Exact plant–bat feeding, guild-specific causal diet selection, absolute habitat/occupancy, spatially independent external replication, resource-conditioned vertical flight, or a universal 3D/5D SDM. One rare sanguivore excluded; unmeasured vegetation clutter, source date anomalies, imperfect sampling effort/animal detection, uneven 17 PO sites, and dependence among source blocks remain.
- No fresh p-value, confidence interval or confirmatory significance statement is added to an already-opened original study. Publication prior art (Capaverde et al. 2018) is not rebranded as new biological field observation.

This is a **multivariate local lower-dimensional resource layer** that can motivate, but not numerically substitute for, a matched bat-identity × resource × time × 3D-height source. Original NeoBat species-level M3−M1/N1 is NOT ESTIMATED. Frozen JAE, BE, esdm main and batter main are unchanged.

Reproduce v3 with [fixed code](ducke_joint_guild_composition_v3.py) and [fixed source-open design](DUCKE_JOINT_FOUR_GUILD_V3_DESIGN.md) after locally importing the SHA-qualified Ducke source. Small aggregate [v3 result receipt](ducke_joint_guild_v3_result.json).