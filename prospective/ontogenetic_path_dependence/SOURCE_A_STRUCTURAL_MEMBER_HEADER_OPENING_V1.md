# Source A structural-member header opening v1

## Status

**FROZEN AFTER CENTRAL-DIRECTORY AUDIT AND BEFORE ANY ROW VALUE FROM THESE TABLES IS READ.**

Parent contract:
`SOURCE_A_GPS_ARCHIVE_INDEX_AMENDMENT_V1.md`

Archive:
`GPS data.zip`, Mendeley id `8bb38dce-f2d5-41b1-bb0e-8454957e8eee`.

The central-directory audit opened no archive payload and identified the following small structural members.

## Members authorized for extraction

| archive member | local-header offset | compressed bytes | uncompressed bytes | method | CRC32 |
|---|---:|---:|---:|---:|---|
| `GPS data/allPairs.xlsx` | 263 | 105,860 | 109,357 | deflate (8) | `b5b9b73c` |
| `GPS data/dataInfo_mompup.xlsx` | 109,821 | 10,180 | 12,788 | deflate (8) | `9a4ba028` |
| `GPS data/trees_mompup.xlsx` | 175,510 | 54,839 | 57,673 | deflate (8) | `19979c40` |

No other ZIP member is authorized.

## Allowed content inspection in this gate

For each XLSX:
1. fetch exactly the local header + the member's compressed payload by byte range;
2. decompress that member only;
3. verify uncompressed size and CRC32;
4. inspect workbook metadata:
   - sheet names;
   - used-range dimensions;
   - first-row column headers;
   - workbook relationship structure.

**Do not read row 2 or later.**

This gate is specifically to learn the structural field names before selecting which non-outcome columns may be read.

## Forbidden

- no `mom/data.mat` or `pup/data.mat`;
- no GPS coordinate files;
- no `allPairs_matlab.mat`;
- no pair-specific trajectory tables;
- no data rows from the three XLSX files;
- no route, distance, path-length, tree-use, or maternal/self prediction outcome.

## Next gate

After headers are known, commit an exact **structural-column value allowlist** before reading any row value.

Only fields necessary for:
- mother–pup identity;
- chronological night/date;
- developmental stage / independent-flight status;
- availability flags;
- exact destination/drop-off identity needed for support counting

may be promoted.

Any route-derived or biological response field stays unopened until the route estimator contract is frozen.
