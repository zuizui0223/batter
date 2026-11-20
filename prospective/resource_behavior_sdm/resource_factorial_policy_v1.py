"""Factorial RESOURCE -> state allocation / within-state height in 5-D use.

Source-free, externally assigned logits and coefficients. NO fitted bat SDM,
no measured fruit supply, no ecological causal estimate. Resource observation
must be independent of test bat height, state labels and detector effort.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Iterable

from resource_behavior_sdm import (
    _softmax, joint_use_distribution, resource_conditioned_state_policies,
    project_horizontal_time,
)
from conditional_scoring import conditional_heldout_log_score


def resource_conditioned_height_policies(
    baseline_height_logits: Mapping,
    resource_by_xy_time: Mapping,
    vertical_response_by_state: Mapping,
) -> dict:
    """phi(z|id,xy,time,state,R) with pre-frozen vertical response coefficients."""
    if not baseline_height_logits or not vertical_response_by_state:
        raise ValueError("height baseline and resource-response coefficients required")
    expected = {(x,t) for (_,x,t,_) in baseline_height_logits}
    if set(resource_by_xy_time) != expected:
        raise ValueError("resource map must match all XY-time keys")
    if any(not math.isfinite(v) for v in resource_by_xy_time.values()):
        raise ValueError("resource map has nonfinite values")
    results = {}
    for (individual,x,t,state), base_logits in baseline_height_logits.items():
        if state not in vertical_response_by_state:
            raise ValueError("missing vertical response for state")
        beta = vertical_response_by_state[state]
        if set(beta) != set(base_logits):
            raise ValueError("height response and outcome support mismatch")
        if any(not math.isfinite(v) for v in beta.values()):
            raise ValueError("nonfinite vertical response coefficient")
        r = resource_by_xy_time[(x,t)]
        results[(individual,x,t,state)] = _softmax({
            z: v + beta[z] * r for z,v in base_logits.items()
        })
    return results


def factorial_resource_use_models(
    horizontal_time_logits: Mapping,
    individual_weights: Mapping,
    base_state_logits: Mapping,
    base_height_logits: Mapping,
    measured_resource_by_xy_time: Mapping,
    state_response: Mapping,
    vertical_response_by_state: Mapping,
) -> dict:
    """Same horizontal marginal for base, state-only, height-only and both.

    No reweighting geographic support, no missing-as-zero interpolation, and
    no preference coefficients learned from held-out bat outcomes here.
    """
    if set(horizontal_time_logits) != set(measured_resource_by_xy_time):
        raise ValueError("resource and horizontal-time support mismatch")
    base_state = {k:_softmax(x) for k,x in base_state_logits.items()}
    base_height = {k:_softmax(x) for k,x in base_height_logits.items()}
    r_state = resource_conditioned_state_policies(
        base_state_logits, measured_resource_by_xy_time, state_response
    )
    r_height = resource_conditioned_height_policies(
        base_height_logits, measured_resource_by_xy_time, vertical_response_by_state
    )
    configurations = {
        "base": (base_state, base_height),
        "state_only": (r_state, base_height),
        "height_only": (base_state, r_height),
        "state_and_height": (r_state, r_height),
    }
    out = {
        label: joint_use_distribution(horizontal_time_logits, individual_weights, s, z)
        for label,(s,z) in configurations.items()
    }
    target = project_horizontal_time(out["base"])
    for label, model in out.items():
        proj=project_horizontal_time(model)
        if set(proj)!=set(target) or any(
            not math.isclose(proj[k], target[k], rel_tol=0, abs_tol=1e-12)
            for k in target
        ):
            raise AssertionError("RESOURCE_FACTORIAL_HORIZONTAL_MARGINAL_CHANGED:"+label)
    return out


def score_resource_factorial(
    models: Mapping,
    heldout_events: Iterable,
    target: str,
) -> dict:
    """Four exact paired test-event scores + arithmetic interaction.

    target='height' marginalizes unobserved behavior. The other supported
    targets require height-independent, separately validated activity labels.
    Observations and folds MUST be frozen elsewhere; this scorer is not a fit.
    """
    keys = {"base","state_only","height_only","state_and_height"}
    if set(models) != keys:
        raise ValueError("exact four candidate models required")
    events = tuple(heldout_events)
    scores = {name: conditional_heldout_log_score(models[name],events,target)
              for name in sorted(keys)}
    if any(not math.isfinite(x) for x in scores.values()):
        raise ValueError("STOP_UNMATCHED_HELDOUT_SUPPORT")
    base = scores["base"]
    s = scores["state_only"]-base
    h = scores["height_only"]-base
    combined = scores["state_and_height"]-base
    return {
        "target":target,
        "n_events":len(events),
        "model_heldout_log_scores_nats_per_event":scores,
        "state_allocation_increment_nats_per_event":s,
        "within_state_height_increment_nats_per_event":h,
        "joint_increment_nats_per_event":combined,
        "score_nonadditivity_nats_per_event":combined-s-h,
        "field_biological_resource_effect":None,
    }
