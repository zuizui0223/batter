# Self-maintaining specialization synthesis v15

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V14.**

JAE v0.4.0 remains frozen.

V15 resolves the remaining geometry ambiguity.

The strongest current architecture is:

\[
\boxed{
\text{personal history}
\rightarrow
\text{portable empirical personal policy } \theta_i
\xrightarrow{G_e}
\text{environment-specific movement geometry}
\rightarrow
\text{optional spatial partition / payoff}
}
\]

The key new point is:

> **the personal coordinate transfers across tasks, but the mapping from that coordinate to detailed route geometry does not.**

---

# 1. Formation

Juvenile fruit-bat movement shows identity-specific refinement.

For late target days 11–20:

- earliest two valid personal-history days:
  - E = **+15.19**
  - p = **0.1655**
  - 8/14 positive
  - unsupported;

- recent two days minus earliest two:
  - Q = **+144.08**
  - p = **0.0001**
  - 10/14 positive
  - supported.

Thus later personal organization is not simply a fixed readout of the earliest observable independent movement.

Personal history materially refines the individualized solution.

---

# 2. Portable empirical policy

For adult *Rhinolophus nippon*:

\[
\theta_i=(I_i,M_i),
\]

with:
- I = FlightIntensity;
- M = ManeuveringExtent.

Transparent 2-D identity:
- K = **+0.55428**
- 5/5 positive
- p = **0.0001**.

Held-out no-refit 2-D prediction:
- R² = **0.4666**
- p = **0.0002**.

Held-out pair displacement geometry:
- R² = **0.5797**
- p = **0.0001**
- 97.1% positive vector direction agreement.

Thus the relative personal coordinate itself is portable across obstacle configurations.

---

# 3. Scale-free route geometry is also identity-bearing

After removing:
- time;
- speed;
- absolute path length;
- absolute vertical range;
- absolute spatial position,

scale-free geometry still carries identity:

- K = **+0.38857**
- 5/5 positive
- p = **0.0153**.

Geometry identity is visible in:
- global route organization;
- horizontal maneuver geometry.

Vertical-slope geometry alone is unsupported.

---

# 4. Geometry components are not independently identity-bearing modules

Family-only:
- G only: K = **+0.40777**, p = **0.0088**
- H only: K = **+0.29605**, p = **0.0089**

But cross-fitted residualization gives:

### H after training-estimated G
- K = **+0.06290**
- 3/5 positive
- p = **0.1064**
- unsupported.

### G after training-estimated H
- K = **+0.00604**
- 4/5 positive
- p = **0.4035**
- unsupported.

Thus G and H are better interpreted as two manifestations of a shared lower-dimensional movement organization than as independent identity modules.

---

# 5. Within an environment, I + M absorbs geometry identity

Remove FlightIntensity only:

- residual geometry K = **+0.30775**
- 5/5 positive
- p = **0.0029**.

Remove I + M jointly within environment:

- residual geometry K = **-0.01467**
- 1/5 positive
- p = **0.4509**.

Thus FlightIntensity alone is insufficient, but the transparent pair captures the identity-bearing geometry within a given task context.

This is an empirical compression result.

It is not proof that I/M is a causal internal controller.

---

# 6. But the I/M -> geometry map is environment specific

A stronger cross-fitted test estimates:
- movement scaling;
- geometry scaling;
- the linear I/M -> geometry relation

using the **other six environments only**, then applies that mapping unchanged to the held-out seventh environment.

Residual held-out geometry identity remains:

- K = **+0.20160**
- 5/5 positive
- p = **0.0156**.

Therefore:

\[
\boxed{
g_{i,e}
\neq
B\theta_i
\text{ with one universal fixed }B
}
\]

for the observed detailed geometry.

A better representation is:

\[
\boxed{
g_{i,e}
=
G_e\theta_i
+
\epsilon_{i,e},
}
\]

where \(G_e\) depends on the obstacle/task environment.

This is the strongest current mechanistic result from the geometry programme.

The personal coordinate transfers.

The detailed geometry expression map does not.

---

# 7. Causal-status boundary

The transparent I/M pair is an **empirical personal-policy coordinate**.

Important overlap:
- ManeuveringExtent includes path efficiency;
- ManeuveringExtent includes vertical range;
- the geometry feature set contains related observables.

Therefore:
- within-environment geometry compression into I/M can reflect a common latent state;
- or statistical redundancy among realized movement summaries.

The present archive does not distinguish those causal explanations.

Allowed:

> **multiple identity-bearing movement observables collapse onto a compact portable personal-policy representation, while their detailed geometry mapping is environment dependent.**

Not yet allowed:

> **I/M is the neural controller that causally generates route geometry.**

---

# 8. Cross-species hierarchy

The fixed Rhino scale-free geometry representation is unsupported in independent *Carollia perspicillata*:

- K = **-0.03504**
- 3/7 positive
- p = **0.2144**.

No leave-one-trial deletion rescues it.

But the earlier fixed Rhino-derived low-dimensional policy representation transfers better to Carollia, especially FlightIntensity.

