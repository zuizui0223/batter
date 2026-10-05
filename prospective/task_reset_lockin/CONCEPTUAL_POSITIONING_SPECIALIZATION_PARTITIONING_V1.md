# Conceptual positioning — specialization versus spatial partitioning v1

## Status

**LITERATURE-POSITIONING NOTE FOR POST-JAE SYNTHESIS.**

This note does not modify JAE v0.4.0 and makes no claim of conceptual priority where the literature already exists.

## 1. What is not new

Several relevant ideas are already established.

### Individual specialization is not equivalent to one definition of low overlap

Sargeant (2007) explicitly distinguished niche-width and niche-overlap concepts of individual specialization.

Therefore this programme should not claim to be the first to separate "specialization" from "overlap" conceptually.

Reference:
Sargeant BL. 2007. *Individual foraging specialization: niche width versus niche overlap*. Oikos 116:1431–1437. DOI 10.1111/j.0030-1299.2007.15833.x.

### Individual niches can overlap or be nested rather than occupy disjoint regions

Aikens et al. (2021) showed temporally consistent individual environmental niches in white storks that were predominantly nested along a specialist–generalist gradient rather than separated into disparate environmental regions.

Therefore "specialized individuals can overlap" is not itself a novel discovery.

Reference:
Aikens EO et al. 2021. *Individual environmental niches in mobile organisms*. Nature Communications. DOI 10.1038/s41467-021-24826-x.

### Behavioral type, plasticity and predictability are established variance components

Movement/personality methodology already distinguishes:
- individual mean / random intercept = behavioral type;
- individual environmental slope = behavioral plasticity / reaction norm;
- residual individual variance = predictability.

The post-JAE batter analyses therefore should not claim invention of this decomposition.

Reference:
Hertel AG et al. 2020. *A guide for studying among-individual behavioral variation from movement data in the wild*. Movement Ecology. DOI 10.1186/s40462-020-00216-8.

### Modern movement-based individualized-niche workflows already combine random effects, niche breadth and overlap

Takola (2026) provides an explicit workflow using mixed-effects resource-selection functions, random intercepts/slopes, repeatability, niche hypervolumes, breadth and pairwise overlap.

Therefore "quantifying individualized niches from movement" is not the contribution here.

Reference:
Takola E. 2026. *The individualized niche in motion: Quantifying individual specialisation with movement data*. Individual-based Ecology 2:e203247. DOI 10.3897/ibe.2.203247.

---

## 2. What the current programme does differently

The strongest distinction is not a new specialization index.

It is an empirical separation of three quantities that are often biologically linked but need not be equivalent:

[
\boxed{
\text{persistent individual policy}
\neq
\text{realized spatial segregation}
\neq
\text{active co-presence avoidance}
}
]

### Persistent individual policy

Does information carried by biological identity predict future movement behavior?

Evidence includes:
- held-out individual movement-policy identity;
- strict-past self-history prediction;
- peer-day residual identity;
- low-dimensional field H/V carrier.

### Realized spatial segregation

Do different individuals occupy separated parts of physical 3-D space?

Measured separately using:
- terrain-relative 3-D geometry;
- added segregation relative to fidelity.

### Active co-presence avoidance

Do individuals become more separated when they are locally present at the same time?

Measured separately using:
- fixed encounter sets;
- synchronous terrain-relative vertical separation;
- phase-shift nulls.

These are not treated as alternative estimators of one latent "specialization" quantity.

They are distinct ecological processes.

---

## 3. The strongest same-system result

In wild *Phyllostomus hastatus*:

### Policy persists

Bivariate H/V policy carrier:
- 2022: K = +0.65314, 32/34 positive, p=0.0001;
- 2023: K = +0.27052, 9/11 positive, p≈0.033.

Strictly prior allocation history predicts future allocation:
- 2022: K_past=+0.37266, p=0.0001;
- 2023: K_past=+0.27201, p=0.0258.

### Spatial partitioning is not the matching consequence

Pairwise persistent policy distance does not predict synchronous vertical separation:
- 2022: Spearman rho=+0.188, p=0.2743;
- 2023: rho=-0.190, p=0.6887.

Therefore the same individuals that differ persistently in movement policy are not ordered along a corresponding gradient of pairwise vertical segregation.

This is stronger than merely observing overlapping niches.

It directly tests the mapping:

[
D_{policy,ij}
\rightarrow
S_{space,ij}
]

and finds no positive relation in either year.

---

## 4. Why this matters relative to standard niche-partitioning stories

A common ecological interpretation of individual specialization is that differentiation reduces competitive similarity or niche overlap.

Examples in the literature explicitly frame individual specialization as:
- reducing overlap among competitors;
- facilitating coexistence;
- being strengthened by competition;
- producing differentiated space/resource use.

