# Geometry identity beyond FlightIntensity contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC.**

Parents:
- \`GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md\`
- \`GEOMETRY_POLICY_FAMILY_ABLATION_RESULT_V1.md\`
- \`CAROLLIA_FIXED_GEOMETRY_EXTERNAL_RESULT_V1.md\`

The Rhino scale-free geometry signal is supported internally but fails to transfer as a fixed geometry representation to Carollia.

This diagnostic asks whether, within Rhino, the geometry identity is merely a linear correlate of the dominant FlightIntensity axis.

## Data

Use exactly the authoritative 45 *Rhinolophus nippon* trajectories and the frozen representations:

### FlightIntensity

Within each environment, standardize the original eight movement features exactly as in the Primary-B programme.

Then:

\[
I_q
=
\frac{
z(v_{med})+
z(v_{90})+
z(|v_z|_{med})+
z(|v_z|_{90})
}{4}.
\]

No refitting.

### Scale-free geometry

Use exactly the frozen eight geometry-only features:
1. path efficiency;
2. horizontal displacement ratio;
3. absolute vertical displacement ratio;
4. vertical range ratio;
5. median absolute horizontal turn angle;
6. p90 absolute horizontal turn angle;
7. median absolute vertical slope;
8. p90 absolute vertical slope.

Standardize each geometry feature within environment exactly as in the supported parent geometry diagnostic.

## Label-free intensity residualization

Within every environment separately, and for every standardized geometry feature j, fit:

\[
g_{qj}=\beta_{0ej}+\beta_{1ej}I_q+\epsilon_{qj}.
\]

The fit uses:
- trajectory values only;
- no bat identity;
- no cross-environment matching.

Retain only:

\[
r_{qj}=\epsilon_{qj}.
\]

Do **not** re-standardize residuals afterward.

Thus a feature that was largely explained by FlightIntensity is appropriately downweighted by its remaining residual variance.

## R1 — residual geometry identity

Apply the exact geometry parent cross-configuration identity estimator to the 8-D residual geometry vectors:

- held-out target environment;
- equal trajectory within bat × training environment;
- equal training environments within bat;
- own versus equal donor-bat centroids;
- equal target trajectories within bat;
- equal bats in programme statistic.

## Null

Within every environment independently permute complete bat labels among trajectory clusters.

Residualization coefficients are label-free and remain fixed.

9,999 permutations.

Seed:
\`202610061401\`.

Require >=9,500 valid statistics.

## Support rule

Call residual geometry identity supported only if:
- K_resid > 0;
- one-sided p <= 0.05;
- >=4/5 bats positive.

## Descriptive diagnostics

Report:
- parent geometry K;
- residual geometry K;
- K_resid / K_parent;
- per-feature within-environment median \(R^2\) from geometry ~ FlightIntensity;
- individual residual K values.

Do not select features after output.

## Interpretation

### Supported

Allowed:

> **Rhino scale-free coordinative geometry contains portable individual information beyond the dominant linear FlightIntensity axis.**

This supports a two-layer within-system architecture:
- coarse movement intensity;
- additional system-specific coordinative organization.

It does not show that these are anatomically independent control modules.

### Unsupported

Allowed:

> the scale-free geometry identity is not separable from the dominant FlightIntensity axis under this linear residualization.

This would make the geometry result less independent mechanistically.

## Ceiling

Even support does not establish:
- motor degeneracy as cause;
- universal geometry individuality;
- nonlinear independence from FlightIntensity;
- morphology versus learning origin.

## No rescue

Do not:
- add polynomial terms after output;
- residualize against a selected subset of speed variables;
- drop features;
- select environments;
- re-standardize residuals to restore signal.

## JAE firewall

No change to JAE v0.4.0.
