#!/usr/bin/env python3
"""2025 Myotis v3 Mendeley: original-author, outcome-BLIND source structure gate.

This does NOT fit a biological model, report a physiological mean, read
pulse/amplitude numeric values or mutate original-source files.
It uses the PUBLIC ANONYMOUS frontend API previously proven in #75,
not the OAuth2-requiring api.data.mendeley.com endpoint.
No credentials or browser automation are required.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

DATASET = "8b57pz6bpj"
VERSION = 3
MANIFEST = f"https://data.mendeley.com/api/datasets/{DATASET}/files?version={VERSION}"
OUTPUT = Path(__file__).with_name("MYOTIS_2025_V3_CATEGORICAL_SOURCE_RECEIPT.json")
USER_AGENT = "batter-mendeley-original-public-v3-source-gate/1.0"
SELECTED_FILES = {
    "lData.csv": "cb6a35d229136f466c7ea90c9b63d082ab7eba599ec3315b5d495194c975635c",
    "wData.csv": "04a0fb92104e390d877a6651a7c06069d5eb4797d4c49d253be493254b5d549b",
    "statistical_analysis.R": "7da887a8e0377fa0470ea703b8c0be02fa4cb8a6bb3ce90c26067f10bb4a2c4f",
    "fig2_lData.mat": "4d17865177009c8ba2afb653112fef123f53a621a03fa7b9d19876a549135d01",
    "fig2_wData.mat": "873a2ec8b9a9e83afe0fe1f35b09977718dcc27e048f980f947a6caca52fb75b",
    "fig3_lData.mat": "24a47604ffe2a034162f7b64d6fa0a49ae96e0086e8a00c6bf84fcd0561fe75c",
    "fig3_wData.mat": "5ebaf71c89d877047c5fb8ac18ed585027ba5b28ee875be5fe718123dce4829b",
    "fig1_lData.mat": "97f8451667ab98f0bc353b9240cb9af487a013378063ef0233fabe0a885081bd",
    "fig1.m": "876af3f00ddfe42d7e36caf51febed97cdfa7d869aa714e779b692aed090376c",
    "fig2.m": "95ac2a17453eefe3c5ff5375b0bb4dca5ee65e2529b49c87b6269d014274e81e",
    "fig3.m": "ebcb1d2e767a80554dc0b10a65441695a30de78a4304d733efc8c00801a1763e",
}
MAX_FILE_BYTES = 5_000_000


def get_bytes(url: str, limit: int = MAX_FILE_BYTES) -> bytes:
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/octet-stream, text/plain, application/json, */*",
    })
    with urllib.request.urlopen(request, timeout=90) as response:
        buf = response.read(limit + 1)
    if len(buf) > limit:
        raise ValueError(f"File > {limit} bytes: {url}")
    return buf


def read_manifest() -> dict[str, dict]:
    raw = get_bytes(MANIFEST)
    entries = json.loads(raw.decode("utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Public file manifest is not a JSON list")
    by_name = {}
    for e in entries:
        name = e.get("filename")
        if not isinstance(name, str) or name in by_name:
            raise ValueError("Duplicate or missing original filename")
        by_name[name] = e
    return by_name


def csv_structure(data: bytes, name: str) -> dict:
    try:
        reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)):
            raise ValueError(f"{name}: duplicate columns")
        n = 0
        # CATEGORICAL fields + missingness indicators ONLY.
        combo = Counter()
        original_treatment_codes = Counter()
        bat_deploy = defaultdict(set)
        valid_buzz_counts = Counter()
        for row in reader:
            n += 1
            if name != "lData.csv":
                continue
            k = (row.get("bat_num", "").strip(),
                 row.get("tag_depl_num", "").strip(),
                 row.get("treat_code", "").strip())
            if any(not x for x in k):
                raise ValueError("Missing source bat/tag-deployment/treatment label")
            combo[k] += 1
            original_treatment_codes[k[2]] += 1
            bat_deploy[k[0]].add(k[1])
            if (row.get("buzz2_dur_ms") or "").strip():
                # NO float() call: do not open biological magnitudes.
                valid_buzz_counts[k] += 1
        result = {"filename": name, "columns": fields, "row_count": n,
                  "opened_numeric_biological_values": False}
        if name == "lData.csv":
            result["source_treatment_code_support"] = dict(sorted(original_treatment_codes.items()))
            result["source_bat_to_tag_deployment_labels"] = {
                bat: sorted(dep, key=lambda x:int(x) if x.isdigit() else x)
                for bat, dep in sorted(bat_deploy.items())}
            result["n_physical_bat_labels"] = len(bat_deploy)
            result["n_distinct_bat_deployment_combinations"] = sum(len(d) for d in bat_deploy.values())
            result["per_bat_tag_deployment_x_code"] = [
                {"bat_num": b, "tag_depl_num": d, "treat_code": t,
                 "row_count": count, "nonnull_buzz_ii_rows": valid_buzz_counts[(b,d,t)]}
                for (b,d,t),count in sorted(combo.items(), key=lambda kv:kv[0])]
            result["six_physical_treatment_regimes_recoverable_from_CSV_alone"] = False
            result["reason"] = "treat_code is a 3-level grouping, not original six movement displacement×speed regimes; date and physical trial ID are absent"
        return result
    except (csv.Error, UnicodeDecodeError, ValueError, KeyError) as e:
        raise ValueError(f"Invalid CSV source structure in {name}: {e}") from e


def mat_structure(data: bytes, name: str) -> dict:
    try:
        import scipy.io
        pairs = scipy.io.whosmat(io.BytesIO(data))
        return {"filename":name, "format":"MAT_v5", "variables":[
            {"name":str(n), "shape":list(d), "class":str(cl)} for n,d,cl in pairs],
            "opened_numeric_biological_values":False}
    except Exception as e:
        # Original fig2/fig3 are MATLAB v7.3/HDF5; scipy.whosmat
        # deliberately rejects this format. Read structure only via h5py.
        try:
            import h5py
            objects=[]
            with h5py.File(io.BytesIO(data), "r") as h:
                root_names=list(h.keys())
                def visit(path, obj):
                    # Datasets' .shape/.dtype is metadata, not values.
                    if len(objects)<250:
                        if isinstance(obj,h5py.Dataset):
                            objects.append({"name":path,"kind":"dataset",
                                            "shape":list(obj.shape),"dtype":str(obj.dtype)})
                        elif isinstance(obj,h5py.Group):
                            objects.append({"name":path,"kind":"group"})
                h.visititems(visit)
            return {"filename":name,"format":"MAT_v7_3_HDF5",
                    "root_names":root_names,"objects_first250":objects,
                    "objects_truncated":len(objects)>=250,
                    "opened_numeric_biological_values":False}
        except Exception as e2:
            return {"filename":name, "format":"UNRESOLVED_MAT_FORMAT",
                    "prior_error":type(e).__name__, "reader_error_type":type(e2).__name__,
                    "error_message":str(e2)[:150],
                    "opened_numeric_biological_values":False}


def matlab_source_structure(data: bytes, name: str) -> dict:
    """Read original-author CODE text for schema/stimulus relationships only.

    Numeric individual observations in MAT/CSV files are never read here.
    Variable assignments in published source code are methods/metadata.
    """
    src = data.decode("utf-8-sig", errors="replace")
    patterns = (
        "treat", "condition", "speed", "veloc", "distance", "displac",
        "tag", "bat", "date", "day", "trial", "load(", "readtable",
        "writetable", "group", "move", "motion", "lData", "buzz", "onset",
        "motor", "chase", "time", "fig",
    )
    matches = []
    for n, line in enumerate(src.splitlines(), 1):
        lo = line.lower()
        if any(p.lower() in lo for p in patterns):
            matches.append({"line": n, "source": line.strip()[:400]})
    return {"filename":name, "code_lines":len(src.splitlines()),
            "method_lines":matches[:140], "matching_lines_total":len(matches),
            "opened_numeric_biological_values":False}


def r_structure(data: bytes, name: str) -> dict:
    src=data.decode("utf-8-sig", errors="replace")
    fields=["treat_code","bat_num","tag_depl_num","buzz2_dur_ms","lData.csv","wData.csv","fig2"]
    line_matches={token:[i for i,line in enumerate(src.splitlines(),1) if token in line]
                  for token in fields}
    # Script fragments are methodological metadata: no observed numeric
    # bat responses are opened or reported. These aid code→stimulus mapping.
    anchors=("treat_code", "tag_depl_num", "bat_num")
    interesting=[{"line":i, "source":line[:240]}
                 for i,line in enumerate(src.splitlines(),1)
                 if any(tok in line for tok in anchors)]
    return {"filename":name, "lines":len(src.splitlines()), "matching_code_line_numbers":line_matches,
            "methodological_lines":interesting[:80],
            "opened_numeric_biological_values":False}


def run() -> dict:
    out = {
        "study":"Foskolos et al. (2025) Myotis myotis",
        "dataset_doi":"10.17632/8b57pz6bpj.3",
        "public_manifest_url":MANIFEST,
        "data_access_method":"anonymous public frontend file list and original per-file download",
        "status":"PENDING",
        "outcome_magnitudes_opened":False,
        "individual_response_coefficients_estimated":False,
        "source_documentation_not_yet_proves_tag_deployment_equals_date":True,
        "files":[],
    }
    names=read_manifest()
    out["original_file_count"]=len(names)
    out["original_file_names"]=sorted(names)
    for name,expected_sha in SELECTED_FILES.items():
        if name not in names:
            raise ValueError(f"Missing expected original deposited file {name}")
        meta=names[name]
        cd=meta.get("content_details") or {}
        advertised=cd.get("sha256_hash")
        if advertised!=expected_sha:
            raise ValueError(f"Unexpected original SHA-256 for {name}")
        url=cd.get("download_url")
        if not url or not url.startswith(
            f"https://data.mendeley.com/public-files/datasets/{DATASET}/files/"):
            raise ValueError("Untrusted original per-file URL")
        content=get_bytes(url)
        digest=hashlib.sha256(content).hexdigest()
        if digest!=expected_sha:
            raise ValueError(f"Downloaded bytes SHA-256 mismatch for {name}")
        if name.endswith(".csv"):
            st=csv_structure(content,name)
        elif name.endswith(".mat"):
            st=mat_structure(content,name)
        elif name.endswith(".m"):
            st=matlab_source_structure(content,name)
        else:
            st=r_structure(content,name)
        out["files"].append({**st,"sha256":digest,"size_bytes":len(content)})
    ldata=next(x for x in out["files"] if x["filename"]=="lData.csv")
    out["status"]="SOURCE_STRUCTURE_AVAILABLE"
    out["six_regime_forecast_on_lData_csv"]="STOP_ONLY_3_GROUPED_TREATMENT_CODES"
    out["new_personal_rule_fit"]="HOLD_DATE_MAPPING_AND_SIX_REGIME_SCHEMA"
    out["next_step"]="Check whether author fig2 MAT preserves six original motor regimes and verify bat×tag_deployment→calendar date before any exploratory slope forecast."
    assert ldata["row_count"]==606
    assert ldata["n_physical_bat_labels"]==4
    assert ldata["n_distinct_bat_deployment_combinations"]==18
    assert sorted(ldata["source_treatment_code_support"])==["1","2","3"]
    return out


def main() -> int:
    try:
        out=run()
        code=0
    except Exception as e:
        out={"status":"HOLD_SOURCE_DOWNLOAD_OR_STRUCTURE",
             "error_type":type(e).__name__, "error":str(e)[:500],
             "dataset_doi":"10.17632/8b57pz6bpj.3",
             "outcome_magnitudes_opened":False,
             "individual_response_coefficients_estimated":False}
        code=2
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":out["status"],"original_file_count":out.get("original_file_count"),
        "selected_files":[{"name":x["filename"],"columns":x.get("columns"),
           "variables":x.get("variables"),"root_names":x.get("root_names"),
           "row_count":x.get("row_count"),"method_lines":x.get("method_lines")}
           for x in out.get("files",[])],
        "error":out.get("error"),
        "outcome_magnitudes_opened":False,
    },ensure_ascii=False,indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
