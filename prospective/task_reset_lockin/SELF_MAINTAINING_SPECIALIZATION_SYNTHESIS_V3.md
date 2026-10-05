# Self-maintaining specialization synthesis v3

## Status

**POST-JAE MECHANISM SYNTHESIS.**

This document does not modify JAE v0.4.0. It synthesizes prospective and post-primary evidence on the mechanism question:

> How can persistent individual specialization be maintained when individuals do not need to keep partitioning space?

---

## 1. Central answer now supported by multiple lines of evidence

The strongest current architecture is:

[
oxed{
	ext{persistent personal policy}
+
	ext{history/state persistence}
ightarrow
	ext{context-specific behaviour}
}
]

with no requirement that different individuals continuously repel one another in physical space.

The persistent object is not a literal route and not an exclusive spatial territory.

It is better represented as a low-dimensional personal movement-policy state.

---

## 2. The mathematical sufficiency result

The self-reinforcing Pólya-process note establishes an exact separation between specialization and partitioning.

For K feasible solutions and symmetric reinforcement parameter alpha:

[
P(A_{it}=kmid n_i(t))
=
rac{alpha+n_{ik}(t)}{Kalpha+t}.
]

No other-individual term appears.

At the asymptotic limit:

[
p_i sim Dirichlet(alpha,ldots,alpha).
]

Within-individual concentration is

[
E[H_i]
=
rac{alpha+1}{Kalpha+1}
>
rac1K.
]

But expected overlap between two independently reinforced individuals remains

[
Eleft[sum_k p_{ik}p_{jk}ight]
=
rac1K.
]

Therefore self-reinforced history is mathematically sufficient to generate:

- persistent individual specialization;
- no expected between-individual repulsion.

The implementation check matched the closed forms to about 0.002 or better across K=2,4,8 and alpha=0.1,0.5,1,5.

This is a sufficiency model, not evidence that bats literally implement a Pólya urn.

---

## 3. Laboratory evidence: the carrier is policy, not route

In *Rhinolophus nippon*, movement individuality transfers across seven different obstacle configurations.

The full measured movement-policy vector contains:
- speed;
- absolute vertical speed;
- horizontal turning rate;
- path efficiency;
- vertical range.

Literal route identity is sensitive to absolute route position and weakens under route-shape controls.

By contrast, policy identity survives across configurations.

Thus the persistent object is better described as a control tendency than as a memorized path.

---

## 4. Low-dimensional structure of the laboratory policy

### PC1 — FlightIntensity

One held-out-environment PC is sufficient for identity:

- K = 0.95785;
- 5/5 bats positive;
- p = 0.0006.

The PC1 direction is almost invariant across folds:

- minimum pairwise cosine = 0.9833;
- median = 0.9964.

It aligns with the transparent scalar

[
I
=
mean(
z_{mathrm{median speed}},
z_{mathrm{p90 speed}},
z_{mathrm{median |v_z|}},
z_{mathrm{p90 |v_z|}}
).
]

Transparent FlightIntensity alone is supported:

- K = 0.49656;
- 5/5 positive;
- p = 0.0003.

A no-refit scalar-plus-noise approximation predicts held-out individual differences:

- pair-difference R² = 0.627;
- p = 0.0005;
- pairwise magnitude calibration slope = 1.031;
- Pearson r = 0.555;
- ordering accuracy = 82.9%.

Errors are concentrated among bats close in the scalar.

### PC2 — ManeuverStructure

PC1 removal leaves residual identity:

- K = 0.38896;
- 5/5 positive;
- p ≈ 0.0031.

Removing PC1+PC2 removes calibrated residual identity:

- K = 0.0570;
- p = 0.1553.

PC2 is itself stable:

- minimum foldwise cosine = 0.9709;
- median = 0.9923.

Its dominant signed loadings are:

- median turning rate: +0.610;
- p90 turning rate: +0.467;
- path efficiency: +0.375;
- vertical range: +0.455;
- median speed: −0.254;
- other speed/vertical-speed terms small.

Its median absolute cosine with FlightIntensity is only about 0.112.

