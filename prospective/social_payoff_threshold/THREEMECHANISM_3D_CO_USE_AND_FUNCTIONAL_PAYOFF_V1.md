# From 3D individuality to social co-use: competing ecological mechanisms and discriminating measurements V1

**2026-10-08 | Prospective biological hypothesis, not a new data finding.** Complements [JAE 3D vertical-organization evidence](https://github.com/zuizui0223/batter) without revising any frozen manuscript, JAE p-values or the failed wild-to-lab mechanism bridge.

## 1. Correct novelty boundary — what is already known

The following are **NOT novel claims**:
- “Bats are attracted at low acoustic conspecific activity and avoid at high activity”: already experimental playback/ecological work, e.g. Lewanzik et al. 2019 *J. Animal Ecology* DOI 10.1111/1365-2656.12989 and published 2024 *Molossus* functional trade-off.
- “Resource abundance modifies response to acoustic social information”: already Lewanzik et al. 2019.
- “Co-foraging can lower attack rate or prompt early patch departure”: already Fujioka et al. 2026 (DOI 10.1371/journal.pone.0343485), including arrival/departure Poisson controls.
- “Learning and stable resource use may lower spatial overlap”: earlier Goldshtein et al. 2020 and related prior art.
- “Individuals retain their vertical-use distributions without confirmed excess contemporaneous segregation”: existing JAE programme, not mechanism confirmation.

**Still unverified and potentially useful:**

> In the same individually tracked bat, does a portable 3-D movement/sensing policy change the *causal effect* of an independently imposed social-acoustic perturbation on real prey-capture performance, and does that moderation persist on an unobserved occasion even when other bats can occupy the same 3D volume?

The mechanism-specific feature is joint measurement of **personal policy + independently manipulated physical/sonar opportunity + prey payoff**, not existence of a general social density threshold.

## 2. Ecological decisions: stay/shared airspace vs maneuver vs exit

Let bat i have a premeasured personal control state theta_i from training nights (independent of test successes). At an opportunity state E (prey distribution, 3D route clearance, interference exposure and alternative patch distance), the bat may choose action a ∈ {remain and maneuver, remain on a route, exit to another patch}. A conceptual decision is

```
a*(i,E) = argmax_a E[ successful prey captures per prespecified fixed time
                       - operational travel/search cost | i, E, do(a) ]
```

This is a **decision model**, not an empirically identified optimizer. The value of an alternate patch is counterfactual and not measured in existing datasets; an observed patch-exit decision cannot by itself establish adaptive optimization or energetic payoff. A separate, independently measured short-term reward endpoint must accompany occupancy.

Potential novel prediction conditional on verified experiment:
- If personal maneuver/sensory ability buffers acoustic interference, among bats exposed to the same randomized masker and obstacle opportunity, those with independently higher relevant training policy state will retain more successful capture performance **without requiring exclusive vertical territories**.
- If benefits instead arise from easier patch departure, the same social intervention may reduce local capture rate but raise exit hazard; a bat with low travel cost may leave rather than reconfigure the 3D path. Thus spatial overlap and adaptation need not co-vary monotonically.
- If prey depletion (not acoustic jamming) dominates, prey enrichment rescues capture benefit while matched acoustic loading does not; if acoustic masking dominates, calibrated masker loading changes success even when prey replenishment is held fixed. These mechanisms can coexist and require separately verified manipulations.
- If only shared group-level responses exist, personal training-state×perturbation performance interaction disappears on held-out sessions, and no persistent personalized buffering mechanism has been demonstrated.

## 3. Beware a causal-selection trap

Conditioning performance estimates on *bats that chose to stay in the patch* can bias the comparison: treatment changes leaving, leaving changes whether later capture is even observed, and personal state can also affect staying. This creates post-treatment selection.

**Correct primary ecological estimand:** effect of **assigned** experimental condition on verified captured prey per **fixed predeclared bat-observation window**, counting zero captures after exit within that fixed assignment window (with explicit follow-up rules and detection quality). Report patch-exit hazard separately. Do not report capture success conditional on staying as the sole outcome, and do not silently drop failed captures or early exits.

## 4. Minimal actual validation needed

1. **Independent personal policy measurement:** train on bouts/nights not used in the function test. Features are predeclared (movement-intensity vs maneuvering and/or sonar control), original five-bat Rhino parameter cannot simply be mapped onto new subjects/species.
2. **Randomize one interpretable physical intervention at a time**, e.g. safe valid alternate route availability or calibrated masker/sham, including the original #93 acoustic bench gate; no assumption that changing a gate leaves sonar echoes unchanged.
3. **Independent functional outcome:** verified prey capture per fixed opportunity window, plus independent prey availability and actual receiver-side acoustic exposure. Feeding-buzz intensity is NOT equivalent to captures; call counts are not a physical density count.
4. **Biological replication:** stable bat IDs, repeated independent bat×condition bouts, held-out occasions and enough subjects chosen by precision analysis rather than inflated 5-s-bin sample size.
5. **Interaction and individual-slope identifiability:** planned estimand is policy×randomized intervention on absolute capture success plus corroborating leave/stay choice; an overall sharp no-treatment-effect rejection (PR #95 V5) does NOT identify heterogeneous bat reaction norms.
6. **External ecological link:** even these laboratory/patch mechanisms do not yet demonstrate they generated JAE field vertical-niche signatures. Same-animal or independent species-specific field bridging must be reported separately.

## 5. Exact falsifiers

| Observed independent result | Interpretation | What it cannot prove |
|---|---|---|
| Known route/sonar opportunity improves pooled captures but personal policy fails held-out moderation | Shared flexible task response | Individualized mechanism maintaining specialisation |
| Personal policy moderates interference but is not repeatable across independent nights | Acute state/context modulation | Stable individual policy |
| Stable moderation predicts actual captures while local 3D co-use remains overlapping | Evidence **consistent with** policy-based sharing/buffering | Long-term evolutionary fitness or field JAE mediation |
| Patch exit increases but fixed-window captures do not improve | Avoidance response without measured profit | Adaptive or optimal threshold |
| Prey supplementation but not masker rescues performance | Resource supply mechanism favored in tested design | General acoustic mechanism |
| Device/soundfield checks fail (#93) | Apparatus effect confounded | Route-opportunity acoustic-buffering mechanism |

## 6. Manuscript division

**JAE:** descriptive spatial-use identity and non-detection/upper bound on extra concurrent segregation under observed systems, without causal interpretation inflation.

**Behavioral Ecology draft:** separate previously completed bat formation/acute-perturbation literature data synthesis, with source-by-source limits, prior-art originality bounds and human PI/coauthor review.

**Prospective third mechanism paper:** only if real independent same-bat 3D policy, randomized context and capture data become available. Avoid a third manuscript now built solely from synthetic nulls and untestable adaptive claims.

**Current verdict:** The combined observations motivate this discriminating opportunity×individual-policy×payoff mechanism, but **none of the available public bat sources currently establishes it**. Stop same-source fishing. The study becomes worth conducting when full crossed bat×bout×function and physical calibration are available.
