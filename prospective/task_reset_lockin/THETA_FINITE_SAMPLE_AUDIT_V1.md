# Finite-sample audit of the bat theta convergence claim (v1)

Status: **mathematical identity audit, not an additional biological outcome test**.

## Important correction

The earlier `THETA_CONVERGENCE_RESULT_V1.md` and synthesis describe a ~91.6% approach to a full-training theta estimate after observing three independent obstacle environments as "rapid convergence". That number is a mathematical consequence of complete subset averaging, not independent empirical evidence that a true invariant personal parameter exists.

This audit does **not** alter those frozen outputs. It changes their scientific interpretation and explicitly marks this claim as superseded.

### Exact theorem

Fix one target bat/environment with an observed target response y. Let the N other environments' scalar centroids be x_1,...,x_N, with population mean mu and population variance

V = (1/N) sum_j (x_j-mu)^2.

For every training subset S of exactly m distinct environments, estimate

theta_hat(S) = mean(x_j for j in S).

The earlier implementation averages squared held-out errors over **all** combinations of size m:

MSE_m(y) = (1 / choose(N,m)) sum_{S:|S|=m} (y-theta_hat(S))^2.

Finite-population sampling variance gives the exact decomposition

MSE_m(y) = (y-mu)^2 + V*(N-m)/(m*(N-1)).

No assumption of stable theta, Gaussian noise, similar behaviour, or even a sensible outcome y is needed.

For the full-training mean m=N,

MSE_full(y) = (y-mu)^2.

Consequently, whenever V>0,

F(m) = 1 - (MSE_m-MSE_full)/(MSE_1-MSE_full)
     = N*(m-1)/(m*(N-1)).

This fraction depends only on N and m and does **not** depend on the biology or y.

In particular,
- N=3 and m=3: F=1.000000;
- N=4 and m=3: F=8/9=0.888889;
- N=5 and m=3: F=5/6=0.833333.

These are exactly the previously reported bat-level convergence fractions:
- A,C,E: 0.889 (N=4);
- B: 1.000 (N=3);
- D: 0.833 (N=5).

The pooled ~0.916 depends on weighting the structurally predetermined fractions by each target's reducible subset-estimation variance. It is not a separately learned biological property.

### Implication for the bootstrap

For every target with V>0, MSE_1 - MSE_3 is **automatically nonnegative** by the same identity. A bat-cluster bootstrap confidence interval excluding zero thus measures positive dispersion across the available training environments. It does **not** test whether the scalar is stationary or converges to a true invariant bat-specific control parameter.

The decreasing subset-estimate SD is similarly guaranteed by finite-sample averaging.

### Evidence that remains legitimate

The following previous analyses have a different estimand and are not invalidated by this identity:

1. *Rhinolophus nippon* 1-D training-only PCA identifies individuals in held-out configurations under a frozen label-permutation null (K~+0.958, p=0.0006; 5/5 bats positive).
2. Transparent FlightIntensity transfers across configurations (K~+0.497; p=0.0003).
3. Training-environment scalar differences predict held-out pairwise magnitudes (beta~1.031, r~0.555, corresponding label-permutation p values 0.0014 and 0.0162).
4. A strict shared-target predictive decomposition found positive group-level portable-theta gain (+0.173, bat-bootstrap CI [+0.033,+0.415]).

These support a **predictively portable one-dimensional summary of measured flight-intensity variation** across the sampled obstacle configurations, not a uniquely identified dynamical law.

The within-environment standardization of the flight features uses the complete environment's unlabeled data (including target-environment distributional information). Leave-one-environment-out transfer is therefore **transductive / environment-normalized**: not a cold-start deployment prediction with only one new bat trajectory.

The d=1 and d=8 Euclidean identity advantage K values use different geometries. Similar K magnitudes do not prove dimensional equality or that 1-D outperforms 8-D; what is valid is that the frozen d=1 adequacy criterion was satisfied.

### Second personal parameter and trajectory link

Later post-primary diagnostics place a clear ceiling on the proposed two-parameter model:
- Individual-specific predictive variance sigma_i did not improve held-out log score over common residual variance: G=-0.0782, 95% bat-cluster CI [-0.3944,+0.2379], 2/5 positive.
- The magnitude-margin versus correct held-out rank ordering had rho=+0.248 but p=0.0963, unsupported.
- Transferable theta did not predict held-out individual's 3-D route-lane centroid: gain=-0.0878, exact p=0.2917, 2/4 positive.

