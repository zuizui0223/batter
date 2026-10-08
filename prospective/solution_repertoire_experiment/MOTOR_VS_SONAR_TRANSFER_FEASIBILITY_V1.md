# Motor-versus-sonar transfer: independent feasibility and causal design note

## STATUS
**PROSPECTIVE FEASIBILITY / REDESIGN NOTE ONLY.** No bat testing, ethics clearance, raw acoustic verification or numerical outcome here. This is written after the v1/v2 synthetic outcomes and is **not part of either frozen simulation's confirmatory endpoint**. It may motivate a new versioned and welfare-reviewed protocol but may NOT be silently appended to existing PR #72 P1/P2 or JAE.

## Why current results cannot assign the biological carrier
The fixed B-R4 sentinel can improve after practice on A-R2 or A-R3 because:
1. both involve reusable horizontal or vertical execution skill (motor); OR
2. both share some trained echo scene, visually/acoustically salient obstacle affordance, landmark, decision cue or route-subgoal (perceptual); OR
3. neither alone mediates transfer, but practice induces a broader sensorimotor policy.

The current two coupled synthetic model worlds set Y_i under motor and sensory stories exactly equal for every trial and assignment; **any analysis of only those observed pre/post sentinel costs is incapable of discriminating them**.

## Existing experimental feasibility evidence
- In freely flying `Pipistrellus kuhlii`, real-time playback of amplified self-echoes has been used to manipulate perceived acoustic targets (2020): https://pmc.ncbi.nlm.nih.gov/articles/PMC7668068/ .
- A 2024 published protocol describes phantom-echo playback to bats in a scanning / perch paradigm, not validated independent soundscape swapping during complex 3-D free flight: https://pmc.ncbi.nlm.nih.gov/articles/PMC11615588/ .
- Real/virtual obstacle experiments report virtual echoes not always eliciting the same evasive response as physical obstacle echoes, potentially because angular echo-spread differs: https://pubmed.ncbi.nlm.nih.gov/22085788/ .
- Human motor-sequence generalization can follow shared parsing/structural cues rather than shared motor elements: https://www.nature.com/articles/s41539-023-00194-7 .
- The existing bat 3-D route memory is prior art (Barchi et al. 2013; DOI 10.1242/jeb.073197). Thus neither return to familiar routes nor transfer to a similar task would be novel by itself.

These papers establish **plausible manipulation concepts**, NOT a validated safe apparatus for this exact species/flight room. Especially do not assume a virtual acoustic echo is identical to a real obstacle or that its playback is safe/behaviorally neutral.

## Distinct follow-up: cross physical maneuver and acoustic cue similarity
Keep the **identical physical B-R4 sentinel, identical reward, and identical post-training assay in all test arms**. Orthogonally change two independently randomized features of the *training* experience:

- M: physical maneuver similarity to B-R4 (M0 = practice A-R1, shares neither; M1 = practice A-R2 or A-R3, shares exactly one motor direction).
- C: training echo/visual cue signature is designed to be matched versus mismatched to a *fixed* sentinel-cue reference, without changing the actual safe physical route clearance or rewards.

This gives four M×C training conditions. At a minimum, balance which component is reused (H or V) within M1, but do not falsely assert equal gains on H and V from a pooled positive M effect. Route-to-sentinel motor similarity and designed acoustic cue similarity should be validated **independently**, not inferred from route codes.

If feasible after a separate pilot, the test outcome is the same pre-vs-first-post R4 physical execution cost Y. A randomized blocked model could estimate:
- Δ_M: average Y under physically shared versus unshared motor demands holding assigned cue condition balanced;
- Δ_C: average Y under acoustically matched versus mismatched training scenes holding physical maneuver similarity balanced;
- interaction: cue-based transfer modifies motor transfer.

A trained-route cue manipulation can itself change motor practice quality; Δ_M and Δ_C are causal **total intervention effects**, not purified neural motor and sensory mediators. They acquire a mechanistic reading only if the acoustic scene and technical task difficulty are checked beforehand and if negative controls eliminate direct changes to reward, attention, fatigue and obstacle detectability.

## Hard structural feasibility gates before ANY outcome
1. Independent 3-D optical measurements confirm R4 safety and matching performance demand under all cue interventions; no increased collision risk.
2. Microphone arrays and a source acoustic model confirm that C conditions actually change sonar scene similarity *in the predicted direction*, at spatial positions used by bats. Physical acoustic recording must not be replaced solely with a speaker hardware nominal setting.
3. Check the bat perceives the cue distinction in **separate pilot animals**, without fitting the primary skill transfer outcome or tuning geometry for positive identity results.
4. Verify training physical route feasibility and equivalent practice success across M0/M1 and C0/C1, or formally model/calibrate training-quality differences in a fully independent planned design.
5. Validate high-rate synchronized 3-D flight reconstruction and a reproducible physical performance metric (collision margins, completion/failure, time, independently validated energetics); do not label generic 3D path similarity as energy.
6. Predeclared abort/safety thresholds, bat handling and welfare approval, realistic sample size and attrition; the previous N=18/24 synthetic comparison does not constitute cohort justification.
7. Freeze the actual randomization schedule, route/cue physical identities, exposure counts, reward timing, code commit hashes, and primary inferential test BEFORE any confirmatory animal outcome.

**If any of 1–4 fails, STOP causal motor-versus-sensory attribution.** Report route-choice / performance transfer as a joint sensorimotor effect, not as pure motor 'modules'.

## Why this matters biologically
The interesting new ecological question is not simply that bats can learn 3-D routes. It is:

> Does an individual's previously learned control of one kind of turn or climb provide a reusable performance advantage in another path through the SAME resource/task space, and is that reuse grounded mainly in physical action, perceived acoustic scene, or their interaction?

A transfer effect under the correctly randomized sentinel design can demonstrate experience-dependent **functional connectivity among paths**, without claiming competitive spatial niche partitioning. The separate motor-vs-acoustic manipulation is required to locate the physiological/perceptual carrier.

Fitness and field niche consequences remain unmeasured.
