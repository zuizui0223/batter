# Cross-night persistence of receiver-minute co-detection: exploratory lock V1b

**2026-10-10. POST-OUTCOME EXPLORATORY, NOT PREREGISTERED CONFIRMATION.** The previously pre-frozen source and RSSI/clock rules, V1a, have already yielded 17 of 28 dyads with same-receiver/same-minute co-detection on 2024-05-15 and 14 of 28 on 2024-05-16. Those count margins were viewed before proposing this extension.

## Narrow supplementary question
Of the **same fixed 28 unordered pairs** from the original eight cross-night verified tagged bats, how many pairs show **at least one** same-receiver/same-minute bin (J>0) on **both original dated nights**?

The explicit possible numerical overlap range given the previously opened margins is max(0,17+14-28)=3 through min(17,14)=14. The actual shared-pair count is UNOPENED when this note is committed.

## Fixed analysis, no degrees-of-freedom search
- Reuse **exact same** original 16 OSF resources, date and source IDs, author's ISO-naive clock-minute convention, and published RSSI > -90 filter from `MYOTIS_2026_DESCRIPTIVE_RECEIVER_MINUTE_AMENDMENT_V1A.md` and executed V1a script.
- Import previous `parse_events()` and `joint_minutes()` functions directly. Recompute the exact V1a margins as an invariance check (17/28,14/28), rather than modifying the processing pipeline.
- The only new statistic is the count of 28 pairs with J_15>0 **AND** J_16>0. Report also the simple fixed 2×2 categorical pairing table: both nights positive, May 15 only, May 16 only, neither; sum exactly 28. No individual physical IDs, receiver IDs, pair labels, raw times, RSSI values or coordinates emitted.
- Optional complementary Jaccard overlap of the two sets: intersection/(17+14-intersection), deterministic from the table. No other thresholds, time windows, or models.
- No p-value, confidence interval, bootstrapping, permutation, social encounter or avoidance claims. Repeated *detected co-receiver minute* does not mean stable individual reaction norms; common receiver choice and nonrandom station uptime alone can explain repeated positive J.
- Biological sampling n remains 8 tagged bats and 2 source nights. 28 dyads are highly dependent because bats recur across dyads. Both nights are from the same broad period and not a study of lifelong social memory.
- No insight into 3D height, echolocation, prey captures or adaptive payoff.

## Stop and source integrity
If the imported V1a frozen source/quality or margins disagree, **STOP_SOURCE_OR_MARGIN_DRIFT** and do not display a new overlap number. Never report a third or revised choice of time bin because of an unfavorable overlap count.

Status prior to opening: `EXPLORATORY_CROSS_NIGHT_PAIR_BINARY_OVERLAP_NOT_YET_EVALUATED`.
