# Self-maintaining specialization synthesis v4

## Status

**POST-JAE MECHANISM SYNTHESIS — supersedes V3.**

This document does not modify JAE v0.4.0.

The mechanism question is:

> How can individual specialization remain persistent when continued spatial partitioning among individuals is not required?

The newest peer-controlled analyses materially revise the answer. In particular, evidence for an autonomous short-term history state is **not robust** once contemporaneous conspecific variation is removed.

---

## 1. Current answer

The strongest empirical architecture is now:

[
oxed{
	ext{stable low-dimensional personal policy}
+
	ext{shared time-varying context}
+
	ext{residual variation}
ightarrow
	ext{realized movement}
}
]

with no requirement for persistent competitor-driven spatial segregation.

The persistent object is not:
- an exclusive territory;
- a fixed literal route;
- a one-step behavioral memory.

It is best described as an individual-specific movement-policy offset in a low-dimensional policy space.

The causal origin of that offset remains unresolved.

---

## 2. Mathematical sufficiency: specialization does not require partitioning

The frozen symmetric self-reinforcement model proves that a process can generate persistent individual specialization without between-individual repulsion.

For K feasible solutions:

[
P(A_{it}=kmid n_i(t))
=
rac{alpha+n_{ik}(t)}{Kalpha+t}.
]

At the asymptotic limit:

[
p_isim Dirichlet(alpha,ldots,alpha).
]

Expected within-individual concentration is:

[
E[H_i]
=
rac{alpha+1}{Kalpha+1}
>
rac1K.
]

Yet expected overlap of two independently reinforced individuals remains:

[
Eleft[sum_k p_{ik}p_{jk}ight]
=
rac1K.
]

The numerical verifier matched these expressions across the frozen K × alpha grid.

Therefore self-reinforcing history is **mathematically sufficient** to create specialization without partitioning.

It is not established as the causal mechanism in the bats.

---

## 3. Laboratory result: individuality is carried by policy rather than literal route

In *Rhinolophus nippon*, movement identity transfers across different obstacle configurations.

Literal 3-D route identity is sensitive to absolute route position and does not survive every route-shape control.

In contrast, configuration-conditioned movement policy transfers strongly.

The persistent object therefore lies above the level of a memorized geometric path.

A compact representation is:

[
x_{iet}
=
mu_e
+
Lambda	heta_i
+
epsilon_{iet},
]

where:
- (x_{iet}) = measured movement-policy features for individual i in environment e on trial t;
- (mu_e) = configuration effect;
- (	heta_i) = persistent personal-policy coordinates;
- (epsilon_{iet}) = remaining trial/context variation.

---

## 4. The laboratory policy is approximately two-dimensional

### Axis 1 — FlightIntensity

The first policy axis is highly stable across leave-one-environment folds.

Foldwise PC1 direction:
- minimum cosine = 0.9833;
- median cosine = 0.9964.

It aligns with the transparent scalar:

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

FlightIntensity alone:
- K = 0.49656;
- 5/5 bats positive;
- p = 0.0003.

A one-dimensional PCA score alone is sufficient for held-out identity:
- K = 0.95785;
- 5/5 positive;
- p = 0.0006.

A training-only identity axis gives:
- K = 0.88483;
- 5/5 positive;
- p = 0.0021.

The scalar is more than a classifier:
- no-refit held-out pair-difference R² = 0.627;
- p = 0.0005;
- pairwise calibration slope = 1.031;
- Pearson r = 0.555;
- pairwise sign accuracy = 82.9%.

Prediction errors concentrate among individuals close in the scalar:
- mean |Delta theta| correct = 0.934;
- mean |Delta theta| error = 0.557;
- permutation p = 0.0249.

Thus FlightIntensity behaves approximately as a transferable individual parameter.

### Axis 2 — ManeuveringExtent / ManeuverStructure

One axis is **not** the complete identity structure.

After training-PC1 removal:
- residual K = 0.38896;
- 5/5 positive;
- p ≈ 0.0031.

After PC1+PC2 removal:
- residual K = 0.0570;
- p = 0.1553.

PC2 is itself stable:
- minimum foldwise cosine = 0.9709;
- median = 0.9923.

Its dominant signed loadings are:
- median horizontal turn rate: +0.610;
- p90 turn rate: +0.467;
- path efficiency: +0.375;
- vertical range: +0.455;
- median speed: −0.254;
- other speed/vertical-speed terms small.

PC2 is nearly orthogonal to FlightIntensity:
- median absolute cosine ≈ 0.112.

A transparent ManeuveringExtent score is independently predictive:
- K = 0.23375;
- positive fraction = 0.80;
- p = 0.0027.

The transparent two-axis policy:
- K = 0.55428;
- 5/5 positive;
- p = 0.0001;
- recovers about 59% of full-8D identity K.

