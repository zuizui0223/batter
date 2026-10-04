# Source B coordinate parser diagnostic amendment v1

## Status

**STRUCTURAL DEBUG ONLY — frozen after the first coordinate-support run and before any parser repair.**

Observed first coordinate-support run:
- 2016–2017: 8/8 individuals passed >=20 valid movement days;
- 2017–2018: 0/14 yielded a valid movement day under the same parser.

The exact cohort-wide zero makes a file-structure/parser mismatch plausible. This amendment distinguishes parser failure from true absence of the already-frozen x/y/time fields.

## Authorized deterministic probes

Only:
- 2016–2017: `Ali/data.mat`;
- 2017–2018: `Anka/data.mat`.

Authorize printing **names/types/shapes only** for:
1. top-level `data`;
2. fields of `data(1)`;
3. the type/class and field names of `data(1).track`;
4. for fields named exactly `x`, `y`, `time`, their container type and array shape only.

No numeric cell/array value may be printed.

## Interpretation fixed before inspection

- If Anka exposes the same semantic fields `track.x`, `track.y`, `track.time` but a different MATLAB container representation, a parser-only repair is allowed.
- If any frozen primary field is truly absent, the frozen Source B primary stops. Do not substitute lon/lat or another representation.
- No estimator, 30-s interval, 20-fix day gate, 20-day horizon, or donor rule may change.

## Outcome firewall

No route distance, coordinate range, map, destination, tree, or movement statistic is authorized.
