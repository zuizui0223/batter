# Ducke v3: one coherent four-guild composition probability model (frozen, source-open exploratory)

2026-11-20. **Post-outcome methodological robustness only**. Both original Ducke response and v1/v2 positive contrasts have already been inspected. Freezing v3 code and source support before running v3 outcomes is good audit discipline but **not external preregistration**.

**Biological question:** Does the separation of 12 published candidate food genera and 10 remaining fruit-bearing genera add heldout information for the **entire captured bat guild composition**, not merely three dependent binary fractions considered separately?

**Source and denominator:** Same SHA-pinned original Ducke ZIP and same 46 original plots, 103 exact-site/date source nights, 810 captures. Four observed major guilds are Frugivore (573), Gleaning animalivore (132), Nectarivore (58), Aerial insectivore (46), totaling **809 captures**. The 1 Sanguivore capture is reported and **excluded**, not reclassified or imputed; the four-guild response is normalized by the sum of the four counts at each plot. Original count and source year inconsistencies remain intact.

**Multivariate estimand:** Heldout per-plot `Σ_g observed_share(g) log predicted_share(g)` for 4 guild classes under one normalized softmax distribution, *not* a four-way species occurrence model. One plot receives weight one irrespective of number of captured bats. Each heldout source group is excluded entirely; training-only feature centering/scaling, fixed reference aerial guild, ridge `λ = 0.15` on all non-intercept slopes. No multinomial p-value is generated.

**Five frozen covariate models:** identical to v2 baseline (terrain elevation + added PO sampling-frame indicator + same-date matched-night count); baseline + candidate12 F; baseline + other10 O; baseline + F and O separately; baseline + total22 fruit amount. Apply log1p to resources. All fits have same withheld plots and scored guild composition; calculate `FO-B`, `FO-G`, `FO-F`, `FO-O` on identical test responses.

**Validation scope:** Primary 7 complete original sampling-layout blocks; secondary L3–L8-only subset (29 plots / 6 blocks) to avoid PO-stratum extrapolation. Do not change original count floor, source group definitions, regularization or rare-guild handling after outcomes. No new spatial permutations, significance tests or target reallocation. No GIS metrics guessed from unavailable clutter or site coordinates.

**Claim boundary:** A positive joint-composition model would strengthen *local captured-guild composition* predictive evidence from one already-published study; it cannot identify actual plant feeding interactions, causal resource partition, physiological specialization, universal SDM, or resource-conditioned 3D flight. No independent matched animal altitude in Ducke. The global NeoBat original M3−M1/N1 remains NOT ESTIMATED.

Reproducible model: `ducke_joint_guild_composition_v3.py`; known-truth source-free regression `test_ducke_joint_guild_composition_v3.py`. Raw 46-source plot aggregates and individual bat records remain local, never uploaded.