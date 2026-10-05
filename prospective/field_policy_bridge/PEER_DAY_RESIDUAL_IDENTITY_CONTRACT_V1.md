# Peer-day-adjusted residual identity contract v1

Status: post-outcome stable-component falsification diagnostic.

Question: after removing the allocation tendency shared by contemporaneous peers on the same source day, do sessions from the same biological individual remain more similar than sessions from other individuals?

Data:
- P. hastatus 2022 and 2023 separately.
- Use the exact peer-day-adjusted allocation values already defined in PEER_DAY_ADJUSTED_STATE_CONTRACT_V1.md.
- Do not alter the fixed-bin 360-s session definitions.

Eligibility:
- individual has at least 2 peer-day-adjusted sessions;
- target has at least one other self session;
- at least 2 other donor individuals are eligible.

Target statistic:
- self centroid = mean adjusted allocation over the focal individual's other sessions;
- donor centroid = mean adjusted allocation for each other individual;
- K_q = equal-donor mean absolute distance to donor centroids minus absolute distance to self centroid.
Aggregate equally within individual, then equally across individuals in the year.

Null:
- within each frozen cohort, shuffle the exact individual-label multiset across complete adjusted session values;
- preserve cohort, adjusted value, source time/day, and the session-count multiset;
- recompute eligibility and the full statistic.

9,999 permutations.
Seeds:
- 2022 = 202610051571
- 2023 = 202610051572

Support requires:
- year-level K > 0;
- one-sided p <= 0.05;
- at least 70% of evaluable individuals have positive individual K;
- at least 9,500 valid permutations.

Interpretation:
- supported: a stable individual-specific component remains after shared peer/day variation is removed;
- unsupported: evidence for an autonomous stable individual parameter is weak after shared temporal structure is controlled.

This diagnostic tests residual individual identity only. It does not identify morphology, learning, physiology, or self-reinforcement.
