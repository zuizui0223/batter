# Low-dimensional policy maintenance synthesis v2

## Central biological problem

JAE v0.4.0 establishes that persistent individual 3-D movement strategies need not be maintained by persistent spatial partitioning.

The follow-on mechanism question is:

> **What can carry an individual strategy when competitors do not have to keep one another spatially separated?**

The current evidence supports a sharper answer than simple route fidelity.

## Current best model

A useful generative form is:

`movement = environment-specific response + individual policy + short-term noise`.

For *Rhinolophus nippon*, the portable individual component is approximately low-dimensional.

A transparent representation is:

### Axis I — FlightIntensity

`I = mean(z_median_speed, z_p90_speed, z_median_abs_vertical_speed, z_p90_abs_vertical_speed)`

This captures how intensely an individual moves through 3-D space, rather than whether it is relatively more vertical versus horizontal.

### Axis M — ManeuverStructure

A transparent approximation is:

`M = mean(-z_median_speed, z_median_turn_rate, z_p90_turn_rate, z_path_efficiency, z_vertical_range)`

This captures a second maneuver / route-organization dimension.

The fitted PC2 is highly stable across held-out environments and nearly orthogonal to FlightIntensity.

## Why this is not a fixed-route model

Literal route identity is sensitive to absolute spatial position and largely collapses under translation/shape controls.

In contrast:
- movement-policy identity transfers across different obstacle configurations;
- geometry-only identity survives after removing time, speed and absolute scale;
- the principal policy axes remain stable when an entire environment is held out.

Thus the persistent object is better described as a **policy** or **control tendency**, not a literal memorized trajectory.

## Why one scalar is important but not the whole story

For *R. nippon*:

- one-dimensional PCA identity:
  `K = 0.95785`, 5/5 positive, `p = 0.0006`;
- training-only identity axis:
  `K = 0.88483`, 5/5 positive, `p = 0.0021`;
- transparent FlightIntensity:
  `K = 0.49656`, 5/5 positive, `p = 0.0003`.

The PC1 direction is nearly invariant across leave-one-environment-out folds:
- pairwise cosine minimum: `0.9833`;
- median: `0.9964`.

PC1 aligns strongly with FlightIntensity:
- foldwise cosine minimum about `0.930`;
- median about `0.943`.

The one-parameter law is genuinely predictive:
- held-out pairwise calibration slope: `1.031`;
- Pearson `r = 0.555`;
- sign accuracy: `82.9%`;
- no-refit held-out pair-difference `R² = 0.627`, `p = 0.0005`.

Errors concentrate among individuals close in the scalar:
- correct comparisons mean |Delta theta|: `0.934`;
- errors: `0.557`;
- margin contrast `p = 0.0249`;
- probability of correct ordering increases with |Delta theta| (`p = 0.0467`).

So a useful first approximation is:

`I_ie = theta_i + epsilon_ie`.

## But individuality is not truly one-dimensional

PC1 removal leaves portable identity:
- residual `K = 0.38896`;
- 5/5 positive;
- `p ≈ 0.0032`.

Removing PC1+PC2 eliminates calibrated residual identity:
- `K = 0.0570`;
- `p = 0.1553`.

Therefore:

> one dimension is sufficient to identify individuals, but approximately two linear dimensions are needed to exhaust the calibrated portable signal.

Rank-one held-out reconstruction of the full 8-D policy centroid:
- `R² = 0.222`, `p = 0.0016`.

Rank two:
- `R² = 0.328`, `p = 0.0002`.

Thus the low-dimensional policy is real but does not explain all trial-level movement variation.

## PC2

Across leave-one-environment-out folds, oriented PC2 is itself highly stable:
- pairwise cosine minimum about `0.971`;
- median about `0.992`.

Median signed loadings show:
- strong positive median turn-rate loading;
- positive p90 turn-rate;
- positive path efficiency;
- positive vertical range;
- comparatively weak speed loading.

Its absolute cosine with FlightIntensity is small:
- median about `0.112`.

This supports a distinct maneuver / route-organization axis.

## Independent external validation

A frozen external application to *Carollia perspicillata* used:
- a different species;
- a different laboratory;
- a different 3-D tracking pipeline;
- public data not used to derive the axes;
- no Carollia-specific axis fitting.

