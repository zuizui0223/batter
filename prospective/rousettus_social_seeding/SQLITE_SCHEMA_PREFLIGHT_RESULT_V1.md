# Rousettus SQLite schema preflight result v1

## Status

**FAIL — STOP before coordinate opening.**

Authoritative workflow:
- run: **37118290793**
- artifact: **11272178349**
- conclusion: workflow success; structural data gate failed

Classification:

**RAW FILE IDENTITY + SQLITE SCHEMA + TAG/TIME COVERAGE ONLY. Coordinate numeric values and route geometry remain unopened.**

## Retrieval result

| campaign | Dryad file_stream ID | retrieval | expected candidate IDs seen |
|---|---:|---|---:|
| June 2020 | 3182077 | HTTP 403 | 0/5 |
| July 2020 | 3182078 | HTTP 403 | 0/1 |
| December 2020 | 3182076 | HTTP 403 | 0/3 |

No SQLite database was opened.

Therefore:
- no table schema was inspected;
- no tag/time coverage was opened;
- no x-y coordinate value was opened;
- no route geometry was opened.

## Decision

`STOP_BEFORE_COORDINATE_OPENING`

This independently reproduces the earlier raw-source retrieval stop. No browser-bypass, credential inference, alternate mirror or copied third-party raw tracking source is used.

The continuous personal-route-reuse test remains **pending inaccessible raw data**, not negative evidence.

## Consequence for the external mechanism programme

The publicly retrievable GitHub tables are sufficient to verify:
- experimental visitor identities;
- manipulated-versus-naive status among visitors;
- the explicit pup exclusion;
- the information-transfer manipulation context.

They are not sufficient to execute the predeclared self-versus-other continuous route geometry test.

The discrete waypoint-sequence test is separately stopped by insufficient known-status donor identities before any sequence similarity is opened.
