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
- `https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/` (only the root provider's *metadata listing*, not any download);
- optionally the exact read-only token as a query string for those endpoints when documented, without fetching binary files or following any file download/view URLs.

Use strict JSON size caps, file names/sizes/extensions only, and no receiver coordinates/roost localization.

**Final aim:** an *independent temporal co-use boundary* for the existing JAE conditional vertical-use idea; not new 3D mechanistic proof, not prey payoff, and no amendment to JAE's frozen empirical results.


## V1a source metadata receipt and fixed next path (2026-10-10, before any animal rows)
- [Official OSF CI 38010699176](https://github.com/zuizui0223/batter/actions/runs/38010699176): **SUCCESS**, original node identity and osfstorage directory metadata verified without numeric events.
- [Official OSF CI 38010744981](https://github.com/zuizui0223/batter/actions/runs/38010744981): **SUCCESS**, root contains exactly `proximity_UD/` folder and `README.md` file.
- [Official OSF CI 38010792711](https://github.com/zuizui0223/batter/actions/runs/38010792711): **SUCCESS**, original OSF root folder metadata has declared directory ID **698dbd04bb73abf03bdfc98c** (`proximity_UD`), original README resource ID **698dc7add062fca4f5dfc63d** (1517 bytes). These are source *identifiers*, not biological observations.
- Consequently the **single next preauthorized exact metadata URL** is `https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/698dbd04bb73abf03bdfc98c/` (optionally the published view-only token). This will enumerate only direct child file/folder *names/types/sizes*. Do not follow download links or open any timestamp/detection values.
- The README file must not be automatically downloaded as part of this folder-listing step; any future README-only text inspection requires a separate source contract and outcome-free extraction.
- Expected result remains `HOLD_DYAD_NIGHT_CROSSING_NOT_VERIFIED` regardless of filename counts; no bat×receiver×night data values authorized.


## V1b exact child folder gate (2026-10-10)
[Official GitHub Actions 38010881468](https://github.com/zuizui0223/batter/actions/runs/38010881468) completed **SUCCESS**. `proximity_UD/` has four child *folders*, not bat values: `scripts/` (OSF ID 698daaafa731d64729dfc7aa), `data/` (ID **698dac7afa739fb04ee258a4**), `output/` (698dbcb1892397af47e24fba), and `analysis/` (698dbe01fae4711f5ac72f78). No event rows opened.

Freeze the next **single exact metadata-only URL**: `https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/698dac7afa739fb04ee258a4/` (plus the publicly published view-only parameter only if needed). This lists direct child names, IDs, declared sizes and file/folder type **only**, not downloadable contents. Do not recursively traverse unspecified children, do not open signal data, and do not infer that a file in `data/` is an independently replicated bat file solely from its filename. `HOLD_DYAD_NIGHT_CROSSING_NOT_VERIFIED` remains the science status until categorical schema and same-dyad repeat nights are confirmed.


## V1c proximity sensor data tree gate (2026-10-10)
[CI run 38010935844](https://github.com/zuizui0223/batter/actions/runs/38010935844) **SUCCESS**, original OSF `proximity_UD/data/` lists only four folders: `bg_maps`, `box_coords`, `sn_coords`, and **`sn_prox`**. No bat event values or station coordinates read. The `sn_prox` metadata resource ID is **698dad08eb682af8bcc73651**; its directory name alone is not proof of original independent animal-level longitudinal records.

Authorize only the next exact *file metadata* endpoint `https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/698dad08eb682af8bcc73651/` (with optional published view-only query). Do not traverse `sn_coords` or `box_coords`, print sensitive site coordinates, or open any individual event values. If the station proximity folder contains child metadata-only directories, a separately frozen endpoint is required for further traversal. Repeat-night dyad crossing remains unverified.
