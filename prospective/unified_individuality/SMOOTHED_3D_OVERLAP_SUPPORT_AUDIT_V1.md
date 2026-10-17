# Smoothed 500-m 3D overlap is not observed physical airspace sharing

**Review date:** 16 October 2026. **Tier:** source-code audit and synthetic-only mathematical examples. No original GPS events, DEM, outcomes or permutations were opened or recomputed.

## Original estimator and its per-cell support

The original 500-m source has ten session-median-centered height bins. For every horizontally occupied cell c, the historical runner adds a pseudocount α=0.5 to **each of the ten altitude bins**:

\[
\widehat p_s(z\mid c)=\frac{n_s(c,z)+0.5}{n_s(c)+10(0.5)},\qquad
\widehat p_s(c,z)=p_s(c)\widehat p_s(z\mid c).
\]

Original joint overlap between two eligible **tracking sessions** is the intersection of these estimated smoothed probabilities over shared horizontal cells:

\[
\widehat O_{XYZ}(a,b)=\sum_{c\in C_a\cap C_b}\sum_z
\min\{\widehat p_a(c,z),\widehat p_b(c,z)\}.
\]

The companion O_Z_given_XY statistic takes the overlap of smoothed within-cell conditional-height probabilities weighted over shared horizontal cells; R_3D=1−O_XYZ/O_XY measures normalized joint-overlap loss, and S_native/terrain S_rel compare other-minus-self R_3D under their source study contracts.

**Critical source gate:** a pair qualifies with a minimum of **50 fixes per session summed across all pairwise-shared horizontal cells**, not a minimum of 50 fixes in **every** shared cell. The value α=0.5 therefore can matter considerably where session tracks spread their shared fixes across sparse cells.

## An exact synthetic counterexample that passes the source pair gate

The examples below contain **no bat observations**. Both sessions have 50 fixes on mutually shared horizontal support, and their median-relative height vectors can be centered at zero. Their recorded height-bin categories **do not overlap at any same horizontal cell**.

| Invented observation layout | Common horizontal cells | Observations per shared cell (each session) | Raw unsmoothed joint-bin overlap | Estimated smoothed O_XYZ at α=0.5 |
|---|---:|---:|---:|---:|
| Spread evenly across 50 cells | 50 | 1 | 0 | **0.833333** |
| Concentrated in one cell | 1 | 50 | 0 | **0.090909** |

For the first case, session A has 25 fixes at about −75 m and 25 at +75 m; session B has 25 at −150 m and 25 at +150 m, in the **same horizontal cells** but different altitude bins. Every cell has one fix from each session. At α=0.5 the smoothed conditional-bin overlap in each cell is exactly 5/6, despite zero raw intersection. Because both p_XY distributions coincide, O_XY=1 and O_XYZ=O_Z_given_XY=5/6.

For the second case, the **same 50 observations per session** are concentrated in one common horizontal cell with the same disjoint relative-height bin categories. The original sample gate still passes, O_XY=1, but the estimated smoothed O_XYZ=O_Z_given_XY=1/11. The different estimates arise solely from horizontal support concentration plus pseudocount regularization. Without pseudocounts both examples' direct observed joint-bin intersection would be zero.

These arithmetic examples demonstrate an identifiability/measurement limitation, **not** an estimate of the empirical smoothing contribution or a suggestion that the field p-values are invalid.

## Consequences for ecological interpretation

- The reported historical original source between-individual O_XYZ values 0.181–0.309 are **overlaps of smoothed session-level estimated joint probability distributions**. They are **not** measured percentages of 3D airspace co-occupied by animals or proof that particular altitude bins were used by both. For any original pair with positive common XY support, smoothing places positive estimated probability in *all* height bins and produces positive modeled joint overlap even if observed shared XY×height bin counts are disjoint.
- Original whole-session identity-label permutations re-used the same estimator, including its α and source support rules. This mathematical example **does not invalidate** their resulting source-calibrated personal fidelity tests. But the absolute size of overlap or added separation can depend on α and per-cell fixes; their empirical sensitivity to α cannot be measured from the existing four-panel summary alone.
- The original co-use I statistic has a different, contemporaneous/phase-shift estimand and cannot be inferred from smoothed O_XYZ. The 0.80–0.92 values of Figure S1 also refer to separate 1D centered self-predictor profiles and cannot be substituted.
- No positive terrain-relative S_rel result was supported under the source null. That non-support is **not equivalence to no partitioning**, particularly when absolute joint distribution overlap does not encode observed physical co-use.
- The originally eligible four panels are from **two taxa**, and neither latent feeding-task assignment nor actual food/resource partitioning is measured.

## No retrospective estimator refit

The paper should **name smoothing and aggregate 50-fix support explicitly** and treat the estimates as algorithm-conditional; it should **not** silently replace α, retrospectively scan grid sizes, or turn this synthetic counterexample into a new biological hypothesis test. A future preregistered estimator-sensitivity study would require the original licensed GPS/DEM input files and suitable replicated individuals.

## Exact source evidence

The original 3D contract (Git blob 5c76d0432e53ea7733216245f229d68ae0df1f77) pins α=0.5, ten bins and the aggregate shared-fix 50 gate. Original native runner (blob c08b442f97940eac3e90c1dac6e2de6d26010a7a) constructs smoothed per-cell p_z, joint p_XY×p_z and eligible paired O_XY/O_XYZ/O_Z_given_XY/R_3D. Original terrain runner helper (blob c869a25c062b4bf5dc6b22e9f3e7fe03b69aeb30) uses the same bin smoothing. Those exact bytes are available under the integration's native_3d_history source-recovery directory and verified by the [synthetic-only source-hash validator](validate_smoothing_support_boundary_v1.py).

Original 3D source commit: https://github.com/zuizui0223/batter/tree/819acc829d615485b57033f1ddcbebf64b4b49a0

**Publication-safe wording:** "Joint XY–height and conditional height overlaps are computed on session-level, Jeffreys-smoothed probability distributions under pairwise shared-cell support; these do not estimate the fraction of directly observed, physically shared 3D airspace."
