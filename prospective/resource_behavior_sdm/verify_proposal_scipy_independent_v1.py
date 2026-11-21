"""Optional independent SciPy cross-check, NOT in pure-stdlib GitHub CI.

Run from prospective/resource_behavior_sdm with numpy/scipy installed:
    python verify_proposal_scipy_independent_v1.py
Replays generated synthetic datasets from frozen regression tests, but solves
the case-control likelihood independently with scipy optimize and logsumexp.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp

from proposal_corrected_3d_stepchoice_v1 import RIDGE, fit
from test_proposal_corrected_3d_stepchoice_v1 import simulate


def scipy_fit(data, corrected):
    x=np.asarray([[c["resource_height_feature"] for c in e["choices"]]
                  for e in data], dtype=float)
    offsets=np.asarray([
        [math.log(c["reference_mass"]/c["proposal_mass"])
         for c in e["choices"]] for e in data], dtype=float)
    if not corrected:
        offsets=np.zeros_like(offsets)
    observed=np.asarray([e["observed_choice"] for e in data], dtype=int)
    i=np.arange(len(data))
    # Generator fixes 2 nights × 35 steps across all fictional animals:
    # source production evaluator instead supports unequal bat/night weights.
    def f(beta):
        logits=beta*x+offsets
        return (float(np.mean(logsumexp(logits,axis=1)-logits[i,observed]))+
                0.5*RIDGE*beta**2)
    return float(minimize_scalar(
        f,bounds=(-8.,8.),method="bounded",options={"xatol":1e-13}).x)


def run():
    results=[]
    for true_beta in (0., .95):
        allrows=simulate(true_beta=true_beta)
        for site, rows in [("ALL",allrows),
                           ("A",[x for x in allrows if x["site"]=="A"]),
                           ("B",[x for x in allrows if x["site"]=="B"])]:
            for corrected in (False,True):
                a=fit(rows,corrected)
                b=scipy_fit(rows,corrected)
                difference=abs(a-b)
                if difference>1e-6:
                    raise AssertionError("STOP_INDEPENDENT_OPTIMIZER_DISAGREES")
                results.append(difference)
    print("VERIFY_APPROVED_SIMULATION_ONLY",len(results),"fits")
    print("SCIPY_INDEPENDENT_MAX_ABS_BETA_DIFFERENCE",max(results))
    print("NO_ORIGINAL_BAT_GPS_OR_RESOURCE_RECORDS_USED")
    return max(results)


if __name__=="__main__":
    run()
