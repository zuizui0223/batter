# Whitworth paired archive V2: alpha/gamma decline with beta inflation
2026-11-27 JST. Local execution on actual user ZIP, not remote CI. Frozen contract 00cc6e86a3c347bb2ac582265c19ddc1960af227; reproduction code 5a0d0fed9fbcab89494a670d3a72468f039757e5. Main and manuscripts unchanged. Original source DOI 10.5061/dryad.32464qs; paper 10.1111/ddi.12930. This is exploratory reanalysis of detected-session composition, not independently observed new biological data.
## Admission
ZIP SHA256 9ea967aba1a1b1a9a38b4621594369f0d632998ba1efe7d535006ad8c6955330, all 7 CRC pass. A 145x24, T 77x26. All effort row keys/order and station keys match, nonnegative counts <= six-day sessions. Union 46, shared 4 as in article; summed archived session detections A 1824/T 3036 (article raw records 2574/4928, different aggregation, not identical; no count editing). 70 exact paired station-years across six sites in one reserve, 8 site-year groups; 65 both nonempty; 63 both effort >=12; intersection 60. Excluded empty detections not ecological absences. Traits 33 exact label matches including 32 finite positive masses: 10/24 arboreal, 26/26 terrestrial; 13 missing labels and one missing mass. Duplicate alias not used. Mass coverage (12 sessions) 35.84% A/100% T count tokens, 39.92%/100% incidence, median A 33.33%/40%, 49 matched nonempty pairs. Full FD gate FAIL, no whole-community FD or common-roster allocation inference.
## Frozen descriptive result
Site-year fixed intercept regression, FACTOR1 standardized (positive = more disturbance), adjusted standardized log effort ratio and camera height. Coefficients per SD; no p-values. Identical support for identity outcomes. LOSO omits whole SITE, not a new region. All slopes reproduced by independent dummy-variable design OLS, max absolute discrepancy 4e-15, full rank 11.
| outcome | count (n60) | incidence (n60) | count >=3 (n65) | incidence >=3 (n65) |
|---|---:|---:|---:|---:|
| alpha | -.08463188 | -.085349 | -.110134 | -.112416 |
| gamma | -.04097963 | -.041301 | -.051233 | -.053248 |
| beta | +.04365225 | +.044048 | +.058901 | +.059168 |
| beta/gamma | +.06930116 | +.062964 | +.092896 | +.086621 |
| JSD | +.01563915 | +.017158 | +.031693 | +.030191 |
| union richness | -1.336864 | -1.336864 | -1.419870 | -1.419870 |
| A richness | -1.609794 | -1.609794 | -1.725589 | -1.725589 |
| T richness | +.063880 | +.063880 | -.041103 | -.041103 |
Beta all six site omissions positive in all four scenarios. Primary count range +.025716..+.052923; incidence +.033071..+.052316. Unadjusted group slopes positive 6/8 count, 7/8 incidence. Frozen negative-beta directional screen FAIL; do NOT claim disturbance-driven loss of vertical beta. JSD baseline near ceiling ln2 (mean .67678).
Restricted mass-domain beta +.019123 count/+ .012309 incidence, but 49 pairs, highly asymmetric missingness. Mass gamma +.010084/-.000672, not robust. No mass result promoted.
## Post-outcome exact decomposition
For identity distance, Q(p)=1-||p||^2. With equal layer weights, beta=(||p||^2+||q||^2-2p dot q)/4. Thus beta can increase when within-layer diversity declines even without a change in cross-layer overlap. Same regression design gives additive slopes:
| component | count | incidence |
|---|---:|---:|
| canopy concentration ||p||^2/4 | +.039716 | +.040429 |
| ground concentration ||q||^2/4 | +.002600 | +.002246 |
| negative cross-overlap -p dot q/2 | +.001336 | +.001373 |
| sum | +.043652 | +.044048 |
Canopy concentration accounts for 90.98% / 91.79% of coefficient (algebraic attribution, NOT causal mediation). Cross overlap term changes sign when one site is omitted. Jaccard mean .01990, slope -.014063, all LOSO negative; shared recorded species mean .3167, slope -.209051. Some decline in recorded overlap exists; do not say zero change in overlap. Near-disjoint rosters limit identifiability.
General symmetric trait distance D: beta = (2 p'Dq - p'Dp - q'Dq)/4. A decline in within-layer Rao diversity can raise beta while mean cross-layer distance remains unchanged. Exact example with disjoint layers each 4 equally weighted species vs each one species: cross distance 1 both cases; alpha .75 -> 0; gamma .875 -> .5; beta .125 -> .5. Numerically verified. This is metric behavior, not newly established ecological law. No use of absent-species matrix as true occurrence.
## Decision
Retain counter-direction as local descriptive result; original study already shows canopy disturbance sensitivity. Novel candidate contribution is distinguishing between-layer differentiation from within-layer impoverishment and cross-layer distance. Avoid interpreting larger beta as added niches, and avoid forcing all sources into a negative-beta loss hypothesis. Next independent prospective test should prespecify total, within and cross-layer trait distances jointly; compare same species/traits, direct measured structure and observation support, and retain zero-record sites as separate observation endpoint. Only four common observed labels here, no common-margin inference. Missing arboreal trait labels require exact publisher supplement or verified trait crosswalk; no further favorable outcome selection on partial archive. No causal effect, regional replication or Nature-level claim. No submissions or raw station files committed.
