"""Source-gated matched 3D step-choice prediction; NOT a continuous ssf3D or bat result.

For each original step all models use the SAME frozen candidate XY x AGL risk
set. Trained conditional softmax scores obey log p(X,Y,Z) = log p(X,Y) +
log p(Z | X,Y) exactly, allowing horizontal/vertical attribution. This is
not a calibrated species occurrence distribution or full 3D-SSF likelihood.
"""
from __future__ import annotations

from collections import defaultdict
import math

BASE = ("step_m", "log_step_m", "cos_turn", "omega_delta", "forest_structure", "agl_50m")
LEVELS = {
    "M0_3d_movement_structure": BASE,
    "M1_add_resource_xy": BASE + ("resource",),
    "M2_resource_by_height": BASE + ("resource", "resource_agl"),
    "M3_state_interactions": BASE + ("resource", "resource_agl",
                                     "resource_state", "resource_agl_state"),
}
CONTRASTS = {
    "resource_main_M1_minus_M0": ("M1_add_resource_xy", "M0_3d_movement_structure"),
    "resource_height_M2_minus_M1": ("M2_resource_by_height", "M1_add_resource_xy"),
    "state_interactions_M3_minus_M2": ("M3_state_interactions", "M2_resource_by_height"),
}
RIDGE = 0.12
MIN_BATS = 4


