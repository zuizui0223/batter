# External task-reset causal triangulation v1

## Status

**EXTERNAL EVIDENCE SYNTHESIS. NO REANALYSIS OF UNAVAILABLE RAW DATA.**

This note triangulates the internal batter results with published repeated-individual perturbation experiments.

It does not modify JAE v0.4.0 and does not treat published qualitative results as if they were newly estimated outcomes.

---

## 1. Why this external evidence matters

The batter programme now distinguishes:

- a portable, low-dimensional individual movement policy;
- context-dependent realized routes;
- shared temporal environmental effects;
- spatial partitioning.

The remaining causal question is:

> Is the persistent personal policy itself an immutable performance constraint, or does experience construct part of the movement solution?

Two published obstacle-learning experiments provide useful perturbations.

---

## 2. Barchi et al. 2013 — scene-specific route memory under a true reset

Source:

Barchi, J. R., Knowles, J. M. & Simmons, J. A. (2013).
*Spatial memory and stereotypy of flight paths by big brown bats in cluttered surroundings*.
Journal of Experimental Biology 216:1053–1063.
DOI: `10.1242/jeb.073197`.

Species:
*Eptesicus fuscus*.

### Experiment TC1

Six bats were introduced to a novel cluttered flight room.

Published result:
- five of six developed sharply stereotyped individual flight tracks within the first three days;
- the sixth converged more slowly;
- each bat developed its own solution through the obstacle array.

### Multiple-release-point perturbation

After stable paths were learned, bats were released from unfamiliar points.

Published result:
- changing the initial view / release position did not disrupt the learned personal path;
- bats rapidly resumed their accustomed route.

This argues that the learned object is not a trivial launch trajectory.

### One-month reset experiment TC2

The same six bats returned after about one month.

Three bats encountered:
- the original obstacle configuration.

Three encountered:
- a mirror-image reconfiguration designed to change the globally efficient path while keeping clutter density broadly similar.

Published result:

**Same configuration**
- bats resumed paths similar to those learned previously.

**Mirror configuration**
- bats did not return to their old literal paths;
- they developed different stable paths;
- previous experience with the original scene initially impaired / delayed adaptation to the mirrored scene.

### Mechanistic implication

This experiment directly demonstrates that:

[
	ext{literal personal route}
]

is a learned, scene-dependent object.

It is retained over long intervals when the scene returns, but is reorganized when scene geometry changes.

Therefore stable morphology alone is insufficient to determine a literal path.

This does **not** show that the low-dimensional policy coordinates measured in batter are learned rather than morphological.

---

## 3. Yamada / Ito et al. 2020 — movement-control variables change with experience

Source:

Ito, K. et al. / Yamada et al. (2020).
*Modulation of acoustic navigation behaviour by spatial learning in the echolocating bat Rhinolophus ferrumequinum nippon*.
Scientific Reports.
DOI: `10.1038/s41598-020-67470-z`.

Species:
*Rhinolophus ferrumequinum nippon*.

Fourteen bats were divided between acoustically permeable and acoustically reflective obstacle conditions.

All bats were naïve to the obstacle environment.

Each individual repeatedly flew the same course 12 times.

Published changes with familiarity include:
- reduced path meandering;
- altered pulse emission;
- reduced pulse-direction shifts;
- strong flight-speed change in the acoustically permeable condition.

### Mechanistic implication

At least some variables closely related to the batter FlightIntensity / maneuvering feature set are plastic on the time scale of repeated spatial experience.

Therefore:

[
	ext{movement-policy feature value}

eq
	ext{immutable morphology only}.
]

Again, this does not establish that the stable **between-individual coordinate** is learned.

---

## 4. Joint interpretation with batter task-reset analyses

The batter *Rhinolophus nippon* analysis shows:

- literal route geometry is configuration dependent;
- a portable individual policy transfers across configurations;
- the dominant portable identity is approximately two-dimensional:
  - FlightIntensity;
  - ManeuveringExtent / ManeuverStructure.

The external experiments show:

- literal paths are learned and scene-specific;
- movement-control variables themselves can change with familiarity.

The combined architecture is therefore better written as a hierarchy:

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

- (	heta_i) = persistent personal policy / performance prior;
- (m_{i,e}) = learned scene-specific representation or solution;
- (E_e) = physical task geometry;
- (eta_t) = shared temporal context;
- (epsilon) = residual trial variation.

A useful local approximation is:

[
x_{iet}
approx
mu_e
+
Lambda	heta_i
+
G(m_{i,e})
+
eta_t
+
epsilon_{iet}.
]

---

## 5. Why this is better than the previous binary alternatives

### Pure morphology model

Prediction:
the same personal route/policy should transfer immediately and rigidly after a scene reset.

Problem:
mirror reconfiguration produces new stable routes, and repeated familiarity changes movement-control variables.

Therefore a pure immutable-route morphology model is inadequate.

### Pure route-memory model

Prediction:
individuality should be tied mainly to the learned literal path.

Problem:
batter detects portable policy identity across different obstacle configurations.

Therefore the persistent individual component lies above a literal path.

### Pure autonomous short-term reinforcement model

Prediction:
session-to-session personal deviations should remain temporally autocorrelated after removing contemporaneous shared context.

Problem:
peer-controlled and peer-day state autocorrelation is unsupported.

Therefore autonomous short-term state propagation is not currently supported.

### Hierarchical policy + learned scene solution

Prediction:
- stable individual tendencies transfer across tasks;
- exact routes reorganize with geometry;
- familiar scene-specific routes can return after long intervals;
- shared environment can move all individuals temporarily;
- individual identity need not cause spatial separation.

This is the architecture most consistent with the combined evidence.

---

## 6. Relation to specialization without partitioning

A bat can therefore be specialized at multiple levels.

### Persistent policy level

Individuals occupy different positions in a low-dimensional movement-policy space.

### Scene-solution level

Within the same physical scene, experience can build an individually stereotyped route.

### Spatial occupancy level

Those policy/solution differences need not generate persistent physical separation among conspecifics.

The P. hastatus dyad test directly supports the last separation:
persistent policy distance does not predict synchronous vertical separation.

---

## 7. What remains causally unresolved

The source of (	heta_i) itself remains unresolved.

It may contain:
- morphology;
- physiology;
- developmental history;
- long-term learned motor style;
- persistent memory;
- combinations.

The external reset experiments demonstrate learning of the scene-specific layer, not the causal origin of the portable policy prior.

A decisive new experiment must estimate both layers in the same individuals.

---

## 8. Decisive experimental design

For each individual:

1. estimate portable policy coordinates (	heta_i) across at least two baseline obstacle geometries;
2. train a stable scene-specific route in geometry A;
3. impose a geometry reset A -> B;
4. measure the **first post-reset flight before substantial relearning**;
5. repeat B until a new stable route forms;
6. restore A later;
7. measure morphology / wing loading / performance independently.

Predictions:

### Stable policy prior
Portable (	heta_i) should transfer immediately on the first B trial.

### Learned route layer
The A-specific route should fail under B and then re-stabilize with experience.

### Memory retrieval
Restoring A should recover the learned A solution faster than de novo acquisition.

### Mixed mechanism
Portable policy transfers immediately, while route geometry is relearned/retrieved.

This mixed outcome is now the strongest prior prediction.
