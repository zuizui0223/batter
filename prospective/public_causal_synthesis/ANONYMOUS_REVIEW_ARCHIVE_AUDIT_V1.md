# Anonymous review archive audit v1

## Status

**PASS — SANITIZED REVIEW ARCHIVE CONTENT VERIFIED.**

Workflow:
- `public-causal-anonymous-review-archive-v1`
- run: `37568870331`
- artifact ID: `11460245697`

Artifact wrapper:
- GitHub artifact digest: `sha256:6acaef0d0c6d805938aa2964582d01709aec0cf03334936a8379efc09c512100`.

Inner deterministic review ZIP:
- filename: `behavioral_ecology_anonymous_review_archive_v1.zip`;
- bytes: **2,486,086**;
- builder SHA256: `66030317a2fbe7726eb955950040544582f7a19b39e6c8bc2d8e6d8937cf4a86`;
- independently re-hashed after artifact download: **same SHA256**.

## Content audit

Inner archive file count:
**90**

Contains:
- Complete Anonymous Text;
- source-analysis contracts;
- executable source-analysis scripts;
- frozen numerical result receipts;
- synthesis evidence matrix / numeric ledger;
- figure scripts and SVGs;
- supplementary draft;
- source-data manifest;
- permitted mirrored CC0 Carollia source subset;
- SHA256 manifest and provenance metadata.

## Anonymization scan

Scanned all text-like files and paths for:
- `zuizui0223`;
- `github.com/zuizui0223`;
- ZHANG Ruiqi;
- 張瑞琪;
- Rachel Zhang variants;
- author email / mailto patterns tied to the author;
- corresponding-author / affiliation placeholders that could identify authors.

Result:

**0 identifying hits.**

The only GitHub source URL retained is:
- `00keveland/Tunnel_2026`

which is a third-party published source-data repository and does not identify the current manuscript authors.

## Intended placeholder

The Complete Anonymous Text intentionally retains:

`[ANONYMIZED_REVIEW_ARCHIVE_URL]`

until the sanitized ZIP is uploaded to an external anonymized review repository.

## Boundary

This GitHub Actions artifact is a staging/review-build object.

It is **not** the final Behavioral Ecology data archive because Behavioral Ecology requires a permanent repository/DOI and does not accept GitHub alone as the publication repository.

Required next step:
- upload this exact sanitized content to an anonymizable permanent repository;
- obtain review link;
- later expose/cite the permanent DOI according to journal policy.

## Verdict

**PASS_ANONYMOUS_ARCHIVE_SANITIZATION_V1**
