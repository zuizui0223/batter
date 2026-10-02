#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CFG = ROOT / "post_freeze_extensions/3d_niche_partition/external_geometry_prediction_contract_v1.json"
SMALL_CONTRACT = ROOT / "post_freeze_extensions/small_panel_generality/contract_v1.json"
SMALL_RECEIPT = ROOT / "post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
HIPPO_RECEIPT = ROOT / "post_freeze_extensions/3d_niche_partition/source_receipts/height_opening_receipt_v1_hipposideros.json"
HIPPO_DESIGN = ROOT / "post_freeze_extensions/3d_niche_partition/source_receipts/primary_design_v1_hipposideros.json"
OUTDIR = ROOT / "post_freeze_extensions/3d_niche_partition/external_results"

EDGES = (-math.inf, -400.0, -200.0, -100.0, -50.0, 0.0, 50.0, 100.0, 200.0, 400.0, math.inf)
K = len(EDGES) - 1
UA = {"User-Agent": "batter-external-3d-geometry-v1/1.0"}
METRICS = ("oxy", "oxyz", "ozxy", "l3d", "r3d")


def present(s):
    txt = s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na", "nan", "null", "none"})


def norm(x):
    return "_".join(str(x).strip().lower().replace("-", "_").replace(" ", "_").replace(".", "_").split("_"))


def boolish(x):
    s = str(x).strip().lower()
    if s in {"true", "t", "1", "yes", "y"}:
        return True
    if s in {"false", "f", "0", "no", "n"}:
        return False
    return None


def load_cfg():
    return json.loads(CFG.read_text(encoding="utf-8"))


def standardize_small_panel(source_key):
    contract = json.loads(SMALL_CONTRACT.read_text(encoding="utf-8"))
    receipt = json.loads(SMALL_RECEIPT.read_text(encoding="utf-8"))
    src = {x["source_id"]: x for x in contract["closed_source_set"]}[source_key]
    rec = receipt["sources"][source_key]

    r = requests.get(src["event_url"], headers=UA, timeout=300)
    r.raise_for_status()
    raw = r.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != rec["raw_sha256"]:
        raise RuntimeError(f"{source_key}: raw SHA mismatch {sha}")

    hdr = pd.read_csv(io.BytesIO(raw), nrows=0)
    cmap = {norm(x): x for x in hdr.columns}
    req = ["timestamp", "location_long", "location_lat", "individual_local_identifier", norm(src["vertical_field"])]
    missing = [x for x in req if x not in cmap]
    if missing:
        raise RuntimeError(f"{source_key}: missing fields {missing}")

    use = [cmap[x] for x in req]
    for q in ["visible", "algorithm_marked_outlier", "manually_marked_outlier", "import_marked_outlier"]:
        if q in cmap:
            use.append(cmap[q])
    use = list(dict.fromkeys(use))
    df = pd.read_csv(io.BytesIO(raw), dtype=str, usecols=use, low_memory=False)

    tcol = cmap["timestamp"]
    loncol = cmap["location_long"]
    latcol = cmap["location_lat"]
    iidcol = cmap["individual_local_identifier"]
    hcol = cmap[norm(src["vertical_field"])]

    mask = present(df[tcol]) & present(df[loncol]) & present(df[latcol]) & present(df[iidcol]) & present(df[hcol])
    d = df.loc[mask].copy()

    if "visible" in cmap and cmap["visible"] in d:
        keep = []
        for x in d[cmap["visible"]]:
            b = boolish(x)
            keep.append(True if b is None else b)
        d = d.loc[keep].copy()

    for q in ["algorithm_marked_outlier", "manually_marked_outlier", "import_marked_outlier"]:
        if q in cmap and cmap[q] in d:
            keep = []
            for x in d[cmap[q]]:
                b = boolish(x)
                keep.append(True if b is None else (not b))
            d = d.loc[keep].copy()

    d["iid"] = d[iidcol].astype(str).str.strip()
    d["t"] = pd.to_datetime(d[tcol], errors="coerce", utc=True, format="mixed")
    d["lon"] = pd.to_numeric(d[loncol], errors="coerce")
    d["lat"] = pd.to_numeric(d[latcol], errors="coerce")
    d["h"] = pd.to_numeric(d[hcol], errors="coerce")
    bad = d["t"].isna() | d["lon"].isna() | d["lat"].isna() | d["h"].isna()
    d = d.loc[~bad].sort_values(["iid", "t"]).copy()
    if not np.isfinite(d["h"].to_numpy(dtype=float)).all():
        raise RuntimeError(f"{source_key}: nonfinite height")

    d["sess_num"] = -1
    for iid, g in d.groupby("iid", sort=True):
        vals = []
        k = 0
        prev = None
        for t in g["t"]:
            if prev is not None and (t - prev) > pd.Timedelta(hours=4):
                k += 1
            vals.append(k)
            prev = t
        d.loc[g.index, "sess_num"] = vals
    d["session"] = d["iid"] + "::" + d["sess_num"].astype(int).astype(str)

    targets = {
        str(x["session"])
        for rows in rec["frozen_vertical_target_sessions"].values()
        for x in rows
    }
    d = d[d["session"].isin(targets)].copy()
    if set(d["session"].unique()) != targets:
        missing = sorted(targets - set(d["session"].unique()))
        raise RuntimeError(f"{source_key}: target sessions missing {missing[:5]}")

    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{int(rec['projection_epsg'])}", always_xy=True)
    x, y = tr.transform(d["lon"].to_numpy(dtype=float), d["lat"].to_numpy(dtype=float))
    out = pd.DataFrame({
        "cohort": source_key,
        "iid": d["iid"].astype(str).to_numpy(),
        "session": d["session"].astype(str).to_numpy(),
        "x": np.asarray(x, dtype=float),
        "y": np.asarray(y, dtype=float),
        "h": d["h"].to_numpy(dtype=float),
    })
    return out, {
        "source_id": source_key,
        "taxon": rec["taxon"],
        "raw_sha256": sha,
        "target_sessions": len(targets),
    }


