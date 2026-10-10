# 2026 Myotis: fixed prospective temporal co-use estimand (NOT YET EXECUTED)

**2026-10-10, BEFORE time/receiver co-detection outcomes.** This is a prospective observational hypothesis for original OSF sg6dz. Do NOT execute it until event-clock/receiver source QA V6 passes and unit/clock/source monitoring conditions are met. No bat timestamp, station-use overlap, dyad co-detection or physical coordinates have been analyzed for the outcome as of freeze.

## Precise scope, prior art, and cohort

Original source: Hernández-Montero et al. (2026), Ecology and Evolution DOI 10.1002/ece3.73604. Author published individual UDs, site fidelity and kinship-associated **marginal spatial** overlap using the 65-station BLE grid. Station radius is treated conservatively as roughly 35m, with 2-second sampling and activity schedule 21:00–05:00. Do not claim the first demonstration of bat space sharing, individualized home ranges, or a social ecology result.

Categorical OSF gate [CI 38012020164](https://github.com/zuizui0223/batter/actions/runs/38012020164) showed 8 distinct original *bat-tag* CSV series with stable unique RFID and transmitter identifiers across dated files 2024-05-15 and 2024-05-16. This is **NOT** verified simultaneous occupation. Eight potential bats imply `8 choose 2 = 28` possible dyads; the original paper's May-2024 batch reports eight tagged, seven retained for UD overlap, and **zero mother–daughter dyads in that batch**. Hence **no kinship hypothesis is testable in this specific two-night subset**.

The only candidate extension is whether time-resolved same-receiver co-detection differs from expectations conditioned on each tagged bat's marginal receiver and broad hour-of-night use, rather than generic UD overlap.

## Source QA gate before running ANY outcome

Require:
- V6 genuine-source 16-file timestamp/receiver-key QA with >=95% valid timestamps and receiver IDs;
- timestamp origin/zone consistent across bats and both source nights, no unresolved naive timezone interpretation unless verified from original author code;
- validated receiver uptime/coverage or explicit inability to distinguish non-detection from station outage (then HOLD for inference);
- strict handling of duplicate timestamps, 2-sec technical beacon pseudoreplication, simultaneous multi-receiver recording and equipment synchronization; receiver footprints overlap physically;
- original covariates may not be used to select a favorable cohort or station after co-detection results;
- core behavioural data files cannot be used to infer actual prey capture, sensory interference, vertical altitude, detailed trajectories or biological contacts.

**If any clock/coverage requirement fails: `STOP_TEMPORAL_COUSE_INFERENCE`; do not select an alternative convenient time scale or a new cohort after values.**

## One frozen descriptive target, conditional on admissible source

Define 1-minute source-clock bins nested in each independently observed **bat-tag × dated-night × hour**. A bat is marked "detected at receiver r" in minute m if the verified, timestamped original file includes >=1 eligible station detection in that bin; do not interpret 2-second technical rows as individual visits. Multiple station detections per minute remain a set (not independently repeated contacts).

For each unordered physical dyad (i,j) and sampling night n, define `J_ijn` as the number of 1-minute bins in which both individuals were recorded by **the same stationary receiver**. Count each dyad×minute at most once regardless of multiple receivers. Report the total number of source-supported dyad×night records and the number with at least one synchronous same-receiver bin, plus median per-dyad conditional co-use; do NOT print receiver identifiers, fine locations, individual-specific maps/times or exact tag RFID.

The numerator `J` is an operational **same-receiver simultaneous-bin** metric, NOT contact, aggression, social cooperation or intentional joint foraging. Preselect one 1-minute bin as a coarse receiver-footprint overlap indicator, not an estimated body separation or biologically proven social-interaction threshold.

## Observational reference / falsifier, only if QA passes

A companion noncausal surrogate should independently rotate each animal's entire within-hour 1-minute receiver-presence sequence by a fixed hour-specific offset sampled from `{10,15,...,50}` minutes, applied **uniformly across all receiver channels of that bat in the same hour**, while holding nighttime/day assignment, the original bat's receiver occupancy, broad hour-of-night activity and 1-minute multi-station correlations fixed. Compute the same `J` for 999 prespecified pseudorandom surrogate realizations (seed 202610101000), with exact identical bat×night/hour support. Compare observed `J` with the surrogate distribution descriptively. No permuted bat IDs, because individual detection support and variance differ. Explicitly display that circular shift disrupts boundaries and may fail if receiver outages and prey/roost departures are synchronized at finer time scales.

This is NOT a randomization test of a bat decision, cannot control unobserved station uptime, and its nominal tail proportion is NOT a population-level p-value. Do not promote it to a confirmatory ecological avoidance result. With two nights and repeated dyads sharing bats, avoid treating 28 dyads as statistically independent biological replicates.

If source QA reveals shared station outage or severe 1-minute missingness, stop at an occupancy description without surrogate "avoidance" inference. If station-only data suggest no repeatable excess, do not claim equivalent synchrony or absence of competition.

## Three rival explanations even if J differs

1. **Temporal avoidance**: bats are physically present at overlapping stations but offset in time because of conspecific interaction. Needs approach/arrival causal intervention or independent close-proximity sensing to identify.
2. **Time-specific prey or roost resource response**: bats independently exploit the same prey/habitat in similar/different times, causing apparent synchrony/asynchrony without responding to each other.
3. **Detection/availability artifact**: overlapping station receiver footprints, logger uptime, source batching, RSSI threshold and common darkness schedule generate apparent co-detection or suppression.

No possible result here identifies prey capture reward, acoustic masking or the mechanism maintaining JAE field 3D vertical-shape identity. Same bat/receiver observations are an *independent middle layer*, not the final payoff experiment.

**Status on freeze:** `NOT_EXECUTED_OUTCOME_LOCKED_PENDING_V6_SOURCE_QA`. The only authorized next step is checking V6 engineering receipts, not looking for favorable overlap scores.
