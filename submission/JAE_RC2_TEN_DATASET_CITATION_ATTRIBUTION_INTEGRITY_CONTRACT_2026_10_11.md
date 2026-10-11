# JAE RC2 public dataset citation and licence-identity crosswalk — frozen 2026-10-11

**Purpose:** Submission provenance QA. This is not a new JAE empirical result, not a new licence grant and not permission to republish source bat telemetry. The frozen science SHA `c4ef51a7f3f291a6f203d303dbf73f5b54fb7683` is authoritative.

The original JAE manuscript and its identifying title-page **template** were independently inspected before writing this gate. All **10** externally collected source DOI identifiers (the 6 source-screen original/focal analyses plus 4 separately frozen external boundary tests) occur in both. DataCite rights-only original DOI receipts [38057807343](https://github.com/zuizui0223/batter/actions/runs/38057807343) report 9 CC0 1.0 datasets and 1 CC BY 4.0 dataset: **`10.5281/zenodo.7535030` (*Nyctalus noctula*)**.

## Frozen test — citation completeness and no cherry-picking

- Obtain the canonical DOI list and scopes from `submission/jae_v0_4_0_original_source_rights.template.json`; require **exactly 6 original and 4 external** with 10 different IDs. Do not materialize a list from the previous DataCite web response or from fabricated DOIs.
- Require each DOI to appear verbatim in `manuscript/MANUSCRIPT_DRAFT_V0_4_0.md` and `manuscript/TITLE_PAGE_TEMPLATE_V0_4_0.md`; require DOI in the source-rights executed ledger, but **do not imply exact DataCite permission has been human approved**.
- The CC BY *Nyctalus* original source DOI must remain cited; manuscript must also retain scientific language of its **first-frozen primary FAIL** with source (p=0.1224), not overwrite with post-outcome revised-eligibility success. This gate checks unaltered manuscript identity SHA and first-primary scientific context, not reinterpreting significance.
- The original source-list/literature attribution should remain separate from licensing rights: CC0 does not mean citations should be omitted; CC BY requires source-level attribution and licence citation if adapted distributions/underlying content are republished.
- Release candidate must continue to have no invented software LICENSE or minted Zenodo DOI, and the full source terms/owner permissions remain separate human signoff. The future versioned AI-disclosure manuscript should be rechecked against the same exact DOI list, but the current frozen RC2 file is NOT to be overwritten.

**Guard PASS meaning:** ten original public-source DOI references are **present and not selectively removed**. It is NOT proof the cited original source owners have been contacted or that journal policy statements have been approved. No wildlife coordinates downloaded or reissued.