def standardize_nyctalus():
    url = "https://zenodo.org/api/records/7535030/files/Observed_GPS_locations.csv/content"
    expected_sha = "2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9"
    r = requests.get(url, headers=UA, timeout=180)
    r.raise_for_status()
    raw = r.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != expected_sha:
        raise RuntimeError(f"Nyctalus SHA mismatch {sha}")
    df = pd.read_csv(io.BytesIO(raw), dtype=str, low_memory=False)

    req = ["bat_id", "trackid", "utc", "x", "y", "Height", "Year", "field_period"]
    mask = pd.Series(True, index=df.index)
    for col in req:
        mask &= present(df[col])
    d = df.loc[mask, req].copy()
    d["x_num"] = pd.to_numeric(d["x"], errors="coerce")
    d["y_num"] = pd.to_numeric(d["y"], errors="coerce")
    d["h_num"] = pd.to_numeric(d["Height"], errors="coerce")
    d["t_num"] = pd.to_datetime(d["utc"], errors="coerce", utc=True)
    d = d.loc[d["x_num"].notna() & d["y_num"].notna() & d["h_num"].notna() & d["t_num"].notna()].copy()
    if not np.isfinite(d["h_num"].to_numpy(dtype=float)).all():
        raise RuntimeError("Nyctalus nonfinite Height")

    d["cohort"] = d["Year"].astype(str) + "::" + d["field_period"].astype(str)
    d["iid_key"] = d["cohort"] + "::" + d["bat_id"].astype(str)
    d["session_key"] = d["cohort"] + "::" + d["trackid"].astype(str)

    counts = d.groupby(["cohort", "iid_key", "session_key"]).size().rename("n").reset_index()
    eligible = counts[counts["n"] >= 50]
    keys = set(zip(eligible["cohort"], eligible["iid_key"], eligible["session_key"]))
    d = d.loc[
        [(c, i, s) in keys for c, i, s in zip(d["cohort"], d["iid_key"], d["session_key"])]
    ].copy()

    # Reconstruct the exact first prospective n=27 target-session universe at 5 km.
    events = defaultdict(list)
    for (cohort, iid, sid), g in d.groupby(["cohort", "iid_key", "session_key"], sort=True):
        med = float(np.median(g["h_num"].to_numpy(dtype=float)))
        for row in g.itertuples(index=False):
            cell = (math.floor(float(row.x_num) / 5000.0), math.floor(float(row.y_num) / 5000.0))
            events[cohort].append(Event(
                individual=iid,
                timestamp=row.t_num.to_pydatetime(),
                cell=cell,
                zbin=z_bin(float(row.h_num - med), edges=EDGES),
                session=sid,
            ))
    arrays = {c: cal.make_cohort_arrays(e, K) for c, e in sorted(events.items())}
    observed, _, session_rows = cal.observed_eval(arrays)
    if observed["eligible_individuals"] != 27 or len(session_rows) != 47:
        raise RuntimeError(f"Nyctalus first-primary universe mismatch n={observed['eligible_individuals']} sessions={len(session_rows)}")
    targets = {str(x["session"]) for x in session_rows}

    d = d[d["session_key"].isin(targets)].copy()
    out = pd.DataFrame({
        "cohort": d["cohort"].astype(str).to_numpy(),
        "iid": d["iid_key"].astype(str).to_numpy(),
        "session": d["session_key"].astype(str).to_numpy(),
        "x": d["x_num"].to_numpy(dtype=float),
        "y": d["y_num"].to_numpy(dtype=float),
        "h": d["h_num"].to_numpy(dtype=float),
    })
    return out, {
        "source_id": "nyctalus_noctula",
        "taxon": "Nyctalus noctula",
        "raw_sha256": sha,
        "first_primary_individual_units": 27,
        "target_sessions": 47,
    }


