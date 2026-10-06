#!/usr/bin/env python3
"""Frozen 4-bat acoustic-policy identity-retention primary.

Runs only after structural gate PASS.
"""

from __future__ import annotations

import itertools
import json
import math
import pathlib
import tempfile
import urllib.request

import numpy as np
import scipy.io

HERE=pathlib.Path(__file__).resolve().parent
STRUCT=HERE/"STRUCTURAL_RESULT_V1.json"
OUT=HERE/"ACOUSTIC_POLICY_RESULT_V1.json"
OUTMD=HERE/"ACOUSTIC_POLICY_RESULT_V1.md"

BASE="https://zenodo.org/records/13857870/files"
BATS=("jane","bea","jason","stella")


def fetch(name):
    req=urllib.request.Request(
        f"{BASE}/{name}?download=1",
        headers={"User-Agent":"batter-acoustic-policy/1.0"},
    )
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def load_struct(data):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data)
        tf.flush()
        mat=scipy.io.loadmat(tf.name,squeeze_me=True,struct_as_record=False)
    st=mat.get("audiopoolstruct")
    if st is None:
        raise RuntimeError("audiopoolstruct absent")
    return st


def flat_numeric(x):
    return np.asarray(x,dtype=float).reshape(-1)


def trial_items(x):
    arr=np.asarray(x,dtype=object)
    if arr.ndim==0:
        return [arr.item()]
    return list(arr.reshape(-1))


def finite_mean(x):
    a=np.asarray(x,dtype=float).reshape(-1)
    a=a[np.isfinite(a)]
    if len(a)==0:
        return None
    return float(np.mean(a))


def trial_rows(bat):
    st=load_struct(fetch(f"{bat}_audiopooldata.mat"))
    treatment=flat_numeric(st.treatment)
    trialtype=flat_numeric(st.trialtype)
    duration=trial_items(st.callduration)
    bandwidth=trial_items(st.callbandwidth)
    onset=trial_items(st.onsetcalltrial)
    lengthadj=flat_numeric(st.lengthtrialadjust)

    n=min(len(treatment),len(trialtype),len(duration),len(bandwidth),len(onset),len(lengthadj))
    rows=[]
    for q in range(n):
        tr=float(treatment[q])
        tt=float(trialtype[q])
        if tr not in (1.0,2.0) or not np.isfinite(tt) or not (tt<4):
            continue

        D=finite_mean(duration[q])
        B=finite_mean(bandwidth[q])

        o=np.asarray(onset[q],dtype=float).reshape(-1)
        o=o[np.isfinite(o)]
        I=float(np.mean(np.diff(o))) if len(o)>=2 else None

        T=float(lengthadj[q])
        C=float(len(o)/T) if np.isfinite(T) and T>0 else None

        vals=(D,B,I,C)
        if any(v is None or not np.isfinite(v) for v in vals):
            continue

        rows.append({
            "bat":bat,
            "treatment":int(tr),
            "trialtype":int(tt),
            "x":np.asarray(vals,dtype=float),
        })
    return rows


def residualize(rows):
    X=np.vstack([r["x"] for r in rows])
    z=np.empty_like(X)

    groups={}
    for idx,r in enumerate(rows):
        groups.setdefault((r["treatment"],r["trialtype"]),[]).append(idx)

    residual=np.empty_like(X)
    for idxs in groups.values():
        mu=np.mean(X[idxs,:],axis=0)
        residual[idxs,:]=X[idxs,:]-mu

    sd=np.std(residual,axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0):
        raise RuntimeError("zero/nonfinite pooled residual SD")

    z=residual/sd
    return z


def centroids(rows,z):
    out={}
    for bat in BATS:
        for tr in (1,2):
            idx=[i for i,r in enumerate(rows) if r["bat"]==bat and r["treatment"]==tr]
            if len(idx)<5:
                raise RuntimeError(f"support drift {bat} treatment={tr}: {len(idx)}")
            out[(bat,tr)]=np.mean(z[idx,:],axis=0)
    return out


def statistic(cent, mapping):
    # mapping is tuple of saline bat labels aligned to ligand bats in BATS order.
    vals=[]
    saline={bat:cent[(bat,1)] for bat in BATS}
    for i,ligbat in enumerate(BATS):
        L=cent[(ligbat,2)]
        mapped_self=saline[mapping[i]]
        dself=float(np.linalg.norm(L-mapped_self))
        others=[saline[mapping[j]] for j in range(4) if j!=i]
        dother=float(np.mean([np.linalg.norm(L-x) for x in others]))
        vals.append(dother-dself)
    return float(np.mean(vals)),vals


def main():
    gate=json.loads(STRUCT.read_text())
    if gate.get("verdict")!="PASS_OPEN_NUMERIC_PRIMARY":
        raise SystemExit("STOP: structural gate did not authorize numerical primary")

    rows=[]
    for bat in BATS:
        rows.extend(trial_rows(bat))

    support={}
    for bat in BATS:
        support[bat]={
            "saline":sum(r["bat"]==bat and r["treatment"]==1 for r in rows),
            "ligand":sum(r["bat"]==bat and r["treatment"]==2 for r in rows),
        }
        if min(support[bat].values())<5:
            raise SystemExit(f"STOP support drift: {bat} {support[bat]}")

    z=residualize(rows)
    cent=centroids(rows,z)

    observed_mapping=tuple(BATS)
    obs,individual=statistic(cent,observed_mapping)

    null=[]
    mapping_rows=[]
    for perm in itertools.permutations(BATS):
        kval,_=statistic(cent,perm)
        null.append(kval)
        mapping_rows.append({"mapping":list(perm),"K":kval})

    null=np.asarray(null,dtype=float)
    p=float(np.mean(null>=obs-1e-15))
    rank=int(1+np.sum(null>obs+1e-15))

    # Descriptive component localization, no p-values.
    component={}
    for k,name in enumerate(("duration","bandwidth","ipi","call_rate")):
        one={key:np.asarray([value[k]]) for key,value in cent.items()}
        kval,ivals=statistic(one,observed_mapping)
        component[name]={"K":kval,"individual_advantages":ivals}

    result={
        "version":1,
        "source":"10.5281/zenodo.13857870",
        "bats":list(BATS),
        "support":support,
        "K":obs,
        "p_exact":p,
        "rank_descending":rank,
        "n_permutations":24,
        "individual_advantages":individual,
        "positive_fraction":float(np.mean(np.asarray(individual)>0)),
        "component_descriptive":component,
        "verdict":"SUPPORTED" if (obs>0 and p<=0.05) else "UNSUPPORTED",
    }
    OUT.write_text(json.dumps(result,indent=2)+"\n")

    lines=[
        "# Acoustic policy result v1","",
        f"- K = **{obs:+.6f}**",
        f"- exact p = **{p:.6f}**",
        f"- observed rank among 24 mappings = **{rank}**",
        f"- positive individuals = **{sum(np.asarray(individual)>0)}/4**",
        f"- verdict = **{result['verdict']}**","",
        "## Structural support","",
    ]
    for bat in BATS:
        lines.append(f"- {bat}: saline {support[bat]['saline']}, ligand {support[bat]['ligand']}")
    lines += ["","## Individual advantages",""]
    for bat,val in zip(BATS,individual):
        lines.append(f"- {bat}: {val:+.6f}")
    lines += ["","## Component localization — descriptive only",""]
    for name,x in component.items():
        lines.append(f"- {name}: K={x['K']:+.6f}")
    lines += ["","No component-wise p-values are authorized.",""]
    OUTMD.write_text("\n".join(lines))
    print(OUTMD.read_text())


if __name__=="__main__":
    main()
