#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import tempfile
import urllib.request

import numpy as np
import scipy.io

HERE=pathlib.Path(__file__).resolve().parent
OUT=HERE/"STRUCTURAL_RESULT_V1.json"
OUTMD=HERE/"STRUCTURAL_RESULT_V1.md"

BASE="https://zenodo.org/records/13857870/files"
BATS=["jane","bea","jason","stella"]
FIELDS=[
    "treatment","trialtype","trialindex","trialnb","lengthtrialadjust",
    "onsetcalltrial","callduration","callbandwidth","startfreq","endfreq"
]

def fetch(name):
    url=f"{BASE}/{name}?download=1"
    req=urllib.request.Request(url,headers={"User-Agent":"batter-structural-audit/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def load_struct(data):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data)
        tf.flush()
        mat=scipy.io.loadmat(tf.name,squeeze_me=True,struct_as_record=False)
    return mat.get("audiopoolstruct")

def audit(bat):
    name=f"{bat}_audiopooldata.mat"
    data=fetch(name)
    st=load_struct(data)
    row={"bat":bat,"filename":name,"bytes":len(data),"fields":{},"counts":{}}
    if st is None:
        row["status"]="STOP_NO_AUDIOPOOLSTRUCT"
        return row

    available=set(getattr(st,"_fieldnames",[]) or [])
    for field in FIELDS:
        if field in available:
            val=getattr(st,field)
            row["fields"][field]={"present":True,"shape":list(np.shape(val))}
        else:
            row["fields"][field]={"present":False,"shape":None}

    if not {"treatment","trialtype"}.issubset(available):
        row["status"]="STOP_MISSING_TREATMENT_STRUCTURE"
        return row

    treatment=np.asarray(getattr(st,"treatment")).reshape(-1)
    trialtype=np.asarray(getattr(st,"trialtype")).reshape(-1)
    n=min(len(treatment),len(trialtype))
    treatment=treatment[:n]
    trialtype=trialtype[:n]
    ok=trialtype<4

    row["counts"]={
        "all_trials":int(n),
        "saline_trialtype_lt4":int(np.sum((treatment==1)&ok)),
        "ligand_trialtype_lt4":int(np.sum((treatment==2)&ok)),
    }

    required={"lengthtrialadjust","onsetcalltrial","callduration","callbandwidth"}
    support=(
        required.issubset(available)
        and row["counts"]["saline_trialtype_lt4"]>=5
        and row["counts"]["ligand_trialtype_lt4"]>=5
    )
    row["status"]="PASS" if support else "STOP"
    return row

def render(result):
    lines=["# Auditory perturbation structural result v1","",
           "**STRUCTURE ONLY — NO ACOUSTIC OUTCOME VALUES.**",""]
    for r in result["bats"]:
        lines += [
            f"## {r['bat']}","",
            f"- status: **{r['status']}**",
            f"- all structural trials: {r['counts'].get('all_trials')}",
            f"- Saline trialtype<4: {r['counts'].get('saline_trialtype_lt4')}",
            f"- Ligand trialtype<4: {r['counts'].get('ligand_trialtype_lt4')}",
            "",
        ]
    lines += ["## Verdict","",f"**{result['verdict']}**",""]
    return "\n".join(lines)

def main():
    rows=[audit(b) for b in BATS]
    verdict="PASS_OPEN_NUMERIC_PRIMARY" if all(r["status"]=="PASS" for r in rows) else "STOP_AUDIO_POLICY_PRIMARY_SUPPORT"
    result={"version":1,"bats":rows,"verdict":verdict}
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    OUTMD.write_text(render(result)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
