# Theta convergence claim audit and actual correspondence test — authoritative result v1

## Evidence status
**Post-outcome diagnostic, not independent confirmatory validation.**
Do not modify old frozen outcomes or recycle the previous 91.6% figure as evidence of biological convergence.

## Reproducibility
- Workflow: [37723799545](https://github.com/zuizui0223/batter/actions/runs/37723799545)
- Head SHA: `7117178a52732420ed796646cb913b0f9fdb1b96`
- Conclusion: success
- Artifact ID: `11527415261`
- Independent local reimplementation using the prior published centroid artifact matches the programme, individual, null, and algebraic outputs.

## A. The supposed MSE convergence is an identity

For fixed held-out observation y, N observed training-environment values x, sample mean xbar, sample variance s² (denominator N-1), and **exhaustive average** over m-element training subsets:

\[
\frac1{\binom Nm}\sum_{|S|=m}(y-\bar x_S)^2
=(y-\bar x)^2+\frac{N-m}{Nm}s^2.
\]

Verified across all 25 bat×environment targets and m=1,2,3:
- maximum floating-point discrepancy = **2.22e-16**.

MSE necessarily falls with m, even if the identity carried by a bat is completely exchangeable across environments.

For the frozen “fraction-to-full” definition,

\[
F(m)=1-\frac{MSE_m-MSE_{full}}{MSE_1-MSE_{full}}
=1-\frac{N-m}{m(N-1)}.
\]

With m=3:
- A,C,E (N=4): F = 8/9 = **0.8889**;
- B (N=3): F = **1**;
- D (N=5): F = 5/6 = **0.8333**.

The published aggregate **91.6%** is determined by these counts and weights; it is **not** empirical evidence for a biological limit or a convergent individual differential equation.

### Superseded interpretations
- `FINITE_SCALAR_RAPID_CONVERGENCE` cannot be treated as a biological discovery from the subset-MSE test.
- “All five individual parameters converge” is not supported by that test.
- Existing primary cross-environment identity and separate magnitude calibration are not invalidated; they answer different questions.

## B. Non-tautological test of self-history against no personal identity

On the same 25 *Rhinolophus nippon* bat×environment FlightIntensity centroids, estimate each target's scalar from **all other configurations of the same bat**.

Compare squared error with the zero baseline, i.e. the environment-standardized cohort center.

Primary equal-bat gain:

\[
G=\mathbb E_{i,e}\left[y_{ie}^2-(y_{ie}-\hat\theta_{i,-e})^2\right]
=\mathbf{+0.293072}.
\]

- baseline MSE: **0.633974**
- self-history MSE: **0.340902**
- relative R²: **+0.462277**

The correspondence null independently permutes bat identity labels among observed members in each environment, preserving exact environment composition and its scalar distribution.

- 19,999 null permutations; seed 20261008111
- null mean: **−0.170206**
- null 95% interval: **[−0.353295,+0.127382]**
- one-sided **p = 0.00175**

Thus real self-history **does** predict unseen configurations beyond the zero-personal-history baseline under this conditional identity-exchangeability test.

Unlike the prior learning-curve contrast, this is **not** an algebraic necessity: randomised bat correspondence produces much worse forecasts.

### Individual differences in effectiveness

| bat | Gain over zero | R² against zero |
|---|---:|---:|
| A | +1.102492 | +0.903990 |
| B | −0.186842 | −0.602845 |
| C | −0.219724 | −0.340498 |
| D | +0.615213 | +0.951675 |
| E | +0.154219 | +0.442401 |

Only **3/5** bats show positive absolute held-out gain; B/C have negative gain even though 1D identity and the population scalar transfer are supported.

Across only five biological bats, bat-cluster bootstrap 95% CI for G: **[−0.131782,+0.747169]**. It spans zero. Therefore the inference must distinguish:
- strong *conditional within-archive label-permutation evidence*;
- substantial uncertainty about cross-bat population generalization.

Leave-one-bat-out G values:
- omit A: +0.090717;
- omit B: +0.413050;
- omit C: +0.421271;
- omit D: +0.212536;
- omit E: +0.327785.

Programme signal does not reverse with any one omitted bat, but A and D are disproportionately informative.

## Biological meaning

The defensible empirical finding is:

> Within the observed *Rhinolophus* obstacle-configuration system, personal identity contains portable low-dimensional information about **relative flight intensity**, but that scalar is individually heterogeneous in reliability.

The data support a stable population-level personal component over these sampled configurations but do **not** establish:
- strict stationarity for each bat;
- long-run convergence as more environments accumulate;
- a unique 1D dynamical flight equation;
- the origins of bat-specific reliability (morphology, learning, sensory control);
- generality to other bat species.

## Why Miniopterus is not a clean negative species comparison

In the same archive, *Miniopterus fuliginosus* has:
- 19 trajectories, four bats, and **12 bat×environment clusters**;
- five of seven environments have exactly **one tracked bat**;
- its frozen within-environment-centering operation forces the sole bat's environment-level centroid to **zero** in each of these five environments;
- only environments 2 and 3 have multiple distinct bats.

The all-dimension null finding remains the exact reported diagnostic result, but the available design has very low identifiability for shared cross-environment personal centroids. It should not be promoted to a biological conclusion that *Miniopterus* lacks a stable personal law.

## Recommended next empirical discriminator

Compare individuals under **multiple identical or matched environments**, each with sufficient co-tracked bats, then manipulate task geometry/learning within the **same identified bats**.

Predefine:
1. baseline individual `theta_i`;
2. an environmental response `g_i(E)` or reliability `sigma_i`;
3. held-out calibration and forward performance across truly new configurations.

That can distinguish a rigid personal prior from a changing individual response rule without the present sampling-composition and algebraic confounds.
