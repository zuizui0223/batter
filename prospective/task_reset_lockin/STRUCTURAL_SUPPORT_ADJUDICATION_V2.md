# Configuration-conditioned structural support adjudication v2

## Status

**AUTHORITATIVE OUTCOME-OPENING GATE. TRAJECTORY NUMERIC VALUES REMAIN UNOPENED.**

Branch:
`prospective/task-reset-lockin-v1`

Authoritative row-count workflow:
- run: **37205143446**
- artifact: **11304666912**
- artifact ZIP SHA256: `b69a5dfa4e6f13a5e1d67c8ffa3fafe17bbfb56e7b956df90215668d30f55947`

Parent:
- `STRUCTURAL_SUPPORT_AMENDMENT_V1.md`
- `ESTIMATOR_IMPLEMENTATION_CLARIFICATION_V1.md`

The workflow read raw CSV bytes only to verify checksums and count lines.
It parsed no Time/X/Y/Z/pulse value.

## Miniopterus fuliginosus

Frozen species batch:
19 CSV trajectories, bats A–D.

### Primary A

No environment contains >=3 bat identities each with >=2 repeated trajectories.

Verdict:
**STOP_A**

### Primary B after the pre-outcome usable-environment clarification

The later frozen clarification requires a Primary-B contributing environment to contain trajectories from >=2 distinct bats.

From filename/row-count structure:

- Env1: A only -> unusable;
- Env2: B, C, D -> usable;
- Env3: A, B, C, D -> usable;
- Env4: B only -> unusable;
- Env5: D only -> unusable;
- Env6: A only -> unusable;
- Env7: C only -> unusable.

Thus only **2 usable environments** remain.

Primary B requires focal individuals with >=3 usable environments.

No Miniopterus individual can satisfy that after the clarification.

Verdict:
**STOP_B**

No Miniopterus trajectory numeric value is authorized to open in this programme.

## Rhinolophus nippon

Frozen species batch:
45 CSV trajectories, bats A–E.

### Primary A structural support

Eligible repeated-route environments under the original gate:

- Env1: repeated bats B, C, D;
- Env2: repeated bats B, C, D, E;
- Env3: repeated bats C, D, E.

Thus 3 environments satisfy the >=3 repeated-bat rule.

Verdict:
**PASS_A_TO_COORDINATE_SUPPORT**

### Primary B structural support

Every Env1–Env7 contains >=2 bat identities in the public filename structure:

- Env1: B,C,D,E;
- Env2: B,C,D,E;
- Env3: A,C,D,E;
- Env4: A,B,C,D,E;
- Env5: A,D,E;
- Env6: A,C,D;
- Env7: A,B.

All five bats occur in >=3 such environments:
- A: Env3,4,5,6,7;
- B: Env1,2,4,7;
- C: Env1,2,3,4,6;
- D: Env1,2,3,4,5,6;
- E: Env1,2,3,4,5.

Verdict:
**PASS_B_TO_COORDINATE_SUPPORT**

The later coordinate-validity and feature-SD rules may still fail closed.

## Authorized next step

Open Time/X/Y/Z values **only for the 45 Rhinolophus CSV files**.

Do not open:
- Miniopterus CSV numeric values;
- pulse values for either species;
- kiku.pkl/yubi.pkl numeric payloads.

Run Primary A and B only if their full frozen coordinate-support rules remain satisfied.

## Interpretation boundary

This programme is configuration-conditioned.

No environment-order or relearning/reset-time claim is authorized.
