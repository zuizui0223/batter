# Bilateral ear-tip distance does not identify head-relative sonar gaze (geometry certificate v1)

## Scope, provenance
**MATHEMATICAL IDENTIFIABILITY AUDIT ONLY. NO OPENING OF BAT EAR VALUES.** This follows the completed author's Zenodo 20927789 source gate. The original PNAS 2026 paper genuinely reconstructs ear orientation from high-speed stereo photogrammetry and supplemental acoustic beam models; our certificate is NOT a challenge to that original result. It applies specifically to the **public compact CSV fields**, which expose \`earTipSep\` and \`eyeDist\` but do not export the source ear direction vectors, receiver beam, head yaw/pitch or full per-frame XYZ used in the original analyses.

## Counterexample for fixed ear lengths and fixed head bases

Let the fixed head's left and right ear-base coordinates be
\[
B_L=(-b,0,0),\quad B_R=(b,0,0),\quad b>0.
\]
Represent ear tip positions as \(P_L=B_L+\ell u_L\) and \(P_R=B_R+\ell u_R\), where \(\ell>0\) is constant ear length and \(u_L,u_R\) are *unit* direction vectors. The public scalar ear-tip separation is
\[
d=\lVert P_R-P_L\rVert=\lVert (2b,0,0)+\ell(u_R-u_L)\rVert.
\]

Let \(R_x(\theta)\) be any 3-D rotation around the left-to-right ear-base axis \(x\). Apply the **same rotation** to BOTH ear direction vectors, while keeping head, ear base positions and lengths unchanged:
\[
u_L^\prime=R_x(\theta)u_L,\qquad u_R^\prime=R_x(\theta)u_R.
\]
Because \(R_x(\theta)\) preserves Euclidean lengths and the baseline vector \((2b,0,0)\),
\[
d^\prime=\lVert(2b,0,0)+\ell R_x(\theta)(u_R-u_L)\rVert=d
\quad \forall \theta.
\]

Yet the directions of both ears relative to a fixed target in the head's forward/up axes generally **change continuously** as \(\theta\) changes. Thus even with constant head size, perfectly calibrated tip locations and rigid ear lengths, an entire continuum of different bilateral sonar-gaze geometries yields EXACTLY THE SAME measured ear-tip distance.

A particularly simple subcase: \(u_L=u_R\). Then \(\|P_R-P_L\|=2b\) for ALL shared left/right ear orientations, including forward-, upward- and backward-facing. The physical frontal gain and gaze to a prey target can differ even though the scalar ear-tip separation is identical.

If \`eyeDist\` is a constant within-bat head-size normalization \(e>0\), then \(d/e\) is also invariant under these rotations; ratio standardization does NOT restore directional information.

## Strict conclusion
\[
\text{earTipSep (or earTipSep/eyeDist)}\not\Rightarrow
\text{3-D left/right ear aim, beam direction or flight-heading alignment}.
\]

This is **structural non-identifiability**, not sample-size underpower, measurement error or a biological finding that bats do not display such coordination.

Even the 5 labeled IDs /39 recording files in the source's \`mdau_basement\` per-frame export cannot resolve the absent ear/head vectors by reweighting, nonlinear fitting or stronger priors without substituting an assumed directional model. In addition, the original source figure configuration selects only 4 \`mdau\` IDs; its fifth compiled key is not documented as another eligible physical bat, and no independently defined second sensorimotor perturbation context is available in the two small CSVs.

## Viable scientific alternatives (not permission to rescope the original gate)
- The same public CSV *could* support **exploratory** predictions about ear-tip spacing versus prey distance, provided original-bat IDs and blocked independent recordings are rigorously verified; however, target-dependent ear-tip spacing is already directly studied in the 2026 PNAS paper. Changing the endpoint after the source gate is **not independent confirmatory individuality evidence**.
- An **independent new cohort or author-provided raw per-frame 3-D keypoints** could allow a new, precommitted head-relative pinna-axis identity test if ≥5 physically verified bats per species and ≥2 comparable conditions remain present.
- Data about social acoustic interference would still be absent: this was a target-focused individual flight experiment, not multi-bat jamming.

## Reproducibility
A dependency-free geometric invariant checker \`ear_tip_geometry_identifiability_v1.py\` evaluates fixed b, ell, nonparallel ear direction examples, rotations about the baseline, target-gaze changes, and normalized separation invariance. It verifies the theorem in a small deterministic numerical family but the conclusion follows **exactly algebraically** for all allowable angle rotations. No external or bat raw source values are loaded.

Stop: do not read physiological \`earTipSep\` columns or promote the source to a numerical across-bout personal pinna-gaze test under the original frozen contract.
