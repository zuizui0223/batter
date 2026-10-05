# Older-history allocation persistence result v1

## Status

- **2022: SUPPORTED.**
- **2023: UNSUPPORTED.**

Authoritative workflow:
- run: **37295628817**
- job: **111716031103**

Parent:
`OLDER_HISTORY_ALLOCATION_PERSISTENCE_CONTRACT_V1.md`

## Question

After completely removing the focal individual's most recent prior session, does deeper personal history still predict the next allocation state better than deeper histories of conspecifics?

## 2022

- (K_{older}=+0.34147)
- positive individuals: **25/32 = 78.1%**
- targets: **160**
- null mean: **-0.01500**
- null 95% interval: **[-0.09465,+0.06639]**
- one-sided p: **0.0001**
- verdict: **SUPPORTED_OLDER_HISTORY_PERSISTENCE**

Stricter descriptive requirement of >=2 older sessions after removing the latest:
- K=+0.21334
- 19/27 positive = **70.4%**
- 128 targets.

Thus the 2022 strict-past result is not reducible to the immediately preceding session.

## 2023

- (K_{older}=+0.14170)
- positive individuals: **5/7 = 71.4%**
- targets: **20**
- null mean: **-0.01126**
- null 95% interval: **[-0.34851,+0.29507]**
- one-sided p: **0.1713**
- verdict: **UNSUPPORTED_OLDER_HISTORY_PERSISTENCE**

Stricter descriptive >=2 older sessions:
- K=+0.09989
- 5/7 positive
- 13 targets.

The positive direction is retained descriptively, but the frozen calibrated primary fails and must not be promoted.

## Inference

A pure one-step inertia explanation is insufficient for **2022**, because personal information remains after the latest session is removed.

The same deeper-history result is **not established in 2023**.

Therefore the field data do not support a universal fixed memory depth. Temporal maintenance strength is heterogeneous across years and/or support regimes.

Importantly, this test concerns the one-dimensional allocation axis A. It does not define the persistence timescale of the full two-dimensional H/V policy carrier.

## Claim ceiling

Supported:
- deep personal-history information beyond the latest session in 2022.

Not established:
- a universal long-memory process;
- cognitive memory as the carrier;
- deeper-history persistence in 2023;
- a fixed decay law.

## JAE firewall

Post-JAE mechanism diagnostic only. No change to v0.4.0.
