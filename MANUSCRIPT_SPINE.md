# Manuscript spine v0.3 — architectures of 3-D individual specialization

## Working title

**Individual specialization in three-dimensional airspace has multiple spatial architectures**

Alternative:
**Bat vertical individuality is encoded by altitude preferences and place-specific routes**

## One-sentence claim

Across four bat taxa, repeated 3-D tracking reveals cross-night individual vertical signatures,
but the signature is not encoded in one universal way: some systems are dominated by
place-specific vertical routing whereas another independent panel is dominated by an
animal-wide altitude distribution, and the architecture can change across temporal contexts
within a species.

## Biological question

Individual specialization is usually described by horizontal home ranges, sites or resources.
Flying animals additionally occupy a vertical axis. Does individuality extend into vertical
airspace, and if so, **what spatial architecture carries that identity**?

Two non-equivalent forms are possible:

1. an individual-wide vertical distribution — “this animal tends to use these heights”;
2. a place-coupled vertical rule — “at this place, this animal tends to use this vertical layer.”

## Predictive decomposition

For a held-out night:

```text
G_cond = mean log P_self(z | x,y) / P_other(z | x,y)
G_marg = mean log P_self(z)     / P_other(z)
G_place = G_cond - G_marg
```

Thus:

```text
conditional identity = altitude-wide identity + place-coupled identity
```

All inference is cross-night; GPS fixes estimate distributions but individuals are the summary
unit.

## H1. Vertical individual identity exists across nights

Supported in multiple systems.

Primary 5-km conditional identity gains:

- *Tadarida teniotis*: +0.428;
- *Eidolon helvum*: +0.219;
- *Hypsignathus monstrosus*: +0.029;
- *Phyllostomus hastatus* 2022: +0.056.

The magnitude and individual consistency vary, so this is not a claim that every bat is strongly
specialized.

## H2. Vertical identity is universally a preferred altitude

Not supported.

*Tadarida*, *Eidolon* and *Hypsignathus* have marginal gains near zero or negative compared with
their place-conditioned gains.

## H3. Vertical identity is universally place-coupled

Also not supported.

The frozen *P. hastatus* 2022 endpoint is altitude-wide dominated:

- conditional +0.056;
- marginal +0.176;
- place × height −0.120.

This is a qualitatively different specialization architecture.

## H4. Place-coupled identity is biologically real in the focal system

Supported by several orthogonal checks in *Tadarida*:

- AGL conditional +0.337 and place × AGL +0.591;
- terrain-only conditional +0.007;
- another night from the same bat beats contemporaneous other bats
  (+0.484 AGL; +0.436 MSL);
- pairwise self-win fractions 0.736 AGL and 0.776 MSL.

Thus focal place-coupled identity is not simply MSL elevation, microtopographic route fidelity,
night-wide environmental state or pooling of heterogeneous alternatives.

## H5. The place-coupled architecture replicates in independent taxa

Supported in two prospectively evaluated species:

### *Eidolon helvum*
20 evaluable individuals; conditional +0.219, marginal +0.002, interaction +0.217;
17/20 positive.

### *Hypsignathus monstrosus*
24 evaluable individuals; conditional +0.029, marginal −0.021, interaction +0.050;
the frozen replication rule passed, with the clearest signal at 2.5 km.

These replications show that local 3-D routing individuality is not peculiar to
*T. teniotis*.

## H6. Specialization architecture is a fixed species or seasonal property

Not supported by *P. hastatus*.

A direct pairwise check shows that this contrast is not produced by population averaging:
2022 has marginal pairwise gain +0.323 versus conditional +0.285 (interaction −0.038), whereas
2023 has conditional +0.148 versus marginal +0.028 (interaction +0.120).

- 2022 primary panel: altitude-wide dominated (+0.176 marginal, −0.120 interaction).
- 2023 temporal panel: weak place-coupled (+0.013 marginal, +0.020 interaction).
- 2016 La Gruta, prospectively frozen as a dry-season replication of the 2022 architecture:
  +0.016 marginal, +0.041 interaction; the predefined altitude-wide replication rule failed.

The 2016 failure is retained. It specifically blocks a simple “dry season causes altitude-wide
specialization” narrative.

## H7. One common vertical-wind reaction norm explains the focal architecture

Not supported. The frozen *Tadarida* uplift-reaction endpoint had only two repeat-evaluable
individuals and conflicting signs (permutation p=0.334).

Mechanism remains open.

## Ecological interpretation

Three-dimensional individual specialization is not one number and not one geometry.

An animal can be repeatable because it carries:

- an **altitude-wide signature**;
- a **place-coupled vertical-route signature**;
- or a mixture whose balance changes with ecological context.

That distinction matters because pooling individuals can create a vertically thick population
while no single pooled place-by-height map transfers to new animals. The apparent “failure of
generality” is then a biological property of the population: different animals organize the
third spatial dimension differently.

## Comparative panel

An outcome-blind screen started from 19 checksum-pinned Movebank bat event sources. Six sources
from four taxa passed fixed structural requirements for same-event x-y-height data and repeat
tracking. Sources without native height or adequate repeat individuals were excluded before
numeric height outcomes.

This makes *Phyllostomus*' failure to replicate the place-coupled pattern especially informative:
it was not selected after seeing a favorable result.

## Main figures

### Figure 1 — Two architectures of vertical individuality
Concept diagram: altitude-wide versus place-coupled specialization.

### Figure 2 — Focal *Tadarida* validation
MSL/AGL/terrain decomposition, same-night control and pairwise fingerprint.

### Figure 3 — Architecture plane
For each primary taxon/context, plot:
x = marginal identity;
y = place × height identity.
Diagonal/zero guides separate altitude-wide and place-coupled dominance without forcing discrete
classes.

### Figure 4 — Independent taxa
Per-individual conditional and marginal gains for *Eidolon*, *Hypsignathus* and
*Phyllostomus* 2022.

### Figure 5 — Within-species architecture instability
*Phyllostomus* 2016, 2022 and 2023, with cohort-specific points and the prospective 2016
prediction failure marked explicitly.

### Figure 6 — Spatial grain
2.5/5/10-km architecture trajectories. Use as exploratory comparative ecology, not as a trait
regression with only four taxa.

## Main limitations

- source-specific vertical references differ (AGL, MSL, ellipsoid);
- no common validated foraging-state classifier;
- observational repeatability does not establish personality or mechanism;
- source datasets differ in schedule, region and context;
- *Phyllostomus* context differences do not identify a causal season/year/colony driver;
- only four taxa pass the fixed public-data architecture screen.

## Paper-level conclusion

> **Individual specialization in bat airspace has multiple spatial architectures. Cross-night
> identity may reside in a bat-wide altitude distribution or in a local coupling between place
> and vertical state, and the balance between these components can vary across ecological
> contexts.**

## Next empirical priority

Do not rescue or retune completed endpoints. The highest-value next data are repeated 3-D
tracking of the **same individuals across contrasting environmental contexts**, which can test
whether specialization architecture itself is a plastic individual trait.
