# Ecology-to-geometry synthesis v4

## Central result

The post-freeze 3D programme now separates four biological layers that are often collapsed under "individual specialization" or "niche partitioning":

1. **landscape fidelity** — an individual repeatedly returns to particular x-y portions of the landscape;
2. **personal vertical-strategy fidelity** — within shared horizontal space, an individual repeatedly reuses a characteristic vertical configuration;
3. **static niche segregation** — different individuals occupy substantially non-overlapping vertical configurations;
4. **dynamic co-presence response** — individuals become additionally separated when they locally co-occur.

The data show that these layers are empirically distinct.

> **Stable individual strategies do not imply niche partitioning, and niche geometry does not imply active avoidance.**

## Layer 1 — landscape fidelity

Metric:
H = self O_XY - other O_XY.

Strong positive H occurs in the structurally evaluable original panels and in Pteropus.

This says individuals repeatedly reuse different parts of the landscape.

## Layer 2 — personal vertical-strategy fidelity

Metric:
V_rel = self O_Z|XY - other O_Z|XY after DEM terrain subtraction.

Supported in all four original panels structurally evaluable at 500 m:

- Hypsignathus +0.042
- P. hastatus 2022 +0.100
- P. hastatus 2023 +0.077
- P. hastatus 2016 +0.079

Thus individuals repeatedly reuse personal vertical configurations relative to the local terrain.

This is the strongest recurrent post-freeze ecological result.

## Layer 3 — static vertical niche segregation

Metric:
S_rel = other R_3D - self R_3D after terrain correction.

Current values:

- Hypsignathus -0.016
- 2022 -0.009
- 2023 +0.016
- 2016 +0.029

None shows strong terrain-relative added segregation.

Therefore personal vertical strategies remain substantially overlapping among individuals.

The current archive supports **specialization without strong static vertical partitioning**.

## Layer 4 — dynamic co-presence-dependent separation

The fixed encounter-phase null preserves each individual's site-specific vertical distribution and asks whether actual synchronous local co-use adds separation.

Results:

- Hypsignathus: excess -1.98 m, p_upper=0.9045
- P. hastatus 2022: -0.95 m, p_upper=0.9186
- P. hastatus 2023: +3.57 m, p_upper=0.0231
- P. hastatus 2016: -0.85 m, p_upper=0.8611

Thus only the 2023 panel contains evidence for an additional co-presence layer.

Three panels with clear personal vertical-strategy fidelity show **no extra separation during co-use**.

This directly demonstrates that repeatable individual strategy and dynamic partitioning are different phenomena.

## Localization of the 2023 exception

The 2023 co-use result survives:
- equal-dyad weighting;
- leave-one-dyad-out diagnostics (positive excess in 8/8; p<0.05 in 6/8);
- a descriptive endpoint-excluded universe (+3.81 m; four individuals, therefore non-inferential).

But the proximity predictions do not succeed.

### Temporal proximity

Most encounters are already near-synchronous:
- median |Delta t| = 3 s;
- 599/679 are <=60 s.

The predeclared equal-dyad temporal slope is in the predicted direction:
- observed -13.56 m per additional minute;
- null mean -9.57;
- p_lower=0.095.

The fixed criterion is not met.

### Horizontal proximity

The predeclared interaction prediction is the opposite of the observed direction:
- predicted: vertical separation should increase as horizontal distance decreases;
- observed slope: +20.93 m per additional 100 m;
- null mean +17.94;
- p_lower=0.889.

Descriptively:
- <=100 m encounters do not show positive excess;
- <=250 m are near null;
- >250 m show the largest separation.

Therefore the 2023 excess does not localize to near-contact geometry.

## Revised interpretation of 2023

The corrected primary remains real under its frozen 500-m co-use endpoint:

> actual local co-use in 2023 contains more vertical separation than the fixed phase null.

But the new localization results argue against a simple "individuals get close and move vertically apart" mechanism.

The more defensible interpretation is:

> **a context-specific shared-site spatial organization, potentially involving sub-cell route, canopy, resource or microhabitat geometry.**

Competition remains possible but is not the leading inference from the current geometry.

## Pteropus: a separate geometry class

Pteropus shows another way that 3D individuality can be generated.

Native MSL:
- H +0.221
- V_abs +0.282
- S_abs +0.280

Terrain-relative:
- V_rel -0.040
- S_rel -0.042

Thus strong realized 3D separation can be inherited from repeated selection of different topographic landscape elements without a stable terrain-relative vertical overlap geometry.

This is **landscape-embedded 3D specialization**, distinct from both personal vertical-strategy fidelity and interaction-driven partitioning.

## The non-trivial ecological hypothesis

The earlier statement "ecological opportunity allows individual differences" is too weak.

The stronger hypothesis is:

> **Ecological strategy predicts where individual-specific information is encoded in spatial geometry.**

Possible outcomes include:

### A. Landscape-embedded specialization
H positive; V_abs/S_abs positive; V_rel/S_rel collapse after substrate correction.

### B. Personal vertical-strategy specialization
V_rel positive; S_rel near zero; co-presence excess absent.

Individuals repeatedly use different strategies but do not exclude one another.

### C. Static vertical partitioning
V_rel positive and S_rel strongly positive.

Different personal strategies become genuinely segregated vertical niches.

Not established in the current terrain-corrected panels.

### D. Dynamic interaction-dependent partitioning
co-presence separation positive **and** localized toward greater spatiotemporal proximity.

The current 2023 primary co-use signal does not satisfy the proximity-localization prediction, so this class is not established.

### E. Weak or constrained geometry
H and V weak or structurally unavailable.

Current Myotis result is consistent with this under a surface-constrained task.

## General principle

The current programme supports:

> **Individual specialization is a statement about repeatability; niche partitioning is a statement about separation; interaction is a statement about context-dependent change.**

These should be measured separately.

This distinction is biologically important because populations can contain stable individual strategies even when:
- individuals share the same resources;
- their realized niches strongly overlap;
- they do not move farther apart during co-presence.

## Consequence for the original "food partitioning" idea

The current tracking archive does not establish food partitioning.

To test true resource partitioning, the next decisive data are not another movement threshold. They are:
- identified feeding trees/patches or prey resources;
- simultaneous resource use by tagged individuals;
- diet/resource identity;
- competitor density;
- resource depletion/manipulation.

Movement geometry has now reached its inferential ceiling.

## Submission boundary

All analyses in this synthesis are post-freeze extensions.

The frozen JAE submission should remain unchanged unless explicitly reopened.

The post-freeze programme is strong enough to motivate a separate geometry/resource-partitioning paper or a deliberate later revision, but its chronology must remain explicit.
