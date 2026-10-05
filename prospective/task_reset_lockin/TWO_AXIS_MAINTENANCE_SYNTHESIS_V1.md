# Two-axis maintenance synthesis v1

## Status

**POST-PRIMARY MECHANISM SYNTHESIS.**

This document integrates only already-opened results.
It does not create a new inferential endpoint.

Branch:
`prospective/task-reset-lockin-v1`

## Central conclusion

The present evidence does **not** support the idea that a bat's persistent individual strategy is an irreducibly idiosyncratic trajectory rule.

For *Rhinolophus nippon*, cross-configuration individual flight organization is well described by a low-dimensional policy space with two interpretable axes:

1. **FlightIntensity**
2. **ManeuveringExtent / route organization**

A compact representation is therefore:

[
mathbf{z}_{ie}
approx
	heta^{(I)}_i mathbf{v}_I
+
	heta^{(M)}_i mathbf{v}_M
+
oldsymbol{arepsilon}_{ie},
]

after obstacle-configuration means/scales are removed.

This is an approximate behavioural factor model, not a deterministic law of flight.

---

## Axis 1 — FlightIntensity

Transparent definition:

[
I = mathrm{mean}
(z_{mathrm{median speed}},
 z_{mathrm{p90 speed}},
 z_{mathrm{median |vertical speed|}},
 z_{mathrm{p90 |vertical speed|}})
]

Evidence:

- transparent scalar identity:
  K = **0.49656**;
  5/5 bats positive;
  p = **0.0003**;

- speed alone:
  K = **0.52121**;
  p = **0.0003**;

- vertical-speed magnitude alone:
  K = **0.44098**;
  p = **0.0012**;

- relative verticality contrast:
  unsupported, p = **0.4093**.

Interpretation:

The primary stable axis is not "vertical versus horizontal flight".
It is closer to an individual's **overall movement intensity / performance scale**.

The PCA equivalent is exceptionally stable:
- leave-one-environment PC1 pairwise cosine:
  minimum **0.9833**;
  median **0.9964**;
- cosine with transparent FlightIntensity direction:
  minimum **0.9300**;
  median **0.9427**.

A one-dimensional PCA coordinate alone is sufficient to identify held-out individuals:
- K = **0.95785**;
- 5/5 positive;
- p = **0.0006**.

A training-only identity axis also succeeds:
- K = **0.88483**;
- 5/5 positive;
- p = **0.0021**.

Thus the one-axis result is not merely a global PCA artifact.

---

## Axis 2 — ManeuveringExtent / route organization

Transparent definition frozen after signed-PC2 inspection:

[
M =
mathrm{mean}
(-z_{mathrm{median speed}},
 z_{mathrm{median turn rate}},
 z_{mathrm{p90 turn rate}},
 z_{mathrm{path efficiency}},
 z_{mathrm{vertical range}})
]

The training PC2 is highly stable across held-out environments:
- pairwise cosine minimum **0.9709**;
- median **0.9923**;
- mean **0.9898**.

Median signed PC2 loadings:
- median speed: **−0.254**;
- p90 speed: **−0.095**;
- median vertical speed: **+0.049**;
- p90 vertical speed: **+0.044**;
- median turn rate: **+0.610**;
- p90 turn rate: **+0.467**;
- path efficiency: **+0.375**;
- vertical range: **+0.455**.

Transparent M aligns with PC2:
- fold cosine range **0.940–0.973**;
- median **0.959**.

M alone carries cross-configuration identity:
- K = **0.23375**;
- 4/5 positive;
- p = **0.0027**.

Interpretation:

This axis is largely independent of FlightIntensity and describes a second mode involving:
- stronger turning;
- larger vertical excursion;
- greater path efficiency;
- somewhat lower median speed.

"ManeuveringExtent / route organization" is a descriptive label, not a physiological mechanism.

---

## Why one axis is sufficient but not complete

The one-dimensional result is real, but it is not the whole individual policy.

Removing training PC1 leaves:
- residual K = **0.38896**;
- 5/5 positive;
- p = **0.0031**.

Removing PC1 + PC2 leaves:
- residual K = **0.05700**;
- 5/5 positive directionally;
- p = **0.1553**.

Thus:

> PC1 is sufficient for individual discrimination, but approximately two dimensions are needed to exhaust the calibrated linear identity signal.

This distinction is important.

---

## Transparent two-axis falsification

Using only the transparent pair ((I,M)):

- K = **0.55428**;
- 5/5 positive;
- p = **0.0001**.

This recovers about **58.7%** of the full 8-D K statistic.

More importantly, after projecting the full 8-D feature vectors onto the orthogonal complement of the transparent ((I,M)) span:

- residual K = **0.08771**;
- 5/5 remain directionally positive;
- p = **0.0863**.

Under the frozen calibrated criterion, residual identity is no longer supported.

Therefore:

> the two transparent axes capture the calibrated cross-configuration individual signal to the resolution of this dataset.

---

## Reconstruction versus identity

A one-axis model is not an exact reconstruction of the full movement vector.

Held-out multivariate reconstruction:

### Rank 1
- R² = **0.22199**;
- p = **0.0016**;
- median cosine = **0.720**.

### Rank 2
- R² = **0.32781**;
- p = **0.0002**;
- incremental R² = **+0.10581**.