This is biologically plausible and empirically supported in many systems.

But it is not logically required.

The batter results identify another regime:

[
\boxed{
\text{persistent differentiation in behavioral solution}
+
\text{substantial shared physical space}
}
]

In this regime, the ecological object that remains individualized is not necessarily an exclusive resource volume.

It can be the **way a recurrent movement problem is solved**.

---

## 5. The important distinction from nested individualized niches

Nested environmental niches already demonstrate that individual niches need not occupy mutually disjoint environmental regions.

The batter result is different in two respects.

### A. Dynamic carrier rather than only realized environmental use

The persistent quantity is measured in movement-policy/history space and can transfer across task configurations in laboratory data.

It is therefore not merely a static hypervolume of environmental conditions used.

### B. Direct interaction-layer falsification

The programme separately tests whether the individual differences manifest as extra separation during actual local co-use.

Three of four JAE terrain/co-use panels lack that interaction-dependent separation, and persistent policy distance does not predict dyadic separation in the directly matched field system.

Thus overlap is not merely described.

The proposed maintenance mechanism based on continued spatial separation is directly challenged.

---

## 6. The strongest conceptual claim that remains defensible

Do **not** claim:

> Individual specialization can occur with overlap.

That is too old and too broad.

Prefer:

> **Persistent individual specialization in movement can be stored in behavioral policy rather than in persistent spatial partitioning: individuals can retain predictive, history-dependent differences in how they move even when those differences do not map onto greater pairwise separation in shared space.**

An even shorter version:

> **Specialization can persist in policy space without being maintained by partition of physical space.**

"Policy space" is descriptive shorthand for low-dimensional movement behavior, not a claim about a specific neural control policy.

---

## 7. What makes the evidence unusually strong

The argument is not based on one correlation.

It triangulates several independent contrasts:

1. individual history predicts future movement;
2. the signal survives coarse place/state matching;
3. terrain-relative strategy fidelity persists;
4. positive added spatial segregation is absent in the same panels;
5. active co-use separation is mostly absent;
6. persistent policy distance does not predict pairwise co-use separation;
7. laboratory movement identity transfers across changed obstacle geometry;
8. an independently fixed intensity-like axis transfers to *Carollia perspicillata*;
9. literal route geometry is more context-specific than the portable movement signal.

This supports a hierarchy in which persistent behavioral organization and realized spatial arrangement are separable.

---

## 8. Current mechanism ceiling

The post-JAE programme has also ruled against over-specification.

Supported strongly:
- persistent low-dimensional personal policy bias / behavioral type.

Not established as general field rules:
- one fixed personal-history centroid forecast;
- individual-specific linear peer-context slopes;
- stable individual policy breadth;
- one universal memory depth;
- one universal cross-species two-axis coordinate.

Therefore the mechanism should remain:

[
x_{iet}=F(E_e,\theta_i,m_{i,e})+\zeta_{iet}
]

rather than a fully parameterized universal law.

Here:
- (	heta_i) = persistent personal movement-policy bias;
- (m_{i,e}) = learned / scene-specific solution where such learning occurs;
- (E_e) = environment/task;
- (zeta) = unresolved flexible realization.

---

## 9. Publication-level positioning

### JAE v0.4.0

The existing paper should remain narrowly focused on:

> **persistent individual vertical strategies need not partition three-dimensional space.**

That result is self-contained and does not require the later policy programme.

### Post-JAE mechanism paper

The stronger second-paper question is:

> **Where is individual specialization stored when it is not stored in exclusive space?**

Current answer:

> **in a persistent low-dimensional movement-policy bias, expressed through context-dependent and learned realizations.**

The strongest second-paper evidence is the laboratory/field triangulation, not another new estimator.

---

## 10. References anchoring the boundary

- Sargeant BL. 2007. Individual foraging specialization: niche width versus niche overlap. *Oikos* 116:1431–1437.
- Schirmer A et al. 2019. Individuals in space: personality-dependent space use, movement and microhabitat use facilitate individual spatial niche specialization. *Oecologia* 189:647–660.
- Kerches-Rogeri P et al. 2020. Individual specialization in the use of space by frugivorous bats. *Journal of Animal Ecology*. DOI 10.1111/1365-2656.13339.
- Hertel AG et al. 2020. A guide for studying among-individual behavioral variation from movement data in the wild. *Movement Ecology*. DOI 10.1186/s40462-020-00216-8.
- Aikens EO et al. 2021. Individual environmental niches in mobile organisms. *Nature Communications*. DOI 10.1038/s41467-021-24826-x.
- Takola E. 2026. The individualized niche in motion: Quantifying individual specialisation with movement data. *Individual-based Ecology* 2:e203247.
