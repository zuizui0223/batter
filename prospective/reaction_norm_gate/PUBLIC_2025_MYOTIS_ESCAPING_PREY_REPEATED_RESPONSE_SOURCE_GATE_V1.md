# Public Myotis myotis moving-prey responses — repeated-individual source gate v1

**Recorded:** 2026-10-13. **Status:** SOURCE-METADATA AND PUBLISHED-RESULT AUDIT ONLY. No unpublished trial outcomes, raw sensor data, Mendeley files, numeric bat×day responses, statistical contrasts, or new p-values accessed. **Post-publication candidate, not prospective evidence.** No JAE release or bat 3-D results changed.

## Published independent source

Foskolos, I., Hubancheva, A., Skalshøi, M. R., Beedholm, K., Madsen, P. T. & Stidsholt, L. (2025). *Fast vocal-motor tracking of escaping prey in echolocating bats*. **BMC Biology 23:21**, doi: https://doi.org/10.1186/s12915-024-02106-6

- Open methods/results: https://link.springer.com/article/10.1186/s12915-024-02106-6
- Author-listed data+analysis code: Mendeley Data **version 3**, https://doi.org/10.17632/8b57pz6bpj.3 ; https://data.mendeley.com/datasets/8b57pz6bpj/3
- Separate, published wild component: 11 bats; 467 aerial attacks; not paired to the four laboratory individuals. Do **not** join wild success and laboratory identities.
- Laboratory *Myotis myotis*: **4 individual bats**, each on **4 separate daily sessions** for IDs 1–3 and **6 separate daily sessions** for ID 4; total **631 laboratory trials** reported. Exactly **six moving-target regimes** were included each day: 0.08 m at 0.5, 1, 1.3 m/s and 0.24 m at 0.5, 1, 1.5 m/s, with repeated stationary trials. Trial order used a pseudo-random Gellermann schedule. These counts are **not** 631 independent animals or 631 independent days.
- Original paper already found more extensive buzz duration at difficult prey movements in all four subjects; a pronounced target-motion–evoked increase in call interval in **one of four** laboratory individuals (mean latency about 242 ms). The last is **not** evidence of independent-day persistence; it is already **known published outcome**. Replicating that effect from the same archive would not be independent discovery.
- The original laboratory functional endpoint described is **chase/target-pursuit probability**, not independent wild foraging success, net energetic gain, or fitness. The original paper's wild-capture outcomes are from **different individuals and setting**.

## Data access outcome, October 13

The Mendeley landing page reports a deposited dataset with MATLAB figure data and R statistical-analysis files, under CC BY 4.0. However, the public file list is **not rendered in the accessible page text** and direct REST file-list endpoints returned **HTTP 401** in the available retrieval channel (tested both `/datasets/{id}/files?version=3` and `/datasets/publics/{id}/files?version=3`). Thus we **did not verify** bat ID, date, six exact regimes, stationary condition, audiovisual trajectories or chase/buzz variables as **columns in a downloaded file**. A user with browser access may inspect the Mendeley landing page's Download All link; this note does **not** assert that the required trial-level fields are present.

**No downloaded 3-D XYZ trajectories have been identified.** High-resolution audio biologgers and synchronized infrared video in the publication **do not by themselves establish open reconstructable individual 3-D flight coordinates**. A moving prey target is also a sensory/foraging challenge, not the randomized obstacle-clearance intervention envisioned in the existing #95 3-D reaction-norm gate.

## Original Methods and endpoint denominator audit (2026-10-13)

