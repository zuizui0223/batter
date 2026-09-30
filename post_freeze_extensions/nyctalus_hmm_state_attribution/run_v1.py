#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batter.analysis import z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CONTRACT = ROOT / "post_freeze_extensions/nyctalus_hmm_state_attribution/contract_v1.json"
OUT = ROOT / "post_freeze_extensions/nyctalus_hmm_state_attribution/result_v1.json"
OUT_MD = ROOT / "post_freeze_extensions/nyctalus_hmm_state_attribution/RESULT_V1.md"

UA = {"User-Agent": "batter-nyctalus-hmm-state-attribution-v1/1.0"}
EDGES = (-math.inf, -400.0, -200.0, -100.0, -50.0, 0.0, 50.0, 100.0, 200.0, 400.0, math.inf)
K = len(EDGES) - 1
ALPHA = 0.5


def present(s: pd.Series) -> pd.Series:
    txt = s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na", "nan", "null", "none"})


def fetch_df(c):
    meta = requests.get(
        f"https://zenodo.org/api/records/{c['source']['record_id']}",
        headers=UA,
        timeout=90,
    )
    meta.raise_for_status()
    rec = meta.json()
    target = None
    for f in rec.get("files", []):
        if (f.get("key") or f.get("filename")) == c["source"]["file"]:
            target = f
            break
    if target is None:
        raise RuntimeError("frozen source file not found")
    url = (target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r = requests.get(url, headers=UA, timeout=180)
    r.raise_for_status()
    raw = r.content
    sha = hashlib.sha256(raw).hexdigest()
    if sha != c["source"]["sha256"]:
        raise RuntimeError(f"source SHA mismatch: {sha}")
    return pd.read_csv(io.BytesIO(raw), dtype=str, low_memory=False), sha, len(raw)


def prepare(c):
    df, sha, size = fetch_df(c)
    req = ["bat_id", "trackid", "utc", "x", "y", "Height", "Year", "field_period", "move_state"]
    missing = [x for x in req if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing frozen fields: {missing}")

    mask = pd.Series(True, index=df.index)
    for col in ["bat_id", "trackid", "utc", "x", "y", "Height", "Year", "field_period"]:
        mask &= present(df[col])
    d = df.loc[mask, req].copy()

    d["x_num"] = pd.to_numeric(d["x"], errors="coerce")
    d["y_num"] = pd.to_numeric(d["y"], errors="coerce")
    d["height_num"] = pd.to_numeric(d["Height"], errors="coerce")
    d["t"] = pd.to_datetime(d["utc"], errors="coerce", utc=True)
    if d[["x_num", "y_num", "height_num", "t"]].isna().any().any():
        raise RuntimeError("parse failure in frozen retained rows")
    if not np.isfinite(d["height_num"].to_numpy(dtype=float)).all():
        raise RuntimeError("non-finite Height")

    d["bat_id"] = d["bat_id"].astype(str)
    d["trackid"] = d["trackid"].astype(str)
    d["cohort"] = d["Year"].astype(str).str.strip() + "::" + d["field_period"].astype(str).str.strip()
    d["move_state"] = d["move_state"].astype(str).str.strip()

    # Exact later-family vertical preprocessing: full-track median before state filtering.
    d["track_median"] = d.groupby(["cohort", "trackid"])["height_num"].transform("median")
    d["resid_height"] = d["height_num"] - d["track_median"]

    valid_states = set(c["fixed_context"]["valid_source_states"])
    q = d[d["move_state"].isin(valid_states)].copy()
    grid = int(c["fixed_context"]["horizontal_grid_m"])
    q["cx"] = np.floor(q["x_num"].astype(float) / grid).astype(int)
    q["cy"] = np.floor(q["y_num"].astype(float) / grid).astype(int)
    q["zbin"] = [z_bin(float(x), edges=EDGES) for x in q["resid_height"]]

    cohorts = defaultdict(dict)
    for (cohort, sid), g in q.groupby(["cohort", "trackid"], sort=True):
        iid = str(g["bat_id"].iloc[0])
        if g["bat_id"].nunique() != 1:
            raise RuntimeError(f"track {sid} has multiple bat IDs")
        state_counts = {}
        base_counts = {}
        state_to_base = {}
        for r in g.itertuples(index=False):
            base = (int(r.cx), int(r.cy))
            st = base + (str(r.move_state),)
            if st not in state_counts:
                state_counts[st] = np.zeros(K, dtype=float)
            if base not in base_counts:
                base_counts[base] = np.zeros(K, dtype=float)
            state_counts[st][int(r.zbin)] += 1
            base_counts[base][int(r.zbin)] += 1
            state_to_base[st] = base
        cohorts[str(cohort)][str(sid)] = {
            "session": str(sid),
            "original_label": iid,
            "state_counts": state_counts,
            "base_counts": base_counts,
            "state_to_base": state_to_base,
        }

    return dict(cohorts), {
        "source_sha256": sha,
        "source_size_bytes": size,
        "all_retained_rows": int(len(d)),
        "arm_com_rows": int(len(q)),
        "tracks_with_arm_com": int(sum(len(x) for x in cohorts.values())),
        "cohorts": sorted(cohorts),
    }


def smooth(cnt):
    x = np.asarray(cnt, dtype=float) + ALPHA
    return x / x.sum()


def self_profile(sessions, sids, key):
    per = defaultdict(list)
    for sid in sids:
        for stratum, cnt in sessions[sid][key].items():
            per[stratum].append(smooth(cnt))
    return {s: np.mean(np.stack(vals), axis=0) for s, vals in per.items()}


def other_profile(sessions, sids, labels, key):
    # Pool sessions within each other bat, then equal-weight other bats.
    grouped = {}
    for sid in sids:
        lab = labels[sid]
        for stratum, cnt in sessions[sid][key].items():
            k = (lab, stratum)
            if k not in grouped:
                grouped[k] = np.zeros(K, dtype=float)
            grouped[k] += cnt
    per = defaultdict(list)
    for (lab, stratum), cnt in grouped.items():
        per[stratum].append(smooth(cnt))
    return {s: np.mean(np.stack(vals), axis=0) for s, vals in per.items()}


def self_common_weights(sessions, sids, supported, key):
    supported = list(supported)
    ws = []
    for sid in sids:
        vals = np.array(
            [float(sessions[sid][key].get(s, np.zeros(K)).sum()) for s in supported],
            dtype=float,
        )
        tot = vals.sum()
        if tot > 0:
            ws.append(vals / tot)
    if not ws:
        return None
    w = np.mean(np.stack(ws), axis=0)
    tot = w.sum()
    return w / tot if tot > 0 else None


def score(cohorts, labels_by_cohort, min_scored):
    rows = []
    for cohort, sessions in sorted(cohorts.items()):
        labels = labels_by_cohort[cohort]
        ids = sorted(sessions)
        for sid in ids:
            lab = labels[sid]
            self_sids = [x for x in ids if x != sid and labels[x] == lab]
            other_sids = [x for x in ids if labels[x] != lab]
            if not self_sids or not other_sids:
                continue

            ps_state = self_profile(sessions, self_sids, "state_counts")
            po_state = other_profile(sessions, other_sids, labels, "state_counts")
            ps_base = self_profile(sessions, self_sids, "base_counts")
            po_base = other_profile(sessions, other_sids, labels, "base_counts")

            target = sessions[sid]
            supported_state = [
                st for st in target["state_counts"]
                if st in ps_state and st in po_state
                and target["state_to_base"][st] in ps_base
                and target["state_to_base"][st] in po_base
            ]
            scored = int(sum(target["state_counts"][st].sum() for st in supported_state))
            if scored < min_scored:
                continue

            supported_base = sorted({target["state_to_base"][st] for st in supported_state})
            w_state = self_common_weights(sessions, self_sids, supported_state, "state_counts")
            w_base = self_common_weights(sessions, self_sids, supported_base, "base_counts")
            if w_state is None or w_base is None:
                continue

            ps_state_mat = np.stack([ps_state[st] for st in supported_state])
            po_state_mat = np.stack([po_state[st] for st in supported_state])
            ps_base_mat = np.stack([ps_base[b] for b in supported_base])
            po_base_mat = np.stack([po_base[b] for b in supported_base])

            m_self_state = np.sum(ps_state_mat * w_state[:, None], axis=0)
            m_other_state = np.sum(po_state_mat * w_state[:, None], axis=0)
            m_self_base = np.sum(ps_base_mat * w_base[:, None], axis=0)
            m_other_base = np.sum(po_base_mat * w_base[:, None], axis=0)

            target_z = np.zeros(K, dtype=float)
            for st in supported_state:
                target_z += target["state_counts"][st]

            g_state = float(np.sum(target_z * (np.log(m_self_state) - np.log(m_other_state))) / scored)
            g_base = float(np.sum(target_z * (np.log(m_self_base) - np.log(m_other_base))) / scored)
            rows.append({
                "cohort": cohort,
                "session": sid,
                "label": lab,
                "scored_events": scored,
                "state_gain": g_state,
                "collapsed_gain": g_base,
                "state_increment": g_state - g_base,
            })

    per = {}
    for lab in sorted({r["label"] for r in rows}):
        rs = [r for r in rows if r["label"] == lab]
        per[lab] = {
            "evaluable_sessions": len(rs),
            "state_gain": float(np.mean([r["state_gain"] for r in rs])),
            "collapsed_gain": float(np.mean([r["collapsed_gain"] for r in rs])),
            "state_increment": float(np.mean([r["state_increment"] for r in rs])),
        }
    vals = list(per.values())
    return {
        "eligible_individuals": len(vals),
        "state_gain": float(np.mean([v["state_gain"] for v in vals])) if vals else None,
        "collapsed_gain": float(np.mean([v["collapsed_gain"] for v in vals])) if vals else None,
        "state_increment": float(np.mean([v["state_increment"] for v in vals])) if vals else None,
        "individual_results": per,
        "session_results": rows,
    }


def observed_labels(cohorts):
    return {
        cohort: {sid: rec["original_label"] for sid, rec in sessions.items()}
        for cohort, sessions in cohorts.items()
    }


def perm_labels(cohorts, rng):
    out = {}
    for cohort, sessions in sorted(cohorts.items()):
        ids = sorted(sessions)
        labs = np.asarray([sessions[sid]["original_label"] for sid in ids], dtype=object)
        pp = rng.permutation(labs)
        out[cohort] = {sid: str(pp[i]) for i, sid in enumerate(ids)}
    return out


def main():
    c = json.loads(CONTRACT.read_text())
    cohorts, diag = prepare(c)
    min_scored = int(c["fixed_context"]["minimum_scored_target_events"])
    obs = score(cohorts, observed_labels(cohorts), min_scored)
    expected = int(c["fixed_context"]["expected_evaluable_individuals"])
    if obs["eligible_individuals"] != expected:
        raise RuntimeError(f"observed n {obs['eligible_individuals']} != frozen {expected}")

    B = int(c["calibration"]["B"])
    seed = int(c["calibration"]["seed"])
    rng = np.random.default_rng(seed)
    null_inc, null_state, null_base = [], [], []
    invalid = 0
    for _ in range(B):
        p = score(cohorts, perm_labels(cohorts, rng), min_scored)
        if p["eligible_individuals"] < 1:
            invalid += 1
            continue
        null_inc.append(float(p["state_increment"]))
        null_state.append(float(p["state_gain"]))
        null_base.append(float(p["collapsed_gain"]))

    if not null_inc:
        raise RuntimeError("no valid permutation replicates")

    inc = cal.tail_summary(null_inc, float(obs["state_increment"]))
    state = cal.tail_summary(null_state, float(obs["state_gain"]))
    base = cal.tail_summary(null_base, float(obs["collapsed_gain"]))
    supported = inc["observed_minus_null_mean"] < 0 and inc["p_null_le_observed"] <= 0.05

    payload = {
        "schema_version": 1,
        "study_id": c["study_id"],
        "diagnostics": diag,
        "observed": obs,
        "permutation": {
            "B": B,
            "seed": seed,
            "invalid_replicates": invalid,
            "state_increment": inc,
            "state_gain": state,
            "collapsed_gain": base,
        },
        "primary_supported": bool(supported),
        "interpretation_key": "attenuation_PASS" if supported else "attenuation_FAIL",
        "interpretation": c["interpretation_matrix"]["attenuation_PASS" if supported else "attenuation_FAIL"],
        "claim_boundary": c["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Nyctalus support-matched HMM-state attribution v1",
        "",
        "**POST-OUTCOME MECHANISM LOCALIZATION; NOT CONFIRMATORY REPLICATION.**",
        "",
        "Both models use the same ARM/COM event pool and are scored on exactly the same HMM-state-supported target events.",
        "",
        f"- n: **{obs['eligible_individuals']}**",
        f"- support-matched collapsed gain: **{obs['collapsed_gain']:+.5f}**",
        f"- HMM-state-conditioned gain: **{obs['state_gain']:+.5f}**",
        f"- paired state increment: **{obs['state_increment']:+.5f}**",
        f"- null-centered paired increment: **{inc['observed_minus_null_mean']:+.5f}**",
        f"- one-sided p(null <= observed): **{inc['p_null_le_observed']:.4f}**",
        f"- frozen attribution verdict: **{'PASS' if supported else 'FAIL'}**",
        "",
        "Secondary support-matched calibration:",
        f"- collapsed calibrated excess: **{base['observed_minus_null_mean']:+.5f}**, p_upper={base['p_null_ge_observed']:.4f}",
        f"- state calibrated excess: **{state['observed_minus_null_mean']:+.5f}**, p_upper={state['p_null_ge_observed']:.4f}",
        "",
        c["interpretation_matrix"]["attenuation_PASS" if supported else "attenuation_FAIL"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "n": obs["eligible_individuals"],
        "collapsed_gain": obs["collapsed_gain"],
        "state_gain": obs["state_gain"],
        "state_increment": obs["state_increment"],
        "calibrated_state_increment": inc["observed_minus_null_mean"],
        "p_lower": inc["p_null_le_observed"],
        "collapsed_calibrated_excess": base["observed_minus_null_mean"],
        "collapsed_p_upper": base["p_null_ge_observed"],
        "state_calibrated_excess": state["observed_minus_null_mean"],
        "state_p_upper": state["p_null_ge_observed"],
        "supported": supported,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
