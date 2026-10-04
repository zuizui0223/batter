# Source A GPS archive-index amendment v1

## Status

**FROZEN BEFORE ANY MEMBER OF `GPS data.zip` IS EXTRACTED.**

This amendment authorizes inspection of the ZIP **central directory only** for Source A.

Dataset:
`gpcg9m5758`, version 1.

Archive:
- filename: `GPS data.zip`
- Mendeley file id: `8bb38dce-f2d5-41b1-bb0e-8454957e8eee`
- size: **1,546,850,907 bytes**
- SHA256 published by Mendeley metadata:
  `e93836ca08452c4fbe5bba55be54a5f6bd23ccf1f136ce7d649ed5f17f433fea`

## Purpose

The published Source A MATLAB code references structural metadata files inside this archive, including:
- `allPairs.xlsx`;
- `dataInfo_mompup.xlsx`;
- `allPairs_matlab.mat`;
- `trees_mompup.xlsx`;
- pair folders with `mom/` and `pup/` subfolders.

Before any archive member is opened, determine whether these files exist, their exact archive paths, compressed/uncompressed sizes, compression method, CRC, and local-header offsets.

## Allowed operation

Use HTTP byte-range requests only to:
1. read the ZIP end-of-central-directory / ZIP64 records if needed;
2. read the central-directory bytes;
3. list member metadata.

Total downloaded bytes for this audit must be bounded to **<= 16 MiB**.

Do **not**:
- download the whole archive;
- decompress any member;
- read local file payload bytes;
- inspect any GPS coordinate value;
- calculate any biological outcome.

## Output

Report:
- whether byte ranges are supported;
- total archive member count;
- exact metadata for filenames matching:
  - `allPairs`;
  - `dataInfo_mompup`;
  - `trees_mompup`;
  - per-pair `.xlsx`;
  - `/mom/`;
  - `/pup/`;
- a compact summary of top-level pair folders;
- no route content.

## Next gate

If small structural members are present, a **new member-extraction allowlist** must be committed before any such member is decompressed.

The route/GPS payload remains closed regardless of this index result.
