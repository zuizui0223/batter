#!/usr/bin/env python3
"""Physics-first no-animal 2x2 acoustic/route gate validator.

Requires REAL independently recorded bench measurements; no bat outcome data,
no ecological power simulations, no p-values. See frozen contract.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

FIELDS = (
    "point_id", "repeat_id", "route_open", "masker_on",
    "target_echo_db_spl", "background_db_spl", "max_peak_db_spl",
    "measured_clearance_m",
)
ARMS = tuple(itertools.product((0, 1), (0, 1)))
STOP_STRUCTURE = "STOP_BENCH_SOURCE_OR_STRUCTURE"
STOP_ACOUSTICS = "STOP_ROUTE_GATE_ACOUSTIC_CONFOUND"
STOP_SAFETY = "STOP_PHYSICAL_SAFETY_OR_REWARD"
PASS = "PASS_PHYSICS_BENCH_ONLY"


class InvalidBench(ValueError):
    pass


def numeric(v, key, *, lower=None, strict_lower=False):
    if isinstance(v, bool):
        raise InvalidBench(f"{key}: boolean passed where numeric expected")
    try:
        z = float(v)
    except (TypeError, ValueError):
        raise InvalidBench(f"{key}: value is not numeric")
    if not math.isfinite(z):
        raise InvalidBench(f"{key}: nonfinite value")
    if lower is not None and (z <= lower if strict_lower else z < lower):
        raise InvalidBench(f"{key}: value outside allowed range")
    return z


def manifest_points(d, label, *, route):
    if not isinstance(d, list) or not d:
        raise InvalidBench(f"{label} must list actual calibrated locations")
    out = {}
    for row in d:
        if not isinstance(row, dict):
            raise InvalidBench(f"{label}: point is not an object")
        name = str(row.get("point_id", "")).strip()
        station = str(row.get("station_id", "")).strip()
        route_id = str(row.get("route_id", route)).strip()
        orient = str(row.get("probe_orientation", "")).strip()
        if not name or not station or not orient:
            raise InvalidBench(f"{label}: point/station/orientation missing")
        if route == "R1":
            if route_id != "R1":
                raise InvalidBench(f"anchor {name} must be canonical R1")
        elif route_id not in ("R2", "R3", "R4"):
            raise InvalidBench(f"alternative {name}: not R2/R3/R4")
        if name in out:
            raise InvalidBench(f"duplicate physical point {name}")
        loc = tuple(numeric(row.get(k), f"{name}.{k}") for k in ("x_m", "y_m", "z_m"))
        out[name] = {"route": route_id, "station": station, "xyz_m": loc,
                     "orientation": orient}
    return out


def load_manifest(info):
    if not isinstance(info, dict):
        raise InvalidBench("manifest is not an object")
    if info.get("mic_calibrated") is not True or info.get("transmitter_calibrated") is not True:
        raise InvalidBench("source microphone/transmitter calibration not verified")
    if not str(info.get("source_id", "")).strip():
        raise InvalidBench("missing source_id")
    source_sha = str(info.get("source_dataset_sha256", ""))
    if len(source_sha) != 64 or any(ch not in "0123456789abcdef" for ch in source_sha):
        raise InvalidBench("source_dataset_sha256 missing or invalid")
    band = info.get("acoustic_band_hz")
    if not isinstance(band, list) or len(band) != 2:
        raise InvalidBench("acoustic_band_hz must have two endpoints")
    a, b = (numeric(z, "acoustic_band_hz", lower=0, strict_lower=True) for z in band)
    if not a < b:
        raise InvalidBench("acoustic_band_hz not increasing")
    floor = info.get("bench_repeat_floor")
    if isinstance(floor, bool) or not isinstance(floor, int) or floor < 3:
        raise InvalidBench("bench_repeat_floor must be an integer >=3 independent setups")
    tol = {}
    for key in ("max_allowed_fixed_point_snr_gate_bias_db",
                "max_allowed_fixed_point_snr_gate_x_masker_interaction_db",
                "max_acceptable_target_loss_db", "min_clearance_m"):
        tol[key] = numeric(info.get(key), key, lower=0, strict_lower=True)
    tol["max_safe_peak_db_spl"] = numeric(info.get("max_safe_peak_db_spl"),
                                          "max_safe_peak_db_spl", lower=0, strict_lower=True)
    anchor_list = info.get("anchor_points")
    if not isinstance(anchor_list, list) or not 2 <= len(anchor_list) <= 25:
        raise InvalidBench("anchor_points must have 2..25 distinct R1 points")
    anchors = manifest_points(anchor_list, "anchor_points", route="R1")
    alts = manifest_points(info.get("alternative_points"), "alternative_points", route="ALT")
    if set(anchors).intersection(alts):
        raise InvalidBench("point_id reused across anchor and alternatives")
    if {x["route"] for x in alts.values()} != {"R2", "R3", "R4"}:
        raise InvalidBench("not all R2/R3/R4 alternative routes mapped")
    stations = {a["station"] for a in anchors.values()}
    if any(x["station"] not in stations for x in alts.values()):
        raise InvalidBench("unmatched station_id in alternative points")
    return anchors, alts, floor, tol, source_sha


def ingest(records, anchors, alts, floor):
    points = {**anchors, **alts}
    seen = {}
    reps = set()
    for i, row in enumerate(records, 2):
        if not set(FIELDS).issubset(row):
            raise InvalidBench(f"row {i}: missing bench data fields")
        point = str(row.get("point_id", "")).strip()
        repeat = str(row.get("repeat_id", "")).strip()
        if not repeat or point not in points:
            raise InvalidBench(f"row {i}: unknown point or repeat ID")
        if row["route_open"] not in ("0", "1") or row["masker_on"] not in ("0", "1"):
            raise InvalidBench(f"row {i}: route/masker is not binary canonical 0/1")
        route, mask = int(row["route_open"]), int(row["masker_on"])
        if point in alts and route != 1:
            raise InvalidBench(f"row {i}: R2-R4 measured with routes nominally closed")
        vals = {key: numeric(row[key], f"row{i}.{key}") for key in FIELDS[4:]}
        if vals["measured_clearance_m"] <= 0:
            raise InvalidBench(f"row{i}: nonpositive safe physical clearance")
        sig = (point, repeat, route, mask)
        if sig in seen:
            raise InvalidBench(f"row{i}: duplicate physical setup+point+arm key")
        seen[sig] = vals
        reps.add(repeat)
    if len(reps) < floor:
        raise InvalidBench(f"only {len(reps)} distinct bench repeats < frozen floor {floor}")
    if not seen:
        raise InvalidBench("no physical bench measurements")
    for point in anchors:
        for repeat in reps:
            missing = [c for c in ARMS if (point, repeat, *c) not in seen]
            if missing:
                raise InvalidBench(f"missing canonical R1 calibration at {point}/{repeat}: {missing}")
    for point in alts:
        for repeat in reps:
            missing = [m for m in (0, 1) if (point, repeat, 1, m) not in seen]
            if missing:
                raise InvalidBench(f"missing R2-R4 soundfield calibration at {point}/{repeat}")
    return seen, sorted(reps)


def calculate(anchors, alts, seen, repeats, tol):
    def get(point, rep, r, m):
        return seen[(point, rep, r, m)]
    def snr(v):
        return v["target_echo_db_spl"] - v["background_db_spl"]
    checks = []
    out = {}
    for point in anchors:
        triples=[]
        for rep in repeats:
            oo = get(point, rep, 1, 0)
            co = get(point, rep, 0, 0)
            om = get(point, rep, 1, 1)
            cm = get(point, rep, 0, 1)
            bias0 = snr(oo) - snr(co)
            bias1 = snr(om) - snr(cm)
            interaction = bias1 - bias0
            target_loss = max(0., co["target_echo_db_spl"] - oo["target_echo_db_spl"],
                             cm["target_echo_db_spl"] - om["target_echo_db_spl"])
            triples.append((bias0, bias1, interaction, target_loss))
            checks.append((point,rep,bias0,bias1,interaction,target_loss))
        out[point] = {
            "max_abs_gate_bias_sham_db": max(abs(v[0]) for v in triples),
            "max_abs_gate_bias_masker_db": max(abs(v[1]) for v in triples),
            "max_abs_gate_x_masker_db": max(abs(v[2]) for v in triples),
            "max_target_echo_loss_open_gate_db": max(v[3] for v in triples),
        }
    maxbias=max(max(abs(v[2]),abs(v[3])) for v in checks)
    maxinter=max(abs(v[4]) for v in checks)
    maxloss=max(v[5] for v in checks)
    allvals=list(seen.values())
    minclearance=min(x["measured_clearance_m"] for x in allvals)
    maxpeak=max(x["max_peak_db_spl"] for x in allvals)
    contam=(maxbias>tol["max_allowed_fixed_point_snr_gate_bias_db"]
            or maxinter>tol["max_allowed_fixed_point_snr_gate_x_masker_interaction_db"]
            or maxloss>tol["max_acceptable_target_loss_db"])
    safety=(minclearance<tol["min_clearance_m"]
            or maxpeak>tol["max_safe_peak_db_spl"])
    # Only within the already-open route field; no claim of animal choice.
    canonical_by_station={}
    for p,attrs in anchors.items():
        canonical_by_station.setdefault(attrs["station"], []).append(p)
    alt_stats=[]
    for p,attrs in alts.items():
        station=attrs["station"]
        for rep in repeats:
            alt_snr=snr(get(p,rep,1,1))
            base=sum(snr(get(q,rep,1,1)) for q in canonical_by_station[station])/len(canonical_by_station[station])
            alt_stats.append({"route":attrs["route"], "station_id":station, "repeat_id":rep,
                              "masked_alt_snr_minus_canonical_db":alt_snr-base})
    # No performance-relevant threshold here; positive/negative are only physics.
    desc={route:{
        "n_measurements":sum(x["route"]==route for x in alt_stats),
        "range_masked_snr_advantage_db":[
            min(x["masked_alt_snr_minus_canonical_db"] for x in alt_stats if x["route"]==route),
            max(x["masked_alt_snr_minus_canonical_db"] for x in alt_stats if x["route"]==route)
        ]} for route in ("R2","R3","R4")}
    # Priority is an independently certified physical safety violation.
    verdict=STOP_SAFETY if safety else STOP_ACOUSTICS if contam else PASS
    return {
        "status":verdict,
        "evidence_tier":"BENCH_CALIBRATION_ONLY_NOT_BAT_DATA",
        "canonical_gate_interaction_db":maxinter,
        "canonical_max_abs_snr_gate_bias_db":maxbias,
        "canonical_max_target_echo_loss_db":maxloss,
        "min_observed_physical_clearance_m":minclearance,
        "max_observed_peak_db_spl":maxpeak,
        "canonical_point_receipts":out,
        "alternative_path_possible_masked_snr_ranges":desc,
        "n_independent_bench_setups":len(repeats),
        "n_independent_physical_points":len(anchors)+len(alts),
        "n_total_calibrated_rows":len(seen),
        "tolerances":tol,
        "bat_masking_buffer_benefit_demonstrated":False,
        "bat_trial_authorized":False,
        "no_animal_inferential_p":None,
        "caution":"Meeting sound/physical bench tolerances cannot prove masking relief, learning, prey payoff or safe animal-study approval."
    }


def main_job(manifest_path, csv_path):
    try:
        info=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        anchors, alts, floor, tol, sha=load_manifest(info)
        actual=hashlib.sha256(Path(csv_path).read_bytes()).hexdigest()
        if actual != sha:
            raise InvalidBench("raw CSV SHA256 does not match frozen manifest")
        with open(csv_path, newline="", encoding="utf-8-sig") as fd:
            reader=csv.DictReader(fd)
            seen,reps=ingest(reader,anchors,alts,floor)
        result=calculate(anchors,alts,seen,reps,tol)
        result["manifest_source_id"]=info["source_id"]
        result["raw_bench_csv_sha256_verified"]=True
        return result
    except (InvalidBench,FileNotFoundError,PermissionError,json.JSONDecodeError,csv.Error) as err:
        return {"status":STOP_STRUCTURE,"reason":str(err),
                "evidence_tier":"NO_USABLE_BENCH_MEASUREMENTS",
                "bat_trial_authorized":False,"bat_masking_buffer_benefit_demonstrated":False,
                "no_animal_inferential_p":None}


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        manifest={
            "source_id":"DUMMY_ONLY_NOT_A_FACILITY_SOURCE",
            "source_dataset_sha256":"",
            "mic_calibrated":True,"transmitter_calibrated":True,
            "acoustic_band_hz":[25000,75000],
            "bench_repeat_floor":3,
            "max_allowed_fixed_point_snr_gate_bias_db":0.5,
            "max_allowed_fixed_point_snr_gate_x_masker_interaction_db":0.5,
            "max_acceptable_target_loss_db":0.5,
            "min_clearance_m":0.1,
            "max_safe_peak_db_spl":110,
            "anchor_points":[
                {"point_id":f"R1_{i}","station_id":f"S{i}","route_id":"R1",
                 "probe_orientation":"fixed_calibrated","x_m":i,"y_m":0,"z_m":1}
                for i in (1,2)],
            "alternative_points":[
                {"point_id":f"{route}_{i}","station_id":f"S{i}","route_id":route,
                 "probe_orientation":"fixed_calibrated","x_m":i,"y_m":j,"z_m":1}
                for j,route in enumerate(("R2","R3","R4"),start=1) for i in (1,2)]
        }
        csv_path=root/"dummy_bench.csv"
        rows=[]
        for repeat in ("setup1","setup2","setup3"):
            for point in ("R1_1","R1_2"):
                for r,m in ARMS:
                    rows.append([point,repeat,str(r),str(m),"58","42" if m else "25","65","0.4"])
            for route in ("R2","R3","R4"):
                for point in (f"{route}_1",f"{route}_2"):
                    for m in (0,1):
                        rows.append([point,repeat,"1",str(m),"58","39" if m else "25","65","0.4"])
        with csv_path.open("w",newline="") as h:
            writer=csv.writer(h);writer.writerow(FIELDS);writer.writerows(rows)
        manifest["source_dataset_sha256"]=hashlib.sha256(csv_path.read_bytes()).hexdigest()
        manifest_path=root/"manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        a=main_job(manifest_path,csv_path)
        assert a["status"]==PASS, a
        assert a["n_total_calibrated_rows"]==len(rows)
        assert a["alternative_path_possible_masked_snr_ranges"]["R2"]["range_masked_snr_advantage_db"]==[3.0,3.0]
        # Apparatus-only interaction while keeping physical route selection fixed.
        contaminated=[r.copy() for r in rows]
        for v in contaminated:
            if v[0]=="R1_1" and v[2]=="1" and v[3]=="1":
                v[4]="60"  # raises open-gate target echo by 2dB only under masker
        with csv_path.open("w",newline="") as h:
            writer=csv.writer(h);writer.writerow(FIELDS);writer.writerows(contaminated)
        manifest["source_dataset_sha256"]=hashlib.sha256(csv_path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        b=main_job(manifest_path,csv_path)
        assert b["status"]==STOP_ACOUSTICS,b
        # Same row cannot masquerade as two independent measurements.
        with csv_path.open("a",newline="") as h:
            writer=csv.writer(h);writer.writerow(contaminated[0])
        manifest["source_dataset_sha256"]=hashlib.sha256(csv_path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        c=main_job(manifest_path,csv_path)
        assert c["status"]==STOP_STRUCTURE,c
        manifest["source_dataset_sha256"]="0"*64
        manifest_path.write_text(json.dumps(manifest))
        d=main_job(manifest_path,csv_path)
        assert d["status"]==STOP_STRUCTURE,d
        return {
            "source":"DUMMY_DATA_ONLY",
            "4_arm_x_3_setup_per_physical_anchor":"PASS",
            "valid_calibration_and_alternative_path_snr_map":"PASS",
            "device_interaction_confound_detected":"PASS",
            "duplicate_bench_repeat_guard":"PASS",
            "raw_csv_hash_mismatch_guard":"PASS",
            "no_bat_p_value_generated":"PASS",
            "no_bat_inferences_or_approvals":"PASS",
        }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",help="predeclared real bench_manifest.json")
    p.add_argument("--csv",help="actual original recorded bench_acoustics.csv")
    p.add_argument("--out",help="path to JSON result, if source supplied")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),indent=2,sort_keys=True));return
    if not args.manifest or not args.csv:
        raise SystemExit("STOP: must supply actual source manifest and bench acoustic CSV; no defaults or generated biological data")
    result=main_job(args.manifest,args.csv)
    if args.out:
        Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
