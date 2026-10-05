# Carollia v7.3 MAT metadata amendment v1

## Status

**TECHNICAL AMENDMENT FROZEN BEFORE ANY MOVEMENT ARRAY VALUE IS READ.**

Parent:
`CAROLLIA_EXTERNAL_STRUCTURAL_PREFLIGHT_V1.md`

The first structural attempt established only that the public trial MAT files are MATLAB v7.3/HDF5 containers. `scipy.io.whosmat` therefore cannot inspect them.

No `RESULTS` field value, track coordinate, time series, or movement outcome has been opened.

## Authorized replacement operation

For every pinned `*_RESULTS.mat` file:

1. open the container read-only with an HDF5 reader;
2. inspect HDF5 object metadata only:
   - group/dataset path;
   - object type;
   - shape;
   - dtype;
   - attribute names and scalar/text attribute metadata only where required to identify MATLAB class;
3. recursively list paths only under:
   - root;
   - `RESULTS`;
   - descendants needed to establish the presence of `track`, `tSec`, and `pos_sm`.

Do not index or materialize any numerical dataset value.

## Structural PASS

A file passes if the HDF5 metadata contains a reproducible route from `RESULTS` to source fields corresponding to:
- `track.tSec`;
- `track.pos_sm`.

The same prospective count threshold remains unchanged:
- on 20231216, >=3 bats with >=3 passing files;
- on 20231222, >=3 bats with >=3 passing files.

## Forbidden

Do not:
- call `dataset[...]`, `dataset[()]`, or NumPy conversion on HDF datasets;
- follow object references to inspect numerical values;
- calculate movement features.

This amendment changes only the metadata reader required by the file format.
