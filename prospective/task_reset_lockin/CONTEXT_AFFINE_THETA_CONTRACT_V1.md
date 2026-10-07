# Rhino context-affine expression of personal theta contract v1

## Status

**POST-PRIMARY MATHEMATICAL-STRUCTURE DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- a one-dimensional personal FlightIntensity parameter theta was supported and shown to converge with repeated environments;
- a simple margin-reliability law was unsupported;
- an individual-specific noise-scale sigma did not improve held-out prediction;
- an independent Yamada learning analysis suggested context-dependent expression strength alpha.

No context-affine held-out result from the Teshima obstacle environments has been calculated before this contract.

## Question

Can the environment-specific deviations from a stable personal coordinate be explained by a **shared affine transformation of the same theta axis**?

Model:

[
y_{ie}
=
gamma_e
+
alpha_e	heta_i
+
epsilon_{ie}.
]

Here:
- (	heta_i) is the portable personal coordinate learned from other environments;
- (gamma_e) is the target-environment operating-point shift;
- (alpha_e) is the target-environment expression strength of the personal axis.

If this works, individual behaviour remains fundamentally one-dimensional even when its expression changes across contexts.

## Data

Use exactly the existing *Rhinolophus nippon* bat × environment mean FlightIntensity values from the seven obstacle configurations.

## Held-out target design

Leave one bat × environment centroid (y_{ie}) out.

A target is evaluable only if:
- the target environment contains at least **4** observed bats before removal, leaving >=3 peer bats;
- the focal bat occurs in at least **4** environments, leaving >=3 non-target environments;
- every peer used in target-environment calibration has at least 2 non-target environments from which its theta can be estimated.

Given the known incidence structure, the frozen expected target universe is:
- Env1–Env4 only;
- **17 bat × environment targets**.

No target from Env5–Env7 may be added after opening.

## Training-only theta

For every bat k appearing in target environment e:

[
hat	heta_{k,-e}
=
mean(y_{k,e'},e'
eq e).
]

The target environment is excluded from every theta estimate, including peers.

Thus the target-environment outcomes are used only to learn how that environment expresses an already-estimated personal axis.

## Three prediction models

### C0 — environment-only peer mean

[
hat y^{(0)}_{ie}
=
mean_{j
eq i}(y_{je}).
]

### C1 — portable theta without target-environment calibration

[
hat y^{(1)}_{ie}
=
hat	heta_{i,-e}.
]

### C2 — context-affine theta

Using peers (j
eq i) in target environment e, fit ordinary least squares:

[
y_{je}
=
gamma_e
+
alpha_ehat	heta_{j,-e}.
]

Then predict:

[
hat y^{(2)}_{ie}
=
hatgamma_e
+
hatalpha_ehat	heta_{i,-e}.
]

No regularization, clipping, or slope-sign constraint is allowed.

## Primary endpoints

For every target calculate squared error under C0, C1, C2.

Aggregate:
1. equal target environments within bat;
2. equal biological bat.

Report:
- MSE_env = C0;
- MSE_theta = C1;
- MSE_affine = C2.

Primary gains:

[
G_{env}=MSE_{env}-MSE_{affine}
]

[
G_{theta}=MSE_{theta}-MSE_{affine}.
]

For the affine-expression model to be called supported, **both** gains must:
- be positive;
- have bat-cluster bootstrap 95% lower bound > 0;
- be positive in at least 3/5 bats.

This requires C2 to outperform both:
- target-environment information without personal theta;
- portable personal theta without target-environment calibration.

## Uncertainty

Cluster bootstrap biological bats.

- B = 9,999
- seed = 20261007961

Report percentile 95% CIs for both gains.

## Secondary outputs

Descriptively report held-out-fold estimates of:
- alpha_e;
- gamma_e;
- peer count.

Because each fold leaves a different bat out, alpha and gamma are fold-specific estimates, not single authoritative environment parameters.

## Interpretation

### Supported

The compact representation becomes:

[
y_{ie}
=
gamma_e
+
alpha_e	heta_i
+
epsilon.
]

The individual-specific portable component still needs only **one scalar theta**; environmental context changes its expression.

### Unsupported

Environment-specific deviations cannot be reduced to a common affine rescaling of one personal axis under this small held-out design.

Then a richer individual × environment term remains necessary.

## Claim ceiling

This diagnostic uses other bats in the target environment to estimate context expression.

It therefore tests structural compressibility of individual × environment variation, not zero-shot prediction in a completely unseen environment before any conspecific is observed.
