# Independent Black Forest 64-site prey → acoustic-bat heldout model (source-free)

2026-11-21. Source-independent model specification and programmatic validation only; **publisher original raw XLSX is not accessible here** after the canonical official-download attempt returned **HTTP 401** in [Actions #44762637892](https://github.com/zuizui0223/batter/actions/runs/44762637892). The independent source **metadata/version/files are authenticated**, but no original bat responses or prey values have been read in this project.

**Paper prior art:** Hendel et al. (2025), *Journal of Applied Ecology* [10.1111/1365-2664.14822](https://doi.org/10.1111/1365-2664.14822), independent Dryad [10.5061/dryad.xksn02vr1](https://doi.org/10.5061/dryad.xksn02vr1), 64 one-hectare plots in the Black Forest. The authors' SEM reported SRE increasing with moth abundance and decreasing with moth richness; LRE related to beetle abundance and richness with caveats. These are **published original authors' findings**, not new external independent prediction by batter.

**Executable transfer test:** `hendel_heldout_prey_activity_v1.py` computes ridge-based leave-entire-site-out scores on the FOUR independent acoustic response channels (SRE, MRE, Ppip, LRE). Crucially bat acoustic activity minutes may overlap; they are **not 4 mutually exclusive species-guild counts**, so NO multinomial simplex normalization from Ducke is transferred. Each channel targets `log1p(activity)`; training-only standardization yields dimensionless negative squared prediction error. Fixed ridge 0.15.

Baseline predictors: elevation, DOY, minimum night temperature, canopy openness, canopy-height variation and forest-management index. Candidate tests independently add (i) moth abundance, (ii) moth richness, (iii) both, and analogous ground beetle abundance/richness predictors, with nested scores and training-only transforms. All models evaluate the same withheld site. The full site universe must contain 50–70 qualified rows, unique plot identifiers, nonnegative prey and acoustic responses and all fixed covariates. Missing records are never imputed as zero.

Biological limitations: Moth UV light traps operated on night 2 whereas bat acoustics use nights 1 & 3; ground beetles were measured in a different calendar window. The source's bat activity is a detection/behavior proxy, NOT bat abundance, observed prey consumption or individual 3D height. Leave-one-site-out across 64 sites in ONE German forest is not *geographically independent external holdout*. Interpretation remains qualitative cross-study triangulation until original source response values can be opened and heldout prediction computed.

**The precise Ducke-to-Germany transfer claim is not a numerical coefficient**: local measured resource abundance or richness may add predictive information beyond physical habitat; abundance and diversity may exert different relationships. Testing whether this principle survives across food channel/continent/detection mode is a **new out-of-study analytical goal**, not yet a new confirmed result. Ducke's 4-guild negative log likelihood and German acoustic activity squared error are **incompatible units**; do not pool their gains as a meta-analysis. Full 5D bat resource/height gain and NeoBat true M3−M1/N1 remain unestimated.

Protected frozen JAE/BE, `batter` main and `esdm` main are untouched.
---

## 2026-11-21: original workbook uploaded and fitted (supersedes the source-free outcome status above)

The **publisher's own HTTPS download is still blocked** in cloud CI (HTTP 401), but the user provided the actual workbook. It is SHA-256 pinned and heldout prediction was computed on **65 observed complete unique plot rows**, not just synthetic values. The paper says 64; no row was removed without an author-approved exclusion key. Every possible 64-site subset was refitted and the main positive directions survived 65/65 tests.

Matched source columns in the original Excel differ from the synthetic runner: mothcount_total corresponds to mothcount; carabidae_SR to carabidae_S. The new [SHA-pinned local adapter](hendel_uploaded_xlsx_original_adapter_v1.py) prevents silent header mismatch; the raw workbook and animal records are **not** in the repository.

- MRE acoustic activity: added moth abundance +0.10990 standardized heldout score; Ppip +0.16283.
- LRE acoustic activity: added ground beetle richness +0.13708; abundance and richness jointly +0.17649.
- SRE: added moth abundance −0.01199, **not a positive heldout prediction**.
- A larger 13-variable forest covariate baseline, ridge strength alternatives, and an MAE loss check all preserve the main three positive directions.

The primary model was defined before source XLSX values were opened in this project; robustness analyses are **post-outcome**. Publication already described in-sample prey/activity associations, so this new *exploratory within-study predictive test* is not novel proof of bat diet or causality, not independent geographic holdout, and not 3D vertical GPS. Neither Ducke's 4-guild log-score units nor its target can be numerically pooled with Hendel.

**Authoritative new result and explicit caveats:** [HENDEL_USER_UPLOAD_ORIGINAL_HELDOUT_RESULT_V1.md](HENDEL_USER_UPLOAD_ORIGINAL_HELDOUT_RESULT_V1.md). Current evidence ledger: [evidence_ledger_v1.json](evidence_ledger_v1.json). Original source gate history above remains intact; frozen manuscripts and main branches remain unchanged.
