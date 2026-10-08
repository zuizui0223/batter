# Ecological mechanism hypothesis: where is the cost of sharing 3-D airspace paid?

## EVIDENCE STATUS
**PROSPECTIVE CAUSAL RESEARCH PROGRAM, not published proof and not a registered animal experiment.** Source crosswalk `SOURCE_BACKED_ECOLOGICAL_EVIDENCE_CROSSWALK_V1.md` distinguishes 2012–2026 real experiments, cross-study contrasts, failed wild carrier gates, and unmeasured mechanism links. JAE and existing `batter` main or PR #72 routes are unchanged.

## Primary biological question
**When conspecific bats must share the same three-dimensional task space, what determines whether they avoid interference by diverging in emitted sonar, stabilizing the received echo/reference window, adjusting sonar beam vs flight heading, or converging onto a partner's path?**

These are **not** guaranteed equivalent solutions: they change different parts of active-sensing information processing and can have opposing impacts on individual differentiation.

Existing 2018 4-bat *Miniopterus* divergence versus 2021 2-bat *Miniopterus* nondivergence+trajectory following is cross-study **suggestive only**; it cannot identify density switch without standardized within-study manipulation. 2012 acute CF pair frequency convergence versus 2026 month-long resting CF2 convergence are **different temporal and measurement endpoints**. 2026 high-band masking causes lost prey attacks (six bats, 12 trials each across conditions) but has NOT been manipulated jointly with acoustic colony convergence, spatial overlap or wild niche occupancy.

## Physiologically relevant observables (do not collapse into one ad hoc 'niche' axis)

For a simultaneously tagged group with bat i and conspecific j:

1. **3-D co-use C_spatial**: genuine synchronized x/y/z trajectories, nearest-neighbor distance conditional on flight region, overlap of 3-D occupancy after equal temporal/spatial sampling, and alignment/lead-follow relationships. No invented 3-D distribution if recordings lack full synchronized tracks.
2. **FM emission differentiation D_emit**: per-bout terminal-frequency differences or cross-correlation of emitted *time-frequency signals* between contemporaneous group members. Difference between spectral means is NOT equivalent to individualized beam steering or functional echo separation.
3. **CF-FM echo/receiver protection Q_echo**: target-bat reference-echo frequency stability, noise energy **above f_ref** in an independently calibrated Doppler/prey glint band, sonar beam–head direction offset, received pulse identity and (if possible) prey detection. A small resting CF2 difference need NOT indicate low Q_echo.
4. **Social information use F_follow**: synchronized leader–follower heading/turn-lag and repeatability of the role, while conditioning on distances, speed and task. Dyadic follower alignment is NOT exclusive route 'niche partition'.
5. **Real ecological consequences Q_task**: sensory signal-detection error, obstacle avoidance success/miss, predatory takeoff/capture and validated energetic/time-cost proxy with biological unit, not a p value derived from trillions of position frames.

Do not define a universal 'spatial + acoustic partition budget' with an assumed invariant sum. Such conservation is neither predicted by physics nor supported by the original data.

## Falsifiable competing mechanism predictions

| Rival | Condition | Prediction | Important falsifier |
|---|---|---|---|
| M1 FM emission deconfliction | Same physical routes and reward, additive spectrally overlapping conspecific-like masker versus properly matched control | Increase in D_emit and/or decrease in pulse similarity while spatial overlap need not fall; Q_task maintained if deconfliction functionally effective | No source-attributable acoustic adjustment or no task benefit despite precisely controlled interference |
| M2 CF-FM receiver/fovea stabilization | Same physical group and location, narrow-band masker above/below each animal's f_ref within welfare limits | Greater impairment **above** f_ref independent of emitted-call distance; Q_echo and sonar scan more predictive than interindividual CF2 distance | Equal high/low-frequency jamming impairment after equivalent calibrated noise and true task support |
| M3 Social-path information reuse | Paired animals, common route/task, partners experimentally providing vs withholding useful navigational information with matched density | Greater direction/path alignment, possibly lower sampling/effort cost even at high spatial co-use, without mandatory greater D_emit | Alignment does not change with informative partner cues or leads to no favorable sensory/behavioral difference under matched test |
| M4 Coordinated multimodal allocation | Same identified animals repeatedly switch role and acoustic load with stable task geometry | Context-dependent substitution or co-adjustment between emission tuning, head-beam scan, 3-D steering; stable *individual response functions* only if validated beyond anonymous bout labels | Role/density alone predicts behavior, individual training history adds no held-out gain |
| M5 Pure biomechanics/geometry | Acoustic load perturbed with physical obstacle structure fixed | No differential acoustic/behavioral response after within-animal, within-geometry controls | True independent changes in signal and task output caused by acoustic perturbation alone |

