# Pickle string-metadata opening amendment v1

## Status

**FROZEN BEFORE ANY PICKLED NUMERIC ARRAY OR CSV TRAJECTORY ROW VALUE IS OPENED.**

Parent:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- `CSV_HEADER_OPENING_ALLOWLIST_V1.md`

## Purpose

Resolve whether the two Figshare pickle files encode deterministic links between:
- species aliases `kiku` / `yubi`;
- environment;
- bat identity;
- trial/file identity.

## Authorized files

- `kiku.pkl` — Figshare file id 55033988
- `yubi.pkl` — Figshare file id 55033991

## Authorized operation

For each pickle:

1. request only the first **8 MiB** by HTTP Range;
2. require HTTP 206 Partial Content;
3. do **not** call `pickle.load`, `joblib.load`, `numpy.load`, pandas, or torch;
4. inspect raw bytes only for printable ASCII/UTF-8 tokens matching a strict whitelist:
   - `Env[0-9]+_Bat[A-Za-z]+_no[^\\x00\\r\\n ,;]+(?:\\.csv)?`
   - `Env[0-9]+`
   - `Bat[A-Za-z]+`
   - literal tokens `kiku`, `yubi`, `Rhinolophus`, `Miniopterus`, `species`, `environment`, `trial`, `filename`.

Do not report arbitrary printable substrings.

## Forbidden

Do not:
- decode or summarize numerical array payloads;
- inspect floating-point values;
- infer species from trajectory geometry or file size;
- infer trial order from numeric trajectory contents;
- use pickle execution.

## Decision

If whitelisted tokens deterministically expose file/species mapping, freeze it.

If they do not, species mapping must rely on independent source documentation or remain unresolved.

This step cannot authorize a temporal reset claim.
