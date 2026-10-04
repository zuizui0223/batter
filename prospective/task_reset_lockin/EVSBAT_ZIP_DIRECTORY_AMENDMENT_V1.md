# evsBat ZIP central-directory opening amendment v1

## Status

**OUTCOME-BLIND CROSS-SOURCE IDENTITY AUDIT.**

Parent:
`MORPHOLOGY_LINKAGE_PREFLIGHT_V1.md`

The public evsBat Figshare record exposes one 5.96-GB `rawdata.zip` file. Metadata alone does not reveal individual IDs.

This amendment authorizes reading the ZIP directory structure only.

## Authorized source

Figshare article:
`29150924`, version 2.

File:
- id: `58421782`
- name: `rawdata.zip`
- bytes: `5,957,619,580`
- MD5: `bf669a6a3d2a439d660f8ee92d86cf5f`

## Authorized network reads

Use HTTP byte-range requests only to:

1. read the final <=128 KiB needed to locate the standard ZIP end-of-central-directory record and, if present, the ZIP64 locator;
2. if ZIP64 is required, read only the ZIP64 end-of-central-directory metadata record;
3. read exactly the central-directory byte range identified by those records.

Maximum central-directory read:
**64 MiB**.

If the directory exceeds this ceiling or the server ignores Range requests:
**STOP**.

## Authorized parsing

From central-directory entries report only:

- filename/path string;
- whether the entry is a directory;
- top-level directory name;
- central-directory entry count.

Do not report:
- compressed or uncompressed byte sizes per entry;
- CRCs;
- local-header offsets;
- timestamps;
- file contents.

## Linkage question

Search source-native path strings for explicit identity structure relevant to *Rhinolophus nippon*, including but not limited to:

- species directory names;
- individual names/IDs;
- A–E labels;
- subject tables;
- weight/body-mass filenames;
- metadata/CSV filenames.

Do **not** infer identity from:
- file count;
- recording order;
- directory size;
- date alone;
- matching number of animals.

## Pass condition

Proceed to a file-header/value allowlist only if the directory contains a reproducible source-native identifier or table that can plausibly crosswalk evsBat individuals to the obstacle-flight A–E identities.

If no such crosswalk structure exists:
**STOP exact same-individual morphology attribution**.

No raw event, video, wingbeat or body-mass value is authorized here.
