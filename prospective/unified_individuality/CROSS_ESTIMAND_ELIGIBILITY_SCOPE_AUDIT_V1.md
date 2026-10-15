# Three field tests, three eligible bat sets: no within-individual V/S/I linkage

**Audit date:** 16 October 2026. **Tier:** cross-source eligibility receipt and observational-unit review, based exclusively on already completed original analyses. Not a new bat tracking analysis, reassignment, cross-test covariance estimate or source permutation.

## The problem concealed by the four shared study-panel labels

The unified Figure 6 juxtaposes (A) individual conditional centered-height fidelity V_rel, (B) added segregation S_rel of smoothed centered-height probabilities, and (C) matched x-y-time co-use deviation I. A companion test showed repeatable identity after 500-m place × coarse speed × turning matching. Each is associated with **the same four named source datasets**, but they do not select identical biological individual populations.

| Original study panel | Fine-place+speed+turn bat n | 500-m geometry V/S bat n | Co-use I bat n | I usable dyads | I time / horizontal scope |
|---|---:|---:|---:|---:|---|
| *Hypsignathus monstrosus* | **19** | **8** | **11** | 22 | 60 seconds; endpoint excluded |
| *Phyllostomus hastatus* 2022 | **23** | **5** | **6** | 10 | 60 seconds; endpoint excluded |
| *P. hastatus* 2023 | **11** | **6** | **6** | 8 | 600 seconds; all-space |
| *P. hastatus* 2016 | **9** | **9** | **5** | 8 | 600 seconds; endpoint excluded |

All three source procedures had **distinct structural gates**:
- Fine-place: a held-out individual-prediction method conditioned on joint 500-m XY × broad speed×turning categories, using the original eligible panel n=19/23/11/9.
- V/S: smoothed, session-centered joint-height/conditional-height geometry requiring sufficient repeated same-animal and other-animal session pairs sharing 500-m horizontal support, n=8/5/6/9.
- I: source-cohort matched x-y-time event/dyad selection and phase shifts, using n=11/6/6/5 and different encounter windows/endpoint scopes.

Hence geometry and co-use biological n differ in **3/4** panels; fine and geometry differ in **3/4**; fine and co-use differ in **4/4**. Equal sample size alone, e.g. V/S and I each use six bats in P2023, or fine and V/S each have nine bats in P2016, **does not establish that their individual-identity sets match**.

The original aggregate source result tables do **not** provide a verified cross-family animal-ID intersection, so we cannot infer its cardinality. This is not a finding that source bat groups are actually completely disjoint; they may substantially overlap. The correct status is **not verified**.

## Why this changes the argument

The source result "V_rel positive but co-use I not positive" is **not a within-animal paired comparison** of whether the *same individually predictable bats* lack a co-presence response. The two test outcomes are separate **panel-level aggregate statistics on differently admitted individuals**, with different nulls and power. Even two tests conducted in the same colony-year do not identify a causal path from individual fidelity to that same animal's synchronous residual-height deviation.

Nor does fine-place matching constitute a **nested robustness test on the identical V/S sample**. It is supportive independent *analytical evidence inside a shared original source*, but its sample and data-use definitions are different. Reporting all three sets of counts prevents conflating ecological generality with sample nesting.

The source's original V_rel/S_rel also share a common subset and are algebraically coupled through the epsilon overlap slack; this is distinct from the **between-analysis animal-set mismatch** that applies to I and fine-place. Co-use I is a **session-median-centered height-deviation mismatch**, not a physical bat-to-bat height gap, as established separately in the co-use source-code audit.

## Publication-safe and unsafe language

**Supported:** "Three independent *source-analysis families* on four corresponding bat study panels respectively detected individually predictive centered-height use under their criteria and failed to consistently support positive added segregation in their source-native probability metrics. Those source tests have different eligible animal sets."

**Not supported:** "The very same bats remain strongly specialized even during encounters but do not avoid one another" or "The co-use analysis proves individual strategies are maintained without contemporaneous partitioning." A per-bat relation between V and I has **not** been estimated.

The nominal P2023 co-use excess (+3.57 metres on the centered-deviation scale, original raw p=0.0231) is not significant under either retrospective within-endpoint four-test Holm p=0.0924 or broader twelve-test Holm p=0.2079, but the present eligibility issue persists independently of how p-values are corrected.

## Possible decisive future comparison

A new ethically appropriate study could preregister **one common identified cohort** of bats with synchronized and common-datum calibrated tracks, adequately repeated held-out sessions, verified feeding/commuting state labels, dyad support and independent physiological/food-resource measurements. On that *same predefined bat set*, estimate each individual's centered-height fidelity and its actual physically calibrated inter-bat gap (separately from residual-height deviation), then test a predeclared bat-level linkage with correct animal/dyad dependence. Do not manufacture this result by treating current nonnested original source panels as a paired experiment.

## Exact evidence

- Source-original native 500-m V/S eligibility: original successful workflow 36881187913; source Git blob c1d37e42f72f59e5aba364daec9aef68b47778b6.
- Source-original 500-m place×kinematic stress test: successful workflow 36519747717; source Git blob a2960b45a1a7ea1e0e3beebe6eb799a47f114bed.
- Corrected source-original co-use result after fixed x-y-time/dyad support: successful workflow 36953712597; source report Git blob d7b6054d95e7a6c27baf8e35a2f7377f628fe818.
- Source-frozen uniform Figure 6 input snapshot: Git blob b3f7b20136d028021a3c33a43c256e40ce91f677.
- [Exact 3-family eligibility ledger](figures/FROZEN_CROSS_ESTIMAND_ELIGIBILITY_V1.json) and [offline independent source-blob validator](validate_cross_estimand_eligibility_v1.py). These audit numbers but **do not** access raw individual identities or reconstruct source GPS/DEM tracks.

**Human editorial decision:** Figure 6 should be read as comparison of different source *estimands and eligibility sets*, not within-bat ecological consequences. Original field panels and inferred source statuses are preserved, and this removes a key route for inadvertent mechanistic overclaim.
