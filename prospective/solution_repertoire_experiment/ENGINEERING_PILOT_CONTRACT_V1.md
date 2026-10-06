# Engineering pilot contract v1

## Status

**PRE-CONFIRMATORY PILOT ONLY. PILOT ANIMALS ARE NEVER ELIGIBLE FOR THE CONFIRMATORY PRIMARY.**

Purpose:
freeze physical geometry, tracking support, route-capability criteria and trial burden without using confirmatory animals or opening the causal treatment outcome.

The pilot may change engineering parameters only before the confirmatory randomization schedule is generated.

---

## 1. Pilot questions

The pilot may answer only:

1. Are all four route classes physically traversable in both matched families?
2. Is 3-D tracking sufficiently complete for the frozen I/M endpoint?
3. How many repeated flights are needed for a stable 2-D policy estimate?
4. What session burden avoids obvious fatigue/performance collapse?
5. Are A and B matched closely enough in baseline difficulty?

The pilot must **not** test whether OPEN acquisition increases individual specialization.

No OPEN-versus-CONSTRAINED causal p-value is calculated in pilot animals.

---

## 2. Pilot subjects

Use animals that will not enter the confirmatory randomized cohort.

Recommended:
- 4 pilot animals if available.

Pilot animals may be experienced laboratory animals if that is necessary for safe engineering.

Their data are permanently excluded from the confirmatory primary and secondary outcomes.

---

## 3. Route capability candidate rule

Initial candidate rule:

For every route in both A and B:
- maximum 4 isolated-route attempts;
- require at least 2 successful traversals;
- both required successes must have valid 3-D tracking sufficient for the frozen I/M endpoint.

A collision/aborted flight is not a success.

The same isolated-route exposure is given before treatment assignment in the confirmatory cohort, so capability testing also equalizes physical familiarity with all alternatives.

The pilot may tighten this rule for safety or tracking reliability.

It may not relax the rule after confirmatory treatment assignment.

---

## 4. Family-level engineering gate

A route family is acceptable only if pilot evidence shows:
- no route is systematically infeasible;
- no corresponding A/B route has a gross difference in collision/failure burden;
- tracking loss is not concentrated in one route/family;
- shortest-path/aperture/turning-demand mismatches are within the predeclared engineering tolerance.

Exact geometric tolerances must be recorded in:
\`MATCHED_FAMILY_ENGINEERING_RECEIPT_V1.md\`
before confirmatory collection.

If a family fails:
redesign and repeat pilot before freezing the confirmatory contract.

---

## 5. Acquisition-trial planning set

The confirmatory acquisition trial count per family must be selected from:

- 8;
- 12;
- 16 successful valid flights.

No other value is allowed without amending this pilot contract before confirmatory data collection.

Rationale:
published bat obstacle-learning work has detected repeated-flight change over roughly 10–12 flights, while other obstacle-course paradigms commonly support repeated blocks of approximately 10 or more successful flights.

The pilot chooses the **smallest** candidate count that provides adequate endpoint stability without evident fatigue.

---

## 6. Probe-trial planning set

The common-OPEN probe requires an even number of valid flights per family.

Candidate totals per family:
- 8 = 4 early + 4 late;
- 12 = 6 early + 6 late.

Prefer 12 unless pilot burden or tracking loss makes 12 impractical.

The split is always exactly half/half and is never changed after outcome opening.

---

## 7. Endpoint-stability rule

Trial count selection is based on measurement stability, not on treatment effect or individual-specialization significance.

For each pilot animal × family in repeated OPEN flight blocks:

1. calculate cumulative I/M centroid using the first n valid trials;
2. use the full 16-trial pilot block as the pilot reference only;
3. standardize I and M using a pilot-only pooled scale;
4. compute Euclidean distance between the n-trial centroid and the 16-trial centroid.

For acquisition count n in {8,12,16}, choose the smallest n such that:

- median centroid error across pilot animal × family units <= 0.25 standardized policy units;
- at least 75% of units have centroid error <= 0.50;
- no visible monotonic degradation in flight completion across the candidate block.

If no candidate count passes:
the experiment remains structurally unready.

Do not optimize n for identity p-values.

---

## 8. Session burden

The pilot must record:
- successful flights;
- failed/aborted flights;
- collision/contact events;
- inter-trial interval;
- total session duration;
- body mass before/after session if husbandry protocol permits;
- behavioral refusal/cessation.

The confirmatory schedule must respect the facility veterinarian/ethics protocol even if that yields fewer flights per day and more experimental days.

No scientific target overrides welfare stopping rules.

---

## 9. Confirmatory freeze outputs

Before pilot closeout, write:

1. final A/B geometry;
2. route topology map;
3. final capability threshold;
4. final acquisition valid-flight count per family;
5. final common-OPEN probe count per family;
6. maximum planned flights per session/day;
7. minimum valid tracking fraction;
8. missing-flight replacement rule;
9. exact early/late windows;
10. statement that pilot animals are excluded from confirmation.

Only after these are frozen may confirmatory animals be randomized.

---

## 10. Prohibited pilot uses

Do not:
- estimate the causal OPEN-versus-CONSTRAINED treatment effect;
- select routes because they maximize individual differences;
- choose I/M weights from pilot identity;
- tune route geometry to create larger among-individual variance;
- include pilot animals later to increase N;
- use pilot p-values as evidence for the paper.

Pilot evidence is engineering information only.
