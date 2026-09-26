# Manuscript spine v0.2 — cross-species replication

## Working title

**Individual specialization in three-dimensional airspace use is place-specific rather than altitude-wide**

Alternative:
**Bats repeat individual vertical routes across nights and landscapes**

## One-sentence claim

Repeated 3-D tracking shows that individual bats carry repeatable vertical signatures across
nights primarily through **place × vertical-state coupling**, rather than through a single
preferred flight height; this pattern persists relative to terrain in *Tadarida teniotis* and
replicates prospectively in an independent *Eidolon helvum* panel.

## Biological question

Individual specialization is usually drawn on a horizontal map: animals differ in where they
forage, commute or establish home ranges. Flying animals also choose a vertical coordinate.
Does individual specialization extend into this third spatial dimension? If it does, is the
repeatable property simply “how high this animal flies,” or is it a local rule linking particular
parts of the landscape to particular vertical layers?

## Study logic

The project began from a paradox in *T. teniotis*: the population was descriptively vertically
thick (~4.02 effective altitude states after x-y was known), yet a pooled
`P(z|x,y)` did not transfer to held-out individuals. Rather than treating that as absence of
vertical structure, we tested whether the failed population transfer arose because vertical
organization is individualized.

The decisive validation target is cross-night self-transfer:

`same individual on another night > other individuals`.

The primary inference unit is the individual, not the 30-s GPS fix.

## Focal species — *Tadarida teniotis*

### H1. Individuals repeat vertical use across nights

Supported. At 5-km horizontal conditioning, matched annotated data give MSL conditional
self-transfer of **+0.428 nats/fix**, with 5/6 evaluable individuals positive.

### H2. Individuality is a stable preferred altitude

Not supported as the general explanation. Marginal MSL identity gain is only **+0.052**.
For terrain-relative height, marginal AGL identity is **-0.255**.

### H3. Individuality resides in place × vertical-state coupling

Supported. At 5 km, identity × location increments are:

- MSL: **+0.376**
- AGL: **+0.591**

The AGL result is particularly diagnostic: an animal's overall height-above-ground distribution
does not transfer, but its location-conditioned AGL organization does.

### H4. The signal is repeated use of the same microtopography

Not supported at 5 km. Conditional terrain-elevation self-transfer is **+0.007**, compared with
+0.337 for AGL and +0.428 for MSL. At 2.5 km some terrain-route repeatability appears (+0.187),
but it remains much smaller than AGL/MSL vertical organization.

### H5. One repeatable vertical-wind reaction norm explains the routes

Not supported by the separately frozen mechanism endpoint. Only two repeat-tracked bats passed
the predeclared within-session variation gate for `W.Component`; their cross-night slope results
conflicted and the permutation p-value was 0.334. The gate was not retuned.

### H6. The signature is only a shared night-specific environmental state

Not supported as the general explanation. The same bat on another night was compared directly
against other bats tracked during the target calendar night.

- AGL self-vs-same-night gain: **+0.484**, 4/5 individuals positive
- MSL self-vs-same-night gain: **+0.436**, 4/5 positive

Thus contemporaneous nightly context does not erase the cross-night individual signature.

## Prospectively frozen independent replication — *Eidolon helvum*

The second species was selected through an outcome-blind repository and structural screen.
Before numeric height values were opened, the archive provided 18,154 GPS records from 63
individuals, including 42 with at least two >=50-fix sessions. The native vertical field is
`height_above_ellipsoid`.

To avoid geographic or annual identity masquerading as individual identity, all other-individual
baselines were restricted to the exact same **study site × year** cohort. The 5-km pass rule was
frozen before height outcomes.

### H7. The conditional-over-marginal identity pattern replicates in a second bat species

**Supported under every frozen criterion.**

At 5 km:

- evaluable individuals: **20**
- conditional identity gain: **+0.219 nats/fix**
- positive individual means: **17/20 (85%)**
- marginal-height identity gain: **+0.002**
- identity × location increment: **+0.217**
- median individual conditional gain: **+0.156**

Every site-year cohort with an evaluable individual had a positive cohort-mean conditional gain.
The pattern also remained positive in the frozen 2.5-km and 10-km scale checks.

