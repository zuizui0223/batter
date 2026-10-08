# Public bat–moth pursuit 2024: independent source structure gate (categorical only)

**DATE:** 2026-10-08. **EVIDENCE TYPE:** repository metadata, original README and ID/date table only. No position, pulse, target-alignment, flight-trajectory, sensory outcome or ecology effect values opened. No reanalysis of source's published result.

## Source

- Nishiumi, Fujioka & Hiryu (2024), *Current Biology*, “Bats integrate multiple echolocation and flight tactics to track prey”, doi: https://doi.org/10.1016/j.cub.2024.05.062
- Original source: https://github.com/Nozomi-Nishiumi/target_tracking_strategy_in_bats
- Original README: https://github.com/Nozomi-Nishiumi/target_tracking_strategy_in_bats/blob/main/README.md
- Source **categorical only** ID/date table: https://github.com/Nozomi-Nishiumi/target_tracking_strategy_in_bats/blob/main/basic_info/ID_table.csv

The original repository genuinely exposes per-session `E01`–`E18` tracking and ultrasound-pulse CSVs, original figure-generating R scripts, and `basic_info/ID_table.csv`. However, the original README describes target tracking of prey, not a crossed, within-occasion randomized 3D obstacle challenge/reference protocol.

## Categorical support (not biology outcomes)

- **18 labelled experimental sessions**, **7 distinct bat ID values** (1–7).
- Distinct recorded experiment **dates per bat**:
  - ID 1: **3** dates (20100930, 20101004, 20101006), **4** sessions (E01, E02, E03, E05).
  - ID 2: **1** date, **1** session (E04).
  - ID 3: **1** date, **1** session (E06).
  - ID 4: **2** dates, **2** sessions (E07, E08).
  - ID 5: **2** dates, **3** sessions (E09, E17, E18).
  - ID 6: **2** dates, **4** sessions (E10, E11, E15, E16).
  - ID 7: **2** dates, **3** sessions (E12, E13, E14).
- Multiple sessions on the **same calendar day** are not automatically independent occasions. The structural source alone does not document washout or an independent bat×reference/challenge contrast in every session.
- No individual has four distinct dated sessions; at most one ID has three separate dates. The 18 files are **not 18 independent animals or 18 independent days**.
- Source information visible does **not** verify the preregistered two-level matched physical 3-D obstacle contrast measured for every bat on >=4 independent occasions, randomized challenge order and sensor/device crossover.

## Frozen source-gate decision

**STOP_NOT_ELIGIBLE_FOR_FOUR_OCCASION_CROSSED_CHALLENGE_PRIMARY.**

Why: (1) no verified per-bat four independent day-level occasions; (2) no verified controlled within-occasion obstacle challenge/reference; (3) no verified device crossover, and (4) raw bat–moth tracking sessions are not automatically matched obstacle-performance interventions.

This is a **source-structure stop**, not a claim that the published bats show no stable policy, and not a criticism of the original study's own research question. The original data may support entirely different ecological or sensory questions, but those need independently justified prospective endpoints rather than repurposing them after seeing the eligibility shortfall.

**Firewall:** do not read response magnitudes or retrofit an endpoint to rescue this STOP; do not pool sessions/dates across bats or treat individual prey pursuits as independent bat-level occasions. No bat behavioural effect is produced by this audit.
