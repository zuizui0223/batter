# Roost-centred 3D connectivity and functional diversity
Status: prospective design, no empirical result. Separate from frozen manuscript.

## Hypotheses
H1: terrain-aware 3D connectivity improves held-out movement prediction over distance and 2D connectivity.
H2: independently measured wing aspect ratio, wing loading and foraging guild modify connectivity responses.
H3: among-roost differences in trait-specific accessible resource distributions explain functional composition and richness-conditioned functional dispersion beyond climate, resource amount, terrain roughness and sampling effort. Sign not assumed: heterogeneity may diversify routes or impose a common bottleneck.

## Model
Build undirected airspace voxel graph above DEM; ground is excluded. Edge resistance = distance * exp(beta_species * standardized environmental edge features). Canopy is not automatically impermeable. Compare Euclidean, 2D circuit, isotropic 3D, terrain 3D, trait-interaction 3D. Wind-direction and ascent/descent asymmetry require separate directed transition model, not ordinary electrical resistance. Fit coefficients using training data only. Roost and independently defined resource endpoints; if resource endpoints unavailable use fixed candidate endpoints and label accessibility, not foraging. Current density is not occupancy probability. Validate normalized current-derived scores against held-out trajectories and matched available steps; block by individual, night and where feasible site/species. Test resolution, boundary and endpoint sensitivity.

## FD bridge
Use external trait data, log mass and wing loading, aspect ratio, guild; audit units, missingness, taxonomic joins and trait redundancy. Compute pairwise trait distances (Gower for mixed traits), FDis and Rao Q using incidence weights unless abundance is comparable. For each roost compute trait-specific accessibility profiles over independently mapped resources; quantify between-guild accessibility dissimilarity and mean accessibility separately. Avoid circularity: define guilds and candidate species pool independently of observed local composition; do not derive accessibility predictors from observed community membership. Primary test: held-out regional prediction of richness-conditioned FD using accessibility dissimilarity beyond mean accessibility, terrain, climate, resource amount and effort. Null: random assemblages of fixed richness from regional pool, with occurrence-frequency sensitivity. Also model species composition with trait-by-accessibility interaction; no causal coexistence claim from occurrence data alone.

## Data gates
Existing batter tracking panels: audit altitude datum, timestamps, roost evidence, DEM resolution and independent resource endpoints. Cave-specific tests require verified cave roosts; do not assume all panels use caves. DarkCideS candidate for global cave assemblages: verify public coordinate precision, completeness, repeated surveys and licenses. Use buffers larger than location uncertainty; no sensitive coordinates published. Global analysis only at supported landscape scale, not entrance-scale 3D. External wing/roost trait sources must be verified before acquisition. Missing effort prevents strong absence inference.

## Decision
First demonstrate numerical graph solver correctness on synthetic grids; then data audit, held-out movement test, trait interaction test, independent assemblage FD test. Do not advance a failed predictive model as an established mechanism. Preserve negative results. No claim of novelty until literature audit.
