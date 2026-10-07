# Public causal synthesis v1

## Status

**CURRENT PUBLIC-DATA BIOLOGICAL SYNTHESIS.**

This document integrates only results already frozen before their numerical outcomes were opened, plus the frozen JAE/wild evidence boundary.

It does not reopen any failed field gate and does not alter JAE v0.4.0.

---

# Central biological result

The public-data programme now supports an asymmetry:

> **environmental and sensory context readily change behavioral expression, but established individual organization is substantially harder to erase than expression is to move.**

At the same time:

> **experience can refine personal organization, but two independent randomized developmental manipulations changed phenotype without demonstrating a change in the total amount of individual differentiation.**

Those manipulations were:
- broad environmental enrichment;
- developmental access to auditory feedback required for normal vocal learning.

Therefore formation and maintenance should not be treated as the same process.

A useful biological architecture is:

[
	heta_i(t)
=
	heta_i^{0}
+
h_i(t)
]

and

[
x_{i,e,t}
=
mathcal{R}_e!left[	heta_i(t)ight]
+
epsilon_{i,e,t},
]

where:
- (	heta_i^0) = persistent intrinsic/predispositional contribution;
- (h_i(t)) = identity-specific historical refinement;
- (mathcal{R}_e) = context-dependent expression map;
- (epsilon) = unresolved bout-level realization.

The current evidence constrains each part differently.

---

# 1. Formation: history refines individuality, but broad enrichment does not simply amplify it

## Juvenile movement history

In the juvenile first-flight programme:

Earliest two structurally valid days predicting late movement:
- E = **+15.19**;
- p = **0.1655**;
- 8/14 positive;
- unsupported.

Recent two days versus earliest two:
- Q = **+144.08**;
- p = **0.0001**;
- 10/14 positive.

Thus later personal movement history becomes much more identity-informative than the earliest independent movement history.

This supports:

> **personal organization is substantially refined through individual history.**

It does not establish that one external environmental treatment creates the between-individual differences.

## Randomized early-enrichment test

Independent public randomized experiment:
Rachum et al. 2025, Egyptian fruit bats.

Season-2 frozen cohort:
- n = **29**;
- enriched = **14**;
- impoverished = **15**;
- City = 9/10;
- Country = 5/5.

Frozen behavioral vector:
- Boldness;
- Exploration;
- Activity.

After removing the common treatment-group change:

- V_enriched = **2.656639**;
- V_impoverished = **1.921940**;
- D = **+0.734699**;
- 199,999 origin-stratified randomizations;
- p = **0.167785**.

Verdict:

**UNSUPPORTED_INDIVIDUALIZATION**

The enriched group is more dispersed in the observed direction, but randomization does not support the claim that enrichment caused increased individual differentiation.

Therefore:

> **history dependence is not equivalent to a confirmed simple environmental variance amplification effect.**

A post-primary exact decomposition shows that the observed positive D is directionally coherent rather than cancellation-driven:

- Boldness contribution = **+0.465792**;
- Exploration = **+0.250837**;
- Activity = **+0.018070**;
- all **3/3** traits point enriched > impoverished;
- cancellation ratio = **0**.

Thus enrichment shows an **expansion-like tendency across the measured personality dimensions**, but the randomized evidence remains insufficient for confirmatory increased individualization.

The broad environment can affect behavior without necessarily increasing the amount of laboratory individuality.

### Post-primary descriptive state rewriting

A pre-authorized descriptive secondary compared three leave-one-out models of Trial 3:

- B = own baseline only;
- G = treatment-group post state only;
- B+S = own baseline + shared treatment-associated shift.

Overall mean squared error:
- B = **3.137006**;
- G = **4.189011**;
- B+S = **2.628609**.

Thus the best simple overall description is:

[
\text{later state}
\approx
\text{personal baseline}
+
\text{shared environmental shift}.
]

Treatment-group decomposition is informative:

### Enriched
- B = **4.060592**;
- G = **3.091958**;
- B+S = **3.081073**.

### Impoverished
- B = **2.274992**;
- G = **5.212927**;
- B+S = **2.206309**.

This secondary is descriptive only, but it suggests a more specific biological picture:

> **enrichment may reposition behavioral state strongly without confirmingly increasing the amount of individuality, whereas impoverished animals retain stronger direct baseline-state predictability.**

The safe synthesis is state recalibration, not confirmed convergence or erasure.

## Randomized developmental auditory-feedback manipulation

Independent public experiment:
Elie et al. 2024, Egyptian fruit bats.

Ten pups were randomly assigned shortly after birth:
- hearing / saline control = **5**;
- deafened / kanamycin = **5**;
- each treatment = **3 females + 2 males**.

