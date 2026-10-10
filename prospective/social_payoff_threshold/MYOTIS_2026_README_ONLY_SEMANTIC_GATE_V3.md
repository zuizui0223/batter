# 2026 Myotis original OSF README-only semantic gate V3

**Pre-README content freeze, 2026-10-10.** The previous two-day header-only GitHub Actions run 38011479273 verified that two actual `data/sn_prox` files (`0A62_20240515.csv`, `0A62_20240516.csv`) have identical headers:
`timestamp,date,batdate,time,rx,tx,rfid,dyad,rssi,batch,box,grid_sn,lon_sn,lat_sn,records`.
Only their **first** header line was opened. All original rows 2+ remain unexamined. The initial algorithm's negative field classification was merely omission of compact `rx/tx/rfid/dyad` aliases; this has been corrected in a separate source-schema-only commit.

To establish what these fields mean BEFORE opening categorical IDs, inspect only the publisher-linked **original OSF root README.md**, public resource ID `698dc7add062fca4f5dfc63d`, metadata-declared length 1517 bytes, under exact canonical path:
`https://osf.io/download/698dc7add062fca4f5dfc63d/`
after verifying `https://api.osf.io/v2/files/698dc7add062fca4f5dfc63d/` returns that exact file ID/name.

Allow redirect only to prior source-verified regional/object storage HTTPS hostnames `files.de-1.osf.io` and `storage.googleapis.com` (besides `osf.io`, `api.osf.io`, `files.osf.io`); do not log signed URLs. Read at most 2048 bytes total and refuse binary non-text.

Allowed output:
- README SHA256 and length;
- first-party **schema-definition lines only** mentioning `rx`, `tx`, `rfid`, `dyad`, `sn_prox`, `receiver`, `sender`, `bat` or `date`, truncated to 200 chars each and stripped of URL query strings/coordinates;
- explicit indication whether the author explains bat↔RFID crosswalk and independent session/nights.

Do not download CSV contents, preview RSSI, timestamps or longitude/latitude rows, nor infer **confirmed biological cross-night same-bat records** merely from header fields. If README lacks definitions, mark `HOLD_SEMANTICS_UNVERIFIED` and defer to an independently frozen categorical-only physical-animal-ID×night structural gate. No statistical behavioral endpoints.
