# JAE v0.4.0 — journal-facing AI/inclusion declaration consistency, not just checkbox approval

**2026-10-10; post-freeze editorial gate, no scientific code or original animal outcome change.** The current immutable JAE RC2 manuscript `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`, Git blob SHA `c4ef51a7f3f291a6f203d303dbf73f5b54fb7683`, was scanned for explicit `ChatGPT`, `OpenAI`, `generative AI`, `large language model` terms: **zero matches** as of this audit. This is source-text evidence of absent explicit disclosure, NOT an external account of precisely which outputs were used.

## The gap

The existing human policy-signoff template `submission/jae_v0_4_0_policy_signoff.template.json` supports author classification of substantive generative-AI use and a written disclosure draft. BUT a green signoff-record validation (even if genuinely human-approved later) would not by itself prove that the required disclosure **actually appears in the submitted scientific document**. The initial JAE RC2 manuscript presently has `## Materials and Methods` but no `## Acknowledgements` and no explicit AI disclosure. Without a linked draft/manuscript/publisher field cross-check, this is a potential silent compliance hole.

British Ecological Society policy source: https://besjournals.onlinelibrary.wiley.com/hub/editorial-policies — substantive generative-AI creation of manuscript material must be disclosed transparently in Methods or Acknowledgements; human authors are accountable and AI cannot be an author. Grammar-only help is distinct. Journal source: https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines — submission requires a Statement on inclusion, whose actual text may be entered in the submission portal.

## Explicit stop conditions for the new reviewer-facing document check

If there is NO *author-approved* policy signoff file, `HOLD_HUMAN_POLICY_SIGNOFF` — this is current real-repo status.

If the human signoff classifies use as **SUBSTANTIVE**:
- require a nonempty, author-approved disclosure text and placement `METHODS` or `ACKNOWLEDGEMENTS`;
- require that specific approved disclosure paragraph (after whitespace and Markdown emphasis normalization only) to occur in **the actual journal-facing source**: `## Materials and Methods` or a dedicated `## Acknowledgements` section in the manuscript, or `## Acknowledgements` in the generated final title page when authors and journal explicitly approve its placement;
- deny a green "submission READY" if an approved statement is merely in a JSON/PR comment, a future-release note, optional cover letter or private email but absent from the final appropriate document;
- require unchanged scientific RC2 manuscript SHA for an untouched RC2 — when authors edit for new disclosure, it **necessarily changes that SHA**, so create a **versioned revised candidate**, update the manifest and regenerated PDF, and revalidate scientific-content preservation. Do NOT bypass the SHA guard, conceal the edit or claim that the already verified 27-page PDF is still current.

If human classification is `LANGUAGE_ONLY` or `NOT_USED`, any exemption must be based on verifiable actual usage and human approval, not on a desire to omit substantive AI disclosure. Existing ChatGPT assistance to manuscript and source-code development is a meaningful reason to require factual scope review.

If an actual inclusion statement is authored, check only that approved wording is stored as a journal-submission text field. Do **not** require that the inclusion statement be in the anonymous manuscript if the publisher collects it during submission; and never invent a local-collaboration claim.

**Human data-rights requirement remains independent:** ten sources received DataCite CC declaration candidates (nine CC0, one CC BY `Nyctalus`), but DOI metadata are not author rights approval and an analysis-code LICENSE does not relicense original telemetry. Only a source-by-source author signoff can end that HOLD.

## Test boundaries

The new checker will run in CI **without any human signoff present** and return a successful *audit execution* plus explicit **HOLD**, preserving a fail-closed workflow. Its synthetic tests demonstrate the negative case (substantive statement absent) and positive simulated case (statement present in the appropriate section), without modifying the actual JAE manuscript, providing author metadata, choosing a licence, minting a DOI or transmitting a journal submission.

**Original result and legal status remain unchanged:** `AUTHOR_DECLARATIONS_AND_DOCUMENT_CONTENT_NOT_YET_ALIGNED`; human/coauthor action required. No automatic adoption of candidate disclosure language.
