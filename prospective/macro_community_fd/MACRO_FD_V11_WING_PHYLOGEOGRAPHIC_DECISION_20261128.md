# V11 separate-source wing phylogeography — completed decision, 2026-11-28 JST
Frozen contract 41a311b72a0093be9e1944d96e829d3b9e9baef8; code 93080b50ccaf430d6457fbe16f5e44637848d94a; workflow 9ef46ae235c468314e27cfdfa3b3532b83dbc4dd. Run 45981059677/job 140444768842 completed; actual aggregate COMPLETE. Artifact 15189227544 registry SHA256 19309a37a458a22724677499576c77c9b260015c0bdc743a779a20ad22671519. Executed full log JSON committed a51e64b8d75c1ea6b1faffbb4d3e53d766297fa4. Output ZIP not independently rehashed; exact source checks and V10 release/tree hashes verified. Independent wing trait compilation, but same range and tree source; not independent field data. 
## Coverage and climate prediction
264 matched wing species; 9310 range-eligible native cells (>=5 matched, >=20% full richness), 8468 climate-complete, 7427 in six admitted coordinate boxes. Europe 790, NA 1297, EA 858, SA 1742, Africa 2183, Australasia 557. Regional median trait coverage .3636–.8333. >=50% coverage sensitivity: 6215 eligible, 5697 climate-complete, 4855 in five admitted boxes (South America 68 cells/6 large blocks fails support). All 264 species retained for fixed trait scaling. No GEDI domain restriction in this distinct climate-only analysis.
|cohort/design|N flight MSE|D|B|B-D relative gain|positive folds|positive region-blocks|
|---|---:|---:|---:|---:|---:|---:|
|primary 5x5|.17674653|.12865663|.10790485|+16.1296%|5/5|261/479|
|primary 10x10|.16788681|.13321440|.11566540|+13.1735%|4/5|86/161|
|primary region|.21278111|.19720922|.20015291|-1.4927%|3/6|202/479|
|>=50% 5x5|.19379316|.13875348|.10868023|+21.6739%|5/5|191/337|
|>=50% 10x10|.18608835|.14309906|.11754366|+17.8585%|5/5|62/120|
|>=50% region|.25807689|.28496949|.28893284|-1.3908%|3/5|153/337|
D includes richness, trait coverage, absolute latitude, climate support; B adds six climate means. The climate screen FAILS both cohorts (block fraction and region transfer). Primary held-out climate increments Africa -.08056, Australasia +.06963, EA +.04297, Europe -.02801, NA +.01265, SA -.03434. No overall useful independent climate increment for whole-region prediction. Neither cohort confirms transfer; higher coverage is not independent.
## Phylogenetic reconstruction versus transfer
|cut|primary reconstruction reduction median, flight|primary spatial 5x5/10x10 G contribution fraction median|>=50% reconstruction reduction|
|---|---:|---:|---:|
|5 Ma|.969804|.939382/.949395|.964889|
|10 Ma|.923968|.913897/.935031|.911184|
|20 Ma|.801173|.775014/.785303|.760996|
|40 Ma|.583966|.597126/.646885|.446498|
Reconstruction uses actual known local clade composition; it is not forecasting unknown regions. At 20 Ma actual flight reconstruction loss .02889396–.05696912; per-tree geography-conditioned random lower 2.5 percentile .05027253–.09622434. Each paired comparison passes reconstruction in 20/20 trees for primary, 17/20 higher coverage; same counts unrestricted. 50 geography strata, 14 singleton, mutable species fraction .9242–.9470. Geo-conditioned shuffle preserves group×dominant box×log2 range-cell-count bin, not exact spatial covariance. Actual G region transfer gains range -.00496369 to +.01373284, total climate increment negative, ratios to negative total are not interpretable as contribution shares. Combined frozen screen 0/20 trees in both cohorts because total climate transfer gain <=0 and additional requirements. Do not say 20/20 passed V11: only the predeclared reconstruction comparison passed in primary. 
V10 and V11 differ in response, roster, cells, climate predictors and baseline contrast B-N vs B-D. Direct cross-domain quantitative comparison is descriptive, not controlled. New next question: distinguish phylogenetic reconstruction from environmental portability using identical species, cells, baseline and folds across wing and joint trophic/stratum response (234 common species); a separately frozen paired contrast, not changing V11 outcome or tuning. Main and manuscripts unchanged. No submission.
