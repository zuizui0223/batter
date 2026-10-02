# Original-panel terrain-relative 3D geometry result v1

## Status

POST-OUTCOME TERRAIN-MEDIATION DIAGNOSTIC. The DEM source, interpolation, target-session universe, geometry estimator, structural gate, permutation count and seeds were fixed before DEM elevation values for these panels were decoded.

Authoritative workflow:
- run: `36946126004`
- head: `819acc829d615485b57033f1ddcbebf64b4b49a0`
- conclusion: success

This diagnostic does not overwrite the native-space 3D geometry results.

## Results

| panel | H | V_native | V_rel | p(V_rel) | S_native | S_rel | terrain-relative V |
|---|---:|---:|---:|---:|---:|---:|---|
| *Hypsignathus monstrosus* | +0.297 | +0.171 | **+0.042** | **0.0001** | +0.103 | -0.016 | supported |
| *Phyllostomus hastatus* 2022 | +0.216 | +0.066 | **+0.100** | **0.0001** | -0.017 | -0.009 | supported |
| *P. hastatus* 2023 | +0.344 | +0.054 | **+0.077** | **0.00010** | -0.004 | +0.016 | supported |
| *P. hastatus* 2016 | +0.302 | +0.145 | **+0.079** | **0.0345** | +0.130 | +0.029 | supported |

H is unchanged by construction because x-y geometry is unchanged.

All four panels that were structurally evaluable in the native 500-m 3D analysis remain structurally evaluable after DEM subtraction, and all four retain a positive, permutation-supported terrain-relative vertical-fidelity contrast.

## Main inference

The terrain audit separates **vertical strategy fidelity** from **vertical niche segregation**.

### Vertical strategy fidelity persists

For all four panels:

> repeated sessions of the same individual have more similar terrain-relative vertical configuration within pairwise-shared 500-m cells than do sessions of different individuals.

Thus the native centered-height individuality in these panels is not explained solely by individuals repeatedly using different terrain elevations.

### Strong added segregation does not persist

The descriptive added-segregation quantity S changes markedly:

- *Hypsignathus*: +0.103 -> -0.016
- *P. hastatus* 2016: +0.130 -> +0.029
- 2022 and 2023 remain near zero before and after terrain correction.

Therefore the current data do **not** show a strong terrain-relative pattern in which different individuals occupy mutually separated vertical layers.

This yields a critical distinction:

> **repeatable individual vertical strategies do not imply vertical niche partitioning.**

Individuals can repeatedly use different vertical probability configurations while those configurations still overlap substantially among individuals.

## Contrast with Pteropus

The pattern differs sharply from *Pteropus poliocephalus*.

Pteropus:
- native V = +0.282, S = +0.280;
- terrain-relative V = -0.040, S = -0.042;
- terrain-relative geometry unsupported.

Original comparative panels:
- all four retain positive supported V_rel;
- none retains large positive S_rel.

Thus at least two geometries can produce apparent 3D individuality:

1. **landscape-embedded 3D individuality** — strong realized x-y-z separation inherited from repeated use of different terrain; current example: Pteropus;
2. **terrain-robust vertical strategy fidelity** — repeatable individual vertical configuration relative to local terrain without strong mutual vertical segregation; current examples: Hypsignathus and all three Phyllostomus panels.

## Consequence for the resource-partitioning hypothesis

The results do not currently support the strong claim that individuals deliberately or competitively divide shared vertical space.

They support a subtler and more general phenomenon:

> individuals can maintain repeatable personal spatial solutions inside shared landscapes even when those solutions are not mutually exclusive.

To establish resource partitioning, future analyses must tie the geometry to identified resources or simultaneous competitor exposure.

## Artifact receipts

- *P. hastatus* 2022: artifact `11201349879`, sha256 `5a868fbdacc71841896534f96b5c3d9db3529e5d610320381a2b0d4364be2e37`
- *P. hastatus* 2016: artifact `11201903101`, sha256 `b8a3c99848dd9c37dfcf6f264e49e3918c8ba3aab6dd41830bed7fb30b711009`
- *Hypsignathus*: artifact `11202650639`, sha256 `6a42b8fb8890c3bf288639adc1f068d3e76dce0aaad9bf240690fce477b4c764`
- *P. hastatus* 2023: artifact `11202795182`, sha256 `e4e47b7f30597ba71c07f06fe317fed98d20286e08b92fe803d1b15251a9a57b`

## Claim ceiling

Supported:
- terrain-relative vertical strategy fidelity in all four structurally evaluable original panels;
- strong horizontal fidelity coexists with terrain-relative vertical fidelity;
- fidelity and segregation are distinct geometric components of individual specialization.

Not established:
- competition-mediated partitioning;
- intentional avoidance;
- mutually exclusive vertical niches;
- diet/resource partitioning;
- a causal ecology-to-geometry law.
