# Self-maintaining specialization synthesis v5

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V4.**

JAE v0.4.0 remains frozen.

The mechanism problem is now split into three distinct questions:

1. **What persists across contexts?**
2. **What is learned within a scene?**
3. **Does either persistent individuality or learned route structure require spatial partitioning from conspecifics?**

The current evidence supports different answers at these three levels.

---

## 1. Current hierarchical model

The most economical architecture is now:

[
oxed{
x_{iet}
=
F(
E_e,
	heta_i,
m_{i,e},
eta_t
)
+
epsilon_{iet}
}
]

where:

- (	heta_i) = persistent portable individual policy;
- (m_{i,e}) = learned scene-specific movement solution;
- (E_e) = physical task geometry / environment;
- (eta_t) = shared time-varying environmental context;
- (epsilon_{iet}) = residual trial-level variation.

The important point is that these objects are **not the same thing**.

A stable personal policy can persist while:
- literal routes change;
- shared environment shifts all individuals;
- conspecifics continue to overlap spatially.

---

## 2. Persistent object: a low-dimensional personal policy

### Rhinolophus nippon laboratory data

Portable individual movement identity survives changes in obstacle configuration.

The calibrated linear identity structure is approximately two-dimensional.

### Axis 1 — FlightIntensity

A transparent scalar:

[
I =
mean(
z_{mathrm{median speed}},
z_{mathrm{p90 speed}},
z_{mathrm{median |v_z|}},
z_{mathrm{p90 |v_z|}}
)
]

alone identifies held-out individuals:

- K = 0.49656;
- 5/5 positive;
- p = 0.0003.

The equivalent PCA1 direction is nearly invariant across leave-one-environment folds:

- minimum foldwise cosine = 0.9833;
- median = 0.9964.

A one-dimensional no-refit model predicts held-out pair differences:

- R² = 0.627;
- p = 0.0005;
- magnitude-calibration slope = 1.031;
- Pearson r = 0.555;
- sign accuracy = 82.9%.

Thus FlightIntensity behaves approximately as a portable individual parameter.

### Axis 2 — ManeuveringExtent / ManeuverStructure

One axis does not exhaust identity.

PC1 removal leaves residual identity:

- K = 0.38896;
- 5/5 positive;
- p ≈ 0.0031.

PC1+PC2 removal eliminates calibrated identity:

- K = 0.0570;
- p = 0.1553.

PC2 is stable:

- minimum foldwise cosine = 0.9709;
- median = 0.9923.

Its dominant signed loadings are:

- median horizontal turn rate: +0.610;
- p90 horizontal turn rate: +0.467;
- path efficiency: +0.375;
- vertical range: +0.455;
- median speed: −0.254.

Its median absolute cosine with FlightIntensity is only ≈0.112.

A transparent ManeuveringExtent proxy is supported:

- K = 0.23375;
- p = 0.0027.

Transparent two-axis identity:

- K = 0.55428;
- 5/5 positive;
- p = 0.0001.

After removing the transparent two-axis span:

- residual K = 0.08771;
- p = 0.0863.

Therefore:

[
oxed{
	heta_i approx (I_i,M_i)
}
]

is a useful biological coordinate system for this species/task.

---

## 3. Low-dimensional does not mean exact

One-dimensional policy is highly discriminative, but not the whole generator.

Rank-one held-out reconstruction of the complete 8-D movement-policy centroid:

- R² = 0.222;
- p = 0.0016.

Rank-two:

- R² = 0.328;
- p = 0.0002.

Thus:

[
x_{ie}
approx
mu_e
+
Lambda_2	heta_i
+
epsilon_{ie}
]

is a useful approximation, not an exact deterministic flight equation.

This resolves the earlier “pi” analogy:

> the flight trajectory itself is not a mathematical constant; it is an environment-dependent output generated from a low-dimensional personal policy plus context.

---

## 4. Scene-specific object: learned route solution

Independent published perturbation experiments establish a second layer above/below the portable policy.

