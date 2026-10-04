# Source B missing/empty track-day handling clarification v1

## Status

**PARSER/STRUCTURAL CLARIFICATION — frozen before repaired structural rerun and before primary outcome opening.**

Observed software failure:
the first MATLAB-native cohort structural run terminated when one source day had a struct `track` object lacking one or more frozen fields.

No route statistic was calculated.

## Existing frozen biological rule

A valid movement day requires:
- finite `x`, `y`, and `time`;
- successful 30-s standardization;
- >=20 standardized fixes.

A day with no usable x/y/time values therefore cannot be valid.

## Clarified implementation

For an individual source day:

- if `track` is empty: mark that day structurally invalid and continue;
- if the native `track` object does not expose **all three exact frozen fields** `x`, `y`, `time`: mark that day structurally invalid and continue;
- if the three arrays have incompatible lengths or cannot be converted to the frozen numeric/time representation: mark that day structurally invalid and continue;
- do not drop the biological individual merely because one day is invalid.

This is identical in spirit to the original Python structural parser, which returned zero usable fixes for a day without the frozen fields.

## Source-wide field stop remains

The deterministic MATLAB-native probe already established that both archive serialization classes expose exact x/y/time:
- 2016–2017 ordinary struct track;
- 2017–2018 ordinary table track.

If a whole cohort's ordinary native representation lacked one of these semantic fields, the source would stop.

Isolated unusable/empty days are simply not valid movement days.

## What does not change

No change to:
- x/y/time field identity;
- 30-s bins;
- >=20 fixes per valid day;
- >=20 valid days per primary juvenile;
- same-cohort donor rule;
- target horizon;
- estimator;
- permutation null;
- primary support rule.

## JAE firewall

No effect on JAE v0.4.0.
