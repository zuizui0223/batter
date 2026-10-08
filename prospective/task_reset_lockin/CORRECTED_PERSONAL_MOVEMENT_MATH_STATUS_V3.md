# Personal movement mathematics: corrected evidence status v3

## Question

Can the individual component of bat 3D flight be recovered as a finite low-dimensional object, or is every animal's movement essentially mathematically unrecoverable?

## Evidence hierarchy

### 1. Repeatable space-use individuality

The earlier outdoor x-y-z analyses show repeated individual spatial organization and terrain-relative individual vertical strategy, but generally do not require 3D territorial segregation.

A pooled collective configuration recurring after complete tracked-member turnover was detected in the 2016 *P. hastatus* panel, including after subtracting terrain elevation. This is **collective spatial persistence**, not evidence of a cognitive colony map.

### 2. Portable flight-policy identity in controlled obstacles

The *Rhinolophus nippon* archive contains 45 trajectories from five identified bats across seven obstacle configurations.

One training-only linear axis is sufficient to identify animals relative to conspecifics in held-out configurations. That is **identification sufficiency**, not evidence that one parameter exhausts movement individuality.

### 3. A second portable component survives beyond speed

After held-out removal of FlightIntensity, geometry-based identity persists. Training-only residual-geometry PCA indicates one additional dimension is sufficient for that held-out identity task.

A transparent pair of coordinates is:

```
I = mean(z_median_speed,z_p90_speed,z_median_abs_vertical_speed,z_p90_abs_vertical_speed)
M = mean(-z_median_speed,z_median_turn,z_p90_turn,z_path_efficiency,z_vertical_range)
```

Earlier tests showed strong cross-environment identification in this fixed two-axis plane. Absence of calibrated residual identity after removing both axes does **not** prove a universal intrinsic dimension of exactly two.

### 4. Correct the false convergence argument

The prior ~91.6% approach to a full-training mean after m=3 environments is not independent evidence of a stable latent theta.

For arbitrary training observations `x_1,...,x_N`, the mean squared error averaged over all size-m subsets equals:

```
(y - mean(x))² + (1/m - 1/N)*sample_variance(x)
```

This guarantees MSE improvement as more training environments are averaged, with no assumption about stable individual parameters.

The earlier finite-scalar-convergence **biological interpretation is downgraded**. The numerical result remains reproducible.

### 5. New genuine held-out validation: calibrated personal identity

The frozen post-outcome null audit tested the actual bat histories against within-environment disruption of complete bat labels.

Workflow 37705394801, success, artifact 11519441963:

| historical coordinate | held-out m=3 gain over environment center | p versus label null | positive bats | strict frozen support |
|---|---:|---:|---:|---|
| I | +0.27669 | .0013 | 3/5 | no |
| M | +0.09369 | .0050 | 3/5 | no |
| normalized equal-axis I+M | **+0.37902** | **.0001** | **4/5** | **yes** |

Joint bat-cluster bootstrap 95% CI: **[+0.0550,+0.6746]**.

The important evidence for portability is therefore the actual-identity forecast advantage over label-disrupted data, **not** the mechanically decreasing subset error.

Under the fixed consistency rule, the joint model passes but neither axis alone passes.

### 6. Individual differences in the carriers

Descriptively, equal-target gains reveal different mixtures:

- A: strong I, negative M
- B: both weak/negative
- C: negative I, strong M
- D: both positive
- E: both modestly positive

These are preliminary phenotype descriptions; no formal inference of discrete individual strategy classes is made.

### 7. Environmental realization is unresolved

A scalar policy estimate does not directly predict exact absolute 3D route lane placement in an unseen bat (previous held-out lane-linkage gain -0.0878, p=.292).

An unregularized low-rank context-specific completion became numerically unstable under missing environment cells and was appropriately stopped.

Thus a compact portable personal descriptor can coexist with complex, context-specific realized trajectories:

[
\mathbf z_{i,e,t}
=
\boldsymbol\mu_{e,t}
+
B_e\mathbf q_i
+
\mathbf h_{i,e,t}
+
\boldsymbol\epsilon_{i,e,t},
\quad \mathbf q_i=(I_i,M_i).
]

This is a **descriptive candidate decomposition**. The context operator `B_e` and route component `h` have not been uniquely identified; they must not be described as known dynamical equations.

### 8. Limits on biological generality and mechanism

- Miniopterus 19-trajectory panel shows no supported linear individual transfer in d=1–8, but matched-support Rhino positive-control detection was only ~40–43%. This is a **power-limited non-detection**, not evidence of infinite-dimensional or absent individual policy.
- The independent 14-animal Yamada learning dataset shows persistent individual speed-state information overall despite common speed shifts, but between-condition persistence/gain contrast remains uncertain (p approximately .08–.10).
- Same-individual morphology correspondence cannot be recovered from public metadata. Biomotor capacity versus learning versus sensorimotor habit remains unresolved.

## Corrected answer

A **finite, jointly predictive two-coordinate behavioural representation** is supported in one controlled horseshoe-bat system. Neither exactly two generative degrees of freedom, a deterministic trajectory equation, nor a general bat-wide law is established.

The genuinely hard biological question is how environmental geometry and learning map this portable individual state onto actual 3D trajectories, not whether an individual must be represented by an infinite numerical expansion.

## High-value decisive future evidence

Within the *same identified animals*, a familiar → unfamiliar → mirrored/reconfigured → recovered task sequence, ideally with reversible biomechanical-load variation, should measure:

1. whether individual I/M coordinates retain their rank under reset;
2. whether route/lane terms change while portable personal coordinates persist;
3. whether learning changes the contextual expression operator;
4. whether a changed biomechanics condition alters I and M independently.

This requires independent intervention data. Further re-mining the same 45 trajectories would not establish causality.

## Manuscript firewall

All of the foregoing remains a post-freeze mechanistic extension. Do not silently rewrite the frozen JAE primary or present the post-outcome tests as independent preregistered replications.
