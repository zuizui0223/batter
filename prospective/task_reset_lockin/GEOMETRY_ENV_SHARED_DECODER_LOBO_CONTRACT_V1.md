# Leave-one-bat-out environment-specific I/M -> geometry decoder contract v1

## Status

**POST-PRIMARY EXPLORATORY FALSIFICATION DIAGNOSTIC.**

Parents:
- `GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS_RESULT_V1.md`
- `GEOMETRY_CROSSFIT_IM_EXPRESSION_RESULT_V1.md`
- `GEOMETRY_FAMILY_CROSSFIT_RESIDUAL_RESULT_V1.md`

The current tension is:

1. within an environment, removing I+M eliminates calibrated geometry identity;
2. a single I/M -> geometry map learned from other environments does **not** generalize to an unseen environment;
3. G and H geometry families do not retain incremental identity after linearly accounting for one another.

This suggests an environment-specific expression map.

The remaining question is:

> **Within a given environment, is that expression map shared across bats?**

## Scope

Use the same 45 *Rhinolophus nippon* trajectories and the same frozen:
- 8 movement features;
- transparent FlightIntensity I;
- transparent ManeuveringExtent M;
- 8 scale-free geometry features.

No new feature is introduced.

## Structurally eligible environments

For a focal bat in one environment, the decoder must be fit using **other bats only**.

Require:
- focal environment contains >=4 biological bats total;
- therefore >=3 donor bats remain after focal exclusion.

Under the frozen public support architecture this admits:
- Env1
- Env2
- Env3
- Env4

and excludes:
- Env5
- Env6
- Env7

before any diagnostic output.

## LOBO transformation

For every environment e and focal bat i:

1. donor set = all trajectories in e from bats j != i;
2. calculate movement-feature means/SDs from donor trajectories only;
3. calculate geometry-feature means/SDs from donor trajectories only;
4. transform donor and focal trajectories using those donor-only scaling parameters;
5. compute donor/focal I and M from the donor-defined movement z scores;
6. fit on donor trajectories only:

[
g
=
a+B
egin{bmatrix}
I\M
end{bmatrix}
+epsilon;
]

7. apply the fitted map unchanged to focal-bat trajectories;
8. focal residual geometry:

[
r_{i,e}
=
g_{i,e}-widehat g_{-i,e}(I_{i,e},M_{i,e}).
]

No focal geometry value contributes to:
- scaling;
- regression coefficients.

## Residual identity test

Use only bats with >=3 structurally eligible environments so that leave-one-environment-out residual identity is estimable.

Expected structurally eligible bats:
- B
- C
- D
- E

Bat A is expected to have only Env3 and Env4 and is structurally excluded before outcome.

For every held-out environment:
- build same-bat training residual centroids from other eligible environments;
- average trajectories within environment first;
- average environments equally within bat;
- own-distance versus equal donor-bat distance;
- equal target trajectories within bat;
- equal bats for programme K.

## Null

Residual vectors are calculated from biological bat exclusion and remain fixed.

Within each eligible environment independently:
- permute complete biological labels among bat × environment clusters;
- rerun the residual identity estimator.

9,999 permutations.

Seed:
`202610061701`.

Require >=9,500 valid permutations.

## Support rule

Residual identity after the shared environment-specific decoder is supported only if:
- K > 0;
- p <= 0.05;
- >=3/4 evaluable bats positive.

## Descriptive decoder performance

Also report:
- pooled donor-trained held-out-bat geometry SSE;
- zero-vector baseline SSE under donor scaling;
- descriptive held-out R² = 1 - SSE_decoder / SSE_zero.

This is descriptive and cannot rescue the identity endpoint.

## Interpretation

### Residual identity unsupported

> **Within an obstacle configuration, a geometry-expression map learned from other bats is sufficient to remove the portable identity component of held-out-bat route geometry.**

This supports:

[
oxed{
	ext{portable personal coordinate}
+
	ext{environment-specific shared decoder}
ightarrow
	ext{route geometry}
}
]

### Residual identity supported

Then a shared environment decoder is insufficient.

Allowed interpretation:
- individual-specific expression mapping;
- additional latent personal state beyond I/M;
- or nonlinear structure not captured by the shared linear map.

## Ceiling

Even if residual identity is unsupported, do not claim:
- neural decoder;
- causal two-dimensional state;
- universal decoder form;
- that obstacle geometry itself has been measured.

This is a statistical expression-map diagnostic.
