# Teshima environment-metadata audit v1

Outcome-blind source audit.

Purpose:
identify public non-trajectory files in Figshare article 29209493 that may encode obstacle/environment geometry for Env1–Env7.

Allowed:
- file id;
- filename;
- byte size;
- MIME type;
- download URL metadata.

Forbidden in this audit:
- downloading file bytes;
- reading trajectory coordinates;
- opening obstacle numeric values;
- fitting any behavioural model.

All article files are classified as:
1. Rhino trajectory CSV;
2. Mini trajectory CSV;
3. other.

The result reports all "other" files verbatim so a later numeric-opening contract can be frozen if an environment-geometry source exists.