This is the crucial replication: a second species reproduces the result that individual
information lies mainly in **where a vertical layer is used**, not in a bat-wide preferred
height.

### H8. The result is an artefact of pooling all other bats
Not supported. A post-primary pairwise fingerprint test compared the same bat directly against
each alternative individual.

- *Tadarida* AGL: conditional self-win fraction **0.736** versus marginal-height **0.500**;
- *Tadarida* MSL: **0.776** versus **0.494**;
- *Eidolon*: **0.875** versus **0.694**.

Mean conditional pairwise gains were +0.611, +0.643 and +0.398 nats/fix respectively, and the
conditional-minus-marginal increments were positive. Thus the signature survives removal of the
pooled-population baseline.

## Ecological interpretation

The population-level vertical niche should not always be interpreted as one shared 3-D
probability surface. In these data it is partly an overlay of **individual-specific local
vertical routes**. Pairwise comparisons show that these routes act as a cross-night statistical
**vertical fingerprint**: the same individual usually outpredicts alternative bats when place
and height are considered jointly.

The inference is stronger than simple route fidelity. In the focal species, the signature
survives conversion to height above ground and is much larger than terrain-elevation transfer.
It is also stronger than a contemporaneous other-bat baseline on the same night.

The independent fruit-bat panel then reproduces the conditional-over-marginal signature across
several African site-year contexts. Previous work on *E. helvum* has documented strong variation
among individual movements and fidelity to foraging areas; the present result adds a third
spatial dimension to that individual-level organization.

The mechanism is deliberately left open. Different individuals could achieve repeatable 3-D
routes through route memory, resource geography, topographic flow, wind exploitation, sensory
rules or combinations of these. The failed common uplift-reaction endpoint argues against
collapsing all individuals onto one wind-response mechanism.

## Exploratory comparative prediction: specialization has a spatial grain

The two species differ descriptively in scale profile.

- *T. teniotis*: strong at 2.5 km, weaker at 5 km, approximately absent by 10 km.
- *E. helvum*: positive at 2.5, 5 and 10 km.

With only two species this is **not** a comparative trait result. It motivates a new prediction:
the horizontal grain at which vertical individuality is expressed may scale with movement
ecology, landscape use or flight mode.

## Figures

### Figure 1 — The individual-vertical-specialization problem
Conceptual diagram showing why a pooled thick 3-D niche can fail between individuals yet repeat
within individuals. Show marginal height versus place-conditioned vertical rules.

### Figure 2 — Focal-species cross-night self-transfer
Per-individual *Tadarida* gains for MSL and AGL at 5 km, with paired identities and zero line.

### Figure 3 — Where identity information lives
Terrain, AGL and MSL decomposition into marginal identity and identity × location. Main visual:
terrain near zero; AGL/MSL interaction dominated.

### Figure 4 — Shared-night control
Self-on-another-night versus contemporaneous-other-bat prediction for AGL/MSL.

### Figure 5 — Independent replication
Per-individual *Eidolon* conditional and marginal gains, grouped by site-year. Highlight
17/20 conditional-positive individuals and near-zero marginal mean.

### Figure 6 — Spatial grain
2.5/5/10-km conditional identity profiles for the two species, explicitly labelled exploratory
because vertical semantics and movement ecology differ.

## Main limitations

- focal species: eight individuals and one to three tracked sessions each;
- independent species uses ellipsoid height, not AGL;
- observation schedules and vertical reference systems differ across species;
- no validated common foraging-state classifier, so the central claim concerns flight/airspace use;
- observational repeatability does not establish personality, learning or causation;
- the wind-response mechanism test has limited cross-night estimability;
- cross-species spatial-grain interpretation is hypothesis-generating with two species.

## Current paper-level conclusion

> **Individual specialization in bat airspace is not adequately described by a preferred flight
> altitude. Across a focal 3-D tracking study and a prospectively frozen independent species,
> individual identity is expressed mainly through repeatable coupling between horizontal place
> and vertical state.**

## Next data priority

Do not retune the completed *Tadarida* or *Eidolon* endpoints. The highest-value next extension is
a broader independent multi-species panel with repeated nights and explicit terrain-relative
height, allowing the spatial grain of vertical specialization to become a comparative ecological
trait rather than an exploratory two-species observation.
