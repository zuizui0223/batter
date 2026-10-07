# Behavioral Ecology format audit v1

## Official requirements checked

Official journal instructions checked on 2026-10-07.

Behavioral Ecology requires at initial submission:
- double-anonymized review material;
- a Complete Anonymous Text file;
- Lay Summary, maximum 75 words;
- title/abstract page with abstract maximum 250 words;
- manuscript section order including references and figure legends;
- separate Cover Page and Acknowledgements;
- a separate Funding section;
- public data repository citation / Data Availability;
- at most one Supplementary Material PDF if supplementary material is used.

The journal currently permits **format-free initial submission**, so complete conversion of the references to final CSE journal punctuation is not a submission blocker.

Official source:
`https://academic.oup.com/beheco/pages/information_for_authors`

## Current anonymous manuscript

File:
`MANUSCRIPT_ANONYMIZED_BEHAVIORAL_ECOLOGY_V1.md`

Current order:
1. Lay Summary;
2. title;
3. Abstract;
4. Keywords;
5. Introduction;
6. Methods;
7. Results;
8. Discussion;
9. Data and code availability / provenance / ethics;
10. References;
11. Figure legends.

Lay Summary:
- 71 words;
- **PASS <=75**.

Abstract:
- guarded automatically at <=250 words.

Identity scan:
- author names absent;
- affiliations absent;
- identified development-repository URL absent;
- anonymous archive placeholder retained.

## Current remaining format tasks

Not blockers at format-free initial submission:
- final CSE punctuation / abbreviated journal names.

Still required before upload:
- external anonymous placement of review archive if journal wants a link;
- complete Cover Page and Acknowledgements with human author metadata;
- Funding;
- CRediT;
- conflicts;
- final AI disclosure verification;
- one Supplementary Material PDF if supplement is submitted.

## Guard

Authoritative CI:
`behavioral_ecology_anonymous_guard_v1.py`.

The guard fails if:
- Lay Summary >75 words;
- Abstract >250 words;
- anonymous section order drifts;
- identified repository tokens reappear;
- frozen formation/wild evidence boundaries disappear.
