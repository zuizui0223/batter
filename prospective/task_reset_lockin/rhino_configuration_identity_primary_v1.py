#!/usr/bin/env python3
"""Frozen configuration-conditioned individual identity primaries for Rhinolophus nippon.

Implements:
- Primary A: within-configuration literal-route identity.
- Primary B: cross-configuration transfer of individual movement policy.

Miniopterus values are never opened.
Pulse values are never used.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import io
import json
import math
import re
import urllib.request

import numpy as np

API = "https://api.figshare.com/v2/articles/29209493"
UA = "batter-rhino-configuration-identity-primary/1.0"
PAT = re.compile(r"^Env(?P<env>\d+)_Bat(?P<bat>[A-Za-z]+)_no(?P<trial>.+)\.csv$")
RHINO_MIN = 55033853
RHINO_MAX = 55033985

FEATURES = [
    "median_speed",
    "p90_speed",
    "median_abs_vertical_speed",
    "p90_abs_vertical_speed",
    "median_abs_horizontal_turn_rate",
    "p90_abs_horizontal_turn_rate",
    "path_efficiency",
    "vertical_range",
]

A_NPERM = 9999
A_SEED = 202610042201
B_NPERM = 9999
B_SEED = 202610042202
B_MIN_VALID_PERM = 9500


def get_article():
    req = urllib.request.Request(API, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def get_bytes(url, maxn):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/csv,*/*"})
    with urllib.request.urlopen(req, timeout=90) as r:
        b = r.read(maxn + 1)
    if len(b) > maxn:
        raise RuntimeError("download budget exceeded")
    return b


def parse_xyz(b):
    txt = io.StringIO(b.decode("utf-8-sig", errors="strict"))
    reader = csv.DictReader(txt)
    expected = ["Time (Seconds)", "X", "Y", "Z", "pulse"]
    if reader.fieldnames != expected:
        raise RuntimeError(f"header drift: {reader.fieldnames}")
    vals = []
    for row in reader:
        try:
            vals.append((
                float(row["Time (Seconds)"]),
                float(row["X"]),
                float(row["Y"]),
                float(row["Z"]),
            ))
        except Exception:
            vals.append((math.nan, math.nan, math.nan, math.nan))
    if not vals:
        return np.empty((0, 4), dtype=float)
    arr = np.asarray(vals, dtype=float)
    arr = arr[np.all(np.isfinite(arr), axis=1)]
    if len(arr) == 0:
        return arr
    order = np.argsort(arr[:, 0], kind="mergesort")
    arr = arr[order]
    _, first_idx = np.unique(arr[:, 0], return_index=True)
    arr = arr[np.sort(first_idx)]
    return arr


def route_and_features(arr):
    out = {
        "route_valid": False,
        "feature_valid": False,
        "route101": None,
        "features": None,
        "n_rows": int(len(arr)),
        "duration": None,
        "path_length": None,
        "positive_dt_intervals": 0,
    }
    if len(arr) < 2:
        return out
    t = arr[:, 0]
    xyz = arr[:, 1:4]
    duration = float(t[-1] - t[0])
    dxyz = np.diff(xyz, axis=0)
    seg = np.linalg.norm(dxyz, axis=1)
    path = float(np.sum(seg[np.isfinite(seg)]))
    dt = np.diff(t)
    posdt = dt > 0
    out["duration"] = duration
    out["path_length"] = path
    out["positive_dt_intervals"] = int(np.sum(posdt))
    route_valid = bool(len(arr) >= 100 and duration > 0 and path > 0 and np.isfinite(path))
    out["route_valid"] = route_valid
    if not route_valid:
        return out

    # Frozen arc-length interpolation. Zero-length steps are removed from the
    # interpolation abscissa by retaining the first occurrence of each
    # cumulative-distance value.
    cum = np.concatenate(([0.0], np.cumsum(seg)))
    keep = np.concatenate(([True], np.diff(cum) > 0))
    cum2 = cum[keep]
    xyz2 = xyz[keep]
    if len(cum2) < 2 or cum2[-1] <= 0:
        out["route_valid"] = False
        return out
    s = cum2 / cum2[-1]
    grid = np.linspace(0.0, 1.0, 101)
    route101 = np.column_stack([np.interp(grid, s, xyz2[:, k]) for k in range(3)])
    out["route101"] = route101

    if np.sum(posdt) < 50:
        return out

    dxyzp = dxyz[posdt]
    dtp = dt[posdt]
    speed = np.linalg.norm(dxyzp, axis=1) / dtp
    vz = np.abs(dxyzp[:, 2] / dtp)

    dx = dxyz[:, 0]
    dy = dxyz[:, 1]
    hmag = np.hypot(dx, dy)
    heading = np.full(len(dt), np.nan, dtype=float)
    good = (dt > 0) & (hmag > 0) & np.isfinite(hmag)
    heading[good] = np.arctan2(dy[good], dx[good])
    turns = []
    for k in range(len(heading) - 1):
        if not (np.isfinite(heading[k]) and np.isfinite(heading[k + 1])):
            continue
        dt_turn = 0.5 * (dt[k] + dt[k + 1])
        if not (np.isfinite(dt_turn) and dt_turn > 0):
            continue
        dtheta = math.atan2(
            math.sin(heading[k + 1] - heading[k]),
            math.cos(heading[k + 1] - heading[k]),
        )
        turns.append(abs(dtheta) / dt_turn)
    turns = np.asarray(turns, dtype=float)

    net = float(np.linalg.norm(xyz[-1] - xyz[0]))
    eff = net / path if path > 0 else math.nan
    vrange = float(np.max(xyz[:, 2]) - np.min(xyz[:, 2]))
    feats = np.array([
        np.median(speed),
        np.percentile(speed, 90),
        np.median(vz),
        np.percentile(vz, 90),
        np.median(turns) if len(turns) else np.nan,
        np.percentile(turns, 90) if len(turns) else np.nan,
        eff,
        vrange,
    ], dtype=float)
    if np.all(np.isfinite(feats)):
        out["feature_valid"] = True
        out["features"] = feats
    return out


def load_rhino():
    article = get_article()
    traj = []
    for f in article.get("files") or []:
        fid = int(f["id"])
        name = f.get("name") or ""
        m = PAT.match(name)
        if not m or not (RHINO_MIN <= fid <= RHINO_MAX):
            continue
        size = int(f["size"])
        b = get_bytes(f["download_url"], size + 4096)
        if len(b) != size:
            raise RuntimeError(f"size mismatch {name}")
        md5 = hashlib.md5(b).hexdigest()
        expected = f.get("computed_md5") or f.get("supplied_md5")
        if expected and md5 != expected:
            raise RuntimeError(f"md5 mismatch {name}")
        arr = parse_xyz(b)
        rf = route_and_features(arr)
        traj.append({
            "id": fid,
            "name": name,
            "env": int(m.group("env")),
            "bat": m.group("bat"),
            "trial": m.group("trial"),
            **rf,
        })
    if len(traj) != 45:
        raise RuntimeError(f"expected 45 Rhino trajectories, got {len(traj)}")
    return traj


def route_distance(a, b):
    return float(np.mean(np.linalg.norm(a - b, axis=1)))


def primary_a(traj):
    rt = [r for r in traj if r["route_valid"]]
    envs = sorted(set(r["env"] for r in rt))

    env_info = {}
    eligible_envs = []
    for e in envs:
        rr = [r for r in rt if r["env"] == e]
        counts = collections.Counter(r["bat"] for r in rr)
        repeated = sorted([b for b, n in counts.items() if n >= 2])
        if len(repeated) >= 3:
            eligible_envs.append(e)
        env_info[e] = {"rr": rr, "counts": counts, "target_labels": repeated}

    if len(eligible_envs) < 2:
        return {"verdict": "STOP_A_COORDINATE_SUPPORT", "eligible_environments": eligible_envs}

    # Precompute pairwise distances for each eligible environment.
    D = {}
    for e in eligible_envs:
        rr = env_info[e]["rr"]
        n = len(rr)
        mat = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                d = route_distance(rr[i]["route101"], rr[j]["route101"])
                mat[i, j] = mat[j, i] = d
        D[e] = mat

    def stat_for_labels(label_maps):
        env_means = []
        bat_env_means = collections.defaultdict(list)
        target_rows = []
        for e in eligible_envs:
            rr = env_info[e]["rr"]
            labels = label_maps[e]
            counts = collections.Counter(labels)
            target_labels = sorted([b for b, n in counts.items() if n >= 2])
            per_bat = collections.defaultdict(list)
            for i, lab in enumerate(labels):
                if lab not in target_labels:
                    continue
                self_idx = [j for j, x in enumerate(labels) if x == lab and j != i]
                donor_labels = sorted(set(labels) - {lab})
                if not self_idx or not donor_labels:
                    continue
                dself = float(np.mean([D[e][i, j] for j in self_idx]))
                donor_means = []
                for dl in donor_labels:
                    idx = [j for j, x in enumerate(labels) if x == dl]
                    if idx:
                        donor_means.append(float(np.mean([D[e][i, j] for j in idx])))
                if not donor_means:
                    continue
                dother = float(np.mean(donor_means))
                a = dother - dself
                per_bat[lab].append(a)
                target_rows.append((e, lab, i, a, dself, dother))
            batmeans = {b: float(np.mean(v)) for b, v in per_bat.items() if v}
            if not batmeans:
                return None
            env_mean = float(np.mean(list(batmeans.values())))
            env_means.append(env_mean)
            for b, v in batmeans.items():
                bat_env_means[b].append(v)
        if len(env_means) != len(eligible_envs):
            return None
        species_stat = float(np.mean(env_means))
        bat_means = {b: float(np.mean(v)) for b, v in bat_env_means.items() if v}
        return species_stat, bat_means, target_rows, env_means

    observed_labels = {e: [r["bat"] for r in env_info[e]["rr"]] for e in eligible_envs}
    obs = stat_for_labels(observed_labels)
    if obs is None:
        return {"verdict": "STOP_A_OBSERVED_SUPPORT"}
    A_obs, bat_means, target_rows, env_means = obs

    rng = np.random.default_rng(A_SEED)
    null = np.empty(A_NPERM, dtype=float)
    for p in range(A_NPERM):
        maps = {}
        for e in eligible_envs:
            labs = np.array(observed_labels[e], dtype=object)
            maps[e] = list(rng.permutation(labs))
        s = stat_for_labels(maps)
        if s is None:
            raise RuntimeError("Primary A fixed-count permutation unexpectedly invalid")
        null[p] = s[0]

    pval = float((1 + np.sum(null >= A_obs)) / (A_NPERM + 1))
    positive = sum(v > 0 for v in bat_means.values())
    nbat = len(bat_means)
    frac = positive / nbat if nbat else math.nan
    support = bool(A_obs > 0 and pval <= 0.05 and frac >= 0.70)

    targets_out = []
    for e, lab, i, a, ds, do in target_rows:
        targets_out.append({
            "env": e,
            "bat": lab,
            "name": env_info[e]["rr"][i]["name"],
            "A": a,
            "D_self": ds,
            "D_other": do,
        })

    return {
        "verdict": "PASS_A_IDENTITY" if support else "FAIL_A_IDENTITY",
        "eligible_environments": eligible_envs,
        "A_obs": A_obs,
        "environment_means": {str(e): v for e, v in zip(eligible_envs, env_means)},
        "bat_means": bat_means,
        "positive_bats": positive,
        "n_evaluable_bats": nbat,
        "positive_fraction": frac,
        "permutation_n": A_NPERM,
        "seed": A_SEED,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "p_one_sided": pval,
        "targets": targets_out,
    }


def build_b_structure(traj):
    ft = [r for r in traj if r["feature_valid"]]
    envs = sorted(set(r["env"] for r in ft))
    usable = []
    for e in envs:
        rr = [r for r in ft if r["env"] == e]
        if len(rr) >= 2 and len(set(r["bat"] for r in rr)) >= 2:
            usable.append(e)

    retained_idx = []
    dropped = []
    stats = {}
    for e in usable:
        rr = [r for r in ft if r["env"] == e]
        mat = np.vstack([r["features"] for r in rr])
        mu = np.mean(mat, axis=0)
        sd = np.std(mat, axis=0, ddof=1)
        stats[e] = (mu, sd)

    for k in range(len(FEATURES)):
        bad = [e for e in usable if not (np.isfinite(stats[e][1][k]) and stats[e][1][k] > 0)]
        if bad:
            dropped.append({"feature": FEATURES[k], "bad_envs": bad})
        else:
            retained_idx.append(k)

    retained = [FEATURES[k] for k in retained_idx]
    if len(retained) < 6:
        return {
            "verdict": "STOP_B_FEATURE_SD",
            "usable_envs": usable,
            "retained_features": retained,
            "dropped_features": dropped,
        }, None

    # z-score trajectories in usable environments.
    rows = []
    for r in ft:
        e = r["env"]
        if e not in usable:
            continue
        mu, sd = stats[e]
        z = (r["features"][retained_idx] - mu[retained_idx]) / sd[retained_idx]
        rows.append({**r, "z": z})

    bats = sorted(set(r["bat"] for r in rows))
    env_presence = {
        b: sorted(set(r["env"] for r in rows if r["bat"] == b))
        for b in bats
    }
    candidates = sorted([b for b, es in env_presence.items() if len(es) >= 3])

    # Fixed observed target set and support.
    targets = []
    support_by_bat = collections.Counter()
    for idx, r in enumerate(rows):
        b, e = r["bat"], r["env"]
        if b not in candidates:
            continue
        own_other = [ee for ee in env_presence[b] if ee != e]
        donors = []
        for j in bats:
            if j == b:
                continue
            jes = [ee for ee in env_presence[j] if ee != e]
            if len(jes) >= 2:
                donors.append(j)
        if len(own_other) >= 2 and len(donors) >= 2:
            targets.append(idx)
            support_by_bat[b] += 1

    pass_support = (
        len(candidates) >= 3 and
        all(support_by_bat[b] >= 1 for b in candidates) and
        all(
            len([ee for ee in env_presence[rows[i]["bat"]] if ee != rows[i]["env"]]) >= 2
            for i in targets
        )
    )
    if not pass_support:
        return {
            "verdict": "STOP_B_TARGET_SUPPORT",
            "usable_envs": usable,
            "retained_features": retained,
            "dropped_features": dropped,
            "candidate_bats": candidates,
            "support_by_bat": dict(support_by_bat),
        }, None

    support = {
        "verdict": "PASS_B_OPEN_OUTCOME",
        "usable_envs": usable,
        "retained_features": retained,
        "dropped_features": dropped,
        "candidate_bats": candidates,
        "support_by_bat": dict(support_by_bat),
        "n_targets": len(targets),
    }
    return support, (rows, bats, env_presence, candidates, targets)


def env_cluster_centroids(rows, labels_by_cluster=None):
    """Return centroid per (environment, assigned label).

    labels_by_cluster maps (env, original bat) -> assigned bat. If None, identity.
    """
    tmp = collections.defaultdict(list)
    for r in rows:
        old = r["bat"]
        e = r["env"]
        lab = labels_by_cluster[(e, old)] if labels_by_cluster is not None else old
        tmp[(e, lab)].append(r["z"])
    return {k: np.mean(np.vstack(v), axis=0) for k, v in tmp.items()}


def b_stat(rows, bats, targets, labels_by_cluster=None):
    cent = env_cluster_centroids(rows, labels_by_cluster)

    # presence of assigned labels by environment
    presence = collections.defaultdict(set)
    for (e, lab) in cent:
        presence[lab].add(e)

    target_values = []
    per_label = collections.defaultdict(list)

    for idx in targets:
        r = rows[idx]
        e = r["env"]
        old = r["bat"]
        lab = labels_by_cluster[(e, old)] if labels_by_cluster is not None else old

        own_envs = sorted([ee for ee in presence[lab] if ee != e])
        if len(own_envs) < 2:
            return None
        own_env_centroids = [cent[(ee, lab)] for ee in own_envs if (ee, lab) in cent]
        if len(own_env_centroids) < 2:
            return None
        own = np.mean(np.vstack(own_env_centroids), axis=0)

        donors = []
        for j in bats:
            if j == lab:
                continue
            jes = sorted([ee for ee in presence[j] if ee != e])
            if len(jes) < 2:
                continue
            jc = [cent[(ee, j)] for ee in jes if (ee, j) in cent]
            if len(jc) < 2:
                continue
            donors.append(np.mean(np.vstack(jc), axis=0))
        if len(donors) < 2:
            return None

        z = r["z"]
        dself = float(np.linalg.norm(z - own))
        dother = float(np.mean([np.linalg.norm(z - d) for d in donors]))
        kval = dother - dself
        target_values.append((idx, lab, kval, dself, dother))
        per_label[lab].append(kval)

    if not target_values or not per_label:
        return None
    batmeans = {b: float(np.mean(v)) for b, v in per_label.items() if v}
    species = float(np.mean(list(batmeans.values())))
    return species, batmeans, target_values


def primary_b(traj):
    support, obj = build_b_structure(traj)
    if obj is None:
        return support
    rows, bats, env_presence, candidates, targets = obj

    obs = b_stat(rows, bats, targets, None)
    if obs is None:
        return {**support, "verdict": "STOP_B_OBSERVED_SUPPORT"}
    K_obs, bat_means, target_values = obs

    # Environment-specific cluster labels.
    env_clusters = {}
    for e in support["usable_envs"]:
        labels = sorted(set(r["bat"] for r in rows if r["env"] == e))
        env_clusters[e] = labels

    rng = np.random.default_rng(B_SEED)
    null = []
    for _ in range(B_NPERM):
        mapping = {}
        for e, labels in env_clusters.items():
            perm = list(rng.permutation(np.array(labels, dtype=object)))
            for old, new in zip(labels, perm):
                mapping[(e, old)] = str(new)
        s = b_stat(rows, bats, targets, mapping)
        if s is not None:
            null.append(s[0])

    nvalid = len(null)
    if nvalid < B_MIN_VALID_PERM:
        return {
            **support,
            "verdict": "STOP_RANDOMIZATION_SUPPORT",
            "K_obs": K_obs,
            "valid_permutations": nvalid,
            "requested_permutations": B_NPERM,
        }

    null = np.asarray(null, dtype=float)
    pval = float((1 + np.sum(null >= K_obs)) / (1 + nvalid))
    positive = sum(v > 0 for v in bat_means.values())
    nbat = len(bat_means)
    frac = positive / nbat if nbat else math.nan
    supported = bool(K_obs > 0 and pval <= 0.05 and frac >= 0.70)

    targets_out = []
    for idx, lab, kval, ds, do in target_values:
        r = rows[idx]
        targets_out.append({
            "name": r["name"],
            "observed_bat": r["bat"],
            "env": r["env"],
            "K": kval,
            "D_self": ds,
            "D_other": do,
        })

    return {
        **support,
        "verdict": "PASS_B_TRANSFER" if supported else "FAIL_B_TRANSFER",
        "K_obs": K_obs,
        "bat_means": bat_means,
        "positive_bats": positive,
        "n_evaluable_bats": nbat,
        "positive_fraction": frac,
        "requested_permutations": B_NPERM,
        "valid_permutations": nvalid,
        "seed": B_SEED,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "p_one_sided": pval,
        "targets": targets_out,
    }


def main():
    traj = load_rhino()
    A = primary_a(traj)
    B = primary_b(traj)
    out = {
        "contract": "CONFIGURATION_CONDITIONED_IDENTITY_CONTRACT_V1.md",
        "implementation": "ESTIMATOR_IMPLEMENTATION_CLARIFICATION_V1.md",
        "species": "Rhinolophus nippon",
        "miniopterus_numeric_values_opened": False,
        "pulse_values_used": False,
        "n_rhino_trajectories": len(traj),
        "primary_A": A,
        "primary_B": B,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
