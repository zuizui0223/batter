# Matched-family engineering receipt v1

## Status

**NORMALIZED TOPOLOGY FROZEN; PHYSICAL SCALE / TOLERANCES / PILOT CLOSEOUT REMAIN OPEN.**

Authoritative normalized template:
- `PARAMETRIC_MATCHED_FAMILY_GEOMETRY_V1.md`
- `matched_family_geometry_v1.json`
- `matched_family_geometry_audit_v1.py`

Verified normalized geometry:
- route classes: R1-R4 = {L/R} × {Low/High};
- A = horizontal then vertical;
- B = vertical then horizontal;
- L = 1;
- x1 = 1/3;
- x2 = 2/3;
- d = 0.20;
- normalized path length for every A/B route = **1.214622820933**;
- total absolute horizontal demand = **0.4**;
- total absolute vertical demand = **0.4**;
- geometric turn-angle multiset identical across all routes/families.

Physical scale factor s and safe center height z0 remain to be frozen by engineering pilot.

## Family geometry

### Family A
- normalized topology: **horizontal decision -> vertical decision**
- normalized start: **(0,0,0)**
- normalized goal: **(1,0,0)**
- normalized decision planes: **x=1/3, 2/3**
- normalized decision offset: **d=0.20**
- room / arena physical dimensions: TBD
- obstacle material: TBD

### Family B
- normalized topology: **vertical decision -> horizontal decision**
- normalized start: **(0,0,0)**
- normalized goal: **(1,0,0)**
- normalized decision planes: **x=1/3, 2/3**
- normalized decision offset: **d=0.20**
- room / arena physical dimensions: TBD
- obstacle material: TBD

## Corresponding route table

| route class | A shortest path | B shortest path | A min aperture | B min aperture | A vertical demand | B vertical demand | A horizontal demand | B horizontal demand |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R1 | 1.214622821 s | 1.214622821 s | TBD | TBD | 0.4 s | 0.4 s | 0.4 s | 0.4 s |
| R2 | 1.214622821 s | 1.214622821 s | TBD | TBD | 0.4 s | 0.4 s | 0.4 s | 0.4 s |
| R3 | 1.214622821 s | 1.214622821 s | TBD | TBD | 0.4 s | 0.4 s | 0.4 s | 0.4 s |
| R4 | 1.214622821 s | 1.214622821 s | TBD | TBD | 0.4 s | 0.4 s | 0.4 s | 0.4 s |

## Canonical constrained route

Frozen route class:
**R1 = L × Low**

Rationale:
fixed prospectively from the topology before individual preference outcomes. The same topological route is used in A and B.

The canonical route must not be chosen using individual-preference outcomes.

## Engineering tolerances

Freeze before pilot closeout:
- maximum relative A/B shortest-path mismatch:
- maximum aperture mismatch:
- maximum vertical-demand mismatch:
- maximum horizontal-demand mismatch:
- acceptable route-specific failure-rate difference:

## Tracking architecture

- camera / tracking system:
- sampling rate:
- coordinate calibration:
- valid-trajectory rule:
- minimum coverage:
- occlusion handling:

## Pilot closeout

- pilot animal IDs:
- pilot animals permanently excluded from confirmation: YES / NO
- final capability rule: **>=2 successful traversals within <=4 isolated-route attempts per route; tracking-validity threshold TBD**
- acquisition count: **12 valid flights/family (frozen)**
- probe count: **16 valid flights/family = 8 early + 8 late (frozen)**
- maximum flights/session:
- missing-flight rule:
- engineering PASS / REDESIGN:

## Freeze signatures / hashes

- geometry file hash:
- analysis code hash:
- randomization script hash:
- freeze date:
