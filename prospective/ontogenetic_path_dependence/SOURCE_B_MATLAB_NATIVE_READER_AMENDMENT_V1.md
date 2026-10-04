# Source B MATLAB-native table reader amendment v1

## Status

**PARSER-ONLY REPAIR CONTRACT.**

This amendment is frozen after the deterministic SciPy parser diagnostic and before opening any numeric value from the 2017–2018 `track` object.

Parent:
- `SOURCE_B_COORDINATE_PARSER_DIAGNOSTIC_V1.md`
- `SOURCE_B_COORDINATE_STRUCTURAL_OPENING_V1.md`
- `SOURCE_B_SELF_HISTORY_ESTIMATOR_CONTRACT_V1.md`

## Established parser problem

The deterministic diagnostic showed:

### 2016–2017 probe: Ali
- `data(1).track` loads through SciPy as a struct array;
- each track element exposes source fields `x`, `y`, and `time`.

### 2017–2018 probe: Anka
- `data(1).track` loads through SciPy as `MatlabOpaque`;
- the ordinary SciPy representation does not expose the saved MATLAB table variables.

This cohort-wide representation difference explains why the first Python coordinate-support parser returned zero valid days for all 14 2017–2018 juveniles.

It is not yet evidence that the frozen source fields are absent.

## Parser repair authorized

Use **MATLAB's native `load` implementation** on the original, source-identity-verified `data.mat` files.

The source files were created and analysed in MATLAB, and the public source code accesses the object using:

- `data(day).track.x`
- `data(day).track.y`
- `data(day).track.time`

The parser repair may therefore use MATLAB solely to restore the source object's native semantics.

## First deterministic diagnostic

Before any cohort-wide numeric coordinate opening, use only:

- Ali / 2016–2017;
- Anka / 2017–2018.

For `data(1).track`, print only:

1. MATLAB class;
2. size;
3. if table or timetable, `Properties.VariableNames`;
4. whether variables named exactly `x`, `y`, `time` exist;
5. sizes/classes of those three variables only.

**Do not print numeric values.**

## Frozen decision rule

### PASS parser repair

If Anka's native MATLAB object contains variables named exactly:
- `x`;
- `y`;
- `time`;

then the structural gate may be re-run with MATLAB-native access to those same frozen fields.

This is a parser-only repair. No scientific design choice changes.

### STOP

If any of the three exact fields is absent under native MATLAB loading:
- stop Source B primary;
- do not substitute `lon`, `lat`, `timeStr`, or another field.

## Cohort-wide repair ceiling

If deterministic PASS occurs, MATLAB may subsequently apply the **already frozen** coordinate-support processing:

- finite `x/y/time`;
- sort by time;
- first fix in each 30-s bin;
- no interpolation;
- no smoothing;
- valid movement day = >=20 standardized fixes;
- target horizon remains >=20 valid days;
- donor gate remains >=3 same-cohort donors.

No route distance or primary outcome may be calculated until that repaired structural gate passes.

## No rescue interpretation

The previous `STOP_COORDINATE_STRUCTURAL_SUPPORT` remains an authoritative record of the SciPy-reader failure.

A MATLAB-native rerun is allowed only because the parser diagnostic identified a serialization/container mismatch fixed independently of biological outcome.

## JAE firewall

No effect on JAE v0.4.0.