def _solve(matrix, vector):
    """Partial-pivot Gaussian elimination for small ridge Hessians."""
    n = len(vector)
    a = [list(matrix[i]) + [vector[i]] for i in range(n)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        if abs(a[pivot][j]) < 1e-12:
            raise ValueError("STOP_SINGULAR_3D_SSF_HESSIAN")
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        for c in range(j, n + 1):
            a[j][c] /= scale
        for i in range(j + 1, n):
            factor = a[i][j]
            for c in range(j, n + 1):
                a[i][c] -= factor * a[j][c]
    out = [0.0] * n
    for i in range(n - 1, -1, -1):
        out[i] = a[i][n] - math.fsum(a[i][j] * out[j] for j in range(i + 1, n))
    return out


def _finite(v, nonnegative=False):
    return (type(v) in (int, float) and math.isfinite(float(v))
            and (not nonnegative or float(v) >= 0.0))


def validate_risksets(risksets, require_dated_flower=False, include_state=False):
    if not isinstance(risksets, (list, tuple)) or len(risksets) < MIN_BATS * 3:
        raise ValueError("STOP_UNAVAILABLE_OR_TOO_FEW_SOURCE_RISKSETS")
    keys = set()
    bats = set()
    resource_kinds = set()
    for event in risksets:
        if not isinstance(event, dict):
            raise ValueError("STOP_ORIGINAL_EVENT_NOT_DICTIONARY")
        for field in ("bat", "site", "night", "step"):
            if not isinstance(event.get(field), str) or not event[field]:
                raise ValueError("STOP_UNVERIFIED_BAT_SITE_NIGHT_STEP_KEY")
        key = tuple(event[k] for k in ("bat", "site", "night", "step"))
        if key in keys:
            raise ValueError("STOP_DUPLICATE_STEP_RISKSET")
        keys.add(key)
        bats.add(event["bat"])
        for gate in ("original_fix", "height_agl_verified", "regular_interval_verified",
                     "riskset_outcome_independent", "candidate_sampling_frozen",
                     "resource_independent_of_tracking"):
            if event.get(gate) is not True:
                raise ValueError("STOP_SOURCE_PROVENANCE_" + gate)
        kind = event.get("resource_kind")
        if kind not in ("cactus_location_proxy", "dated_measured_flower"):
            raise ValueError("STOP_RESOURCE_KIND_NOT_INDEPENDENTLY_DEFINED")
        resource_kinds.add(kind)
        if kind == "dated_measured_flower" or require_dated_flower:
            if (kind != "dated_measured_flower" or
                event.get("resource_same_night_observed") is not True or
                event.get("resource_no_simulated_imputation") is not True or
                event.get("resource_survey_effort_verified") is not True):
                raise ValueError("STOP_NO_DATED_DIRECT_FLOWER_SURVEY_JOIN")
        state = event.get("state_context")
        if include_state and (state not in (0, 1) or type(state) is not int or
                              event.get("state_annotation_height_blind") is not True):
            raise ValueError("STOP_STATE_DERIVED_FROM_HEIGHT_OR_NOT_VERIFIED")
        choices = event.get("choices")
        idx = event.get("observed_choice")
        if (not isinstance(choices, list) or len(choices) < 4 or
            type(idx) is not int or not 0 <= idx < len(choices)):
            raise ValueError("STOP_INVALID_SHARED_3D_CHOICE_SET")
        by_xy = defaultdict(set)
        seen = set()
        resource_at_xy = {}
        for c in choices:
            if not isinstance(c, dict):
                raise ValueError("STOP_CANDIDATE_NOT_DICTIONARY")
            xy, z = c.get("xy_cell"), c.get("z_level")
            if not isinstance(xy, str) or not xy or not isinstance(z, str) or not z:
                raise ValueError("STOP_CANDIDATE_XYZ_SUPPORT_MISSING")
            if (xy, z) in seen:
                raise ValueError("STOP_DUPLICATE_XY_HEIGHT_CANDIDATE")
            seen.add((xy, z))
            by_xy[xy].add(z)
            for field in ("step_m", "cos_turn", "omega_delta",
                          "forest_structure", "agl_m"):
                if not _finite(c.get(field), nonnegative=field in ("step_m", "agl_m")):
                    raise ValueError("STOP_MISSING_CANDIDATE_3D_MOVEMENT_HABITAT")
            if c["step_m"] <= 0:
                raise ValueError("STOP_ZERO_LENGTH_OR_GPS_TIME_STEP")
            if not _finite(c.get("resource_count"), nonnegative=True):
                raise ValueError("STOP_MISSING_OR_NEGATIVE_MEASURED_RESOURCE")
            if xy not in resource_at_xy:
                resource_at_xy[xy] = c["resource_count"]
            elif abs(float(c["resource_count"]) - float(resource_at_xy[xy])) > 1e-10:
                raise ValueError("STOP_XY_RESOURCE_CHANGES_WITH_CANDIDATE_HEIGHT")
            if c.get("is_control_built_from_test_endpoint") is not False:
                raise ValueError("STOP_RESPONSE_LEAKING_CONTROL_SAMPLER")
        if (len(by_xy) < 2 or len(next(iter(by_xy.values()))) < 2 or
            len(set(map(frozenset, by_xy.values()))) != 1):
            raise ValueError("STOP_UNBALANCED_XY_BY_Z_CANDIDATES")
    if len(bats) < MIN_BATS:
        raise ValueError("STOP_TOO_FEW_INDEPENDENT_ANIMALS")
    if len(resource_kinds) != 1:
        raise ValueError("STOP_MIXED_PROXIES_AND_MEASURED_FLOWER_COUNTS")
    return tuple(risksets)


def _feature(c, state):
    state = 1 if state == 1 else 0
    length = float(c["step_m"])
    height = float(c["agl_m"]) / 50.0
    resource = math.log1p(float(c["resource_count"]))
    return {
        "step_m": length / 50.0,
        "log_step_m": math.log(length),
        "cos_turn": float(c["cos_turn"]),
        "omega_delta": float(c["omega_delta"]),
        "forest_structure": float(c["forest_structure"]),
        "agl_50m": height,
        "resource": resource,
        "resource_agl": resource * height,
        "resource_state": resource * state,
        "resource_agl_state": resource * height * state,
    }


def _weights(events):
    bats = {e["bat"] for e in events}
    nights = defaultdict(set)
    nsteps = defaultdict(int)
    for e in events:
        nk = (e["bat"], e["site"], e["night"])
        nights[e["bat"]].add(nk)
        nsteps[nk] += 1
    return [1.0 / (len(bats) * len(nights[e["bat"]]) *
                   nsteps[(e["bat"], e["site"], e["night"])]) for e in events]


def _train_scale(events, fields):
    # Availability covariates only, never observed choice indexes.
    vectors = [[_feature(c, e.get("state_context", 0))[f] for f in fields]
               for e in events for c in e["choices"]]
    n = len(vectors)
    center = [math.fsum(row[j] for row in vectors) / n for j in range(len(fields))]
    sds = [math.sqrt(math.fsum((r[j] - center[j]) ** 2 for r in vectors) / n)
           for j in range(len(fields))]
    return center, [s if s > 1e-8 else 1.0 for s in sds]


def _matrix(event, fields, center, scale):
    return [[(_feature(c, event.get("state_context", 0))[f] - center[j]) / scale[j]
             for j, f in enumerate(fields)] for c in event["choices"]]


def _softmax(scores):
    m = max(scores)
    unnormalized = [math.exp(s - m) for s in scores]
    denom = math.fsum(unnormalized)
    return [s / denom for s in unnormalized], m + math.log(denom)


def _obj_grad_hess(data, fields, center, scale, beta, weights, with_hessian=True):
    p = len(fields)
    loss = RIDGE * math.fsum(b * b for b in beta) / 2.0
    gradient = [RIDGE * b for b in beta]
    hessian = [[RIDGE if j == k else 0.0 for k in range(p)]
               for j in range(p)] if with_hessian else None
    for event, w in zip(data, weights):
        rows = _matrix(event, fields, center, scale)
        scores = [math.fsum(x[j] * beta[j] for j in range(p)) for x in rows]
        prob, lse = _softmax(scores)
        chosen = event["observed_choice"]
        loss += w * (lse - scores[chosen])
        avg = [math.fsum(prob[k] * rows[k][j] for k in range(len(rows)))
               for j in range(p)]
        for j in range(p):
            gradient[j] += w * (avg[j] - rows[chosen][j])
        if hessian is not None:
            for j in range(p):
                for k in range(j, p):
                    cov = math.fsum(prob[z] *
                                    (rows[z][j] - avg[j]) * (rows[z][k] - avg[k])
                                    for z in range(len(rows)))
                    hessian[j][k] += w * cov
                    if k != j:
                        hessian[k][j] += w * cov
    return loss, gradient, hessian


def fit(events, fields, max_iter=18):
    events = tuple(events)
    if len(events) < 10:
        raise ValueError("STOP_FEWER_THAN_TEN_TRAINING_STEPS")
    center, scale = _train_scale(events, fields)
    weights = _weights(events)
    beta = [0.0] * len(fields)
    for _ in range(max_iter):
        loss, grad, hess = _obj_grad_hess(events, fields, center, scale, beta, weights)
        if max(abs(v) for v in grad) < 1e-8:
            break
        direction = _solve(hess, grad)
        step = 1.0
        accepted = False
        while step > 1e-7:
            trial = [b - step * d for b, d in zip(beta, direction)]
            new_loss, _, _ = _obj_grad_hess(
                events, fields, center, scale, trial, weights, False)
            if new_loss <= loss + 1e-12:
                beta = trial
                accepted = True
                break
            step *= 0.5
        if not accepted:
            raise ValueError("STOP_CONDITIONAL_LOGISTIC_OPTIMIZATION_FAILED")
    else:
        _, g, _ = _obj_grad_hess(events, fields, center, scale, beta, weights, False)
        if max(abs(v) for v in g) > 1e-5:
            raise ValueError("STOP_CONDITIONAL_LOGISTIC_NOT_CONVERGED")
    return {"fields": fields, "center": center, "scale": scale, "beta": beta}


def score_event(model, event):
    rows = _matrix(event, model["fields"], model["center"], model["scale"])
    beta = model["beta"]
    probs, _ = _softmax([
        math.fsum(r[j] * beta[j] for j in range(len(beta))) for r in rows])
    idx = event["observed_choice"]
    xy = event["choices"][idx]["xy_cell"]
    pjoint = probs[idx]
    pxy = math.fsum(p for p, c in zip(probs, event["choices"]) if c["xy_cell"] == xy)
    return {"joint": math.log(pjoint),
            "horizontal": math.log(pxy),
            "height_given_horizontal": math.log(pjoint / pxy),
            "mass_sum": math.fsum(probs)}


def _fold_value(event, heldout):
    if heldout == "bat":
        return event["bat"]
    if heldout == "bat_night":
        return (event["bat"], event["site"], event["night"])
    if heldout == "site":
        return event["site"]
    raise ValueError("STOP_INVALID_HELDOUT_UNIT")


def _aggregate(events, model):
    by_night = defaultdict(list)
    for e in events:
        nk = (e["bat"], e["site"], e["night"])
        by_night[nk].append(score_event(model, e))
    by_bat = defaultdict(list)
    components = ("joint", "horizontal", "height_given_horizontal")
    for nk, items in by_night.items():
        by_bat[nk[0]].append({
            k: math.fsum(z[k] for z in items) / len(items) for k in components})
    return ({k: math.fsum(
                math.fsum(n[k] for n in nights) / len(nights)
                for nights in by_bat.values()) / len(by_bat)
             for k in components}, len(by_bat), len(by_night))


def evaluate(risksets, heldout="bat", require_dated_flower=False, include_state=False):
    events = validate_risksets(risksets, require_dated_flower, include_state)
    models = {key: value for key, value in LEVELS.items()
              if include_state or key != "M3_state_interactions"}
    folds = sorted({_fold_value(e, heldout) for e in events}, key=str)
    if len(folds) < 2:
        raise ValueError("STOP_FEWER_THAN_TWO_HELDOUT_BLOCKS")
    rows = []
    for i, group in enumerate(folds, 1):
        train = [e for e in events if _fold_value(e, heldout) != group]
        test = [e for e in events if _fold_value(e, heldout) == group]
        if len({e["bat"] for e in train}) < 3:
            raise ValueError("STOP_FEWER_THAN_THREE_TRAINING_BATS")
        scores = {}
        n_bats = n_nights = None
        for name, fields in models.items():
            model = fit(train, fields)
            result, n_bats, n_nights = _aggregate(test, model)
            scores[name] = result
        deltas = {}
        for label, (better, base) in CONTRASTS.items():
            if better not in models:
                continue
            deltas[label] = {k: scores[better][k] - scores[base][k]
                             for k in ("joint", "horizontal", "height_given_horizontal")}
        rows.append({"heldout_group_ordinal": i, "n_bats": n_bats,
                     "n_bat_nights": n_nights, "n_steps": len(test),
                     "nested_gain_nats_per_step": deltas})
    summary = {
        k: {component: math.fsum(
                f["nested_gain_nats_per_step"][k][component]
                for f in rows) / len(rows)
            for component in ("joint", "horizontal", "height_given_horizontal")}
        for k in rows[0]["nested_gain_nats_per_step"]
    }
    for delta in summary.values():
        if abs(delta["joint"] - delta["horizontal"] -
               delta["height_given_horizontal"]) > 1e-9:
            raise AssertionError("BROKEN_HORIZONTAL_VERTICAL_CHAIN_RULE")
    return {
        "schema": "batter.paired_3d_ssf_resource_benchmark.v1",
        "status": "DISCRETE_MATCHED_RISKSET_HELDOUT_PREDICTION_NOT_CONTINUOUS_SSF",
        "model_family": "conditional multinomial step-choice softmax with ridge; not ssf3D reproduction",
        "resource_kind": events[0]["resource_kind"],
        "heldout_unit": heldout, "n_folds": len(rows),
        "n_unique_bats": len({e["bat"] for e in events}),
        "n_unique_step_risksets": len(events),
        "animal_night_balanced": True, "matched_control_3d_risksets": True,
        "original_source_authenticity_verified_by_this_engine": False,
        "source_original_observation_flag_present": True,
        "is_regional_species_occupancy_sdm": False,
        "empirical_resource_height_bat_gain_claim_allowed": False,
        "user_source_is_currently_method_verified_only": True,
        "state_is_independent": include_state,
        "gains_equal_holdout_group_mean": summary,
        "fold_aggregates_without_ids": rows,
        "no_individual_fix_level_pvalues": True,
        "vertical_height_marginalization_exact_on_discrete_XYxZ_riskset": True,
        "scientific_boundary": "3D-SSF alternative endpoint proposals and continuous normalizer not implemented; sampling correction and 3D telemetry/detection validation needed before causal interpretation",
    }