A direct reread of the version-of-record HTML (https://link.springer.com/article/10.1186/s12915-024-02106-6) confirms the following **published figures**, which are NOT new individual outcomes:

| Data grain | Published figure/source count | Consequence |
|---|---:|---|
| Total laboratory attempts | 631 trials / 4 bats | Source exposure count, **not** any specific analytic endpoint denominator |
| Figure 2b pursuit/chase status | 606 trials / 4 bats | Invalid/ambiguous chase trials do not automatically have binary 0 |
| Figure 2c buzz I duration | 474 buzzes / 4 bats | Conditional on usable buzz I; must audit absence/selection |
| Figure 2d buzz II duration | 479 buzzes / 4 bats | Conditional on usable buzz II; distinct eligibility from chase |
| Figure 3 call-interval timing | 391 trials / 4 bats | A selected subset; 59/123 stationary trials sampled to balance figure conditions; **not** all 631 trials |

Do not use these denominators as if the counts were independent observations from different animals. Do not infer independent test replication just because recordings occur on successive days.

**Timing origin is not equivalent across conditions.** The paper's moving-target trials use visually verified physical onset `t0`; **stationary** controls instead assign a **mock t0** using a randomly sampled call-interval threshold derived from moving trials. Since the control t0 depends on the outcome process, a moving-minus-stationary difference of aligned call-interval curves **does not isolate a personal motion-triggered gain**. Additionally, the paper fits an exponential decay curve to the combined normalized CI and subtracts it for its figure. That pooled empirical fit is not an independently measured causal baseline; do not use it as a held-out baseline unless it is trained wholly within training-day data.

**Pursuit outcome meaning:** the publication's 'chase' refers to pursuing/intercepting the moved target in a laboratory trial, whereas a stationary target has no movement to follow; Fig. 2b includes stationary trials as a comparison group. Restrict any primary *motion-response* chase contrast to the **six moving treatments** (easy versus difficult) and report stationary approach/interception separately, rather than interpreting stationary/chase difference as motion-feedback strength. Real prey capture, hunting energetic return and field fitness were not measured for these four laboratory bats.

**Apparatus/batch:** tags were reattached across daily sessions, target onset was triggered when a bat crossed an approach line, and the motor generated noise. Each must be recorded/controlled when possible. The original single-day *motor-without-target-movement* sham trials (108 published) were a different control session, not six independent additional baseline days. These can bound acoustic apparatus artifacts, but cannot by themselves resolve individual-day response persistence.

**Access outcome:** The public dataset landing page explicitly says data+code are deposited under CC BY 4.0; nevertheless, the machine-readable list and zip routes are documented as OAuth2 endpoints, and this session's API requests were inaccessible (401 or retrieval errors). HTML text does not expose file names or trial columns. This is an **access/schema HOLD**, not evidence that the dataset lacks the fields.

## Pre-analysis source-column gate — required BEFORE computing new animal endpoint

1. Confirm physical bat identifier, recording session/date, trial ID, treatment distance/speed, stationary reference, actual temporal order, and recording/calibration batch.
2. Confirm moving-trial chase status with original validity coding (Fig. 2b: 606 valid chase records), and separate buzz I, buzz II and call-timing eligibility; do not code invalid/absent acoustic responses as zero. No assumption of one fully observed 631-trial table.
3. Confirm each of the four bats has within-day challenge + stationary controls on **at least four distinct dates**. If labels have been aggregated to stationary/easy/difficult and day ID lost, independent-re-exposure test is unidentifiable.
4. Confirm replicated trials per bat×day×challenge, and inspect any session dropout, different number of stationary trials, censoring by chase attempt, order/fatigue/learning confounding and daily reattachment of recording tags.
5. Confirm the data license at **file** level, immutable dataset version and digital provenance.

If 1–5 cannot be verified, no bat-level outcome opening or retrospective `PASS`. For time-resolved CI, verify original physically observed stimulus onset for moving trials and do not treat stationary mock `t0` as the same exposure time. For any held-out forecast, recompute all pooled normalization and smoothing using only training days.

## Fixed analysis proposal (exploratory, because published outcomes already read)

**Question:** Does the response of an identified bat to the **same** target-motion treatment, relative to its own stationary-condition baseline, predict that bat's response on an independently held-out day **better than a group-common response**?

For identified bat `i`, day `d`, challenge `c`, response `Y`:
`Delta[i,d,c] = mean(Y | i,d,c) - mean(Y | i,d,stationary)`.
- First fit the **published all-trial pursuit indicator** as a bat×day×challenge aggregated success proportion (not actual capture success); compare held-out Brier/log scores at the trial level, with bat/day clustering. Acoustic outcome (prefer log buzz-II duration among *observed and valid buzz-II trials*) is a **separate conditional phenotype**; first report selection into a valid buzz, rather than conditioning away the chase/no-chase effect.
- Primary repeated-challenge context contrast may use **one fixed published 'difficult' class** (0.24 m/1 and 1.5 m/s) vs stationary. No selection of the most responding bat/treatment/metric after observing a fold.
- Train models using **days 1–2 only**; predict **days 3–4** for all four bats. Day 5–6 available for only bat 4 is an explicitly separate robustness visualization, not part of the group-balanced primary.
- Competing training-only predictors: (M0) pooled group-average challenge response, and (M1) pooled group mean + bat-specific **challenge deviation**. Control for day order if estimable using training days without leaking held-out outcomes. Report unadjusted individual mean (personal intercept) versus actual within-bat **challenge-response slope** as different estimands.
- **Hold-out score**: equal weight to each physically identified bat, and within bat equal weight to eligible test days. Report each bat's difference `Loss(M0)-Loss(M1)`, then across-bat average and all individual signs. Do not count repeated trials or audio frames as independent biological units.
- Four bats yield very imprecise population statements. Ordinary animal-label permutation is **not valid for mean-policy identity under arbitrary bat-specific heteroscedastic noise**, per this repository's #95 calibration. No retrofitted Fisher randomization: pseudo-random order is not a verified exact randomized treatment assignment. No preregistration claim, no 'independent confirmation' from reusing this published dataset.
- If only one individual supports M1, report **case-level effect**, not an individualized group-wide law. Any observed acoustic response does **not** establish 3-D route mechanism, neural memory, improved real prey capture, or adaptive specialization.

## Scientific verdict / boundaries

| Question | Current source verdict |
|---|---|
| Four physically identified bats each challenged under matched moving-target treatments on >=4 dated occasions? | **YES AS DESCRIBED IN THE ORIGINAL METHODS** (not yet matched to file columns) |
| Trial-level outcome files downloaded and schema/independence verified? | **HOLD_ACCESS_SCHEMA_UNVERIFIED** |
| A possible individual acoustic/target-pursuit reaction norm with repeated dates? | **POTENTIALLY TESTABLE**, descriptive post-publication extension only |
| Replicated individual **3-D flying XYZ trajectory** reaction norm? | **STOP_OPEN_3D_XYZ_NOT_VERIFIED** |
| Causal effect on real foraging capture, energy or field 3-D niche individuality? | **STOP_DIFFERENT_OUTCOME/INDIVIDUALS** |

**Prior-art boundary:** Grey, Aung & Abaid (2026), *PLOS Complex Systems*, doi: https://doi.org/10.1371/journal.pcsy.0000100, used SINDy for **group-level** gray-bat acoustic dynamics under different crowding/obstacles, not per-bat physical 3-D equations. Thus neither 'first mathematical model of bat acoustic response' nor 'group equations establish personal control laws' is defensible.

**Next permitted step:** acquire/inspect dataset files **without choosing alternative endpoints**. If the schema meets this documented conditional sensory gate, run a clearly labeled exploratory held-out repeated-day calculation; if not, stop. This is not evidence to change JAE, the five-Rhinolophus archive, or publication status.
