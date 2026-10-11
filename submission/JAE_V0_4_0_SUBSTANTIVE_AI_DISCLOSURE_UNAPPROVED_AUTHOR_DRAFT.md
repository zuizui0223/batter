# Proposed JAE Methods disclosure — human author review ONLY

**2026-10-10. NOT PART OF THE FROZEN MANUSCRIPT. NOT SUBMITTED. NOT APPROVED.**

If the actual research team verifies that substantive ChatGPT/generative-AI assistance contributed to text and/or analytical software, BES requires a transparent Methods or Acknowledgements disclosure. The following is a candidate for discussion, **not** an assertion that independent verification has already happened.

## Proposed text, subject to exact author confirmation

> OpenAI ChatGPT was used to assist with manuscript drafting and revision, construction and debugging of analysis and validation scripts, and organisation of literature and methodological checks. Generative AI did not collect the original animal tracking data. The authors [SPECIFY WHICH AUTHORS VERIFIED WHICH INPUT DATA, ANALYSIS OUTPUTS, SOURCE CODE, REFERENCES, AND STATISTICAL CLAIMS] and [DESCRIBE WHAT WAS REVISED OR REJECTED AFTER HUMAN REVIEW]. All substantive scientific decisions, interpretations and responsibility for the final work remain with the human authors.

## Required factual review before any use

- Confirm which listed activities actually contributed to the **canonical v0.4.0 JAE manuscript** and source software, not merely exploratory branches or previous discussions.
- Confirm all tools/models/services that materially contributed to the published work; identify ChatGPT/version only to the extent known and necessary under the publisher's policy. Do not invent model versions or falsely imply that all programmatic analyses were independently rerun by a person.
- Replace both bracketed statements with **verified human actions only**. If any claimed verification was not conducted, perform it or accurately state its scope and limitations instead.
- Decide whether the final disclosure belongs in **Materials and Methods** or **Acknowledgements**, accounting for double-anonymous review. The exact human-approved disclosure text in `submission/jae_v0_4_0_policy_signoff.json` must then match the text in that approved journal-facing section.
- If the frozen manuscript needs editing to include a disclosure, **do not change `release/jae-v0.4.0-rc2` silently**. Prepare a revision branch/candidate with an explicit diff and author approval, regenerate the anonymous review PDF, recompute the final combined word count and rerun all published analyses' provenance/format guards. Previously frozen inference should remain unchanged.
- The BES [editorial AI policy](https://besjournals.onlinelibrary.wiley.com/hub/editorial-policies) distinguishes substantive content development from ordinary spelling/grammar changes. Claims of grammar-only assistance would be inappropriate if substantial drafting or code generation was actually used.

## Word-budget guard

The existing rc2 validation manifest records **7,995/8,500** project-counted manuscript words. The previous **synthetic** author-metadata test reported **8,175/8,500**, leaving **325 words** with fake names/affiliations/DOI. The above unapproved sample paragraph and any reviewer-facing section heading consume additional words; any **real** list of authors, affiliations, acknowledgement details, licences and generated title-page text can change the final count substantially. Recount the complete actual package **after** author approval; do not treat synthetic headroom as publisher clearance.

**Author-signoff state:** `HOLD_HUMAN_APPROVAL_AND_FINAL_MANUSCRIPT_DISCLOSURE`. No assumption of tool authorship, complete human validation, software licensing or data-owner permission is made.
