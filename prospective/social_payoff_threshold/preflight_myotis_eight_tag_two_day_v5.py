#!/usr/bin/env python3
"""Eight pre-frozen OSF tagged-bat series, categorical RFID/TX support only.

No telemetry timestamps, RSSI or geographical values inspected. Raw IDs are
kept only temporarily for identity equality and NEVER serialized.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from preflight_myotis_two_day_categorical_v4 import categorical_file

FILE_PAIRS=(
 ("0A62","698dad850d35ac498ec72cd3","698dadb876b09fd62fe255fe"),
 ("4ECA","698dad87ab12904856dfcaed","698dadb80d35ac498ec72cfe"),
 ("AC37","698dad880d35ac498ec72cd5","698dadb78ef9cd34ebdfd42d"),
 ("A42D","698dad88ab06d8ff5ae255b6","698dadb70bd29b8ed4e24ba5"),
 ("922C","698dad89ab12904856dfcaef","698dadb7ab12904856dfcb2d"),
 ("418B","698dad895888d84fdec733b7","698dadb7ab12904856dfcb2b"),
 ("A24D","698dad890d35ac498ec72cd7","698dadb855339dbcd4c731c6"),
 ("663E","698dad8aa731d64729dfc99a","698dadb85888d84fdec733d7")
)


def test():
    assert len(FILE_PAIRS)==8
    assert len({p[0] for p in FILE_PAIRS})==8
    assert len({rid for _,a,b in FILE_PAIRS for rid in (a,b)})==16
    return "PASS_PRE_FROZEN_SIXTEEN_FILE_ALLOWLIST"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--out",default="MYOTIS_2026_EIGHT_BATS_CATEGORICAL_V5.json")
    args=ap.parse_args()
    check=test()
    if args.self_test:
        print(json.dumps({"self_test":check,"bat_values_opened":False}))
        return
    all_ids={"20240515":[],"20240516":[]}
    all_tx={"20240515":[],"20240516":[]}
    results=[]
    n_stable=0
    inaccessible=False
    for prefix,rid15,rid16 in FILE_PAIRS:
        outputs={}
        ids={}
        senders={}
        valid={}
        for day,rid in (("20240515",rid15),("20240516",rid16)):
            name=f"{prefix}_{day}.csv"
            receipt,rfids,txs=categorical_file(name,rid,day)
            outputs[day]={
              "source_identity_ok":receipt.get("source_metadata_ok"),
              "source_status":receipt.get("status"),
              "technical_row_count":receipt.get("n_technical_rows"),
              "unique_rfid_count":receipt.get("n_distinct_rfid_values"),
              "unique_tx_count":receipt.get("n_distinct_tx_values"),
              "date_within_sampling_night":receipt.get("all_civil_dates_within_sampling_night"),
              "missing_rfid_count":receipt.get("n_missing_rfid"),
              "missing_tx_count":receipt.get("n_missing_tx"),
              "source_sha256":receipt.get("sha256_raw_source"),
            }
            ids[day]=rfids
            senders[day]=txs
            if rfids is not None and txs is not None:
                all_ids[day].extend(rfids)
                all_tx[day].extend(txs)
            else:inaccessible=True
            valid[day]=(rfids is not None and txs is not None and
                len(rfids)==1 and len(txs)==1 and
                receipt.get("n_missing_rfid")==0 and
                receipt.get("n_missing_tx")==0 and
                receipt.get("all_civil_dates_within_sampling_night") is True and
                receipt.get("n_technical_rows",0)>0)
        stable=bool(all(valid.values()) and ids["20240515"]==ids["20240516"]
                    and senders["20240515"]==senders["20240516"])
        n_stable+=int(stable)
        results.append({"public_series_label":prefix,
                        "stable_rfid_and_tx_across_two_nights":stable,
                        "dates":outputs})
    n_unique={day:len(set(all_ids[day])) for day in all_ids}
    n_unique_tx={day:len(set(all_tx[day])) for day in all_tx}
    all_distinct=all(n_unique[day]==8 and n_unique_tx[day]==8 for day in all_ids)
    if inaccessible: status="STOP_SOURCE_FILE_INACCESSIBLE"
    elif n_stable==8 and all_distinct:
        status="PASS_EIGHT_DISTINCT_CROSS_NIGHT_TAGS_CATEGORICAL_ONLY"
    elif n_stable==8 and not all_distinct:
        status="STOP_INCONSISTENT_BAT_TAG_IDENTITY"
    else:
        status="HOLD_PARTIAL_STABLE_BAT_SUPPORT"
    out={
      "source_doi":"10.1002/ece3.73604",
      "source_osf_id":"sg6dz",
      "contract":"MYOTIS_2026_EIGHT_TAG_TWO_NIGHT_CATEGORICAL_CONTRACT_V5.md",
      "status":status,
      "fixed_original_tag_series_count":8,
      "files_accessed_categorical_only":16,
      "n_tag_series_stable_both_nights":n_stable,
      "distinct_rfid_by_date":n_unique,
      "distinct_tx_by_date":n_unique_tx,
      "same_dyad_multinight_co_detection_verified":False,
      "raw_rfid_or_transmitter_values_logged":False,
      "RSSI_coordinates_or_timestamps_inspected":False,
      "prey_capture_or_3d_outcomes_computed":False,
      "source_series":results,
      "synthetic_self_test":check
    }
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
       "status":status,
       "n_series_stable":n_stable,
       "distinct_rfid_per_day":n_unique,
       "distinct_tx_per_day":n_unique_tx,
       "raw_animal_ids_printed":False,
       "behavioral_outcomes_opened":False
    },sort_keys=True))


if __name__=="__main__":main()
