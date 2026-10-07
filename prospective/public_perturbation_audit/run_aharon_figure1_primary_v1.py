#!/usr/bin/env python3
"""Frozen Aharon Figure-1 cross-condition identity primary."""
from __future__ import annotations
import io,itertools,json,re,tempfile,urllib.parse,urllib.request,zipfile
from pathlib import Path
import numpy as np, scipy.io

HERE=Path(__file__).resolve().parent
GATE=HERE/"AHARON_FIGURE1_ZERO_GATE_V1.json"
OUT=HERE/"AHARON_FIGURE1_PRIMARY_RESULT_V1.json"
OUTMD=HERE/"AHARON_FIGURE1_PRIMARY_RESULT_V1.md"
DATASET="f6mvhj5gj9";VERSION=3;TARGET="Figure 1.zip"
BATS=("500","503","505","510");CONDS=("con","75","300")
HEADERS={"User-Agent":"Mozilla/5.0 batter-aharon-figure1-primary/1.0","Accept":"application/json,*/*"}

def get_bytes(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def file_rows():
    u=f"https://data.mendeley.com/api/datasets/{DATASET}/files?"+urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
    x=json.loads(get_bytes(u,"application/json").decode())
    return x if isinstance(x,list) else x.get("items") or x.get("files") or x.get("results") or x.get("data") or []

def zipbytes():
    for row in file_rows():
        if (row.get("filename") or row.get("name"))==TARGET:
            cd=row.get("content_details") or {};u=cd.get("download_url") or row.get("download_url")
            if not u:raise RuntimeError("no download URL")
            return get_bytes(u)
    raise RuntimeError("Figure 1.zip absent")

def matrix(data):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data);tf.flush();m=scipy.io.loadmat(tf.name)
    vars=[v for k,v in m.items() if not k.startswith("__") and isinstance(v,np.ndarray) and np.issubdtype(v.dtype,np.number)]
    if len(vars)!=1:raise RuntimeError("expected one numeric variable")
    return np.asarray(vars[0],dtype=float)

def trial_vectors(a):
    out=[]
    for j in range(a.shape[1]):
        r=a[0::2,j];l=a[1::2,j]
        r=r[np.isfinite(r)];l=l[np.isfinite(l)]
        if len(r)>=1 and len(l)>=1:
            out.append([float(np.median(r)),float(np.median(l))])
    return np.asarray(out,float)

def load_states():
    pat=re.compile(r"(500|503|505|510)_YRLturns_together_(con|75|300)\.mat$",re.I)
    q={}
    support={}
    with zipfile.ZipFile(io.BytesIO(zipbytes())) as z:
        for name in z.namelist():
            m=pat.search(name)
            if not m:continue
            b=m.group(1);c=m.group(2).lower()
            tv=trial_vectors(matrix(z.read(name)))
            if len(tv)<5:raise RuntimeError(f"support drift {b}|{c}: {len(tv)}")
            q[(b,c)]=tv.mean(axis=0)
            support[f"{b}|{c}"]=int(len(tv))
    if len(q)!=12:raise RuntimeError(f"expected 12 states, got {len(q)}")
    return q,support

def residual_states(q):
    r={}
    for c in CONDS:
        mu=np.mean(np.vstack([q[(b,c)] for b in BATS]),axis=0)
        for b in BATS:r[(b,c)]=q[(b,c)]-mu
    return r

def score_with_labels(r,label_maps):
    # label_maps maps condition -> dict target biological label -> source state label.
    vals={}
    for c in CONDS:
        train=[d for d in CONDS if d!=c]
        for b in BATS:
            target=r[(label_maps[c][b],c)]
            selfhist=np.mean(np.vstack([r[(label_maps[d][b],d)] for d in train]),axis=0)
            dself=float(np.linalg.norm(target-selfhist))
            donors=[]
            for j in BATS:
                if j==b:continue
                h=np.mean(np.vstack([r[(label_maps[d][j],d)] for d in train]),axis=0)
                donors.append(float(np.linalg.norm(target-h)))
            vals[(b,c)]=float(np.mean(donors)-dself)
    batmean={b:float(np.mean([vals[(b,c)] for c in CONDS])) for b in BATS}
    condmean={c:float(np.mean([vals[(b,c)] for b in BATS])) for c in CONDS}
    K=float(np.mean(list(batmean.values())))
    return K,batmean,condmean,vals

def mapping_from_perm(perm):
    return {b:p for b,p in zip(BATS,perm)}

def main():
    if json.loads(GATE.read_text()).get("gate")!="PASS_NO_ZERO_SENTINEL":
        raise SystemExit("STOP: zero-sentinel gate did not authorize primary")
    q,support=load_states();r=residual_states(q)
    identity={b:b for b in BATS}
    observed_maps={c:identity.copy() for c in CONDS}
    obs,batmean,condmean,vals=score_with_labels(r,observed_maps)

    null=[];rows=[]
    for p75 in itertools.permutations(BATS):
        m75=mapping_from_perm(p75)
        for p300 in itertools.permutations(BATS):
            m300=mapping_from_perm(p300)
            maps={"con":identity,"75":m75,"300":m300}
            k,_,_,_=score_with_labels(r,maps)
            null.append(k)
            rows.append({"75":list(p75),"300":list(p300),"K":k})
    null=np.asarray(null,float)
    p=float(np.mean(null>=obs-1e-15))
    rank=int(1+np.sum(null>obs+1e-15))

    loo={}
    for drop in BATS:
        keep=[b for b in BATS if b!=drop]
        # descriptive only: same observed identity advantages averaged over remaining bats.
        loo[drop]=float(np.mean([batmean[b] for b in keep]))

    result={
      "version":1,"source":"10.17632/f6mvhj5gj9.3","figure":1,
      "bats":list(BATS),"conditions":list(CONDS),"support":support,
      "K":obs,"p_exact":p,"rank_descending":rank,"n_null":int(len(null)),
      "bat_mean_advantage":batmean,"condition_mean_advantage":condmean,
      "positive_bats":int(sum(v>0 for v in batmean.values())),
      "leave_one_bat_out_K_descriptive":loo,
      "verdict":"SUPPORTED" if (obs>0 and p<=0.05) else ("POSITIVE_BUT_UNRESOLVED" if obs>0 else "NO_POSITIVE_IDENTITY")
    }
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Aharon Figure-1 cross-condition identity result v1","",
      f"- K = **{obs:+.6f}**",f"- exact p = **{p:.6f}**",
      f"- observed rank among 576 mappings = **{rank}**",
      f"- positive bats = **{result['positive_bats']}/4**",
      f"- verdict = **{result['verdict']}**","",
      "## Bat-level mean advantages",""]
    for b in BATS:lines.append(f"- {b}: {batmean[b]:+.6f}")
    lines += ["","## Condition-level mean advantages",""]
    for c in CONDS:lines.append(f"- {c}: {condmean[c]:+.6f}")
    lines += ["","## Support",""]
    for b in BATS:
        lines.append(f"- {b}: con={support[f'{b}|con']}, 75={support[f'{b}|75']}, 300={support[f'{b}|300']}")
    OUTMD.write_text("\n".join(lines)+"\n");print(OUTMD.read_text())

if __name__=="__main__":main()