def hippo_session_date(d, rule):
    t = pd.to_datetime(d["timestamp"], errors="coerce", format="mixed")
    if t.isna().any():
        raise RuntimeError("Hipposideros timestamp parse failure")
    if rule == "timestamp_minus_12h_then_date":
        return (t - pd.Timedelta(hours=12)).dt.date.astype(str)
    if rule == "raw_calendar_date":
        return t.dt.date.astype(str)
    raise RuntimeError(f"unknown Hipposideros session rule {rule}")


def standardize_hipposideros():
    receipt = json.loads(HIPPO_RECEIPT.read_text(encoding="utf-8"))
    design = json.loads(HIPPO_DESIGN.read_text(encoding="utf-8"))
    token = os.environ.get("DRYAD_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN missing")

    file_id = int(receipt["dryad_file_id"])
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "batter-external-3d-geometry-v1/1.0",
    }
    api_url = f"https://datadryad.org/api/v2/files/{file_id}/download"
    r = requests.get(api_url, headers=headers, timeout=180, allow_redirects=True)
    if r.status_code != 200:
        # Access-route fallback only: the published Dryad landing page exposes the
        # same file through /downloads/file_stream/<file_id>. Scientific identity
        # remains guarded by the pre-existing frozen SHA256 below.
        public_url = f"https://datadryad.org/downloads/file_stream/{file_id}"
        r = requests.get(public_url, headers=UA, timeout=180, allow_redirects=True)
    r.raise_for_status()
    raw = r.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != receipt["raw_sha256"]:
        raise RuntimeError(f"Hipposideros SHA mismatch {sha}")

    df = pd.read_csv(io.BytesIO(raw), dtype=str, low_memory=False)
    req = ["id", "timestamp", "longitude", "latitude", "height"]
    mask = pd.Series(True, index=df.index)
    for col in req:
        mask &= present(df[col])
    d = df.loc[mask, req].copy()
    d["id"] = d["id"].astype(str).str.strip()
    d["session_date"] = hippo_session_date(d, receipt["session_rule"])

    prefix_to_species = receipt["species_by_prefix"]
    def map_species(iid):
        p = ""
        for ch in iid:
            if ch.isalpha():
                p += ch
            else:
                break
        return prefix_to_species.get(p)

    d["species"] = d["id"].map(map_species)
    if d["species"].isna().any():
        raise RuntimeError("Hipposideros species mapping failure")

    d["lon"] = pd.to_numeric(d["longitude"], errors="coerce")
    d["lat"] = pd.to_numeric(d["latitude"], errors="coerce")
    d["h"] = pd.to_numeric(d["height"], errors="coerce")
    if d[["lon", "lat", "h"]].isna().any().any():
        raise RuntimeError("Hipposideros numeric parse failure")
    if not np.isfinite(d["h"].to_numpy(dtype=float)).all():
        raise RuntimeError("Hipposideros nonfinite height")

    target_keys = set()
    for sp, by_id in receipt["frozen_evaluable_target_sessions_by_species"].items():
        for iid, rows in by_id.items():
            for x in rows:
                target_keys.add((sp, iid, str(x["session_date"])))

    keep = [
        (sp, iid, sd) in target_keys
        for sp, iid, sd in zip(d["species"], d["id"], d["session_date"])
    ]
    d = d.loc[keep].copy()
    got = set(zip(d["species"], d["id"], d["session_date"]))
    if got != target_keys:
        missing = sorted(target_keys - got)
        raise RuntimeError(f"Hipposideros target sessions missing {missing[:5]}")

    tr = Transformer.from_crs("EPSG:4326", "EPSG:32648", always_xy=True)
    x, y = tr.transform(d["lon"].to_numpy(dtype=float), d["lat"].to_numpy(dtype=float))
    out = pd.DataFrame({
        "cohort": d["species"].astype(str).to_numpy(),
        "iid": d["id"].astype(str).to_numpy(),
        "session": (d["id"].astype(str) + "::" + d["session_date"].astype(str)).to_numpy(),
        "x": np.asarray(x, dtype=float),
        "y": np.asarray(y, dtype=float),
        "h": d["h"].to_numpy(dtype=float),
    })
    return out, {
        "source_id": "hipposideros",
        "taxa": list(receipt["eligible_species_panels"]),
        "raw_sha256": sha,
        "target_sessions": len(target_keys),
        "paper_doi": design["source"]["paper_doi"],
    }


