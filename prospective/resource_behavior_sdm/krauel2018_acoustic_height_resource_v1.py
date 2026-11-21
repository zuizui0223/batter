"""Night-heldout prediction of recorded stratum and acoustic buzz marks.

The source is a published aggregate acoustic table, not individual telemetry.
No source observations, coordinates or animal identifiers are embedded here.
The fixed design is KRAUEL2018_FIELD_ACOUSTIC_HEIGHT_RESOURCE_FROZEN_20261121.md.
"""
import argparse
import datetime as dt
import hashlib
import json
import math

INTERCEPT_RIDGE = 0.01
SLOPE_RIDGE = 0.15
SOURCE_URL = "https://krauel.com/publications/Krauel%20et%20al%202018%20CJZ%20early.pdf"
TRANSCRIPTION_SHA256 = "cc85b52cbb8d43fb9d580ae5c859c900d7d806b2d38386452ec53d186971d69e"
FREEZE_COMMIT = "677efa131705736f860e15ad479f19532ffc4f2e"


def _integer(value):
    return type(value) is int and value >= 0


def validate_rows(rows):
    """Return complete nights and aggregate QC, retaining missing versus zero."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("STOP_EMPTY_TABLE")
    seen, complete = set(), []
    audit = {"n_source_nights": len(rows), "n_observed_cells": 0,
             "missing_cells": 0, "source_total_passes": 0,
             "source_buzz_positive_passes": 0, "complete_total_passes": 0,
             "complete_buzz_positive_passes": 0}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("STOP_INVALID_ROW")
        date = row.get("date")
        try:
            parsed = dt.date.fromisoformat(date)
        except (ValueError, TypeError):
            raise ValueError("STOP_INVALID_DATE") from None
        if parsed.isoformat() != date or date in seen:
            raise ValueError("STOP_DUPLICATE_OR_NONCANONICAL_DATE")
        seen.add(date)
        if not _integer(row.get("trap_moths")):
            raise ValueError("STOP_INVALID_MEASURED_TRAP_COUNT")
        passes, buzz = row.get("passes"), row.get("buzz")
        if not (isinstance(passes, list) and isinstance(buzz, list)
                and len(passes) == len(buzz) == 3):
            raise ValueError("STOP_EXPECT_THREE_STRATA")
        missing = False
        for n, b in zip(passes, buzz):
            if (n is None) != (b is None):
                raise ValueError("STOP_MISMATCHED_INSTRUMENT_MISSINGNESS")
            if n is None:
                missing = True
                audit["missing_cells"] += 1
                continue
            if not _integer(n) or not _integer(b) or b > n:
                raise ValueError("STOP_INVALID_PASS_OR_BUZZ_COUNT")
            audit["n_observed_cells"] += 1
            audit["source_total_passes"] += n
            audit["source_buzz_positive_passes"] += b
        if not missing:
            if sum(passes) == 0:
                raise ValueError("STOP_NO_DETECTED_PASS_DENOMINATOR")
            complete.append(row)
            audit["complete_total_passes"] += sum(passes)
            audit["complete_buzz_positive_passes"] += sum(buzz)
    complete.sort(key=lambda row: row["date"])
    audit["n_complete_nights"] = len(complete)
    audit["excluded_incomplete_nights"] = len(rows) - len(complete)
    return complete, audit


def _raw_features(row, resource):
    values = [float(dt.date.fromisoformat(row["date"]).toordinal())]
    if resource:
        values.append(math.log1p(row["trap_moths"]))
    if not all(math.isfinite(v) for v in values):
        raise ValueError("STOP_NONFINITE_COVARIATE")
    return values


def _standardized(row, model):
    raw = _raw_features(row, model["resource"])
    return [(v - m) / s for v, m, s in zip(raw, model["mean"], model["scale"])]


def _log_softmax(logits):
    maximum = max(logits)
    centered = [v - maximum for v in logits]
    log_sum = math.log(math.fsum(math.exp(v) for v in centered))
    return [v - log_sum for v in centered]


def _softplus(value):
    return max(value, 0.0) + math.log1p(math.exp(-abs(value)))


def _sigmoid(value):
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def _solve(matrix, vector):
    size = len(vector)
    a = [list(row) + [v] for row, v in zip(matrix, vector)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-14:
            raise ValueError("STOP_SINGULAR_HESSIAN")
        a[col], a[pivot] = a[pivot], a[col]
        denominator = a[col][col]
        for j in range(col, size + 1):
            a[col][j] /= denominator
        for i in range(col + 1, size):
            multiplier = a[i][col]
            for j in range(col, size + 1):
                a[i][j] -= multiplier * a[col][j]
    out = [0.0] * size
    for i in range(size - 1, -1, -1):
        out[i] = a[i][size] - math.fsum(a[i][j] * out[j] for j in range(i + 1, size))
    return out


def _objective(beta, observations, factor, feature_count, penalties):
    size, n_nights = len(beta), len(observations)
    loss = 0.0
    gradient = [0.0] * size
    hessian = [[0.0] * size for _ in range(size)]
    for features, counts, positive in observations:
        total = sum(counts)
        if factor == "height":
            x = [1.0] + features
            logits = [math.fsum(beta[c * feature_count + j] * x[j]
                                for j in range(feature_count)) for c in range(3)]
            logp = _log_softmax(logits)
            probabilities = [math.exp(v) for v in logp]
            target = [v / total for v in counts]
            loss -= math.fsum(q * lp for q, lp in zip(target, logp)) / n_nights
            for c in range(3):
                for j in range(feature_count):
                    u = c * feature_count + j
                    gradient[u] += (probabilities[c] - target[c]) * x[j] / n_nights
                    for d in range(3):
                        covariance = probabilities[c] * ((1.0 if c == d else 0.0) - probabilities[d])
                        for t in range(feature_count):
                            v = d * feature_count + t
                            hessian[u][v] += covariance * x[j] * x[t] / n_nights
        else:
            for height in range(3):
                x = [float(height == j) for j in range(3)] + features
                logit = math.fsum(v * b for v, b in zip(x, beta))
                probability = _sigmoid(logit)
                weight = counts[height] / total
                positives = positive[height] / total
                loss += (positives * _softplus(-logit)
                         + (weight - positives) * _softplus(logit)) / n_nights
                for j in range(size):
                    gradient[j] += (weight * probability - positives) * x[j] / n_nights
                    for t in range(size):
                        hessian[j][t] += weight * probability * (1 - probability) * x[j] * x[t] / n_nights
    for j, penalty in enumerate(penalties):
        loss += penalty * beta[j] ** 2 / 2
        gradient[j] += penalty * beta[j]
        hessian[j][j] += penalty
    if not math.isfinite(loss) or not all(math.isfinite(v) for v in gradient):
        raise ValueError("STOP_NONFINITE_OPTIMIZATION")
    return loss, gradient, hessian


def fit_factor(training_rows, factor, resource=False):
    """Fit using training nights only; all observed counts get night normalization."""
    rows, audit = validate_rows(training_rows)
    if factor not in ("height", "buzz") or type(resource) is not bool:
        raise ValueError("STOP_UNKNOWN_MODEL")
    if len(rows) < 4 or audit["excluded_incomplete_nights"]:
        raise ValueError("STOP_INCOMPLETE_OR_INSUFFICIENT_TRAINING_NIGHTS")
    raw = [_raw_features(row, resource) for row in rows]
    width = len(raw[0])
    mean = [math.fsum(row[j] for row in raw) / len(rows) for j in range(width)]
    scale = [math.sqrt(math.fsum((row[j] - mean[j]) ** 2 for row in raw) / len(rows))
             for j in range(width)]
    scale = [s if s > 1e-12 else 1.0 for s in scale]
    model = {"factor": factor, "resource": resource, "mean": mean, "scale": scale}
    observations = [(_standardized(row, model), row["passes"], row["buzz"]) for row in rows]
    feature_count = 1 + width
    if factor == "height":
        penalties = [INTERCEPT_RIDGE if j % feature_count == 0 else SLOPE_RIDGE
                     for j in range(3 * feature_count)]
    else:
        penalties = [INTERCEPT_RIDGE] * 3 + [SLOPE_RIDGE] * width
    beta = [0.0] * len(penalties)
    for iteration in range(100):
        loss, gradient, hessian = _objective(beta, observations, factor, feature_count, penalties)
        norm = max(abs(g) for g in gradient)
        if norm < 1e-10:
            model.update(beta=beta, gradient_max_abs=norm, n_iterations=iteration,
                         training_nights=len(rows))
            return model
        step = _solve(hessian, gradient)
        directional = math.fsum(g * s for g, s in zip(gradient, step))
        step_size = 1.0
        while step_size >= 2 ** -30:
            candidate = [v - step_size * s for v, s in zip(beta, step)]
            candidate_loss = _objective(candidate, observations, factor, feature_count, penalties)[0]
            if candidate_loss <= loss - 1e-4 * step_size * directional + 1e-15:
                beta = candidate
                break
            step_size /= 2
        else:
            raise ValueError("STOP_NEWTON_LINE_SEARCH")
    raise ValueError("STOP_NEWTON_NONCONVERGENCE")


def predict_factor(model, row):
    """Return stable log probabilities without reading any heldout response."""
    features = _standardized(row, model)
    beta = model["beta"]
    if model["factor"] == "height":
        x = [1.0] + features
        width = len(x)
        return _log_softmax([math.fsum(beta[c * width + j] * x[j] for j in range(width))
                             for c in range(3)])
    if model["factor"] == "buzz":
        shared = math.fsum(beta[j + 3] * value for j, value in enumerate(features))
        return [[-_softplus(beta[h] + shared), -_softplus(-beta[h] - shared)] for h in range(3)]
    raise ValueError("STOP_UNKNOWN_PREDICTION_FACTOR")


def _validate_log_distribution(logp, size):
    if not isinstance(logp, (list, tuple)) or len(logp) != size:
        raise ValueError("STOP_INVALID_PROBABILITY_SHAPE")
    if not all(type(v) in (int, float) and math.isfinite(v) and v <= 0 for v in logp):
        raise ValueError("STOP_INVALID_LOG_PROBABILITY")
    maximum = max(logp)
    log_total = maximum + math.log(math.fsum(math.exp(v - maximum) for v in logp))
    if abs(log_total) > 1e-10:
        raise ValueError("STOP_UNNORMALIZED_LOG_PROBABILITIES")


def score_night(row, height_logp, buzz_logp):
    """Proper empirical log score; refuse incomplete or unnormalized inputs."""
    if not isinstance(row, dict):
        raise ValueError("STOP_INVALID_SCORE_ROW")
    counts, positive = row.get("passes"), row.get("buzz")
    if not (isinstance(counts, (list, tuple)) and isinstance(positive, (list, tuple))
            and len(counts) == len(positive) == 3):
        raise ValueError("STOP_INVALID_SCORE_COUNT_SHAPE")
    if not all(_integer(n) and _integer(b) and b <= n for n, b in zip(counts, positive)):
        raise ValueError("STOP_INVALID_SCORE_COUNTS")
    if sum(counts) <= 0:
        raise ValueError("STOP_INVALID_SCORE_DENOMINATOR")
    _validate_log_distribution(height_logp, 3)
    if not isinstance(buzz_logp, (list, tuple)) or len(buzz_logp) != 3:
        raise ValueError("STOP_INVALID_BUZZ_PROBABILITY_SHAPE")
    for logp in buzz_logp:
        _validate_log_distribution(logp, 2)
    total = sum(counts)
    height = math.fsum(n * lp for n, lp in zip(counts, height_logp)) / total
    buzz = math.fsum(b * lp[1] + (n - b) * lp[0]
                     for n, b, lp in zip(counts, positive, buzz_logp)) / total
    if not math.isfinite(height + buzz):
        raise ValueError("STOP_INVALID_PROBABILITY_SUPPORT")
    return {"height": height, "buzz_given_height": buzz, "joint": height + buzz}


def cross_validate(source_rows, split="leave_night_out"):
    rows, _ = validate_rows(source_rows)
    if len(rows) < 6:
        raise ValueError("STOP_TOO_FEW_COMPLETE_NIGHTS")
    if split == "leave_night_out":
        groups = [[i] for i in range(len(rows))]
    elif split == "adjacent_pair_out" and len(rows) % 2 == 0:
        groups = [list(range(i, i + 2)) for i in range(0, len(rows), 2)]
    else:
        raise ValueError("STOP_UNKNOWN_OR_INCOMPLETE_SPLIT")
    components = ("height", "buzz_given_height", "joint")
    folds = []
    maximum_gradient = 0.0
    for heldout in groups:
        training = [row for i, row in enumerate(rows) if i not in heldout]
        models = {(factor, resource): fit_factor(training, factor, resource)
                  for factor in ("height", "buzz") for resource in (False, True)}
        maximum_gradient = max(maximum_gradient, *(m["gradient_max_abs"] for m in models.values()))
        night_scores = []
        for i in heldout:
            row = rows[i]
            h0, h1 = [predict_factor(models[("height", r)], row) for r in (False, True)]
            b0, b1 = [predict_factor(models[("buzz", r)], row) for r in (False, True)]
            baseline = score_night(row, h0, b0)
            resource = score_night(row, h1, b1)
            night_scores.append({"baseline": baseline, "resource": resource})
        baseline = {name: math.fsum(s["baseline"][name] for s in night_scores) / len(heldout)
                    for name in components}
        resource = {name: math.fsum(s["resource"][name] for s in night_scores) / len(heldout)
                    for name in components}
        gains = {name: resource[name] - baseline[name] for name in components}
        if abs(gains["joint"] - gains["height"] - gains["buzz_given_height"]) > 1e-12:
            raise ValueError("STOP_NONADDITIVE_PAIRED_SCORE")
        folds.append({"fold_ordinal": len(folds) + 1, "n_test_nights": len(heldout),
                      "n_training_nights": len(training), "baseline_scores": baseline,
                      "resource_scores": resource, "gains": gains,
                      "joint_model_scores": {
                          "baseline": baseline["joint"],
                          "resource_height_only": resource["height"] + baseline["buzz_given_height"],
                          "resource_buzz_only": baseline["height"] + resource["buzz_given_height"],
                          "resource_both": resource["joint"]}})
    return {"split": split, "n_nights": len(rows), "n_folds": len(folds),
            "score_unit": "nats_per_recorded_pass_averaged_equally_over_nights",
            "mean_gains": {name: math.fsum(f["gains"][name] * f["n_test_nights"] for f in folds) / len(rows)
                           for name in components},
            "positive_folds": {name: sum(f["gains"][name] > 0 for f in folds) for name in components},
            "maximum_training_gradient": maximum_gradient,
            "folds": folds}


def source_receipt(payload):
    """Authenticate the specific crosschecked transcription, then run frozen CV."""
    if payload.get("schema") != "batter.krauel2018.table1_transcription.v1":
        raise ValueError("STOP_UNKNOWN_TRANSCRIPTION_SCHEMA")
    rows = payload.get("rows")
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    if (digest != TRANSCRIPTION_SHA256 or payload.get("transcription_sha256") != digest
            or payload.get("source_url") != SOURCE_URL
            or payload.get("independent_transcription_agreement") is not True
            or payload.get("original_pdf_sha256") is not None):
        raise ValueError("STOP_UNVERIFIED_TRANSCRIPTION_OR_SOURCE_VERSION")
    _, audit = validate_rows(rows)
    expected = {"n_source_nights": 13, "n_observed_cells": 36, "missing_cells": 3,
                "source_total_passes": 1104, "source_buzz_positive_passes": 97,
                "n_complete_nights": 10, "complete_total_passes": 1073,
                "complete_buzz_positive_passes": 95, "excluded_incomplete_nights": 3}
    if audit != expected:
        raise ValueError("STOP_SOURCE_TABLE_STRUCTURE_MISMATCH")
    return {"schema": "batter.krauel2018.observed_acoustic_resource_height.v1",
            "analysis_date": "2026-11-21",
            "status": "SOURCE_OPEN_EXPLORATORY_PUBLISHED_FIELD_ACOUSTIC_TABLE",
            "source": {"paper_doi": "10.1139/cjz-2017-0284", "url": SOURCE_URL,
                       "version": "author_hosted_accepted_manuscript_table_1_page_29",
                       "access_mode": "web_reader_table_text_with_independent_transcription",
                       "original_pdf_sha256": None, "transcription_sha256": digest,
                       "independent_transcription_agreement": True},
            "design_freeze_commit": FREEZE_COMMIT, "source_audit": audit,
            "model": {"height": "symmetric_softmax_stratum_intercepts_day_and_optional_moths",
                      "buzz": "logistic_stratum_intercepts_shared_day_and_optional_moths",
                      "resource": "log1p_measured_ground_pheromone_trap_count",
                      "intercept_ridge": INTERCEPT_RIDGE, "slope_ridge": SLOPE_RIDGE,
                      "preprocessing": "training_nights_only",
                      "loss_weighting": "equal_night_then_within_night_pass_fraction"},
            "leave_night_out": cross_validate(rows, "leave_night_out"),
            "adjacent_pair_out": cross_validate(rows, "adjacent_pair_out"),
            "scientific_boundaries": {
                "one_acoustic_site": True, "dates_not_proven_independent": True,
                "recorded_stratum_not_individual_flight_altitude": True,
                "ground_trap_count_not_aerial_prey_density": True,
                "absent_buzz_not_verified_nonfeeding": True,
                "recorder_effort_and_detection_not_calibrated": True,
                "weather_not_controlled": True,
                "same_night_resource_not_prospective_forecast": True,
                "p_value": None, "wild_individual_resource_height_gain": None,
                "resource_conditioned_3d_sdm_gain": None,
                "causal_resource_effect": None,
                "raw_source_rows_coordinates_or_individual_ids_included": False,
                "source_exploration_closed_after_fixed_comparisons": True}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.table_json, encoding="utf-8") as handle:
        result = source_receipt(json.load(handle))
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "source_audit": result["source_audit"],
                      "leave_night_out": result["leave_night_out"]["mean_gains"],
                      "adjacent_pair_out": result["adjacent_pair_out"]["mean_gains"]}))


if __name__ == "__main__":
    main()
