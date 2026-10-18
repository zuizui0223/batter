# What is maintained? — Ecological identifiability and decisive tests v1

**Status:** Theoretical/interpretive synthesis of previously completed source analyses only (2026-10-14). **No new wild-data test, outcome opening, threshold search, model fit or independent validation.**

## Central inferential question

The useful ecological question is not merely whether individually held-out vertical profiles are distinguishable. It is:

> When bats repeatedly solve overlapping space-use problems, do they differ primarily in **which tasks they undertake**, **how they solve the same task**, or **how they respond to other bats/environmental conditions**?

The available source outcomes **constrain** these hypotheses but do not identify a unique mechanism. They reveal individualized conditional use of vertical space, not which cognitive, trophic, anatomical or social state causes it.

## Existing ecological priority boundary

Previous ecological studies had **already demonstrated** persistent individual environmental niche differentiation without disjoint or modular niches (white storks; Carlson et al. 2021, DOI 10.1038/s41467-021-24826-x). In bats, spatial individual specialization and horizontal home-range overlap vary together between seasons (*Ia io*; Wang et al. 2023, DOI 10.1186/s40462-023-00394-1). The ecological novelty here therefore **cannot** be that individual niches ever overlap. The narrower possible increment is source-calibrated individual *vertical probability shape* after common horizontal and conditional movement controls, tested alongside separate terrain-relative segregation and contemporaneous co-use nulls. See [prior-art comparison](ECOLOGICAL_PRIOR_ART_POSITIONING_V1.md).

## Three distinct measured objects

1. **Predictive individuality:** whether a same-individual predictor of the held-out vertical-use probability distribution beats an eligible other-individual predictor under the original weighted common-cell support, evaluated against each full-pipeline whole-session permutation null. The observed-minus-null score is calibrated in **nats per fix**; it is **not** a metre separation or exclusive-niche overlap index.
2. **Added segregation:** the original terrain-relative **S_rel** statistic compares same- versus other-individual 3D overlap-distance constructs, again under its own label-permutation architecture. It is not automatically determined by the held-out identity score; the sign and permutation tail are necessary to evaluate evidence for positive added segregation.
3. **Extra co-use separation:** the source I statistic compares median dyad vertical separation at fixed same-500-m-cell encounters with a whole-session phase-shift reference that preserves individual routes and vertical-use patterns. It is neither the S_rel permutation statistic nor a direct estimate of instantaneous competitor avoidance. Its 60-s and 600-s panel windows and endpoint/all-space rules are not interchangeable.

Operational empirical claims:

| Evidence source, JAE rc2 | Frozen source result | What it supports | What it does not establish |
|---|---|---|---|
| Original six panels | 6/6 common-cell vertical identity; 5/5 comparative panels survive session-median centering, focal *Tadarida* does not | Individually predictive vertical-use shape in selected admissible tracking systems after coarse 5-km occupancy alignment and constant height-offset removal | Nonadditive sensor-error elimination, full 3D niche exclusivity, a universal bat behavioral rule |
| Original four tropical field panels | V_rel fidelity 4/4 supported; **positive** S_rel 0/4 supported | Repeatable terrain-relative individuality not consistently accompanied by added 3D segregation at tested scale | Equivalence to zero segregation, absence of resource partitioning, independent replication in four species |
| Fixed local co-use tests | Positive I in *P. hastatus* 2023 only (1/4; +3.574 m, upper-tail p=0.0231)** | A separable context-sensitive interaction/co-use signal is possible in one coarse all-space panel | General competitor avoidance or instantaneous response in a 600-s window |
| Post-outcome 500-m place × speed × turning stress test | 4/4 retain centered identity: calibrated excess +0.384, +0.0868, +0.1015, +0.451 (p = 0.0002, 0.0002, 0.0006, 0.0286; eligible n = 19, 23, 11, 9) | **Coarse** repeated patches (≥500 m) together with 2×2 speed-turn composition are insufficient to account for identity in the eligible subset | Genuine task labels, microhabitat below 500 m, local atmospheric response, self/other fitness differences |
| Same-night 2-km place × kinematic control | 3/4 supported, P2016 p=0.0544 **unresolved** | Shared shifted-night and broad place/movement context alone do not remove the identity advantage in three eligible panels | Perfect within-night environmental matching or transfer to all panels |
| Lag-separated self histories | ≥1 day: 4/4; ≥3 days: 3/3; ≥7 days: 2/2 | Personal predictive information persists across the structurally evaluable spans | A fitted temporal decay law, memory acquisition, persistence beyond observed lag support |
| Frozen continuous wind-slope preflight | STOP at 7/8 required *P. hastatus* 2023; no numeric vertical outcomes opened | Source limitations prevent a predeclared three-panel reaction-norm test | Evidence **for or against** individual wind response |
| Frozen lab-style scalar field bridge | PASS, PASS, FAIL, structural STOP; criterion ≥3/4 therefore **overall FAIL** | Current experimental-to-field scalar carrier hypothesis not validated | Matched same-individual laboratory-to-field mechanism |