Adult whole-repertoire vocal phenotype:
- **28,091** good-microphone-quality calls;
- **28** fixed acoustic features;
- bat is the biological unit;
- minimum finite support = **1,037 calls per bat × feature**.

Frozen whole-repertoire individualization primary:
- one 28-D centroid per bat;
- treatment-blind scaling across the ten bat centroids;
- shared sex × treatment centroid removed;
- exact sex-conditioned treatment randomization:
  (inom{6}{3}inom{4}{2}=120) assignments;
- two-sided test fixed before acoustic values were opened.

Result:
- V_hearing = **15.766760**;
- V_deaf = **17.192257**;
- D = V_hearing − V_deaf = **−1.425497**;
- exact two-sided p = **0.716667**;
- verdict = **NO_DIFFERENCE_IN_AMOUNT**.

The source study establishes that developmental auditory feedback affects learned vocal production, but the frozen re-analysis does not show a detectable effect on the **total amount of adult whole-repertoire individual differentiation**.

Thus:

> **developmental feedback can alter learned phenotype without necessarily altering how much individuals differ overall.**

Sex-specific directions were opposite (female D positive; male D negative), but these are descriptive only and cannot be promoted into subgroup rescue.

A post-primary exact additive decomposition across all 28 features shows that the null total is not uniform invariance:

- positive feature contribution sum = **+3.746740**;
- negative contribution sum = **−5.172237**;
- total absolute contribution = **8.918976**;
- net D = **−1.425497**;
- positive / negative features = **15 / 13**;
- cancellation ratio = **0.840173**.

This is consistent descriptively with **reallocation of individual differentiation across acoustic dimensions** rather than simple gain or loss of total individuality.

No feature-wise causal p-values are authorized.

## Developmental effects are not one-dimensional changes in individuality

The randomized enrichment and auditory-feedback experiments manipulate very different developmental inputs:

1. broad environmental complexity / enrichment;
2. access to auditory feedback required for vocal learning.

Both affect phenotype in their source studies.

Yet neither frozen re-analysis confirms a treatment effect on the **total amount of multivariate individual differentiation**.

The post-primary decompositions reveal two distinct descriptive patterns:

### Enrichment — expansion-like

All three frozen laboratory personality dimensions contribute in the same positive direction to the enriched-minus-impoverished dispersion contrast.

The total increase is not confirmatory (p=0.167785), but it is not produced by cancellation.

### Auditory feedback — reallocation-like

Fifteen of 28 acoustic dimensions contribute hearing > deaf and thirteen contribute hearing < deaf.

Large opposing feature-level contributions cancel by about **84%**, leaving little net whole-repertoire difference.

Thus the public data suggest that developmental experience can alter the **geometry/composition of individuality** in more than one way:

- coherent expansion/contraction across traits;
- redistribution across dimensions with little net change.

Therefore the strongest bounded statement is:

[
oxed{
	ext{developmental environment can change phenotype and the structure of individual differences}

otequiv
	ext{simple change in total individuality}
}
]

The decomposition evidence is descriptive, not feature-wise confirmatory.

This does **not** mean development is irrelevant to individuality.

The juvenile own-history result still shows strong identity-specific refinement.

Instead it implies that formation is increasingly a question of **which dimensions and trajectories become individualized**, not only how much total between-individual variance exists.


## Randomized developmental auditory-feedback test

Independent public experiment:
Elie et al. 2024, Egyptian fruit bats.

Design:
- 10 pups randomly assigned shortly after birth;
- hearing/saline = 5;
- deafened/kanamycin = 5;
- each treatment = 3 females + 2 males;
- adult phenotype recorded 3–4 years later.

Frozen whole-repertoire representation:
- 28,091 adult vocalizations;
- 28 source acoustic features;
- all 10 bats;
- bat is the biological unit;
- smallest finite support = 1,037 calls per bat × feature.

After treatment-blind feature scaling and removal of sex × treatment common state:

- V_hearing = **15.766760**;
- V_deaf = **17.192257**;
- D = **-1.425497**;
- exact sex-conditioned randomization space = **120**;
- extreme |D| assignments = **86**;
- exact two-sided p = **0.716667**.

Verdict:

**NO_DIFFERENCE_IN_AMOUNT**

The source experiment causally establishes that auditory feedback is needed for normal learning of subsets of the vocal repertoire.

Yet the frozen individualization analysis does not show that feedback changed the **total amount of adult between-individual vocal differentiation**.

Thus a second independent randomized developmental experiment supports:

> **developmental environment can change phenotype without necessarily changing how different individuals are from one another.**

The two formation experiments now converge on a causal boundary:

[
\boxed{
\text{developmental environmental effect}
\not\Rightarrow
\text{change in total individualization}
}
]

