# Self-maintaining specialization synthesis v13

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V12.**

JAE v0.4.0 remains frozen.

V13 adds the ecological payoff layer.

The complete working architecture is now:

\[
\boxed{
\text{solution repertoire + history}
\rightarrow
\text{personal policy}
\xrightarrow{G_e}
\text{realized phenotype / niche}
\rightarrow
\text{performance}
}
\]

The central idea is no longer merely that specialization can persist without spatial partition.

It is:

> **an individual's movement strategy can be constructed through personal history, stored as a portable control bias, projected differently by current context, and carry environment-dependent benefits or mismatch costs.**

---

# 1. Formation — personal history individualizes the solution

Juvenile fruit-bat data:

- earliest two valid movement days do not robustly predict late personal movement:
  - E = **+15.19**
  - p = **0.1655**
  - 8/14 positive;

- recent two matched days strongly improve identity-specific prediction:
  - Q = **+144.08**
  - p = **0.0001**
  - 10/14 positive.

Thus adult-like personal organization is not simply a fixed readout already visible in the earliest independent movement.

Personal history substantially refines the individualized solution.

---

# 2. Maintenance — the individualized solution becomes portable

Adult *Rhinolophus nippon*:

- transparent 2-D policy identity:
  - K = **+0.554**
  - p = **0.0001**;

- held-out 2-D no-refit prediction:
  - R² = **0.4666**
  - p = **0.0002**;

- pair-displacement geometry:
  - R² = **0.5797**
  - p = **0.0001**;
  - 97.1% positive vector alignment.

Therefore the persistent object is a transferable behavioral coordinate, not just a task-local route.

---

# 3. Portable individuality is not only performance magnitude

Scale-free geometry-only identity survives removal of:

- speed;
- elapsed time;
- absolute spatial scale;
- absolute position.

Result:
- K = **+0.3886**
- 5/5 positive
- p = **0.0153**.

Thus personal organization includes relative route geometry and coordination.

---

# 3b. Cross-species boundary: intensity generalizes better than geometry

The scale-free geometry signature has a clear external boundary.

A fixed eight-feature Rhino geometry representation was transferred unchanged to an independent *Carollia perspicillata* 3-D navigation dataset.

The external null preserved:
- date block;
- source-native broad turn class;
- trial feature vectors.

Result:
- K = **-0.0350**
- 3/7 bats positive
- p = **0.2144**
- both date-block means negative.

Verdict:
**UNSUPPORTED_FIXED_GEOMETRY_EXTERNAL**

No fixed geometry family gives a coherent external carrier:
- G global route organization: K = **-0.0408**
- H horizontal maneuver geometry: K = **-0.0729**
- V vertical slope geometry: K = **+0.0343**

By contrast, the previously frozen Carollia external validation supports:
- fixed Rhino-derived I/M policy;
- especially the FlightIntensity component.

Therefore cross-species portability is not a universal geometry law.

The stronger current hierarchy is:

\[
\boxed{
\text{recurrent coarse movement-intensity individuality}
+
\text{system-specific coordinative geometry}
}
\]

This is useful for the functional-abundance hypothesis:
the specific coordinative solution selected by history can be species/task dependent even if a broader personal movement state recurs across systems.

Do not use the positive Rhino geometry result as a universal bat claim.

---

# 4. Expression — current context gates stored individuality

Controlled *Pipistrellus kuhlii* sensory perturbation:

### baseline -> masker
- K = **+4.941°**
- 5/6 positive
- exact p = **0.0403**

### foam/no-masker -> foam+masker
- K = **+6.779°**
- 5/5 positive
- exact p = **0.025**
- R² = **0.641**

Post-primary:
- K30 = **+8.004°**
- K10 = **+1.878°**
- ΔK exact p = **0.00278**.

Therefore environmental manipulation can:
- shift common behavior;
- change how strongly individuality is expressed;
- without necessarily erasing the stored personal signal.

---

# 5. Spatial niche is an environment-specific projection

Let:

\[
Var(\theta_i)=\Sigma_\theta.
\]

