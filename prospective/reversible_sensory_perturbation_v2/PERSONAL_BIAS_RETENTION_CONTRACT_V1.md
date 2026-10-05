# Reversible sensory personal-bias retention contract v1

## Status

**FROZEN PUBLIC-DATA REANALYSIS BEFORE CACHED NUMERIC WORKBOOK OUTCOMES ARE OPENED BY THIS PROGRAMME.**

This is not an independent blinded replication of the source paper:
the published paper already displays individual condition means and reports condition effects.

The new endpoint is nevertheless frozen before this programme opens the exact public-workbook numeric cells used below.

Parents:
- `SOURCE_RECEIPT_V1.md`
- `SOURCE_DESIGN_SEQUENCE_V1.md`
- `ARCHIVE_INVENTORY_CONTRACT_V1.md`
- `SCHEMA_OPENING_CONTRACT_V1.md`
- `STRUCTURAL_LAYOUT_CONTRACT_V1.md`

## Biological question

> **Does a bat's pre-perturbation 3-D movement bias predict its relative movement state under controlled sensory masking?**

The source-defined movement endpoint is 3-D angle of attack.

The source Methods define each flight's 3-D angle summary from the final 50 cm of flight using the median of the smallest 15% of angle samples.

The public workbooks reproduce this architecture:
- one source condition per sheet;
- one source-derived per-flight median row;
- one workbook formula averaging those per-flight medians.

This programme does not reconstruct raw trajectories.

---

# Source-native bat-condition scalar

Biological individuals:
- Lucy
- Alvin
- Betty
- Stevie
- Dolores
- Clementine

Primary source sheets present for all six:
- baseline: `No masker_xyz`
- masker 30 cm: `board30_xyz`
- masker 10 cm: `board10_xyz`

For each bat × sheet:

1. locate the row-12 string cell equal to `median` case-insensitively;
2. identify the contiguous row-12 formula cells immediately to its right;
3. require >=5 per-flight summary formula cells;
4. let first and last summary cells be (c_1, c_n);
5. require the first summary column's row-13 formula to be source-equivalent to:
   `AVERAGE(c1_row12:cn_row12)`;
6. open **only the cached numeric result of that row-13 formula**.

That cached value is the bat-condition source-native mean of per-flight 3-D angle summaries.

Do not open:
- raw left-block numeric series;
- row-12 per-flight cached medians;
- any acoustic endpoint;
- any other numeric cell.

---

# P1 — baseline personal-bias retention under masker

Let (m_{i0}) be bat i's baseline no-masker mean angle.

Define the centered baseline personal bias:

[
\theta_i
=
m_{i0}
-
\frac{1}{6}\sum_j m_{j0}.
]

For each masked condition (c\in\{30,10\}):

[
y_{ic}
=
m_{ic}
-
\frac{1}{6}\sum_j m_{jc}.
]

Thus the common population shift caused by each masker condition is removed.

For every bat-condition target:

[
D^{self}_{ic}=|y_{ic}-\theta_i|
]

and

[
D^{other}_{ic}
=
\frac{1}{5}
\sum_{j\neq i}|y_{ic}-\theta_j|.
]

Identity advantage:

[
K_{ic}=D^{other}_{ic}-D^{self}_{ic}.
]

Aggregate:
1. equal mean of 30 cm and 10 cm within bat;
2. equal mean across six bats.

Call the result (K_{mask}).

## Exact null

Keep all target condition values and labels fixed.

Enumerate **all 6! = 720** permutations of the mapping between the six baseline personal-bias values and biological bat labels.

For every mapping recompute the full statistic.

Exact one-sided p:

[
p=
\frac{\#\{K_{null}\ge K_{obs}\}}{720}.
]

The observed identity mapping is one of the 720 exact mappings.

## P1 support rule

Call baseline personal-bias retention supported only if all are true:

- (K_{mask}>0);
- exact one-sided p <= 0.05;
- >=5/6 bats have positive mean (K_i);
- mean K is positive separately in both:
  - 30 cm;
  - 10 cm.

Also report:
- baseline vs 30 cm Pearson and Spearman correlation of centered bat means;
- baseline vs 10 cm Pearson and Spearman;
- pair-order accuracy for each target condition;
- no-refit R²:
  [
  1-\frac{\sum_{i,c}(y_{ic}-\theta_i)^2}{\sum_{i,c}y_{ic}^2}.
  ]

These are secondary and cannot rescue P1.

---

# P2 — masker removal and re-addition under foam target

This is a secondary source-defined reversibility test and cannot rescue P1.

Use only the five bats with a common 30-cm foam-masker condition:

- Lucy
- Betty
- Stevie
- Dolores
- Clementine

Exclude Alvin **before outcome opening** because the source design gave Alvin:
- `foam20_xyz`, not `foam30_xyz`.

Recovery/control source sheets:
- Lucy: `No masker foam_xyz`
- Betty: `No masker foam_xyz`
- Stevie: `No masker foam_xyz`
- Dolores: `No masker foam_xyz`
- Clementine: `No masker foam`

Re-perturbation:
- `foam30_xyz`

Extract the same source-native row-13 mean angle.

Center within the five bats separately for:
- foam no-masker;
- foam + 30-cm masker.

Use the same self-vs-other identity advantage with the no-masker-foam bias as predictor of the foam+masker target.

Exact null:
- enumerate all **5! = 120** predictor-label permutations.

Report:
- K;
- exact p;
- positive-bat fraction;
- no-refit R²;
- Pearson/Spearman;
- pair-order accuracy.

Secondary support requires:
- K > 0;
- exact p <= 0.05;
- >=4/5 positive bats.

P2 cannot rescue failed P1.

---

# Interpretation

## P1 supported

Allowed:

> **A pre-perturbation individual movement bias remains predictive after the same animals are exposed to controlled acoustic masking, even after the shared condition shift is removed.**

This directly supports persistence of an identity-bearing movement state through an experimental sensory perturbation.

It does not establish that the bias is:
- learned;
- biomechanical;
- neural;
- the same coordinate as Rhino FlightIntensity/ManeuveringExtent.

## P2 additionally supported

Allowed:

> **Under a second target material, personal movement bias remains recognizable across masker removal and re-addition.**

Because the target material differs from the original baseline, do not call P2 exact return-to-baseline recovery.

## P1 unsupported

Conclude only that this source-defined 1-D movement bias does not retain enough cross-condition identity under the frozen endpoint.

Do not change to:
- minimal altitude;
- 2-D horizontal angle;
- speed;
- a subset of bats;
- only the weaker or stronger masker condition.

---

# Claim ceiling

This programme tests a **source-defined one-dimensional movement-policy bias**.

It is not a fixed-axis external validation of the Rhino two-dimensional policy law.

Its value is causal:
the sensory environment is manipulated within the same biological individuals.

## No rescue

Do not:
- open individual per-flight medians to tune aggregation;
- z-score conditions after seeing results;
- select one masker distance;
- substitute minimal altitude if P1 fails;
- exclude Stevie because the source paper reports an unusual baseline angle;
- use asymptotic p-values instead of exact permutation.
