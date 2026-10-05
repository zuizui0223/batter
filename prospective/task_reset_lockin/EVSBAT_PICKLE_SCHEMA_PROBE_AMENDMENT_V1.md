# evsBat one-member pickle schema probe amendment v1

## Status

**FROZEN BEFORE ANY PICKLE OBJECT IS EXECUTED OR NUMERIC TRAJECTORY VALUE IS INTERPRETED.**

Parent:
`EVSBAT_EXTERNAL_POLICY_PREFLIGHT_V1.md`

Stage-1 central-directory metadata found 47 candidate *Rhinolophus nippon* tracking pickles across all five source-native individuals.

## Deterministically selected schema member

Smallest candidate by uncompressed size:

- path: `rawdata/chamber/event_camera/R_nippon/particle_tracking_results_kiku_2868_17-3_particle1_lower.pkl`
- individual: `2868`
- ZIP compression method: 8 (deflate)
- CRC32: `34bb9458`
- compressed bytes: **101,716**
- uncompressed bytes: **461,730**
- local-header offset: **34,165,152**

This member was selected by the predeclared smallest-uncompressed-file rule, not by trajectory content.

## Authorized extraction

From Figshare `rawdata.zip`:

1. range-read the exact local header;
2. verify the frozen path;
3. range-read exactly the compressed member payload;
4. raw-deflate decompress;
5. verify uncompressed byte count and CRC32.

Do not use `zipfile.extract` or download the full archive.

## Authorized pickle inspection

Use Python `pickletools.genops` only.

Do **not** call:
- `pickle.load`;
- `pickle.loads`;
- `pandas.read_pickle`;
- `joblib.load`;
- `numpy.load`.

Report only:

- pickle protocol-related opcode names;
- referenced GLOBAL opcode arguments, if any;
- string opcode values matching case-insensitive structural keywords:
  - time
  - timestamp
  - frame
  - x
  - y
  - z
  - position
  - coordinate
  - track
  - trajectory
  - velocity
  - particle
  - points
  - xyz
  - centroid

Do not report numerical opcode arguments or arbitrary strings.

## Decision

If static inspection establishes a reproducible tabular/array structure that plausibly contains time + 3-D position, freeze a safe numeric-opening contract.

If not, STOP or freeze a narrower safe-load strategy before any numeric value is opened.
