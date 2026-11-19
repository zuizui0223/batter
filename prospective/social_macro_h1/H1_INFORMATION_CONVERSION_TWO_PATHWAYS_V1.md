# H1 Information conversion: two fundamentally different pathways, not a single trade-off

**2026-11-19. Prospective mechanistic integration, NOT a new empirical biological discovery.** Source effects belong to original authors; branch is draft and frozen `batter` 3D individual identity study remains untouched.

## Two pathways supported qualitatively by published distinct experiments

| Path | Required private state before social cue | What the social input supplies | Observable behavior | Direct original work | Limits |
|---|---|---|---|---|---|
| **A: social→private (WHERE acquisition)** | Initial exit/patch route unknown or unactionable | A skilled conspecific helps discover a route/patch | Exit during informed partner and solo exit afterwards | Vrtilek et al. 2018 DOI `10.1098/rsos.172483` | Published 4/5 post-demonstrator retention among those who exited with demonstrator; NOT private *pre-cue* spatial memory quantified; maze exit not feeding |
| **B: private WHERE + social WHEN** | Familiar sites already in spatial map | Indirect social signal of resource becoming temporally profitable | Independent revisit of known, currently fruitless tree without following | Lourie et al. 2024 DOI `10.1098/rstb.2024.0060` | Original 10/56 naïve visits after odour manipulation; no individual independent memory-score × cue-accuracy quantification; no individual complete outcome roster in author file |
| **C: reliability vs guild (spatial baseline)** | Learned location, sounds and odors as trained together | None: tests competing *physical features*, not a conspecific | Choice of trained location under conflict | Dixon et al. 2023 DOI `10.1093/beheco/arad001` | Published predator and frugivore both favor location; *not social learning* and cannot be pooled with A/B |
| **D: social emission risk** | Not measured | Predator call signals external danger | Reduced outward inquiry/social vocalization | Gamba-Rios et al. 2025 DOI `10.1098/rsbl.2025.0042` | Published selected 38-responder bat effect; not a memory task or sender's observed food-sharing cost |

The previous narrative of mutually exclusive "private information" vs "social information" is structurally incorrect as a generic model: a social cue can alter an individual's private knowledge state (A) or supplement a private knowledge base (B). The same receiver can display both across different times. This integration has been theorized/published by authors cited; the new programme is a **specific mechanistic and empirical design**, not a novel discovery of the existence of the pathways.

## Minimal state transition and estimands

Let (K_{it}=1) denote independently testable knowledge of a location/route at time (t), and (S_{it}) denote exposure to a knowledgeable demonstrator. A legitimate *social-to-private conversion* parameter would compare the **causal effect of social exposure on later solo performance**:
[
Delta_{mathrm{convert}} =
P(K_{t+1}^{mathrm{solo}}=1mid operatorname{do}(S_t=1))
-
P(K_{t+1}^{mathrm{solo}}=1mid operatorname{do}(S_t=0)).
]

Operationally, compare two sets of originally naive individually marked bats in matched/repeated solo trials: one assigned a demonstrator cue and one to non-demonstrator/no-cue learning, with unbiased observation effort. A conditional response
(P(Y_{mathrm{solo,post}}=1mid Y_{mathrm{with demonstrator}}=1)=4/5)
from 2018 is **NOT** the causal conversion estimand: selection on (Y_{mathrm{during}}) and absence of randomized comparable no-demonstrator exposure may produce biased contrasts.

For pre-existing private spatial memory + social WHEN, use `H1_TWO_CHANNEL_DECISION_RULE_AND_FALSIFIERS_V1.md`: state (m=P(	ext{correct place recall})) independently of cue outcome; cue posterior ((pi,a,b)) for temporal food; utility (R,c_v,c_s). This has a theoretical nonmonotonic (V(m)), but no original source yet measures all parameters in the same independently sampled population. Pre-existing-location memory **cannot** be substituted by later observed visitation to define (m).

For sender/receiver social risk, use a separate emission policy (E_t) and cost of revealing calls, not a signed generic sociality scale. Predator acoustics can suppress emitting without implying the receiver lacks social learning ability.

## Two strong empirical falsifiers, precommitted to independent holdout

1. If a demonstrator makes the naive bat leave during the cue but the bat reliably fails to use the exit after removal (with valid solo observation), this is **following/dependence, not social→private conversion**. Report those negative cases, including animals never exiting with cue, rather than fitting only successful mice/bats.
2. If social activation-of-fruiting cues aid bats with **no independently acquired knowledge of where the target lies** despite the cue having no spatial content, the timing-only model cannot explain the outcome; either hidden location information was available or its required place-memory gating was false.
3. Across two or more independent populations using the same task, test whether later solo success increases with demonstration duration or quality after controlling baseline solo experience, not whether frugivores have large roost groups.

## Source data actual status

2018 vampire maze original supplementary is public (`rsos172483supp1.csv`, Figshare collection `10.6084/m9.figshare.c.4128575`, Europe PMC `PMC6030285`). **Original individual trial-row access / SHA / column schema not yet verified at this writing**; an isolated source-gate action is registered. 2023 Dixon article cites Dryad `10.5061/dryad.pzgmsbcr7`; direct source DOI verification is running separately; no claim of downloaded bat trial tables.

Any source found will be handled with physical subject and triad as independent levels, before/during/after phases in original coding, and no double counting across papers from Panama; 2018/2023 Panama experiments also cannot be counted as independent geographic test regions.

**No grand universal biological result is justified from these sources.** The near-term contribution is an auditable distinction between (1) social learning of private knowledge, (2) application of social timing to remembered places, and (3) listening/emission risk, with precise independent measurements needed for a new test.
