# H1 — ecological rules for personal and social information use in bats

**2026-11-19 status: source-audited prospective study design, not a completed meta-analysis.**
This branch preserves the frozen JAE `batter` results and does not alter `main`. The positive results below refer to *published prior work* and independently audited descriptive counts, NOT new phylogenetic evidence or causal inferences.

## Verified inventory

- **2022 theory-development reference sample**: Kohles et al. Table 2 contains 35 cases, including 29 explicit named bat taxa and one pooled taxon row; 20 cases have one of four social information strategy labels; 25 cases have both resource persistence and social information location classifications. They are **not independent external tests** of the hypothesis.
- **Targeted post-2022 original-paper sample**: 12 context/receiver-specific observations, eight explicitly named taxa, six source-study clusters; none (0) independently codes one of Kohles's four classical strategies with measured resource predictors. Not a systematic census, not 12 independent studies, not a worldwide sampled absence frame.
- **Source-data QA, not author-result replication**: Original Lourie et al. 2024 field table + bat-tag visitor table produce 10 naive visitors / 56 naive tagged animals = 17.86% following social odor manipulation. One source CSV `n_total` cell for 19 July 2020 Gershom lists 22 while 4 manipulated + 19 naive = 23; author manuscript's 23 is consistent. This does not change the naive 10/56 descriptive count and cannot be interpreted as a new p-value.
- **Main hypothesis revision**: Personal place memory and social *timing* information can be complementary. Information about food presence, availability, competition and social role should not be collapsed to one social-versus-individual trait.
- **STOP gates**: no phylogenetic four-strategy outcome test, no species-wide social-information absence model, and no H3 individual-memory-vs-social-cue negative correlation from the current data. Tested negatives, resource observability, independent study cohorts and taxonomic join quality do not yet meet requirements.

## Files

| Path | Status |
|---|---|
| `H1_PREREG_AND_FEASIBILITY_V1.md` | Predeclared feasibility and stop logic |
| `H1_CODING_DICTIONARY_V1.md` | Blinded ecological and behavioral coding rules |
| `H1_V2_INFORMATION_CHANNEL_AMENDMENT.md` | Novelty boundary and revised information-channel hypotheses |
| `SOURCE_SEED_V1.csv` | Source-discovery seed (not an outcome dataset) |
| `REVIEW_TABLE2_BASELINE_V1.csv` | 35-case 2022 prior-art reference inventory |
| `POST2022_PRIMARY_EVIDENCE_V1.csv` | Targeted post-2022 evidence ledger with study clusters and unknowns |
| `ROUSETTUS_ORIGINAL_SOURCE_QA_V1.md` | Primary-data traceability and 1-cell source discrepancy |
| `run_h1_feasibility.py` | Deterministic structural audit; no statistical effect estimation |
| `test_h1_feasibility.py` | Unit tests of counts and analysis stops |
| `.github/workflows/h1-social-information-evidence.yml` | Branch-scoped automated check + JSON artifact |

Last verified Actions success (2026-11-19): https://github.com/zuizui0223/batter/actions/runs/44446583428

## Next experiment gate

1. Use a preregistered/dated literature search to sample original field and lab *foraging cue use*, preserving all screened negatives.
2. Validate each source’s primary original tables, taxa, physical IDs and experimental effort.
3. Have ecological predictor and behavioral outcome codes independently assigned and checked blind.
4. Only after enough independent study-population responses support a comparable outcome: evaluate held-out cue-response sign/strength and moderator transfer. Treat phylogenetic model as optional, not a substitute for a valid observational denominator.

**Do not merge into the JAE inference ledger or rewrite its scientific claims.**
