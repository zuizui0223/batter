# Source-defined 2026 Myotis foraging-window constants (code-only freeze V3)

**2026-10-10. Pre-author-constant read**. This is a narrow original author-Quarto **literal-constant inspection**, not an analysis of animal detection events. The original full-night V1a, post-outcome V1b and central-hour V2 results have already been seen; any future use of these constants on the two-night bat outcomes is **explicitly post-outcome sensitivity**, not a new confirmatory endpoint.

## Source prior evidence
Author [Hernández-Montero et al. (2026)](https://doi.org/10.1002/ece3.73604), original OSF `sg6dz`. [Successful CI 38015302389](https://github.com/zuizui0223/batter/actions/runs/38015302389) read **author source code text only** from original `proximity_UD/analysis/Appendix1_anonym.qmd` (source OSF resource `698dea461a7b213810c7311d`, advertised 68,621 bytes). Source snippets proved there are exact variables `thresh_time_start` and `thresh_time_end` with explanatory comments `two hours after sunset` and `three hours before sunrise`; the previous method-audit redacted their HH:MM literal values.

## Fixed permitted extraction

- Metadata identity (original file ID + name), exact size <=100KB; SHA256 of original text.
- **Only** statically inspect source code lines matching `^\\s*thresh_time_(?:start|end)\\s*(?:<-|=)\\s*["']([01]\\d|2[0-3]):([0-5]\\d)["']`, allowing trailing comments and optional whitespace. Output only assignment variable name, fixed **HH:MM** clock constant and sanitized comment type. The clock literals are author *methodological constants*, NOT sensitive bat observation timestamps.
- Report all occurrences and whether both start/end variables are defined uniquely; do NOT select arbitrary sets of values if repeated. If multiple values change by source season/batch or effective selection is unclear, `HOLD_AUTHOR_TIME_BOUNDARIES_AMBIGUOUS`.
- Also report **boolean only** whether original source code contains references to variables `thresh_time_start` and `thresh_time_end` in later filter logic, and whether original code explicitly sets `tz`, `force_tz`, `with_tz`, or `as.POSIXct` next to them. Do not print any original source context lines containing bat tags, receiver IDs, actual bat values, roost/coordinate paths or GPS.
- No execution of original Quarto/R scripts, no download of raw bat CSVs, no original data values examined, no dyadic tests or shift-window search.
- Do not convert clock boundary HH:MM to local sunrise/sunset/solar phase without a verified local timezone convention and year/day-specific astronomical data.
- The one pre-existing V2 23:00–02:00 logger-centered observational sensitivity remains distinct from original author foraging UD hours. This code-only check cannot prove station uptime or true clock synchronization.

**Decision:** method constants may be reported as author **source-clock processing cutoffs**, not local-solar times unless cross-verified. The original May cohort 7-of-8 eligibility for UD analysis is a separate unresolved source-selection issue.
