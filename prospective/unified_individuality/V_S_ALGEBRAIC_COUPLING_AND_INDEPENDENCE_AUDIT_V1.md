# Exact source-algebra audit: conditional vertical individuality V versus added 3D segregation S

**Date:** 16 October 2026. **Tier:** deterministic source-summary algebra plus one synthetic-only original-estimator example. This document does **not** reopen original GPS/DEM, re-fit any wild data, add a source null, or demonstrate absent biological niche partitioning.

## Critical scientific distinction

The original 500-m native joint-grid analysis reported *V* (self-minus-other conditional vertical probability overlap) and *S* (other-minus-self normalized loss of joint XY×height probability overlap). They ask non-equivalent ecological questions and have separately archived source nulls, but **they are not algebraically independent or two separate field replications**. A specific nonnegative overlap-weighting term links them *exactly* for each eligible source session pair.

A review that reports "V is significant but S is not" without the algebra could incorrectly interpret this as independent evidence for a special behavioral mechanism, rather than an outcome that can arise from the different way the two estimators weight horizontal-cell use.

## The mathematical identity

For paired original session distributions a and b, let c index jointly occupied 500-m horizontal cells and z index the **ten smoothed, session-centered vertical bins**. Let x_c=P_a(c), y_c=P_b(c), u_cz=P_a(z|c), and v_cz=P_b(z|c). The original source code defines

\[
O_{XY}=\sum_c\min(x_c,y_c),
\qquad
O_{Z|XY}=\sum_c\frac{\min(x_c,y_c)}{O_{XY}}\sum_z\min(u_{cz},v_{cz}),
\]

\[
O_{XYZ}=\sum_{c,z}\min(x_cu_{cz},y_cv_{cz}),
\qquad
R_{3D}=1-\frac{O_{XYZ}}{O_{XY}},
\]

for eligible pairs with O_XY>0.

For nonnegative x,y,u,v, \(\min(xu,yv)\ge\min(x,y)\min(u,v)\) because both products exceed the product of their respective minima. Summing gives the **nonnegative geometric overlap slack**

\[
\epsilon_{ab}
=\frac{O_{XYZ}}{O_{XY}}-O_{Z|XY}\ge0,
\qquad
R_{3D}=1-O_{Z|XY}-\epsilon_{ab}.
\]

The slack is zero when the two sessions place **identical probability mass in every pairwise shared horizontal cell**, though other special equalities are possible. A positive slack arises from how **unequal XY cell masses interact with conditional height distributions**, not from a separately measured species-level or causal resource mechanism.

The native source uses the same per-session, per-other-individual and equal-biological-individual aggregation weights for all these pair metrics. Thus at the panel level, with self and other subscripts,

\[
V=\overline{O}_{Z|XY,\mathrm{self}}-\overline{O}_{Z|XY,\mathrm{other}},
\]

\[
S=\overline R_{3D,\mathrm{other}}-\overline R_{3D,\mathrm{self}}
=V-\left(\overline{\epsilon}_{\mathrm{other}}-\overline{\epsilon}_{\mathrm{self}}\right).
\]

**The exact source algebra is S = V − overlap-slack gap**. The original two metrics may differ in sign and statistical support even when computed from the **same eligible biological comparisons**.

## Four source panels, directly reconstructed from original unchanged values

| Original native 500-m source | Eligible bat n | V_native | S_native | Mean ε_self | Mean ε_other | Gap ε_other − ε_self = V−S | Terrain V_rel−S_rel |
|---|---:|---:|---:|---:|---:|---:|---:|
| *H. monstrosus* | 8 | +0.17070 | +0.10295 | 0.11730 | 0.18505 | **+0.06775** | +0.05767 |
| *P. hastatus* 2022 | 5 | +0.06596 | −0.01660 | 0.09317 | 0.17573 | **+0.08255** | +0.10852 |
| *P. hastatus* 2023 | 6 | +0.05417 | −0.00392 | 0.09947 | 0.15755 | **+0.05809** | +0.06062 |
| *P. hastatus* 2016 | 9 | +0.14523 | +0.13040 | 0.11203 | 0.12686 | **+0.01483** | +0.04975 |

