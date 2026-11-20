"""A minimal *synthetic-only* resource × behavior use-distribution kernel.

This module DOES NOT fit bat SDMs or estimate ecological effects. Its purpose
is to enforce a probabilistic interface that preserves 2-D marginals and
separates modeled use from the observation process.

No original GBIF records, individual IDs, GPS tracks, or resource rasters
are included. Inputs are already fitted/frozen *external* scores or policies.
"""
from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping

SpaceTime = tuple[str, str]  # (horizontal cell ID, time stratum)
UseEvent = tuple[str, str, str, str, str]  # (individual, cell, time, state, z)
DetectionStratum = tuple[str, str, str, str]  # (cell, time, state, z)


def _normalized(weights: Mapping) -> dict:
    """Strict normalization, without silently filling missing supports."""
    if not weights:
        raise ValueError("cannot normalize empty support")
    values = list(weights.values())
    if any(not math.isfinite(v) or v < 0.0 for v in values):
        raise ValueError("weights must be finite and nonnegative")
    denominator = math.fsum(values)
    if denominator <= 0.0:
        raise ValueError("positive total weight is required")
    return {key: value / denominator for key, value in weights.items()}


def _softmax(log_scores: Mapping) -> dict:
    if not log_scores:
        raise ValueError("spatiotemporal support must be nonempty")
    if any(not math.isfinite(v) for v in log_scores.values()):
        raise ValueError("all log scores must be finite")
    maximum = max(log_scores.values())
    return _normalized({k: math.exp(v - maximum) for k, v in log_scores.items()})


def habitat_log_scores(
    abiotic: Mapping[SpaceTime, float],
    generic_plant: Mapping[SpaceTime, float],
    linked_plant: Mapping[SpaceTime, float],
    beta_generic: float = 0.0,
    beta_linked: float = 0.0,
) -> dict[SpaceTime, float]:
    """Combine externally calibrated covariates, NOT fitted coefficients.

    beta_linked=0 is a generic-plant ablation, not a fitted null hypothesis.
    For empirical use, every predictor must be cross-fitted/source-independent,
    and every coefficient must be trained without held-out bat outcomes.
    """
    if not abiotic or set(abiotic) != set(generic_plant) or set(abiotic) != set(linked_plant):
        raise ValueError("abiotic/generic/linked predictors require identical support")
    if not all(math.isfinite(v) for v in (beta_generic, beta_linked)):
        raise ValueError("coefficients must be finite")
    combined = {}
    for key, a in abiotic.items():
        g, r = generic_plant[key], linked_plant[key]
        if not all(math.isfinite(v) for v in (a, g, r)):
            raise ValueError("predictors must be finite; missing is not zero")
        value = a + beta_generic * g + beta_linked * r
        if not math.isfinite(value):
            raise ValueError("nonfinite model score")
        combined[key] = value
    return combined


def joint_use_distribution(
    horizontal_time_logits: Mapping[SpaceTime, float],
    individual_weights: Mapping[str, float],
    state_probabilities: Mapping[tuple[str, str, str], Mapping[str, float]],
    height_probabilities: Mapping[tuple[str, str, str, str], Mapping[str, float]],
) -> dict[UseEvent, float]:
    """Build p(x,t,i,b,z)=p(x,t)p(i)p(b|i,x,t)p(z|b,i,x,t).

    'Individual weights' here are a *population mixture assumption*, not
    an observed colony or social-group composition. 'State' is a declared
    behavior class; its interpretation requires independent annotation.
    The conditional tables can differ across x,t and hence be conditioned
    on independently measured resources when later fitted outside this kernel.
    """
    p_xt = _softmax(horizontal_time_logits)
    p_i = _normalized(individual_weights)
    joint = {}
    for (cell, time), horizontal_mass in p_xt.items():
        for individual, individual_mass in p_i.items():
            if individual_mass == 0.0:
                continue
            state_key = (individual, cell, time)
            if state_key not in state_probabilities:
                raise KeyError(f"missing behavior policy: {state_key!r}")
            p_b = _normalized(state_probabilities[state_key])
            for behavior, state_mass in p_b.items():
                if state_mass == 0.0:
                    continue
                height_key = (individual, cell, time, behavior)
                if height_key not in height_probabilities:
                    raise KeyError(f"missing height policy: {height_key!r}")
                p_z = _normalized(height_probabilities[height_key])
                for height, vertical_mass in p_z.items():
                    probability = horizontal_mass * individual_mass * state_mass * vertical_mass
                    if probability > 0.0:
                        joint[(individual, cell, time, behavior, height)] = probability
    if not joint or not math.isclose(math.fsum(joint.values()), 1.0, abs_tol=1e-12):
        raise ValueError("joint distribution did not normalize")
    return joint