The four field rows are **four study panels from two taxa**. Differences in eligible n across lag/state/encounter families prevent interpreting the above rows as independent tests of one identical sample.

## The unobserved-state identifiability problem

Write an individual's conditional vertical-use distribution at horizontal location \(h\) and observed context \(c\) as

\[
p_i(z\mid h,c)=\sum_{k=1}^{K}\pi_i(k\mid h,c)\,q_i(z\mid k,h,c).
\]

Here \(k\) is an **unobserved true behavioral task/state** (commuting, feeding, social use, etc.), \(\pi_i\) is the fraction of within-context time allocated to that state, and \(q_i\) is the within-state vertical-use rule.

Two nonexclusive mechanisms generate the same observation:

- **Task allocation:** \(q_i=q\) across bats, but the \(\pi_i\) differ.
- **Within-task solutions:** \(\pi_i=\pi\) across bats, but their \(q_i\) differ (morphology, learned approach, fine-scale resource choice, micro-weather response).

Absent independent labels for \(k\), a stable and individually predictive marginal \(p_i\) **cannot identify which mechanism carries it**.

### Exact logical counterexample — completely synthetic, not bat data

Consider two vertical bins. Both individuals use both bins; their *marginal* probabilities are

\[
p_A=(0.6,0.4),\qquad p_B=(0.4,0.6).
\]

A purely **task-allocation** construction assigns shared within-task profiles

\[
q_1=(0.8,0.2),\quad q_2=(0.2,0.8)
\]

and personal task proportions \(\pi_A=(2/3,1/3)\) versus \(\pi_B=(1/3,2/3)\). These produce \(p_A,p_B\) exactly.

An equally valid **within-task** construction assigns shared proportions \(\pi_A=\pi_B=(1/2,1/2)\), but sets

\[
q_{A1}=(0.7,0.3),\;q_{A2}=(0.5,0.5),\qquad
q_{B1}=(0.5,0.5),\;q_{B2}=(0.3,0.7).
\]

These **also** produce the identical marginals \(p_A,p_B\). Hence even with infinite precision in a full marginal vertical-use distribution, the two underlying task mechanisms are observationally indistinguishable *without task labels or interventions*.

The toy **overlap coefficient** for the marginal distributions is

\[
O(A,B)=\sum_z\min\{p_A(z),p_B(z)\}=0.8.
\]

Their true-pair log-prediction advantage over each other in the corresponding idealized known-distribution toy is \(D_{\mathrm{KL}}(p_A\Vert p_B)=0.081093\) nats per independent draw (symmetric here). **These are not empirical effect sizes or source S_rel values.** The example only demonstrates that marginal overlap can be high at the same time as individual probability profiles carry positive identity information. It does **not** imply the empirical S_rel would equal zero.

The real 500-m × coarse speed-turn result narrows one possible task-mixture account, because broad categories have been conditionally matched. But within each broad class several unobserved true tasks or microhabitats can remain; these data **do not** identify a latent behavioral policy.

## Competing ecological mechanisms and distinguishing predictions

### A. Stable task-mixture allocation

Mechanism: individuals spend stable fractions of time in different real tasks in otherwise shared airspace.

**Discriminating prediction:** with validated fine task labels (simultaneously collected prey-capture acoustics, accelerometry, video/echolocation, trip phase, actual resource visits), the extra held-out identity advantage should materially **decrease** after matching individual target and training contexts on task and patch. The expected attenuation criterion and task classifier must be frozen **before** opening vertical outcomes. If the advantage remains, pure task-mixture allocation is insufficient.

### B. Stable within-task flight solutions

