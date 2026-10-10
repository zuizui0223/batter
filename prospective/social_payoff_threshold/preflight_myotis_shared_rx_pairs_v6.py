#!/usr/bin/env python3
"""Categorical RX/receiver-footprint support across exact 8 bats x 2 nights.

No event timestamps, RSSI, lat/lon, dyad, prey, or behavioral values opened.
This is not a synchronous proximity analysis and contains no ecology p-values.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import urllib.request
from pathlib import Path

from preflight_myotis_eight_tag_two_day_v5 import FILE_PAIRS
from preflight_myotis_two_day_csv_headers_v2 import metadata, opener, UA

SOURCE_SIZE_CAP=1_000_000
DAYS=("20240515","20240516")
HEADER=("timestamp","date","batdate","time","rx","tx","rfid","dyad",
        "rssi","batch","box","grid_sn","lon_sn","lat_sn","records")


def source_receivers(name,rid):
    source=metadata(name,rid)
    if not source["ok"]:
        return None, {"status":"STOP_SOURCE_IDENTITY","metadata_http":source["http_status"]}
    try:
        request=urllib.request.Request(
            f"https://osf.io/download/{rid}/",
            headers={"User-Agent":UA,"Accept":"text/csv,application/octet-stream"})
        with opener().open(request,timeout=24) as response:
            raw=response.read(SOURCE_SIZE_CAP+1)
        if len(raw)>SOURCE_SIZE_CAP:
            raise ValueError("SOURCE_TOO_LARGE")
        reader=csv.reader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
        header=tuple(s.strip().lower() for s in next(reader))
        if header!=HEADER:
            raise ValueError("UNEXPECTED_SOURCE_HEADER")
        j=header.index("rx")
        stations=set()
        n=missing=0
        for cells in reader:
            if not cells:
                continue
            if len(cells)!=len(header):
                raise ValueError("BAD_CSV_ROW_LENGTH")
            # The sole original DATA value accessed is the rx/receiver
            # candidate string. No other cell indices are evaluated.
            key=cells[j].strip()
            n+=1
            if key:
                stations.add(key)
            else:
                missing+=1
        if n==0:
            raise ValueError("NO_RECEIVER_OBSERVATIONS")
        return stations, {
            "status":"SOURCE_RX_CATEGORICAL_ONLY",
            "technical_rows":n,
            "missing_rx_rows":missing,
            "distinct_receiver_keys":len(stations),
            "original_source_sha256":hashlib.sha256(raw).hexdigest()
        }
    except Exception as e:
        return None,{"status":"STOP_RX_COLUMN_ACCESS_OR_STRUCTURE",
                     "error_type":type(e).__name__}


def synthetic_self_test():
    demo={
      "20240515":{"A":{"x","z"},"B":{"y","z"},"C":{"u"}},
      "20240516":{"A":{"q","z"},"B":{"v","z"},"C":{"u"}},
    }
    pairs=list(itertools.combinations(("A","B","C"),2))
    both=sum(bool(demo[DAYS[0]][a]&demo[DAYS[0]][b]) and
             bool(demo[DAYS[1]][a]&demo[DAYS[1]][b])
             for a,b in pairs)
    strict=sum(bool((demo[DAYS[0]][a]&demo[DAYS[0]][b])&
                    (demo[DAYS[1]][a]&demo[DAYS[1]][b]))
               for a,b in pairs)
    assert both==1 and strict==1
    assert len(FILE_PAIRS)==8
    return "PASS_FAKE_PAIR_INTERSECTION"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--out",default="MYOTIS_2026_SHARED_RECEIVER_PAIR_V6.json")
    opts=ap.parse_args()
    check=synthetic_self_test()
    if opts.self_test:
        print(json.dumps({"test":check,"bat_behavior_opened":False}))
        return

    data={d:{} for d in DAYS}
    source_summaries={}
    hard_stop=False
    for prefix,id15,id16 in FILE_PAIRS:
        for day,rid in zip(DAYS,(id15,id16)):
            receiver_keys,detail=source_receivers(f"{prefix}_{day}.csv",rid)
            source_summaries[f"{prefix}_{day}"]={
              **detail, "public_filename_prefix":prefix,"sampling_night":day
            }
            if receiver_keys is None:
                hard_stop=True
            else:
                data[day][prefix]=receiver_keys

    report={"source_doi":"10.1002/ece3.73604",
            "source":"OSF sg6dz/proximity_UD/data/sn_prox",
            "contract":"MYOTIS_2026_RECEIVER_PAIR_TWO_NIGHT_CATEGORICAL_CONTRACT_V6.md",
            "source_files_attempted":len(FILE_PAIRS)*2,
            "fixed_bat_series":len(FILE_PAIRS),
            "original_rfid_cross_night_gate":"PASS_EIGHT_DISTINCT_CROSS_NIGHT_TAGS_CATEGORICAL_ONLY",
            "source_structural_summaries":source_summaries,
            "individual_receiver_ids_logged":False,
            "timestamp_rssi_latitude_longitude_dyad_or_fitness_read":False,
            "actual_simultaneous_encounters_verified":False,
            "co_detection_p_values":0,
            "synthetic_self_test":check}
    if hard_stop:
        report["status"]="STOP_RECEIVER_SOURCE_OR_SCHEMA_INCOMPLETE"
    elif any(not data[d][prefix] for d in DAYS for prefix,_,_ in FILE_PAIRS):
        report["status"]="HOLD_INCOMPLETE_RECEIVER_COVERAGE"
    else:
        bat_prefixes=[p for p,_,_ in FILE_PAIRS]
        pairs=list(itertools.combinations(bat_prefixes,2))
        pair_night={
          d:sum(bool(data[d][a]&data[d][b]) for a,b in pairs)
          for d in DAYS
        }
        pair_both=sum(bool(data[DAYS[0]][a]&data[DAYS[0]][b]) and
                      bool(data[DAYS[1]][a]&data[DAYS[1]][b])
                      for a,b in pairs)
        pair_identical_site=sum(bool((data[DAYS[0]][a]&data[DAYS[0]][b])&
                                  (data[DAYS[1]][a]&data[DAYS[1]][b]))
                                for a,b in pairs)
        distinct_stations={
          d:len(set().union(*(data[d][p] for p in bat_prefixes)))
          for d in DAYS}
        station_overlap=len(set().union(*(data[DAYS[0]][p] for p in bat_prefixes))
                          &set().union(*(data[DAYS[1]][p] for p in bat_prefixes)))
        report.update({
          "n_possible_unordered_bat_pairs":len(pairs),
          "n_bat_series_with_receiver_support_per_night":{
              d:sum(bool(data[d][p]) for p in bat_prefixes) for d in DAYS},
          "n_distinct_rx_candidates_per_night":distinct_stations,
          "n_receiver_ids_in_both_night_rosters":station_overlap,
          "n_pairs_sharing_any_receiver_per_night":pair_night,
          "n_pairs_with_some_shared_receiver_either_on_each_night":pair_both,
          "n_pairs_with_same_receiver_shared_on_both_nights":pair_identical_site,
          "status":("PASS_SHARED_RECEIVER_STRUCTURE_BOTH_NIGHTS_ONLY"
                    if pair_both>0 else
                    "HOLD_NO_CROSS_NIGHT_SHARED_RECEIVER_PAIR")
        })
    Path(opts.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",
                              encoding="utf-8")
    print(json.dumps({
       "status":report["status"],
       "pairs_potential":report.get("n_possible_unordered_bat_pairs"),
       "pairs_with_any_shared_receiver_each_night":report.get(
           "n_pairs_with_some_shared_receiver_either_on_each_night"),
       "pairs_with_same_receiver_both_nights":report.get(
           "n_pairs_with_same_receiver_shared_on_both_nights"),
       "receiver_roster_sizes":report.get("n_distinct_rx_candidates_per_night"),
       "no_times_or_coords_or_outcomes_opened":True,
    },sort_keys=True))


if __name__=="__main__":
    main()
