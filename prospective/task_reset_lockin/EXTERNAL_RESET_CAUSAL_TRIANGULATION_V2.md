# External task-reset causal triangulation v2

## Status

**CURRENT EXTERNAL CAUSAL TRIANGULATION — supersedes V1.**

This document integrates:
- internal `batter` post-JAE policy results;
- Barchi et al. 2013 scene-reset evidence;
- Yamada/Ito et al. 2020 repeated-learning evidence;
- Taub & Yovel 2021 long-term clutter-policy recall.

It does not modify JAE v0.4.0.

Published perturbation results are used as external evidence, not relabelled as new confirmatory estimates.

A separate prospective re-analysis of the Taub–Yovel public archive was stopped before acoustic outcome opening because an individual-identity recall permutation test is not identifiable at the conventional 0.05 level under the source's mixed stage-4 environment assignment.

---

## 1. The mechanism problem now has three timescales

The post-JAE programme establishes a persistent low-dimensional personal movement-policy bias, but the realized behavior is strongly context dependent.

The external perturbation literature now separates three candidate persistent objects:

1. **portable personal policy bias**
   - survives changes among task geometries;
   - strongest internal example: *Rhinolophus nippon* cross-configuration movement policy;

2. **learned task-class policy**
   - can be acquired through repeated exposure;
   - can remain latent while the task is absent;
   - can be recalled when the task class returns;
   - strongest external example: *Pipistrellus kuhlii* clutter sensorimotor strategy;

3. **learned scene-specific solution**
   - a particular route/trajectory solution tied to a geometry;
   - can be retained and retrieved in the familiar scene;
   - can break and reorganize after a geometric reset;
   - strongest external example: *Eptesicus fuscus* obstacle routes.

These layers are not synonyms.

---

## 2. Portable personal policy — Teshima / batter

In *Rhinolophus nippon*, held-out individual movement identity transfers across seven obstacle configurations.

Key internal results:
- full 8-D policy identity: `K = +0.94356`, 5/5 positive, `p=0.0001`;
- one training-only latent dimension is sufficient for individual identification;
- transparent FlightIntensity: `K=+0.49656`, `p=0.0003`;
- ManeuveringExtent adds a second interpretable within-species dimension;
- calibrated identity after removing the transparent two-axis span is unsupported.

Thus a persistent personal component exists above the level of one literal route.

The best local object is:

[
\boldsymbol\theta_i
]

a persistent low-dimensional individual policy bias.

It need not specify one exact trajectory.

---

## 3. Learning changes the operating state — Yamada/Ito 2020

Naive *Rhinolophus ferrumequinum nippon* repeatedly traversed obstacle environments.

Published and prospectively re-analysed evidence shows:
- movement behavior changes with familiarity;
- population mean speed and meandering can shift;
- after condition × trial normalization, individual state information remains overall across trial 1 to trial 12.

Thus:

[
\text{learning-induced state shift}
\not\Rightarrow
\text{erasure of all individual information}.
]

But condition-level persistence is heterogeneous.

This argues against treating (oldsymbol\theta_i) as an immutable raw behavioral value.

A portable individual prior can coexist with learning-dependent expression.

---

## 4. Scene-specific route memory — Barchi et al. 2013

In *Eptesicus fuscus*:

- bats developed individual stereotyped paths in a novel cluttered room;
- changing release position did not erase the learned path;
- after about one month, bats returned to the original geometry resumed familiar routes;
- mirror-reconfigured obstacles forced formation of new stable routes and initially impaired adaptation.

This identifies a learned object that is:
- more abstract than launch position;
- persistent across a long interval;
- tied to scene geometry;
- replaceable when the scene is genuinely reset.

Denote it:

[
m_{i,e},
]

the learned scene-specific movement solution for individual (i) in environment (e).

This layer cannot be reduced to fixed morphology because the same animal can acquire a new route after the geometry changes.

---

## 5. Long-lived task-class policy recall — Taub & Yovel 2021

Five adult *Pipistrellus kuhlii* experienced a prolonged clutter-learning protocol:

1. large, relatively open room;
2. first long clutter exposure;
3. approximately six months back in the large room;
4. return to clutter.

The published experiment reports:
- progressive acquisition of a clutter-specific sensorimotor strategy during the first exposure;
- immediate expression of the learned strategy when clutter returned after the six-month interruption;
- transfer in a subset to an acoustically enhanced clutter environment.

The key biological implication differs from Barchi.

Barchi demonstrates memory for a **specific learned route/scene solution**.

Taub & Yovel demonstrate persistence of a learned **task-class sensorimotor strategy** across an extended period in which that strategy did not need to be continuously expressed.

Denote this intermediate learned state:

[
\boldsymbol\lambda_{i,k},
]

where (k) is a recurring task class such as clutter navigation.

This state may influence sensing/motor planning while allowing multiple concrete spatial routes.

---

## 6. Why the new Taub prospective re-analysis stopped

A new public-data programme was opened outcome-blind to ask a stronger question:

> does each bat's stage-4 state specifically recall its own late stage-2 learned state better than other bats' learned states?

