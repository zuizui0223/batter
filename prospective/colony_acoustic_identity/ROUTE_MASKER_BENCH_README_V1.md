# Physics-first bench gate: how to use it

**This directory contains no actual calibrated room measurements and NO observed biological result.** The validator is an engineering prerequisite for any new bat acoustic opportunity × masking experiment. Do not attach it to JAE results or the separately frozen PR #72 history experiment.

## Source package the facility must produce
1. Save `bench_acoustics.csv` with exactly these columns (one row per true independent bench setup, physical point and masker/gate condition):

```
point_id,repeat_id,route_open,masker_on,target_echo_db_spl,background_db_spl,max_peak_db_spl,measured_clearance_m
```

Every predefined point R1 has **all four route_open × masker_on cells** in **at least three independent hardware setups**. Points on R2/R3/R4 have both masker levels when all routes are open. A microphone timeseries/FFT bin is NOT a new independent setup.

2. Freeze `bench_manifest.json` BEFORE reviewing numeric measurements, including calibrated acoustic band, hardware provenance, SHA256 of the exact `bench_acoustics.csv` bytes, true 3-D sample coordinates, matched longitudinal station IDs, tested probe orientations, and facility-calibrated thresholds. These thresholds MUST come from independent apparatus/behavior and safety rationale. The code supplies none. Required numeric threshold keys:

```
max_allowed_fixed_point_snr_gate_bias_db
max_allowed_fixed_point_snr_gate_x_masker_interaction_db
max_allowed_fixed_point_echo_change_db
max_allowed_fixed_point_background_change_db
max_acceptable_target_loss_db
min_clearance_m
max_safe_peak_db_spl
```

Additional manifest fields are documented in `ACOUSTIC_BENCH_IDENTIFIABILITY_GATE_CONTRACT_V1.md`. No raw bench data or sound files are supplied by this repo branch.

## Running the validator
```bash
python prospective/colony_acoustic_identity/validate_route_masker_acoustic_bench_v1.py --self-test

python prospective/colony_acoustic_identity/validate_route_masker_acoustic_bench_v1.py \
  --manifest /path/to/predeclared/bench_manifest.json \
  --csv /path/to/real/bench_acoustics.csv \
  --out /path/to/physics-only-result.json
```

The self-test uses explicitly labeled DUMMY 58 dB echo/42 dB background values to exercise software invariants, never field-derived bat data. It verifies correct format, gate-only acoustic interaction detection, source hash mismatch, duplicate physical setups, and an important cancellation trap where both echo and background shift **+2 dB** but their net SNR does not change. The self-test thresholds are arbitrarily chosen software fixtures and cannot be used as physiological/safety thresholds.

## Interpret results narrowly
- `STOP_BENCH_SOURCE_OR_STRUCTURE`: missing or invalid real apparatus input, source hash mismatch, omitted matched cells or insufficient independent setups.
- `STOP_ROUTE_GATE_ACOUSTIC_CONFOUND`: moving a physical route gate changes recorded acoustics on the SAME common canonical path beyond facility predeclared limits.
- `STOP_PHYSICAL_SAFETY_OR_REWARD`: calibrated physical clearance / peak exposure outside facility limits.
- `PASS_PHYSICS_BENCH_ONLY`: the declared physical and acoustic tolerances were met, **not** that animal intervention is approved, that individual flight choices are learned, or that extra routes measurably improve foraging success.

Changing the gate could affect the soundscape without moving the bat. Separately mapped SNR differences along R2–R4 may provide opportunity for auditory buffering, but only a future randomized physiological and behavioral test can establish that bats exploit those differences to improve task outcomes. Difference-in-differences in future bat success cannot be given a naive Fisher exact p-value under a pure interaction null in the presence of main effects.

**No animal welfare authorization, real source recording or acoustic calibration has been performed through this software.**
