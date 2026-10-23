# Seasonal spatial-overlap comparison: evidence boundary and next analysis

**20 October 2026 · Audit, not a confirmed cross-taxon result.**

## What is complete and source-verified
The [mule-deer report](DEER_SEASONAL_RX_RESULT_2026_10_20.md) retains 36 original-data months (2018–2020), 836,636 cadence-matched steps and constant annual X cohorts of 66/64/42 animals. Its winter/summer mean X at 5 km was 0.169215/0.009670 (2018), 0.083283/0.027888 (2019), and 0.087878/0.026532 (2020). Forty-eight sensitivity settings have the same sign but represent **three repeated study years, not 48 independent biological replications**. Same-record conditional movement-model gain is small and positive in 27/36 months, not a calibrated identity/partitioning effect.

## Session-reported provisional comparison: NOT SOURCE-REVERIFIED
The previous analysis session reported nominal 5-km winter-minus-summer spatial X contrasts: wild turkey 2019 +0.1223 and 2020 +0.2840, moose 2019 −0.0195, black bear 2020 +0.0002, white-tailed deer 2020 +0.0064. That session also described sensitivity checks and original-source downloads, **but its 12-source numeric outputs, individual risk sets and original bytes were not committed before the session ended**. These numbers are preserved only in [the provisional ledger](PROVISIONAL_CROSS_SOURCE_SESSION_LEDGER_2026_10_20.json); do not cite them as independently verified empirical findings, significance tests or evidence of cross-clade generality. The 1–2 versus 3–4 month contrast has no preserved numeric result.

## New exact decomposition and biological question
Fix the *same opportunity-qualified dyads* in both seasons. If X denotes season-specific, pair-day-balanced 2D occupancy overlap, define p=Pr(X>0) and m=mean(X|X>0). Then mean(X)=p*m. If p is nonzero in both seasons:

    Δmean(X) = (p_w - p_s)*(m_w + m_s)/2
             + (m_w - m_s)*(p_w + p_s)/2

The two terms are **symmetric arithmetic contributions**, not causal effects. Also count matched dyad states 00 (neither season overlaps), 10 (winter only), 01 (summer only), 11 (both). Seasonal marginal means and the two positive counts cannot reveal actual rewiring; see [synthetic unit tests](tests/test_seasonal_overlap_decomposition_v1.py) and the [exact helper](seasonal_overlap_decomposition_v1.py). If a season has zero positive dyads, conditional m is undefined and the decomposition terms remain null. Missing shared-date opportunity is never coded as an observed overlap of zero.

### Black-bear marginal example, rounded and NOT source-verified
Prior session: 5-km grid with six winter-positive dyads averaging 0.544 versus fourteen summer-positive dyads averaging 0.232, with the matched dyad denominator N **not retained**. Conditional on a shared N, winter sum=3.264, summer sum=3.248, so Δmean=0.016/N. The incidence component is −3.104/N and conditional-strength component +3.120/N: near cancellation. An illustrative N=78 would give −0.039795 and +0.040000, net +0.000205; N=78 is **not an observed source count**. No particular dyad change can be recovered from these marginals. This is a mathematical insight and hypothesis generator, not evidence of an ecological trade-off.

## Re-acquisition and claim gates
1. Re-download whole original Movebank package manifests, reference tables and GPS data for the source-selected turkey (DOI 10.5441/001/1.671), Wyoming Bighorn moose (DOI 10.5441/001/1.714) and Connecticut black bear (DOI 10.5441/001/1.706). Verify publisher MD5 and disallow partial parsing, outlier omissions without receipts, and ambiguous ID/tag joins. These are **candidate source identities**, not proof of which prior session observations came from each archive.
2. Freeze source cohort, time-of-day/UTC ambiguity, sampling effort and pair-shared observed dates. Analyze both **Dec–Feb versus Jun–Aug within the same calendar year**, and **Jan–Feb versus Mar–Apr**. Require seven matched observed days per pair-month and two qualifying months per season; explicitly label non-estimability. All 1/2/5/10-km widths × four origins must be shown, including null results. The new definition is not retrospectively the missing previous algorithm.
3. Quantify p, conditional m, all 00/10/01/11 paired transitions, and scale-dependent differences; report absolute dyad counts and the eligible denominator, individual/animal count and biological site or study-year. Never use dependent pairs or grid origins as separate population replications.
4. Do not claim universal seasonal convergences, actual synchronous meetings T, independently characterized resource use E, or a direct R→X relationship. Other-taxon R remains unestimated under a comparable model; simply appending these X records to the bat/penguin evidence cannot establish a cross-taxon identity/partitioning mechanism.

**Current endpoint:** the original deer study is source-verified; the cross-taxon numeric session notes are not. The next primary analysis must produce **new source-hash-pinned outputs** for independently eligible additional populations.