This does not mean development is irrelevant to individuality. The juvenile-history analysis shows that personal history becomes more identity-informative. It means that the amount of individuality is not a simple monotonic output of broad enrichment or access to auditory feedback.

---

# 2. Maintenance and portability: controlled manipulations repeatedly fail to erase individual organization

Four independent public experimental systems now converge.

## Pipistrellus kuhlii — external sensory masker

Frozen movement endpoint:
3-D angle of attack.

Baseline -> masker:
- K = **+4.941°**;
- 5/6 positive;
- exact p = **0.04028**.

Foam no-masker -> foam + masker:
- K = **+6.779°**;
- 5/5 positive;
- exact p = **0.025**.

Interpretation:

> individual movement bias remains predictive while sensory conditions are experimentally altered.

## Myotis daubentonii — five-level masking gradient

Frozen movement/performance endpoint:
log flight time.

Complete bats:
- n = **3**.

Across five source noise conditions:
- A = **+0.377542**;
- exact assignments = **1296**;
- true biological mapping uniquely most extreme;
- p = **1/1296 = 0.00077160**;
- 3/3 bats positive;
- all five noise contexts positive.

Biological n remains small, but within-experiment identity correspondence is exceptionally consistent.

## Eptesicus fuscus — reversible central auditory perturbation

Four DREADDs bats.

Frozen 4-D vocal vector:
- call duration;
- bandwidth;
- IPI;
- call rate.

After treatment × trialtype pooled residualization:

- K = **+1.004452**;
- 4/4 positive;
- true same-bat mapping rank = **1/24**;
- exact p = **1/24 = 0.041667**.

This is the strongest exact mapping rank possible with n=4.

Interpretation:

> reversible central auditory perturbation altered common vocal expression without erasing all individual-specific multivariate organization.

## Pipistrellus kuhlii — path-integration / navigation-context manipulation

Independent public source:
Aharon, Sadot & Yovel 2017.

Frozen Figure-1 bilateral turning-location endpoint:
- 4 bats;
- 3 source-defined navigation conditions;
- 10–15 valid trials per bat × condition;
- no zero-sentinel ambiguity.

After condition-level mean removal and leave-one-condition-out identity testing:

- K = **+3.695264**;
- **4/4 bats positive**;
- all 3 condition-level mean advantages positive;
- exact cross-condition null = **576** mappings;
- exact p = **0.00347222**;
- observed biological mapping rank = **2/576**.

Leave-one-bat-out K remains positive regardless of the deleted bat.

Interpretation:

> **individual turning-location organization remains identifiable across experimentally altered navigation conditions after common condition shifts are removed.**

This adds a nonredundant path-integration / navigation-context manipulation to the perturbation evidence.

---

# 3. What the perturbation convergence means

The four systems differ in:

- species;
- laboratories;
- perturbation type;
- behavioral domain;
- endpoint;
- statistical architecture.

They do **not** identify one universal latent variable.

But jointly they support the bounded cross-system principle:

[
oxed{
	ext{strong current perturbation}

otRightarrow
	ext{erasure of all individual organization}
}
]

This is stronger than ordinary repeatability.

The experiments manipulate current context.

The relative information identifying individuals survives those manipulations.

Thus the stable biological object is not adequately described as one fixed expressed value.

---

# 4. Portability: coarse personal organization transfers more broadly than detailed geometry

## Rhinolophus nippon

Transparent two-axis policy:
- FlightIntensity;
- ManeuveringExtent.

Cross-environment policy identity:
- K = **+0.55428**;
- 5/5 positive;
- p = **0.0001**.

Held-out environment prediction:
- supported;
- p = **0.0002**.

Scale-free route geometry identity:
- K = **+0.38857**;
- p = **0.0153**.

But the same-data mechanism programme shows that detailed geometry is more context specific than the coarse I/M organization.

Adult biological n = 5, so this is deep repeated-measures mechanism localization, not broad prevalence inference.

## Independent Carollia perspicillata

Fixed Rhino I/M representation:
- K = **+0.34758**;
- p = **0.0007**.

FlightIntensity:
- K = **+0.36775**;
- p = **0.0014**.

Fixed Rhino detailed scale-free geometry:
- K = **-0.0350**;
- p = **0.2144**.

Thus:

> **coarse personal organization can generalize where detailed trajectory geometry does not.**

Miniopterus does not show the same coarse portable axis under the tested framework, so this is not universal across bats.

---

# 5. Wild expression: the laboratory carrier-to-niche bridge remains unresolved

The preregistered wild FlightIntensity carrier gate required >=3/4 panels.

Observed:
- PASS;
- PASS;
- FAIL;
- structural STOP.

Overall:
**2/4 — FAIL.**

