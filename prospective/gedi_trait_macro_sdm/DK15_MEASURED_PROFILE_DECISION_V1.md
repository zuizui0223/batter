# Danish measured-profile decision and neutral-score diagnostic — 2026-11-26 JST
Source: DK15_MEASURED_PROFILE_DIAGNOSTIC_RECEIPT_V1.json, blob b6463bb6549102638366a1e15fdd92d2dbc946a3. Actual run 45642275218, 28,321 constructed comparisons, 24 50-km blocks, 12 contributing taxa; local CV evaluated 28,259 comparisons (11 taxa, 24 blocks, 5 providers), strict provider+block CV 19,451 (11 taxa, 17 blocks, 3 providers). The same recorded-label support and scores are retained within each design. No model refit or predictor selection. Models B include both ALS and GVSM height; G adds GVSM R50, L adds measured historical ALS mean/H95, GL both.
 
| Design | G−B | L−B | L−G | GL−G | GL−L |
|---|---:|---:|---:|---:|---:|
| Local block | -0.00009260 | 0.00048031 | 0.00057291 | 0.00034616 | -0.00022675 |
| Strict source+block | 0.00163262 | -0.00147611 | -0.00310873 | -0.00122623 | 0.00188250 |

The conditional block-bootstrap intervals for G−B, L−B, L−G and GL−G span zero in both designs; strict GL−L has a narrowly positive conditional interval but GL does not improve G. Do not interpret this secondary contrast as measured-profile rescue. The local and strict samples differ. 
   
## Neutral-score arithmetic check
Neutral paired-orientation probability is 0.5, so the constant log score is −log(2) = -0.693147180560. Subtract this constant from the already reported block-mean held-out scores (same evaluated rows and weights; no re-fit).
   
| Design | B−neutral | G−neutral | L−neutral | GL−neutral |
|---|---:|---:|---:|---:|
| Local block | -0.00296210 | -0.00305471 | -0.00248179 | -0.00270855 |
| Strict provider+block | -0.03612128 | -0.03448867 | -0.03759739 | -0.03571490 |
   
All four fitted models are below neutral on each support. The positive local L−B contrast does not establish successful prediction relative to no information. This is a descriptive diagnostic from frozen scores, not a new predeclared hypothesis test. No strong environmental-sensor-only explanation of continental north transfer failure is established; local weak prediction, sample size, observation heterogeneity, acquisition time and distinct structural proxies cannot be separated. The original 20-taxon calibrated SDM remains nonadmitted. Main V4 preserved.
