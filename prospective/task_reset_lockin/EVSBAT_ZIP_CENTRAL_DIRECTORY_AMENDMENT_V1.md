# evsBat ZIP central-directory opening amendment v1

## Status

**METADATA-ONLY ARCHIVE INDEX OPENING. NO ARCHIVE MEMBER CONTENT MAY BE DECOMPRESSED.**

Parent:
`MORPHOLOGY_LINKAGE_PREFLIGHT_V1.md`

Figshare file:
- article 29150924 v2
- `rawdata.zip`
- file id 58421782
- bytes 5,957,619,580
- MD5 `bf669a6a3d2a439d660f8ee92d86cf5f`

## Purpose

Determine whether the archive's source-native directory/member names expose:
- individual bat IDs;
- explicit A–E labels;
- body-mass / weight tables;
- morphology tables;
- metadata/crosswalk files;
- session/date names that could establish correspondence with the obstacle-flight archive.

## Authorized operation

Using HTTP Range only:

1. read the final <=131,072 bytes to locate the ZIP EOCD/ZIP64 records;
2. recover central-directory offset and size;
3. range-read the central directory;
4. parse only central-directory file headers;
5. report only:
   - member pathname;
   - compressed size;
   - uncompressed size;
   - compression method;
   - CRC32;
   - directory/file flag.

## Forbidden

Do not:
- fetch any local-file data region;
- decompress any member;
- read member file headers beyond what is needed for the central index;
- infer individual linkage from numeric trajectory content;
- use matching sample size alone.

## Linkage decision

If member names themselves expose an exact crosswalk or source-native matching identifiers, freeze a narrow member-opening contract.

If member names provide no reproducible A–E correspondence, do not open arbitrary large raw members searching for a match. The same-individual morphology route remains unestablished unless a clearly relevant small metadata member is identifiable by name.
