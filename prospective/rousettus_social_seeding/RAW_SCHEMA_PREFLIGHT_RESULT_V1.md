# Rousettus raw-schema preflight result v1

## Status

**STOP — pending raw-data retrieval. No route geometry opened.**

Authoritative workflow:
- run: **37112482932**
- artifact: **11269939441**
- conclusion: **success**

The workflow attempted only Dryad file retrieval plus SQLite schema/tag/date presence. It did not calculate route similarity, overlap, corridor width, self-versus-other distance or any vertical endpoint.

## Retrieval result

All current Dryad raw-file routes were blocked to non-interactive CI:

| source | file ID | file_stream | API download |
|---|---:|---|---|
| June SQLite | 3182077 | HTML security challenge | HTTP 401 |
| July SQLite | 3182078 | HTML security challenge | HTTP 401 |
| December SQLite | 3182076 | HTML security challenge | HTTP 401 |
| target-tree CSV | 3182081 | HTML security challenge | HTTP 401 |

A live-browser check independently confirmed that the file_stream URLs exist, but direct file access is protected by Dryad BotStopper/validation in this environment.

## Documented schema

Dryad's public README documents the raw track fields:

- TAG — tracked bat ID
- TIME — Unix timestamp
- X / Y — Israel Transverse Mercator coordinates in metres
- FREQ
- NBS
- VARX / VARY / COVXY
- dateTime
- date
- date_global
- Night
- distance / dT / spd
- stdVarXY
- Lon / Lat

The target-tree file is documented as containing X_ITM, Y_ITM, Lat_WGS84 and Long_WGS84.

Therefore the intended geometry and coordinate semantics are source-defined; the blocker is access to the file bytes, not an ambiguous route definition.

## Decision

`may_open_xy_support_preflight = false`.

Under the frozen contract:
- do not switch to a different annulus;
- do not substitute tree-stop sequences as the primary route endpoint;
- do not infer raw-route support from movies;
- do not open self-versus-other route geometry.

The external test remains a **pending-data preregistration** until the pinned Dryad files can be retrieved through an authorized reproducible route.