Realized phenotype:

\[
z_{i,e}
=
\mu_e
+
G_e\theta_i
+
\epsilon_{i,e}.
\]

Identity-attributable realized covariance:

\[
\Sigma_{z,e}^{id}
=
G_e\Sigma_\theta G_e^T.
\]

Thus:

\[
\Sigma_\theta\neq0
\]

does not imply strong spatial differentiation.

Environment can:
- attenuate;
- rotate;
- compress;
- hide

personal-policy dimensions.

This explains why policy distance need not map monotonically to physical-space distance.

---

# 6. Wild spatial consequence — partition remains optional

Wild *P. hastatus*:

- persistent H/V policy identity supported;
- policy distance does not predict synchronous vertical separation.

2022:
- rho = **+0.188**
- p = **0.274**

2023:
- rho = **-0.190**
- p = **0.689**

Therefore:

\[
\boxed{
\text{persistent personal policy}
\not\Rightarrow
\text{physical niche partition}
}
\]

Spatial partitioning is a downstream alignment outcome, not the storage mechanism.

---

# 7. Formation hypothesis — functional abundance

Bat flight biomechanics provides an external premise that the same mechanical task can be solved by different combinations of wing motion and wing shape.

The proposed internal mechanism is:

\[
\boxed{
\text{multiple adequate solutions}
+
\text{personal history}
\rightarrow
\text{personal policy}
}
\]

History breaks initial symmetry among functionally adequate alternatives.

The exact reinforced-choice model gives:

\[
\Delta(K,a)
=
\frac{K-1}{K(Ka+1)}.
\]

Thus K > 1 plus history dependence is sufficient for persistent individuality from initially exchangeable agents.

---

# 8. Solution abundance has a nontrivial prediction

Under fixed per-solution exploration mass:

\[
K^*
=
1+\sqrt{1+\frac{1}{a}}
\]

maximizes same-individual specialization advantage.

Under fixed total exploration budget:

\[
\Delta(K,A)
=
\frac{K-1}{K(A+1)}
\]

instead rises and saturates.

Therefore:

\[
\boxed{
\text{specialization depends on solution abundance relative to exploration budget}
}
\]

not simply on opportunity alone.

The current Teshima archive cannot test this directly because independent obstacle geometry is not publicly recoverable.

That route is explicitly stopped rather than approximated from realized trajectories.

---

# 9. Payoff — personal policy is a reusable prior, not guaranteed optimum

Let current expressed policy be:

\[
z_{i,e}
=
\mu_e+G_e\theta_i.
\]

Let the individual-specific task optimum be:

\[
z^*_{i,e}
=
\mu_e^*+H_e\theta_i.
\]

With quadratic performance curvature \(Q_e\), expected individuality-related mismatch loss is:

\[
\boxed{
E[L_e^{id}]
=
tr[
Q_e
(G_e-H_e)
\Sigma_\theta
(G_e-H_e)^T
].
}
\]

This formalizes when a persistent personal prior is:
- well matched;
- harmless;
- or costly.

---

# 10. Flat performance surfaces allow individuality cheaply

Functional abundance corresponds to directions of behavior space with weak performance curvature.

When eigenvalues of \(Q_e\) are small along individualized directions:

- different individuals can use different solutions;
- performance remains similar;
- strong individuality can persist without competitive exclusion.

This gives a direct payoff meaning to motor abundance.

Individual specialization can accumulate along **cheap directions of behavioral variation**.

---

# 11. Narrow constraints can compress expressed individuality

For a one-dimensional illustration:

\[
z_i=\mu_e+\alpha_e\theta_i.
\]

If the current task favors one common solution, individuality creates loss:

\[
q_e\alpha_e^2Var(\theta).
\]

Add a generic switching/history cost:

\[
\lambda_e(\alpha_e-1)^2.
\]

Then optimal expression gain is:

\[
\boxed{
\alpha_e^*
=
\frac{\lambda_e}
{q_eVar(\theta)+\lambda_e}.
}
\]

