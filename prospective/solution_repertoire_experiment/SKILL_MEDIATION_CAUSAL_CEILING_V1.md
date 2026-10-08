# Causal mediation audit — learned skill can accompany choice without causing it

## Evidence tier
**Mathematical observational-equivalence argument, not animal data or newly verified bat mechanism.** This strengthens interpretation boundaries for PR #83; it does not alter the source numerical results or frozen PR #72, #81 or #82.

## A third rival model defeats a simple skill-mediation interpretation

The paired synthetic main models show that **choice-only observations** cannot distinguish a history-specific behavioral prior from a true path-specific performance advantage. Measuring post-seed cost helps establish whether such a performance advantage actually exists.

But there is a stricter causal limitation: even the joint observational distribution of **choice plus measured cost** may not establish that the performance advantage **caused** preference.

For each individual i and route r, write observed post-acquisition physical cost:

```
c_ir = c0_ir - gamma*1[r=S_i].
```

Suppose `h=a*gamma`, and bonus for the independently randomized reward route B is `Delta`.

### Model A: utility genuinely tracks acquired skill

```
Pr_A(R=r|S,B,Delta,c) ∝ exp(u_ir + a*(Delta*1[r=B_i] - (c_ir-c0_ir))).
```

Since `c_ir-c0_ir=-gamma*1[r=S_i]`, this is

```
Pr_A(R=r) ∝ exp(u_ir + h*1[r=S_i] + a*Delta*1[r=B_i]).
```

### Model B: habit chooses the seed; practice improves skill incidentally

```
Pr_B(R=r|S,B,Delta,c) ∝ exp(u_ir + h*1[r=S_i] + a*Delta*1[r=B_i]),
```

but the causal choice rule *does not consult c_ir*. Repeated route practice nevertheless reduces true measured cost by the same gamma, as in Model A. Consequently:

1. S is still causally randomized;
2. measured pre/post all-route performance is **identical**;
3. choices at baseline and both reward magnitudes are **identical**;
4. randomized seed, reward and cost-association statistics are **identical**.

Thus observational records of **history, reward, routes and route-specific cost measurements** cannot separate these causal models when the resulting conditional distributions are the same. Cost improvement can be an **effect of repeated choice**, rather than the mechanism sustaining choice.

This is an exact rival-model construction, not a claim that the animals use either model.

## Biological and ecological claim ladder

A. **History→choice causality:** independently randomize early route S; establish route-specific later choice after appropriate common-state reset. Supports path dependence.

B. **History→performance causality:** independently randomize S, measure all physical routes before/after exposure on comparable physical scales. Supports history-dependent skill/performance. Caveat: later choice trials themselves may contribute to that performance change; balanced independent forced-route measurement needs careful timing.

C. **Performance→choice causal effect:** after history is held fixed, independently and reversibly manipulate the **physical performance cost** of the routes, with matched sensory/reward cues and safe clearance; assess whether choice changes in the predeclared direction. This is the critical step for skill-mediation rather than mere cost-choice coexistence. If a direct route-cost intervention has other cues, those competing pathways must be documented; an instrumental-variable claim would require an explicit exclusion restriction and is not automatic.

D. **Adaptive significance:** separately demonstrate that any behavioral change improves *net biologically comparable reward–effort–risk return* relative to feasible alternatives, and eventually a fitness-relevant consequence. Higher food reward, shorter time, single-route fidelity or increased energy efficiency alone do not establish evolutionary selection.

## Positive feedback hypothesis, not result

```
early random route experience
  -> route-specific skill accumulation
  -> lower future execution cost
  -> increased route-choice probability
  -> more practice
  -> even lower personal cost.
```

This is one mechanism by which individual specialization could emerge even when all bats have the same external route options and no strong inter-individual spatial segregation. Unlike an assertion of fixed personal morphology, the **experienced environment becomes functionally more favorable for a given individual because of its own training**.

The model predicts a context-dependent tradeoff: in stable habitats, personal route practice may be economically beneficial; after sufficiently large environmental or reward changes, excessive historical fidelity may delay switching and become costly. This offers a falsifiable ecology-first direction, but remains untested.

## Next ethically feasible design requirement
A new prospective independent causal test must manipulate execution difficulty/effort separately from route history and reward, preferably with a matched sham route manipulation and all-animal welfare/flight-clearance pilot. It must not silently change PR #72's fixed design, require unsafe obstacles, or claim that physiological energy expenditure can be inferred from speed alone.

Even a successful experimental cost manipulation would justify only the scope of the manipulated task and outcome, not a universal bat flight law, learned hippocampal storage, or population fitness effect.
