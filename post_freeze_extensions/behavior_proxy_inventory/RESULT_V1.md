# Behaviour-proxy inventory v1

## Status

**HEADER-ONLY POST-FREEZE INVENTORY. No vertical outcomes were summarized.**

Authoritative workflow:
- run: `36512982578`
- head: `31b4a85fb6f6df613eed7ce23647417e76bcbae2`
- artifact: `11010182186`
- digest: `sha256:a0240013c4d0a92973d4294e27bb8b959d71adc744a8dbd17eca2dac9af2c26d`

## Result

No source provides a harmonized direct behavioural-state field such as foraging, feeding, activity or social state across all five comparative panels.

Common candidate GPS fields across all five:
- `ground_speed`
- `sensor_type`
- `event_id`

Additional fields:
- *Eidolon* and *Hypsignathus*: `heading`, `eobs_speed_accuracy_estimate`
- the three *Phyllostomus* panels: no common heading field

Reference tables provide no candidate behavioural fields under the frozen keyword inventory.

## Consequence

A direct foraging-vs-commuting test is not possible from the harmonized public columns. The next common proxy should therefore be derived from x-y-time kinematics. Because speed-only conditioning already retained vertical identity in 5/5 panels, the next test adds path tortuosity/turning intensity to the state definition.

This inventory does not modify the v0.3.8 submission.
