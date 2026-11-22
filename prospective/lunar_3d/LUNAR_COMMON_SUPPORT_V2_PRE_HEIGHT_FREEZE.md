# Lunar exposure spatial/time common-support audit v2 — PRE-HEIGHT FREEZE

Date: 2026-11-22. **Frozen after v1 source/exposure results, before any numeric height result was inspected.** This is a distinct, explicitly source-selected *data-support* diagnostic; it is neither an elevation-effect test nor a modification of the v1 PASS criteria.

v1 receipts: `P. hastatus` 2021–22: 15 animals with >=2 bright and >=2 dark nights, population span 49 days; `Eidolon`: 5, span 1,929 days; `Hypsignathus`: 16, span 19 days and 15 individual-night transitions, so it fails v1's 35-day duration criterion. Other three sources have zero dual-exposure individuals. Actual height values remain sealed.

## New independent common-support question

Among only metadata-qualified records (timestamp, individual ID, longitude, latitude, native-height **presence**, and outlier flag), do both exposures occur for the **same animal, approximate 5.5-km cell, and 2-hour local-solar clock band**, on repeated independent nights? Require:
- source-only astronomical geometry and classes identical to v1 (Sun < -12°, bright Moon >=10° and phase >=0.8, dark Moon <=-5° or phase <=0.2);
- same individual, 0.05-degree latitude×longitude grid cell and 2-hour local-solar clock band;
- at least **2 distinct nights and >=20 fixes in each exposure** per matched animal×cell×clock stratum;
- at least one bright/dark pair of nights separated by **<=45 days**, preventing years-apart overlap from masquerading as contemporaneous exposure support;
- a source has sufficiently broad matched support for a prospective conditional-height test only when **>=5 individuals** have at least one eligible matched stratum. Smaller panels are descriptive support only.

These boundaries are conservative and mechanically defined. Do not reoptimize the spatial/time window based on altitude outcomes. Within-night brightness transitions remain a separate optional estimand, not an automatic PASS override.

Source download must verify size and checksum against `config/bat_panel_sources_v1.json`. Code cannot read numeric height fields. Preserve source-level counts (not GPS rows or individual identities) as an Action artifact. The original v1 classifications remain unchanged regardless of v2 results.

A v2 match is **not** a causal result, a valid sensor AGL, confirmed foraging or evidence that predation causes lunar response. Site/timing/effort/weather, elevation datum and cross-validated heldout scores remain necessary after this gate.
