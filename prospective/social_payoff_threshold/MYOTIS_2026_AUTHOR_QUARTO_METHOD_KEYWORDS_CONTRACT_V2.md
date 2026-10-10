# 2026 Myotis: exact author Quarto method-keyword source gate (V2)

**Frozen 2026-10-10, prior to inspecting original Quarto text.** This follows the independently successful source-only [two-directory catalog run 38015195249](https://github.com/zuizui0223/batter/actions/runs/38015195249). This is an author-analysis **code-text inspection**, NOT a behavioral data analysis, not a new sunrise-aligned result, and not a new bat spatial interaction null.

## Exact source allowlist from original OSF sg6dz/analysis catalog

- `Appendix1_anonym.qmd`, OSF resource **698dea461a7b213810c7311d**, metadata size 68,621 bytes;
- `Appendix2_anonym.qmd`, OSF resource **698dea4664f82861d0e2544a**, metadata size 13,562 bytes.

Verify exact OSF resource `data.id`, name, and max 100 KB respectively via `https://api.osf.io/v2/files/{id}/`. Then retrieve only `https://osf.io/download/{id}/` using previously source-verified HTTPS hosts `osf.io`, `api.osf.io`, `files.osf.io`, `files.de-1.osf.io`, `storage.googleapis.com`. Do NOT follow other redirects or links in downloaded text.

## Extract, sanitize, and restrict

The ONLY output is:
- original file name, exact source file size and SHA256;
- totals of lines matching pre-fixed methodological keyword families below;
- at most 25 sanitized individual **source text code** lines per file, each <=180 chars, selected by:
  - `sunset`, `sunrise`, `dusk`, `dawn`, `solar`, `night`, `daylight`, `time_zone`, `timezone`, `tz\s*=`, `with_tz`, `force_tz`, `ymd_hms`, `as.POSIXct`, `UTC`;
  - `duration`, `threshold`, `uptime`, `offline`, `saturation`, `battery`, `missing`, `grid`, `two nights`, `UDOI`, `filter`, `group_by`, `rfid`, `batdate`.
- Before printing: strip all URLs, absolute/relative filesystem paths, any GPS/location columns (`lat\w*`, `lon\w*`, `coord\w*`, `roost\w*`, `box\w*`), any raw RFID or hexadecimal IDs of >=4 characters, and all exact numeric literal tokens including time-of-day. **Prefer keyword counts** if lines cannot be safely redacted.
- No bat CSV downloads, spreadsheet output tables, published result numerics, GPS or receiver coordinates, source script execution, observed dyad stats or social p-values.

**Use evidence status only**: `HOLD_SUN_CLOCK_AVAILABILITY_NOT_ESTABLISHED` unless unambiguous source code explicitly documents conversion/filters AND independently linked station-uptime coverage. Even valid author sunset/sunrise code alone is insufficient for a causal temporal avoidance analysis.

## Scientific priority and prior art

Same-site Melber et al. 2013 (doi:10.1111/eth.12123) already showed space sharing by kin without frequent co-foraging in *Myotis bechsteinii*. Kerth et al. 2001 (doi:10.1007/s002650100352) established roosting together/foraging apart. The 2026 study explicitly cites this work as rationale for its receiver-grid layout. Thus the novelty claim `first bat space/time dissociation` is definitively blocked. Our two-night receiver-minute descriptors are **technical/observational intermediate records**, not a new ecological law.

**STOP** after a single file-code audit if no independent clock/roost-window and uptime definitions can be established. Do not resume cherry-picked post hoc time windows.
