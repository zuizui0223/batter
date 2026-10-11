# JAE v0.4.0 — mandatory submission-policy declarations and human factual sign-off

**2026-10-10. EDITORIAL / ETHICS SOURCE CHECK. Not a change to original bat results or frozen JAE RC2. Do not treat any example statement in this file as an approved declaration.**

Authoritative current sources:
- [JAE initial-submission author guidelines](https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines) — a **Statement on inclusion is required during submission**, though inclusion in the *published article's* Author Contributions is optional. It asks what action was taken to include regional stakeholders/scientists and what opportunities they had for input; it permits candid statements about limitations.
- [British Ecological Society editorial policies, Artificial Intelligence Generated Content](https://besjournals.onlinelibrary.wiley.com/hub/editorial-policies) — if ChatGPT or another generative LLM was used to develop *any manuscript content*, it **must be disclosed transparently and in detail in Methods or Acknowledgements**. Mere spelling, grammar, and general copyediting is treated differently; AI cannot be an author; the human authors are responsible for all factual claims, analysis and citations.
- [BES editorial policy, Use of third-party data](https://besjournals.onlinelibrary.wiley.com/hub/editorial-policies) — publicly available third-party data must be verified as freely reusable or appropriate explicit permission from owners must be demonstrated if restricted. Dataset DOI availability alone does not establish unrestricted licence rights. Bespoke non-standard analysis code must be archived as the actual reproducible version of record.
- [JAE author guidelines, author approvals](https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines) — all named authors must approve the submitted version; author order/CRediT/ORCID and conflict-of-interest are human declarations, not inferred from GitHub.

## Evidence-status audit specific to this repository

This manuscript reanalyses independently collected, openly archived bat trajectories. No new bats were handled *for this secondary analysis*, but the original studies DID perform fieldwork; do not claim the original studies required no animal ethics, made no community contact or enjoyed universal data licences.

In the research and manuscript-preparation workflows there has been substantive ChatGPT/LLM assistance with drafting, code construction, literature consideration and interpretation checks. However, which precise outputs were incorporated into the frozen canonical manuscript, which source-code parts were author independently validated, and whether any external generative services were involved **must be affirmed by the human authors**. Do not claim the usage was merely grammar correction; do not claim that AI is a co-author or responsible researcher.

### A. Statement on inclusion — two CONDITIONAL, unapproved examples

**Example only if TRUE after author review (secondary public-data-only work):**

> This study is a secondary analysis of previously published and publicly archived animal tracking data; no new field sampling was carried out for the present analysis. We acknowledge and cite the original data collectors and publications and considered [describe demonstrable steps to engage relevant regional researchers or literature, and whom, if any]. The present analysis team included [verify actual geographical representation and participants]. Opportunities for input from researchers and stakeholders in the original study regions were [describe actual opportunities, or explicitly state that direct engagement did not occur and acknowledge its limitation].

**If there was NO new regional engagement, explicitly acknowledge that rather than inventing it:**

> This study reanalysed publicly archived datasets collected by independent research teams and did not undertake new fieldwork. We credit the original data contributors and cite their publications. Direct engagement with local researchers and stakeholders in every source region was [not undertaken / describe actual level of engagement]; this limits the range of perspectives informing the secondary interpretation. [Add any genuine actions taken to consider local literature or obtain feedback, if applicable.]

The exact text should be written by the responsible human team. Do **not** automatically insert these unapproved examples into a journal-facing document.

### B. Transparent generative-AI disclosure — CONDITIONAL wording only

**Potential author-approved Methods or Acknowledgements wording if substantive use is confirmed:**

> OpenAI ChatGPT [record model/version where verified] was used during manuscript preparation and analysis development to assist with [enumerate actual tasks performed: e.g., drafting/rephrasing passages, generating and debugging scripts, evaluating analytical assumptions, organizing literature or reproducibility records]. All reported data sources, calculations, claims and cited references were [describe the specific independent checks that human authors actually performed]. The authors reviewed and approved the final text and remain solely responsible for the integrity, accuracy and reproducibility of the work.

**Do not** represent authors as having verified all calculations independently until they actually have. If the authors report that the only actual use was minor language/grammar correction, the BES policy treats that differently; a substantive-use finding cannot be overwritten merely to avoid disclosure.

Be mindful of double-anonymized submission: the factual disclosure wording must avoid identifying authors in the anonymous main manuscript. The author may need to seek clarification from the journal about placement only if the permitted journal location conflicts with anonymity or contribution details.

### C. Third-party source rights and scholarly credit

The title page already names original data DOI sources. Human code/data rights review should cover all original source DOI/terms rather than assume 'public' equals 'unrestricted':
- original `Tadarida teniotis`: 10.5441/001/1.52nn82r9;
- original `Eidolon helvum`: 10.5441/001/1.k8n02jn8;
- original `Hypsignathus monstrosus`: 10.5441/001/1.278;
- original three `Phyllostomus hastatus` panels: 10.5441/001/1.282, 10.5441/001/1.321, 10.5441/001/1.322;
- boundary external data reuse includes separately frozen Zenodo / Dryad / Movebank original citations, as mapped in the frozen JAE metadata.
- confirm per-source reuse conditions, required references, licence attribution and any restrictions on republishing **raw telemetry**, sensitive locations and derivative figures. If original metadata forbids unrestricted reuse, contact the data owner and preserve written permission **outside public GitHub** before submission.
- choose one new software LICENSE only after rights-holder approval; an analysis-code licence does **not** relicense source wildlife tracking datasets.

### D. Operational signoff, not an invented declaration

A public template with only non-personal fields is stored in `submission/jae_v0_4_0_policy_signoff.template.json`. A finalized non-sensitive `submission/jae_v0_4_0_policy_signoff.json` can be authored by a responsible human in the approved release branch, with **no personal email, private author signatures or restricted raw data**. Until approved, the optional additional handoff checker must report `HOLD_HUMAN_POLICY_SIGNOFF`.

The author MUST verify before marking completed:
1. Inclusion statement is true and ready for the journal's submission field, acknowledging actual secondary-data/regional engagement.
2. Real substantive ChatGPT use was classified accurately; disclosure and independently verified responsibilities/limits written into the approved Methods or Acknowledgements where necessary (not fabricated nor appended silently).
3. Dataset rights/reuse and attribution/permissions were checked on each actual source; no silent relicensing or publication of sensitive locations.
4. All author consents and conflicts are genuinely resolved.
5. Any necessary amendments to the frozen RC2 manuscript require explicit human editorial revision and a new versioned candidate with a rebuilt anonymous PDF and updated validation; **never treat this handoff note as having changed the manuscript**.

**Decision:** `NO_AUTOMATIC_ETHICS_DISCLOSURE`; `HOLD_HUMAN_POLICY_SIGNOFF`. The scientific manuscript's prior statistical results and current SHA remain untouched.
