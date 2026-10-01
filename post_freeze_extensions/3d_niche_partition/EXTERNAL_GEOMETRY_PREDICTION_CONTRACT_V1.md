# External ecology-to-geometry prediction contract v1

## Status

POST-OUTCOME CROSS-SYSTEM GEOMETRY TEST; FIXED BEFORE ANY EXTERNAL 3D-OVERLAP OUTPUT IS COMPUTED.

The source datasets and their earlier centered-vertical outcomes are already known. This contract therefore does not create an independent prospective replication of vertical individuality. It freezes a new question before opening a new endpoint: whether the geometry of individual specialization matches natural-history predictions about the ecological task.

## General hypothesis

The spatial dimensionality of individual specialization should depend on the geometry of the ecological problem.

We distinguish four idealized geometries:

1. HORIZONTAL-DOMINANT: individuals repeatedly reuse different horizontal patches, with little additional individual structure in height within shared space.
2. NESTED-3D: individuals show both horizontal patch fidelity and repeatable vertical configuration within horizontally shared space.
3. VERTICAL-SEGREGATING: adding height reduces between-individual overlap more than within-individual overlap.
4. WEAK / CONTEXT-DEPENDENT: no stable individual 3D geometry survives across repeated sessions.

The primary geometric statistic is the already frozen 500-m common-horizontal conditional vertical-overlap contrast:
D = self O_Z|XY - other O_Z|XY.

The descriptive segregation statistic is:
Delta_R = other R_3D - self R_3D,
where R_3D = 1 - O_XYZ/O_XY.

No external source is reclassified after its 3D results are seen.

## Source-specific predictions frozen before external 3D output

### Myotis vivesi

Natural-history basis:
- prey are predominantly marine crustaceans and larval fish captured from the ocean surface;
- prey capture is physically associated with the water surface;
- bats search over long distances for unpredictable prey patches.

Prediction:
- geometry class: WEAK / SURFACE-CONSTRAINED;
- D should be small and should not meet the positive primary criterion;
- Delta_R should be near zero because adding vertical space should contribute little stable separation;
- stable horizontal specialization is not required.

Interpretation if contradicted:
A strong D would show that even a surface-constrained foraging system can contain repeatable vertical configuration, weakening the simple task-geometry prediction.

### Pteropus poliocephalus

Natural-history basis:
- repeatedly visited foraging sites and routes are documented;
- productive trees and feeding sites are reused across nights and weeks;
- at least some foraging sites are shared among tracked individuals.

Prediction:
- geometry class: NESTED-3D;
- self O_XY > other O_XY;
- D > 0 under the primary 500-m geometry;
- Delta_R may be positive, but this is secondary because terrain can generate apparent vertical structure.

Pteropus terrain diagnostic:
A separate secondary analysis may repeat D using centered MSL-minus-DEM height. This is not a second primary test. Based on the already known terrain audit, attenuation relative to native MSL is expected; persistence after DEM subtraction would support terrain-relative solution fidelity.

### Nyctalus noctula

Natural-history basis:
- aerial-hawking on mobile/ephemeral insects;
- habitat and flight altitude shift with ecological context such as moonlight and prey distribution;
- the same prey-centered vertical problem need not recur from session to session.

Prediction:
- geometry class: WEAK / CONTEXT-DEPENDENT;
- primary all-context D should be small and should not meet the positive criterion;
- no state-conditioned rescue is allowed in v1.

Interpretation if contradicted:
A strong D would indicate that stable individual 3D geometry can persist despite mobile prey and context-dependent altitude use.

### Hipposideros armiger / H. pratti

Natural-history basis:
- strong foraging-site fidelity is documented, with individuals often retaining a single foraging site for 7-10 consecutive nights;
- source-study analyses indicate multidimensional responses to competition, including temporal and dietary adjustment, while spatial ranges contract rather than simply shifting away;
- population-level spatial and dietary overlap remain substantial.

Prediction:
- geometry class: HORIZONTAL-DOMINANT OR WEAK-VERTICAL;
- self O_XY > other O_XY;
- D is not expected to be strongly positive;
- Delta_R is expected to be small or near zero;
- species are analysed separately for identity exchangeability and then summarized source-wise.

Interpretation if contradicted:
A strong D or positive Delta_R would reveal an unmeasured vertical niche dimension within a system already known to coordinate competition across space, time and diet.

## Fixed analysis rules

- Primary horizontal grain: 500 m.
- Same centered-height bins as the original 3D-overlap contract.
- Session pair support: at least 50 fixes from each session inside the pairwise shared-cell set.
- Same O_XY, O_XYZ, O_Z|XY, L_3D and R_3D definitions as CONTRACT_V1.md.
- Whole-session identity permutation within the source's original exchangeability strata.
- Minimum 5 evaluable biological individual units for an inferential source-level primary test, except the already-established four-individual Myotis/Pteropus programmes: for those two sources the structural gate is exactly 4 because the source universe itself contains only four admitted repeat individuals.
- 9,999 permutations.
- New seeds:
  - Myotis vivesi: 20261002021
  - Pteropus poliocephalus: 20261002022
  - Nyctalus noctula: 20261002023
  - Hipposideros source: 20261002024
- If a source fails the structural gate at 500 m, report it as structurally non-evaluable. Do not open another grid as rescue.

## Source-specific session universes

- Myotis and Pteropus: exact frozen training/target session universe from small-panel-generality v1.
- Nyctalus: the first prospective n=27 programme, including its >=50-fix source-track rule; do not use the later relaxed n=36 analysis as the primary geometry universe.
- Hipposideros: exact species-specific training and target-night universe frozen in height_opening_receipt_v1.json of the original primary programme.

## Claim ceiling

Even if all predictions align, allowed:
- natural-history strategy is descriptively associated with different realized spatial geometries;
- external systems are consistent or inconsistent with the generated ecology-to-geometry hypothesis;
- vertical geometry can add a niche dimension missed by 2D home-range overlap.

Not allowed:
- ecology has been shown to causally determine geometry;
- competition caused the observed 3D partitioning;
- the four external systems form a representative prevalence sample;
- a post-outcome geometry result is an independent replication of the earlier vertical endpoint.

## Stop rule

After the first external 3D-overlap result:
- no source-specific recoding of predicted geometry;
- no change to 500-m grid, 50-fix pair gate, vertical bins, alpha or overlap index;
- no dropping a source because it contradicts prediction;
- no switching Nyctalus to the later n=36 universe;
- no state-conditioned or alternative-grid rescue;
- no terrain-adjusted Pteropus result may overwrite the native-MSL primary geometry result.