### Eptesicus fuscus — Barchi et al. 2013

Six bats learned individually stereotyped paths in a novel cluttered scene.

Key causal perturbations:

#### Different release locations

After stable paths formed, changing the release point did **not** disrupt the learned route.

Therefore the learned path was not merely a launch-condition trajectory.

#### One-month retention

After about one month:
- bats returned to the same obstacle layout resumed their previously learned paths.

#### Mirror-image reset

Three bats instead encountered a mirror-image obstacle layout.

They:
- did not return to the old literal route;
- formed new stable paths;
- showed impaired/delayed adaptation relative to bats returned to the original scene.

Therefore:

[
oxed{
	ext{literal personal route is learned and scene-specific}
}
]

Stable morphology alone cannot specify an immutable literal route.

### Rhinolophus ferrumequinum nippon — spatial-learning experiment

Naïve bats repeatedly flew an obstacle course 12 times.

With familiarity:
- meandering decreased;
- speed changed;
- echolocation behavior changed.

Thus even movement-control quantities related to the portable policy feature set are behaviorally plastic.

---

## 5. Combined interpretation: stable prior × learned scene map

The internal and external evidence jointly reject both simple extremes.

### Pure fixed morphology / fixed route

Too rigid:
- mirror-reconfigured bats form new scene-specific routes;
- repeated experience changes movement dynamics.

### Pure literal route memory as the individual carrier

Too narrow:
- batter detects portable policy identity across different obstacle configurations.

### Best current model

[
oxed{
	ext{persistent personal policy prior}
+
	ext{learned scene-specific solution}
}
]

The portable policy biases **how** an individual solves movement problems.

The learned scene representation determines **how that policy is instantiated in a particular geometry**.

A bat can therefore preserve individuality without preserving the exact same route.

---

## 6. Wild-field policy survives shared temporal context

### P. hastatus fixed-bin 2-D carrier

Policy coordinates:

- H = horizontal movement intensity;
- V = vertical movement intensity.

Carrier support:

#### 2022
- K_2D = 0.65314;
- 32/34 positive;
- p = 0.0001.

#### 2023
- K_2D = 0.27052;
- 9/11 positive;
- p ≈ 0.033.

So repeated free-ranging movement contains an individual-specific low-dimensional carrier.

---

## 7. Shared environment, not autonomous short-term self-reinforcement, explains the apparent session-to-session state

Raw allocation-state autocorrelation was positive.

But after contemporaneous peer correction it disappears.

### ±12 h peer correction

2022:
- R_peer = −0.110;
- p = 0.134.

2023:
- R_peer = −0.0216;
- p ≈ 0.055.

### Exact peer-day correction

2022:
- R_peerday = −0.124;
- p = 0.174.

2023:
- R_peerday = −0.0216;
- p = 0.0527.

Thus:

[
oxed{
	ext{short-term deviation persistence is not robust after shared-context control}
}
]

The Pólya-type self-reinforcement process remains a mathematical sufficiency example, but it is **not** empirically identified as the actual field maintenance mechanism.

---

## 8. Stable individual component remains after removing shared day effects

Subtracting the contemporaneous peer/day tendency does not erase individual identity.

### 2022

- K_peerday = 0.16271;
- 28/34 positive;
- p = 0.0002.

### 2023

- K_peerday = 0.30102;
- 7/8 positive;
- p = 0.0153.

Therefore there is a stable individual component beyond common day-level movement shifts.

---

## 9. Early-to-late stability is strongest in the full two-dimensional field policy

The one-dimensional allocation contrast is too lossy after peer control.

### 1-D allocation contrast

2022:
- K = 0.07696;
- p = 0.0522.

2023:
- K = 0.20283;
- p = 0.1265.

Neither passes the frozen support rule.

### Peer-controlled 2-D (H,V) early → late

#### 2022

- K = 0.20192;
- 19/25 positive;
- p = 0.0004.

Supported.

Descriptive early-vs-late rank correlations:

