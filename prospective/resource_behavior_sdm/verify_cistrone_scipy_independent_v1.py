#!/usr/bin/env python3
"""Independent, optional SciPy check of the frozen Cistrone comparison.

This program does not import the production adapter or model implementation.
It parses the original uploaded ZIP in memory, builds features itself, and fits
the three fixed logistic models with scipy.optimize.minimize(method="BFGS").
Only the caller-specified private JSON receives plot identifiers or fold data.
Standard output contains unkeyed aggregate results and integrity diagnostics.

Third-party imports are lazy: importing this file requires only the standard
library. Running it requires NumPy, SciPy, and openpyxl. No workbook is written.

Example (all paths are supplied by the caller):
    python verify_cistrone_scipy_independent_v1.py \
        --source-zip SOURCE.zip --protocol PROTOCOL.md --output PRIVATE.json

Optional post-fit verification reads a separately produced JSON result only
after all independent fits have completed and been saved. Add:
    --compare-production PRODUCTION_PRIVATE.json --comparison-output RECEIPT.json

The frozen estimand is recorded ground/canopy allocation within positive-pass
plots. It is not individual movement, feeding, abundance, occupancy, or an SDM.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import tempfile
import zipfile


SOURCE_SHA256 = "3eed7ceeb9c1201a3e8594c6d28115d268a7c64e1c1acdccfb6e5d50da872653"
MEMBER_SHA256 = {
    "1-s2.0-S0378112726008807-mmc1.xlsx":
        "7220410f012954b82ae12d33a06d0a6ff70abb66aaa7e17a5aaaf874242f9259",
    "1-s2.0-S0378112726008807-mmc2.xlsx":
        "adcfc18635b5f7d804dad496f3f5108f642a86ba4aaec6d90a932c724148531d",
}
LEPIDOPTERA = (
    "Agrotis ipsilon", "Alcis bastelbergi", "Amata phegea",
    "Arctornis l-nigrum", "Biston betularia", "Lymantria monacha",
    "Crambus pascuella", "Tuta absoluta", "Eilema caniola", "Orgyia antiqua",
    "Catocala ilia", "Pscoparia basistrigalis", "Eudonia lacustrata",
    "Tineola bisselliella",
)
DIPTERA = (
    "Scathophaga stercoraria", "Brevicornu foliatum",
    "Pseudolynchia canariensis", "Cylindromyia rufipes",
)
STAND_FIELDS = (
    "Mean_basal_area_m2_ha", "Mean_DBH_cm", "Mean_tree_height_m",
)
BASELINE_NAMES = (
    "canopy_minus_ground_Clear_canopy_percentage_points",
    "unweighted_two_night_mean_Temp_min",
    *STAND_FIELDS,
)
FEATURE_NAMES = {
    "baseline": BASELINE_NAMES,
    "total": BASELINE_NAMES + ("canopy_minus_ground_log1p_all_insects",),
    "orders": BASELINE_NAMES + (
        "canopy_minus_ground_log1p_Lepidoptera",
        "canopy_minus_ground_log1p_Diptera",
    ),
}


def require(condition: bool, message: str) -> None:
    """Fail explicitly without including a source record in the message."""
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def number(value: object, label: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool),
            f"Missing or nonnumeric {label}")
    result = float(value)
    require(math.isfinite(result), f"Nonfinite {label}")
    return result


def count(value: object, label: str) -> int:
    result = number(value, label)
    require(result >= 0 and result.is_integer(), f"Invalid count in {label}")
    return int(result)


def plot_key(value: object) -> str:
    if isinstance(value, str):
        require(bool(value) and value == value.strip(), "Invalid plot identifier")
        return value
    result = number(value, "Plot")
    require(result.is_integer(), "Noninteger numeric plot identifier")
    return str(int(result))


def read_sheet(data: bytes, *, cached: bool) -> tuple[list[str], list[dict]]:
    import openpyxl

    workbook = openpyxl.load_workbook(io.BytesIO(data), read_only=True,
                                     data_only=cached)
    try:
        require("Data" in workbook.sheetnames, "Missing Data sheet")
        rows = list(workbook["Data"].iter_rows(values_only=True))
    finally:
        workbook.close()
    require(len(rows) >= 2, "Empty Data sheet")
    header = rows[0]
    indices = [i for i, name in enumerate(header) if name is not None]
    names = [header[i] for i in indices]
    require(all(isinstance(name, str) for name in names), "Invalid header")
    require(len(names) == len(set(names)), "Duplicate source header")
    require(all(row[i] is None for row in rows[1:]
                for i, name in enumerate(header) if name is None),
            "Data in an unnamed source column")
    return names, [{header[i]: row[i] for i in indices} for row in rows[1:]]


def parse_and_construct(source: bytes) -> tuple[list[dict], dict]:
    """Read and validate source counts, then construct plot-level raw features."""
    require(sha256(source) == SOURCE_SHA256, "Uploaded ZIP SHA256 mismatch")
    members = {}
    with zipfile.ZipFile(io.BytesIO(source)) as archive:
        for name, expected_hash in MEMBER_SHA256.items():
            require(archive.namelist().count(name) == 1,
                    "Required workbook missing or duplicated")
            members[name] = archive.read(name)
            require(sha256(members[name]) == expected_hash,
                    "Workbook SHA256 mismatch")
    insect_bytes = members["1-s2.0-S0378112726008807-mmc1.xlsx"]
    bat_bytes = members["1-s2.0-S0378112726008807-mmc2.xlsx"]
    insect_headers, insect_rows = read_sheet(insect_bytes, cached=True)
    bat_headers, bat_rows = read_sheet(bat_bytes, cached=True)
    formula_headers, formula_rows = read_sheet(bat_bytes, cached=False)

    require(len(insect_rows) == 41, "Unexpected S1 row count")
    annotation = insect_rows.pop(0)
    require(annotation["Plot"] == "Identified with DNA barcoding"
            and annotation["Stratum"] is None
            and all(value in (None, "*") for name, value in annotation.items()
                    if name != "Plot"), "Unexpected S1 annotation row")
    require(insect_headers[:6] == ["Plot", "Stratum", "Clear_canopy_%",
                                  "Canopy_cover_%", "Height_m", "n_traps"]
            and insect_headers[-1] == "Total_individuals",
            "Unexpected S1 header layout")
    insect_taxa = insect_headers[6:-1]
    require(len(insect_taxa) == 23, "Expected exactly 23 insect taxa")
    require(set(LEPIDOPTERA + DIPTERA) <= set(insect_taxa),
            "Prespecified insect taxon absent")
    require(len(bat_rows) == 80 and len(formula_rows) == 80,
            "Unexpected S2 row count")
    require(formula_headers == bat_headers, "Cached/formula schema mismatch")
    require(bat_headers[:3] == ["Plot", "Stratum", "Night"]
            and bat_headers[20:] == ["Total_bat_passes", "Temp_min", *STAND_FIELDS],
            "Unexpected S2 header layout")
    bat_taxa = bat_headers[3:20]
    require(len(bat_taxa) == 17, "Expected exactly 17 bat acoustic groups")

    insects = {}
    for row in insect_rows:
        key = (plot_key(row["Plot"]), row["Stratum"])
        require(key[1] in ("ground", "canopy"), "Invalid insect stratum")
        require(key not in insects, "Duplicate insect plot-stratum key")
        require(count(row["n_traps"], "n_traps") == 1, "Unexpected trap count")
        catches = {name: count(row[name], "insect taxon") for name in insect_taxa}
        total = sum(catches.values())
        require(total == count(row["Total_individuals"], "Total_individuals"),
                "Insect total does not equal taxon sum")
        insects[key] = {
            "total": total,
            "lepidoptera": sum(catches[name] for name in LEPIDOPTERA),
            "diptera": sum(catches[name] for name in DIPTERA),
            "clear_canopy": number(row["Clear_canopy_%"], "Clear_canopy_%"),
        }

    bats = {}
    for row, formula in zip(bat_rows, formula_rows, strict=True):
        key = (plot_key(row["Plot"]), row["Stratum"], count(row["Night"], "Night"))
        require(key[1] in ("ground", "canopy") and key[2] in (1, 2),
                "Invalid bat stratum or night")
        require(key not in bats, "Duplicate bat plot-stratum-night key")
        total = sum(count(row[name], "bat acoustic group") for name in bat_taxa)
        require(total == count(row["Total_bat_passes"], "Total_bat_passes"),
                "Cached bat total does not equal acoustic-group sum")
        require(isinstance(formula["Total_bat_passes"], str)
                and formula["Total_bat_passes"].startswith("="),
                "Expected a cached formula for every bat total")
        require((plot_key(formula["Plot"]), formula["Stratum"],
                 count(formula["Night"], "formula Night")) == key,
                "Cached/formula row alignment mismatch")
        bats[key] = {"total": total,
                     "temperature": number(row["Temp_min"], "Temp_min"),
                     "stand": tuple(number(row[name], name) for name in STAND_FIELDS)}

    plots = sorted({key[0] for key in insects})
    require(len(plots) == 20 and len(insects) == 40 and len(bats) == 80,
            "Unexpected plot coverage")
    expected_pairs = {(plot, stratum) for plot in plots
                      for stratum in ("ground", "canopy")}
    expected_triples = {(*pair, night) for pair in expected_pairs for night in (1, 2)}
    require(set(insects) == expected_pairs and set(bats) == expected_triples,
            "Incomplete or mismatched whole-plot source join")
    require(sum(row["total"] for row in insects.values()) == 1123,
            "Unexpected total insect count")
    require(sum(row["total"] == 0 for row in insects.values()) == 1,
            "Unexpected zero-catch sample count")
    require(sum(row["total"] for row in bats.values()) == 1301,
            "Unexpected total bat passes")

    constructed = []
    zero_plots = []
    for plot in plots:
        pairs = {stratum: insects[(plot, stratum)] for stratum in ("ground", "canopy")}
        recorder_rows = [bats[(plot, stratum, night)]
                         for stratum in ("ground", "canopy") for night in (1, 2)]
        require(len({row["stand"] for row in recorder_rows}) == 1,
                "Stand variables differ within plot")
        temperatures = []
        for night in (1, 2):
            temperatures_at_night = {bats[(plot, stratum, night)]["temperature"]
                                     for stratum in ("ground", "canopy")}
            require(len(temperatures_at_night) == 1,
                    "Temperature differs between strata within a plot-night")
            temperatures.append(next(iter(temperatures_at_night)))
        pooled = {stratum: sum(bats[(plot, stratum, night)]["total"] for night in (1, 2))
                  for stratum in ("ground", "canopy")}
        total_passes = pooled["ground"] + pooled["canopy"]
        baseline = [pairs["canopy"]["clear_canopy"] - pairs["ground"]["clear_canopy"],
                    math.fsum(temperatures) / 2.0, *recorder_rows[0]["stand"]]

        def contrast(name: str) -> float:
            return math.log1p(pairs["canopy"][name]) - math.log1p(pairs["ground"][name])

        if total_passes == 0:
            zero_plots.append(plot)
            continue
        constructed.append({
            "plot_id": plot,
            "ground_count": pooled["ground"],
            "canopy_count": pooled["canopy"],
            "y_canopy": pooled["canopy"] / total_passes,
            "features": {
                "baseline": baseline,
                "total": baseline + [contrast("total")],
                "orders": baseline + [contrast("lepidoptera"), contrast("diptera")],
            },
        })
    require(len(constructed) == 19 and len(zero_plots) == 1,
            "Unexpected positive/zero-pass plot coverage")
    require(sum(row["ground_count"] + row["canopy_count"] for row in constructed) == 1301,
            "Passes lost when excluding an all-zero plot")
    return constructed, {
        "plot_count": 20, "positive_pass_plot_count": 19,
        "insect_sample_count": 40, "bat_recorder_night_count": 80,
        "insect_taxon_count": 23, "bat_acoustic_group_count": 17,
        "insect_individuals": 1123, "bat_passes": 1301,
        "zero_insect_samples_retained": 1,
        "zero_pass_plots_excluded_from_fitting_and_scoring": zero_plots,
        "cached_bat_total_formulas_checked": 80,
        "source_sha256": SOURCE_SHA256,
        "workbook_sha256": MEMBER_SHA256,
    }


def fit_and_score(raw_train, target_train, raw_test, target_test: float) -> dict:
    import numpy as np
    from scipy.optimize import minimize
    from scipy.special import expit

    require(raw_train.shape[0] == 18, "A source fold must train on 18 plots")
    center = raw_train.mean(axis=0)
    population_sd = raw_train.std(axis=0, ddof=0)
    scale = np.where(population_sd <= 1e-12, 1.0, population_sd)
    transformed_train = (raw_train - center) / scale
    transformed_test = (raw_test - center) / scale
    design = np.column_stack((np.ones(len(raw_train)), transformed_train))
    heldout_design = np.concatenate(([1.0], transformed_test))
    penalty = np.array([0.01] + [0.15] * raw_train.shape[1])

    def objective_and_gradient(coef):
        eta = design @ coef
        objective = np.mean(np.logaddexp(0.0, eta) - target_train * eta)
        objective += 0.5 * np.dot(penalty, coef * coef)
        gradient = design.T @ (expit(eta) - target_train) / len(target_train)
        gradient += penalty * coef
        return float(objective), gradient

    result = minimize(objective_and_gradient, np.zeros(design.shape[1]),
                      method="BFGS", jac=True,
                      options={"gtol": 1e-10, "maxiter": 1000})
    final_objective, final_gradient = objective_and_gradient(result.x)
    max_gradient = float(np.max(np.abs(final_gradient)))
    require(np.all(np.isfinite(result.x)) and math.isfinite(final_objective)
            and max_gradient < 1e-8,
            "Independent BFGS fit failed the absolute gradient gate")
    eta = float(heldout_design @ result.x)
    logp = [-float(np.logaddexp(0.0, eta)), -float(np.logaddexp(0.0, -eta))]
    score = float((1.0 - target_test) * logp[0] + target_test * logp[1])
    require(math.isfinite(score), "Nonfinite held-out score")
    return {
        "logp": logp,
        "probabilities": [math.exp(value) for value in logp],
        "score": score,
        "coefficients": result.x.tolist(),
        "training_mean": center.tolist(),
        "training_population_sd": population_sd.tolist(),
        "training_scale": scale.tolist(),
        "heldout_standardized_features": transformed_test.tolist(),
        "diagnostics": {
            "optimizer": "scipy.optimize.minimize BFGS",
            "scipy_success": bool(result.success),
            "status": int(result.status), "message": str(result.message),
            "iterations": int(result.nit), "function_evaluations": int(result.nfev),
            "gradient_evaluations": int(result.njev),
            "objective": final_objective, "max_abs_gradient": max_gradient,
            "gradient_gate": 1e-8, "gradient_gate_passed": True,
        },
    }


def evaluate(constructed: list[dict]) -> tuple[list[dict], dict]:
    import numpy as np

    targets = np.array([row["y_canopy"] for row in constructed])
    features = {variant: np.array([row["features"][variant] for row in constructed])
                for variant in FEATURE_NAMES}
    folds = []
    for heldout_index, source_plot in enumerate(constructed):
        training_mask = np.arange(len(constructed)) != heldout_index
        fold = {key: source_plot[key] for key in
                ("plot_id", "ground_count", "canopy_count", "y_canopy")}
        fold["training_plot_count"] = int(training_mask.sum())
        fold["variants"] = {
            variant: fit_and_score(raw[training_mask], targets[training_mask],
                                   raw[heldout_index], targets[heldout_index])
            for variant, raw in features.items()
        }
        baseline_score = fold["variants"]["baseline"]["score"]
        fold["gains"] = {
            f"{variant}_minus_baseline": fold["variants"][variant]["score"] - baseline_score
            for variant in ("total", "orders")
        }
        folds.append(fold)
    diagnostics = [fold["variants"][variant]["diagnostics"]
                   for fold in folds for variant in FEATURE_NAMES]
    aggregate = {
        "mean_scores": {
            variant: math.fsum(fold["variants"][variant]["score"] for fold in folds) / len(folds)
            for variant in FEATURE_NAMES
        },
        "comparisons": {},
        "fit_diagnostics": {
            "fit_count": len(diagnostics),
            "gradient_gate_pass_count": sum(d["gradient_gate_passed"] for d in diagnostics),
            "scipy_success_count": sum(d["scipy_success"] for d in diagnostics),
            "scipy_non_success_accepted_by_gradient_count": sum(not d["scipy_success"] for d in diagnostics),
            "max_abs_gradient": max(d["max_abs_gradient"] for d in diagnostics),
            "max_iterations": max(d["iterations"] for d in diagnostics),
        },
    }
    for variant in ("total", "orders"):
        name = f"{variant}_minus_baseline"
        gains = [fold["gains"][name] for fold in folds]
        aggregate["comparisons"][name] = {
            "role": "primary" if variant == "total" else "prespecified_secondary",
            "mean_paired_gain": math.fsum(gains) / len(gains),
            "positive_plot_count": sum(gain > 0 for gain in gains),
            "negative_plot_count": sum(gain < 0 for gain in gains),
            "zero_plot_count": sum(gain == 0 for gain in gains),
            "sorted_gains": sorted(gains), "minimum": min(gains), "maximum": max(gains),
        }
    return folds, aggregate


def private_json_write(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    encoded = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".cistrone-reference-",
                                         suffix=".tmp", delete=False) as output:
            temporary_path = Path(output.name)
            os.chmod(temporary_path, 0o600)
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def compare_production_output(reference: dict, production: dict) -> dict:
    """Compare output values only; never reuse production features or fitting."""
    reference_folds = {plot_key(fold["plot_id"]): fold for fold in reference["folds"]}
    production_folds = {plot_key(fold["heldout_plot_id"]): fold
                        for fold in production["folds"]}
    require(len(reference_folds) == len(reference["folds"]) == 19
            and len(production_folds) == len(production["folds"]) == 19
            and set(reference_folds) == set(production_folds),
            "Independent/production fold identifiers do not match uniquely")
    expected_coverage = {
        "source_plots": 20, "eligible_positive_pass_plots": 19,
        "zero_pass_plots_excluded_from_conditional_score": 1,
        "recorded_passes": 1301,
    }
    require(production["coverage"] == expected_coverage,
            "Independent/production coverage differs")
    errors = {name: [] for name in (
        "log_probability", "probability", "fold_score", "paired_gain",
        "training_feature_mean", "training_feature_scale", "coefficient",
        "aggregate_mean_score", "aggregate_mean_gain", "aggregate_sorted_gain",
        "aggregate_minimum_gain", "aggregate_maximum_gain",
    )}

    def record(name: str, actual, expected) -> None:
        require(len(actual) == len(expected), "Comparison vector lengths differ")
        for first, second in zip(actual, expected, strict=True):
            require(math.isfinite(first) and math.isfinite(second),
                    "Nonfinite comparison value")
            errors[name].append(abs(first - second))

    for key, fold in reference_folds.items():
        other_fold = production_folds[key]
        require(set(other_fold["models"]) == set(FEATURE_NAMES),
                "Production model variants differ")
        for variant, fitted in fold["variants"].items():
            other = other_fold["models"][variant]
            require(other["fit"]["training_plots"] == 18
                    and other["fit"]["variant"] == variant,
                    "Production model fold identity differs")
            record("log_probability", fitted["logp"], other["logp"])
            record("probability", fitted["probabilities"],
                   [math.exp(value) for value in other["logp"]])
            record("fold_score", [fitted["score"]], [other["score"]])
            record("training_feature_mean", fitted["training_mean"], other["fit"]["mean"])
            record("training_feature_scale", fitted["training_scale"], other["fit"]["scale"])
            record("coefficient", fitted["coefficients"], other["fit"]["beta"])
            if variant != "baseline":
                other_gain = other["score"] - other_fold["models"]["baseline"]["score"]
                record("paired_gain", [fold["gains"][variant + "_minus_baseline"]],
                       [other_gain])
    for variant, mean_score in reference["aggregate"]["mean_scores"].items():
        record("aggregate_mean_score", [mean_score],
               [production["summary"][variant]["mean_score"]])
    for variant in ("total", "orders"):
        comparison = reference["aggregate"]["comparisons"][variant + "_minus_baseline"]
        other = production["summary"][variant]
        require(comparison["positive_plot_count"] == other["positive_plots"],
                "Independent/production positive gain counts differ")
        record("aggregate_mean_gain", [comparison["mean_paired_gain"]], [other["mean_gain"]])
        record("aggregate_sorted_gain", comparison["sorted_gains"], other["sorted_plot_gains"])
        record("aggregate_minimum_gain", [comparison["minimum"]], [other["min_gain"]])
        record("aggregate_maximum_gain", [comparison["maximum"]], [other["max_gain"]])
    maxima = {name: {"count": len(values), "max_absolute_difference": max(values)}
              for name, values in errors.items()}
    scored_quantities = (
        "log_probability", "probability", "fold_score", "paired_gain",
        "aggregate_mean_score", "aggregate_mean_gain", "aggregate_sorted_gain",
        "aggregate_minimum_gain", "aggregate_maximum_gain",
    )
    tolerance = 1e-7
    passed = all(maxima[name]["max_absolute_difference"] <= tolerance
                 for name in scored_quantities)
    return {
        "schema": "cistrone_independent_scipy_comparison_v1",
        "passed": passed,
        "matching_plot_identifier_count": 19,
        "matching_model_fit_count": 57,
        "source_coverage_matches": True,
        "positive_plot_counts_match": True,
        "absolute_comparison_tolerance": tolerance,
        "gated_quantities": scored_quantities,
        "differences": maxima,
        "independent_fit_diagnostics": reference["aggregate"]["fit_diagnostics"],
        "independent_runtime_versions": reference["versions"],
        "independent_script_sha256": reference["script_sha256"],
        "protocol_sha256": reference["protocol_sha256"],
        "source_zip_sha256": reference["source_audit"]["source_sha256"],
    }


def main() -> None:
    import numpy as np
    import scipy
    import openpyxl

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True,
                        help="Private keyed output; do not publish or commit this file")
    parser.add_argument("--compare-production", type=Path,
                        help="Optional production result JSON; read only after independent fitting")
    parser.add_argument("--comparison-output", type=Path,
                        help="Receipt path; required when comparing production output")
    args = parser.parse_args()
    require((args.compare_production is None) == (args.comparison_output is None),
            "Both optional comparison arguments must be supplied together")
    protected = {args.source_zip.resolve(), args.protocol.resolve(), Path(__file__).resolve()}
    if args.compare_production is not None:
        protected.add(args.compare_production.resolve())
    outputs = [args.output]
    if args.comparison_output is not None:
        outputs.append(args.comparison_output)
    require(len({path.resolve() for path in outputs}) == len(outputs)
            and not ({path.resolve() for path in outputs} & protected),
            "Output would overwrite an input, another output, or this script")
    source = args.source_zip.read_bytes()
    constructed, audit = parse_and_construct(source)
    folds, aggregate = evaluate(constructed)
    require(sha256(args.source_zip.read_bytes()) == sha256(source),
            "Source ZIP changed during verification")
    versions = {"python": platform.python_version(), "numpy": np.__version__,
                "scipy": scipy.__version__, "openpyxl": openpyxl.__version__}
    script_hash = sha256(Path(__file__).read_bytes())
    result = {
        "schema": "cistrone_independent_scipy_v1",
        "scope": "source-open exploratory, same-study recorded-stratum allocation",
        "score_units": "nats per recorded pass within plot, macro-averaged across positive-pass plots",
        "method": {"validation": "leave-one-whole-positive-pass-plot-out",
                   "feature_names": FEATURE_NAMES,
                   "penalties": {"intercept": 0.01, "each_slope": 0.15},
                   "training_scale_ddof": 0,
                   "scale_floor": 1e-12,
                   "loss": "mean training-plot Bernoulli cross-entropy with fractional canopy targets"},
        "versions": versions, "script_sha256": script_hash,
        "protocol_sha256": sha256(args.protocol.read_bytes()),
        "source_audit": audit, "folds": folds, "aggregate": aggregate,
    }
    private_json_write(args.output, result)
    public_result = {"versions": versions, "script_sha256": script_hash,
                     "output_sha256": sha256(args.output.read_bytes()),
                     "aggregate": aggregate}
    if args.compare_production is not None:
        production_bytes = args.compare_production.read_bytes()
        receipt = compare_production_output(result, json.loads(production_bytes))
        receipt["reference_output_sha256"] = public_result["output_sha256"]
        receipt["production_output_sha256"] = sha256(production_bytes)
        private_json_write(args.comparison_output, receipt)
        public_result["comparison_receipt_sha256"] = sha256(args.comparison_output.read_bytes())
        public_result["comparison"] = receipt
        require(receipt["passed"], "Independent/production results exceed frozen tolerance")
    print(json.dumps(public_result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
