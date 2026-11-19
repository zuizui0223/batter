# H1 revised mechanistic law: resource place memory × social timing cues — preliminary theory V1

**2026-11-19. Status: analytic decision-theory model, NOT new observational evidence, novel cognitive mechanism proof, or global phylogenetic inference.** The frozen \`batter\` JAE/BE result remains a separate empirical estimate of individual use of vertical space, not a memory trait.

## Problem with original H3

A universal negative \`private_memory ↔ social_information_use\` correlation was inferred conceptually by classifying fixed food as "individual memory" and ephemeral insects as "social information." The hypotheses omit (i) spatial predictability of a *place*, (ii) temporal uncertainty of resource activation at that place, (iii) identity/content of social cue, (iv) the effect of cue information on actual decisions. Published counterexamples already exist: Lourie et al. (2024) experimentally manipulated odors conveyed at a communal fruit bat roost, showing social timing information can work with individual remembered tree locations. Interpreting published bat flight identity as verified private memory would be a measurement error.

The following model is **classical Bayesian value-of-information theory**, offered as a falsifiable specification, not claiming the theory as a new invention.

## Exact model

For one potentially profitable, spatially known resource patch:
- \(\pi=P(F=1)\) is the prior probability the food is currently available.
- \(m\in[0,1]\) is the focal animal's probability of correctly navigating to this patch from individual spatial memory, *measured independently of cue response*.
- \(R>0\) is the reward from accessing food when the place and time are both correct.
- \(c_v>0\) is the visit/travel cost, paid even if spatial memory is wrong.
- The conspecific timing cue \(Y\in\{+,-\}\) has sensitivity \(a=P(Y=+|F=1)\) and false-positive rate \(b=P(Y=+|F=0)\), with \(a>b\).
- The cost of observing the cue is \(c_s\ge 0\).
- The animal chooses between visit and stay based on expected payoff; no fitness inference or reproductive effects are assumed.

Define \(q=a\pi+b(1-\pi)\),
\(p_+=P(F=1|Y=+)=a\pi/q\),
\(p_-=P(F=1|Y=-)=(1-a)\pi/(1-q)\).

The value of not receiving the social cue is
\[
U_0(m)=\max\{0,m\pi R-c_v\}.
\]
The optimal value with timing information is
\[
U_Y(m)=q\max\{0,mp_+R-c_v\}+(1-q)\max\{0,mp_-R-c_v\}.
\]
The **gross value of information**, before observing cost, is
\[
V(m)=U_Y(m)-U_0(m)\ge 0.
\]
The *net* value from observing it, if optional, is \(V(m)-c_s\); an individual can decline the cue if negative. This model does not assume information use is mutually exclusive with private memory.

## Falsifiable directional result

For the illustrative values \(\pi=0.4\), \(a=0.85\), \(b=0.15\), \(R=10\), \(c_v=3\), \(c_s=0.1\):
- Cue-positive posterior = 0.7906977; cue-negative posterior = 0.1052632; \(P(Y=+)=0.43\).
- The positive cue first induces visiting when \(m>0.37941\), whereas without a cue visiting becomes profitable at \(m>0.75\). The negative cue is never a sufficient reason to visit for \(m\le1\), its threshold is \(m>2.85\).
- **0.37941 < m < 0.75:** only a positive social cue triggers visiting, so \(dV/dm=\pi a R=+3.4\). This is memory–social-timing **complementarity** (higher private place memory raises the value of learning the time).
- **0.75 < m < 1:** the individual would already visit without the cue, but the negative cue can prevent an unproductive visit. Now \(dV/dm=-\pi(1-a)R=-0.6\). This is a **declining marginal informational value** as memory is strong.
- Exact net gain at m=0.25 is -0.10 (cue not worth observing); at m=0.50, +0.31; at m=0.75, **+1.16**; at m=1, +1.01. The net gain is **non-monotonic**. These illustrative inputs were not fitted to observed bats.

A globally negative correlation between individual memory and social information is therefore **not implied by resource predictability alone**. Even in a one-patch optimal-action model, the predicted sign changes with private memory, cue reliability, food timing, travel and observation costs. Other social cue types, e.g. *location* information, have different decision rules; thus pooling WHO/WHERE/WHEN/RISK into one sociality score is inappropriate.

## Theory-to-empirics pathway and strict falsifiers

1. Measure **spatial memory** as cross-night correct navigation/revisit to mapped places without a prior social cue. A repeated 3D flight altitude shape alone is **not** this.
2. Measure **resource temporal predictability** independently (repeat fruit/flower/prey availability at fixed sites, base-rate and switching times) and **social timing cue accuracy** (signal predictive value conditional on place and food).
3. Randomize availability-cue exposure separately from place-search information, and include a genuine no-cue control; distinguish responses from foraging/crowding competition and from emitting/acquiring information costs.
4. Predict **intermediate-memory maximization** for the parameter regime above and reversals when the no-cue visit threshold shifts. Test held-out populations/species using absolute effort-normalized resource-visitation / capture reward, not narrative trophic guilds. If low-memory animals still exploit a purely timing-only cue without any location information, this model's spatial gating assumption is falsified or the signal carried an unmeasured spatial channel.
5. **Separate sender risk**: the choice to broadcast (possibly predation-costly, as studied in Gamba-Rios 2025) is a distinct policy from the receiver's positive value of hearing a cue. Silence need not mean low information competence; no ecological parameter for sender risk has been fitted here.
6. Within the same resource guild/family, distinguish *temporally unpredictable* fixed sites from ephemeral drifting insect swarms. A guild-only test can conflate the different cue channels and is not a test of this model.

## Existing evidence constraints

- Lourie et al. 2024 \`10.1098/rstb.2024.0060\`: direct already-published Rousettus roost-borne fruit odor × personal tree-location logic; this is **prior-art motivation**.
- Kohles et al. 2022 \`10.1111/brv.12881\`: existing theory of foraging information strategies; the model is neither the first social-information framework nor independent external confirmation.
- Gamba-Rios et al. 2025 \`10.1098/rsbl.2025.0042\`: published predator cue suppression of emitted social calls; supports a separate RISK channel but not the private-memory model parameters.
- Lewanzik et al. 2019 \`10.1111/1365-2656.12989\`: acoustic feeding-buzz intensity × receiver pre-activity did not improve held-out-lake prediction in this project's source reanalysis; **does not test the memory-by-timing predictions above**.
- COMBINE Soria et al. 2021 \`10.1002/ecy.3344\`: original-hash verified group-size values in only 45/1342 bat taxa, all 30 majority-plant recorded taxa Pteropodidae. Not viable as a private-memory or information-transfer response.
- Dorrestein et al. 2024 \`10.1002/ece3.70149\`: 84 bat species have published mating-system descriptions (Appendix A); this is **reproductive system, not male foraging information or male-only seasonal aggregation**. Similarly, EuroBaTrait Froidevaux et al. 2023 \`10.1038/s41597-023-02157-4\` has roost-type and foraging trait coverage for 47 European species, **not necessarily individual-group information usage**. Do not use either as direct observed H1 response without source-level verification.

## Reproduction

\`h1_two_channel_value_of_information_v1.py\` implements exact Bayesian posteriors, utility maximization and a 1001-point grid search; \`test_h1_two_channel_value_of_information_v1.py\` checks known posterior identities, switching thresholds, analytic derivatives and no empirical claim inflation. GitHub Actions generates a JSON derived theoretical receipt, not an ecological fitted estimate.

**Next material bottleneck:** independent observations of **personal resource location-memory and social timing-cue value in the same individuals/populations**, plus independent across-species replication, remain unavailable in current sources. Manuscript use should explicitly mark this as a prospective mechanistic hypothesis rather than a supported global inference.
