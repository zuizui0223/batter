# Co-use behavioural-context descriptive audit v1

## Status

POST-OUTCOME DESCRIPTIVE DIAGNOSTIC.

The synchronous vertical-separation result is already known. This audit does not add a hypothesis test and cannot rescue or invalidate any co-use verdict.

It uses x-y-time only.

## Purpose

Describe what kind of movement context generates the frozen primary co-use encounters, especially the supported 2023 panel.

## Frozen primary encounter universe

Exactly reconstruct the encounter set and SHA recorded in COUSE_PRIMARY_ENCOUNTER_RECEIPT_V1.

Abort if any encounter SHA differs.

## Stationary-like endpoint definition

Reuse the project's existing stationary-candidate definition:

For a fix within its individual session:
- both previous and next fixes exist;
- both adjacent time gaps are >0 and <=20 min;
- horizontal speed on both adjacent segments is <=0.5 m/s.

Such a fix is labelled stationary-like.

All other fixes are labelled not-stationary-candidate. This second class must not be interpreted as confirmed foraging or commuting.

For each encounter report:
- both endpoints stationary-like;
- exactly one endpoint stationary-like;
- neither endpoint stationary-like.

## Session-phase description

For every endpoint, define phase within its full target session:

phase = (timestamp - session start) / (session end - session start).

Classify:
- early: phase <0.2
- middle: 0.2 <= phase <=0.8
- late: phase >0.8.

Report encounter-level combinations and the fraction for which both endpoints are middle-session.

## Local horizontal speed description

For endpoints with valid adjacent segments:
- record the mean of the two adjacent segment speeds;
- summarize median and quartiles by panel and by stationary-like status.

No speed threshold other than the inherited 0.5 m/s stationary definition is used to create biological state labels.

## Interpretation ceiling

Allowed:
- co-use encounters are concentrated in stationary-like versus non-stationary-candidate movement contexts;
- co-use is concentrated in middle versus endpoint portions of sessions.

Not allowed:
- stationary-like = roosting;
- non-stationary = foraging;
- a behavioural context causes vertical separation;
- post-outcome state subsets become new primary tests.
