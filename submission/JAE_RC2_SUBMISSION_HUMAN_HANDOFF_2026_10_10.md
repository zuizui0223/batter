# JAE v0.4.0 rc2 — practical editor/coauthor submission handoff

**Prepared 2026-10-10.** This is a post-freeze HANDOFF, not an amendment to the scientific manuscript, tests, figures, original data or preregistered statistical claims.

## Authoritative version and checked repository state

- Submission branch: **`release/jae-v0.4.0-rc2`**, head at handoff **`eb4101ebbeed195c17ba86be44c2d2f34d5f9d21`**.
- Canonical title: **Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species**.
- Canonical frozen manuscript: `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`; **Git blob SHA `c4ef51a7f3f291a6f203d303dbf73f5b54fb7683`** (independently matches `SUBMISSION_MANIFEST_JAE_V0_4_0.json`).
- The paper's partitioning/co-use claim applies to **4 evaluable panels** from ***Hypsignathus monstrosus* and *Phyllostomus hastatus***, not all bats.
- Positive terrain-relative persistence 4/4, **positive added segregation supported 0/4**, synchronous additional separation 1/4 (2023 exception). Nonsignificant differences **do not** prove zero segregation. The separate *Tadarida* source is a motivating *boundary case*, not the strongest confirmatory panel.
- First prospectively frozen *Nyctalus* external primary and *Hipposideros*/*Myotis vivesi* are all FAIL; separately gated four-individual *Pteropus* passed. The external set is not a random prevalence sample. No learning or fitness mechanism established.
- JAE data source DOI citations, claim ledger and provenance accompany the manuscript. This handoff is based on existing [rc2 submission readiness](../manuscript/JAE_SUBMISSION_READINESS_V0_4_0.md) and [manifest](../SUBMISSION_MANIFEST_JAE_V0_4_0.json); it does NOT rerun the frozen 3D inference.

## Confirmed packaging machinery (existing checked rc2 receipts)

| Component | Source-backed rc2 receipt | Status |
|---|---|---|
| JAE submission/checks | [Actions 37123936286](https://github.com/zuizui0223/batter/actions/runs/37123936286); 7,995 whitespace-like CI words including frozen package rules, main figures 6 and supporting figures 3 | Previously validated |
| English abstract | 313 words per v0.4.0 manifest (author guideline maximum 350) | Previously validated |
| Double-anonymous review | [Actions 37123738669](https://github.com/zuizui0223/batter/actions/runs/37123738669), 27-page PDF, separate title-page/identity guard PASS; artifact ID 11274153477 | Previously validated; re-download before uploading |
| Figures | Main artifact 11273753416; supporting artifact 11273793396, original SHA256 digests in source manifest | Previously validated; re-download before uploading |
| Synthetic author-metadata pipeline | [Actions 37124460765](https://github.com/zuizui0223/batter/actions/runs/37124460765): combined 8,175 /8,500 before release, 8,170 /8,500 with fake DOI; **not genuine author metadata** | Only structural rehearsal |
| GitHub release / permanent DOI | No GitHub release listed at handoff, `archive_doi` blank template, no final metadata JSON, no single explicit LICENSE on rc2 | **Human/release-blocked** |

**Never call the combined author-word count final:** the 8,175 and 8,170 are from synthetic placeholder author identities. The real author list, affiliations, acknowledgements and final archival DOI change the final count.

## Current 2026 JAE *initial-submission* rules confirmed at the journal

Official source checked 2026-10-10: https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines

- Research Article **≤8,500 words** including title page, English abstract, main text, references, tables and figure legends (not SI); explain excess in optional cover letter.
- **Double-anonymous review**, including no identifiable authors in review manuscript or SI; **separate identifying title page**.
- English numbered factual abstract **≤350 words**; no more than eight alphabetized keywords; main text single-column, double spaced, with continuous line/page numbers.
- Data availability: cite public data repository and accession/DOI; reuse appropriate original dataset citations. Do not upload underlying datasets merely as journal Supporting Information.
- Cover letter optional, **anonymous and ≤500 words**; submission online at https://mc.manuscriptcentral.com/jae-besjournals .
- Every eligible coauthor must approve the submitted version, author order and authorship contributions; source-data reuse must not imply a new animal ethics approval. Retain proper source-level ethics/provenance wording.

The existing frozen `manuscript/COVER_LETTER_JAE_V0_4_0.md` is **~491 whitespace words excluding its heading, approximately at the journal limit**. An optional shorter and more cautious [~300-word editorial replacement proposal](JAE_V0_4_0_EDITORIAL_SHORT_COVER_LETTER_PROPOSAL_2026_10_10.md) has been created **in this handoff branch only**; its adoption requires author review. Neither draft should contain author-identifying metadata under this review procedure.

## Human author / PI input packet — NO VALUES INFERRED

The exact machine-readable template already exists:
`submission/jae_v0_4_0_metadata.template.json`

**Create only after human approval** `submission/jae_v0_4_0_metadata.json` with:
- **All author names in final order**, given/family components, affiliation IDs, full affiliation text, individual CRediT roles, any ORCIDs and exactly one corresponding author.
- Corresponding author's **genuine address, email and ORCID**, not guessed from a GitHub handle or memory.
- Acknowledgements and funding grant numbers, or literal `None` when explicitly confirmed absent.
- Explicit conflict-of-interest declaration approved by authors.
- The ONE repository software license **chosen by the rights holders** (SPDX matching a single root `LICENSE` file); **do not** select a license without source-code ownership/coauthor permission. Check third-party source-data licenses separately from a code license.
- Actual GitHub release date **when issued**; exact immutable Zenodo **version DOI only when minted**. Do not fabricate a version DOI or replace it with an unrelated concept DOI.

Obtain author approvals separately; do not send the draft to the journal or connect an external submission workflow without explicit human review.

## Strict repository pre-release / post-DOI sequence (already implemented)

Follow [`FINAL_METADATA_INTAKE_JAE_V0_4_0.md`](../FINAL_METADATA_INTAKE_JAE_V0_4_0.md), rather than improvising a new release process:
1. Human writes approved metadata JSON without `[INSERT]` placeholders and with empty `archive_doi`; approves software LICENSE and confirms Zenodo–GitHub integration.
2. Run `python scripts/apply_jae_v0_4_0_metadata.py --stage pre-release`; check generated title page, citation and **real** combined word count.
3. Run `python scripts/check_zenodo_release_ready_v0_4_0.py` and the `jae-github-release-preflight-v0.4.0` workflow on the **intended release RC**, with metadata and LICENSE included. Never create a release tag merely to clear a failing gate.
4. Only after the full prerelease gate and human sign-off, publish one `jae-v0.4.0` GitHub release and confirm the Zenodo archive version DOI.
5. Insert that exact version DOI in approved metadata and run `--stage post-doi` and `python scripts/check_jae_upload_ready_v0_4_0.py`.
6. Review final anonymous PDF and supplementary figures *with the final release version*, then submit on ScholarOne with any appropriate editorial disclosures.

**The publisher may allow initial submission without the repository's extra release-readiness order; the sequence above is the repository's deliberately stricter reproducibility gate**, not a claim of an external rule requiring a pre-submission GitHub Release.

## Scientific referee risk sign-off before clicking Submit

A separate [six-objection referee-response matrix](JAE_RC2_REFEREE_RISK_RESPONSE_MATRIX_2026_10_10.md) was prepared for coauthor/editorial review. Its source-verifiable arguments distinguish:
- the existing horizontal spatial-specialization/overlap literature (Kerches-Rogeri et al. 2020 and Wang et al. 2023) from the present **horizontally matched, centered, terrain-relative vertical-shape** prediction;
- the three nonsupporting local co-use panels from the coarser *P. hastatus* 2023 supported exception; **lack of significance is not an equivalence test**;
- *Tadarida* and the first-frozen external nonreplications from the four panels underlying the two-species claim;
- temporal persistence as evidence of retained individual *information*, **not** causally established skill, memory, learning or fitness benefit.

The optional short cover-letter proposal was edited to say that three panels **did not provide statistical support** for extra co-use separation, rather than implying that a non-significant test proves exactly zero separation. **No canonical manuscript, figure, title, result, license or DOI was changed.**

## New critical 2026 JAE policy requirements — author review required

The 2026-10-10 live [Journal of Animal Ecology initial-submission instructions](https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines) and [British Ecological Society editorial policies](https://besjournals.onlinelibrary.wiley.com/hub/editorial-policies) add distinct human tasks not fully covered by the legacy v0.4.0 author metadata JSON:

- **Statement on inclusion:** the submission portal requires an account of what the study team actually did to engage or include scientists/stakeholders in the regions represented by the original bat tracking studies. This secondary-data analysis involved no new fieldwork, but must not misrepresent the original collectors, identities, collaboration or local engagement. Human approval is essential.
- **Generative AI disclosure:** substantive ChatGPT/LLM assistance to manuscript drafting or analytical code/interpretation must be transparently described in Methods or Acknowledgements, consistent with actual usage and independently verified human responsibility. Merely language-only editing has different status. No AI can be listed as author; do not claim only language edits if research development use was substantive. Human authors must review factual claims and outputs.
- **Original data reuse permissions:** Movebank/Dryad/Zenodo sources may be public, but public visibility alone does not prove unrestricted reuse or permission to republish sensitive wildlife telemetry. Check the licence and citations/permissions for every source; resolve restrictions with data owners and keep any correspondence outside public GitHub.
- **Human accountability:** authorship contribution, conflicts, institutional and source collection ethics, original human approvals and manuscript signoff cannot be inferred from repository history or synthesized.
- **Separate from the canonical metadata pipeline:** the new public signoff template `submission/jae_v0_4_0_policy_signoff.template.json` has deliberately *unapproved* fields, backed by [policy guidance](JAE_V0_4_0_AI_INCLUSION_AND_DATA_RIGHTS_POLICY_GATE_2026_10_10.md) and [an additional fail-closed checker](../scripts/audit_jae_v0_4_0_policy_signoff.py). A human may create the *approved* `submission/jae_v0_4_0_policy_signoff.json` without personal signatures or restricted information. Until then, the status is `HOLD_HUMAN_POLICY_SIGNOFF`, even when the separate source-hash/metadata gate passes.

**Important:** a checked signoff JSON does not itself insert disclosure into the frozen manuscript, or prove the journal requirement has been met. If substantive-AI disclosure is needed in the anonymous Methods/Acknowledgements or if the inclusion statement is placed in the submission portal, the human editor must review its placement, rebuild any changed anonymous PDF and generate a separately versioned submission candidate. Never append unapproved language silently to RC2.

## Original tracking-source reuse: all ten public DataCite licence declarations now traced

An independent, [source-frozen public metadata audit](JAE_RC2_DATACITE_SOURCE_RIGHTS_METADATA_GATE_2026_10_10.md) and [successful GitHub Actions #38057807343](https://github.com/zuizui0223/batter/actions/runs/38057807343) recovered rightsList entries from DataCite for **every one of the ten cited source DOIs**. All original six Movebank comparative/focal datasets declare **CC0 1.0 Universal**. Of the four external boundary datasets, *Nyctalus noctula* Zenodo `10.5281/zenodo.7535030` declares **CC BY 4.0 International**, and *Hipposideros* Dryad, *Myotis vivesi* Movebank and *Pteropus* Movebank declare **CC0 1.0**. This was a metadata-only query: no animal position records or original data files opened. [Full source-specific receipt](JAE_RC2_EXECUTED_TEN_SOURCE_DATACITE_RIGHTS_RESULT_2026_10_10.md).

[Movebank General Terms](https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use) generally exempt licensed publicly downloadable CC0/CC BY/CC BY-NC dataset use from separate owner permission when licence conditions are honored, while encouraging citation and reasonable owner contact for new research. This is **not a blanket owner permission** or a substitute for the actual dataset landing page/restricted wild animal location terms.

The exact ten-DOI public [rights-review template](jae_v0_4_0_original_source_rights.template.json) remains **all UNVERIFIED**, and the separate [fail-closed source-rights checker](../scripts/audit_jae_v0_4_0_source_rights_signoff.py) requires human approval of actual licence, evidence URL, source citation, permission applicability, contact/credit assessment and any sensitive-location restrictions **for every individual original DOI**, not a single global boolean. This source-rights review is independent of the future root software LICENSE selection by copyright holders and the substantive AI/inclusion policy signoff.

## Integrated final journal-document compliance gate — after all author approvals

New explicit safeguard: a completed `submission/jae_v0_4_0_policy_signoff.json` is **NOT SUFFICIENT** if substantive generative AI was involved and the approved text has not actually been placed in the **submitted Methods or Acknowledgements**. The frozen current rc2 main manuscript contains **zero explicit ChatGPT/OpenAI/generative-AI disclosure markers**. [Code-level match contract](JAE_V0_4_0_AI_DISCLOSURE_MANUSCRIPT_INTEGRATION_GATE_2026_10_10.md); [author-editable but UNAPPROVED example paragraph](JAE_V0_4_0_SUBSTANTIVE_AI_DISCLOSURE_UNAPPROVED_AUTHOR_DRAFT.md). Neither modifies the submitted version.

After (and only after) human approval and verified data rights, use the *composite* guard rather than relying only on the legacy native upload validator:

```bash
python scripts/check_jae_v0_4_0_integrated_final_editorial_gate.py --strict
```

`--strict` is deliberately **nonzero while** any real human author/AI/inclusion signoff, per-source rights confirmation, approved document-level AI disclosure, matching final title page, software licence, Zenodo version DOI or native final-upload/release check is missing. For reviewable diagnostic output that does not break exploratory CI, omit `--strict`: it prints `HOLD_EDITORIAL_OR_RELEASE_GATES` with exactly which condition remains unmet and does **not** imply journal submission has happened.

If any substantive AI disclosure changes the frozen manuscript, the original rc2 Git blob SHA necessarily changes and the immutable-source checks must STOP; this requires author review and a **new versioned release candidate** with new manuscript blob/manifest, approved source content, rebuilt anonymous PDF, final word count, new provenance QA and the appropriate replacement freeze. Do not turn off the SHA check just to obtain green CI.

The *mandatory Statement on inclusion* is a separately approved submission-portal field, not something this package can upload automatically. Green automated checks NEVER supersede authors' own final proofread and submit action.

## Release vs manuscript safety

This handoff is stored in a separate proposed PR **based on rc2**. Do not merge automatically into the frozen scientific branch until author approval. No `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`, figures, original tests, JAE release candidate, `main` or original release tags have been altered.

**Verdict as of 2026-10-10:** `SCIENTIFIC_RC2_VALIDATED; INITIAL_SUBMISSION_FORMAT_VERIFIED; HUMAN_METADATA_LICENSE_ARCHIVE_DOI_BLOCKED`. Submission ready **conditional on genuine human release inputs**, not currently submitted.
