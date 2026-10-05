# Post-JAE second-paper blueprint v1

## Working title

### Preferred

**Persistent movement policies decouple individual specialization from spatial partitioning**

### Alternatives

- **Individual specialization can persist upstream of spatial niche partitioning**
- **Movement-policy individuality persists without pairwise spatial partitioning**
- **Where individual specialization is stored: persistent movement policy beyond exclusive space**

Do not title the paper around PCA, dimensionality, personality or “unique flight styles.”

---

## 1. One biological question

> **What maintains individual specialization when individuals do not continuously occupy exclusive portions of physical space?**

This is not a method question.

It is a mechanism question about the storage of ecologically persistent individual differences.

---

## 2. Competing hypotheses

## H1 — partition-storage

Individual specialization is maintained primarily through stable external separation among individuals.

Mechanistic logic:

[
\text{different individual states}
\rightarrow
\text{different spatial niches}
\rightarrow
\text{continued reduced overlap / competition}
\rightarrow
\text{maintenance of specialization}.
]

Predictions:

1. persistent individual movement differences should map onto stronger pairwise spatial separation;
2. individuals with more different policies should separate more during local co-use;
3. route/spatial geometry should be at least as stable across contexts as the underlying movement signature;
4. contemporaneous co-presence should commonly add separation;
5. specialization should weaken when the spatial structure supporting the partition is removed.

---

## H2 — policy-storage

Individual specialization is maintained as persistent control information carried by the individual.

Mechanistic logic:

[
\text{persistent personal policy}
+
\text{current task/environment}
\rightarrow
\text{realized movement}.
]

Predictions:

1. individual movement policy should transfer across different physical configurations;
2. realized route geometry can change more strongly with context than the personal policy;
3. persistent policy distance need not predict pairwise spatial separation;
4. co-presence-dependent avoidance is not required;
5. learned task/scene solutions can be stored and later re-expressed after interruption.

The two hypotheses are not mutually exclusive in every system.

The paper asks which architecture is required to explain the recurrent empirical pattern.

---

## 3. Core empirical tests

# Test 1 — Does individual information live above literal route geometry?

### System

Laboratory *Rhinolophus nippon* obstacle-flight archive.

### Evidence

Full movement policy transfers across obstacle configurations:
- full 8-D K = **+0.94356**;
- 5/5 positive;
- p = **0.0001**.

Low-dimensional structure:
- PCA1 identity K = **+0.95785**, p = **0.0006**;
- transparent FlightIntensity K = **+0.49656**, p = **0.0003**;
- ManeuveringExtent K = **+0.23375**, p = **0.0027**;
- transparent 2-D K = **+0.55428**, p = **0.0001**;
- residual calibrated identity after removal of the 2-D span is unsupported.

### Environment-target transfer

Across seven target obstacle configurations:

- full movement policy broadly transfers in **6/7**;
- pulse policy in **5/7**;
- scale-free route geometry in only **3/7**.

### Interpretation

The persistent object is more portable than the exact geometry of its expression.

Supports H2.

---

# Test 2 — Does the representation recur outside the discovery system?

### Independent *Carollia perspicillata*

Fixed Rhino-derived transparent axes, no external refit:

- fixed 2-D K ≈ **+0.348**;
- 6/7 positive;
- p = **0.0007**.

FlightIntensity alone:
- K ≈ **+0.368**;
- p = **0.0014**.

Maneuver axis has weaker external value and no demonstrated incremental benefit beyond I.

### Negative boundaries

*Miniopterus fuliginosus*:
- full policy unsupported;
- fixed FlightIntensity unsupported;
- fixed Rhino PC1 unsupported;
- species-specific PCA1 unsupported.

Other external programmes stop structurally where public trajectory support is inadequate.

### Interpretation

A portable low-dimensional policy is a recurrent biological architecture, not a universal two-axis bat constant.

---

# Test 3 — Does a low-dimensional policy carrier exist in the wild?

### System

Free-ranging *Phyllostomus hastatus*.

Field-specific coordinate:

[
\boldsymbol\theta_i=(H_i,V_i)
]

where:
- H = horizontal movement intensity;
- V = vertical movement intensity.

### 2022

- K_2D = **+0.65314**;
- 32/34 positive;
- p = **0.0001**.

### 2023

- K_2D = **+0.27052**;
- 9/11 positive;
- p ≈ **0.033**.

### Variance decomposition

2022 equal-axis descriptive fractions:
- individual = **52.5%**;
- day = **17.3%**;
- residual = **30.1%**.

