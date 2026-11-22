"""Frozen, exploratory prediction of recorded ground/canopy pass allocation.

One plot is one scoring unit. Two nights are pooled before fitting; raw trap
catch is a plot/stratum proxy without verified temporal or effort alignment.
This module contains no original source rows, plot IDs or coordinates.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

MODELS = ("baseline", "total", "orders")
BASELINE_NAMES = (
    "canopy_minus_ground_openness_percentage_points",
    "mean_two_night_regional_station_minimum_temperature",
    "stand_basal_area_m2_ha", "stand_DBH_cm", "stand_tree_height_m",
)
INTERCEPT_RIDGE = 0.01
SLOPE_RIDGE = 0.15
FREEZE_COMMIT = "0f7b9a6972f81203f95c6eaf7d161c768946eacf"


def _count(value):
    return type(value) is int and value >= 0


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _validate_covariates(row):
    if not isinstance(row, dict):
        raise ValueError("STOP_INVALID_PLOT")
    baseline = row.get("baseline")
    if not (isinstance(baseline, (list, tuple)) and len(baseline) == 5
            and all(_finite(x) for x in baseline)):
        raise ValueError("STOP_INVALID_BASELINE_COVARIATES")
    resources = row.get("resources")
    if not isinstance(resources, dict) or set(resources) != {"total", "lepidoptera", "diptera"}:
        raise ValueError("STOP_INVALID_RESOURCE_FIELDS")
    for counts in resources.values():
        if not (isinstance(counts, (list, tuple)) and len(counts) == 2
                and all(_count(x) for x in counts)):
            raise ValueError("STOP_INVALID_RESOURCE_COUNTS")
    for h in (0, 1):
        if resources["lepidoptera"][h] + resources["diptera"][h] > resources["total"][h]:
            raise ValueError("STOP_RESOURCE_SUBGROUP_EXCEEDS_TOTAL")


def validate_plots(rows):
    """Validate all plots; zero-pass plots contribute coverage, never a zero loss."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("STOP_EMPTY_PLOTS")
    seen, positive, zero, passes = set(), [], 0, 0
    for row in rows:
        _validate_covariates(row)
        key = row.get("plot_id")
        if not isinstance(key, str) or not key.strip() or key in seen:
            raise ValueError("STOP_MISSING_OR_DUPLICATE_PLOT")
        seen.add(key)
        counts = row.get("passes")
        if not (isinstance(counts, (list, tuple)) and len(counts) == 2
                and all(_count(x) for x in counts)):
            raise ValueError("STOP_INVALID_PASS_COUNTS")
        passes += sum(counts)
        if sum(counts) == 0:
            zero += 1
        else:
            positive.append(row)
    positive.sort(key=lambda row: row["plot_id"])
    return positive, {
        "source_plots": len(rows), "eligible_positive_pass_plots": len(positive),
        "zero_pass_plots_excluded_from_conditional_score": zero,
        "recorded_passes": passes,
    }


def raw_features(row, variant):
    _validate_covariates(row)
    if variant not in MODELS:
        raise ValueError("STOP_UNKNOWN_MODEL_VARIANT")
    values = [float(v) for v in row["baseline"]]
    groups = {"baseline": (), "total": ("total",),
              "orders": ("lepidoptera", "diptera")}[variant]
    for group in groups:
        ground, canopy = row["resources"][group]
        values.append(math.log1p(canopy) - math.log1p(ground))
    return values


def _softplus(value):
    return max(value, 0.0) + math.log1p(math.exp(-abs(value)))


def _sigmoid(value):
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    v = math.exp(value)
    return v / (1.0 + v)


