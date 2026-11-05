"""Aggregate-only comparison of the pinned author release with full discovery GPS."""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

DISCOVERY_SHA = '8ec5b7cce94abe526dee08b1662f57d2d9022b42e7c4d067672b43454774e1e0'
MAINE_SHA = '2c7f1651235dbc4d411bee524393d91a761fd493751c845ac53eae223501e996'

def records(path, expected, fields):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('Source digest mismatch')
    with path.open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            try:
                animal, time, lat, lon = (row[k].strip() for k in fields)
                t = datetime.fromisoformat(time.replace('Z', '+00:00'))
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                lat, lon = float(lat), float(lon)
                if not animal or not math.isfinite(lat + lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError('Invalid position')
                yield animal, t.astimezone(timezone.utc), lat, lon
            except (ValueError, KeyError):
                yield None

def audit(discovery, candidate):
    original = list(records(discovery, DISCOVERY_SHA, ('individual-local-identifier', 'timestamp', 'location-lat', 'location-long')))
    maine = list(records(candidate, MAINE_SHA, ('BirdID', 'timestamp', 'location_lat', 'location_long')))
    a = [r for r in original if r is not None]
    b = [r for r in maine if r is not None]
    if not a or not b:
        raise ValueError('No comparable records')
    exact = {(t, lat, lon) for _, t, lat, lon in a}
    rounded = {(t, round(lat, 5), round(lon, 5)) for _, t, lat, lon in a}
    latitude_gap = max(0, min(r[2] for r in b) - max(r[2] for r in a), min(r[2] for r in a) - max(r[2] for r in b))
    return {
        'discovery_sha256': DISCOVERY_SHA, 'candidate_sha256': MAINE_SHA,
        'candidate_version': 'author GitHub e639fb66bf27b16d83c72d03faa638a496246ff4; NOT Dryad bytes',
        'comparison_scope': 'all discovery CSV rows, before focal cohort or ecological filtering',
        'discovery_total_rows': len(original), 'discovery_comparable_rows': len(a),
        'discovery_unusable_rows': len(original)-len(a), 'discovery_animals': len({r[0] for r in a}),
        'candidate_total_rows': len(maine), 'candidate_comparable_rows': len(b),
        'candidate_unusable_rows': len(maine)-len(b), 'candidate_animals': len({r[0] for r in b}),
        'candidate_rows_matching_timestamp_and_position': sum((t, lat, lon) in exact for _, t, lat, lon in b),
        'candidate_rows_matching_timestamp_and_position_rounded_5dp': sum((t, round(lat,5), round(lon,5)) in rounded for _, t, lat, lon in b),
        'literal_id_label_intersection_count': len({r[0] for r in a} & {r[0] for r in b}),
        'id_comparison_limit': 'different namespaces; label equality or inequality alone cannot establish animal identity',
        'minimum_spatial_separation_lower_bound_km': 6371*math.radians(latitude_gap),
        'spatial_bound_method': 'latitude envelope gap; a conservative lower bound, not exact nearest-pair distance',
        'interpretation': 'Evaluate together with independent Maine study provenance; absence of matching rows alone is not proof of no shared animals',
        'hypothesis_effect_computed': False,
    }

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--discovery', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = audit(args.discovery, args.candidate)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