Therefore the calibrated portable movement signal is approximately two-dimensional:

1. **FlightIntensity**;
2. **ManeuverStructure**.

One dimension is enough to identify bats, but approximately two dimensions are required to exhaust the calibrated linear identity signal.

---

## 5. One parameter is useful but not exact

Rank-one reconstruction of the held-out eight-dimensional policy centroid is positive:

- R² = 0.222;
- p = 0.0016.

Rank two improves reconstruction:

- R² = 0.328;
- p = 0.0002.

Thus the policy is genuinely low-dimensional, but trial-level movement is not a deterministic one-parameter trajectory generator.

A useful representation is:

[
x_{iet}
=
mu_e
+
Lambda_s	heta_i
+
epsilon_{iet},
]

where (	heta_i) is low-dimensional and (epsilon) contains remaining trial/context variation.

---

## 6. External generality is component-specific, not universal

A frozen external application to *Carollia perspicillata* supports the fixed low-dimensional representation:

- fixed 2-D K = 0.34758;
- 6/7 bats positive;
- p = 0.0007.

The strongest recurring component is FlightIntensity:

- fixed I alone K = 0.36775;
- p = 0.0014.

The second axis is weaker as a universal increment.

By contrast, *Miniopterus fuliginosus* shows no calibrated portable identity under:
- full 8-D policy;
- Rhino-fixed PC1;
- transparent FlightIntensity;
- Miniopterus-specific PCA1.

Therefore there is no universal bat-wide single axis.

The defensible generalization is:

> low-dimensional personal policy can occur, but the strength and orientation of the policy manifold are species/task dependent.

---

## 7. Wild-field carrier in Phyllostomus hastatus

The laboratory policy axes are not assumed to transfer literally to the field.

Instead, a frozen field-specific two-dimensional policy was constructed from:
- horizontal movement intensity H;
- vertical movement intensity V.

The 2-D carrier is supported independently in both years:

### 2022
- K_2D = 0.65314;
- 32/34 positive;
- p = 0.0001.

### 2023
- K_2D = 0.27052;
- 9/11 positive;
- p ≈ 0.033.

Thus the central low-dimensional carrier phenomenon is present in wild repeated movement.

The H and V coordinates show a strong allocation-like structure rather than being simple duplicates of one scalar.

The transparent allocation axis

[
A=(H-V)/sqrt2
]

is strongly supported in 2022 and directional but not conventionally significant in 2023.

Therefore the field result should remain primarily **two-dimensional**, with an interpretable horizontal-versus-vertical allocation component.

---

## 8. The policy carrier is not the full spatial phenotype

A critical negative result:

Similarity in the two-dimensional field policy does **not** reliably predict similarity in the full centered vertical-distribution shape.

- 2022 policy-to-shape p = 0.4548;
- 2023 p = 0.5627.

Therefore:

[
	ext{persistent policy state}

eq
	ext{complete realized vertical distribution}.
]

The persistent policy is a carrier or latent control state whose realized spatial output depends on context.

This is exactly what is expected under an environment-dependent generator.

---

## 9. Temporal evidence for maintenance

### Strict-past prediction

A target field session is better predicted by the focal bat's strictly earlier allocation history than by strictly earlier histories of other bats.

2022:
- K_past = 0.37266;
- 26 positive individuals;
- p = 0.0001.

2023:
- K_past = 0.27201;
- 6/7 positive;
- p = 0.0258.

This is temporal self-predictability, not merely same-dataset clustering.

### Excluding the latest session

After deleting the immediately previous self session:

2022:
- K_older = 0.34147;
- 25/32 positive;
- p = 0.0001.

2023:
- K_older = 0.14170;
- 5/7 positive;
- p = 0.1713.

Thus 2022 directly rejects a pure one-step-inertia explanation.
2023 is directionally consistent but underpowered/inconclusive after latest-session deletion.

### Within-individual dynamic state

After preserving each individual's entire marginal distribution and fixed mean, but randomizing temporal order within individual:

2022:
- R = 0.03463;
- p = 0.0003.

2023:
- R = 0.01654;
- p = 0.026.