def _solve(matrix, vector):
    """Partial-pivot elimination for the strictly ridge-positive Hessian."""
    n = len(vector)
    a = [list(row) + [v] for row, v in zip(matrix, vector)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        if abs(a[pivot][j]) < 1e-14:
            raise ValueError("STOP_SINGULAR_HESSIAN")
        a[j], a[pivot] = a[pivot], a[j]
        div = a[j][j]
        for k in range(j, n + 1):
            a[j][k] /= div
        for i in range(j + 1, n):
            multiplier = a[i][j]
            for k in range(j, n + 1):
                a[i][k] -= multiplier * a[j][k]
    solution = [0.] * n
    for i in range(n - 1, -1, -1):
        solution[i] = a[i][n] - math.fsum(a[i][j] * solution[j] for j in range(i + 1, n))
    return solution


def _objective(beta, observations, penalties):
    n, width = len(observations), len(beta)
    loss, gradient = 0., [0.] * width
    hessian = [[0.] * width for _ in range(width)]
    for x, target in observations:
        eta = math.fsum(b * v for b, v in zip(beta, x))
        prob = _sigmoid(eta)
        loss += (target * _softplus(-eta) + (1. - target) * _softplus(eta)) / n
        for j in range(width):
            gradient[j] += (prob - target) * x[j] / n
            for k in range(width):
                hessian[j][k] += prob * (1. - prob) * x[j] * x[k] / n
    for j, penalty in enumerate(penalties):
        loss += .5 * penalty * beta[j] ** 2
        gradient[j] += penalty * beta[j]
        hessian[j][j] += penalty
    if not math.isfinite(loss) or not all(math.isfinite(g) for g in gradient):
        raise ValueError("STOP_NONFINITE_OPTIMIZATION")
    return loss, gradient, hessian


def fit_model(training_rows, variant):
    rows, audit = validate_plots(training_rows)
    if audit["zero_pass_plots_excluded_from_conditional_score"] or len(rows) < 4:
        raise ValueError("STOP_INSUFFICIENT_OR_ZERO_PASS_TRAINING_PLOTS")
    raw = [raw_features(row, variant) for row in rows]
    n, width = len(raw), len(raw[0])
    mean = [math.fsum(row[j] for row in raw) / n for j in range(width)]
    scale = [math.sqrt(math.fsum((row[j] - mean[j]) ** 2 for row in raw) / n)
             for j in range(width)]
    scale = [s if s > 1e-12 else 1. for s in scale]
    observations = [([1.] + [(v - m) / s for v, m, s in zip(values, mean, scale)],
                     row["passes"][1] / sum(row["passes"])) for values, row in zip(raw, rows)]
    penalties = [INTERCEPT_RIDGE] + [SLOPE_RIDGE] * width
    beta = [0.] * (width + 1)
    for iteration in range(100):
        loss, gradient, hessian = _objective(beta, observations, penalties)
        norm = max(abs(g) for g in gradient)
        if norm < 1e-10:
            return {"variant": variant, "mean": mean, "scale": scale, "beta": beta,
                    "training_plots": n, "gradient_max_abs": norm, "iterations": iteration}
        step = _solve(hessian, gradient)
        directional = math.fsum(g * s for g, s in zip(gradient, step))
        alpha = 1.
        while alpha >= 2 ** -30:
            candidate = [b - alpha * s for b, s in zip(beta, step)]
            if _objective(candidate, observations, penalties)[0] <= loss - 1e-4 * alpha * directional + 1e-15:
                beta = candidate
                break
            alpha /= 2
        else:
            raise ValueError("STOP_LINE_SEARCH_FAILURE")
    raise ValueError("STOP_NEWTON_NONCONVERGENCE")


def predict_log_probabilities(model, row):
    """Predict [ground, canopy] log probabilities without reading responses."""
    raw = raw_features(row, model["variant"])
    mean, scale, beta = model["mean"], model["scale"], model["beta"]
    if not (len(raw) == len(mean) == len(scale) == len(beta) - 1):
        raise ValueError("STOP_INVALID_MODEL_SHAPE")
    if not all(_finite(v) for v in mean + scale + beta) or not all(v > 0 for v in scale):
        raise ValueError("STOP_INVALID_MODEL_PARAMETERS")
    x = [1.] + [(v - m) / s for v, m, s in zip(raw, mean, scale)]
    eta = math.fsum(b * v for b, v in zip(beta, x))
    if not math.isfinite(eta):
        raise ValueError("STOP_NONFINITE_PREDICTION")
    return [-_softplus(eta), -_softplus(-eta)]


def score_plot(counts, logp):
    if not (isinstance(counts, (list, tuple)) and len(counts) == 2
            and all(_count(v) for v in counts) and sum(counts) > 0):
        raise ValueError("STOP_INVALID_SCORE_COUNTS")
    if not (isinstance(logp, (list, tuple)) and len(logp) == 2
            and all(_finite(v) and v <= 0 for v in logp)):
        raise ValueError("STOP_INVALID_LOG_PROBABILITIES")
    m = max(logp)
    log_total = m + math.log(math.fsum(math.exp(v - m) for v in logp))
    if abs(log_total) > 1e-10:
        raise ValueError("STOP_UNNORMALIZED_LOG_PROBABILITIES")
    return math.fsum(n / sum(counts) * p for n, p in zip(counts, logp))


def cross_validate(plots):
    rows, coverage = validate_plots(plots)
    if len(rows) < 5:
        raise ValueError("STOP_TOO_FEW_HELDOUT_PLOTS")
    folds = []
    for index, heldout in enumerate(rows):
        training = rows[:index] + rows[index + 1:]
        models = {}
        for name in MODELS:
            fitted = fit_model(training, name)
            logp = predict_log_probabilities(fitted, heldout)
            models[name] = {"score": score_plot(heldout["passes"], logp),
                            "logp": logp, "fit": fitted}
        folds.append({"heldout_plot_id": heldout["plot_id"], "models": models})
    summary = {}
    for name in MODELS:
        scores = [fold["models"][name]["score"] for fold in folds]
        gains = [fold["models"][name]["score"] - fold["models"]["baseline"]["score"]
                 for fold in folds]
        summary[name] = {"mean_score": math.fsum(scores) / len(scores),
                         "mean_gain": math.fsum(gains) / len(gains),
                         "positive_plots": sum(g > 0 for g in gains),
                         "min_gain": min(gains), "max_gain": max(gains),
                         "sorted_plot_gains": sorted(gains),
                         "max_fit_gradient": max(f["models"][name]["fit"]["gradient_max_abs"]
                                                 for f in folds)}
    return {"coverage": coverage, "summary": summary, "folds": folds}


def public_summary(result):
    """Only aggregate results and sorted, unkeyed score gains leave scratch."""
    return {"split": "leave_entire_plot_out", "n_heldout_plots": len(result["folds"]),
            "coverage": result["coverage"], "models": result["summary"],
            "score_unit": "nats per recorded pass within plot, macro-averaged over positive-pass plots",
            "primary_comparison": "total minus baseline",
            "secondary_comparison": "orders minus baseline",
            "independent_replication_claim": False,
            "original_plot_ids_or_observations_included": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--private-details")
    args = parser.parse_args()
    if len(FREEZE_COMMIT) != 40 or any(c not in "0123456789abcdef" for c in FREEZE_COMMIT):
        raise ValueError("STOP_PROTOCOL_MUST_BE_COMMITTED_BEFORE_SOURCE_FIT")
    from cistrone_supplement_adapter_v1 import load_archive
    source = load_archive(args.archive)
    result = cross_validate(source["plots"])
    receipt = {
        "schema": "batter.cistrone.recorded_stratum.resource_holdout.v1",
        "paper_doi": "10.1016/j.foreco.2026.124382",
        "protocol_freeze_commit": FREEZE_COMMIT,
        "engine_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_audit": source["source_audit"],
        "analysis": public_summary(result),
        "scope": {
            "source_open_exploratory": True,
            "same_study_plot_stratum_join_verified": True,
            "same_night_insect_bat_matching_verified": False,
            "actual_sampling_effort_verified": False,
            "per_plot_recorder_heights_available": False,
            "individuals_or_flight_trajectories_measured": False,
            "feeding_behavior_measured": False,
            "capture_counts_are_effort_standardized": False,
            "spatial_or_temporal_independent_validation": False,
            "species_specific_diet_response_estimated": False,
            "causal_resource_tracking_established": False,
            "regional_ecological_sdm_confirmed": False,
            "strict_individual_resource_height_gain": None,
        },
    }
    Path(args.receipt).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    if args.private_details:
        Path(args.private_details).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(receipt["analysis"], ensure_ascii=False))


if __name__ == "__main__":
    main()