Therefore:
- the wild policy-to-vertical-shape bridge remains closed;
- post-outcome H/V decomposition is exploratory only;
- selected carrier-positive panels cannot reopen the bridge.

This matters conceptually.

The laboratory evidence for persistent/portable individual organization is stronger than the evidence linking that organization to wild vertical niche structure.

Do not collapse:
- personal organization;
- spatial niche;
- synchronous partition.

---

# 6. The new biological picture

The old simple picture would be:

[
	ext{different environment}
ightarrow
	ext{different individuals}
ightarrow
	ext{different spatial niches}.
]

The public-data evidence does not support that simple chain.

A better picture is:

[
oxed{
	ext{predisposition}
+
	ext{identity-specific history}
ightarrow
	ext{persistent personal organization}
ightarrow
	ext{context-specific expression}
}
]

with ecological spatial consequences as a separate downstream layer.

Key asymmetry:

### Formation / rewriting
- personal history becomes more identity-informative;
- broad randomized enrichment does not confirm increased differentiation;
- randomized developmental auditory-feedback loss does not change total adult vocal individualization;
- descriptively, enrichment is best approximated by personal baseline plus a shared environmental shift.

Therefore environmental effects on phenotype and environmental effects on **amount of individuality** are empirically separable.

### Maintenance / portability under manipulated current context
- external sensory perturbation: retained individuality;
- graded masking: retained individuality;
- central auditory perturbation: retained individuality;
- navigation-context manipulation: retained bilateral turning organization.

### Expression
- current conditions alter movement/vocal behavior strongly;
- detailed realized geometry is context specific.

### Wild consequence
- direct carrier-to-vertical-niche bridge remains unconfirmed.

---

# 7. Strongest current ecological interpretation

The strongest public-data interpretation is:

> **Individual specialization behaves less like a context-specific expressed value and more like persistent personal organization whose expression is repeatedly recalculated in the current environment.**

The two randomized developmental experiments add:

> **environmental experience can strongly alter behavioral phenotype without necessarily changing the amount of individuality.**

And therefore:

> **the persistence of individuality is better established than a simple environmental mechanism for its initial formation.**

This distinction is the main causal advance.

It explains why:
- individuals can remain individually recognizable across strong perturbations;
- routes/geometry can change while personal organization persists;
- developmental history can refine individuality;
- broad enrichment need not simply inflate between-individual variance;
- persistent specialization need not require continuous exclusive spatial partition.

---

# 8. What this changes relative to ordinary individual-specialization framing

Much of individual-specialization ecology asks:
- how much individuals differ;
- whether environments alter the magnitude of specialization;
- whether resource use partitions.

The current programme instead separates:

1. **formation** — how personal organization emerges/refines;
2. **storage/maintenance** — whether identity-bearing organization survives perturbation;
3. **expression** — how current context maps organization to behavior;
4. **ecological consequence** — whether that expression creates niche/spatial partition.

The evidence shows these are empirically separable.

A change in one layer need not imply a change in the others.

---

# 9. Current public-data ceiling

Supported:
- history-specific refinement;
- low-dimensional cross-task portability;
- multiple controlled perturbation non-erasure results;
- independent navigation-context portability in Aharon Figure 1;
- cross-species generality for a coarse policy component;
- context specificity of detailed realization.

Not supported:
- broad enrichment causes increased individualization;
- developmental auditory feedback changes the total amount of adult whole-repertoire vocal individualization;
- developmental auditory feedback changes total adult whole-repertoire vocal individualization;
- one universal bat policy axis;
- one universal detailed geometry;
- confirmed wild policy-to-vertical-niche bridge;
- one known neural/biomechanical storage substrate;
- direct feasible-solution-opportunity -> specialization formation.

Therefore the remaining formation question is narrower than before:

> **What causes individuals exposed to broadly similar environments to take different historical trajectories through behavioral state space?**

Neither broad environmental richness nor developmental access to auditory feedback is sufficient, under the frozen tests, to explain the total amount of individual differentiation.

---

# 10. Next public-data priority

Do not prioritize another repeatability or current-context perturbation dataset.

Aharon has now supplied the independent navigation-information manipulation and is closed for new confirmatory identity searches.

The remaining public-data priority is specifically **formation**.

A new source is worth opening only if it adds one of:

1. randomized/controlled developmental or learning history with individual-level pre/post data;
2. reversible biomechanics within identified individuals;
3. a treatment that changes the history available for policy formation rather than merely changing current expression;
4. an independently specified solution-opportunity manipulation.

The 2024 fruit-bat auditory-feedback manipulation has now been tested and closed: it changes learned vocal phenotype but not the total amount of adult vocal individualization under the frozen whole-repertoire test.

Another current-context perturbation showing non-erasure would add little to the main bottleneck.
