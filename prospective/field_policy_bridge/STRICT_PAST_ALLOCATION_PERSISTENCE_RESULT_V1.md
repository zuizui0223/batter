# Strict-past allocation persistence result v1

## Status

**SUPPORTED in both 2022 and 2023 under the frozen rule.**

Authoritative workflow:
- run: **37295249991**
- job: **111714823378**

Parent:
`STRICT_PAST_ALLOCATION_PERSISTENCE_CONTRACT_V1.md`

## Question

Does a bat's strictly prior allocation history predict its next eligible session better than strictly prior histories of conspecifics?

Allocation axis:

[
A=(H-V)/\sqrt{2}.
]

Histories use only sessions with start time strictly before the target.

## 2022

- (K_{past}=+0.37266)
- positive individuals: **26/32 = 81.25%**
- targets: **160**
- prior-self sessions: median **4**, range **2–13**
- null mean: **-0.00800**
- null 95% interval: **[-0.07976,+0.07161]**
- one-sided p: **0.0001**
- verdict: **SUPPORTED_STRICT_PAST_MAINTENANCE**

Descriptive recent-history sensitivities:
- most recent one session: K=+0.33704, 28/34 positive;
- most recent two sessions: K=+0.33960, 23/32 positive.

## 2023

- (K_{past}=+0.27201)
- positive individuals: **6/7 = 85.7%**
- targets: **20**
- prior-self sessions: median **3**, range **2–4**
- null mean: **-0.00828**
- null 95% interval: **[-0.27341,+0.27480]**
- one-sided p: **0.0258**
- verdict: **SUPPORTED_STRICT_PAST_MAINTENANCE**

Descriptive recent-history sensitivities:
- most recent one session: K=+0.34141, 9/11 positive;
- most recent two sessions: K=+0.34522, 7/7 positive.

## Inference

Strictly prior personal history predicts future allocation better than histories of other bats in both years.

This establishes temporal self-predictiveness, but by itself does not distinguish:
- one-step inertia;
- deeper accumulated history;
- stable morphology/performance;
- repeated task/resource structure.

The latest-session-exclusion test is the required discriminator for immediate inertia.

## JAE firewall

Post-JAE mechanism diagnostic only. No change to v0.4.0.
