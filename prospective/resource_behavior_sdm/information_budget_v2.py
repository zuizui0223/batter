"""Noncausal identity-information bookkeeping for 5-D use distributions.

Known-truth mathematics only; no animal telemetry or measured resources.
Chain rule I(ID;B,Z|XY,T) = I(ID;B|XY,T) + I(ID;Z|XY,T,B)
does not imply state allocation causally mediates identity in height.
"""
from __future__ import annotations
import math
from collections import defaultdict
from collections.abc import Mapping

def _mi(joint, outcome, conditioning):
    p_c = defaultdict(float)
    p_i_c = defaultdict(float)
    p_y_c = defaultdict(float)
    p_i_y_c = defaultdict(float)
    vals = []
    if not joint:
        raise ValueError("empty joint probability distribution")
    for event, mass in joint.items():
        if len(event)!=5:
            raise ValueError("five axes (id, XY, time, state, height) required")
        if not math.isfinite(mass) or mass<0 or mass>1:
            raise ValueError("invalid joint mass")
        individual,x,t,b,z=event
        c=conditioning(x,t,b)
        y=outcome(b,z)
        p_c[c]+=mass
        p_i_c[(individual,c)]+=mass
        p_y_c[(y,c)]+=mass
        p_i_y_c[(individual,y,c)]+=mass
        vals.append(mass)
    if not math.isclose(math.fsum(vals),1,rel_tol=0,abs_tol=1e-10):
        raise ValueError("joint density must be normalized")
    info=0.
    for (i,y,c),p in p_i_y_c.items():
        if p>0:
            den=p_i_c[(i,c)]*p_y_c[(y,c)]
            if den<=0:
                raise ValueError("invalid MI denominator")
            info+=p*math.log((p*p_c[c])/den)
    if info < -1e-10:
        raise ValueError("negative information outside floating tolerance")
    return max(0.,info)


def identity_information_budget(joint: Mapping):
    """Exact observational decomposition, in nats per draw from *joint*.

    Conditional terms do not isolate mechanisms absent externally validated
    behavioral labels, detection and appropriate animal-level holdouts.
    """
    xt=lambda x,t,b:(x,t)
    xtb=lambda x,t,b:(x,t,b)
    state=_mi(joint,lambda b,z:b,xt)
    residual=_mi(joint,lambda b,z:z,xtb)
    joint_info=_mi(joint,lambda b,z:(b,z),xt)
    z_marginal=_mi(joint,lambda b,z:z,xt)
    discrepancy=joint_info-state-residual
    if abs(discrepancy)>1e-10:
        raise AssertionError("chain-rule identity failed")
    return {
        "state_allocation_identity_nats":state,
        "within_state_vertical_identity_nats":residual,
        "joint_state_height_identity_nats":joint_info,
        "marginal_vertical_identity_nats":z_marginal,
        "chain_rule_error_nats":discrepancy,
        "ecological_resource_causation":None,
    }