For Miniopterus, even the coarse portable individual signal is unsupported.

Therefore:

\[
\boxed{
\text{portable individuality is hierarchical and heterogeneous}
}
\]

The best hierarchy is:

\[
\boxed{
\text{recurrent coarse personal state}
+
\text{system/task-specific realization}
}
\]

not one universal bat geometry law.

---

# 9. Expression under controlled perturbation

In *Pipistrellus kuhlii*:

Baseline -> masker:
- K = **+4.941°**
- 5/6 positive
- exact p = **0.0403**.

Foam no-masker -> foam + masker:
- K = **+6.779°**
- 5/5 positive
- exact p = **0.025**
- no-refit R² = **0.641**.

Post-primary attenuation:
- K30 = **+8.004°**
- K10 = **+1.878°**
- exact difference p = **0.00278**.

Thus environmental context can shift and compress expression without necessarily erasing the personal bias.

---

# 10. Wild spatial consequence

Wild *P. hastatus* retains a persistent H/V personal carrier, but policy distance does not predict synchronous vertical separation.

2022:
- rho = **+0.188**
- p = **0.274**.

2023:
- rho = **-0.190**
- p = **0.689**.

Therefore:

\[
\boxed{
\text{portable personal differentiation}
\not\Rightarrow
\text{physical niche partition}
}
\]

The realized niche is an environment-dependent projection of upstream personal information.

---

# 11. Formation hypothesis — functional abundance

The strongest remaining formation hypothesis is:

\[
\boxed{
\text{multiple adequate solutions}
\times
\text{personal history}
\rightarrow
\text{individualized policy}
}
\]

This is consistent with:
- motor-abundance theory;
- bat loading studies showing several adequate kinematic compensation strategies;
- juvenile history-dependent refinement.

But this concept is not itself novel:
2026 ecological-motor-abundance literature already explicitly connects multiple movement solutions, individuality, environmental constraints and learning history.

The potential ecological contribution here is narrower:

> **an individualized movement state can become portable across ecological tasks while its realized spatial niche remains context specific and need not partition from conspecifics.**

---

# 12. Exact abundance theory

With fixed total exploration mass A and K initially equivalent solutions:

\[
P_i(k|n)
=
\frac{A/K+N_{ik}(n)}
{A+n}.
\]

Then:

\[
\theta_i
\sim
\mathrm{Dirichlet}(A/K,\ldots,A/K)
\]

and:

\[
\boxed{
\Delta_K
=
\frac{K-1}{K(A+1)}
}
\]

for same-individual matching advantage over independent individuals.

Thus:
- K = 1 -> no solution-choice individuality;
- K > 1 plus history dependence -> persistent individuality becomes possible.

This remains a sufficient-mechanism theory, not an identified empirical bat model.

---

# 13. Direct solution abundance remains unmeasured

The Teshima public archive does not expose independent obstacle-layout geometry.

Verdict:

**STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA**

Therefore do not infer solution abundance from:
- route dispersion;
- route clusters;
- trial count;
- policy dispersion;
- model error.

The abundance hypothesis requires:
- new designed geometry;
- author-provided obstacle coordinates;
- or another public source with independently specified feasible paths.

---

# 14. Payoff remains a hypothesis layer

A persistent personal policy can act as a reusable prior.

Possible benefits:
- reduced search;
- reduced relearning;
- lower decision/sensorimotor uncertainty.

Possible costs:
- mismatch after environmental change;
- correction cost;
- switching/update cost.

The batter data do not directly estimate fitness or energetic payoff.

External systems provide conceptual triangulation only.

Do not label persistent policy universally adaptive.

---

# 15. Strongest current ecological principle

The full programme now supports:

\[
\boxed{
\text{formation}
\neq
\text{portable state}
\neq
\text{expression map}
\neq
\text{spatial niche}
\neq
\text{payoff}
}
\]

The novel ecological point is not merely that individuals differ.

It is:

> **personal movement information can persist at a level upstream of the realized spatial niche. The individual state can transfer across tasks even when the detailed geometry through which it is expressed changes with the environment.**

This directly explains why persistent specialization need not require persistent physical partitioning.

---

# 16. Decisive next experiment

The current archives have reached their causal ceiling.

The next experiment should measure the same individuals while independently manipulating:

1. **solution repertoire during formation**
   - one effective solution;
   - several adequate solutions;
   - reopen previous alternatives;

2. **expression environment after policy has formed**
   - obstacle geometry;
   - sensory information;
   - biomechanical constraint.

The decisive result would be:

\[
\theta_i \text{ remains predictive}
\]

while:

\[
G_e
\]

is experimentally changed enough to alter:
- route geometry;
- spatial overlap;
- performance.

That would convert the current empirical decomposition into a causal mechanism.

---

# Bottom line

The strongest current model is:

\[
\boxed{
\text{history}
\rightarrow
\text{portable personal policy}
\xrightarrow{G_e}
\text{task-specific movement geometry}
\rightarrow
\text{optional niche partition / payoff}
}
\]

The newest evidence shows that the personal coordinate is more portable than the detailed geometry through which it is expressed.