Schema-only opening established:
- five reproducible biological individuals;
- five individual call tables;
- explicit IPI and duration fields;
- source structural fields for the six-month boundary and new-box assignment.

However the source stage-4 design assigns:
- 3 bats to the same clutter chamber;
- 2 bats to an enhanced/new-box clutter condition.

A valid identity permutation must preserve this stage-4 environment assignment.

The exact condition-preserving permutation space is therefore:

[
3!\times2! = 12.
]

The smallest attainable exact one-sided probability is:

[
p_{min}=1/12=0.08333.
]

Therefore a `p<=0.05` confirmatory individual-identity recall test is mathematically unattainable under the public design.

The programme was stopped before IPI outcome opening.

This is an inferential identifiability limit, not evidence against recall.

The published perturbation result remains valuable external causal evidence.

---

## 7. Revised hierarchy

The combined evidence now supports a more explicit hierarchy:

[
\boxed{
x_{iet}
=
F(
E_e,
\boldsymbol\theta_i,
\boldsymbol\lambda_{i,k(e)},
m_{i,e},
\eta_t
)
+
\epsilon_{iet}
}
]

where:

### (oldsymbol\theta_i) — portable personal policy bias

Persistent individual movement tendency that can transfer across multiple task geometries.

Evidence:
- Teshima/batter cross-configuration identity;
- external *Carollia* fixed-axis validation;
- wild low-dimensional field carrier.

### (oldsymbol\lambda_{i,k}) — learned task-class policy

A learned strategy relevant to a recurring class of movement problem.

Evidence:
- long-term clutter-strategy recall after six months in Taub & Yovel;
- partial transfer to enhanced clutter.

This is an external-evidence layer; an independent individual-identity estimate is not recovered from the current public design.

### (m_{i,e}) — learned scene-specific solution

Environment-specific route/lane/solution memory.

Evidence:
- Barchi route stereotypy;
- long-term return in the original scene;
- route replacement after mirror reset.

### (E_e) — current physical geometry / task

Constrains the available solution space.

### (eta_t) — shared time-varying context

Weather, resource state, motivation, social context or other shared temporal forcing.

### (epsilon_{iet}) — unresolved bout-level realization

The wild archive shows that this residual expression is substantial and is not well captured by:
- one fixed history centroid;
- one individual peer-context slope;
- one confirmed stable personal breadth.

---

## 8. What this hierarchy explains

### Why individuality can survive environmental change

(oldsymbol\theta_i) can transfer even when (m_{i,e}) changes.

### Why learning changes behavior without erasing individuality

Learning alters (oldsymbol\lambda) and/or (m), while a persistent (oldsymbol\theta_i) remains informative.

### Why familiar behavior can reappear after months without use

A learned task-class or scene state can be stored and later retrieved without continuous behavioral expression.

### Why exact routes can break after a reset

The scene-specific term (m_{i,e}) is conditional on geometry.

### Why specialization need not imply spatial partitioning

Neither (oldsymbol\theta_i) nor (oldsymbol\lambda_{i,k}) requires exclusive occupation of physical space.

Several individuals can carry different persistent control biases or learned policies while using overlapping spatial volumes.

---

## 9. What is now disfavored

### Persistent exclusive niche as the storage medium

Not required by JAE terrain/co-use results or wild policy-distance/separation tests.

### One immutable literal route

Contradicted by scene reset and relearning evidence.

### One immutable raw personality value

Learning shifts movement-control variables, and field realization contains large within-individual variation.

### Pure one-step behavioral inertia

Older-history support in 2022 and long-delay external recall make immediate carryover insufficient as a general explanation.

### One universal individual reaction slope

The held-out peer-context reaction-norm test is unsupported in both wild years.

---

## 10. The strongest causal interpretation now available

The evidence does not identify the origin of the portable personal bias (oldsymbol\theta_i).

But it does establish that learned movement organization can persist at levels more abstract than an immediately repeated path.

The strongest bounded interpretation is:

> **Individual movement specialization can be carried by a hierarchy of persistent control information: a portable personal bias, learned task-class strategies, and learned scene-specific solutions. None requires continuous spatial exclusion from conspecifics.**

This is stronger and more mechanistically explicit than simply saying that individuals overlap.

---

## 11. The decisive experiment is now obvious

A single within-individual factorial experiment could identify the hierarchy.

For the same animals:

1. estimate portable policy bias across several baseline geometries;
2. train a recurring task class in scene A;
3. leave the task unused for a substantial interval;
4. reintroduce the same task in:
   - scene A;
   - a modified scene B;
5. include a true geometric reset;
6. independently perturb biomechanics where ethically feasible;
7. restore baseline conditions.

Measure separately:
- immediate transfer of (oldsymbol\theta_i);
- recall of task-class (oldsymbol\lambda_{i,k});
- retrieval/relearning of scene-specific (m_{i,e});
- changes in actual spatial overlap.

Predictions:

- portable bias transfers immediately;
- learned task policy reappears after interruption;
- literal route depends on scene and can be rebuilt;
- none of these necessarily predicts stronger spatial segregation.

This experiment would finally separate persistent intrinsic control, learned generalized strategy, and learned local route within the same identified individuals.