def project_horizontal_time(joint: Mapping[UseEvent, float]) -> dict[SpaceTime, float]:
    """Integrate individual, behavior and height (NOT detector-corrected)."""
    projected = defaultdict(float)
    for (_, cell, time, _, _), probability in joint.items():
        projected[(cell, time)] += probability
    return dict(projected)


def project_horizontal(joint: Mapping[UseEvent, float]) -> dict[str, float]:
    """Integrate time as well: the 2-D horizontal use projection."""
    projected = defaultdict(float)
    for (_, cell, _, _, _), probability in joint.items():
        projected[cell] += probability
    return dict(projected)


def identity_vertical_information(joint: Mapping[UseEvent, float]) -> float:
    """I(individual; height | horizontal cell, time), in nats.

    A positive value is statistical individuality, NOT competition, a
    measured physical separation, or a causal explanation.
    """
    p_xt = defaultdict(float)
    p_ixt = defaultdict(float)
    p_zxt = defaultdict(float)
    p_izxt = defaultdict(float)
    for (i, x, t, _, z), p in joint.items():
        if not math.isfinite(p) or p < 0.0:
            raise ValueError("joint weights must be finite/nonnegative")
        p_xt[(x, t)] += p
        p_ixt[(i, x, t)] += p
        p_zxt[(z, x, t)] += p
        p_izxt[(i, z, x, t)] += p
    info = 0.0
    for (i, z, x, t), p in p_izxt.items():
        if p == 0.0:
            continue
        numerator = p * p_xt[(x, t)]
        denominator = p_ixt[(i, x, t)] * p_zxt[(z, x, t)]
        info += p * math.log(numerator / denominator)
    return max(info, 0.0) if info > -1e-12 else info


def detected_event_distribution(
    use: Mapping[UseEvent, float],
    detection_probability: Mapping[DetectionStratum, float],
) -> dict[UseEvent, float]:
    """p(recorded event | event recorded) proportional to p(use)*q.

    q must come from a separate sampling/detection design. This is NOT an
    occupancy estimator; treating non-recording as absence is prohibited.
    """
    observed = {}
    for (individual, cell, time, behavior, height), p in use.items():
        key = (cell, time, behavior, height)
        if key not in detection_probability:
            raise KeyError(f"missing detection probability: {key!r}")
        q = detection_probability[key]
        if not math.isfinite(q) or not 0.0 <= q <= 1.0:
            raise ValueError("detection probability must belong to [0,1]")
        if not math.isfinite(p) or p < 0.0:
            raise ValueError("invalid use probability")
        observed[(individual, cell, time, behavior, height)] = p * q
    return _normalized(observed)


def mean_heldout_event_log_score(
    predicted: Mapping[UseEvent, float], events: Iterable[UseEvent]
) -> float:
    """Transparent event-level log score with NO hidden pseudocount.

    For matched, independently held-out observed usage events only; without
    a predeclared source/time/individual block, this is not a validation.
    """
    values = list(events)
    if not values:
        raise ValueError("heldout event set must be nonempty")
    scores = []
    for event in values:
        p = predicted.get(event, 0.0)
        if not math.isfinite(p) or p < 0.0 or p > 1.0:
            raise ValueError("invalid model probability")
        if p == 0.0:
            return float("-inf")
        scores.append(math.log(p))
    return math.fsum(scores) / len(scores)
