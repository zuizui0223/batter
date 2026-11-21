"""Prospective paired conditional held-out scoring for high-D resource/behavior SDM.

No empirical bat/ecological model is fitted. Event support and source/time
eligibility must be frozen before this metric is used on original records.
"""
from __future__ import annotations
import math
from collections import defaultdict
from collections.abc import Iterable, Mapping

# (individual, horizontal_cell, time, behavior_state, vertical_bin)
UseEvent = tuple[str, str, str, str, str]


def conditional_heldout_log_score(
    joint: Mapping[UseEvent, float],
    events: Iterable[UseEvent],
    target: str = "height",
) -> float:
    """Score p(z|i,x,t), p(b,z|i,x,t), or p(z|i,x,t,b) in nats/event.

    Unknown states should use 'height', which marginalizes behavior.
    States used in other targets MUST be independently annotated rather
    than reconstructed from the held-out z/height outcome.
    """
    if target not in ("height", "state_height", "height_given_state"):
        raise ValueError("invalid conditional target")
    heldout = tuple(events)
    if not heldout or not joint:
        raise ValueError("empty prediction or heldout event set")
    p_ixt, p_ixtb, p_ixtz = defaultdict(float), defaultdict(float), defaultdict(float)
    values = []
    for event, prob in joint.items():
        if len(event) != 5 or not math.isfinite(prob) or not 0 <= prob <= 1:
            raise ValueError("invalid five-dimensional joint distribution")
        i, x, t, b, z = event
        p_ixt[(i, x, t)] += prob
        p_ixtb[(i, x, t, b)] += prob
        p_ixtz[(i, x, t, z)] += prob
        values.append(prob)
    if not math.isclose(math.fsum(values), 1, rel_tol=0, abs_tol=1e-10):
        raise ValueError("joint prediction is not normalized")
    scores = []
    for event in heldout:
        if len(event) != 5:
            raise ValueError("invalid heldout event")
        i, x, t, b, z = event
        if target == "height":
            den, num = p_ixt[(i, x, t)], p_ixtz[(i, x, t, z)]
        elif target == "state_height":
            den, num = p_ixt[(i, x, t)], joint.get(event, 0.0)
        else:
            den, num = p_ixtb[(i, x, t, b)], joint.get(event, 0.0)
        if den <= 0 or num <= 0:
            return float("-inf")
        scores.append(math.log(num/den))
    return math.fsum(scores)/len(scores)


def paired_conditional_gain(
    candidate: Mapping[UseEvent, float],
    baseline: Mapping[UseEvent, float],
    heldout_events: Iterable[UseEvent],
    target: str = "height",
) -> float:
    """Paired log-score contrast on the EXACT same held-out events.

    No posthoc intersection or pseudocount rescue. A new individual
    without a trained behavior policy must be treated as cold-start STOP.
    """
    events = tuple(heldout_events)
    new = conditional_heldout_log_score(candidate, events, target)
    old = conditional_heldout_log_score(baseline, events, target)
    if not math.isfinite(new) or not math.isfinite(old):
        raise ValueError("STOP_UNMATCHED_HELDOUT_SUPPORT")
    return new - old