After removing the transparent two-axis span:
- residual K = 0.08771;
- p = 0.0863.

Thus the measured portable identity is approximately captured by two interpretable axes:

[
oxed{
	heta_i
approx
(I_i, M_i)
}
]

with:
- I = overall 3-D flight intensity;
- M = maneuvering / route-organization tendency.

---

## 5. Low-dimensional does not mean deterministic

Rank-one reconstruction of the held-out 8-D policy centroid is positive:

- R² = 0.222;
- p = 0.0016.

Rank-two reconstruction improves it:

- R² = 0.328;
- p = 0.0002.

Therefore the policy is genuinely low-dimensional, but the exact trajectory is not generated deterministically by one or two constants.

The appropriate analogy is not a mathematical constant such as pi.

It is a low-dimensional latent control state embedded in a context-dependent stochastic generator.

---

## 6. Generality is heterogeneous

The Rhino axis is not a universal bat-wide coordinate.

### Carollia perspicillata

Frozen external fixed-axis validation supports low-dimensional policy identity:
- fixed 2-D K ≈ 0.348;
- 6/7 positive;
- p = 0.0007.

The strongest recurring component is FlightIntensity.

### Miniopterus fuliginosus

Portable identity is unsupported under:
- full 8-D policy;
- Rhino-fixed PC1;
- transparent FlightIntensity;
- Miniopterus-specific PCA1.

Therefore:

> low-dimensional personal policy is a biological architecture that can occur, not a universal bat constant.

The orientation and strength of the policy manifold are species/task dependent.

---

## 7. Wild P. hastatus: a two-dimensional field policy carrier

A field-specific policy was constructed independently from:
- H = horizontal movement intensity;
- V = vertical movement intensity.

The fixed-bin 360-s 2-D carrier is supported in both years.

### 2022
- K_2D = 0.65314;
- 32/34 positive;
- p = 0.0001.

### 2023
- K_2D = 0.27052;
- 9/11 positive;
- p ≈ 0.033.

Thus repeated free-ranging movement contains a low-dimensional individual carrier.

The 1-D allocation contrast

[
A=(H-V)/sqrt2
]

is informative, but it is not the complete field policy and should not replace the 2-D result.

---

## 8. Shared temporal environment explains the apparent short-term state persistence

Raw within-individual allocation deviations showed positive temporal autocorrelation.

However, this does **not** survive contemporaneous conspecific controls.

### ±12 h peer correction

After subtracting an equal-individual mean of other bats observed within ±12 h:

2022:
- R_peer = −0.110;
- p = 0.134.

2023:
- R_peer = −0.0216;
- p ≈ 0.055.

No positive autonomous state persistence is supported.

### Exact peer-day correction

Using source-native calendar day and at least two peer individuals:

2022:
- R_peerday = −0.124;
- p = 0.174.

2023:
- R_peerday = −0.0216;
- p = 0.0527.

Thus the original short-gap autocorrelation can plausibly arise from environmental/time variation shared among bats.

The mechanism synthesis must **not** claim that a short-term personal state self-reinforces from one session to the next.

---

## 9. Stable individual identity remains after removing shared day effects

The disappearance of temporal autocorrelation does not erase individual identity.

After subtracting the contemporaneous peer/day allocation tendency, sessions still cluster by biological individual.

### 2022
- K_peerday = 0.16271;
- 28/34 positive;
- p = 0.0002.

### 2023
- K_peerday = 0.30102;
- 7/8 positive;
- p = 0.0153.

Therefore:

[
oxed{
	ext{stable individual component}

eq
	ext{shared day-level environmental component}
}
]

This is currently the strongest field evidence for an individual-specific policy offset.

---

## 10. Peer-controlled early-to-late stability is strongest in two dimensions

The transparent 1-D allocation contrast is not robust enough after peer correction.

### 1-D allocation early → late

2022:
- K = 0.07696;
- 18/25 positive;
- p = 0.0522.

2023:
- K = 0.20283;
- 5/7 positive;
- p = 0.1265.

Neither passes the frozen support rule.

### 2-D (H,V) early → late after ±12 h peer control

2022:
- K_2D = 0.20192;
- 19/25 positive;
- p = 0.0004;
- supported.

Within cohort descriptive early-vs-late rank correlations:
- Aj-cave: rho_H = 0.659, rho_V = 0.368;
- La Gruta: rho_H = 0.531, rho_V = 0.266.

2023:
- K_2D = 0.11921;
- 4/7 positive;
- p = 0.2473;
- unsupported.

Thus 2022 provides strong evidence that the **two-dimensional** individual policy persists from the early to late part of the record even after shared short-term context is removed.

The smaller 2023 panel does not independently reproduce this early-to-late result.

---

