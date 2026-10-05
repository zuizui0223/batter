# Carollia independent 3-D structural preflight v1

## Status

**OUTCOME-BLIND EXTERNAL STRUCTURAL PREFLIGHT.**

Independent source repository:
`00keveland/Tunnel_2026`

Pinned commit:
`59928a71887d521fec143080b0b187736c046a0e`

Peer-reviewed source:
Eveland et al. (2026), *Looking ahead: echolocation and flight behaviors of two fruit bat species navigating a corridor*.

## Public cohort

Directory:
`Trial_Data_Carolia/`

Filename schema:
`C<bat>_<trial>_<date>_traj_bat_pos_RESULTS.mat`.

Metadata-only inventory fixes:
- C1: 2 files;
- C2: 3;
- C3: 4;
- C4: 5;
- C5: 5;
- C6: 4;
- C7: 3;
- C8: 4.

Dates:
- C1-C4: 20231216;
- C5-C8: 20231222.

## Source-code provenance

The public author code `Population_Analysis.m` reads:
- top-level `RESULTS`;
- `RESULTS.track.tSec`;
- `RESULTS.track.pos_sm`;

and treats `pos_sm` as 3-D position.

The public author code `carollia_build_track_from_calls.m` documents:
- `BAT.pos_call [K x 3]`;
- `BAT.tSec`;
- `BAT.pos_sm [T x 3]`;
- coordinates in meters;
- interpolation of call-localized positions to a continuous track.

## Authorized structural operation

For every `*_RESULTS.mat` in the pinned directory:
- download exact pinned bytes;
- calculate SHA256 for provenance;
- run `scipy.io.whosmat` only;
- report top-level variable names/classes/shapes.

Do not call `loadmat`.
Do not open any numeric array or struct field value.

## Structural PASS

Proceed only if:
- >=3 bats on 20231216 each have >=3 files containing a top-level `RESULTS` struct;
- >=3 bats on 20231222 each have >=3 files containing a top-level `RESULTS` struct.

Because C1 has only two public files, C1 is prospectively ineligible for the repeated-trial external primary.

No threshold relaxation.
