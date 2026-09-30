# Nyctalus support-matched source-RSF resource-context attribution result v1

## Status

**POST-OUTCOME MECHANISM LOCALIZATION; FINAL SAME-SOURCE NYCTALUS MECHANISM FAMILY.**

Frozen contract:
`post_freeze_extensions/nyctalus_resource_context/attribution_contract_v1.json`

Authoritative workflow:
- run: `36701810706`
- head: `913273a8bcea6b799e3b51eb9f5bd89755e25f79`
- artifact: `11090789820`
- artifact digest: `sha256:59a214a10daef8a8f47125c8f7f31efc78336ca99c446677d9fe3a3bbdab661a`

Frozen selected context:
- 5-km horizontal cell;
- source HMM state (ARM/COM);
- source-defined closest-potential-roost distance: 0–0.5 / 0.5–2 / 2–5 / >5 km;
- source `main_clc2_ratrel` local 50-m land-cover classification.

The base and context models are scored on **identical context-supported target events**.

## Result

- evaluable individuals: **20**
- support-matched HMM-state base gain: **+0.02470**
- + potential-roost-distance × local-land-cover gain: **+0.06693**
- paired context increment: **+0.04223**
- null-centered paired increment: **+0.02871**
- one-sided attenuation p(null <= observed): **0.8204**
- frozen attribution verdict: **FAIL**

Support-matched calibrated identity:
- HMM-state base: **+0.04355**, p = **0.1228**
- + resource context: **+0.07226**, p = **0.0768**

## Interpretation

Conditioning on the source study's measured potential-roost distance and local land-cover context does **not** attenuate centered vertical individuality.

The paired context increment is positive rather than negative, and there is no evidence that the richer context removes same-individual predictive information.

Therefore the measured pathway

> repeated allocation among broad movement states, radial position relative to potential roosts, and local 50-m land-cover classes

is **not supported as a sufficient explanation** for the Nyctalus centered vertical-individuality signal.

This result is consistent with the earlier support-matched findings:
- HMM movement-state conditioning did not attenuate identity;
- distance from track start / central-place flight stage did not attenuate identity.

Together they push the unresolved Nyctalus mechanism beyond these measured context-mixture explanations.

## What remains live

This result does **not** exclude:
- exact occupied roost identity;
- exact feeding trees or prey patches;
- sub-50-m habitat or corridor structure;
- local wind / uplift / boundary-layer exposure;
- wing morphology / wing loading;
- memory, experience or learned routes;
- individual-specific environmental reaction norms.

The source field `DistanceAssumedRoostsInKm` is distance to the closest **potential** roost, not verified actual roost occupancy. The land-cover field is habitat context, not exact food-resource identity.

## Stop rule

Per `NYCTALUS_SAME_SOURCE_STOP_RULE_V1.md`, no further same-source context variants, subgroups, grids, state definitions, turbine variables or endpoint variants are opened after this result.

Further progress requires:
1. a genuinely new external source under a separately frozen programme; or
2. new field data with repeated cross-individual overlap in exact resource/route × behaviour × local-environment contexts.

The frozen JAE v0.3.8 submission remains unchanged.
