# JAE RC2-to-new-candidate AI disclosure transition — structural gate V1

**2026-10-11. Editorial transition ONLY.** Original scientific revision `release/jae-v0.4.0-rc2` and its manuscript SHA `c4ef51a7f3f291a6f203d303dbf73f5b54fb7683` remain immutable. This procedure cannot itself approve author statements, change statistics, mint a DOI or submit a manuscript.

## Why a separate candidate is essential

The British Ecological Society requires transparent **substantive** generative-AI use disclosure in Methods or Acknowledgements. Current frozen `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md` has no explicit ChatGPT/OpenAI disclosure. A new acknowledgement or method paragraph would necessarily change the Git blob, which must NOT be hidden by switching off the RC2 identity guard.

No manuscript candidate and no final human signoff have yet been created. This is a source-level **future approval path**, not a claim that any author has endorsed the unapproved example.

## Frozen versioned candidate path and scope

Use the newly named **separate** source path `manuscript/MANUSCRIPT_DRAFT_V0_4_0_AI_DISCLOSURE_CANDIDATE.md` only after authors confirm the substantive tool-use scope and exact wording in `submission/jae_v0_4_0_policy_signoff.json`.

The separate `scripts/check_jae_v0_4_0_AI_disclosure_candidate_transition.py` checks the frozen original SHA and, ONLY if a human-approved candidate actually exists, requires that the candidate be **exactly the original manuscript plus one approved paragraph**:
- `METHODS`: insert that paragraph immediately after the existing `## Materials and Methods` heading;
- `ACKNOWLEDGEMENTS`: insert under an existing `## Acknowledgements` heading, or introduce a single `## Acknowledgements` section immediately before the existing `## Data and code availability` section.

Any changed data, result, reference, figure caption, title, numerical effect, method specification, other text or unexpected source reordering produces `STOP_UNAUTHORIZED_CANDIDATE_CONTENT_DIFF`. A README/JSON/PR comment alone cannot count as disclosure. Also reject `[INSERT]`, `TBD`, `TODO` and unapproved bracketed human-verification claims.

### Two independent positive-path situations

1. **Substantive AI use actually verified:** Require the one-paragraph Methods/Acknowledgements disclosure; new manuscript SHA; version/rebuild/validate the candidate with human coauthor approval. The existing frozen RC2 package's earlier PDF and word-count receipt are **NOT transferable**.
2. **Actual language-only/no use established and all verified by authors:** The previously fixed source may require **no manuscript edit**, and the separate editorial signoff checker must be able to return a real human-approved exempt state. However, a false `LANGUAGE_ONLY` classification cannot be justified just to evade transparency given substantive drafting/code assistance in this project.

**Candidate passing its content check does NOT mean submission is ready.** Once all coauthors approve the new editorial candidate, set up a *new versioned* RC3 candidate, update the canonical manuscript/manifest/approved-policy SHA together, run the full JAE automated and human inspections, regenerate 27-page anonymous reviewer PDF (page count may change), align real title page and word count, then mint an authentic versioned archive DOI only after release safeguards. Do not re-use the old automated strict gate as evidence that the revised version is identical to RC2.

**Current factual status:** `HOLD_HUMAN_AI_USE_AND_REVISION_APPROVAL`. None of the human-verified JSON, new-version manuscript or publisher-facing declaration files exists.

## Test integrity
The candidate checker must self-test all: (1) precisely allowed insertion, (2) unchanged original, (3) extra changed numeric result rejected, (4) missing appropriate section rejected, (5) undisclosed author verification placeholders rejected, (6) current real checkout returns HOLD. No animal records read, no journal upload.

BES author policies: https://besjournals.onlinelibrary.wiley.com/hub/editorial-policies .
