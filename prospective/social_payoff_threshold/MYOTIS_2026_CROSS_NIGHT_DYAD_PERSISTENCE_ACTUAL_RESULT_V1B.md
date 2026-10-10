# Myotis 2026: post-outcome exploratory repeat co-receiver dyad result V1b

**Status: ACTUAL original OSF source; DESCRIPTIVE POST-OUTCOME EXPLORATORY. No social-effect p-values, causal claims, 3D altitude, or measured prey captures.**

## Reproducibility and analysis sequence

- Original author data: Hernández-Montero et al. (2026), *Ecology and Evolution*, DOI 10.1002/ece3.73604, OSF node `sg6dz`.
- The V1a measure of shared same-station receiver within a 60-second original clock minute was **frozen before V1a outcomes** and found, separately, 17/28 pairs (20240515) and 14/28 (20240516); [successful original data workflow 38012845003](https://github.com/zuizui0223/batter/actions/runs/38012845003).
- **V1b was created after opening those aggregate margins**, so this is an explicitly **post-outcome descriptive follow-up**, NOT a prospectively registered independent result. The narrower [V1b lock](MYOTIS_2026_CROSS_NIGHT_DYAD_PERSISTENCE_EXPLORATORY_LOCK_V1B.md), committed `4e6ec44b054ead386567be2dcefe01c38d49dcda`, fixed identity cohort, binary J>0 endpoint, all four 2×2 cells, code-reuse invariance, no null/p-values, before **opening the 2-night individual pair intersection**.
- Executed the unchanged previously frozen `parse_events()` and `joint_minutes()` imported from `myotis_2026_one_minute_same_receiver_descriptive_v1a.py`, with the exact same 16 original files and the original published RSSI >-90dB filter.
- [Official successful GitHub Actions 38014108133](https://github.com/zuizui0223/batter/actions/runs/38014108133), code SHA `e7a9ab7dbd9fb5f738e494b1a28f7711f81ca84a`, job `114100485567`, artifact `myotis-2026-exploratory-cross-night-dyads-v1b`. The output checks re-established the original 17/28 and 14/28 source outcome margins; no per-tag, receiver, timestamp, coordinate, RSSI or kinship identity was printed, and no social p-value was calculated.

## Actual original-data dyad repetition table

| Original tagged-bat dyad J>0 at identical receiver within some minute | Count of the 28 fixed possible pairs |
|---|---:|
| Both 2024-05-15 and 2024-05-16 | **13** |
| 2024-05-15 only | **4** |
| 2024-05-16 only | **1** |
| Neither night | **10** |
| Total | **28** |

Check: May 15 =13+4=**17**, May 16 =13+1=**14**; union of positive dyads=18/28; descriptive across-night set Jaccard=**13/18 = 0.72222**. These are paired categorical descriptions of two source nights, **not** 28 biologically independent replication units.

**Do not misread the station requirement:** Each dyad must have **some** matching receiver and matching minute *within each night*; the original code does not require the co-detection to be at **the same particular receiver ID on both nights**. These are receiver-footprint co-detections, not observed near-contact or mutual awareness.

## Biological interpretation and competing explanations

The strong binary recurrence in this one cohort shows that the **recorded candidate pair-level minute co-use is not restricted to disjoint, once-only pairs**. This is an empirical intermediate behavioral-ecology descriptor linking published marginal UD overlap to time-conditioned source co-occurrence.

However:
- Pairs can be observed repeatedly simply because both animals have strong preference for a station neighborhood, high detection effort, or the same broad nightly activity period, even **with no attraction**. The original author already establishes individualized home ranges/kin-related overlap; repeat receiver co-use does not establish an independent new causal social strategy.
- A station (~35m detection radius) can detect animals potentially ~70m apart and within different seconds of the same minute; it measures co-detection rather than interactions. Event RSSI was only used for the published -90 dB quality threshold, not for fine distance.
- Unknown station-level uptime and synchrony errors could create apparently frequent co-use. All source timestamps are naive ISO; original author R uses `ymd_hms(timestamp)` default UTC parsing, but no independent ground-truth clock drift or physical timezone origin has been recovered.
- The May-2024 group in the original study has **zero published mother–daughter dyads** in its eligible UD pair cohort; no kinship effect can be tested here. The 28 possible pairs share eight bats, two nights cannot establish robust population-level repeatability.
- No measured 3D elevation, actual prey captures or local competition data; these co-use observations cannot validate the laboratory/Rhinolophus and tropical-fruit-bat JAE field mechanisms or adaptive payoff.
- No null/reference for expected synchronous co-receiver minutes conditional on marginal occupancy, hour, receiver uptime, site-day prey distribution and autocorrelation was calibrated. Therefore **no excess synchrony, temporal avoidance, choice, competition or cooperation is established**.

## Decision

**Supported, narrowly:** 13 of 28 fixed bat-tag pairs had at least one 1-minute same-station-receiver co-detection in both of two dated nights under the unchanged source rule.

**Unsupported and held:** Bat-specific social preference, causal avoidance, adaptation, exclusive/nonexclusive *3D vertical niches*, or a quantified deviation from independently expected social co-use.

Future work should first obtain/calibrate station uptime and synchronized event detection support. Do not add more post hoc time-window scans or interpret 13/28 as p<0.05. The V1a main result and frozen JAE main/release remain untouched.