## 11. The field policy is not the complete spatial phenotype

Similarity in field (H,V) policy does not reliably predict similarity of the complete centered vertical-distribution shape.

- 2022 policy-to-shape p = 0.4548.
- 2023 p = 0.5627.

Therefore:

[
	ext{personal policy}

eq
	ext{realized spatial distribution}.
]

The policy acts as a latent control tendency whose observed spatial output remains context dependent.

---

## 12. Direct field test: policy differentiation does not produce spatial partitioning

For the same wild P. hastatus dyads, persistent policy distance was compared with the authoritative frozen terrain-relative vertical separation measured during synchronous local co-use.

### 2022

10/10 frozen dyads had policy coordinates.

[
ho(D_{policy},S_{couse})=0.188,
]

one-sided permutation:
- p = 0.2743.

No positive association.

### 2023

8/8 frozen dyads had policy coordinates.

[
ho(D_{policy},S_{couse})=-0.190,
]

one-sided permutation:
- p = 0.6887.

No positive association.

This is particularly informative because 2023 is the exceptional year in which overall synchronous vertical separation itself is elevated relative to its phase-shift null.

Even there, persistent policy distance does not order which dyads separate.

Thus the same field system directly supports:

[
oxed{
	ext{individual policy differentiation}

eq
	ext{spatial partitioning}
}
]

---

## 13. Revised maintenance architecture

The most economical empirical model is now:

[
oxed{
x_{it}
=
f(E_t,	heta_i)+epsilon_{it}
}
]

where:
- E_t = current/shared environmental context;
- theta_i = persistent low-dimensional individual policy;
- epsilon_it = residual trial-specific variation.

For the laboratory Rhino data:

[
	heta_iapprox(I_i,M_i).
]

For wild P. hastatus:

[
	heta_iapprox(H_i,V_i)
]

at the field-policy level.

The data support persistence of theta_i much more strongly than autonomous temporal persistence of session-level deviations around theta_i.

---

## 14. What the evidence now argues against

The accumulated results argue against:

- persistent spatial ownership as necessary maintenance;
- policy difference automatically becoming spatial separation;
- literal fixed-route memory as the stable carrier;
- a universal slow learning ramp;
- a purely one-step behavioral inertia mechanism;
- autonomous short-term state persistence after peer/time control;
- a universal bat-wide one-dimensional flight axis;
- independent pulse identity after strict cross-fitted movement/route conditioning;
- simple body-mass matching as the general explanation.

---

## 15. What remains unresolved

The causal origin of theta_i is still unidentified.

Live candidates:
- stable biomechanics;
- physiology;
- developmental history;
- learned motor familiarity;
- long-term task/spatial memory;
- switching or search costs;
- combinations of these.

The public archives do not support a defensible same-individual morphology crosswalk for the lab bats.

The randomized broad enriched-versus-impoverished early environment did not alter history-carrier strength.

Therefore none of:
- morphology;
- learning;
- development

has yet been isolated as the causal source.

---

## 16. Correct interpretation of the Pólya model

The Pólya process remains useful because it proves:

> history-dependent self-reinforcement can, in principle, produce specialization without partitioning.

But the peer-controlled field results mean it should **not** be presented as the empirically identified maintenance mechanism.

It is one member of the causal model class capable of generating the observed architecture.

The actual bats may instead possess a stable performance or developmental policy that is repeatedly expressed under changing environmental inputs.

---

## 17. Decisive next experiment

The remaining causal discrimination requires a genuine task reset or controlled perturbation in the **same individuals**.

Measure:
1. policy before perturbation;
2. immediate behavior under a new task/environment;
3. repeated behavior as experience accumulates;
4. morphology/performance independently.

Predictions:

### Stable morphology / physiology
Individual policy coordinates transfer immediately before meaningful new experience.

### Learned-history lock-in
Old policy correspondence is disrupted at the reset and individual policy re-stabilizes with repeated experience.

### Mixed mechanism
One axis transfers immediately while another re-forms.

That last outcome is now especially plausible given the empirically supported two-axis structure.

---

## Bottom line

The maintenance problem now has a sharper answer than “history keeps repeating itself.”

> **Individual specialization can persist because each animal carries a stable, low-dimensional movement policy that is repeatedly expressed through changing environmental contexts. That persistent policy does not require, and empirically does not map onto, continued spatial partitioning among conspecifics.**

In wild P. hastatus:
- shared temporal environment explains the apparent short-term state autocorrelation;
- individual identity remains after that shared component is removed;
- a peer-controlled two-dimensional policy remains early-to-late in the stronger 2022 panel;
- policy distance does not predict synchronous spatial separation.

So the key ecological distinction is now:

> **individuals can stably differ in how they solve movement problems without stably dividing the physical space among themselves.**
