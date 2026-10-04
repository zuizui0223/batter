# Source B MATLAB-native coordinate structural result and gate adjudication v1

## Status

**PASS — primary Source B biological outcome may open in the structurally eligible cohort only.**

Authoritative MATLAB-native workflow:
- run: **37176264766**
- job: **111359386031**
- artifact: **11293102339**
- artifact ZIP SHA256: `4c433b851c950b4e767dbbfce0a6c38fd018d071b2198f04f2554c0b1ddeb7c4`

Parent:
- `SOURCE_B_COORDINATE_STRUCTURAL_OPENING_V1.md`
- `SOURCE_B_MATLAB_NATIVE_READER_AMENDMENT_V1.md`
- `SOURCE_B_EMPTY_DAY_HANDLING_CLARIFICATION_V1.md`

## Outcome firewall

This run calculated only within-day structural support:
- exact source x/y/time;
- finite-value filtering;
- chronological ordering;
- first fix per frozen 30-s bin;
- count of days with >=20 standardized fixes.

It calculated no between-day distance, no self/other comparison, no B, no R, no L, and no permutation statistic.

## Native structural result

| source cohort | juveniles | >=20 valid movement days |
|---|---:|---:|
| 2016–2017 | 8 | **0** |
| 2017–2018 | 14 | **14** |
| **Total** | **22** | **14** |

Eligible juveniles:
`Anka, Eli, Eva, Fima, K, Mazi, Nadav, Nature, Nazir, Odelia, Shem_Tov, Tishray, Tzedi, V`.

## Frozen gate adjudication

The parent contract requires:

1. >=5 juveniles with >=20 valid movement days;
2. **within each target's cohort**, >=3 other juveniles with >=20 valid movement days.

Observed:

- overall primary targets: **14 >= 5**;
- every eligible target is in the 2017–2018 cohort;
- that cohort has 14 complete-history juveniles, so each target has 13 possible complete-history conspecifics before target-specific donor filtering;
- the 2016–2017 cohort has zero primary targets and therefore has no target for which a donor requirement must be satisfied.

Therefore the frozen rule is satisfied.

### Correct verdict

`PASS_OPEN_PRIMARY_OUTCOME`

with the primary inferential target cohort:
**GPS_2017_2018 only**.

## Why this is not a cohort rescue

No result from the biological self-history endpoint has been opened.

The design did not require both cohorts to contribute targets. It required biological replication and same-cohort donors for every target that enters the primary.

The 2016–2017 juveniles fail the frozen >=20-valid-day target requirement and are simply structurally ineligible.

Do not:
- shorten their target horizon;
- lower the valid-day threshold;
- pool them with 2017–2018;
- create a separate 2016 rescue endpoint.

## Parser provenance

The earlier SciPy result had the opposite cohort pattern because:
- 2017–2018 MATLAB tables were opaque to SciPy;
- native MATLAB restores exact x/y/time.

The authoritative coordinate-support result for outcome opening is therefore the native-source result above.

## Primary implications fixed before outcome

- primary target n = **14**;
- all primary targets are from 2017–2018;
- whole-history identity permutations occur within that cohort;
- the frozen >=70% direction rule therefore requires **10 of 14** juveniles to have `B_i > 0`.

No biological direction has yet been inspected.

## JAE firewall

No effect on JAE v0.4.0.