2023:
- individual = **33.6%**;
- day = **1.7%**;
- residual = **64.7%**.

The 2022 vertical-intensity component is particularly individual:
- individual fraction **73.4%**.

### Interpretation

The lab carrier is not merely an arena artifact.

Wild movement contains persistent low-dimensional individual structure, but its expression strength varies strongly through time/context.

---

# Test 4 — Does policy differentiation generate spatial partitioning?

This is the decisive same-system test.

For each *P. hastatus* dyad:

[
D^{policy}_{ij}
=
||\boldsymbol\theta_i-\boldsymbol\theta_j||.
]

Compare to observed synchronous terrain-relative vertical separation.

### 2022

- Spearman rho = **+0.188**;
- p = **0.2743**.

### 2023

- rho = **−0.190**;
- p = **0.6887**.

Therefore:

[
D^{policy}_{ij}
\not\rightarrow
S^{space}_{ij}.
]

More different policies do not identify the dyads that separate more in physical vertical space.

Supports H2 and directly falsifies the simplest H1 mapping.

---

# Test 5 — Is active current avoidance required?

JAE/post-freeze terrain-relative co-use analyses provide the interaction boundary.

Across four structurally evaluable original tropical panels:

- terrain-relative vertical-strategy fidelity persists in 4/4;
- positive terrain-relative added segregation in 0/4;
- synchronous co-use extra vertical separation supported in only 1/4;
- in the three unsupported panels, positive compatibility endpoints are roughly 1–2 m.

Therefore:

[
\text{persistent strategy}
\not\equiv
\text{active co-presence separation}.
]

This rejects ongoing traffic-like avoidance as the general maintenance mechanism.

---

## 4. Mechanism localization: what persists?

The simplest fixed-personality model is also too strong.

### Stable personal center

Supported:
- policy identity;
- peer-day residual identity;
- temporal self-history.

### One fixed past-history centroid as a forecast rule

Unsupported under the >=70% individual-consistency rule.

### Individual-specific peer-context linear slope

Unsupported:
- 2022 G_RN = −0.0634, p = 0.1163;
- 2023 G_RN = −0.0833, p = 0.1595.

### Stable individual policy breadth

Not established:
- 2022 primary p = 0.0899, 11/16 positive;
- 2023 structural stop.

Thus the persistent object is most defensibly:

> **a stable low-dimensional individual bias/prior, not a fully deterministic trajectory generator.**

---

## 5. Storage versus expression

The paper should explicitly distinguish:

[
\boxed{
\text{storage}
\neq
\text{expression}
\neq
\text{spatial segregation}
\neq
\text{active avoidance}
}
]

### Storage

Persistent control information carried by the individual.

### Expression

How it appears in the current environment/task.

### Spatial segregation

Whether realized trajectories occupy different physical space.

### Active avoidance

Whether current co-presence causes extra separation.

This four-way distinction is the conceptual center of the paper.

---

## 6. External causal triangulation

These are external perturbation anchors, not new confirmatory estimates.

### Barchi et al. 2013

*Eptesicus fuscus*:
- learned individual stereotyped routes;
- route retained across unfamiliar release points;
- familiar route retrieved after ~1 month;
- mirror reset produces new stable routes.

Inference:
**scene-specific route state is learned, stored and resettable.**

### Yamada/Ito et al. 2020

*Rhinolophus*:
- repeated obstacle experience changes speed/meandering/sensing;
- internal prospective re-analysis retains individual state overall after removing shared trial/condition shifts.

Inference:
**learning changes expression without necessarily erasing individual information.**

### Taub & Yovel 2021

*Pipistrellus kuhlii*:
- clutter-specific sensorimotor strategy acquired over weeks;
- expressed immediately when clutter returned after ~6 months away;
- partial transfer to enhanced clutter.

Inference:
**learned task-class control information can persist without continuous expression.**

A prospective individual-identity re-analysis was stopped before acoustic outcome opening because the source's 3 same + 2 enhanced stage-4 design allows only 12 condition-preserving identity permutations:

[
p_{min}=1/12=0.0833.
]

Do not turn this source into a weak post-hoc p-value.

---

## 7. Mechanistic model

Use one hierarchy only.

[
\boxed{
\mathbf x_{i,e,t}
=
F(
E_e,
\boldsymbol\theta_i,
\boldsymbol\lambda_{i,k(e)},
m_{i,e},
\eta_t
)
+
\epsilon_{i,e,t}
}
]

where:

