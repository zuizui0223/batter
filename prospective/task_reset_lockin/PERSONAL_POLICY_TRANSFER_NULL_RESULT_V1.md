# Non-tautological personal-policy transfer: authoritative result v1

## Execution

- GitHub Actions workflow: **37705394801**
- head SHA: `f8e2fc833f258f8978d79e3bf79583f2f7c64186`
- conclusion: **success**
- artifact: **11519441963**
- artifact ZIP SHA256: `8bb97a6e51ea44dad86dae1b7ab17077388ec2cd2d6c9b4af8a0fb91432efc75`
- 45 original *Rhinolophus nippon* trajectories, 5 bats, 7 configurations
- same 25 held-out bat × environment targets for both fixed transparent axes
- 9,999 within-environment complete bat-label permutations
- exact finite-sample subset-MSE identity self-test: **PASS**

This is a post-outcome diagnostic using the same archive as the previously positive individual-policy programme, not an independent confirmation.

## Background mathematical correction

The previously emphasized `MSE_1-MSE_3 > 0` and ~91.6% recovery to the full non-target training mean are, by exact finite-population algebra, driven by averaging more training samples. They cannot by themselves establish convergence of a true latent biological parameter. See `THETA_CONVERGENCE_MATHEMATICAL_AUDIT_V1.md`.

The meaningful question here is whether **true identity correspondence** improves held-out prediction relative to label-disrupted correspondences.

## Two pre-fixed coordinates

- `I`: mean of standardized speed and absolute vertical-speed magnitude features
- `M`: mean of `-median speed`, median/p90 turn rate, path efficiency and vertical range

The null preserves all numerical observations and environment membership, disrupting only which bat carries each environment cluster.

## Results

| model | held-out m=3 gain versus zero | null mean | 95% null interval | p(null >= observed) | positive bats | frozen support |
|---|---:|---:|---|---:|---:|---|
| Intensity I | **+0.27669** | -0.22079 | [-0.41061,+0.09173] | **0.0013** | **3/5** | FAIL: fewer than 4/5 |
| Maneuvering M | **+0.09369** | -0.09686 | [-0.18062,+0.03877] | **0.0050** | **3/5** | FAIL: fewer than 4/5 |
| **Joint I+M** | **+0.37902** | -0.34037 | [-0.57643,-0.01117] | **0.0001** | **4/5** | **PASS** |

The joint gain is the equal mean of the two gains normalized by their fixed observed zero-baseline MSEs, thus it is dimensionless and is not directly comparable in units to either raw-axis gain.

Bat-cluster bootstrap 95% intervals for m=3 gain:

- I: **[-0.15744, +0.72368]**
- M: **[-0.08786, +0.27837]**
- Joint: **[+0.05500, +0.67461]**

Held-out m=3 R² relative to within-environment standardized group-center baseline:

- I: **0.43644**
- M: **0.32160**

Full-training gains remain strongly above label permutations:

- I full gain +0.29307; permutation p=.0019
- M full gain +0.10315; permutation p=.0053
- joint full normalized gain +0.40816; permutation p=.0001

### Biological-bat heterogeneity

The m=3 raw-axis gains by bat:

| bat | I gain | M gain | descriptive main carrier |
|---|---:|---:|---|
| A | +1.0947 | -0.2103 | intensity-dominant |
| B | -0.1868 | -0.0391 | neither positively predictive under this strict baseline |
| C | -0.2774 | +0.4153 | maneuvering-dominant |
| D | +0.6117 | +0.2309 | both positive |
| E | +0.1413 | +0.0718 | both positive, modest |

This pattern explains why the joint fixed-score diagnostic passes the 4/5 rule while each axis alone has 3/5 positive. These individual labels are descriptive, not separately tested response classes.

## Inference

**Supported under the new fixed rule:**
- joint two-coordinate individual history has genuine predictive value beyond the mechanical training-subset averaging identity;
- it exceeds the complete environment-wise bat-identity disruption null;
- the five bats carry heterogeneous mixtures of the two measured personal signals.

**Not established:**
- that each axis individually meets the strict >=4/5 individual-consistency criterion;
- that the second axis improves prediction *conditionally beyond the first* in an independently calibrated nested forecast test;
- that the exact mathematical dimension of the full motor controller is two;
- a universal cross-species law;
- a stable biological attractor or neural parameter;
- a deployable forecast without the label-free standardization of the test environment.

The result should be described as **a compact jointly predictive two-coordinate individual representation in the observed obstacle-task system**, not proof of a unique two-parameter generative equation.
