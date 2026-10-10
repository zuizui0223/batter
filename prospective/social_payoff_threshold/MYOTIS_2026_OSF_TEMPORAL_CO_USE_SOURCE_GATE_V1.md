# 2026 Myotis bechsteinii OSF source gate: simultaneous co-use versus persistent spatial overlap

**Date:** 2026-10-10. **Pre-outcome, categorical/source-only.** No 2026 telemetry numbers beyond published methods/results have been opened; no receiver-event timestamps, location records, UD estimates or kinship dyad outcomes have been reanalyzed.

## Exact original source

Hernández-Montero, J. R., Wolf, J. M., Chávez, F., Mayer, F., & Kerth, G. (2026). *Determining Activity Patterns and Home Range of Wild Bats Using a Proximity Biologging System Based on the Internet of Things (IoT).* **Ecology and Evolution**, 16, e73604. DOI **10.1002/ece3.73604**. Public text: https://pmc.ncbi.nlm.nih.gov/articles/PMC13158582/

Original author source declaration: **https://osf.io/sg6dz/overview?view_only=4624cf1757b34e87bf7a4aca9d889319**; do not substitute data from another bat study or assume this view-only link is anonymous API-downloadable.

### Published verified structure (PRIOR ART, not new finding)

- 25 individually tagged adult female *Myotis bechsteinii* were detected; 21 had detections on **more than one night**, mean ~2.55 nights monitored per bat.
- 65 stationary BLE receivers in a forest detection grid, mobile beacons targeted 2-second intervals; original authors' candidate conservative detector range ~35 m, overlapping neighbor receiver footprints. Spatial precision is **receiver scale**, not sub-meter GPS or directly observed altitude.
- Per original methods, receiver logs have mobile tag ID, stationary receiver ID, timestamp and RSSI, with station coordinates added for inferred use. Differing time-of-night activity and gaps due to detection/receiver coverage are possible.
- Original paper already reports individualized UDs/site fidelity, **higher mother–daughter overlap** than unrelated pairs, 103 dyads, and an imperfect monitored grid. These findings are NOT new and must not be marketed as independent discovery of nonexclusive bat space-use individuality.
- No simultaneously measured confirmed prey captures, calibrated received echoes, individual elevation or direct 3D continuous flight trajectories. Thus **not** a test of the proposed #96 personal 3D maneuver → payoff threshold or the JAE terrain-relative vertical identity mechanism.

## A narrower independent gap, only if original timestamped logs are legitimately accessible

**Question:** When two identified bats overlap in *where* they are detected, do they also overlap in *when* they use the same receiver footprint, after adjusting for their respective site-use intensity, time-of-night and family relationship?

**Why new/different from the paper's reported UD result:** The published dyadic Bhattacharyya-type UD overlap measures marginal spatial distributions. It does not, by itself, distinguish asynchronous sharing, synchronous co-visitation or social avoidance. A carefully verified individual×receiver×night time-series could estimate time-conditioned co-detection **at a receiver's resolution**, but NOT true direct body-body encounters.

### Mandatory categorical gate before observing occurrence timestamps

1. Official OSF project identity verified; metadata file list must expose at least one **genuine bat-tag receiver event CSV** with source recording date/timestamp field, physical individual-tag key and stationary receiver identifier; source must provide a bat-tag↔biological-animal crosswalk stable across independent nights and years, rather than changing mobile-device IDs.
2. Confirm station coordinates and station deployment/year mapping without revealing sensitive exact roost locations to chat/repo. Receiver positions shifted between 2024 and 2025 (published mean displacement), so cross-year receiver-ID matching is not a guaranteed identical spatial comparison.
3. Confirm at least **two independently monitored overlapping nights for the same dyad** if claiming repeatable dyad-specific synchrony; individual multi-night tracking alone is insufficient. If not, settle for *night-level temporal interaction only* and explicitly abandon persistence claims.
4. Verify timestamp synchronization, readout/storage gaps, logger saturation and RSSI-dependent detection probability. Treat 2-second transmissions as technical samples, not independent visits, and overlapping receiver beams as one approximate space-use neighborhood rather than multiple independent sites.
5. Freeze co-detection tolerance using validated beacon transmission/window synchronization; no search over 2/5/10/20 second windows after seeing outcomes. If source only supports discrete receiver occupancy, report occupancy overlap, not flight distance/avoidance mechanisms.
6. Time-conditioned null must preserve each bat's station-specific occupancy, within-night activity envelope and bouts/serial autocorrelation. Simple independent per-beacon shuffling destroys biology and is INVALID. The null must be frozen, simulated and source-calibrated prior to inspecting the co-detection statistic.
7. Independent sampling unit is bat/dyad/night, with dependence when a bat occurs in multiple dyads; n=103 dyads is **not 103 independent bats**. Family effects require kinship identity proof, appropriate clustered inference and confounding controls; maternal relation is observational and cannot be called causal social attraction.
8. No *confirmed capture success*, foraging energy, 3D altitude or social-acoustic received interference: stop all adaptation and sensory-buffering claims even if temporal avoidance is demonstrated.

### Source-only decision statuses

- `STOP_OSF_METADATA_INACCESSIBLE` if original metadata APIs fail, rather than assuming private or fabricated values;
- `STOP_NO_TAG_RECEIVER_TIMESTAMP_STRUCTURE` if no actual event table exists;
- `STOP_NO_STABLE_BIOLOGICAL_ID_CROSSWALK` if mobile logger IDs cannot be matched safely;
- `HOLD_DYAD_NIGHT_CROSSING_NOT_VERIFIED` if schema exists but same-dyad independent repeat nights are unknown;
- `PASS_SOURCE_STRUCTURE_ONLY` solely after documented categorical identities, timestamps, station/bat mapping and session support; this never authorizes response outcome opening.
- No eligible publication-level result from metadata alone.

### Exact limited source probe (does not download bat detections)

The preflight script may request only:
- `https://api.osf.io/v2/nodes/sg6dz/` (OSF project metadata);
- `https://api.osf.io/v2/nodes/sg6dz/files/` (provider-level file metadata);
- optionally the exact read-only token as a query string for those endpoints when documented, without fetching binary files or following any file download/view URLs.

Use strict JSON size caps, file names/sizes/extensions only, and no receiver coordinates/roost localization.

**Final aim:** an *independent temporal co-use boundary* for the existing JAE conditional vertical-use idea; not new 3D mechanistic proof, not prey payoff, and no amendment to JAE's frozen empirical results.
