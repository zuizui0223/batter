# Parametric matched-family geometry v1

## Status

**PROSPECTIVE NORMALIZED GEOMETRY TEMPLATE.**

This document fixes the topology and normalized geometry of matched obstacle families A and B before confirmatory outcome collection.

The engineering pilot may choose the physical scale subject to the frozen topology and symmetry constraints.

It may not redesign the route graph to increase individual differences.

---

## 1. Biological design goal

Each family must provide four simultaneously feasible route classes:

\[
\{L,R\}\times\{Low,High\}.
\]

The four routes represent two independent binary movement decisions:
- horizontal sign;
- vertical sign.

This prevents the four-route treatment from collapsing to one simple left-right choice.

---

## 2. Normalized coordinates

Let the start-goal axis be x.

Normalize total start-to-goal forward distance to:

\[
L=1.
\]

Decision planes:

\[
x_1=1/3,\qquad x_2=2/3.
\]

Use equal horizontal and vertical decision magnitude:

\[
d_y=d_z=d.
\]

Template value:

\[
d=0.20L.
\]

The actual physical value of L and safe vertical center z0 are engineering quantities to be frozen after pilot.

All geometric comparisons below use coordinates relative to the safe flight center, so z=0 denotes the center flight height rather than the floor.

---

## 3. Route codes

Route code is fixed before data collection:

| Route | horizontal bit | vertical bit |
|---|---|---|
| R1 | L = -1 | Low = -1 |
| R2 | L = -1 | High = +1 |
| R3 | R = +1 | Low = -1 |
| R4 | R = +1 | High = +1 |

Route labels are topological labels, not labels learned from observed trajectories.

---

## 4. Family A — horizontal then vertical

For route with horizontal sign h in {-1,+1} and vertical sign v in {-1,+1}:

Start:

\[
S=(0,0,0).
\]

Waypoint 1:

\[
W_{A1}=(x_1,hd,0).
\]

Waypoint 2:

\[
W_{A2}=(x_2,hd,vd).
\]

Goal:

\[
G=(1,0,0).
\]

Interpretation:
- first obstacle/gate resolves L versus R;
- second resolves Low versus High while preserving the horizontal branch.

---

## 5. Family B — vertical then horizontal

Start:

\[
S=(0,0,0).
\]

Waypoint 1:

\[
W_{B1}=(x_1,0,vd).
\]

Waypoint 2:

\[
W_{B2}=(x_2,hd,vd).
\]

Goal:

\[
G=(1,0,0).
\]

Interpretation:
- first gate resolves Low versus High;
- second resolves L versus R while preserving the vertical branch.

Thus A and B share the same route code but differ in the order in which the two movement decisions must be realized.

---

## 6. Exact geometric matching

Because:

\[
d_y=d_z=d
\]

and:

\[
x_2-x_1=x_1=1-x_2=1/3,
\]

Family A and B are related by exchanging the order of equal-magnitude orthogonal displacements.

Every R1-R4 route has the same Euclidean segment-length sequence up to coordinate permutation.

Therefore, in the normalized template:

- all four A routes have identical total path length;
- all four B routes have identical total path length;
- corresponding A/B routes have identical total path length;
- total absolute horizontal displacement is matched;
- total absolute vertical displacement is matched;
- the unordered internal turn-angle sequence is matched.

Reference audit:
\`matched_family_geometry_audit_v1.py\`.

---

## 7. What is and is not matched

Geometrically matched:
- forward distance;
- path length;
- absolute horizontal displacement demand;
- absolute vertical displacement demand;
- number of decision stages;
- aperture count;
- nominal aperture size;
- Euclidean turn demand;
- reward;
- start/goal distance.

Not assumed identical biologically:
- horizontal-first versus vertical-first sensorimotor sequencing;
- gravity-related cost of vertical maneuvers;
- acoustic context created by exact obstacle placement;
- micro-scale aerodynamic effects.

These remaining family effects are why:
- OPEN-family assignment is randomized/counterbalanced across A/B;
- starting-family order is orthogonalized;
- A-open/B-open strata are always reported.

A family effect is not a treatment effect.

---

## 8. Aperture / obstacle construction

At each decision plane, the apparatus must physically prevent arbitrary shortcuts that create unregistered fifth routes.

The engineering implementation may use:
- obstacle panels;
- hanging arrays;
- framed apertures;
- other safe modular structures.

But it must preserve the frozen route graph.

Before confirmatory randomization, the engineering receipt must show that:
- each R1-R4 path is realizable;
- no additional shortcut has comparable accessibility;
- aperture dimensions are matched across corresponding routes/families.

---

## 9. Canonical constrained route

Freeze:

> **R1 = L × Low**

as the canonical constrained route in both families.

During CONSTRAINED acquisition:
- only R1 is available;
- R2-R4 are structurally closed.

During OPEN acquisition and common OPEN probe:
- R1-R4 are simultaneously available.

R1 is fixed by topology before individual preference data are observed.

No route may be chosen as canonical because it is most/least preferred in pilot free-choice data.

---

## 10. Capability equalization

Before randomization, every confirmatory animal is exposed to each isolated route R1-R4 in both A and B.

Frozen behavioral capability rule:
- maximum four attempts per route;
- require at least two successful traversals.

Thus every eligible animal has physically experienced all eight family × route combinations before OPEN versus CONSTRAINED acquisition is assigned.

This reduces simple route unfamiliarity as an explanation for the P1 contrast.

---

## 11. Physical scaling rule

Engineering pilot chooses one global scale factor s.

Physical coordinates are:

\[
(x,y,z)_{physical}
=
s(x,y,z)_{normalized}
+
(0,0,z_0).
\]

The same s is used for A and B.

The pilot may adjust s before confirmatory freeze for:
- animal safety;
- aperture clearance;
- tracking volume;
- room dimensions.

It may not use specialization/identity outcomes to choose s.

Once frozen, s and z0 are recorded in:
\`MATCHED_FAMILY_ENGINEERING_RECEIPT_V1.md\`.

---

## 12. Engineering tolerances

Before confirmatory randomization, the physical build must satisfy predeclared tolerances for corresponding A/B routes.

At minimum audit:
- shortest-path mismatch;
- aperture-width mismatch;
- aperture-height mismatch;
- forward-plane-position mismatch;
- route-specific tracking coverage;
- route-specific isolated-traversal success.

Numeric tolerances remain to be frozen from engineering measurement precision, not behavioral individuality.

---

## 13. Why the two-family architecture is useful

The treatment effect is not A versus B.

Within every animal:
- one family receives OPEN acquisition;
- the other receives CONSTRAINED acquisition.

At the common probe both are OPEN.

The randomized contrast therefore asks:

> **Does history with multiple feasible solutions create more persistent individual organization than history with one forced solution, under equal current opportunity?**

Family A/B is a matched repeated-measures scaffold that allows this causal history contrast.
