from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import hashlib
import math
from typing import Iterable

import numpy as np


Z_EDGES = (-math.inf, 0.0, 50.0, 100.0, 200.0, 400.0, 800.0, 1600.0, 3200.0, math.inf)


@dataclass(frozen=True)
class Event:
    individual: str
    timestamp: datetime
    cell: tuple[int, int]
    zbin: int
    session: str


def canonical_name(name: str) -> str:
    return "_".join(name.strip().lower().replace("-", "_").replace(" ", "_").split("_"))


def truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def parse_timestamp(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def z_bin(height: float, edges: tuple[float, ...] = Z_EDGES) -> int:
    for i in range(len(edges) - 1):
        if edges[i] <= height < edges[i + 1]:
            return i
    if height == edges[-1]:
        return len(edges) - 2
    raise ValueError(f"height outside z edges: {height}")


def assign_sessions(rows: list[dict], gap_hours: float = 4.0) -> dict[int, str]:
    by_individual: dict[str, list[tuple[int, datetime]]] = defaultdict(list)
    for i, row in enumerate(rows):
        by_individual[row["individual"]].append((i, row["timestamp"]))
    assignment: dict[int, str] = {}
    gap_seconds = gap_hours * 3600.0
    for individual, values in by_individual.items():
        values.sort(key=lambda x: x[1])
        session_index = 0
        previous = None
        for idx, timestamp in values:
            if previous is not None and (timestamp - previous).total_seconds() > gap_seconds:
                session_index += 1
            assignment[idx] = f"{individual}::S{session_index + 1}"
            previous = timestamp
    return assignment


def build_events(
    rows: Iterable[dict[str, str]],
    *,
    projector,
    cell_size_m: float = 5000.0,
    gap_hours: float = 4.0,
    exclude_marked_outliers: bool = True,
    min_session_fixes: int = 50,
    z_edges: tuple[float, ...] = Z_EDGES,
) -> tuple[list[Event], dict]:
    parsed = []
    outliers = 0
    for raw in rows:
        row = {canonical_name(k): ("" if v is None else str(v)) for k, v in raw.items()}
        if exclude_marked_outliers and truthy(row.get("manually_marked_outlier", "")):
            outliers += 1
            continue
        try:
            individual = row.get("individual_local_identifier") or row["individual_id"]
            timestamp = parse_timestamp(row["timestamp"])
            lon = float(row["location_long"])
            lat = float(row["location_lat"])
            height = float(row["height_above_msl"])
        except (KeyError, TypeError, ValueError):
            continue
        if not all(math.isfinite(v) for v in (lon, lat, height)):
            continue
        x, y = projector(lon, lat)
        parsed.append({
            "individual": individual,
            "timestamp": timestamp,
            "cell": (math.floor(x / cell_size_m), math.floor(y / cell_size_m)),
            "zbin": z_bin(height, edges=z_edges),
        })

    assignments = assign_sessions(parsed, gap_hours=gap_hours)
    counts = defaultdict(int)
    for i in range(len(parsed)):
        counts[assignments[i]] += 1
    retained_sessions = {s for s, n in counts.items() if n >= min_session_fixes}
    events = [
        Event(
            individual=row["individual"],
            timestamp=row["timestamp"],
            cell=row["cell"],
            zbin=row["zbin"],
            session=assignments[i],
        )
        for i, row in enumerate(parsed)
        if assignments[i] in retained_sessions
    ]
    meta = {
        "parsed_finite_events": len(parsed),
        "excluded_source_marked_outliers": outliers,
        "retained_events": len(events),
        "retained_sessions": len(retained_sessions),
        "individuals": sorted({e.individual for e in events}),
        "session_counts_by_individual": {
            individual: len({e.session for e in events if e.individual == individual})
            for individual in sorted({e.individual for e in events})
        },
        "fix_counts_by_session": dict(sorted(counts.items())),
    }
    return events, meta


def _smoothed(counts: np.ndarray, alpha: float) -> np.ndarray:
    x = counts.astype(float) + alpha
    return x / x.sum()


def conditional_profile(
    events: Iterable[Event],
    *,
    unit: str,
    alpha: float = 0.5,
    k: int = 9,
) -> dict[tuple[int, int], np.ndarray]:
    if unit not in {"session", "individual"}:
        raise ValueError("unit must be session or individual")
    by_unit_cell: dict[tuple[str, tuple[int, int]], np.ndarray] = {}
    for event in events:
        unit_id = event.session if unit == "session" else event.individual
        key = (unit_id, event.cell)
        if key not in by_unit_cell:
            by_unit_cell[key] = np.zeros(k, dtype=float)
        by_unit_cell[key][event.zbin] += 1

    per_cell: dict[tuple[int, int], list[np.ndarray]] = defaultdict(list)
    for (_, cell), counts in by_unit_cell.items():
        per_cell[cell].append(_smoothed(counts, alpha))
    return {cell: np.mean(np.stack(probs), axis=0) for cell, probs in per_cell.items()}


def score_session(
    target: list[Event],
    self_training: list[Event],
    population_training: list[Event],
    *,
    alpha: float = 0.5,
    minimum_scored_fixes: int = 50,
    n_z_bins: int = 9,
) -> dict:
    p_self = conditional_profile(self_training, unit="session", alpha=alpha, k=n_z_bins)
    p_pop = conditional_profile(population_training, unit="individual", alpha=alpha, k=n_z_bins)
    supported = [e for e in target if e.cell in p_self and e.cell in p_pop]
    if len(supported) < minimum_scored_fixes:
        return {
            "evaluable": False,
            "scored_fixes": len(supported),
            "target_fixes": len(target),
            "coverage": len(supported) / len(target) if target else 0.0,
            "gain_nats_per_fix": None,
        }
    values = [
        math.log(float(p_self[e.cell][e.zbin])) - math.log(float(p_pop[e.cell][e.zbin]))
        for e in supported
    ]
    return {
        "evaluable": True,
        "scored_fixes": len(supported),
        "target_fixes": len(target),
        "coverage": len(supported) / len(target),
        "gain_nats_per_fix": float(np.mean(values)),
    }


def leave_one_session_out(events: list[Event], *, alpha: float = 0.5, minimum_scored_fixes: int = 50, n_z_bins: int = 9) -> dict:
    sessions = sorted({e.session for e in events})
    by_session = {s: [e for e in events if e.session == s] for s in sessions}
    results = []
    for session, target in by_session.items():
        individual = target[0].individual
        self_training = [
            e for e in events
            if e.individual == individual and e.session != session
        ]
        population_training = [e for e in events if e.individual != individual]
        other_sessions = {e.session for e in self_training}
        if not other_sessions:
            results.append({
                "session": session,
                "individual": individual,
                "evaluable": False,
                "reason": "no_other_session_for_same_individual",
                "target_fixes": len(target),
            })
            continue
        scored = score_session(
            target, self_training, population_training,
            alpha=alpha, minimum_scored_fixes=minimum_scored_fixes, n_z_bins=n_z_bins,
        )
        scored.update({
            "session": session,
            "individual": individual,
            "self_training_sessions": len(other_sessions),
        })
        results.append(scored)

    per_individual = {}
    for individual in sorted({e.individual for e in events}):
        gains = [
            r["gain_nats_per_fix"] for r in results
            if r.get("individual") == individual and r.get("evaluable") and r.get("gain_nats_per_fix") is not None
        ]
        per_individual[individual] = {
            "evaluable_sessions": len(gains),
            "mean_gain_nats_per_fix": float(np.mean(gains)) if gains else None,
            "positive_session_fraction": float(np.mean(np.array(gains) > 0.0)) if gains else None,
        }

    eligible_individual_gains = [
        v["mean_gain_nats_per_fix"] for v in per_individual.values()
        if v["mean_gain_nats_per_fix"] is not None
    ]
    return {
        "session_results": results,
        "individual_results": per_individual,
        "eligible_individual_count": len(eligible_individual_gains),
        "equal_individual_mean_gain_nats_per_fix": (
            float(np.mean(eligible_individual_gains)) if eligible_individual_gains else None
        ),
        "positive_individual_fraction": (
            float(np.mean(np.array(eligible_individual_gains) > 0.0))
            if eligible_individual_gains else None
        ),
    }


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()
