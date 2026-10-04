# Source B coordinate structural-opening amendment v1

## Status

**POST-ESTIMATOR, OUTCOME-BLIND COORDINATE SUPPORT GATE.**

The primary estimator is already frozen in:
`SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md`.

This amendment authorizes the minimum coordinate opening needed to determine whether that frozen estimator is structurally executable.

## Authorized source

Ordinary juvenile `data.mat` files under:
- `Pure data/GPS_2016_2017`;
- `Pure data/GPS_2017_2018`.

No translocation or resampled source is authorized.

## Authorized values

For each top-level `data(day)`, use only:
- `track.x`;
- `track.y`;
- `track.time`.

The implementation may deserialize the enclosing MATLAB `data` object to access these fields, but:
- no other field may be inspected, printed, summarized, or used;
- no destination/tree/visit identity may be read;
- no route similarity or between-day spatial distance may be calculated.

## Frozen structural processing

Exactly as already frozen:

1. finite x/y/time only;
2. sort by time;
3. first fix per 30-second bin relative to the day's first retained timestamp;
4. no interpolation;
5. no smoothing;
6. valid day = >=20 standardized fixes.

For each juvenile report only:
- number of source day objects;
- number of structurally valid movement days;
- whether >=20 valid days.

Do not report:
- coordinate ranges;
- path length;
- home-range area;
- route maps;
- distances;
- destination use;
- spatial overlap.

## Frozen gate

The primary outcome may open only if:

- **>=5 juveniles** have >=20 valid movement days; and
- within each target's cohort, at least 3 other juveniles also have >=20 valid movement days, ensuring the frozen donor rule can be met through target ordinal 20.

If this fails:
STOP. Do not shorten the 20-day horizon.

## No interpretation

Passing this gate means only that the prospective estimator is structurally executable.

It provides no evidence for path dependence or self-history predictability.
