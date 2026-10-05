# evsBat external fixed-policy validation result v1

## Status

**STOP — public evsBat tracking output is not dimensionally compatible with the frozen 3-D policy representation.**

Branch:
`prospective/task-reset-lockin-v1`

Parent:
- `EVSBAT_EXTERNAL_POLICY_PREFLIGHT_V1.md`
- `EVSBAT_PICKLE_SCHEMA_PROBE_AMENDMENT_V1.md`
- `EVSBAT_PICKLE_STRUCTURAL_STRINGS_AMENDMENT_V2.md`
- `EVSBAT_RESTRICTED_NDARRAY_METADATA_AMENDMENT_V3.md`

## Structural support recovered

The evsBat archive contains 47 candidate *Rhinolophus nippon* tracking pickles across five independent source-native individual IDs:

- 2670: 9
- 2681: 19
- 2860: 3
- 2868: 9
- 2899: 7

Thus individual replication itself is adequate.

## Safe pickle audit

The deterministically selected smallest candidate pickle was:

`rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_2868_17-3_particle1_lower.pkl`

Static pickle inspection found a NumPy-only object graph:
- `numpy.core.multiarray._reconstruct`
- `numpy.ndarray`
- `numpy.dtype`
- float64.

A restricted NumPy-only unpickler returned:
- top-level type: ndarray;
- shape: **19,232 × 3**;
- dtype: float64.

No arbitrary/project-specific class was executed.

## Source-defined column semantics

The public evsBat repository defines the event tracking pipeline unambiguously.

`trackParticlesC.py` constructs tracker input as:

`(x, y, time)`

and stores particle events as:

`events  # All events [(x, y, time), ...]`.

`particle_tracking.cpp` likewise defines:

`std::vector<std::tuple<int, int, float>> events;  // (x, y, time)`.

`splitTrajectory.py` writes the lower/upper event sets directly as NumPy arrays of those events.

Therefore the frozen 3-column lower pickle is:

**x pixel, y pixel, event time**

not a 3-D spatial `x,y,z` trajectory.

## Verdict

`STOP_EXTERNAL_INCOMPATIBLE_DIMENSION`

The fixed obstacle-flight policy representation requires:
- 3-D speed;
- absolute vertical speed;
- horizontal turning;
- 3-D path efficiency;
- vertical range.

These cannot be reconstructed from a single event-camera `x,y,time` array without introducing a new representation.

## No rescue

Do not:
- reinterpret time as spatial z;
- construct a 2-D substitute for the fixed axes and call it replication;
- drop the vertical components;
- infer 3-D coordinates from pixel trajectories without a source-defined calibration/reconstruction pipeline.

A future **new** 2-D policy study could use evsBat, but it is not an external validation of the frozen two-axis result.

## Consequence

The strongest current two-axis result remains internally held-out across seven obstacle configurations within the Teshima *R. nippon* cohort.

External validation of the fixed 3-D axes still requires an independent dataset with repeated individual-level **3-D** trajectories.
