# What co-use I actually measures: session-centered relative-height deviation, not physical altitude gaps

**Audit:** 16 October 2026. Source-code/estimand-only reinterpretation of the **original corrected successful workflow** 36953712597, commit 7d5f310b0ec5337b47202ced4378a78edc3daa66. No animal GPS/DEM records re-opened, no endpoint/encounter selection, null permutation or new empirical output generated. The historical frozen code and original source outcomes are unchanged.

## Exact original measurement operation

At each fix in a given source study, the original code first computes a terrain-relative *proxy* height h_rel = native GPS height minus interpolated DEM height. Then, **within each individual tracking session**, it computes median m_session of those h_rel values and stores

\[
z_{\mathrm{rel}}=h_{\mathrm{rel}}-m_{\mathrm{session}}.
\]

For two distinct bats' encounter-matched source fixes a and b, the published source code computes

\[
A_e=|z_{\mathrm{rel},a}-z_{\mathrm{rel},b}|
=\left|(h_{\mathrm{rel},a}-h_{\mathrm{rel},b})
-(m_{\mathrm{session},a}-m_{\mathrm{session},b})\right|.
\]

This is an **absolute difference in two session-specific baseline-centered *deviations***, expressed in metres. It is **not** the same estimand as the actual physical altitude difference |h_rel,a − h_rel,b| at the encounter; when the two session medians differ, the two quantities can diverge arbitrarily.

The source's dyad-level statistic is the median A_e over selected encounters. The original panel statistic averages those dyad medians equally. Its null uses a *fixed* original x-y-time encounter set and within-individual×session×500-m-cell circular shifts of the z_rel values. This can test whether **relative vertical deviations** align/differ differently during admitted matched encounters than under the particular shifted baseline. It cannot directly detect physical vertical avoidance, true relative flight clearance or intentionally partitioned absolute altitude layers.

### Exact synthetic examples (not GPS observations)

Take two source-consistent synthetic sessions with locally harmonized terrain-relative heights (same hypothetical vertical datum and terrain cell):
- Session medians 100 m and 200 m; matched actual terrain-relative heights 100 m and 200 m. **Physical height difference = 100 m**, source-centered deviation A_e = |0−0| = **0 m**.
- The same respective session medians, but matched actual heights 150 m and 150 m. **Physical height difference = 0 m**, source-centered deviation A_e = |50−(−50)| = **100 m**.

Both are algebraically possible if other observations within each session establish the stipulated medians. Even with perfect GPS/datum/terrain calibration, **one cannot derive a physical between-bat height gap from a source A_e value alone**.

## What is (and is not) supported in the original outcome

The original 2023 *Phyllostomus hastatus* source reported a +3.5737 m **excess in session-centered deviation difference relative to its fixed phase-shift null**, with nominal upper-tail source p=0.0231 under a 600-second **all-space** encounter definition. The 95% dyad-bootstrap compatibility interval of that excess was −4.63 to +11.73 m. The within-endpoint four-panel Holm p=0.0924 and illustrative 12-test Holm p=0.2079; neither retrospective adjusted family supports a positive result below .05.

**This does NOT show that real co-occurring bats were physically 3.57 m further apart vertically, nor that they intentionally avoided one another.** The other three original panel intervals and their positive ~1–2 m upper endpoints similarly constrain only *excess centered-deviation differences* under their source definitions, **not an equivalence margin on true physical vertical separation**.

The matched x-y-time samples are not always instantaneous: two panels use 60 seconds and two use 600 seconds; the 2023 sample uses all-space rather than endpoint-excluded events. Thus even the narrower co-presence interpretation is observational and time-window dependent.

## Relation to smoothed native 3D overlap

The source O_XYZ and O_Z_given_XY overlap measurements are **session-median-centered and α=0.5-smoothed estimated probability distributions** (see SMOOTHED_3D_OVERLAP_SUPPORT_AUDIT_V1.md). Session-centering alone makes the vertical coordinate a *within-session deviation*, not a common absolute three-dimensional altitude axis; smoothing can also yield positive joint-bin overlap with no matching raw observed XY×height bin. These facts prohibit interpreting joint overlap as physically shared 3D habitat volume or the co-use I endpoint as direct physical altitude separation.

The original terrain-relative V_rel identity test remains about repeatability of an estimated **within-session-centered conditional vertical-use shape**; its original source-supported gate and retrospective multiplicity sensitivity are unchanged. S_rel pertains to **estimated additional relative-height shape segregation**, not an equivalence test on real altitude exclusion.

## Editorial correction

The integrated manuscript must:
- Say **excess co-use-associated session-centered height-deviation difference**, or the defined source statistic I, rather than unqualified "extra physical vertical separation", "active avoidance" or a precise physical gap in metres.
- Restrict the claim to **identifiable personal vertical-use probability structure without consistently detected added segregation in *the tested centered estimator***, not a positive demonstration that animals actually share the same 3D airspace or that physical vertical exclusion is absent.
- Preserve the original 2023 nominal source result and the unsuccessful within-4/within-12 Holm sensitivities, while making the metric clear in figure captions, SI and reviewer explanation.
- Preserve frozen source code and all original outputs; do not infer real pairwise altitude separation from source summaries or retrospectively fit a different spatial/height estimator here.

## Historical audit trail

The corrected successful co-use runner is the same original Git blob (SHA-1 **1f528f0343ac9e6e26851e4adad5c106e8e5dffc**) at source success commit 7d5f310b0ec5337b47202ced4378a78edc3daa66 and in later frozen JAE rc2. Its original frozen contract has blob **9e5f65772605baaba400e57ea21a9bb91baa819f** and defines the endpoint as absolute pair difference in DEM-terrain-relative, session-median-centered height. Both source-only files are independently snapshotted under source_recovery/co_use_centered_history, without any animal observations or DEM tiles.

Corrected original source: https://github.com/zuizui0223/batter/blob/7d5f310b0ec5337b47202ced4378a78edc3daa66/post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py

Source-frozen numerical p-values are tracked separately in the original JAE source and the unified figure data. [Byte-verifying mathematical-source audit](validate_couse_centering_boundary_v1.py) establishes the equation and two synthetic counterexamples without rerunning any original bat analysis.
