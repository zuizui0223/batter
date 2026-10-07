# Rhino exactly-two-training-environment support result v1

## Execution

- workflow run: **37627591723**
- head SHA: `8484980906d49c875af72edc7356c35569121f00`
- conclusion: **success**
- artifact: **11484618068**
- artifact zip SHA256: `7f352d1fdba3c6cae5421183bba0b0f443bc2cc16e93397e4364ef463d17f144`

## Question

Does the Rhino one-dimensional personal signal survive when every held-out identity estimate is forced to use exactly two non-target environments, matching the per-target environment support available to Miniopterus?

## Results

### Training-only PCA1

- K = **+0.90983**
- positive bats = **5/5**
- null mean = -0.01317
- null 95% interval = [-0.33631,+0.50550]
- one-sided p = **0.0005**
- 9,999/9,999 valid permutations

Bat means:
- A +2.0437
- B +0.4669
- C +0.1064
- D +1.1529
- E +0.7793

Verdict:
**SUPPORTED**

### Transparent FlightIntensity

- K = **+0.46901**
- positive bats = **5/5**
- null mean = -0.00362
- null 95% interval = [-0.17034,+0.26351]
- one-sided p = **0.0002**
- 9,999/9,999 valid permutations

Bat means:
- A +0.9419
- B +0.2275
- C +0.0687
- D +0.6724
- E +0.4346

Verdict:
**SUPPORTED**

## Interpretation

The Rhino/Mini contrast is not explained simply by Rhino having more independent training environments available for each held-out personal estimate.

Even when every Rhino self/donor centroid is built from exactly two non-target environments:

[
Rhinolophus:quad K_{PCA1}=+0.910,quad p=.0005,
]

whereas the Miniopterus species-specific PCA1 under its native two-training-environment architecture is unsupported and negative:

[
Miniopterus:quad K_{PCA1}=-0.169.
]

This strengthens the biological/mathematical contrast:

- *Rhinolophus*: a portable low-dimensional between-individual component is detectable even under sparse environment support;
- *Miniopterus*: no portable linear personal component is detected across dimensions 1–8 in the current archive.

The comparison still does not equalize total trajectory count, repeated trajectories per bat × environment, noise level, or exact obstacle incidence.