- (oldsymbol\theta_i): portable personal movement-policy bias;
- (oldsymbol\lambda_{i,k}): learned task-class policy;
- (m_{i,e}): learned scene-specific solution;
- (E_e): physical environment/task geometry;
- (eta_t): shared temporal context;
- (epsilon): bout-level realization.

Do not claim every term is independently identified in one dataset.

The hierarchy is a synthesis constrained by complementary experiments.

---

## 8. Primary ecological conclusion

> **Persistent individual movement specialization can reside upstream of realized niche partitioning.**

More explicitly:

> **Animals can retain predictive differences in how they solve movement problems even when those differences do not map onto stronger pairwise separation in shared physical space.**

This is the paper's ecological answer.

---

## 9. Why it matters

Classical individual-niche reasoning often moves from:

[
\text{consistent behavioral differences}
\rightarrow
\text{different realized niches}
\rightarrow
\text{reduced competition}.
]

The current evidence shows that this chain is not obligatory.

A population can instead contain:

[
\text{different persistent movement policies}
+
\text{overlapping realized space}.
]

Consequences:

1. individual specialization can be underestimated if measured only as spatial segregation;
2. high spatial overlap does not imply behavioral exchangeability;
3. competition is not required to remain contemporaneously expressed for individual differences to persist;
4. conservation models based only on occupied space may miss persistent individual differences in how animals use the same space;
5. niche theory should distinguish **the state that stores specialization** from **the realized niche through which it is expressed**.

---

## 10. Figure architecture

### Figure 1 — Two competing maintenance hypotheses

Left:
partition-storage.

Right:
policy-storage.

Show distinct predictions for:
- policy transfer;
- route context dependence;
- policy–space coupling;
- co-use avoidance;
- reset/recall.

### Figure 2 — Portable personal policy

Rhinolophus:
- individual positions in I/M policy space;
- cross-configuration transfer;
- environment-by-environment identity visibility.

Include representation comparison:
- movement 6/7;
- pulse 5/7;
- geometry 3/7.

### Figure 3 — Wild policy carrier

P. hastatus:
- H/V personal centers;
- 2022 and 2023 carrier effect;
- variance decomposition.

### Figure 4 — The decisive decoupling

Dyad scatter:
- policy distance vs synchronous vertical separation;
- 2022;
- 2023.

Add panel-level terrain-relative fidelity vs segregation result compactly.

### Figure 5 — Storage–expression hierarchy

Schematic integrating:
- portable theta;
- task-class lambda;
- scene solution m;
- environment;
- realized route.

Overlay evidence source for each link.

---

## 11. Results order

Do not present results chronologically.

Use hypothesis order:

1. portable policy exists;
2. it is low dimensional and externally recurrent;
3. a corresponding low-dimensional carrier exists in free-ranging bats;
4. persistent policy difference does not map onto spatial separation;
5. active co-use avoidance is not required;
6. learned task/scene information can persist without continuous expression.

This order makes the ecology, not the analytical history, the story.

---

## 12. What stays out of the main paper

Move to Supplement or provenance:

- every failed external source preflight;
- detailed pipeline calibration history;
- superseded architecture classifiers;
- every intermediate policy-axis diagnostic;
- raw nats/fix estimator details beyond what is necessary;
- all GitHub workflow/debug history;
- most negative mechanistic branches.

Keep only negative results that directly discriminate H1 versus H2.

---

## 13. Claim ceiling

Do not claim:

- policy is purely learned;
- policy is purely morphological;
- competition never matters;
- spatial partitioning never occurs;
- all bats have the same 2-D policy;
- theta is a neural variable;
- all individual specialization is policy-based.

Allowed:

> **Spatial partitioning is not necessary to maintain the persistent movement individuality observed here.**

and:

> **The evidence is most consistent with persistent individual control information expressed through context-dependent movement solutions.**

---

## 14. Submission positioning

The paper is strongest as **behavioral ecology / movement ecology / individual specialization**, not as a statistical-method paper.

Likely audience:
- movement ecology;
- behavioral ecology;
- individual niche specialization;
- spatial ecology;
- animal personality/plasticity;
- cognitive ecology.

The broad novelty is the empirical failure of the assumed mapping:

[
\text{behavioral individuality}
\Rightarrow
\text{spatial niche partitioning}.
]

The mechanistic novelty is the storage–expression hierarchy.

---

## One-sentence paper

> **Individual bats carry persistent movement policies that can transfer across environments and remain predictive in the wild, yet policy differences do not predict pairwise spatial separation, showing that individual specialization can be maintained upstream of physical niche partitioning.**