Aj-cave:
- rho_H = 0.659;
- rho_V = 0.368.

La Gruta:
- rho_H = 0.531;
- rho_V = 0.266.

#### 2023

- K = 0.11921;
- 4/7 positive;
- p = 0.2473.

Unsupported.

Thus the strongest peer-controlled temporal evidence for a stable 2-D field policy comes from 2022.

The smaller 2023 panel preserves residual individual identity overall, but does not independently reproduce early-to-late 2-D stability.

---

## 10. Policy is not the realized spatial phenotype

Field policy similarity does not predict full centered vertical-distribution shape:

- 2022 p = 0.4548;
- 2023 p = 0.5627.

Therefore:

[
oxed{
	heta_i 
eq 	ext{realized spatial distribution}
}
]

The same personal policy can produce different spatial realizations under different contexts.

---

## 11. Direct field result: policy differentiation does not imply partitioning

Same wild P. hastatus dyads:

### 2022

[
ho(D_{policy},S_{couse})=0.188
]

- p = 0.2743.

### 2023

[
ho(D_{policy},S_{couse})=-0.190
]

- p = 0.6887.

No positive relationship in either year.

This is especially informative because 2023 shows elevated overall synchronous vertical separation relative to the phase-shift null.

Even then, persistent policy distance does not identify the dyads that separate most.

Therefore:

[
oxed{
	ext{policy differentiation}

eq
	ext{spatial partitioning}
}
]

directly in the same field system.

---

## 12. Revised ecological mechanism

The maintenance architecture is now:

[
oxed{
	heta_i
;;+;;
m_{i,e}
;;+;;
eta_t
longrightarrow
x_{iet}
}
]

where:

- (	heta_i): persistent personal policy;
- (m_{i,e}): learned scene-specific solution;
- (eta_t): shared temporal context;
- (x_{iet}): realized movement.

Individual specialization persists because (	heta_i) and learned scene solutions retain individual information across repeated behavior.

It does **not** require individuals to maintain exclusive portions of physical space.

---

## 13. What is now strongly disfavored

- persistent spatial partition as a necessary maintenance mechanism;
- literal immutable route as the personal carrier;
- pure one-step inertia;
- autonomous short-term self-reinforcement after peer control;
- one universal bat-wide policy axis;
- independent pulse identity after strict cross-fitted movement conditioning;
- simple body-mass matching as the general explanation.

---

## 14. What remains unresolved

The causal origin of portable (	heta_i) remains unknown.

It may include:
- morphology;
- physiology;
- developmental history;
- learned motor style;
- long-term memory;
- persistent skill;
- combinations.

The external reset literature shows that **scene-specific solutions are learned**.

It does not prove that the portable personal policy itself is learned.

---

## 15. Decisive next experiment

The strongest new prediction is now mixed.

For the same individual:

1. estimate portable (	heta_i) across several baseline tasks;
2. learn a scene-specific route (m_{i,A});
3. abruptly reset geometry A -> B;
4. measure the first B trial before meaningful relearning;
5. repeat B until stable;
6. restore A;
7. independently measure morphology/performance.

### Prediction

Immediately after reset:

[
	heta_i
]

should transfer more strongly than the literal learned route.

With repeated experience:

[
m_{i,B}
]

should stabilize.

On restoring A:

[
m_{i,A}
]

should be retrieved more rapidly than de novo learning.

This directly separates:
- portable policy;
- scene memory;
- new learning.

---

## Bottom line

The mechanism is no longer best phrased as:

> “past behavior simply reinforces itself.”

The stronger current conclusion is:

> **individual specialization can be maintained by a persistent, low-dimensional personal movement policy that is expressed through learned scene-specific solutions and changing shared environmental conditions.**

And critically:

> **persistent differences in how individuals solve movement problems do not require persistent differences in where they are allowed to be.**

That distinction — **policy specialization without spatial partitioning** — is now supported mathematically, in laboratory movement structure, and directly in wild dyads.