Therefore, neither a predictively stable second noise parameter nor a common theta-to-lane equation has been established.

### Miniopterus structural limitation

The Miniopterus all-dimension scan found no positive cross-configuration linear identity, but its available 19 trajectories are severely unbalanced:

- four individuals: A,B,C,D;
- each bat occurs in only three environments;
- of seven environments, **five have only one biological individual**;
- only Env2 (three bats) and Env3 (four bats) compare multiple individual identities.

The Mini normalization subtracts within-environment feature means. In a singleton-bat environment, that bat's entire environment-average feature vector is therefore exactly zero by construction. It cannot supply cross-bat mean separation there.

This is a structural weakness for between-individual transfer, **not** evidence that Miniopterus requires higher or infinite-dimensional laws. Without a balanced multi-individual cross-environment panel, absence of transfer cannot be compared directly with Rhinolophus as a species-level mechanism difference.

## Revised scientific statement

> In the available horseshoe-bat system, a one-dimensional movement-intensity summary preserves cross-configuration individual information under the frozen label null. The previous "91.6% parameter convergence" is a finite-subset averaging identity and cannot independently establish parameter identifiability. The source of the persistent individual component remains unidentified, as do any additional stable context-sensitivity or trajectory-generating parameters.

## Next legitimate discriminator

A new, independently sampled set of obstacle configurations (or ordered same-individual task reconfigurations) is needed to test stability, learning and physical meaning without mechanically guaranteed subset-convergence metrics.

Do not relabel the existing post-outcome results as prospective proof.


## Source-native structural gate: direct Rhino/Mini contrast is asymmetric

The original outcome-blind structural adjudication (`STRUCTURAL_SUPPORT_ADJUDICATION_V2.md`) explicitly recorded:

- Rhino: all seven Env1–Env7 had >=2 different bat identities, and five bats occurred in >=3 such environments; `PASS_B_TO_COORDINATE_SUPPORT`.
- Mini: only Env2 (B,C,D) and Env3 (A,B,C,D) had >=2 identities. Five of seven environments were single-bat; the original gate required >=3 usable multi-bat environments per bat; `STOP_B`.

The later Mini 1–8-dimensional and supervised 1–3-dimensional scans were **post-primary exploratory** extensions on the previously stopped data geometry. Their negative outcomes are properly described as *non-detection under an unsuitable sparse comparison design*, not as a calibrated species-level absence of stable individual policy.

This asymmetry matters because per-environment feature centering forces a bat's mean standardized feature vector to **zero** when it is the only individual in that environment. Thus a one-bat environment cannot contribute a cross-individual mean contrast, regardless of latent dimensions.

## Reproducibility and action

A self-contained Python identity checker accompanies this audit:
`verify_theta_finite_sample_identity_v1.py`.

The code enumerates all training subsets on arbitrary synthetic vectors and verifies the finite-population MSE formula independently of the actual bat outcomes, including the exact A–E structural fractions.

Earlier numeric results are preserved. All language promoting the finite-subset recovery fraction to independent confirmation of biological parameter convergence is superseded by this audit.


## A second, independent mathematical issue: parameter non-identifiability

Even if cross-environment scalar prediction is genuinely positive, the decomposition

y_(i,e) = mu_e + theta_i + h_(i,e)

does not uniquely identify theta_i **without extra restrictions on h**.

For any per-bat constant delta_i, the transformation

theta_i' = theta_i + delta_i,
h_(i,e)' = h_(i,e) - delta_i

leaves every observed y_(i,e) unchanged.

This is an exact reparameterization symmetry (a "gauge freedom"), not evidence for infinite-dimensional movement. To give theta_i a unique operational meaning one must specify a constraint such as

mean_e h_(i,e) = 0

on a declared environmental sampling distribution, or fit a model in which h has a prespecified zero-mean random-effects law independent of theta and is estimated across sufficient independent configurations.

The current equal-environment mean is therefore an **operational personal coordinate defined by the sampled environments**, not an identified neural/physical constant.

A separate dynamic model for the full trajectory requires measured state and environment covariates, transition rules and independently held-out trajectory predictions. A one-dimensional discriminative identity axis cannot substitute for these elements.

### Legitimate next claim tiers

- **Established within the source:** identity-associated scalar information transfers across the sampled Rhino obstacle configurations under an explicit label-permutation null.
- **Hypothesis, not proven:** the scalar is a stable control prior theta_i independent of task context.
- **Not established:** a unique one-parameter law generating individual three-dimensional flight trajectories, or a universal species-independent personal policy.
