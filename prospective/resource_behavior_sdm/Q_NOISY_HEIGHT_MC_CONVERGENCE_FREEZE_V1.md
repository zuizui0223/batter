# Frozen post-outcome *method-only* check: importance-sampled GPS height quadrature vs exact grid

2026-11-21. Source-free, prospective after two-world result was opened. This is a **post-result numerical accuracy diagnostic**, not prospective hypothesis confirmation, no wild-bat biological effects, no original Goldshtein records.

## Scientific question and mathematical reference

In q_stratified_noisy_height_bridge_v1.py, the observation density p(XY, noisy AGL) is estimated by q-stratified self-normalized importance integration over independently sampled candidate heights. At finite K this need not reproduce exhaustive reference-grid predictions, even when the known q corrections are algebraically right. A low effective-sample fraction, or missing one of the source-positive candidate height levels from an observed sample, can distort heldout log-scores.

The **benchmark reference** is the exact full 2 XY × 3 Z synthetic grid from noisy_observations. This is a numerical reference for a fixed simple model (no fitting or optimizer) and is **not** a regional ecological SDM.

## Freeze before running this new grid

- World: constructed resource_agl; 6 fictional bats × 2 nights × 4 steps; GPS σ=11m fixed, synthetic seed=20261121. No real source rows.
- Control proposal: same independently simulated candidate q(z|XY) with opposite site tilts ±1.7 and base RNG seed=889 as the previously opened two-world result.
- Per-XY candidate samples K **[12, 24, 96, 384, 1536]**. No choosing K based on outcomes.
- Model evaluated **without refitting**: fields M2 as defined in paired_3d_ssf_resource_benchmark_v1.py, zero centers, unit standard deviations, fixed coefficient vector [0, 0, 0, 0, 0, -0.08, 0.12, 0.45] for step, log-step, cos-turn, arc orientation, structure, height, resource, resource×height.
- All K use the identical noisy GPS observations and independent q candidate generator; only MC point count differs. Compare **corrected q importance** vs **naively uncorrected** candidate weights with exact full-grid M2 predictive p(XY,Y).
- Primary numerical metric: equal-fictional-bat mean absolute discrepancy in heldout **joint observed-data log density** relative to exact-grid reference. Also report signed mean bias, conditional-height discrepancy and minimum q effective sample fraction / sampled-Z coverage.
- Monte Carlo errors are not guaranteed monotonic between successive K. No CI or p-values, no selective subset of K.
- If corrected importance at largest K is not close to exact, keep the status FAIL/STILL_UNSTABLE rather than relabel results.
- No fixed "successful" finite K gate is defined before source-specific spatial support, continuous sampling measure, and sensor calibration are established. These are software diagnostics only.

## Hard inference boundaries

This is NOT the independent *observed-step label* case-control p/q likelihood, not a gamma/Kent continuous 3D-SSF reproduction, not a true biological resource × height coefficient, and not a validated q for any source. A future field application requires authentic original GPS source, known sensor SD and datum, truly independent q, full target support and time-aligned plant resource surveys. The source Mendeley archive remains HTTP401 in GitHub workflow as of last checked. Keep batter PR #102 DRAFT, frozen JAE/BE and main untouched.
