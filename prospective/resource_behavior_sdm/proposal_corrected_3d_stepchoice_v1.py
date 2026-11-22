"""Proposal-density audit for sampled 3D step-choice risk sets.

Source-free. Given one endpoint drawn from a target p_mu and K control
endpoints drawn independently from q, the conditional observed-label
likelihood is proportional to p_mu(x_j)/q(x_j).
If p_mu(x) is proportional to mu(x)*exp(beta*f(x)), use the exact offset
log(mu/q). This is NOT continuous ssf3D, field-bat ecology, or an
authenticated data adapter.
"""
from __future__ import annotations
from collections import defaultdict
import math

RIDGE = 0.003
MIN_BATS = 6


def _numeric(x):
    return type(x) in (int, float) and math.isfinite(float(x))


def validate(records):
    if not isinstance(records, (list, tuple)) or len(records) < 48:
        raise ValueError("STOP_INSUFFICIENT_OR_MISSING_RISKSETS")
    keys = set()
    bats = set()
    for event in records:
        if not isinstance(event, dict):
            raise ValueError("STOP_INVALID_RISKSET_TYPE")
        for k in ("bat", "site", "night", "step"):
            if not isinstance(event.get(k), str) or not event[k].strip():
                raise ValueError("STOP_INVALID_ANIMAL_SITE_NIGHT_STEP_IDENTIFIER")
        key = tuple(event[k] for k in ("bat", "site", "night", "step"))
        if key in keys:
            raise ValueError("STOP_DUPLICATE_SOURCE_STEP")
        keys.add(key)
        bats.add(event["bat"])
        if (event.get("proposal_fitted_on_training_only_or_external") is not True or
            event.get("controls_independent_of_observed_endpoint") is not True or
            event.get("reference_measure_prespecified") is not True):
            raise ValueError("STOP_PROPOSAL_PROVENANCE_NOT_ESTABLISHED")
        c = event.get("choices")
        idx = event.get("observed_choice")
        if (not isinstance(c, list) or len(c) < 4 or type(idx) is not int
            or not 0 <= idx < len(c)):
            raise ValueError("STOP_INVALID_MATCHED_SAMPLED_CONTROLS")
        for row in c:
            if not isinstance(row, dict):
                raise ValueError("STOP_INVALID_CANDIDATE_TYPE")
            if not _numeric(row.get("resource_height_feature")):
                raise ValueError("STOP_MISSING_OR_INVALID_HEIGHT_RESOURCE_FEATURE")
            for field in ("reference_mass", "proposal_mass"):
                v = row.get(field)
                if not _numeric(v) or not 0 < float(v) <= 1.0:
                    raise ValueError("STOP_UNVERIFIED_POSITIVE_PROPOSAL_OR_REFERENCE_MASS")
    if len(bats) < MIN_BATS:
        raise ValueError("STOP_TOO_FEW_INDEPENDENT_ANIMALS")
    return tuple(records)


def _logits(event, beta, corrected):
    scores = []
    for row in event["choices"]:
        offset = (math.log(row["reference_mass"] / row["proposal_mass"])
                  if corrected else 0.0)
        scores.append(beta * row["resource_height_feature"] + offset)
    return scores


def _probabilities(scores):
    m = max(scores)
    w = [math.exp(s - m) for s in scores]
    total = math.fsum(w)
    return [v / total for v in w]


def _balanced_weights(records):
    nights = defaultdict(set)
    counts = defaultdict(int)
    bats = {r["bat"] for r in records}
    for e in records:
        key = (e["bat"], e["site"], e["night"])
        nights[e["bat"]].add(key)
        counts[key] += 1
    return [1.0 / (len(bats) * len(nights[e["bat"]]) *
                   counts[(e["bat"], e["site"], e["night"])])
            for e in records]


