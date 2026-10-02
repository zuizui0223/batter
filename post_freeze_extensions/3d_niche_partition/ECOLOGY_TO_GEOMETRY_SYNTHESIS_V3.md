# Ecology-to-geometry synthesis v3

## Central revision

The 3D-overlap and terrain analyses force a stronger distinction than the earlier ecological-opportunity framing.

Individual specialization in space has at least three separable geometric components:

1. **fidelity** — does the same individual repeatedly reuse a similar spatial configuration?
2. **segregation** — are different individuals actually less overlapping with one another?
3. **environmental embedding** — is apparent 3D separation inherited from the physical elevation/shape of the landscape that individuals select?

These components can vary independently.

Therefore:

> **individual specialization is not equivalent to niche partitioning, and 3D niche partitioning is not equivalent to vertical behavioural partitioning.**

## Geometry variables

### H — horizontal landscape fidelity

H = self O_XY - other O_XY.

Positive H means repeated sessions of one individual overlap more in horizontal space than sessions of different individuals.

### V_abs — absolute-coordinate vertical fidelity

V_abs = self O_Z|XY - other O_Z|XY using centered native altitude.

Positive V_abs means an individual's vertical configuration within horizontally shared cells is repeatable in geographic z coordinates.

### V_rel — substrate-relative vertical fidelity

V_rel is the same contrast after subtracting local DEM terrain.

Positive V_rel means individual-specific vertical configuration persists relative to local terrain.

### S_abs and S_rel — added segregation

S = other R_3D - self R_3D.

Positive S means adding z removes more overlap between individuals than within an individual.

S is descriptive under the current contract.

## Empirical geometry classes

### Class I — landscape-embedded realized 3D specialization

Current example: *Pteropus poliocephalus*.

Native MSL:
- H +0.221
- V_abs +0.282
- S_abs +0.280

Terrain-relative:
- H +0.221
- V_rel -0.040
- S_rel -0.042

Interpretation:
individuals repeatedly use different fine-scale landscape/topographic settings. Those x-y choices inherit different z coordinates and create strong realized 3D separation. Once local terrain is removed, stable pairwise vertical geometry disappears.

This is strong 3D niche differentiation **without evidence for a distinct terrain-relative vertical strategy under the overlap endpoint**.

### Class II — terrain-robust personal vertical strategy without strong mutual segregation

Current examples: *Hypsignathus monstrosus* and all three *Phyllostomus hastatus* panels.

Terrain-relative V remains supported in 4/4 structurally evaluable original panels:

- *Hypsignathus*: V_rel +0.042, p=0.0001
- *P. hastatus* 2022: +0.100, p=0.0001
- *P. hastatus* 2023: +0.077, p≈0.00010
- *P. hastatus* 2016: +0.079, p≈0.0345

But S_rel is small in all four:
- -0.016, -0.009, +0.016, +0.029.

Interpretation:
individuals repeatedly reuse personal terrain-relative vertical configurations, but those configurations remain substantially overlapping among individuals.

This is **individual strategy fidelity without strong vertical niche segregation**.

### Class III — weak / surface-constrained geometry

Current example: *Myotis vivesi*.

- H -0.003
- V_abs +0.036
- primary p=0.055
- S +0.022

Interpretation:
the current source does not establish stable 3D geometry under the fixed endpoint, consistent with a task physically constrained near the ocean surface. The positive direction and n=4 prevent a strong absence claim.

### Class IV — fine-scale shared-space question structurally unavailable

Current examples:
- *Tadarida teniotis*
- *Eidolon helvum*
- *Nyctalus noctula*

At the fixed 500-m / >=50-shared-fixes geometry, these sources do not provide enough repeated pairwise shared space for the primary question.

This itself is informative about realized geometry: some movement systems are so horizontally dispersed or non-overlapping at fine scale that "vertical partitioning within shared space" cannot be estimated from the archived tracks.

It is not evidence of absence.

## The key ecological insight

The important question is no longer:

> Does ecological opportunity permit individuality?

Nor simply:

> Do individuals partition 3D space?

It is:

> **Which spatial layer carries repeatable individual information, and does that information represent personal strategy fidelity, mutual niche segregation, or environmental embedding?**

Ecological strategy should predict this decomposition.

## Ecology-to-geometry predictions

### Persistent resources distributed among distinct terrain/landscape elements

Expected:
- H strong;
- V_abs and S_abs can be strong because landscape selection inherits z;
- V_rel and S_rel may collapse.

Geometry:
**landscape-embedded 3D specialization**.

Current example:
Pteropus.

### Recurrent task within shared or repeatedly revisited habitat, with multiple reusable vertical solutions

Expected:
- H may be positive;
- V_rel positive;
- S_rel need not be positive.

Geometry:
**personal vertical strategy fidelity**.

If S_rel is also positive, the stronger condition of actual vertical niche segregation is met.

Current examples:
Hypsignathus and Phyllostomus support V_rel, but not strong S_rel.

### Surface-constrained task

Expected:
- residual vertical freedom small;
- V_rel weak;
- any stable specialization is more likely horizontal, temporal or resource-specific than vertical.

Current consistent example:
Myotis, narrowly non-supporting.

### Mobile/ephemeral prey

Expected:
- stable prey-centred vertical geometry weak unless animals repeatedly exploit stable landscape/atmospheric structures;
- fine-scale shared-space support may itself be low.

Current sources motivate but do not confirm this prediction.

## Why this is less trivial than ecological opportunity

"More available options allow more individuality" is nearly tautological.

The geometry formulation makes directional predictions before seeing movement outcomes:

- a terrain-associated resource strategy can create V_abs without V_rel;
- a reusable behavioural solution can create V_rel without S_rel;
- competition/resource partitioning specifically predicts stronger S_rel or resource-level non-overlap;
- a surface-constrained task predicts weak V_rel;
- low fine-scale horizontal sharing predicts structural inability to express/test within-patch vertical partitioning.

These are distinct observable geometries.

## Consequence for the original resource-partitioning idea

The current data do **not** justify saying that bats deliberately divide vertical space.

They show something subtler:

> individuals can maintain repeatable personal vertical strategies inside shared landscapes even when those strategies overlap strongly with those of other individuals.

Thus the evidence currently favours **individual strategy specialization** over **competition-mediated vertical partitioning**.

To promote the claim to resource partitioning, future data must show at least one of:
- identified shared resources with lower-than-null individual overlap;
- simultaneous co-use where competitor presence increases separation;
- diet/resource identity matching spatial strategies;
- competition-density or resource-depletion effects;
- experimental resource manipulation.

## New general principle

> **Ecological strategy may predict not only how much individuals specialize, but what kind of geometry that specialization takes: landscape fidelity, environment-embedded 3D separation, personal substrate-relative vertical strategy, or true niche segregation.**

This makes individual specialization a problem of **information location in spatial geometry**, not only specialization magnitude.

## Submission boundary

This synthesis is post-outcome and belongs to the exploratory extension branch.

The frozen integrated JAE submission should not be rewritten around this result unless the manuscript is explicitly unfrozen. A later paper or deliberate revision can promote this framework only with full chronology and post-outcome labeling.