Thus the policy is low-dimensional in its **individual information**, but environment/trial variation still occupies substantial dimensions of the observed flight vector.

This prevents an overclaim that bat trajectories are generated exactly by two constants.

---

## Scalar-plus-noise structure of the primary axis

The transparent FlightIntensity parameter has more structure than a classifier embedding.

Using only other environments to estimate individual (	heta_i):

- held-out pair-difference slope through origin:
  **1.0314**;
- Pearson r:
  **0.5548**;
- pair × environment sign accuracy:
  **82.9%**;
- equal-pair sign accuracy:
  **82.2%**.

No-refit prediction:

[
widehat{Delta y}_{ij,e}
=
	heta_{i,-e}
-
	heta_{j,-e}
]

achieves:
- R² against zero-difference prediction:
  **0.6274**;
- p = **0.0005**.

Prediction errors concentrate where individual parameters are close:
- mean |(Delta	heta)| correct = **0.934**;
- mean |(Delta	heta)| errors = **0.557**;
- margin contrast p = **0.0249**;
- 4/6 errors occur in the lower half of observed margins;
- 3/6 occur in the lowest quartile.

Probability of preserving pairwise order increases with |(Delta	heta)|:
- logistic margin slope = **+1.879**;
- permutation p = **0.0467**.

This is compatible with an approximate:

[
y_{ie} = 	heta_i + epsilon_{ie}
]

architecture for the intensity axis.

---

## The policy is not immutable

The low-dimensional policy should not be interpreted as a fixed morphological constant.

Independent published experiments on naïve *R. nippon* show that repeated exposure to a novel obstacle course alters flight control:

Yamada et al. 2020:
- 14 bats;
- all naïve to the obstacle layouts;
- 12 repeated flights per animal;
- meandering width declines with familiarity;
- in the acoustically permeable condition, maximum speed rose from about **2.5 to 3.4 m/s** between the first and twelfth flights;
- pulse timing and acoustic gaze also changed with learning.

Therefore the current synthesis is more consistent with:

> a low-dimensional policy state that can be updated by experience, rather than a literal immutable trajectory fingerprint.

---

## Formation and maintenance model

The combined evidence now suggests four levels.

### 1. Species architecture

Morphology, flight mechanics and sonar architecture constrain the available policy space.

This is consistent with independent evidence that:
- *R. nippon* and *M. fuliginosus* have strongly contrasting flight morphology;
- the two species use different acoustic-gaze strategies.

### 2. Personal policy coordinates

Within *R. nippon*, individuals occupy different positions in a low-dimensional movement-policy space.

Current approximation:

[
Theta_i =
(	heta^{(I)}_i,
 	heta^{(M)}_i).
]

### 3. Experience-dependent updating

Repeated experience can move behaviour within that policy space:
- speed changes;
- route meandering changes;
- sensing strategy changes.

### 4. Maintenance without spatial partition

Once a personal policy state is established, subsequent movement can remain history-dependent even when individuals occupy overlapping physical space.

Thus individual specialization need not be maintained by:
- persistent exclusion;
- exclusive vertical strata;
- exclusive resource patches.

It can instead be maintained by persistence/reuse of an **individual policy state**.

---

## Cross-species boundary

The Rhino-derived axes do not generalize to *Miniopterus fuliginosus*:

Transparent FlightIntensity transferred to Miniopterus:
- K = **0.09747**;
- p = **0.2508**.

Fixed Rhino PC1:
- K = **0.33063**;
- p = **0.1593**.

A Miniopterus-specific PC1 also failed:
- K = **−0.16876**;
- p = **0.2529**.

The original full-8D Miniopterus transfer was also unsupported.

Therefore the current low-dimensional individual-policy result is **not a universal bat law**.

A biologically plausible boundary is that species differ in the number and type of sensorimotor degrees of freedom available during obstacle avoidance.

This remains a hypothesis, not a demonstrated cause of the species contrast.

---

## What the current evidence rules out

The current programme makes the following simple explanations less plausible:

1. **persistent spatial partition maintains individuality**
   - contradicted by JAE co-use/separation analyses;

2. **literal route memory is the whole individual signature**
   - route identity collapses after translation/shape controls while portable movement-policy identity remains;

3. **individuality is only one trivial speed scalar**
   - PC1 removal leaves significant identity;
   - PC2/ManeuveringExtent independently carries identity;

4. **pulse individuality is clearly independent of movement**
   - initial residual pulse diagnostics were positive, but stricter cross-fitted nuisance control was unsupported
     (P=0.1179, p=0.2032, 3/5 positive);

5. **simple body mass explains the original adult-field individuality**
   - donor-gradient test: 0/4 panels;
   - same-individual morphology attribution for the Rhino arena bats remains unidentifiable because no defensible A–E crosswalk exists.

---

## Current strongest mechanistic statement

> **Persistent individual movement strategies can be carried by a low-dimensional, experience-modifiable sensorimotor policy rather than by continued spatial partitioning.**

For *R. nippon* in the obstacle-flight system, the calibrated individual information is approximately two-dimensional and can be represented transparently by:
- flight intensity;
- maneuvering / route organization.

The origin of each individual's coordinates remains unresolved:
- morphology;
- physiology;
- developmental history;
- learned motor policy;
- or their interaction.

That is now the main causal question.