def _objective_gradient_hessian(records, w, beta, corrected):
    loss = RIDGE * beta * beta / 2
    grad = RIDGE * beta
    hessian = RIDGE
    for e, weight in zip(records, w):
        prob = _probabilities(_logits(e, beta, corrected))
        x = [row["resource_height_feature"] for row in e["choices"]]
        chosen = e["observed_choice"]
        av = math.fsum(p * xx for p, xx in zip(prob, x))
        loss -= weight * math.log(max(prob[chosen], 1e-300))
        grad += weight * (av - x[chosen])
        hessian += weight * math.fsum(
            p * (xx - av) ** 2 for p, xx in zip(prob, x))
    return loss, grad, hessian


def fit(records, corrected=True):
    data = tuple(records)
    w = _balanced_weights(data)
    beta = 0.0
    for _ in range(60):
        loss, grad, h = _objective_gradient_hessian(data, w, beta, corrected)
        if abs(grad) < 1e-9:
            break
        step = grad / h
        step_scale = 1.0
        while step_scale > 1e-6:
            trial = beta - step * step_scale
            t_loss, _, _ = _objective_gradient_hessian(
                data, w, trial, corrected)
            if t_loss <= loss + 1e-14:
                beta = trial
                break
            step_scale /= 2
        else:
            raise ValueError("STOP_PROPOSAL_OBJECTIVE_NOT_CONVERGED")
    else:
        raise ValueError("STOP_TOO_MANY_NEWTON_ITERATIONS")
    return beta


def _heldout_score(records, beta, corrected):
    bats = defaultdict(lambda: defaultdict(list))
    for e in records:
        p = _probabilities(_logits(e, beta, corrected))
        bats[e["bat"]][(e["site"], e["night"])].append(
            math.log(max(p[e["observed_choice"]], 1e-300)))
    return math.fsum(
        math.fsum(math.fsum(l) / len(l) for l in nights.values()) / len(nights)
        for nights in bats.values()) / len(bats)


def crossvalidate(records, holdout="site"):
    data = validate(records)
    if holdout not in ("site", "bat"):
        raise ValueError("STOP_INVALID_PROPOSAL_HOLDOUT_UNIT")
    key = lambda e: e[holdout]
    folds = sorted({key(e) for e in data})
    if len(folds) < 2:
        raise ValueError("STOP_NOT_ENOUGH_INDEPENDENT_GROUPS")
    rows = []
    for ordinal, group in enumerate(folds, 1):
        train = [e for e in data if key(e) != group]
        test = [e for e in data if key(e) == group]
        if len({e["bat"] for e in train}) < 4:
            raise ValueError("STOP_TOO_FEW_TRAINING_BATS")
        bc = fit(train, corrected=True)
        bn = fit(train, corrected=False)
        sc = _heldout_score(test, bc, True)
        sn = _heldout_score(test, bn, False)
        rows.append({"fold_ordinal": ordinal,
                     "n_bats": len({e["bat"] for e in test}),
                     "n_steps": len(test),
                     "corrected_beta": bc, "naive_beta": bn,
                     "corrected_log_score": sc,
                     "naive_log_score": sn,
                     "corrected_minus_naive_log_score": sc - sn})
    return {
        "schema": "batter.proposal_corrected_3d_stepchoice_audit.v1",
        "status": "KNOWN_TRUTH_SOURCE_FREE_SAMPLED_STEP_CHOICE_ONLY",
        "holdout": holdout, "n_folds": len(folds),
        "n_unique_bats": len({e["bat"] for e in data}),
        "n_source_risksets": len(data),
        "exact_same_sampled_candidate_sets_scored": True,
        "corrected_offset": "log(reference mass) - log(proposal mass)",
        "reference_measure_and_proposal_authenticated_by_this_code": False,
        "is_full_ssf3d_reproduction": False,
        "resource_causality_or_field_bat_effect_estimated": False,
        "fold_aggregates_without_bat_site_IDs": rows,
        "mean_corrected_minus_naive_log_score": math.fsum(
            x["corrected_minus_naive_log_score"] for x in rows) / len(rows),
    }