def standardized_source(source):
    if source == "myotis_vivesi":
        return standardize_small_panel("myotis_vivesi_kk3bg2f4")
    if source == "pteropus_poliocephalus":
        return standardize_small_panel("pteropus_poliocephalus_5bd6pq55")
    if source == "nyctalus_noctula":
        return standardize_nyctalus()
    if source == "hipposideros":
        return standardize_hipposideros()
    raise ValueError(source)


def build_sessions(df, grid_m, alpha):
    by_cohort = defaultdict(list)
    for (cohort, sid, iid), g in df.groupby(["cohort", "session", "iid"], sort=True):
        med = float(np.median(g["h"].to_numpy(dtype=float)))
        counts = defaultdict(lambda: np.zeros(K, dtype=np.int64))
        for row in g.itertuples(index=False):
            c = (math.floor(float(row.x) / grid_m), math.floor(float(row.y) / grid_m))
            zb = z_bin(float(row.h - med), edges=EDGES)
            counts[c][zb] += 1
        cell_n = {c: int(v.sum()) for c, v in counts.items()}
        total = int(sum(cell_n.values()))
        if total <= 0:
            continue
        pxy = {c: n / total for c, n in cell_n.items()}
        pz = {
            c: (v.astype(float) + alpha) / (float(v.sum()) + alpha * K)
            for c, v in counts.items()
        }
        joint = {c: pxy[c] * pz[c] for c in counts}
        by_cohort[str(cohort)].append({
            "cohort": str(cohort),
            "session": str(sid),
            "individual": str(iid),
            "n": total,
            "cell_n": cell_n,
            "pxy": pxy,
            "pz": pz,
            "joint": joint,
        })
    for c in by_cohort:
        by_cohort[c].sort(key=lambda x: x["session"])
    return dict(by_cohort)


def pair_metrics(a, b, min_common):
    common = sorted(set(a["cell_n"]) & set(b["cell_n"]))
    if not common:
        return None
    na = sum(a["cell_n"][c] for c in common)
    nb = sum(b["cell_n"][c] for c in common)
    if na < min_common or nb < min_common:
        return None
    oxy = float(sum(min(a["pxy"][c], b["pxy"][c]) for c in common))
    if oxy <= 0:
        return None
    oxyz = 0.0
    ozxy = 0.0
    for c in common:
        oxyz += float(np.minimum(a["joint"][c], b["joint"][c]).sum())
        w = min(a["pxy"][c], b["pxy"][c]) / oxy
        ozxy += w * float(np.minimum(a["pz"][c], b["pz"][c]).sum())
    l3d = oxy - oxyz
    r3d = 1.0 - oxyz / oxy
    return {
        "oxy": oxy,
        "oxyz": float(oxyz),
        "ozxy": float(ozxy),
        "l3d": float(l3d),
        "r3d": float(r3d),
    }


