# Engineering receipt template v1

## Status

**TO BE COMPLETED AND FROZEN BEFORE CONFIRMATORY RANDOMIZATION.**

Pilot animals used to tune any quantity below are excluded from the confirmatory cohort.

## A. Matched family geometry

### Family A
- room / arena dimensions:
- start location:
- goal / reward location:
- obstacle coordinates:
- obstacle material:

### Family B
- room / arena dimensions:
- start location:
- goal / reward location:
- obstacle coordinates:
- obstacle material:

## B. Route graph correspondence

| Route class | Family A path | Family B path | graph-isomorphic? |
|---|---|---|---|
| R1 | TBD | TBD | TBD |
| R2 | TBD | TBD | TBD |
| R3 | TBD | TBD | TBD |
| R4 | TBD | TBD | TBD |

Canonical CONSTRAINED route:
**TBD**.

## C. Physical equivalence table

For every corresponding route record:

| Metric | A | B | difference |
|---|---:|---:|---:|
| shortest path length | TBD | TBD | TBD |
| minimum aperture | TBD | TBD | TBD |
| horizontal displacement | TBD | TBD | TBD |
| vertical displacement | TBD | TBD | TBD |
| obstacle count | TBD | TBD | TBD |
| nominal turn demand | TBD | TBD | TBD |

Any non-isomorphic difference must be justified before animal randomization.

## D. Tracking architecture

- tracking hardware:
- frame/sample rate:
- coordinate system:
- calibration procedure:
- expected position error:
- missing-frame handling:
- minimum raw rows per valid trajectory:
- minimum positive-dt intervals:

## E. Capability gate

- isolated traversals attempted per route:
- required successful traversals per route:
- maximum collision/failure fraction:
- minimum tracking support:
- family-level redesign trigger:

Capability screening occurs before randomization.

## F. Trial schedule

- acquisition sessions per family:
- trials per acquisition session:
- interleaving rule:
- rest interval:
- common-OPEN probe trials per family:
- early/late split:
- suppression trials:
- exact-reopening trials:
- transformed-transfer trials:
- late-acquisition history window m:

## G. Probe route classification

- deterministic topology rule for R1-R4:
- boundary/tie handling:
- failed/aborted flight handling:

No trajectory clustering is used to define route labels.

## H. Transformation map

Exact transformed-transfer operation:
- mirror / rotation / relabelling:
- coordinate map:
- route-class correspondence after transformation:

## I. Pilot firewall receipt

- pilot animal IDs:
- confirmatory exclusion verified:
- geometry changes made after pilot:
- tracking changes made after pilot:
- final apparatus freeze date:

## J. Freeze metadata

- repository commit:
- contract version:
- randomization script hash:
- endpoint code hash:
- frozen by:
- date/time: