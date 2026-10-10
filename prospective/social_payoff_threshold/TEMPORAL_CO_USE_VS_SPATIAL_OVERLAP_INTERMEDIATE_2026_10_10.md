# 2026-10-10 ecological discriminator: shared utilization vs synchronous co-use

**Status:** literature + accessible OSF file-catalog facts and *pre-outcome design*. No bat receiver timestamp rows, 3D positions, prey captures or dyad interaction statistics have been opened or computed. This is NOT a new empirical effect.

## Independent antecedents, not new discoveries

1. JAE programme (frozen): centered conditional *vertical* use shape can retain individual identity even where added simultaneous between-individual separation is not positively supported. This is a statement about the studied distributions and explicit matching; it is not an assertion of unmeasured absence of competition.
2. Calderón-Capote et al. (2025), *PLOS ONE* 20:e0313782, DOI **10.1371/journal.pone.0313782**: female *Phyllostomus hastatus* in the Panamá sample commuted individually despite groups' foraging areas overlapping. Published paper contrasts Trinidad and Panamá social systems; do not claim individual commute plus overlapping group range as a first discovery. Its 2016/2022 GPS data also require provenance comparison before counting them as an independent replication of any JAE *Phyllostomus* cohort.
3. Hernández-Montero et al. (2026), *Ecology and Evolution* 16:e73604, DOI **10.1002/ece3.73604**: *Myotis bechsteinii* 25 identified females, 21 recorded on multiple nights; higher UD overlap for mother–daughter dyads, site fidelity for retagged females, 65 receiver-grid stations with approximate receiver-footprint spatial resolution. These are published findings, **not** novel analyses in `batter`.
4. Fujioka et al. (2026), *PLOS ONE* DOI **10.1371/journal.pone.0343485**: wild pond co-use correlates with ~25% reduction in attack-attempt rate (not confirmed capture success) and shorter simultaneous patch residence. Their visitor counts within nights do not independently establish tagged cross-night bat identity.
5. Krivoruchko et al. (2024), *PNAS* DOI **10.1073/pnas.2321724121**: independent functional social-acoustic benefit/cost under one evening-or-morning bout per tracked physical bat; confirmed longitudinal personal payoff thresholds cannot be obtained by splitting 5-second rows.

These are **different species, instruments, exposure definitions, and outcomes**, so they cannot be pooled into one confirmatory bat metaanalysis or treated as replications of JAE's 3D terrain-conditioned result.

## Distinguish four separate observables

- **Marginal space sharing:** two animals have overlapping long-run occupancy kernels/UDs. This says nothing about time synchrony, direct contact, task reward, or intention.
- **Contemporaneous use:** two animals are simultaneously detected in a defined shared receiver/patch neighborhood. Requires calibrated sensor footprints, synchronized clocks and detection support; not automatically direct body-body proximity.
- **Response to arrival:** an already present bat changes route/sensing/patch-exit hazard after another arrives. May arise from correlated prey, time or detection factors; observations alone do not isolate acoustic or competitive effects.
- **Functional effect:** assigned or appropriately controlled co-use/interference changes *actual prey captured per fixed bat-time*. Attack buzzes and receiver detections alone cannot establish this.

## A novel but constrained observational test if OSF row-level source gate passes

**Frozen scientific question:** Within dyads whose receiver-footprint utilization overlaps, is *simultaneous receiver-footprint use* reproducibly more or less frequent than expected given their own night-specific station use and activity schedules, and does kinship predict the residual synchronization?

### Requirements before opening a co-detection outcome
- Genuine stable animal ID (not just hardware tag ID); receiver ID and synchronized timestamps; independent nights; station deployment-year map.
- Define co-detection from prevalidated hardware latency and spatial footprint, not from post-result window selection. Multiple neighboring receivers detecting the same tag are not independent bat encounters.
- Conditional reference must retain the single-animal within-night location sequence, receiver dwell bouts, common nocturnal activity envelope and detection coverage. Naive independent permutation of 2-second beacons creates false social evidence. Prespecify blocked temporal shifts or a prevalidated conditional intensity model on pilot/night-only data; test calibration with known independent synthetic traces before opening dyad synchrony outcomes.
- Same-dyad independent-night support is necessary to claim **repeatable dyadic personal synchrony**. A source table with 21 individual bats monitored on >1 night does not guarantee even one same-dyad repeat; do not inflate a 103-dyad overlap calculation into 103 independent social experimental units.
- Bat-linked cross-dyad correlation, kinship (only seven mother–daughter dyads in the publication's main analysis) and receiver-level autocorrelation constrain inference; do not claim a family/social effect from a naive dyad-permutation p.
- Separately report the direction of temporal co-use and whether the information adds held-out-night prediction over marginal spatial UDs. A positive overlap association without incremental temporal prediction remains a re-description of already published space sharing.

### Meaning of falsification
- Negative excess co-detection *after* conditioning on site-time availability would be consistent with temporal avoidance in observed receiver neighborhoods, but **does not prove intentional avoidance, prey competition, or received-echo jamming**.
- Positive excess co-detection could be consistent with coordinated or shared-resource activity, but **does not prove cooperation**, kin-affinity or adaptive payoff.
- Null excess is not equivalent to equality/absence of social interaction without an informative error bound and power/precision.
- Signal confined to same device/single night, or removed by receiver detection quality and common darkness timing, is not evidence for a personal social response.
- In no case does a 35m-footprint/receiver-grid source measure 3D elevation, fine-scale vertical separation or confirmed prey capture.

## Repository/source work completed
- [Official OSF metadata CI 38010699176](https://github.com/zuizui0223/batter/actions/runs/38010699176) **SUCCESS**: node `sg6dz` and public osfstorage metadata accessible; **zero event values** retrieved.
- [Second metadata CI 38010744981](https://github.com/zuizui0223/batter/actions/runs/38010744981) **SUCCESS**: top-level public OSF entries `proximity_UD/` and `README.md`. Still no bat-event schema, stable ID crosswalk, day-level dyad crossing or quantitative outcome access.
- Source gate `MYOTIS_2026_OSF_TEMPORAL_CO_USE_SOURCE_GATE_V1.md` forbids bat-event opening until folder schema and persistent dyad support are verified.

**Research priority:** The original functional-payoff 3D causal mechanism is not directly testable here; this new source is a plausible **independent intermediate test of spatial overlap vs timing**. It should be positioned as a prospective exploratory extension under honest source restrictions, not a JAE manuscript result.