All native source numbers are copied from the exact same original per-session and equal-animal weighted means; **the identity holds to floating-point precision for all four**. In every panel, the original **other-individual** group has greater mean epsilon than the original **same-individual** group, so native S is smaller than V. No hypothesis test of these epsilon differences was performed.

The original terrain summary preserves V_rel and S_rel, allowing the last column's arithmetic contrast but **not separate terrain mean epsilon_self / epsilon_other components**; those must not be fabricated from the summary. Both native and terrain quantities refer to α=0.5-smoothed session-centered height bins, different from observed physical flight space.

## Concrete synthetic logical counterexample using the original source estimator

Invent **two bats**, each represented by repeated identical sessions (this illustration does **not** meet the real panel-level ≥5 animal gate). Both use two common XY cells and 100 total event fixes per session, so the *pairwise* ≥50-common-fix support criterion holds. There are ten height bins, each assigned α=0.5 pseudocount within an occupied horizontal cell.

Use **session-median-consistent relative heights of −1 m (bin 4) and +1 m (bin 5)**. A has [40,50] events in those two height bins in XY cell 0 and [10,0] in cell 1; B has [10,0] in cell 0 and [40,50] in cell 1 (all other height bins zero). Thus **both sessions have 50 events at −1 m and 50 at +1 m, giving an actual median of zero**, so this construction is compatible with the source's per-session median-centering step. A allocates **0.9/0.1** horizontal mass, B **0.1/0.9**, and both occupy the same two cells with different conditional relative-height profiles.

For two repeated copies of the **same bat**: O_Z|XY=1 and R_3D=0. For an A–B pair: O_XY=0.2; smoothed O_XYZ=0.2; O_Z|XY=0.5017543860; epsilon=0.4982456140; R_3D=0. If source-like panel averages contained these pairs, **V≈+0.498** but **S≈0**, despite clearly nonexchangeable conditional relative-height estimates. This difference follows mathematically from the original estimators' weighting and the invented XY proportions. It does **not** show any ecological effect in real bats and is **not** an empirically observed false positive.

The exact source code, source summaries and toy are hash-checked in [the independent validator](validate_original_v_s_overlap_coupling_v1.py). A separate [smoothing audit](SMOOTHED_3D_OVERLAP_SUPPORT_AUDIT_V1.md) demonstrates why O_XYZ must not be called directly observed shared physical 3D space.

## Consequences for the unified manuscript

1. **Retain** source-valid conclusion that conditional relative-height individuality was detected within original eligible tracking panels, and source-positive terrain-relative S_rel was not consistently supported. The originally archived test statistics and source nulls are unchanged; original four-panel vs broader twelve-test Holm sensitivity remains clearly post-outcome.
2. **Retract any assertion of statistical independence/orthogonality:** V and S are **different, explicitly coupled estimator functionals** of the same sessions; their difference has a deterministic mathematical source. Separate p-values cannot be treated as two independent confirmation events.
3. **Do not attribute epsilon to actual behavioral avoidance, resource sharing, learning or terrain:** the slack is generated by the interaction of horizontal probability weights and conditional smoothed vertical distributions. Its nonzero source group contrast was not independently tested.
4. **Avoid a proved "need not" ecological law:** the findings constrain one original centered model, not absolute altitude exclusivity, competition, diet, physically measured co-use or mechanisms maintaining behavior.
5. **Retain the failed lab-to-wild carrier test.** Controlled identity under perturbation and wild individual relative-height prediction are logically comparable questions, not observed causal stages along one shared bat mechanism.

## Code and provenance

Original native 3D result: successful workflow 36881187913, [source summary](figures/ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json), Git blob c1d37e42f72f59e5aba364daec9aef68b47778b6. Original native runner's Git blob c08b442f97940eac3e90c1dac6e2de6d26010a7a; source terrain helper c869a25c062b4bf5dc6b22e9f3e7fe03b69aeb30. Terrain source summary Git blob 08631a0dce61cc47e12b2d32642c46b5759fe872. All from exact original historical source, without new animal observations. [Machine-readable exact panel table](figures/NATIVE_3D_V_S_OVERLAP_SLACK_DECOMPOSITION_V1.json).

**Editorial verdict:** the strongest field story is *source-calibrated individual-specific conditional relative-height prediction and careful separation of that result from estimated added 3D segregation*, **not** two independent ecological discoveries or a demonstrated absence of physical spatial partitioning.
