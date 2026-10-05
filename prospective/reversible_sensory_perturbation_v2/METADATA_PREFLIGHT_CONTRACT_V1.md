# Reversible sensory perturbation Dropbox metadata preflight v1

## Status

**OUTCOME-BLIND NETWORK/METADATA PREFLIGHT.**

Parent:
`SOURCE_RECEIPT_V1.md`

## Allowed request

Use the exact source-declared Dropbox shared-folder URL.

Allowed operations:
- HTTP HEAD;
- redirect following;
- response headers only.

Do not read/download the response body in this first preflight.

## Report

- requested URL host/path, with query retained only as the source-native dl flag;
- final resolved host/path;
- HTTP status;
- Content-Type;
- Content-Length if supplied;
- Content-Disposition if supplied;
- Accept-Ranges;
- redirect count.

Do not print cookies, tokens, signed query values, or authorization headers.

## Proceed rule

A file-inventory programme may proceed only if the shared source remains publicly resolvable.

If the endpoint resolves to a ZIP/download:
- report its size if available;
- freeze a maximum download budget before any content is downloaded.

If only an HTML landing page is available:
- a separate no-outcome page/schema inventory must be frozen before parsing.

## No outcome opening

No Dropbox body bytes may be consumed by this preflight.
