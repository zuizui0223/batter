# External payoff triangulation — persistent bias × environmental constraint v1

## Status

**EXTERNAL ECOLOGICAL TRIANGULATION.**

This note uses published results only.
It is not a new batter reanalysis and does not modify JAE v0.4.0.

---

## 1. Bat sensory perturbation: changing behavior improves the sensory problem

Taub & Yovel (2020), *Pipistrellus kuhlii*.

Controlled manipulation:
- no masker;
- masker 30 cm behind target;
- masker 10 cm behind target;
- foam target / masker contrasts.

Published source result:
- bats reduce 3-D angle of attack when masking increases;
- the movement change reduces background echo intensity by approximately 4–6 dB;
- therefore movement changes the sensory signal-to-noise problem rather than merely changing trajectory geometry.

The batter prospective reanalysis independently shows:
- personal baseline movement bias remains identifiable through the perturbation;
- expression is attenuated in the stronger 10-cm context post-primary.

Thus the same system combines:
- persistent identity-bearing bias;
- environmentally useful movement plasticity.

---

## 2. Honeybee aperture experiment: persistent bias can incur a constraint mismatch cost

Ong et al. (2017), *Apis mellifera*.
DOI:
\`10.1371/journal.pone.0184343\`.

Experimental architecture:
- two side-by-side apertures;
- total opening width held at 10 cm;
- left/right widths varied:
  - 2/8;
  - 3/7;
  - 4/6;
  - 5/5;
  - mirrored asymmetrical conditions;
- 102 individually marked bees contributed repeated route choices.

Published result:
- population choice shifts toward the wider opening;
- individuals retain idiosyncratic left/right biases;
- Entry/Exit bias rankings are highly consistent;
- among filmed bees, transit time increases when a persistent personal bias directs the bee toward the narrower aperture.

Thus:

\[
\boxed{
\text{personal bias}
\times
\text{environmental asymmetry}
\rightarrow
\text{performance consequence}
}
\]

The same personal prior can be:
- behaviorally real;
- repeatable;
- neutral when options are symmetric;
- costly when it conflicts with current constraints.

---

## 3. Why this matters for the bat mechanism

The bat programme already establishes:

\[
\text{history-dependent formation}
\rightarrow
\text{portable personal bias}
\rightarrow
\text{context-dependent expression}.
\]

The honeybee result supplies an independent ecological example of why context-dependent expression matters:

> retaining a bias is not always free.

A flexible animal faces a trade-off between:
- reusing a familiar personal solution;
- adapting to current environmental opportunity.

---

## 4. Ecological interpretation

A persistent personal policy is best interpreted as a **reusable prior**.

Benefits can include:
- reduced search;
- reduced relearning;
- faster sensorimotor deployment;
- lower decision cost in recurrent environments.

Costs can include:
- mismatch with a changed environment;
- slower transit;
- extra maneuvering;
- lower sensory performance;
- switching/update cost.

Therefore persistence is not equivalent to universal adaptive optimality.

---

## 5. General payoff statement

Let:
- \(\theta_i\) = stored personal policy;
- \(G_e\theta_i\) = expressed personal component;
- \(H_e\theta_i\) = individual component favored by the current task;
- \(Q_e\) = performance curvature.

Expected personal-policy mismatch loss is:

\[
E[L_e^{id}]
=
tr\left[
Q_e
(G_e-H_e)
\Sigma_\theta
(G_e-H_e)^T
\right].
\]

Individuality is cheap when:
- feasible solutions are abundant;
- performance surfaces are flat;
- the stored bias aligns with current opportunity.

Individuality becomes costly when:
- environmental constraints narrow;
- the personal prior points away from the current optimum;
- switching is slow or costly.

---

## 6. Boundaries

Do not claim:
- honeybee handedness is homologous to bat movement policy;
- persistent bias is generally maladaptive;
- the bat masker reanalysis directly measures fitness;
- all context-dependent compression is caused by optimization.

The cross-taxon result is conceptual triangulation:

> persistent individual control biases can have environment-dependent performance consequences.

---

## Bottom line

The ecological significance of persistent individuality lies not only in whether the bias survives.

It lies in the balance:

\[
\boxed{
\text{reuse benefit}
-
\text{environmental mismatch cost}
-
\text{switching cost}
}
\]

This gives the policy framework an explicit performance/payoff layer.
