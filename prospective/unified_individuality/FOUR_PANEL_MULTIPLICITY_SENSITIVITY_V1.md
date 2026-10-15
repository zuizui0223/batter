# Original four-panel multiplicity sensitivity — individual fidelity versus segregation

**Date:** 2026-10-15  
**Evidence tier:** exploratory **post-outcome arithmetic on original frozen p-values**, not a new GPS/DEM computation, new permutation, independent replication, or prospective experimentwise error-control claim.

## Scientific question

Do the reported contrasts — repeatable conditional terrain-relative flight-height use (**V_rel**), *added* terrain-relative vertical segregation (**S_rel**) and extra separation during coarse synchronized co-use (**I**) — have the same sensitivity to four-panel multiplicity?

We do **not** combine the three endpoints into a single family. For a transparent *within-endpoint* sensitivity only, apply the step-down Holm adjustment separately to the **four originally eligible source-study panels** of each family. This check was defined **after seeing** original results; it cannot reverse any original source verdict or substitute for prospectively freezing all tested outcomes and selection decisions.

The source panels represent **two species**, not four taxonomically independent replications: `H. monstrosus` and three distinct `P. hastatus` collection panels.

## Recalculation using original frozen source p-values

| Source panel | V_rel raw / Holm | S_rel two-sided raw / Holm | Co-use I upper-tail raw / Holm |
|---|---:|---:|---:|
| *H. monstrosus* | 0.0001 / **0.0004** | 0.0362 / **0.1448** | 0.9045 / 1.0000 |
| *P. hastatus* 2022 | 0.0001 / **0.0004** | 0.3639 / 0.8113 | 0.9186 / 1.0000 |
| *P. hastatus* 2023 | 0.0001016 / **0.0004** | 0.2704 / 0.8113 | 0.0231 / **0.0924** |
| *P. hastatus* 2016 | 0.03453 / **0.03453** | 0.4796 / 0.8113 | 0.8611 / 1.0000 |

**Within-family results at 0.05:** V_rel remains supported in **4/4**; two-sided S_rel remains supported in **0/4** after Holm (original one nominal negative-direction *Hypsignathus* p = 0.0362); co-use remains supported in **0/4** after Holm (original one nominal positive *P. hastatus* 2023 p = 0.0231). **Positive S_rel was already unsupported in 0/4** at the source's unadjusted per-panel level.

The 2023 co-use interval in the source was wide (95% dyad-bootstrap compatibility −4.63 to +11.73 m for a +3.57 m excess) and the endpoint used 600-second **all-space** exposure; it is not a harmonized 60-second endpoint-excluded experiment. The p = 0.0231 nominal source result remains historically true, but its inferential tier should now be described as **suggestive, not multiplicity-robust**.

## Exactly what is computed

Given a family of `m=4` original p-values, order them `p_(1) <= ... <= p_(4)`; the Holm-adjusted value for the jth ordered test is `min(1, max_{k<=j}[(m-k+1) p_(k)])`. Map adjusted p-values back to the original panel order. No new null values or outcome statistics are produced and no post-hoc choice of a favorable subgroup was made for these four displayed panels.

Holm controls within a **declared family** of valid input p-values under arbitrary dependency; here the family was retrospectively selected as a **sensitivity** on the published four-panel subset. Neither selection of the original source studies nor the additional developmental/laboratory/out-of-domain studies is included in this arithmetic. Importantly, Holm does not correct across the **V, S and I** families simultaneously, or across all earlier attempts and analysis choices, and the original post-outcome nature of the terrain and co-use results remains.

The 2016 V_rel adjusted p = 0.03453 is close to the threshold, and source coverage, sample eligibility, possible tag errors and vertical datum mismatches remain; therefore even the V result cannot be interpreted as a bat-wide population prevalence or a mechanism shared between species.

## Ecological reading

**Supported but narrowly:** identity-correlated terrain-relative vertical configurations persist under the source permutation definitions in four structurally evaluable tracking studies. Individual-specific conditional height-use information cannot be reduced to an observed need for continuing, strong between-animal vertical segregation. The observed data remain compatible with task allocation, within-task policies, small-scale environmental heterogeneity and some competition histories.

**Not shown:** true zero segregation at any spatial scale; no horizontal partitioning; ecological equivalence; no resource competition; one causal behavioral program connecting different experimental bat systems to the field; or a generic species-level probability of individual specialization.

## Integrity and reproducibility

- Original source values: `figures/FROZEN_FIGURE_DATA_V1.json` (Git blob `b3f7b20136d028021a3c33a43c256e40ce91f677`), `figures/ORIGINAL_TERRAIN_RELATIVE_3D_SOURCE_V1.json` (Git blob `08631a0dce61cc47e12b2d32642c46b5759fe872`) and `figures/ORIGINAL_TERRAIN_PARTITIONING_CALIBRATION_V1.json` (Git blob `e969698e2a594d2eeca2631d7473e598a8a8f371`).
- Machine-derived per-panel unrounded arithmetic, original source p-values and explicit analysis-class limits: `figures/FROZEN_FOUR_PANEL_MULTIPLICITY_V1.json`.
- Independently recomputing and hash-guarding the arithmetic: `validate_four_panel_multiplicity_v1.py`.
- Original positive co-use at the **nominal per-panel** level remains in Fig. 6 and source Results without relabeling original success gates. Corrected sensitivity is clearly kept separate.
