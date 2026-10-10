# Frozen author-code clock semantics source gate, 2026-10-10

**Before any additional source inspection. No bat detection outcomes, receiver positions or dyad synchrony statistics may be opened.**

Original: Hernández-Montero et al., 2026 DOI 10.1002/ece3.73604, public OSF project `sg6dz`. The original `proximity_UD/scripts` directory was identified in successful OSF source-only metadata work, with resource ID `698daaafa731d64729dfc7aa`.

Motivation: prior event-clock QA (Actions 38012274824) found valid timestamps and receiver IDs in all sixteen bat×night files, but all timestamp strings lack an explicit timezone. The original paper says gateway synchronizes mobile and fixed logger times, but this does not by itself establish whether the processed `timestamp` column is local-clock, UTC, or converted consistently.

### Allowed metadata operation
Request **only** `https://api.osf.io/v2/nodes/sg6dz/files/osfstorage/698daaafa731d64729dfc7aa/`, plus the original author publicly published view-only token as fallback. Report directory child names/extensions/file sizes/source IDs only; do not follow file download URLs or any related data file; limit first page to <=100 names, record presence of more pages.

Potential next operation, only after a separate exact file-ID frozen contract: retrieve **source code text** if an R/Python script exists, sanitize and report only lines handling `timestamp`, `date`, timezone (`tz`, `UTC`, `local`), `ymd_hms`, `as.POSIXct`, or clock synchronization. Do not open bat event CSVs, output files, biologically sensitive exact roost coordinates or any individual time sequences.

The objective is an **author-code interpretability gate**, not a search for favorable bat co-detection outcomes. Any timezone ambiguity unresolved must keep `HOLD_TIMEZONE_AMBIGUITY`, and the previously frozen 1-minute time-conditioned co-use endpoint cannot execute. Two nights and eight biological tags are not sufficient to claim adaptive mechanisms or JAE 3D mediation.