For M1 and M2, prior studies already report acoustic changes and Q_task effects in distinct systems, respectively. Novelty cannot be claimed for those effects individually. The missing test is the **simultaneous physical space × acoustic response × downstream ecological function causal linkage**, ideally in both FM and CF-FM systems without assuming homologous sonar tuning.

## Minimal identification strategy (prospective only; not an approved animal protocol)

A. **Data preflight**: choose independent study where stable physical bat IDs, bat-specific emitted and received ultrasonic pulses, synchronized 3-D coordinates, task geometry, flight-session/time support, and social group roles are verifiable. Source-only headers/metadata before outcomes; block if absent. Never use track-frame IDs as biological IDs.

B. **Within-guild causal experiment first**: keeping obstacles, payoff, actual physical room, handling and bat identities constant, prospectively randomize biologically safe conspecific-signal masking or sonar interference in a within-individual/block-balanced manner. Separately control group size and nearest-neighbor distance. Independent calibration of perceived/spectral signal similarity, noise intensity and bat welfare MUST precede testing. Acoustic data must be measured, not assumed from loudspeaker setting.

C. **Group-context interaction**: only after safety/structural feasibility, compare actual 1-, 2-, 4-bat settings under the same protocol; analyze biologically independent groups and repeat measurements within same bats without pseudoreplicating group assignments. Small anatomical species differences cannot be separated by a simplistic group-size slope across two published studies.

D. **Predeclare functional linkage**, e.g. effect of acoustic masking assignment on 3-D co-use and task outcome, with spectra/beam-angle retained as separate *putative* mediators. No 'acoustic mediator' claim without independently justified exclusion/no-confounding assumptions.

E. **Response mode generality**: only after structural animal-ID gate, test whether one bat's context-response signature transfers to held-out role/geometry, over whole bouts/days (not pooled frames), and is not reducible to size, sensor placement or partner identity. This is the bridge to the older `batter` individual 3D policy story.

## Physical/biological nulls to preserve
- **No-space-partition null**: under assigned acoustic interference, physical 3-D co-use may remain unchanged even with large sound adaptation; quantify precision rather than interpreting a nonsignificant distance p as equivalence.
- **No-obligatory-acoustic-divergence null**: CF-foveal protection can maintain task performance with call convergence. Thus a pooled positive "frequency separation under interference" across FM+CF is NOT the hypothesis.
- **No-personal-policy null**: response to role, geometry and social density is wholly population-shared; do not call 2012 pair tests or 2026 N101 rest frequencies proof of stable individual flight-control rules.
- **No-fitness claim**: time/signal accuracy/prey takeoff is task function, not adult survival or evolutionary selection.

## Scientific relevance to the older programme
The supported movement-policy contrast in the same five *Rhinolophus* lab bats and repeated 3-D spatial use in wild panels cannot currently be linked causally to any of these sonar mechanisms; the originally preregistered wild carrier bridge failed at 2/4. The published parent Figshare 29209493 `Rhinolophus` 45-track CSVs DO include binary `pulse` emission events time-aligned with X/Y/Z. Their post-primary pulse-timing identity is governed by a previously frozen contract. They do NOT contain verified emitted spectral frequencies, beam angles, nor individual received-echo waveforms. **A new synchronised rich-sonar × 3D source is required** for the proposed acoustic-functional mechanism; the old emission-timing-only subset cannot establish it. The older laboratory result should remain a **movement representation**, not be retroactively relabelled a sonar-causal mechanism.

## Current decision: SOURCE-GATED prospective research only
Actual acoustic/3D published studies support **different response repertoires and a genuine acoustic functional payoff**, not an experimentally confirmed unified multimodal partition/allocation rule. Do not open a new within-archive high-dimensional neural decoder or fit an arbitrary combined score to make all cases appear consistent.