The fixed 2-D representation passed:
- `K = 0.34758`;
- 6/7 bats positive;
- both date blocks positive;
- `p = 0.0007`.

Robustness:
- 22/22 admissible single-trial deletions retained support;
- deleting an obvious source-track anomaly retained support (`K = 0.32454, p = 0.005`);
- condition-stratified turn-class permutation retained support (`p = 0.0017`);
- removing all <=90-degree trials retained support (`p = 0.0094`).

The external component result is asymmetric:
- fixed I alone: `K = 0.36775, p = 0.0014`;
- fixed M alone: `K = 0.08933, p = 0.0392`;
- incremental M beyond I: unsupported (`p = 0.6278`).

Therefore the strongest generality claim is about **FlightIntensity**, not a universal two-axis architecture.

## Negative boundaries

### Miniopterus fuliginosus

No calibrated portable identity was detected:
- full 8-D failed;
- Rhino-fixed PC1 failed;
- transparent FlightIntensity failed;
- Miniopterus-specific PCA1 failed.

Therefore low-dimensional individuality is not a universal property of every dataset/species.

### Pipistrellus kuhlii

Independent public 3-D validation stopped before outcome because the frozen numeric support threshold was not met.

### evsBat

External trajectory data were incompatible with the frozen 3-D representation.

### Same-individual morphology

No reproducible crosswalk linked obstacle-flight A–E individuals to public morphology/performance IDs.

Morphological attribution therefore stopped.

### Pulse/sensing

Raw pulse identity looked portable, but the stricter cross-fitted movement/route-conditioned analysis failed:
- residual pulse statistic about `0.118`;
- 3/5 positive;
- `p = 0.2032`.

Do not claim an independent sensing-policy carrier.

## Formation evidence

The first-flight juvenile programme did not support a common slow monotonic increase in individuality.

Instead:
- self-history information was already detectable very early;
- later personal history strongly predicted later movement.

A randomized enriched versus impoverished developmental treatment did not measurably alter history-carrier strength in the available external experiment.

The current formation hypothesis is therefore:

> **rapid symmetry breaking followed by reuse of a stable low-dimensional policy**, rather than slow divergence maintained by ongoing spatial exclusion.

This remains a hypothesis because the exact emergence of the I/M coordinates has not been observed prospectively within the same individuals.

## Mechanistic interpretation

The most defensible current architecture is:

`x_iet = mu_e + Lambda_s theta_i + epsilon_iet`

where:
- `x_iet` is the measured movement-policy vector of individual i in environment e on trial t;
- `mu_e` is the environment-specific response;
- `theta_i` is a low-dimensional persistent individual coordinate;
- `Lambda_s` may be species/task dependent;
- `epsilon_iet` is trial-level variation.

For *R. nippon*, `dim(theta)` is approximately 2 under the present linear measurements.

Across *R. nippon* and *C. perspicillata*, the strongest recurring component is an intensity-like coordinate.

This is not a mathematical constant analogous to pi.

It is closer to a **low-dimensional latent control parameter embedded in a stochastic, environment-dependent dynamical system**.

## Relation back to specialization maintenance

This gives a concrete way for specialization to persist without spatial segregation:

1. multiple behavioral solutions are feasible;
2. an individual acquires or expresses a persistent low-dimensional control setting;
3. environmental changes alter the realized trajectory;
4. the individual control setting remains informative across tasks;
5. repeated behavior is therefore individually structured even when individuals use overlapping physical space.

In shorthand:

> **specialization can reside in how an animal moves, not in exclusive ownership of where it moves.**

## Critical unresolved bridge to JAE

The obstacle-flight programme demonstrates a plausible carrier of individual movement identity.

It does **not yet prove** that the same I/M coordinates cause the wild vertical-distribution individuality in JAE v0.4.0.

That bridge remains a separate test.

JAE already shows that broad place and movement-state matching does not erase individual vertical identity, so a simple speed-only explanation is unlikely to be sufficient.

The next decisive field-side question is whether a low-dimensional personal policy estimated from one set of wild bouts predicts held-out vertical-distribution organization beyond place and coarse movement state.

## JAE firewall

None of these post-freeze analyses modify JAE v0.4.0.