def metric_matrices(sessions, min_common):
    n = len(sessions)
    mats = {m: np.full((n, n), np.nan, dtype=float) for m in METRICS}
    pair_count = 0
    for i in range(n):
        for j in range(i + 1, n):
            pm = pair_metrics(sessions[i], sessions[j], min_common)
            if pm is None:
                continue
            pair_count += 1
            for m in METRICS:
                mats[m][i, j] = mats[m][j, i] = pm[m]
    return mats, pair_count


def eval_cohort(sessions, mats, labels):
    rows = []
    uniq = sorted(set(labels))
    idx = np.arange(len(sessions))
    for t in range(len(sessions)):
        lab = labels[t]
        row = mats["ozxy"][t]
        valid = np.isfinite(row) & (idx != t)
        self_mask = valid & (labels == lab)
        if not np.any(self_mask):
            continue
        other_labels = []
        for olab in uniq:
            if olab == lab:
                continue
            mask = valid & (labels == olab)
            if np.any(mask):
                other_labels.append(olab)
        if len(other_labels) < 2:
            continue

        out = {
            "cohort": sessions[t]["cohort"],
            "session": sessions[t]["session"],
            "individual": str(lab),
        }
        for m in METRICS:
            mr = mats[m][t]
            self_mean = float(np.nanmean(mr[self_mask]))
            other_means = []
            for olab in other_labels:
                mask = valid & (labels == olab)
                other_means.append(float(np.nanmean(mr[mask])))
            other_mean = float(np.mean(other_means))
            out[f"self_{m}"] = self_mean
            out[f"other_{m}"] = other_mean
            out[f"d_{m}"] = self_mean - other_mean
        rows.append(out)
    return rows


def aggregate_rows(rows):
    per = {}
    for iid in sorted({r["individual"] for r in rows}):
        rs = [r for r in rows if r["individual"] == iid]
        d = {"evaluable_sessions": len(rs), "cohorts": sorted({r["cohort"] for r in rs})}
        for p in ("self", "other", "d"):
            for m in METRICS:
                d[f"{p}_{m}"] = float(np.mean([r[f"{p}_{m}"] for r in rs]))
        per[iid] = d
    vals = list(per.values())
    out = {"eligible_individuals": len(vals)}
    for p in ("self", "other", "d"):
        for m in METRICS:
            out[f"{p}_{m}"] = float(np.mean([v[f"{p}_{m}"] for v in vals])) if vals else None
    out["d_panel"] = out["d_ozxy"]
    return out, per


def evaluate_generic(sessions_by_cohort, mats_by_cohort, labels_by_cohort):
    rows = []
    for cohort, sessions in sessions_by_cohort.items():
        rows.extend(eval_cohort(sessions, mats_by_cohort[cohort], labels_by_cohort[cohort]))
    return aggregate_rows(rows) + (rows,)


def evaluate_hippo(sessions_by_cohort, mats_by_cohort, labels_by_cohort, species_min=3, total_min=5):
    species = {}
    all_rows = []
    eligible_total = 0
    for sp, sessions in sessions_by_cohort.items():
        rows = eval_cohort(sessions, mats_by_cohort[sp], labels_by_cohort[sp])
        summ, per = aggregate_rows(rows)
        species[sp] = {"summary": summ, "individual_results": per, "session_results": rows}
        all_rows.extend(rows)
        if summ["eligible_individuals"] >= species_min:
            eligible_total += summ["eligible_individuals"]

    included = [sp for sp, x in species.items() if x["summary"]["eligible_individuals"] >= species_min]
    source_ok = eligible_total >= total_min and len(included) >= 1
    out = {
        "eligible_individuals": eligible_total,
        "eligible_species": included,
        "d_panel": None,
    }
    for p in ("self", "other", "d"):
        for m in METRICS:
            vals = [species[sp]["summary"][f"{p}_{m}"] for sp in included]
            out[f"{p}_{m}"] = float(np.mean(vals)) if source_ok and vals else None
    out["d_panel"] = out.get("d_ozxy")
    return out, species, all_rows