Persistence is stronger at short temporal gaps and weakens at long gaps.

The field data therefore support a two-timescale picture:

[
	ext{persistent individual policy}
+
	ext{short-term state persistence}.
]

This is stronger than a model containing only a fixed individual mean plus exchangeable noise.

It still does not uniquely distinguish memory from temporally autocorrelated environment or physiology.

---

## 10. Direct field test: policy differentiation is not spatial partitioning

The strongest new bridge uses the **same wild dyads**.

For each *P. hastatus* dyad:
- policy distance = Euclidean distance between persistent 2-D (H,V) policy coordinates;
- spatial outcome = the authoritative frozen median terrain-relative vertical separation during synchronous local co-use.

The co-use endpoints are read directly from the authoritative frozen workflow artifacts; no encounter geometry was redefined.

### 2022

All 10 frozen dyads had policy coordinates.

Spearman association:

[
ho(D_{policy},S_{couse})=0.188.
]

Permutation:
- p = 0.2743.

Result:
**no positive policy-distance/separation association.**

### 2023

All 8 frozen dyads had policy coordinates.

Spearman association:

[
ho(D_{policy},S_{couse})=-0.190.
]

Permutation:
- p = 0.6887.

Result:
**no positive policy-distance/separation association.**

This is especially informative because 2023 is the one panel in which overall synchronous separation itself was elevated relative to the phase-shift null.

Even in that exceptional year, persistent policy distance does not monotonically organize dyad vertical separation.

Therefore the same field system directly supports:

[
oxed{
	ext{individual policy differentiation}

eq
	ext{spatial partitioning}
}
]

at the dyad level.

---

## 11. Revised mechanism

The current most economical biological architecture is:

[
oxed{
	ext{early symmetry breaking / stable performance bias}
ightarrow
	ext{persistent low-dimensional personal policy}
leftrightarrow
	ext{history-dependent short-term state}
ightarrow
	ext{context-specific spatial realization}
}
]

The double arrow marks that current observational data do not identify whether history creates the long-term policy, updates it, or merely tracks a stable underlying performance trait.

The crucial point is that no persistent competitor-driven separation term is required to maintain individuality.

---

## 12. What is now ruled against

The accumulated results argue against several simple explanations as general mechanisms:

- **persistent spatial ownership / partitioning** — not required, and dyad policy distance does not predict co-use vertical separation;
- **literal fixed route memory** — exact route shape changes with configuration and route identity is sensitive to absolute position;
- **a universal slow learning ramp** — unsupported in first-flight ontogeny;
- **only the immediately previous bout/session matters** — rejected in 2022 older-history analysis;
- **simple body-size matching** — unsupported in the existing four-panel body-mass programme;
- **a universal bat-wide policy axis** — contradicted by Miniopterus;
- **independent pulse/sensing identity after movement conditioning** — unsupported under cross-fitting.

---

## 13. What remains unresolved

The source of the persistent policy coordinates remains unidentified.

Live candidates:

- learned motor familiarity;
- long-term spatial/task memory;
- switching/search costs;
- stable biomechanics;
- physiology;
- developmental history;
- combinations of the above.

Public same-individual morphology data are insufficient to attribute the laboratory policy axes.

The decisive causal experiment is still a genuine repeated-individual task reset with:
- policy measured before reset;
- immediate post-reset behavior;
- subsequent repeated experience;
- morphology/performance measured independently.

History-dependent reuse predicts disruption followed by rapid re-stabilization.
Stable morphology predicts immediate transfer before new experience accumulates.

---

## Bottom line

The maintenance problem now has a much sharper empirical and mathematical answer:

> **individual specialization can be self-maintaining because individuality is carried by a persistent, low-dimensional personal movement policy and temporally persistent state, rather than by continued exclusion of conspecifics from space.**

A minimal self-reinforcement process is mathematically sufficient to generate specialization without reducing between-individual overlap.

And in wild *P. hastatus*, persistent policy differences are empirically **not** translated into greater dyad vertical separation during co-use.

So the central ecological distinction is now direct:

> **bats can differ in how they solve movement problems without having to differ in where they are allowed to be.**
