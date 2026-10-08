# Route-availability × acoustic masker: physical bench gate v1

## Status
**NO ANIMAL DATA / NO ROOM CALIBRATION MEASUREMENTS.** Frozen engineering specification and structural/diagnostic validator only. The JAE RC2 manuscript, Behavioral Ecology draft, original PR #72 and all synthetic identifiability branches remain unchanged.

Parent candidate study: `prospective/colony_acoustic_identity/FOUR_ROUTE_OPPORTUNITY_X_MASKING_PERFORMANCE_DESIGN_V1.md`. This gate is NOT evidence that a four-route intervention buffers masking, and running its code does not authorize animal testing.

## Physics problem to solve before animals
Experimental route availability is R=0 (only canonical path R1 physically open) vs R=1 (four available paths R1–R4). Acoustic masker M=0/1 is assigned independently. Changing the path gate may itself change reflected echoes and masker shadowing **at exactly the same physical point on R1**, even before the bat chooses another path. An observed R×M interaction in success cannot then be attributed cleanly to availability of alternative routes alone.

The key distinction is:
1. **Apparatus contamination**: changing route gate changes target echo, noise or perceived acoustics on the same canonical R1.
2. **Legitimate route-opportunity mechanism**: with all four routes available, the bat may choose R2–R4 whose true acoustic field differs from R1; this is the potential ecological buffering pathway, not noise to 'control away'.
3. **Other effect**: route path length, maneuver cost and safe clearance change under gating, potentially interacting with masker even if sound level were fixed.

Do not demand equal acoustic field across DIFFERENT routes: that would remove the very physical variation a route-choice buffering hypothesis needs. Demand credible matched calibration at **fixed points** on R1 across closed/open gate, while mapping absolute soundfields for all four routes when open.

## File contract, frozen before field/room measurement
No supplied real records exist in this branch. A future technician must make two source files.

`bench_manifest.json`:
- `source_id` nonempty, `acoustic_band_hz` two *facility-provided* ordered Hz values, `mic_calibrated` true, `transmitter_calibrated` true;
- `source_dataset_sha256` exactly 64 lowercase hex chars for the raw measurement package (not computed from the manifest itself);
- `anchor_points`: 2–25 canonical R1 physical points, with unique `point_id`, 3D coordinates `x_m, y_m, z_m`, and fixed receiving/probe orientation, plus canonical `station_id`.
- `alternative_points`: an array of mapped physical R2–R4 positions for an open-gate ecological opportunity map; site-recorded geometry plus `route_id` R2/R3/R4 and matched `station_id`, no invented locations;
- `bench_repeat_floor`: must be >=3 **independent bench repeated setups** (distinct day/setup IDs); repeated waveform FFT bins or time frames are not independent bench setups;
- `max_allowed_fixed_point_snr_gate_bias_db` and `max_allowed_fixed_point_snr_gate_x_masker_interaction_db`, `max_allowed_fixed_point_echo_change_db`, `max_allowed_fixed_point_background_change_db`: positive tolerances chosen by pilot engineers/acousticians **before reading these measurements**, with a calibration/behavioral rationale. No arbitrary default numerical acceptance tolerance is implemented.
- `min_clearance_m` and `max_acceptable_target_loss_db`: pilot-validated limits, positive; `max_safe_peak_db_spl`: independently approved physical exposure limit chosen before measurement. This is NOT a bat welfare threshold selected by this model.

`bench_acoustics.csv` one calibrated summary per physically independent setup×fixed probe point×configuration:
- `point_id`, `repeat_id`, `route_open` (0/1), `masker_on` (0/1), `target_echo_db_spl`, `background_db_spl`, `max_peak_db_spl`, `measured_clearance_m`;
- echo/noise SPL computed in the SAME frozen frequency band, microphone/receiver orientation and target reward point; all fields physically measured, not simulated.
- canonical anchor R1 points must appear in all FOUR R×M cells for each repeat; alternative points R2–R4 appear only for `route_open=1`, both masker conditions, with comparable matched sampling.
- no missing bat/audio outcomes can be filled in with zeros, no frequency-band changing to make an endpoint fit.
- physical clearance must be verified per route/condition, not inferred from acoustic spectrum.

