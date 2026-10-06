# Geometry-policy family ablation result v1

## Status

**ROBUST TO ALL BROAD GEOMETRY-FAMILY DELETIONS.**

Authoritative workflow:
- run: **37400943476**
- job: **112067746542**
- conclusion: **success**
- fail-closed shell: `set -euo pipefail`

Parent:
`GEOMETRY_POLICY_FAMILY_ABLATION_CONTRACT_V1.md`

This is a post-primary exploratory mechanism diagnostic.

## Parent result

Scale-free geometry identity across obstacle configurations:

- `K_geometry = +0.38857`
- 5/5 bats positive
- p = **0.0153**

The parent representation removes:
- elapsed-time scale;
- speed magnitude;
- turn rate per unit time;
- absolute path length;
- absolute vertical range;
- absolute spatial offset.

## Frozen geometry families

### G — global route organization
- 3-D path efficiency
- horizontal displacement ratio
- absolute vertical displacement ratio
- vertical range ratio

### H — horizontal maneuver geometry
- median absolute horizontal turn angle
- p90 absolute horizontal turn angle

### V — vertical maneuver geometry
- median absolute vertical slope
- p90 absolute vertical slope

---

# Family-only localization

## G only

- K = **+0.40777**
- 5/5 positive
- p = **0.0088**

Global route organization alone carries strong cross-configuration identity.

## H only

- K = **+0.29605**
- 5/5 positive
- p = **0.0089**

Horizontal maneuver geometry alone also carries strong cross-configuration identity.

## V only

- K = **-0.04844**
- 2/5 positive
- p = **0.5906**

Vertical slope geometry alone does **not** carry the portable identity signal.

Thus the scale-free route signature is not a generic "vertical style" effect.

---

# Leave-family-out robustness

## Drop G — retain H + V

- K = **+0.17413**
- 5/5 positive
- p = **0.0461**

Identity remains without global route-organization features.

## Drop H — retain G + V

- K = **+0.30366**
- 5/5 positive
- p = **0.0184**

Identity remains without horizontal-turn features.

## Drop V — retain G + H

- K = **+0.46622**
- 5/5 positive
- p = **0.0111**

Identity is strongest when the unsupported vertical-slope family is removed.

Frozen diagnostic verdict:

**ROBUST_TO_ALL_FAMILY_ABLATIONS**

---

# Mechanistic interpretation

Portable scale-free route identity is not dependent on one broad geometric family.

At least two distinct aspects of movement organization independently contain personal information:

1. **global route organization**
   - route efficiency;
   - relative horizontal/vertical displacement;
   - relative vertical extent;

2. **horizontal maneuver organization**
   - ordinary and upper-tail turning geometry.

The vertical-slope family alone is not identity-bearing.

Therefore the result is better described as a **distributed coordinative solution** than as one scalar geometric trait.

This is compatible with:
- multiple lower-level combinations contributing to an individual's higher-level movement policy;
- stable sensorimotor coordination style;
- history-refined control organization.

It is not direct evidence that the environment contains multiple feasible solutions.

---

# Relation to functional abundance

The abundance-history hypothesis requires two logically separate ingredients:

1. the animal expresses a distributed personal coordinative organization;
2. the environment supplies multiple feasible solutions from which history can select.

This result supports ingredient 1.

Ingredient 2 remains unmeasured in the current Teshima archive because public obstacle geometry is unavailable independently of observed trajectories.

Do not use:
- trajectory dispersion;
- route clusters;
- number of flights

as a proxy for solution abundance.

---

# Strongest bounded statement

> **Portable individuality persists in multiple independent components of scale-free route organization rather than being carried by a single speed, scale, vertical-slope or route-shape statistic.**

This strengthens the interpretation of the personal policy as a distributed movement-control solution.

## Claim ceiling

Do not infer:
- motor degeneracy as a proven cause;
- neural modularity;
- direct environmental solution abundance;
- independence of G and H as biological modules.

These feature families are transparent descriptive decompositions, not identified anatomical control systems.

## JAE firewall

No change to JAE v0.4.0.
