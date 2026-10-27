# Cross-taxon seasonality: dyad incidence versus positive-overlap strength

**Status (20 October 2026):** A mathematical identity and synthetic checks are complete; the prior session's cross-source numeric outcomes were **not preserved as source-verifiable artifacts**. They must remain **PROVISIONAL / NOT INDEPENDENTLY RECOMPUTED**. The repository's existing mule-deer results are separately verified and unchanged. No cross-taxon inference, ecological partitioning claim, or significance test is asserted.

## Exact estimands

Fix the SAME risk set of dyads with adequate observed-date opportunities in each season; let its size be `N` and let `X_ijt` be dyad `ij`'s season-t pair-date-balanced 2D occupancy overlap at a declared grid scale/origin. Define `p_t = N^(-1) sum 1(X_ijt > 0)` and `m_t = mean(X_ijt | X_ijt > 0)`. Then `mean(X_t) = p_t m_t`. If either season has no positive dyads, its conditional `m_t` is undefined; do not set it to zero as though observed.

For seasons `w` and `s` with both conditional means estimable, the algebraic symmetric decomposition (not causal) is:

```
mean(X_w) - mean(X_s)
  = (p_w - p_s) * (m_w + m_s) / 2    [incidence component]
  + (m_w - m_s) * (p_w + p_s) / 2    [positive-strength component].
```

Also count paired dyad transitions: `00` neither season, `10` winter only, `01` summer only, `11` both. Marginal counts and seasonal means alone CANNOT identify these transitions; synthetic counterexamples are in the unit tests. Even observed transitions are changes in discretized spatial occupancy, not proof of interaction or actual synchronous association.

## Black bear: session-reported rounded illustration (not a source result)

At a reported 5-km grid: `n_positive_w = 6`, `m_w = 0.544`, `n_positive_s = 14`, `m_s = 0.232`. These FOUR marginal summary values were reported in an earlier analysis session. The matching dyad-risk-set denominator `N` and dyad identities are no longer available for independent checking. CONDITIONAL ON THE SAME N:

- Unnormalized overlap sums: winter `6×0.544 = 3.264`, summer `14×0.232 = 3.248`. The mean difference is only `0.016/N`.
- Incidence contribution: `−3.104/N`; positive-overlap strength contribution: `+3.120/N`. Their cancellation is an **arithmetic observation**, not statistical evidence of an evolved trade-off.
- For the **illustrative assumption** `N = 78` (not independently observed), the two terms are about `−0.039795` and `+0.040000`, leaving `+0.000205`. The earlier rounded `+0.0002` cross-source difference is compatible with, but does not verify, this assumption.
- The number of overlapping partners and their conditional sharing strength change in opposite directions in these reported marginals. Whether *which particular pairs* rewire is **NOT ESTIMABLE** from the four summaries.

## Previous session provisional contrasts (DO NOT PROMOTE)

The prior session reported signed winter–summer means at a nominal 5-km grid: wild turkey 2019 `+0.1223`, turkey 2020 `+0.2840`, moose 2019 `−0.0195`, black bear 2020 `+0.0002`, white-tailed deer 2020 `+0.0064`. It also reported 16 grid/origin scenarios of reversed direction for moose, and sensitivity of black-bear/white-tailed-deer directions to grid choices. These are retained as **session notes only** because the 12-source output JSON, source-specific cohort risk sets, scripts and original bytes were not committed before that session ended. They cannot be treated as independently verified ecological evidence. Newer reproductions must be marked as new exploratory analyses, not retroactively preregistered results.

### What is verified in GitHub already

Mule deer source DOI `10.5441/001/1.708`: 36 months (2018–2020), source-verified 948,632 original fixes, 836,636 native-cadence steps, and year-constant cohorts 66/64/42 with winter–summer mean X at 5 km of `0.169215−0.009670`, `0.083283−0.027888`, and `0.087878−0.026532`. Each of 48 predeclared year/grid/origin seasonal contrasts is positive in the recorded report, but these are dependent scenarios from **one study/source**. An individual-versus-same-record-pooled movement distribution advantage occurs in 27/36 months with small magnitude. No comparable R was established for the other taxa.

## Re-acquisition and source verification protocol

The accompanying `cross_source_seasonal_overlap_v1.py` is an **additional, newly defined analysis**, not the missing previous algorithm. It selects three already queued original Movebank packages (wild turkey DOI `10.5441/001/1.671`; Wyoming Bighorn Mountain moose DOI `10.5441/001/1.714`; Connecticut black bear DOI `10.5441/001/1.706`) before seeing its new results. It (a) retrieves entire original GPS and reference manifests; (b) validates published original-file MD5, refusing partial archives; (c) joins source animals to their original tags; (d) restricts calendar years to 2019–2020; (e) requires seven *shared observed days per pair-month* and at least two qualifying months in each season, with the same final dyads on both sides; (f) evaluates all 4 widths × 4 origins and two fixed month-window pairs, including no-support cases; and (g) computes incidence, positive strength, and actual paired `00/10/01/11` transitions, publishing aggregate counts only.

Windows are calendar Dec–Feb versus Jun–Aug **within a recorded year**, and Jan–Feb versus Mar–Apr. No alternative winter spanning December of the previous year is assumed. The archive download cap is 170 MiB per complete source package. An oversized or malformed source is STOP, not a partially evaluated sample. Source mixed populations and varying tagging cadence are not harmonized, and the clock may be UTC or GPS time. Inference must remain exploratory even when checksum-verified, until native source site/population, sampling cadence and effort are properly controlled.

### Biological scope

The primary publication question remains which ecological behavioral and spatial dimensions differ versus remain shared across animals, **not** fitting an arbitrary individuality-to-partitioning threshold. `X` is geographic co-use and cannot be called trophic partitioning `E` or actual synchronous encounter `T`. Other-taxon `R` has not been reproduced. A cross-taxon causal link between `R` and `X` is unsupported. In the proposed extension, conditional incidence and positive-sharing strength should be reported separately with stable denominators, support masks, study/year effects and no pseudoreplicated dyad p-values.