So:
- weak environmental penalty -> personal bias remains visible;
- stronger constraint -> expression compresses;
- nonzero switching/history cost -> individuality is not erased instantly.

This gives one possible mechanistic interpretation of context-gated expression.

The present data do not identify \(q_e\) or \(\lambda_e\).

---

# 12. External payoff triangulation

## Bat sensory system

The source masker experiment shows that changing angle of attack reduces background echo intensity and improves the sensory problem.

Thus plastic movement has a measurable functional consequence.

## Honeybee two-aperture system

Individually marked honeybees possess persistent left/right route-choice biases.

Aperture widths are manipulated while total gap width is held constant.

When a personal side bias directs a bee toward the narrower aperture, published transit times increase.

Thus:

\[
\boxed{
\text{personal bias}
\times
\text{current environmental constraint}
\rightarrow
\text{performance cost}
}
\]

is observed independently in another flying animal.

This is cross-taxon conceptual triangulation, not bat evidence.

---

# 13. The specialization trade-off

The maintenance of a personal policy can now be framed as:

\[
\boxed{
\text{reuse benefit}
-
\text{mismatch cost}
-
\text{switching/update cost}.
}
\]

Reuse can reduce:
- search;
- relearning;
- decision effort;
- sensorimotor uncertainty.

Mismatch can increase:
- transit time;
- correction cost;
- sensory error;
- failure risk.

Switching itself can be costly.

Persistent specialization is expected when the long-run benefit of reusing a personal solution exceeds the expected cost of being wrong when conditions change.

---

# 14. This changes the ecological interpretation

Do not equate individual specialization with:
- adaptive resource partition;
- optimized niche separation;
- stable superiority of one personal strategy.

A persistent individual strategy can be:
- beneficial in familiar conditions;
- neutral along flat-performance directions;
- costly after environmental change.

This makes individual specialization a problem of **stateful decision/control under recurrent environments**, not merely niche geometry.

---

# 15. Strongest unified mechanism

The current evidence and theory support:

\[
\boxed{
\text{solution repertoire}
+
\text{personal history}
\rightarrow
\theta_i
\xrightarrow{G_e}
z_{i,e}
\xrightarrow{Q_e}
\text{performance}
}
\]

where:

- solution repertoire controls what can be learned;
- history helps individualize the stored policy;
- \(G_e\) controls how the stored policy is expressed;
- \(Q_e\) controls how costly or beneficial that expression is;
- spatial niche is one component of \(z\), not the storage medium.

---

# 16. Decisive experiment

The next experiment should independently manipulate:

## Solution abundance
one route vs several adequate routes.

## Constraint/payoff curvature
broad safe corridors vs narrow high-penalty corridors.

## History
train, reset, and re-open previous solution sets.

For the same animals measure:
- personal-policy formation;
- consolidation;
- expression gain;
- performance cost;
- hysteresis;
- recovery;
- spatial overlap.

The decisive prediction is not merely that individuality changes.

It is that:

> **individuality should be strongest and cheapest where multiple solutions are viable, while strong constraints should suppress mismatched expression without necessarily deleting the stored personal state.**

---

# 17. Current evidence ceiling

Directly supported:
- history-specific developmental refinement;
- portable adult policy;
- scale-free geometry individuality;
- perturbation-resistant personal bias;
- context-sensitive expression;
- lack of required spatial partition.

Externally triangulated:
- multiple biomechanical solutions in bat flight;
- functional consequence of movement adjustment;
- bias × environmental constraint performance cost in honeybees.

Still untested directly:
- solution abundance causes more/less bat individuality;
- individual bat policy mismatch predicts fitness;
- \(G_e\), \(H_e\), \(Q_e\) are identifiable as universal low-dimensional operators.

---

# Bottom line

The strongest current ecological statement is:

> **Individual specialization is a reusable behavioral prior: personal history helps build it, repeated tasks preserve it, context controls how strongly it is expressed, and its value depends on whether that prior matches the current environment.**

Spatial partitioning is only one possible outcome of that process.

It is neither the necessary origin nor the necessary maintenance mechanism.
