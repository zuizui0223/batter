# Public 3-D external-candidate metadata preflight v1

## Status

**OUTCOME-BLIND EXTERNAL DATA DISCOVERY.**

This preflight is downstream of the frozen *Rhinolophus nippon* transparent two-axis policy:
- FlightIntensity;
- ManeuveringExtent.

No external candidate may redefine those axes.

## Candidate A — pregnancy flight-room dataset

Study:
Taub, M., Mazar, O. & Yovel, Y. (2023).
*Pregnancy-related sensory deficits might impair foraging in echolocating bats*.
BMC Biology 21:60.

Public dataset:
- Mendeley id: `hbb2t3dnbc`
- version: 1
- DOI: `10.17632/hbb2t3dnbc.1`

The paper reports:
- 20 tracking cameras;
- 3-D flight room;
- bat ID and trial number;
- five pregnant and five post-lactating bats in the analyzed comparison.

## Candidate B — adaptive learning / recall dataset

Study:
Taub, M. & Yovel, Y. (2021).
*Adaptive learning and recall of motor-sensory sequences in adult echolocating bats*.
BMC Biology 19:164.

Public dataset:
- Mendeley id: `wccbjdrrsg`
- version: 1
- DOI: `10.17632/wccbjdrrsg.1`

The paper reports:
- five individually identified bats;
- repeated landings across environmental stages;
- a large 3-D flight room recorded by 20 tracking cameras;
- a long-term environment switch and recall design.

The Mendeley landing-page description says "Acoustic results generated for analysis", so raw 3-D movement support is uncertain and must be checked without opening values.

## Allowed operation

For each Mendeley dataset read only public metadata:

- snapshot title/DOI/version/publish date;
- folder ids/names/parents;
- file ids;
- filenames;
- file sizes;
- hashes;
- content types.

Do not download file contents.

## Structural triage

Classify each candidate into one of:

- `RAW_3D_PLAUSIBLE`
  - filenames/metadata explicitly indicate raw or trial-level 3-D coordinates, motion capture, trajectories, X/Y/Z, Vicon, or equivalent;

- `SUMMARY_ONLY_PLAUSIBLE`
  - files appear to contain derived sensory/movement summaries but not raw trajectories;

- `UNCERTAIN_NEEDS_HEADER_ONLY_OPENING`
  - spreadsheets/MAT/archives are present but filenames do not establish whether raw 3-D coordinates exist;

- `STOP_NO_RELEVANT_MOVEMENT_FILE`
  - metadata establishes no plausible movement/trajectory source.

## No rescue

A summary-only file cannot be treated as external validation of the fixed two-axis 3-D policy.

If raw 3-D support is absent, it may still be useful for a separate mechanistic context study but not for the fixed-axis replication.
