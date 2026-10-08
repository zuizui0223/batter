# Personal flight policy evidence ceiling — 2026-10-08 (v1)

## Scope and evidence status

This is a **post-outcome audit/synthesis**, not a new confirmatory result. It supersedes strong interpretations that theta has been mathematically proven stationary, convergent to a physical constant, or a unique 1-parameter equation of motion. Earlier frozen outcomes are retained unaltered.

Target question: can individual bat movement be summarized by a finite-dimensional portable state, and what does the archive actually identify?

## A. Supported predictive facts in the Rhinolophus obstacle dataset

Authoritative data: 45 *Rhinolophus nippon* trajectories, 5 bats A–E, 7 obstacle configurations, eight measured movement summaries. All leave-one-environment analyses inherit environment-wise standardization using the entire unlabeled target-environment feature distribution. These are **transductive, conditional within-archive predictions**, not truly unobserved-environment cold-start forecasts.

1. Training-only PCA dimension 1 carries cross-configuration identity: K≈+0.95785, 5/5 positive, label-permutation p=.0006.
2. A transparent relative flight-intensity scalar carries identity: K≈+.49656, 5/5 positive, p=.0003.
3. Pairwise scalar ordering/magnitude carries to held-out configurations: equal-pair accuracy≈.8217; through-origin beta≈1.0314, r≈.5548; p_beta=.0014, p_r=.0162.
4. A **non-tautological correspondence test** evaluates the true held-out self-history mean versus zero-personal-history baseline on the same 25 bat×environment centroid targets:
    - MSE baseline .633974 → personal .340902, G=+.293072, R²=.462277;
    - environment-preserving label permutations B=19,999: p=.00175;
    - individual gains A +1.1025, B −.1868, C −.2197, D +.6152, E +.1542;
    - only 3/5 individual gains positive;
    - 95% bat-cluster bootstrap CI for population gain [−.1318,+.7472] spans zero.

Thus the inference is **portable identity-associated information in this sampled system**, accompanied by pronounced bat-specific differences in predictive reliability.

## B. Mathematical correction: subset-MSE “91.6% convergence” is not biological evidence

The earlier m=1→2→3 exhaustive-subset comparison obeys, exactly,

[
mathrm{MSE}_m(y)=
(y-ar x)^2+rac{N-m}{Nm}s^2,
]

where s² is the sample variance across the N training-environment centroids. Therefore its error monotonically declines with m regardless of whether true bat identity transfers. The relative progress-to-full fraction equals

[
F(m)=1-rac{N-m}{m(N-1)}
]

and depends solely on N and m. The published aggregate 91.6% is a finite-combination averaging artifact, not a biological convergence rate.

An independent source-backed correspondence test (section A.4) is the legitimate signal, **not** the exhaustive-subset algebra.

Additionally, in the decomposition

[
y_{ie}=	heta_i+h_{ie},
]

the transformation

[
	heta'_i=	heta_i+delta_i,quad
h'_{ie}=h_{ie}-delta_i
]

is observationally indistinguishable. Theta is not a unique neural/physical constant absent an explicit zero-mean constraint or an independently identified generative model.

## C. One axis sufficient for identification is not exhaustive

Scale-free geometry still contains cross-configuration personal information after linear removal of FlightIntensity:
- cross-fitted residual geometry identity K=+.45399, 5/5 positive, p=.0088 (separate post-primary diagnostic);
- one training-only residual geometry PC sufficient for held-out identity: K=+.56879, 5/5, p=.0106.

A transparent 2-coordinate intensity/maneuvering representation carries identity:
- K≈+.55428, 5/5 positive, p=.0001.
- Removing that 2D span leaves no identity exceeding the frozen support rule in the residual 8D policy (K≈+.08771, p=.0863) or separate geometry family (K≈−.01467, p=.4509).

**Do not infer an exact intrinsic dimension of 2.** These are linear residual tests on finite preselected summaries. Failure of residual detection is not evidence of mathematical equivalence to zero.

The physiological meaning and correspondence of the geometry-PCA residual coordinate and the transparent ManeuveringExtent scalar are not identical, even if both aim to represent additional maneuver structure.

## D. Missing test: does a second coordinate improve the same future outcome?

Identity advantage K is computed in different geometries when the dimension changes. Similar or larger K across dimensions is **not** a nested numerical forecast comparison.

The separate `post-freeze/rhino-rank-two-forward-test-v1` freezes an actual conditional same-endpoint comparison:

[
Delta_{2mid 1}=L_{rank1}-L_{rank2}
]

using squared error for the same held-out original 8-feature vector, training-only SVD, fixed 45 targets, bat-cluster uncertainty, and an environment-wise cluster-label permutation null.

**This document contains no guessed outcome for that analysis.**

## E. Environment and learning context

A specific post-primary peer-calibrated common multiplicative environment adjustment fails:
- equal-bat MSE individual-theta-only .27745;
- peer-derived multiplier .32295;
- gain M0−M1 = −.04550, bat-cluster 95% CI [−.0771,−.0171], 5/5 bats negative.

This rejects predictive usefulness of **that estimator**. It does not prove alpha=1 or disprove all shared environmental reactions.

Independent Yamada naive→familiar scalar evidence:
- total personal-speed persistence K≈+.5277, p=.0052, 12/14 bats positive;
- reflective condition alpha≈+.800, supported within group;
- permeable condition alpha≈+.002, unsupported within group;
- cross-condition delta-alpha≈+.798, p≈.0997 (not significant by 0.05).

The 14 Yamada bats are not linked to the five Teshima bats. The two scalars are not numerically the same identified theta.

## F. Miniopterus is not evidence of mathematical non-convergence

The Mini all-dimension identity sweep failed under its frozen estimator. But four bats in 19 trajectories occupy only 12 bat×environment cells, and **five of seven environments contain only one bat**. Within-environment centering forces each such singleton bat’s environment-level centroid exactly to zero. This confounds portability inference.

Therefore non-detection cannot establish *Miniopterus* has no stable, finite, or low-dimensional individual state.

## G. Ecological and mathematical conclusion

The narrowest defensible synthesis is:

> Measured individual movement summaries can contain portable low-dimensional identity-associated information, but the current sparse source does not identify a unique finite-dimensional trajectory-generating law, a stationary biological theta, or its developmental/physiological mechanism.

A reasonable **hypothesis**, not an estimated unique law, is

[
mathbf y_{i,e,t}
=oldsymbolmu_{e,t}+mathbf A_{e,t}mathbf z_i(t)
+mathbf h_{i,e,t}+oldsymbolepsilon_{i,e,t}.
]

The key missing evidence is a same-endpoint incremental forward prediction test of additional dimensions, followed by new balanced, temporally ordered same-individual × environment experiments with measured biomechanical/environment inputs.

The “pi/nonconvergent” hypothesis cannot be established merely by a failure to identify a simple equation. Conversely, low-dimensional discrimination does not prove that all 3D flight trajectories follow a low-dimensional dynamical law.

## Evidence links

- [Convergence algebra and correspondence audit](https://github.com/zuizui0223/batter/blob/post-freeze/theta-correspondence-audit-v1/prospective/task_reset_lockin/THETA_CORRESPONDENCE_AUDIT_AUTHORITATIVE_RESULT_V1.md)
- [Peer environment gain](https://github.com/zuizui0223/batter/blob/post-freeze/theta-peer-environment-gain-v1/prospective/task_reset_lockin/THETA_PEER_ENVIRONMENT_GAIN_AUTHORITATIVE_RESULT_V1.md)
- [Mini identifiability audit](https://github.com/zuizui0223/batter/blob/post-freeze/mini-latent-dimensionality-scan-v1/prospective/task_reset_lockin/MINI_DIMENSIONALITY_IDENTIFIABILITY_AUDIT_V1.md)
- [Joint axis transfer audit](https://github.com/zuizui0223/batter/blob/post-freeze/personal-policy-transfer-null-audit-v1/prospective/task_reset_lockin/PERSONAL_POLICY_TRANSFER_NULL_RESULT_V1.md)
- [New nested quantitative forecast contract](https://github.com/zuizui0223/batter/blob/post-freeze/rhino-rank-two-forward-test-v1/prospective/task_reset_lockin/RHINO_RANK_TWO_FORWARD_TEST_CONTRACT_V1.md)
