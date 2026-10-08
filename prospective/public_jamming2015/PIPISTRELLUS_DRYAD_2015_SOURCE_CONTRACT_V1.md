# Dryad 2015 Pipistrellus jamming raw calls — source-only eligibility v1

**Freeze before opening bat acoustic values.** Independent source/structural gate, NOT new biological test; JAE and PR #72–89 unchanged.

## Immutable source

Amichai, Blumrosen & Yovel 2015, Proc R Soc B 282:20152064; DOI 10.1098/rspb.2015.2064. Dryad dataset 10.5061/dryad.8f0v4, native filename Dryad.xlsx, approx 1.81 MB; official Dryad file-stream link https://datadryad.org/downloads/file_stream/68296. This is call-derived acoustic data, NOT verified synchronized raw 3D tracks. No source version substitution.

PUBLISHED ALREADY: Four trained Pipistrellus kuhlii exposed to playback of self, another bat, multiple conspecifics, clutter-self, self time-reversed, dense self duty-cycle, and reference/no-masker contexts. Changes of intensity, duration and frequency are already published, as is 61% across-condition individual call classification (Figure 6). Hundreds of thousands of calls do not increase the number of biological bats. Manipulation sessions occur on separate days; pulses within a session are dependent.

## Gate 0: source bytes
Retrieve only official Dryad public file, limit to 8 MiB, record HTTP status, file bytes, original SHA256 and XLSX magic. Do not put raw workbook into GitHub. On failure STOP_RAW_SOURCE_INACCESSIBLE. No numerical outcomes may be opened during this check.

## Gate 1: schema only
Read XLSX ZIP container workbook sheet names, sheet dimension metadata and first header row per sheet without reading numeric call data. Identify whether source includes:
- stable bat ID across sessions;
- actual jamming condition, duty cycle, clutter and unjammed control;
- recording session/flight/date, not just call index;
- emitted intensity/duration/frequency/interval feature with units;
- any trial-level success/collision endpoint (optional).
If no reliable bat ID or session key, stop rather than treating pulses as separate biological units.

## Gate 2: source-defined categorical support, only if Gate 1 passes
Read only bat IDs, masker labels, clutter, sessions and feature missingness (not magnitudes). Require:
- four physically identified bats (as published);
- at least three source-defined playback conditions per bat including control;
- at least two independent sessions per bat that support within-bat control-versus-playback contrasts;
- for the reversible self-call hypothesis, original SELF versus REVERSED SELF with similar duty-cycle, present across at least 3 bats with independent session support.
If source fails, report STOP_ACOUSTIC_SESSION_GRAIN_UNIDENTIFIED or STOP_NO_MATCHED_MASKER_REVERSAL with exact reasons.

## Gate 3: separate outcome contract ONLY if eligible
If all structural criteria hold, before reading feature magnitudes lock ONE hypothesis: same spectral content but temporally reversed self-masker causes a different within-bat emitted call-compensation vector (duration/intensity/frequency) relative to original self-masker after accounting for duty-cycle, clutter and session. Use independent bat/session clustered uncertainty, no pulse-level pseudoreplication, and an explicit prior-art check (no claim if already answered in paper). With n=4 bats inference remains narrow.

Do not infer spatial-acoustic tradeoffs unless synchronized XYZ, bat identity and call joins are documented in source. Do not rescope significant posthoc subsets, fabricate independent replications or reopen frozen Rhinolophus original data.