Mechanism: bats repeatedly implement individual-specific altitudes/approaches for the **same confirmed task**, due to morphology, sensorimotor skill or learned familiarity.

**Discriminating prediction:** conditional identity remains when known task and actual patch are held fixed, with externally calibrated height and body size. Identity transfer across controlled changes in identical tasks may distinguish stable control preferences from mere previous task fractions. A drop after novel-resource relocation/familiarity manipulation would support a history-related component, but morphology and task constraints must be measured concurrently.

### C. Conditional atmospheric reaction norms

Mechanism: (q_i(zmid k,h,c,w)) depends individually on measured wind, uplift, turbulence or air density.

**Discriminating prediction:** after prospective in-situ microclimate measurement and repeated overlap of animals across the same atmospheric covariate ranges, supported individual × weather interactions explain held-out vertical use better than a single population reaction norm. A source-era ERA5 structural STOP is **neither** support nor failure of this mechanism; the new design needs enough independently tracked animals and weather support across individuals before outcomes open.

### D. Social co-presence / interference

Mechanism: instantaneous individual separation depends on who is co-present, not merely on fixed personal altitude preferences.

**Discriminating prediction:** with truly synchronized high-resolution location and calibrated altitude, vertical separation should increase over each individual's own task/weather-matched temporal phase-shift or encounter-shuffled reference **specifically during true close encounters**. The sign and upper/lower equivalence margins should be preregistered using tracking error and ecologically interpretable vertical separation. In the old observations only 2023 is positive, and its 600-s all-space window cannot establish immediate avoidance.

### E. Performance matching vs learning (historical causes)

Both history-dependent habits and stable morphology/wing loading can support personal solutions with no ongoing spatial exclusion. Distinguish them with within-individual repeated body-performance measurements and an ethical randomized change in task familiarity/available routes. Predict a change in conditional within-task vertical use from independently measured information/skill changes after holding performance constant, versus association with stable performance costs across contexts. **No current dataset isolates these causes.**

## Strongest bounded synthesis for the integrated paper

The source evidence is most consistent with *persistent, individually informative conditional probability organization* that is not consistently expressed as increased vertical separation. Such an organization can be reused in shared space; it is not equivalent to ownership of a private vertical layer, and no new task/carrier is identified.

Keep the **negative/positive asymmetry** explicit:

- Positive calibration supports presence of individually predictive vertical organization within eligible panels.
- The absence of supported positive S_rel or I in some panels is **not** a formal demonstration that all meaningful segregation is absent.
- Co-use 2023 is a substantive heterogeneity/exclusion to a universal no-interaction law.
- Component-level profile differences, exact diet/foraging task, morphological mechanisms and fitness remain unverified.

A defensible main conclusion is therefore:

> **Persistent individual vertical-use distributions can remain predictive after coarse place and movement-state matching without consistently detectable added segregation under the source-specific null models; whether the carrier is task allocation, within-task execution, environment response or past experience remains unidentified.**

## Publication and audit boundaries

- All effect summaries above are from frozen original JAE rc2 source receipts and were opened previously. The conceptual counterexample is a **mathematical illustration**, clearly not derived from the archived animals.
- No new wild outcome, data-dependent cluster/strategy type, significance test, preregistration claim, causal meta-analysis, or polished fictitious animal profile has been introduced.
- The experimental controlled sources remain independent and heterogeneous; the scalar lab-to-field bridge failed its own overall criterion.
- Reuse of a cited source archive must respect original redistribution permissions. Review and coauthor sign-off remain mandatory before submission.

### Exact JAE source receipts used

- `post_freeze_extensions/fine_place_kinematic_500m/RESULT_V1.md`, `result_summary_v1.json`, run **36519747717**.
- `post_freeze_extensions/fine_place_same_night_four_panel/RESULT_V1.md`, run **36518735021**.
- `post_freeze_extensions/temporal_persistence_1d_four_panel/RESULT_V1.md`, run **36539006089**.
- `post_freeze_extensions/strategy_maintenance/STRATEGY_MAINTENANCE_SYNTHESIS_V1.md`.
- `post_freeze_extensions/3d_niche_partition/COUSE_VERTICAL_SEPARATION_RESULT_V1.md`, corrected run **36953712597**.
- Original JAE rc2 summary for first-frozen external cases and `post_freeze_extensions/strategy_maintenance/WIND_SUPPORT_PREFLIGHT_RESULT_V1.md`.
