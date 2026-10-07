# Anonymized review archive receipt v1

## Status

**BUILD PASS / ANONYMIZATION SCAN PASS**

Authoritative workflow:
- run: **37575382273**
- job: **112642990552**
- artifact: **11462003405**

Artifact name:
`public-causal-anonymized-review-archive-v1`

Internal review ZIP:
`PUBLIC_CAUSAL_ANONYMIZED_REVIEW_ARCHIVE_V1.zip`

Internal ZIP SHA256:
`b6c455ab94554360a0631537b055c4bf89fdce8cbfc1852f79fe1ab163ebb3af`

GitHub artifact-bundle SHA256:
`33357161a92436b63a01330dbb64bfd45329d3650dddff9138976b83678c20d3`

## Build checks

The builder:
- copied only the curated review manifest;
- excluded Git history;
- excluded the non-anonymous cover page;
- excluded the cover letter;
- excluded acknowledgements/funding/CRediT metadata;
- scanned every packaged text file for identified working-repository tokens;
- failed closed if an identifying repository token was present.

Build result:

**PASS anonymized review archive build**

## Included review material

- anonymized manuscript;
- supplementary-material draft;
- figures;
- captions;
- alt text;
- lay summary;
- master results table;
- evidence matrix;
- manuscript numerical audit;
- reviewer-risk audit;
- publication-overlap audit;
- causal-ceiling/source-screen records;
- manuscript-level plotting and evidence-guard code;
- public source-data/result index.

## Remaining anonymity step

The artifact currently lives inside the identified development repository workflow.

Therefore it is **not itself the anonymous review URL**.

Before journal submission:
1. download the ZIP;
2. upload it to an anonymous review-capable host or the journal's anonymous file mechanism;
3. replace `[ANONYMIZED_REVIEW_ARCHIVE_URL]` in the anonymized manuscript with that anonymous URL, if the journal requests a link.

Do not submit the identified workflow artifact URL to reviewers.
