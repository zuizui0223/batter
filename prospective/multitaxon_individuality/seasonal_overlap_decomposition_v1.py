"""Audit spatial X incidence, positive strength, and paired dyad states.
Input MUST be the same valid individual-pair risk set in both seasons.
No GPS source data, biological p-values, dietary partitioning or encounters.
"""
from collections import Counter
import math

def summarize(winter, summer):
    if set(winter) != set(summer):
        raise ValueError("Both seasons must use identical dyad risk sets")
    if not winter:
        return {"status": "NOT_ESTIMABLE_NO_COMMON_DYADS", "n_pairs": 0}
    for x in list(winter.values()) + list(summer.values()):
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not 0 <= x <= 1:
            raise ValueError("Overlap must be finite in [0,1]; missing is not zero")
    n = len(winter)
    w, s = list(winter.values()), list(summer.values())
    a, b = sum(v > 0 for v in w), sum(v > 0 for v in s)
    pw, ps = a / n, b / n
    iw = math.fsum(v for v in w if v > 0) / a if a else None
    is_ = math.fsum(v for v in s if v > 0) / b if b else None
    mw, ms = math.fsum(w) / n, math.fsum(s) / n
    states = Counter((winter[k] > 0, summer[k] > 0) for k in winter)
    result = {
        "status": "DESCRIPTIVE_MATCHED_DYAD_X", "n_pairs": n,
        "winter": {"positive_pairs": a, "incidence": pw, "positive_strength": iw, "mean_X": mw},
        "summer": {"positive_pairs": b, "incidence": ps, "positive_strength": is_, "mean_X": ms},
        "difference_winter_minus_summer": mw - ms,
        "states": {"neither": states[(False, False)], "winter_only": states[(True, False)],
                   "summer_only": states[(False, True)], "both": states[(True, True)]},
        "paired_difference_signs": {
            "winter_greater": sum(winter[k] > summer[k] for k in winter),
            "summer_greater": sum(winter[k] < summer[k] for k in winter),
            "equal": sum(winter[k] == summer[k] for k in winter)},
    }
    if a and b:
        incidence = (pw - ps) * (iw + is_) / 2
        strength = (iw - is_) * (pw + ps) / 2
        residual = (mw - ms) - incidence - strength
        if abs(residual) > 1e-10:
            raise AssertionError("Incidence + strength decomposition failed")
        result.update({"incidence_contribution": incidence,
                       "strength_contribution": strength,
                       "decomposition_residual": residual})
    else:
        result.update({"incidence_contribution": None, "strength_contribution": None,
                       "decomposition_residual": None,
                       "reason": "Positive-overlap strength undefined when incidence is zero"})
    return result
