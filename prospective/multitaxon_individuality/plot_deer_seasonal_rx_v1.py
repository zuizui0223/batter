#!/usr/bin/env python3
"""Reproduce the four-panel deer figure from aggregate analysis JSON only.

Example:
  python plot_deer_seasonal_rx_v1.py --audit DEER_EQUAL_DATA_AUDIT_2026_10_20.json

The script never reads tracking files or per-animal outputs. It validates
panel/cohort mappings, verifies plotted coordinates against the aggregate
chart data, and embeds the input and chart-data hashes in SVG/PNG metadata.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

YEARS = (2018, 2019, 2020)
SCALES = (1, 2, 5, 10)
COLORS = {2018: "#276D9B", 2019: "#B07B18", 2020: "#795399"}
MARKERS = {2018: "o", 2019: "s", 2020: "^"}
LINESTYLES = {2018: "-", 2019: "--", 2020: "-."}
ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "DEER_SEASONAL_RX_RESULT_2026_10_20.json"
DEFAULT_OUTPUT = ROOT / "DEER_SEASONAL_RX_FIGURE_2026_10_20"
TITLE = "Mule deer movement prediction and geographic overlap"
CAPTION_LINES = (
    "R = peer-only CRPS − personal-mixture CRPS on log(1 + standardized 2 h displacement / 0.1 km); positive favors the personal model.",
    "R conditions on full-month eligibility and common 5 km × 6 h contexts, averaging both calendar-half holdout directions; it is not a prospective test.",
    "X is pair-date-balanced geographic occupancy overlap, not resource overlap or encounters. B–C use fixed annual cohorts; selection is survivor-conditioned.",
    "Winter = Dec–Feb; summer = Jun–Aug. C uses pairs with ≥2 supported months per season; shading spans four grid origins, not confidence intervals.",
    "D matches R and X within each month’s evaluated animals. One adult-female Sublette source over three years; no population CI or causal inference.",
)
AUDITED_CAPTION_LINES = (
    "R scores log(1 + standardized 2 h displacement / 0.1 km). Solid: same-record anonymous-pool CRPS − personal CRPS; faint dashed: peer-only gain.",
    "Same-record audit added after inspecting primary outcomes. Both contrasts use full-month eligibility and both calendar-half holdout directions.",
    "R conditions on common 5 km × 6 h contexts. X is pair-date-balanced geographic occupancy overlap, not resource overlap or encounters.",
    "B–C use fixed annual cohorts conditional on year-round observation. C compares winter (Dec–Feb) and summer (Jun–Aug) within supported pairs.",
    "C requires ≥2 supported months per season; shading spans four grid origins, not CI. D uses same-record gain and X for the same monthly animals.",
    "One adult-female Sublette source over three years; survivor-conditioned cohorts, descriptive comparisons, no population CI or causal inference.",
)


def _number_or_none(value):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Chart values must be finite numbers or explicit nulls")
    return float(value)


def _is_origin_zero(row):
    return row["origin_x_fraction"] == 0 and row["origin_y_fraction"] == 0


def _grid_mean(report, scale=5):
    matches = [row for row in report["grids"] if row["scale_km"] == scale and _is_origin_zero(row)]
    if len(matches) != 1:
        raise ValueError("Expected exactly one origin-zero geography grid at the requested scale")
    value = _number_or_none(matches[0]["overlap"]["mean"])
    if value is not None and not 0 <= value <= 1:
        raise ValueError("Geographic occupancy overlap lies outside [0, 1]")
    return value


def prepare_chart_data(result, audit=None):
    """Extract all plotted aggregates with explicit cohort/scale/origin checks."""
    monthly = {}
    for row in result["monthly"]:
        key = (row["year"], row["month"])
        if key in monthly:
            raise ValueError("Duplicate source year/month in aggregate results")
        monthly[key] = row
    expected = {(year, month) for year in YEARS for month in range(1, 13)}
    if set(monthly) != expected:
        raise ValueError("Figure requires exactly twelve months in each of 2018, 2019, and 2020")
    audited = {}
    if audit is not None:
        if audit.get("audit_stage") != "POST_PRIMARY_PEER_GAIN_INSPECTION":
            raise ValueError("The audit stage must explicitly identify its post-primary timing")
        for row in audit["monthly"]:
            key = (row["year"], row["month"])
            if key in audited:
                raise ValueError("Duplicate source year/month in equal-data audit")
            audited[key] = row
        if set(audited) != expected:
            raise ValueError("Equal-data audit and primary results must cover the same 36 months")
    chart = {"years": list(YEARS), "scales_km": list(SCALES), "series": {},
             "R_baseline": "same-record anonymous pool" if audit is not None else "peer-only",
             "equal_data_audit_added_after_primary_inspection": audit is not None}
    for year in YEARS:
        fixed_n = result["constant_cohort_by_year"][str(year)]
        series = {"constant_cohort_n": fixed_n, "monthly_R": [], "monthly_peer_R": [], "monthly_constant_X": [],
                  "matched_monthly": [], "seasonal_X": []}
        for month in range(1, 13):
            row = monthly[(year, month)]
            if row["context_km"] != 5 or not _is_origin_zero(row):
                raise ValueError("Primary R rows must use origin-zero 5 km contexts")
            if row["constant_cohort_X"]["n_animals"] != fixed_n:
                raise ValueError("Constant-cohort X denominator changes within a source year")
            if row["matched_X"]["n_animals"] != row["n_evaluated_animals"]:
                raise ValueError("Matched X does not use the evaluated monthly R cohort")
            primary_r = _number_or_none(row["R_gain"])
            r = primary_r
            if audit is not None:
                audit_row = audited[(year, month)]
                if audit_row["context_km"] != 5 or not _is_origin_zero(audit_row):
                    raise ValueError("Equal-data audit must use the same 5 km origin-zero contexts")
                for key in ("n_evaluated_animals", "heldout_steps", "heldout_animal_days"):
                    if audit_row[key] != row[key]:
                        raise ValueError("Equal-data audit observation mask differs from primary monthly results")
                for key in ("peer_CRPS", "personal_CRPS"):
                    original, checked = _number_or_none(row[key]), _number_or_none(audit_row[key])
                    if ((original is None) != (checked is None)
                            or (original is not None and not math.isclose(original, checked, abs_tol=1e-12, rel_tol=1e-10))):
                        raise ValueError("Audit baseline scores do not reconcile with primary scores")
                peer_gain = _number_or_none(audit_row["original_peer_gain"])
                if ((peer_gain is None) != (primary_r is None)
                        or (primary_r is not None and not math.isclose(peer_gain, primary_r, abs_tol=1e-12, rel_tol=1e-10))):
                    raise ValueError("Audit peer-only gain does not reconcile with primary R")
                r = _number_or_none(audit_row["identity_weight_gain"])
                data_gain = _number_or_none(audit_row["data_addition_gain"])
                if r is not None and not math.isclose(r + data_gain, peer_gain, abs_tol=1e-12, rel_tol=1e-10):
                    raise ValueError("Audit gain components do not sum to the original peer-only gain")
            fixed_x = _grid_mean(row["constant_cohort_X"])
            matched_x = _grid_mean(row["matched_X"])
            series["monthly_R"].append(r)
            series["monthly_peer_R"].append(primary_r)
            series["monthly_constant_X"].append(fixed_x)
            if r is not None and matched_x is not None:
                series["matched_monthly"].append({"month": month, "R": r, "X": matched_x,
                                                 "n_animals": row["n_evaluated_animals"],
                                                 "season": "Winter" if month in (12, 1, 2) else
                                                           "Summer" if month in (6, 7, 8) else "Other months"})
        for scale in SCALES:
            rows = [row for row in result["seasonal_constant_cohort_X"]
                    if row["year"] == year and row["scale_km"] == scale]
            origins = {(row["origin_x_fraction"], row["origin_y_fraction"]) for row in rows}
            if len(rows) != 4 or origins != {(0, 0), (.5, 0), (0, .5), (.5, .5)}:
                raise ValueError("Seasonal sensitivity requires exactly the four declared grid origins")
            origin_zero = next(row for row in rows if _is_origin_zero(row))
            value = _number_or_none(origin_zero["winter_minus_summer_mean"])
            values = [_number_or_none(row["winter_minus_summer_mean"]) for row in rows]
            available = [value for value in values if value is not None]
            series["seasonal_X"].append({"scale_km": scale, "origin_zero": value,
                                          "origin_min": min(available) if available else None,
                                          "origin_max": max(available) if available else None,
                                          "n_available_origins": len(available),
                                          "n_pairs_origin_zero": origin_zero["n_pairs"]})
        chart["series"][str(year)] = series
    return chart


def _array(values):
    return [float("nan") if value is None else value for value in values]


def _verify_coordinates(actual_x, actual_y, expected_x, expected_y):
    """Assert plotted numbers equal the extracted source aggregates exactly."""
    if len(actual_x) != len(expected_x) or len(actual_y) != len(expected_y):
        raise AssertionError("Plotted data length differs from reviewed chart data")
    for actual, expected in zip(list(actual_x) + list(actual_y), list(expected_x) + list(expected_y)):
        if math.isnan(expected):
            if not math.isnan(actual):
                raise AssertionError("Missing data was replaced by a plotted number")
        elif float(actual) != float(expected):
            raise AssertionError("Plotted coordinate differs from its source aggregate")


def render_figure(result, source_sha256, output_stem, *, audit=None, audit_sha256=None):
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "batter-matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FormatStrFormatter, MaxNLocator

    chart = prepare_chart_data(result, audit)
    caption_lines = AUDITED_CAPTION_LINES if audit is not None else CAPTION_LINES
    chart_serialized = json.dumps(chart, sort_keys=True, separators=(",", ":"), allow_nan=False)
    chart_hash = hashlib.sha256(chart_serialized.encode()).hexdigest()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.titlesize": 11.5, "axes.labelsize": 10.5,
                         "xtick.labelsize": 10, "ytick.labelsize": 10,
                         "legend.fontsize": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.edgecolor": "#89919A",
                         "axes.labelcolor": "#20262D", "text.color": "#20262D",
                         "xtick.color": "#40474F", "ytick.color": "#40474F",
                         "svg.fonttype": "none", "svg.hashsalt": "deer-seasonal-rx-v1",
                         "figure.facecolor": "white", "axes.facecolor": "white"})
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.5))
    fig.subplots_adjust(left=.095, right=.975, top=.86, bottom=.275, wspace=.27, hspace=.50)
    fig.suptitle(TITLE, x=.095, y=.974, ha="left", fontsize=16, fontweight="semibold")
    subtitle = ("Sublette adult females · 2018–2020 · primary and post-inspection same-record audit"
                if audit is not None else "Sublette adult females · 2018–2020 · descriptive within-source comparisons")
    fig.text(.095, .933, subtitle,
             fontsize=11, color="#505B65")
    ax_a, ax_b, ax_c, ax_d = axes.flat
    titles = ("A  Conditional prediction-score contrasts", "B  Geographic overlap through the year",
              "C  Winter–summer overlap contrast",
              "D  Same-record gain and geographic X" if audit is not None else "D  Matched monthly R and geographic X")
    for ax, title in zip(axes.flat, titles):
        ax.set_title(title, loc="left", pad=12, fontweight="semibold")
        ax.grid(axis="y", color="#E3E7EB", linewidth=.65, zorder=0)
        ax.tick_params(axis="both", length=3.5, width=.7)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    for ax in (ax_a, ax_b):
        ax.set_xlim(.65, 12.35)
        ax.set_xticks(range(1, 13), [calendar.month_abbr[m] for m in range(1, 13)])
        ax.set_xlabel("Source calendar month", labelpad=7)
    ax_a.axhline(0, color="#616B74", linewidth=.85, zorder=1)
    ax_a.set_ylabel("Gain in log-displacement CRPS\n(positive favors personal model)", labelpad=9)
    ax_b.set_ylabel("X at 5 km\n(mean pair occupancy overlap)", labelpad=9)
    ax_c.axhline(0, color="#616B74", linewidth=.85, zorder=1)
    ax_c.set_xscale("log")
    ax_c.set_xticks(SCALES, [str(value) for value in SCALES])
    ax_c.minorticks_off()
    ax_c.set_xlim(.90, 11.2)
    ax_c.set_xlabel("Grid width (km)", labelpad=7)
    ax_c.set_ylabel("Winter − summer X", labelpad=9)
    ax_d.axhline(0, color="#616B74", linewidth=.85, zorder=1)
    ax_d.set_xlabel("Matched geographic X at 5 km", labelpad=7)
    ax_d.set_ylabel("Same-record CRPS gain" if audit is not None else "R gain (CRPS units)", labelpad=9)
    verified_artists = 0
    for year in YEARS:
        series = chart["series"][str(year)]
        style = {"color": COLORS[year], "marker": MARKERS[year], "linestyle": LINESTYLES[year],
                 "linewidth": 1.65, "markersize": 4.3, "markeredgewidth": .7, "zorder": 3}
        if audit is not None:
            peer_values = _array(series["monthly_peer_R"])
            peer_line, = ax_a.plot(range(1, 13), peer_values, color=COLORS[year], linestyle="--",
                                   marker=MARKERS[year], markersize=2.7, markeredgewidth=.5,
                                   linewidth=1.25, alpha=.38, zorder=2)
            _verify_coordinates(*peer_line.get_data(), list(range(1, 13)), peer_values)
            verified_artists += 1
        for ax, key, label in ((ax_a, "monthly_R", str(year)),
                               (ax_b, "monthly_constant_X", f"{year} (n = {series['constant_cohort_n']})")):
            values = _array(series[key])
            panel_style = dict(style)
            if ax is ax_a and audit is not None:
                panel_style["linestyle"] = "-"
            line, = ax.plot(range(1, 13), values, label=label, **panel_style)
            _verify_coordinates(*line.get_data(), list(range(1, 13)), values)
            verified_artists += 1
        contrasts = series["seasonal_X"]
        origin_values = _array([row["origin_zero"] for row in contrasts])
        line, = ax_c.plot(SCALES, origin_values, label=str(year), **style)
        _verify_coordinates(*line.get_data(), list(SCALES), origin_values)
        verified_artists += 1
        ax_c.fill_between(SCALES, _array([row["origin_min"] for row in contrasts]),
                          _array([row["origin_max"] for row in contrasts]),
                          color=COLORS[year], alpha=.14, linewidth=0, zorder=2)
        for season, marker in (("Winter", "o"), ("Summer", "^"), ("Other months", "s")):
            rows = [row for row in series["matched_monthly"] if row["season"] == season]
            xs, ys = [row["X"] for row in rows], [row["R"] for row in rows]
            artist = ax_d.scatter(xs, ys, marker=marker, s=37, edgecolors=COLORS[year],
                                  facecolors="white" if season == "Other months" else COLORS[year],
                                  linewidths=.9, alpha=.90, zorder=3)
            offsets = artist.get_offsets()
            _verify_coordinates(offsets[:, 0], offsets[:, 1], xs, ys)
            verified_artists += 1
    year_legend = ax_a.legend(loc="upper right", frameon=False, handlelength=2.4, borderaxespad=.35)
    if audit is not None:
        ax_a.add_artist(year_legend)
        ax_a.legend(handles=[Line2D([], [], color="#4C5863", linewidth=1.65, label="Same-record pool"),
                             Line2D([], [], color="#4C5863", linewidth=1.25, linestyle="--", alpha=.45, label="Peer-only")],
                    loc="upper left", frameon=False, handlelength=2.3, borderaxespad=.35, labelspacing=.4)
    all_fixed_x = [value for series in chart["series"].values() for value in series["monthly_constant_X"] if value is not None]
    ax_b.set_ylim(0, min(1, max(all_fixed_x, default=.1) * 1.22))
    ax_b.legend(loc="upper center", bbox_to_anchor=(.65, 1), frameon=False,
                handlelength=2.4, borderaxespad=.35)
    ax_c.text(.02, .96, "Lines: origin 0\nShading: grid-origin sensitivity, not CI", transform=ax_c.transAxes,
              va="top", fontsize=10, color="#4C5863")
    season_handles = [Line2D([], [], color="#67717C", marker=marker, linestyle="None", markersize=6,
                             markerfacecolor="white" if label == "Other months" else "#67717C", label=label)
                      for label, marker in (("Winter", "o"), ("Summer", "^"), ("Other months", "s"))]
    ax_d.legend(handles=season_handles, loc="upper right", frameon=False, borderaxespad=.35,
                handletextpad=.4, labelspacing=.35)
    ax_d.set_xlim(left=min(0, ax_d.get_xlim()[0]))
    for ax in (ax_a, ax_c, ax_d):
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax_b.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax_d.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    if audit is not None:
        ax_d.yaxis.set_major_locator(MaxNLocator(nbins=6, min_n_ticks=5, steps=[1, 2, 5, 10]))
        ax_d.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    caption_y = .204 if audit is not None else .179
    for index, line in enumerate(caption_lines):
        fig.text(.025, caption_y - index * .024, line, fontsize=10, ha="left", va="top", color="#4D5761")
    fig.text(.025, .035, "Source: Movebank DOI 10.5441/001/1.708 · Aggregate analysis dated 20 Oct 2026",
             fontsize=10, color="#69737C")
    description = (" ".join(caption_lines) + f" Input SHA256: {source_sha256}. Equal-data audit SHA256: {audit_sha256}. Aggregate chart-data SHA256: {chart_hash}.")
    output_stem = Path(output_stem)
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    svg, png = output_stem.with_suffix(".svg"), output_stem.with_suffix(".png")
    fig.savefig(svg, metadata={"Title": TITLE, "Description": description,
                              "Creator": Path(__file__).name, "Date": result.get("as_of", "2026-10-20")})
    fig.savefig(png, dpi=220, metadata={"Title": TITLE, "Description": description,
                                       "Software": Path(__file__).name})
    plt.close(fig)
    return {"input_sha256": source_sha256, "audit_sha256": audit_sha256, "chart_data_sha256": chart_hash,
            "R_baseline": chart["R_baseline"],
            "verified_line_and_scatter_artists": verified_artists,
            "monthly_R_values": sum(value is not None for series in chart["series"].values() for value in series["monthly_R"]),
            "monthly_constant_X_values": sum(value is not None for series in chart["series"].values() for value in series["monthly_constant_X"]),
            "seasonal_origin_zero_contrasts": sum(row["origin_zero"] is not None for series in chart["series"].values() for row in series["seasonal_X"]),
            "matched_scatter_points": sum(len(series["matched_monthly"]) for series in chart["series"].values()),
            "constant_cohort_sizes": {year: series["constant_cohort_n"] for year, series in chart["series"].items()},
            "svg": str(svg), "png": str(png), "plotted_coordinate_maximum_absolute_difference": 0.0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--audit", type=Path, help="Optional post-primary equal-data audit for solid R curves and matched scatter")
    parser.add_argument("--output-stem", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.input.read_bytes()
    result = json.loads(source)
    audit_source = args.audit.read_bytes() if args.audit else None
    audit = json.loads(audit_source) if audit_source is not None else None
    summary = render_figure(result, hashlib.sha256(source).hexdigest(), args.output_stem,
                            audit=audit, audit_sha256=hashlib.sha256(audit_source).hexdigest() if audit_source else None)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