def run(source):
    cfg = load_cfg()
    source_cfg = cfg["sources"][source]
    df, provenance = standardized_source(source)
    sessions = build_sessions(df, float(cfg["primary_grid_m"]), float(cfg["alpha"]))
    mats = {}
    pair_counts = {}
    for cohort, ss in sessions.items():
        mats[cohort], pair_counts[cohort] = metric_matrices(ss, int(cfg["pair_shared_fix_min_each"]))

    labels = {
        cohort: np.array([s["individual"] for s in ss], dtype=object)
        for cohort, ss in sessions.items()
    }

    if source == "hipposideros":
        observed, species_results, session_rows = evaluate_hippo(sessions, mats, labels)
        structural = (
            observed["eligible_individuals"] >= int(source_cfg["source_total_min_evaluable_individuals"])
            and len(observed["eligible_species"]) >= 1
        )
        individual_results = {sp: x["individual_results"] for sp, x in species_results.items()}
        extra_observed = {"species_results": species_results}
    else:
        observed, individual_results, session_rows = evaluate_generic(sessions, mats, labels)
        structural = observed["eligible_individuals"] >= int(source_cfg["primary_gate_n"])
        extra_observed = {}

    B = int(cfg["B"])
    seed = int(source_cfg["seed"])
    rng = np.random.default_rng(seed)
    null = []
    null_n = []
    invalid = 0

    if structural:
        for _ in range(B):
            plabels = {c: rng.permutation(v) for c, v in labels.items()}
            if source == "hipposideros":
                s, _, _ = evaluate_hippo(sessions, mats, plabels)
                ok = (
                    s["eligible_individuals"] >= int(source_cfg["source_total_min_evaluable_individuals"])
                    and len(s["eligible_species"]) >= 1
                    and s["d_panel"] is not None
                )
            else:
                s, _, _ = evaluate_generic(sessions, mats, plabels)
                ok = s["eligible_individuals"] >= int(source_cfg["primary_gate_n"]) and s["d_panel"] is not None
            if not ok:
                invalid += 1
                continue
            null.append(float(s["d_panel"]))
            null_n.append(int(s["eligible_individuals"]))

    calibration = cal.tail_summary(null, float(observed["d_panel"])) if structural and null else None
    supported = bool(
        calibration
        and calibration["observed_minus_null_mean"] > 0
        and calibration["p_null_ge_observed"] <= 0.05
    )

    if not structural:
        prediction_status = "not_evaluable"
    elif source in {"myotis_vivesi", "nyctalus_noctula", "hipposideros"}:
        prediction_status = "aligned" if not supported else "contradicted"
    else:
        prediction_status = "aligned" if supported else "contradicted"

    payload = {
        "study_id": cfg["study_id"],
        "source": source,
        "prediction": source_cfg,
        "provenance": provenance,
        "session_counts": {c: len(v) for c, v in sessions.items()},
        "pair_counts": pair_counts,
        "observed": {
            **observed,
            "individual_results": individual_results,
            "session_results": session_rows,
            **extra_observed,
        },
        "permutation": {
            "B_requested": B,
            "seed": seed,
            "valid_replicates": len(null),
            "invalid_replicates": invalid,
            "eligible_individuals_null": {
                "mean": float(np.mean(null_n)) if null_n else None,
                "min": int(np.min(null_n)) if null_n else None,
                "max": int(np.max(null_n)) if null_n else None,
            },
            "primary_d_panel": calibration,
        },
        "decision": {
            "structural_gate_met": structural,
            "supported": supported,
            "prediction_status": prediction_status,
        },
        "claim_boundary": [
            "new 3D geometry endpoint; previous centered-vertical outcomes already known",
            "does not prove causal ecology-to-geometry mapping",
            "does not prove competition or intentional avoidance",
        ],
    }

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f"{source}_result_v1.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "source": source,
        "eligible_individuals": observed["eligible_individuals"],
        "eligible_species": observed.get("eligible_species"),
        "self_oxy": observed.get("self_oxy"),
        "other_oxy": observed.get("other_oxy"),
        "self_ozxy": observed.get("self_ozxy"),
        "other_ozxy": observed.get("other_ozxy"),
        "d_panel": observed.get("d_panel"),
        "self_r3d": observed.get("self_r3d"),
        "other_r3d": observed.get("other_r3d"),
        "calibrated_excess": calibration["observed_minus_null_mean"] if calibration else None,
        "p_upper": calibration["p_null_ge_observed"] if calibration else None,
        "structural_gate": structural,
        "supported": supported,
        "prediction_status": prediction_status,
    }, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=[
        "myotis_vivesi",
        "pteropus_poliocephalus",
        "nyctalus_noctula",
        "hipposideros",
    ])
    args = ap.parse_args()
    run(args.source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