## Strict structural / physics indicators (not inferential animal tests)
For each canonical anchor point and repeat, define acoustic SNR (S=E-N) in dB as measured target-echo SPL E minus background masker/noise SPL N.

- `gate_bias_sham = S(R=1,M=0) - S(R=0,M=0)`
- `gate_bias_masker = S(R=1,M=1) - S(R=0,M=1)`
- `gate_x_masker = gate_bias_masker - gate_bias_sham`.

Also **test** the absolute gate changes in both **target echo** and **background level** separately against their own pilot-declared positive tolerances: a zero net SNR change can hide equally large changes in both signals. This requirement is part of the initial physics audit, not a post-hoc outcome rescue. All four acoustic tolerances in manifest (SNR gate bias, SNR interaction, target-echo absolute gate change, background-noise absolute gate change) are required and checked against the **maximum absolute of all anchor×repeat contrasts** (engineering conservative worst-case; may be too strict in real room). Report individual point summaries, not just mean. Do not call small mean a proof of no acoustic contamination.

Distinctly for accessible alternatives with R=1/M=1, report the measured range of acoustic SNR relative to the canonical R1 point at matched path stations. This is a **possibility map**, not evidence of bat pathway choice or ecological advantage; mechanical and sensory effects need separate endpoints.

## Stop/fail-closed rules before analyzing animals
- Missing manifest, no real bench measurements, uncalibrated equipment, source-file hash missing or mismatched, missing predeclared tolerances, insufficient independent repeated setups, missing an R1×M cell, duplicated probe×repeat×condition, invalid units, nonfinite values, or implausible positive clearance => `STOP_BENCH_SOURCE_OR_STRUCTURE`.
- If physical measured R1 gate response exceeds either predeclared limit, => `STOP_ROUTE_GATE_ACOUSTIC_CONFOUND` (cannot interpret a pure route-availability×masking bat test as designed, though an alternative joint-route-and-echo manipulation could be newly preregistered).
- If physical clearance falls below predeclared min or max peak exposure exceeds independently approved facility safe limits, => `STOP_PHYSICAL_SAFETY_OR_REWARD`.
- `PASS_PHYSICS_BENCH_ONLY` means calibrated apparatus constraints met; **not** animal study authorization and not evidence of masking-buffering benefit. Behavior/intake and received actual bat-ear soundscape remain distinct.
- To establish a credible gain from alternative routes, need independent physical-route quality and acoustic response maps showing choices are available and non-equivalent; do not precommit positive effect at this stage.

## Guard on statistical inference
The future bat 2x2 success interaction uses one bat per R×M block and **BAT** as the unit. The test of no interaction with potentially nonzero R and M main effects is NOT equivalent to the globally sharp null of no treatment, so all 4!^B reassignment does not automatically give an exact p-value. Physical bench probes likewise are NOT independent bats or pseudo animal samples.

## Implementation boundary
A dependency-free validator must accept EXACT file paths, assert all predeclarations, compute conservative anchor contrasts and physics flags, print JSON; never generate substitute measurements, p-values, synthetic biological effect sizes or declare causal masking buffer success. Only self-test may use explicitly labeled tiny **dummy** values to exercise arithmetic and fail-closed guards.

### Pre-execution software correction to the frozen engineering description
Before any real bench outcome or completed CI test, the initial implementation review recognized that matching SNR alone plus a one-sided echo-loss limit would allow target echo and noise level to both shift by equal large amounts. The explicit absolute echo-change AND absolute background-change tolerances above repair this observational blind spot. No physical observations were opened or scientific acceptance values chosen in making this correction.
