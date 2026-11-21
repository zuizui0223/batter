"""Source-free bridge: noisy continuous AGL + stratified importance sampled 3D availability.

Observation: horizontal cell XY known, continuous AGL Y ~ Normal(latent Z,sigma).
Latent endpoint never enters data rows; controls sampled independently of XY,Y
from q(z|xy), with predeclared mu(xy), mu(z|xy). This is NOT the
case-control observed-label p/q likelihood and not continuous ssf3D.

For each XY stratum, weighted Monte Carlo approximates
  A_xy(beta) = mu_xy * E_{q(z|xy)}[mu(z|xy)/q(z|xy)*exp(eta(xy,z))]
and the observed density numerator adds Normal(Y|z,sigma).
The denominator is sum_xy A_xy(beta). All M0–M3 share the same q draws.
Estimator is self-normalized and has finite-sample integration error.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math

from gps_height_error_likelihood_v1 import (
    FIELDS, _balanced_test_score, _foldkey, fit_error_aware
)
from paired_3d_ssf_resource_benchmark_v1 import LEVELS, MIN_BATS

STATUS = "KNOWN_TRUTH_SOURCE_FREE_NOISY_AGL_STRATIFIED_Q_ONLY"
SAMPLER = "independent_known_q_stratified_importance_integration"
REQUIRED_EVENT_FLAGS = (
    "original_fix", "regular_interval_verified", "sensor_agl_datum_verified",
    "sensor_sigma_from_independent_calibration",
    "sampled_controls_independent_of_recorded_height_xy",
    "q_known_externally_or_fit_using_training_only",
    "reference_support_frozen_before_response",
    "resource_measured_independently",
)
ALLOWED_RESOURCES = ("cactus_location_proxy", "dated_measured_flower")


def _number(v, positive=False, nonnegative=False):
    if type(v) not in (int, float) or not math.isfinite(float(v)):
        return False
    if positive and v <= 0:
        return False
    if nonnegative and v < 0:
        return False
    return True


def validate_q_noisy_events(data, include_state=False):
    if not isinstance(data, (tuple, list)) or len(data) < MIN_BATS * 3:
        raise ValueError("STOP_UNAVAILABLE_OR_TOO_FEW_NOISY_Q_EVENTS")
    bats = set()
    seen = set()
    diagnostics = []
    for e in data:
        if not isinstance(e, dict):
            raise ValueError("STOP_Q_EVENT_TYPE")
        for field in ("bat", "site", "night", "step", "observed_xy"):
            if not isinstance(e.get(field), str) or not e[field].strip():
                raise ValueError("STOP_Q_MISSING_ANIMAL_NIGHT_XY")
        k = tuple(e[f] for f in ("bat", "site", "night", "step"))
        if k in seen:
            raise ValueError("STOP_Q_DUPLICATE_BAT_NIGHT_STEP")
        seen.add(k)
        bats.add(e["bat"])
        if any(key in e for key in (
            "observed_choice", "true_z", "latent_z_truth",
            "observed_endpoint_in_controls")):
            raise ValueError("STOP_Q_LATENT_HEIGHT_OR_LABEL_LEAKAGE")
        if any(e.get(flag) is not True for flag in REQUIRED_EVENT_FLAGS):
            raise ValueError("STOP_Q_SOURCE_SENSOR_OR_PROPOSAL_PROVENANCE")
        if (not _number(e.get("sensor_sigma_m"), positive=True)
                or not _number(e.get("observed_agl_m"))):
            raise ValueError("STOP_Q_UNCALIBRATED_CONTINUOUS_AGL")
        if e.get("resource_kind") not in ALLOWED_RESOURCES:
            raise ValueError("STOP_Q_RESOURCE_SOURCE_KIND")
        if e["resource_kind"] == "dated_measured_flower" and any(
            e.get(flag) is not True for flag in (
                "resource_same_night_observed",
                "resource_survey_effort_verified",
                "resource_no_simulated_imputation")):
            raise ValueError("STOP_Q_NO_TRUE_DATED_FLOWER_SURVEY")
        if include_state and (
                type(e.get("state_context")) is not int or
                e["state_context"] not in (0, 1) or
                e.get("state_annotation_height_blind") is not True):
            raise ValueError("STOP_Q_HEIGHT_DERIVED_BEHAVIOR_STATE")
        mu_xy = e.get("reference_xy_mass")
        catalog = e.get("z_support_by_xy")
        cs = e.get("choices")
        if (not isinstance(mu_xy, dict) or
                not isinstance(catalog, dict) or
                set(catalog) != set(mu_xy) or len(mu_xy) < 2 or
                e["observed_xy"] not in mu_xy or
                not isinstance(cs, list) or len(cs) < 6):
            raise ValueError("STOP_Q_MISSING_FULL_REFERENCE_SUPPORT")
        if (any(not _number(x, positive=True) for x in mu_xy.values()) or
                abs(math.fsum(mu_xy.values()) - 1.) > 1e-9):
            raise ValueError("STOP_Q_BAD_XY_REFERENCE_NORMALIZATION")
        levels = None
        supported = {}
        for xy, states in catalog.items():
            if not isinstance(xy, str) or not xy or not isinstance(states, list):
                raise ValueError("STOP_Q_SUPPORT_NOT_PREDECLARED")
            if len(states) < 2:
                raise ValueError("STOP_Q_TOO_FEW_ALTITUDE_LEVELS")
            values = {}
            for state in states:
                if not isinstance(state, dict):
                    raise ValueError("STOP_Q_INVALID_SUPPORT_CELL")
                z = state.get("z_level")
                if not isinstance(z, str) or not z or z in values:
                    raise ValueError("STOP_Q_DUPLICATE_OR_MISSING_Z_SUPPORT")
                q, mu = state.get("q_z"), state.get("mu_z")
                if not _number(q, positive=True) or not _number(mu, positive=True):
                    raise ValueError("STOP_Q_NO_POSITIVE_SUPPORT_FOR_Z")
                values[z] = (float(q), float(mu))
            if (abs(math.fsum(v[0] for v in values.values()) - 1.) > 1e-9 or
                abs(math.fsum(v[1] for v in values.values()) - 1.) > 1e-9):
                raise ValueError("STOP_Q_Z_DENSITY_NOT_NORMALIZED")
            if levels is not None and set(values) != levels:
                raise ValueError("STOP_Q_UNMATCHED_Z_UNIVERSE_ACROSS_XY")
            levels = set(values)
            supported[xy] = values
        count = Counter()
        massratio = defaultdict(list)
        resource = {}
        for c in cs:
            if not isinstance(c, dict):
                raise ValueError("STOP_Q_CANDIDATE_NOT_OBJECT")
            xy, z = c.get("xy_cell"), c.get("z_level")
            if xy not in supported or z not in supported[xy]:
                raise ValueError("STOP_Q_CANDIDATE_OUTSIDE_FROZEN_UNIVERSE")
            if c.get("is_control_built_from_test_endpoint") is not False:
                raise ValueError("STOP_Q_RESPONSE_CONDITIONED_CONTROL")
            for col in ("agl_m", "step_m", "cos_turn", "omega_delta",
                        "forest_structure", "resource_count"):
                if not _number(c.get(col)):
                    raise ValueError("STOP_Q_MISSING_OR_NONFINITE_3D_COVARIATE")
            if (c["agl_m"] < 0 or c["step_m"] <= 0 or c["resource_count"] < 0):
                raise ValueError("STOP_Q_INVALID_3D_RESOURCE_HEIGHT_OR_STEP")
            if xy in resource and abs(resource[xy] - c["resource_count"]) > 1e-10:
                raise ValueError("STOP_Q_RESOURCE_CHANGED_BY_HEIGHT")
            resource[xy] = c["resource_count"]
            # Check actual sampled point's q/mu values against the full
            # prespecified support; not merely a user-provided boolean.
            q, mu = supported[xy][z]
            if (not _number(c.get("proposal_z_prob"), positive=True) or
                not _number(c.get("reference_z_prob"), positive=True) or
                abs(c["proposal_z_prob"] - q) > 1e-10 or
                abs(c["reference_z_prob"] - mu) > 1e-10):
                raise ValueError("STOP_Q_CANDIDATE_DENSITY_DISAGREES_WITH_SUPPORT")
            if "log_sampling_weight" in c:
                raise ValueError("STOP_Q_CANDIDATE_SUPPLIED_UNVERIFIED_WEIGHT")
            count[xy] += 1
            massratio[xy].append(mu / q)
        if set(count) != set(mu_xy) or min(count.values()) < 3:
            raise ValueError("STOP_Q_INSUFFICIENT_STRATIFIED_MC_COVERAGE")
        n_effective = {
            xy: math.fsum(ws) ** 2 / math.fsum(v*v for v in ws)
            for xy, ws in massratio.items()}
        diagnostics.append({
            "min_effective_sample_fraction": min(
                n_effective[xy] / count[xy] for xy in count),
            "min_samples_per_xy": min(count.values()),
            "n_xy": len(mu_xy),
            "sampled_z_coverage_min": min(
                len({c["z_level"] for c in cs if c["xy_cell"] == xy}) /
                len(supported[xy]) for xy in mu_xy),
        })
    if len(bats) < MIN_BATS:
        raise ValueError("STOP_Q_FEWER_THAN_FOUR_ANIMALS")
    return tuple(data), diagnostics


def attach_mc_log_weights(events, corrected=True):
    """Only call following validate_q_noisy_events; never label one true Z."""
    prepared = []
    for e in events:
        count = Counter(c["xy_cell"] for c in e["choices"])
        choices = []
        for c in e["choices"]:
            a = dict(c)
            weight = (math.log(e["reference_xy_mass"][c["xy_cell"]]) -
                      math.log(count[c["xy_cell"]]))
            if corrected:
                weight += math.log(c["reference_z_prob"]) - math.log(
                    c["proposal_z_prob"])
            a["log_sampling_weight"] = weight
            choices.append(a)
        item = dict(e)
        item["choices"] = choices
        prepared.append(item)
    return tuple(prepared)


def _test_scores(events, model):
    return _balanced_test_score(events, model)


def compare_q_noise(events, heldout="site", include_state=False):
    """Refit and score exactly the same recorded XY+noisy Y for every model.

    No empirical source admission: the numerical flags and full-support
    dictionaries cannot prove real original file/proposal authenticity.
    """
    data, diagnostics = validate_q_noisy_events(events, include_state)
    names = tuple(LEVELS) if include_state else tuple(LEVELS)[:3]
    if heldout not in ("site", "bat", "bat_night"):
        raise ValueError("STOP_Q_UNKNOWN_HELDOUT_UNIT")
    folds = sorted({_foldkey(e, heldout) for e in data}, key=str)
    if len(folds) < 2:
        raise ValueError("STOP_Q_FEWER_THAN_TWO_GROUPS")
    results = []
    for ordinal, k in enumerate(folds, 1):
        tr = [e for e in data if _foldkey(e, heldout) != k]
        te = [e for e in data if _foldkey(e, heldout) == k]
        if len({e["bat"] for e in tr}) < 3:
            raise ValueError("STOP_Q_FEWER_THAN_THREE_TRAINING_BATS")
        scored = {}
        for name in names:
            scored[name] = {}
            for mode in ("corrected_importance", "uncorrected_q_sampling"):
                corrected = mode == "corrected_importance"
                model = fit_error_aware(
                    attach_mc_log_weights(tr, corrected), LEVELS[name])
                score = _test_scores(
                    attach_mc_log_weights(te, corrected), model)
                scored[name][mode] = score
        gains = {}
        for later, earlier in zip(names[1:], names[:-1]):
            label = later + "_minus_" + earlier
            gains[label] = {
                mode: {field: scored[later][mode][field] -
                       scored[earlier][mode][field] for field in FIELDS}
                for mode in ("corrected_importance", "uncorrected_q_sampling")}
        results.append({
            "heldout_ordinal": ordinal,
            "n_observed_steps": len(te),
            "n_bats": len({e["bat"] for e in te}),
            "scores": scored,
            "nested_gains": gains,
        })
    summary = {}
    for later in names:
        summary[later] = {
            mode: {field: math.fsum(
                r["scores"][later][mode][field] for r in results) / len(results)
                   for field in FIELDS}
            for mode in ("corrected_importance", "uncorrected_q_sampling")}
    increments = {
        later + "_minus_" + earlier: {
            mode: {field: summary[later][mode][field] -
                   summary[earlier][mode][field] for field in FIELDS}
            for mode in ("corrected_importance", "uncorrected_q_sampling")}
        for later, earlier in zip(names[1:], names[:-1])}
    for model_scores in summary.values():
        for comps in model_scores.values():
            if abs(comps["joint"]-comps["horizontal"]-
                   comps["height_given_horizontal"]) > 1e-9:
                raise AssertionError("STOP_BROKEN_Q_NOISE_LOG_DENSITY_IDENTITY")
    return {
        "schema": "batter.q_stratified_importance_noisy_gps_v1",
        "status": STATUS,
        "methods": ["corrected_importance", "uncorrected_q_sampling"],
        "sampling_design": SAMPLER,
        "observed_target": "XY cell and continuous noisy AGL under known sigma",
        "same_noisy_heldout_events_in_all_models": True,
        "same_q_samples_in_all_nested_models": True,
        "n_source_free_events": len(data),
        "n_bats": len({e["bat"] for e in data}),
        "n_folds": len(results),
        "heldout_unit": heldout,
        "model_names": list(names),
        "min_importance_effective_sample_fraction": min(
            d["min_effective_sample_fraction"] for d in diagnostics),
        "min_sampled_z_support_fraction": min(
            d["sampled_z_coverage_min"] for d in diagnostics),
        "per_model_group_equal_scores": summary,
        "nested_group_equal_gains": increments,
        "folds_without_original_group_keys": results,
        "finite_mc_self_normalized_biased": True,
        "not_observed_choice_vs_controls_label_likelihood": True,
        "not_reproduced_continuous_ssf3d": True,
        "source_original_file_access_verified": False,
        "real_resource_height_joint_bat_gain": None,
        "empirical_bat_ecology_claim_allowed": False,
    }
