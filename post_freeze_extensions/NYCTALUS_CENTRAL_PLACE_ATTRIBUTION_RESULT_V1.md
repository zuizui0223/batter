# Nyctalus support-matched central-place attribution result v1

## Status

**POST-OUTCOME MECHANISM LOCALIZATION; NOT CONFIRMATORY REPLICATION.**

Authoritative workflow:
- run: `36700377387`
- head: `2fa7690d04b7b6d0a39a505264e8ce2446ea4a62`

Frozen context:
- n = **22**
- 5-km cell × source HMM state
- distance from track start bins: 0–0.5 / 0.5–2 / 2–5 / >5 km
- both models scored on identical distance-context-supported target events.

## Result

- support-matched HMM-state base gain: **+0.02903**
- + distance-from-start context gain: **+0.05830**
- paired context increment: **+0.02927**
- null-centered paired increment: **+0.01551**
- attenuation p(null <= observed): **0.6886**
- frozen attribution verdict: **FAIL**

Support-matched calibrated identity:
- HMM-state base: **+0.04103**, p=0.1466
- + distance-from-start: **+0.05654**, p=0.1232

## Interpretation

Conditioning on distance from the start of each source track does **not** attenuate centered vertical individuality. The paired difference is positive rather than negative.

Thus the reduction in support caused by matching flight-stage context cannot be interpreted as evidence that individual differences are merely caused by repeated allocation to different radial stages of a central-place flight.

A start-distance proxy is not a verified daytime-roost distance, so this result is superseded mechanistically by the source-RSF potential-roost/resource-context test when that result is available.
