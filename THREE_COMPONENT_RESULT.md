# Matched 3-D component decomposition

Date: 2026-09-26

All three axes below were evaluated on the same checksum-pinned annotated rows, the same
`animal-id × BatDay` sessions, the same horizontal cells and the same fixed bins.

## 5-km result

| Component | Conditional self-transfer | Marginal identity | Identity × location | Positive individuals |
|---|---:|---:|---:|---:|
| Terrain elevation | +0.007 | -0.145 | +0.152 | 4/6 |
| Height above ground (AGL) | **+0.337** | -0.255 | **+0.591** | 4/6 |
| Height above sea level (MSL) | **+0.428** | +0.052 | **+0.376** | 5/6 |

The near-zero terrain result is important. At 5 km, repeatable individual 3-D organization is
not reducible to repeatedly choosing the same sub-cell terrain elevations. A substantial signal
remains after terrain is removed from the vertical coordinate.

AGL individuality is especially interaction-dominated: the population mean marginal identity
signal is negative, while the identity × location increment is strongly positive. Thus animals
do not simply carry a stable preferred height above ground. They repeat **where** they occupy
different height-above-ground layers.

## 2.5-km result

| Component | Conditional self-transfer | Marginal identity | Identity × location | Positive individuals |
|---|---:|---:|---:|---:|
| Terrain elevation | +0.187 | +0.041 | +0.145 | 4/5 |
| AGL | **+0.766** | +0.090 | **+0.675** | 5/5 |
| MSL | **+0.866** | +0.191 | **+0.675** | 4/5 |

At finer horizontal resolution, some repeatable microtopographic route selection appears, but it
is still much weaker than the AGL/MSL vertical signal.

## Individual coordinate-frame heterogeneity

The population does not have one universal vertical reference frame.

At 5 km:
- Bat4 is strongly MSL-dominant (+0.843 MSL vs -0.144 AGL).
- Bat7 is terrain-relative (+0.098 AGL vs -0.206 MSL); at 2.5 km the contrast becomes
  +0.609 AGL vs -0.066 MSL.
- Bat6 and Bat8 transfer positively in both frames.
- Bat5 is positive in both but stronger in MSL.
- Bat3 is MSL-positive while its AGL marginal distribution transfers very poorly; its
  location-specific AGL increment is nevertheless large.

These patterns are descriptive, not fitted strategy classes. They motivate a future larger-panel
test of whether individuals differ in the coordinate frame used for repeatable 3-D routing.

## Current ecological statement

The strongest supported statement is now:

> European free-tailed bats show repeatable individual fine-scale organization of vertical
> airspace use. The identity signal is primarily in the coupling between place and vertical
> state, persists when height is measured relative to local terrain, and is not explained by
> microtopographic route fidelity alone.

The frozen uplift reaction-norm test did not establish one common wind-response mechanism, so the
mechanism of these individual 3-D routes remains open.
