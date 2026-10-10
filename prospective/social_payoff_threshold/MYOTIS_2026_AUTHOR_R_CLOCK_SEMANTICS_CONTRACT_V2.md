# Fixed original author R-script clock-semantics inspection V2

**2026-10-10, pre-content freeze.** This is an original author **code-only** source gate, not analysis of bat trajectories or receiver events.

Previous official OSF author-script metadata run [38012537614](https://github.com/zuizui0223/batter/actions/runs/38012537614) verified the exact original file `proximity_UD/scripts/func_cAKDE_amt_v2.R` (48,503 bytes), resource ID `698dbbf6a779a96a01e24de0`. A `sub_functions/` folder also exists but is **not authorized** in this step.

The aim is to determine whether this named R code documents any clock conversion rules needed to interpret a field-source `timestamp` column that was parsed as valid but lacked timezone offsets in all 16 original bat×night files (QA V6 `HOLD_TIMEZONE_AMBIGUITY`). The published article describes synchronization through a gateway, but common clock origin after processing is unverified.

## Exact allowed source and output
- Verify OSF file metadata name/resource ID via `https://api.osf.io/v2/files/698dbbf6a779a96a01e24de0/`.
- Retrieve ONLY `https://osf.io/download/698dbbf6a779a96a01e24de0/` with the prior whitelist of OSF regional/object-storage redirect hosts, max 80KB.
- Parse R code as UTF-8 text. Output its SHA256, size, and **sanitized only** lines matching `timestamp`, `as.POSIXct`, `ymd_hms`, `lubridate`, `timezone`, `tz=`, `tz ` or `UTC`, at most 25 lines ≤180 characters each. Remove URLs, file paths, numeric values, fixed tag/device identifiers, potential coordinates, comments containing sensitive location information. NEVER print full script or raw line numbers linked to GPS data.
- No bat CSV downloads, no co-detection times, RSSI, lat/lon, physical roost or receiver keys, behavioral effect sizes.
- If no clock time-setting code can be unambiguously identified: `HOLD_AUTHOR_SCRIPT_DOES_NOT_RESOLVE_TIMEZONE`. Do not automatically interpret ISO-naive timestamps as UTC, local German time or mixed epochs.
- If a parser explicitly assigns timezone, report its literal setting **only if clearly local to the input `timestamp` pipeline**, not a constant used to annotate plots or convert external metadata. If ambiguous: HOLD.

This source gate cannot establish logger drift or station downtime and does not authorize temporal co-use inference. It is not a new bat behavioral result.
