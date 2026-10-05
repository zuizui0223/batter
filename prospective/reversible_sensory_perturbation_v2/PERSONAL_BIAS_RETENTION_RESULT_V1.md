# Reversible sensory personal-bias retention result v1

## Status

**P1 SUPPORTED. P2 SUPPORTED.**

Authoritative workflow:
- run: **37390031185**
- job: **112032657710**
- workflow conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`PERSONAL_BIAS_RETENTION_CONTRACT_V1.md`

This is a frozen public-data reanalysis, not an independent blinded replication of the source paper.
The source paper already displays individual condition means and reports the common condition effect.
The new endpoint is the exact cross-condition identity-retention statistic frozen before this programme opened the workbook cached numeric cells.

## Source-native endpoint

For each bat × source condition, the programme opened only the workbook's cached formula value for:

> equal-flight mean of the source-derived per-flight 3-D angle-of-attack summaries.

The source analysis defines each flight's angle summary as the median of the smallest 15% of 3-D angle values in the final 50 cm before landing.

No raw trajectory series, per-flight cached angle values, acoustic outcome or alternative movement endpoint was opened for model selection.

---

# P1 — baseline personal bias retained under masker

Six bats:
- Lucy
- Alvin
- Betty
- Stevie
- Dolores
- Clementine

Conditions:
- baseline: no masker / styrofoam target;
- masker 30 cm;
- masker 10 cm.

For every condition, the equal-bat population mean was removed.
The no-masker centered bat mean was used as the pre-perturbation personal predictor.

## Primary

- `K_mask = +4.94141 deg`
- masker 30 cm: `K = +8.00448 deg`
- masker 10 cm: `K = +1.87833 deg`
- positive bats: **5/6 = 83.3%**
- exact permutations: **720 / 720**
- exact one-sided `p = 0.0402778`

Verdict:
**SUPPORTED_BASELINE_BIAS_RETENTION**

All frozen gates pass:
- overall K > 0;
- p <= .05;
- >=5/6 bats positive;
- both masker-condition mean K values > 0.

Individual mean identity advantages:

- Lucy: **+7.522**
- Alvin: **-0.260**
- Betty: **+6.730**
- Stevie: **+10.280**
- Dolores: **+2.113**
- Clementine: **+3.263**

No individual was removed after outcome opening.

## Prediction-scale diagnostics

No-refit centered prediction:

- `R2 = 0.28555`

Baseline vs 30-cm centered bat means:
- Pearson `r = 0.9268`
- Spearman `rho = 0.7714`
- pair-order accuracy = **0.800**

Baseline vs 10-cm centered bat means:
- Pearson `r = 0.4870`
- Spearman `rho = 0.5429`
- pair-order accuracy = **0.733**

Thus the personal ordering is especially strong at 30 cm and attenuated, but not erased, under the stronger 10-cm sensory challenge.

The primary exact statistic explicitly required both masker conditions to retain positive identity advantage.

---

# P2 — foam no-masker control to masker re-addition

This secondary test was frozen independently of P1 outcome.

Five bats share the same source-defined foam + 30-cm masker treatment:
- Lucy
- Betty
- Stevie
- Dolores
- Clementine

Alvin was excluded before outcome opening because the source design used 20 cm, not 30 cm, for Alvin's foam condition.

The predictor is each bat's centered angle in the four-day foam/no-masker control.
The target is its centered angle after the masker is added under the same foam target.

## Secondary result

- `K = +6.77896 deg`
- positive bats: **5/5**
- exact permutations: **120 / 120**
- exact one-sided `p = 0.025`

Verdict:
**SUPPORTED_FOAM_REPERTURBATION_BIAS_RETENTION**

Prediction scale:

- no-refit `R2 = 0.64139`
- Pearson `r = 0.95686`
- Spearman `rho = 0.9000`
- pair-order accuracy = **0.900**

Individual K:

- Lucy: **+7.613**
- Betty: **+7.097**
- Stevie: **+5.928**
- Dolores: **+3.894**
- Clementine: **+9.363**

This is especially informative because target material is held constant within P2 while the masker state changes.

---

# Main biological inference

The source experiment is known to produce a population-level movement adjustment under acoustic masking.

The new reanalysis shows something orthogonal:

> **After removing the shared condition shift, a bat's pre-perturbation relative movement bias remains predictive of its relative state under the masker.**

And under the foam-target control/re-perturbation sequence:

> **the individual ordering is retained strongly when the masker is absent and then added under the same target material.**

Therefore a controlled sensory perturbation can move the population operating point without erasing the identity-bearing personal movement bias.

A compact representation is:

[
x_{ic}
=
\mu_c
+
\theta_i
+
\delta_{ic},
]

where:
- (mu_c) is the shared condition shift;
- (	heta_i) is a persistent individual movement bias;
- (delta_{ic}) is remaining individual × condition deviation.

The present result supports persistence of (	heta_i).
It does not establish a universal individual reaction slope.

---

# Relation to the field mechanism problem

Wild *P. hastatus* already shows:
- persistent low-dimensional individual policy;
- policy distance does not map onto synchronous vertical partitioning;
- simple individual peer-context slopes are unsupported.

The present controlled experiment adds a different causal piece:

> **individual movement bias survives an experimentally imposed sensory change.**

This strongly supports the interpretation that specialization can be carried by information/state within the animal rather than requiring continuous spatial exclusion among conspecifics.

It does not prove that this exact 3-D angle coordinate is the same latent variable as the wild H/V carrier or the Rhino I/M policy.

---

# Claim boundary

Supported:

- source-defined 1-D movement bias remains identity-bearing through masker perturbation;
- shared condition change and persistent individual bias coexist;
- foam no-masker to foam+masker re-perturbation preserves individual ordering strongly.

Not established:

- neural storage mechanism;
- learning versus biomechanics as the origin of the bias;
- universal reaction norm;
- equivalence to Rhino FlightIntensity/ManeuveringExtent;
- fitness benefit;
- universal bat law.

## No post-hoc rescue was used

No:
- alternate endpoint;
- minimal-altitude substitution;
- single-condition selection;
- individual exclusion based on result;
- z-score rescue;
- asymptotic p-value.

The exact frozen tests are reported as observed.
