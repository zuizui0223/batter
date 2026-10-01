# Pteropus terrain-relative 3D geometry result v1

## Status

Secondary diagnostic specified before this terrain-relative 3D-overlap output.

Authoritative workflow:
- run: 36887389097
- head: 4c3a5fa45a064c8499de45364c7de8724be499a8
- artifact: 11174578625
- digest: sha256:dc90328249af396355222d46ad95ec7156fe0a4cfef636c87a406ee5259dd145

This diagnostic cannot overwrite the native-MSL 3D geometry result.

## Result

Native-MSL geometry had shown:
- H = +0.22066
- V = +0.28155
- S = +0.28024
- primary V calibrated excess = +0.27908
- p = 0.0001278

After replacing native MSL height with the same pre-specified MSL-minus-DEM terrain-relative proxy:

- H = **+0.22066**
- V = **-0.04011**
- S = **-0.04188**
- calibrated V excess = **-0.04030**
- p(null >= observed) = **0.9620**
- terrain-relative primary geometry is not supported.

The horizontal component H is unchanged, as expected, because only z was transformed. The vertical solution-fidelity component reverses sign and the additional-segregation component collapses from strongly positive to slightly negative.

## Interpretation

The striking native-MSL nested-3D geometry in *Pteropus poliocephalus* is therefore **not terrain-robust**.

At the 500-m scale used here, different individuals repeatedly use different fine-scale terrain within horizontally shared cells. Because absolute altitude inherits local ground elevation, this fine-scale landscape fidelity produces strong realized 3D separation in MSL coordinates.

Once local terrain elevation is removed, the data do not show repeatable individual-specific terrain-relative vertical configurations under this overlap metric.

This creates an important ecological distinction:

1. **realized 3D niche geometry** — where an animal occurs in x-y-z geographic space;
2. **terrain-relative vertical strategy** — how it positions itself vertically relative to the local ground surface.

The first can be strongly individualized even when the second is weak.

Thus, for Pteropus, the current 3D partitioning signal is best described as **landscape/topographic niche partitioning expressed in three-dimensional coordinates**, not as evidence that individuals repeatedly choose different heights above local terrain.

## Relation to the earlier terrain audit

This result is compatible with the earlier prediction-score terrain audit but is not identical to it.

The earlier audit retained a small positive terrain-relative centered predictive-identity effect (+0.0323, p=0.0023). The new pairwise 3D-overlap endpoint instead gives negative terrain-relative V.

These estimands ask different questions:
- prediction score: does own-individual history improve held-out log probability relative to other individuals?
- overlap geometry: are repeated sessions of the same individual more geometrically similar to each other than to sessions of other individuals?

Therefore the terrain-relative source can contain weak predictive identity without forming a stable pairwise-overlap geometry.

Do not treat the two results as contradictory or select one as a rescue for the other.

## General implication generated here

**Three-dimensional niche segregation is not equivalent to vertical-behaviour segregation.**

Topographic or substrate selection can convert horizontal ecological specialization into strong separation in x-y-z space. Analyses of 3D niche partitioning should therefore distinguish:
- horizontal/landscape selection;
- topographic elevation inherited from that selection;
- residual vertical placement relative to the local surface.

This distinction may be especially important for terrestrial and aerial animals moving over heterogeneous terrain.

## Claim ceiling

Supported for this four-individual source:
- strong individual horizontal fidelity;
- strong native-MSL realized 3D geometry;
- native-MSL vertical separation is highly terrain-sensitive;
- no repeatable terrain-relative pairwise-overlap geometry under the fixed 500-m endpoint.

Not established:
- resource competition;
- intentional avoidance;
- exact feeding-tree partitioning;
- absence of all terrain-relative vertical individuality;
- generality beyond this source.

The DEM-derived MSL-minus-terrain value remains a proxy, not source-measured AGL.
