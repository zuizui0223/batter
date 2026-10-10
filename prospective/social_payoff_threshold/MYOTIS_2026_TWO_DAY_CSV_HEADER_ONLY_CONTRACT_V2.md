# Myotis 2026: two-source file CSV header-only gate V2 (source-frozen)

**2026-10-10 — BEFORE any CSV content opening.** This is solely a source-schema eligibility check. The root OSF identity, data folders, date folder names and resource IDs were established by successful GitHub Actions metadata-only runs 38010699176, 38010744981, 38010792711, 38010881468, 38010935844, 38010983448, 38011050723 and 38011119952. No real bat detection rows have been read in these jobs.

## Precisely frozen allowlist

Only inspect the **first CSV header line** of the same named original receiver station file from two independent dated directories:
- `0A62_20240515.csv`, official OSF file resource **698dad850d35ac498ec72cd3**, metadata-declared 150,481 bytes;
- `0A62_20240516.csv`, official OSF file resource **698dadb876b09fd62fe255fe**, metadata-declared 38,503 bytes.

Allowed OSF routes (same frozen file IDs only):
- `https://api.osf.io/v2/files/{resource-id}/` — original JSON file metadata and OSF download link identity;
- `https://osf.io/download/{resource-id}/` — original file URL;
- `https://files.osf.io/v1/resources/sg6dz/providers/osfstorage/{resource-id}?action=download` — original resource provider link, if canonical identity and HTTPS host verified.

Only read up to one first line from each resource, capped at 2048 bytes and containing a newline. Use HTTP Range when possible; if the remote server streams more data, do not parse, print or iterate any subsequent rows. Verify source name/resource ID through official JSON metadata first, and require a CSV/comma header, not a numerical event row. No S3 or third-party URL redirect allowed in this phase. If the exact host/identity is inaccessible, `STOP_CSV_HEADER_ACCESS`.

## Authorized output

For each of the two files: source ID, declared original filename, HTTP status, whether header successfully read, and up to 25 field names. Detect field *presence* for:
- stationary receiver key;
- mobile sender key;
- timestamp/date/time;
- RSSI/signal;
- any separately declared **physical bat identifier** field distinct from a sensor's physical MAC/tag address.

No bat tags, numeric timestamps, visit counts, receiver coordinates, RSSI values, movement, or biological co-detection numbers may be opened/printed.

**This does not verify** that a mobile sender key is one biological individual across separate days; physical-bat↔tag mapping and independent same-dyad night coverage require a separate pre-frozen categorical source gate. Repeated receiver filenames are NOT a multi-bat repeated identity proof.

Status only: `HOLD_EVENT_SCHEMA_ONLY_REQUIRES_BAT_ID_CROSSWALK` on successful compatible headers, `STOP_CSV_HEADER_ACCESS` on unreachable, `STOP_UNEXPECTED_CSV_HEADER_SCHEMA` on invalid/discordant structure. No empirical effect, social synchrony or JAE 3D claim is authorized.
