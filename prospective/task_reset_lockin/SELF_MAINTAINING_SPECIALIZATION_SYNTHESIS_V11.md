# Self-maintaining specialization synthesis v11

## Status

**CURRENT POST-JAE MECHANISM SYNTHESIS — supersedes V10.**

JAE v0.4.0 remains frozen.

V11 adds one final mechanistic layer:

> **the current evidence is consistent with history-dependent selection among multiple adequate movement solutions, but direct solution abundance is not measured in the existing public obstacle-flight archive.**

The programme therefore separates:
- empirical results already supported;
- a quantitative mechanism hypothesis;
- the single missing causal manipulation.

---

# 1. Four empirically separated stages

[
\boxed{
\text{formation}

\neq
\text{maintenance}

\neq
\text{expression}

\neq
\text{spatial consequence}
}
]

## Formation

Juvenile movement history becomes identity-specific through development.

Matched two-day histories:
- earliest two valid days -> late movement: unsupported;
- immediately recent two days -> much stronger personal prediction;
- recent-minus-early gain:
  - Q = **+144.08**
  - p = **0.0001**
  - 10/14 positive.

Thus later personal organization is not simply a fixed readout of the earliest observable independent movement.

## Maintenance

Adult *Rhinolophus nippon* carries a portable low-dimensional movement-policy coordinate.

Held-out task prediction:
- 2-D no-refit R² = **0.4666**
- p = **0.0002**

Pairwise policy geometry:
- vector R² = **0.5797**
- p = **0.0001**
- 97.1% positive direction agreement.

## Expression

Controlled sensory perturbation in *Pipistrellus kuhlii* shifts movement while retaining identity-bearing personal bias.

Baseline -> masker:
- K = **+4.941°**
- 5/6 positive
- exact p = **0.0403**

Foam no-masker -> foam + masker:
- K = **+6.779°**
- 5/5 positive
- exact p = **0.025**
- no-refit R² = **0.641**

Post-primary expression attenuation:
- K30 = **+8.004°**
- K10 = **+1.878°**
- difference exact p = **0.00278**

Thus context can alter how strongly personal information is expressed without necessarily erasing it.

## Spatial consequence

Wild *P. hastatus*:
- persistent H/V policy is individually repeatable;
- policy distance does not predict synchronous vertical separation.

Therefore persistent behavioral differentiation need not be stored as physical niche partition.

---

# 2. Portable individuality is not only speed/performance magnitude

A scale-free geometry-only diagnostic removes:

- elapsed time;
- speed;
- absolute path length;
- absolute vertical range;
- absolute spatial offset.

It retains only dimensionless/angular route organization.

Observed:
- K_geometry = **+0.38857**
- 5/5 positive
- p = **0.0153**

Thus portable individuality also exists in:
- relative displacement;
- route efficiency;
- turn geometry;
- vertical route shape.

This weakens a pure "some bats are simply faster / larger-scale movers" explanation.

---

# 3. The emerging internal mechanism

External bat biomechanics establishes that a bat can solve the same increased-load problem through different combinations of:

- wingbeat motion;
- wing conformation;
- camber;
- realized wing area;
- aerodynamic force coefficient.

The current ecological data independently show that personal movement organization is history-dependent and portable.

The proposed bridge is:

[
\boxed{
\text{multiple adequate solutions}
+
\text{personal history}
\rightarrow
\text{personal policy}
}
]

The environment defines a feasible solution repertoire.

Personal history progressively selects/refines one individual's region of that repertoire.

The resulting higher-level bias can transfer across tasks.

Current context then determines how that bias is expressed.

---

# 4. Quantitative solution-abundance theory

Use the symmetric reinforced-choice model:

[
P_i(k|n)=\frac{a+N_{ik}(n)}{Ka+n},
]

with K feasible solutions and identical initial state for all individuals.

Long-run personal solution weights:

[
\\theta_isim Dirichlet(a,dots,a).
]

The exact same-individual matching advantage over different individuals is:

[
\boxed{
\Delta(K,a)
=
\frac{K-1}{K(Ka+1)}
}
]

for K > 1.

Thus multiple feasible solutions are sufficient for individuality under history dependence.

But the theory gives a stronger prediction.

---

# 5. More solutions do not always mean more specialization

Under fixed **per-solution** baseline pseudo-count (a):

[
\frac{\partialDelta}{partial K}=0
]

at:

[
\boxed{
K^*=1+\sqrt{1+\frac{1}{a}}
}
]

so specialization is predicted to peak at an intermediate number of available solutions.

The logic is:

- K=1: no possibility of individual solution differentiation;
- moderate K: strong scope for personal lock-in;
- very large K: personal history is diluted across many alternatives.

However, if total exploration concentration:

[
A=Ka
]

is held fixed instead, then:

[
\Delta(K,A)
=
\frac{K-1}{K(A+1)},
]

which increases and saturates.

Therefore the general prediction is not:

> more opportunity -> more specialization.

It is:

[
\boxed{
\text{specialization depends on solution abundance relative to exploration budget}
}
]

This is experimentally testable.

---

# 6. Existing Teshima archive cannot test this directly

A dedicated public-source audit was performed.

Figshare article 29209493 contains:
- Env × Bat × trial CSV trajectories;
- kiku.pkl;
- yubi.pkl;
- no standalone obstacle/layout geometry file.

A structure-only 16-MiB pickle probe:
- executed no pickle code;
- decoded no numeric arrays;
- found no obstacle/layout/arena/geometry structural key candidate.

Verdict:

**STOP_NO_PUBLIC_OBSTACLE_GEOMETRY_SCHEMA**

Therefore do not estimate solution abundance from:
- observed route dispersion;
- route cluster count;
- trajectory number;
- VRNN error;
- policy dispersion.

Those are realized outcomes, not independent environmental solution sets.

This prevents a circular abundance -> specialization analysis.

---

# 7. What the loading literature contributes — and what it does not

The bat-loading experiment is strong **external mechanistic premise**:

- same species-level challenge;
- different individuals use different kinematic combinations;
- authors explicitly discuss functional redundancy and flat performance surfaces.

But the accessible supporting material does not expose the raw repeated 3-D wing-kinematic trial data needed for a new individual-level reanalysis.

Therefore use it as:
- evidence that bat flight can admit multiple adequate control solutions;

not as:
- a new batter confirmatory endpoint.

---

# 8. Revised causal architecture

A minimal dynamic representation is:

[
\\theta_i(t)
=
\\theta_i^{intrinsic}
+
h_i(t),
]

where:
- intrinsic = morphology / physiology / early developmental predisposition;
- h_i(t) = history-dependent personal refinement.

Let:

[
\mathcal S(E_t,M_i)
]

be the feasible movement-solution set under current environment and biomechanics.

Then:

[
\\theta_i(t+1)
=
U(
\\theta_i(t),
\mathcal S(E_t,M_i),
x_i(t),
r_i(t)
),
]

and realized behavior:

[
x_i(t)
=
G(
E_t,
M_i,
\alpha_{E_t}\\theta_i(t),
\lambda_{i,k},
m_{i,E}
)
+
epsilon.
]

The current evidence constrains:
- history-dependent refinement;
- portability;
- context-dependent expression;
- spatial non-necessity.

It does **not** identify U or directly measure (\mathcal S).

---

# 9. The decisive experiment is now more specific

Do not merely perturb task difficulty.

Manipulate **feasible solution abundance** while holding the task goal constant.

For the same identified bats:

### Narrow
One effective corridor / solution class.

### Moderate
Two to several similarly viable route/control solutions.

### Broad
Many viable alternatives.

Counterbalance order among individuals.

For each condition measure:

- own-history identity advantage;
- between-individual policy dispersion;
- trials-to-consolidation;
- within-individual exploration;
- persistence after delay;
- hysteresis after narrowing then reopening.

The key prediction is an abundance × exploration-budget interaction.

This is a stronger experiment than simply comparing easy versus hard environments.

---

# 10. Mechanistic novelty

Do not claim:
- discovery of motor degeneracy;
- first evidence of overlapping individual niches;
- first demonstration that experience shapes behavior.

Those are established.

The potential contribution is the empirical chain:

[
\boxed{
\text{history-dependent formation}
\rightarrow
\text{portable control individuality}
\rightarrow
\text{context-gated expression}
\rightarrow
\text{optional spatial partition}
}
]

combined with the mechanistic hypothesis:

[
\boxed{
\text{solution abundance}
\times
\text{history}
\rightarrow
\text{ecological individuality}
}
]

This connects motor-control abundance to individual-specialization ecology.

---

# 11. Programme stop rule

The current opened archives should not be mined further for a direct solution-abundance effect.

Specifically, do not:
- redefine K from realized routes;
- select environments by observed individual dispersion;
- use route clustering as an independent variable;
- infer obstacle opportunity from trial counts;
- keep rotating field behavior bases.

The next abundance result must come from:
- independently specified geometry;
- a designed manipulation;
- or a public dataset with explicit feasible-path constraints.

---

# Bottom line

The current programme no longer needs a story in which individuals remain specialized because they keep one another spatially separated.

A stronger mechanism is now plausible:

> **movement systems can admit several adequate solutions; personal history progressively individualizes solution use; the resulting policy becomes portable; current context gates its expression; and spatial partitioning is only an optional downstream outcome.**

The direct causal test that remains is not another repeatability analysis.

It is to manipulate the **solution repertoire itself**.
