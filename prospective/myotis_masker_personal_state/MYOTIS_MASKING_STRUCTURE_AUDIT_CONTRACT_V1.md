# Myotis masking public-data structural audit contract v1

## Status

**OUTCOME-BLIND STRUCTURAL AUDIT.**

Frozen source snapshot:
- Zenodo record 4946256
- DOI 10.5281/zenodo.4946256

The newer record may be checked later for provenance, but it cannot silently replace this frozen source after outcomes are opened.

## Source A — control experiment 1

File: control_experiment__1_data.txt  
Frozen md5: db9c7b38579435d9f63ef6b4973d6825

Public README states:
- each row is one selected call;
- source level = sl_rms;
- noise-source location = transducer;
- source noise = noiselevel;
- bat ID = animal;
- trial ID = trialno;
- collection day = date;
- five loudest calls were selected from each successful trial.

Frozen treatment mapping:
- noiselevel = 20 -> no_noise;
- noiselevel = 94 and transducer h -> noise_target;
- noiselevel = 94 and transducer a -> noise_above;
- noiselevel = 94 and transducer s -> noise_side;
- anything else -> structural anomaly.

Proceed only if:
- exactly 5 animals;
- exactly 3 dates;
- all four treatments occur for every animal × date;
- every animal × date × treatment has at least 4 distinct successful trials;
- every retained trial has exactly 5 call rows;
- all required columns exist.

No threshold relaxation.

## Source B — main-experiment landing time

File: dataset_tc.csv  
Frozen md5: c6b1e0310d98c364e14a79dae4a27360

One row is one trial with bat_num, noise_sphere, time_flight_s and daynumber.

Proceed only if:
- five source-defined noise conditions are present;
- at least 3 bats have at least 5 successful trials at every noise level;
- those bats have at least 2 source days at every noise level;
- all retained time_flight_s values are finite and positive.

The retained bat set is defined only by this support rule.

If fewer than 3 bats remain:
STOP_MOVEMENT_ENDPOINT_SUPPORT.

## Boundary

This stage may report only structure:
columns, checksums, IDs, conditions, dates, counts and missingness.

Do not report source-level values, flight-time values, individual rankings, treatment effects or identity statistics.
