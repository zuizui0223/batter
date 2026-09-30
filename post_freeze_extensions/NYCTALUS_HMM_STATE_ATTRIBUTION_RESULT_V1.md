# Nyctalus support-matched HMM-state attribution result v1

## Status

**POST-OUTCOME MECHANISM LOCALIZATION; NOT CONFIRMATORY REPLICATION.**

Frozen contract:
`post_freeze_extensions/nyctalus_hmm_state_attribution/contract_v1.json`

Authoritative workflow:
- run: `36697105982`
- head: `95d65141ef2e8489b7ecda82134b88418d157e41`
- artifact: `11089086743`
- digest: `sha256:a855297a6cc26a9276be1d6d7ca1643d2d3bc3dfb1b9696c5210b9167560cca8`

Both models use the **same ARM/COM event pool**, the **same 27 individuals**, and are scored on the **same HMM-state-supported target events**.

## Result

- evaluable individuals: **27**
- support-matched collapsed gain: **+0.01210**
- HMM-state-conditioned gain: **+0.02401**
- paired state increment: **+0.01191**
- null-centered paired increment: **+0.00222**
- one-sided attenuation p(null <= observed): **0.5431**
- frozen attribution verdict: **FAIL**

Secondary support-matched calibration:
- collapsed calibrated excess: **+0.04821**, p = **0.0652**
- state-conditioned calibrated excess: **+0.05044**, p = **0.0707**

## Interpretation

Adding the source study's HMM movement-state labels does **not** reduce the same-individual vertical-identity advantage on matched support. The paired increment is slightly positive, not negative, and is indistinguishable from its permutation expectation.

Therefore the earlier contrast

- unconditioned centered test: n=36, p=0.0115;
- HMM-state-conditioned test: n=27, p=0.0707

must **not** be interpreted as evidence that behavioural-state mixture explains the Nyctalus signal.

When support and event pool are held fixed, the collapsed and state-conditioned effects are nearly identical:

- calibrated excess +0.0482 without state;
- calibrated excess +0.0504 with state.

The loss of conventional significance relative to the n=36 analysis is therefore consistent with the reduced support / smaller evaluable set rather than attenuation by HMM-state conditioning.

## Ecological consequence

This strengthens the cross-system mechanism-localization pattern:

> broad movement-state allocation is not supported as a sufficient explanation for centered vertical individuality.

In the original comparative archive, identity survives broad kinematic conditioning in 5/5 panels. In Nyctalus, independently generated ARM/COM labels likewise do not measurably attenuate identity on support-matched events.

This does **not** establish a successful externally replicated within-state identity effect because the state-conditioned calibrated test itself remains above the frozen p<=0.05 threshold (p=0.0707). It instead establishes a narrower but important point: **there is no evidence that conditioning on the available independent HMM state explains away the signal.**

## Claim boundary

- post-outcome mechanism localization only;
- ARM/COM are source-study HMM proxies, not exact feeding/resource identity;
- no claim that state is irrelevant at finer behavioural resolution;
- no claim of intrinsic morphology, memory, learning or personality;
- frozen JAE v0.3.8 remains unchanged.
