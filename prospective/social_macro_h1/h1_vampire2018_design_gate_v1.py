#!/usr/bin/env python3
"""Vrtilek 2018 original Figshare maze source DESIGN audit, not outcome test.

The source code does not read exit.in.15/latency/latency2 outcome values.
Physical IDs and individual rows remain transient and aren't logged or
committed. Exact source original MD5 verified.
"""
import collections,csv,hashlib,io,json,os,urllib.request
from pathlib import Path

URL="https://ndownloader.figshare.com/files/12183227"
EXPECTED_MD5="935d61487756bd62837b9a53cc5f11f8"
EXPECTED_BYTES=6615
EXPECTED_FIELDS=["experiment","trial ","bat","demonstrator","phase","attempt","latency","latency2","exit.in.15","naive"]
OUT=Path(os.getenv("H1_VAMPIRE2018_DESIGN_RECEIPT","/tmp/h1_vampire2018_design_receipt.json"))

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"BatH1MazeOriginalSourceCodeAudit/1.0"})
    with urllib.request.urlopen(req,timeout=30) as r:
        dat=r.read(20000);status=r.status
    if len(dat)!=EXPECTED_BYTES or hashlib.md5(dat).hexdigest()!=EXPECTED_MD5:
        raise ValueError("Original Figshare CSV MD5 or length differs from publisher")
    return dat,status

def analyse_design(dat):
    reader=csv.DictReader(io.StringIO(dat.decode("utf-8-sig"),newline=""))
    if reader.fieldnames!=EXPECTED_FIELDS:
        raise ValueError("Original field names drifted: "+str(reader.fieldnames))
    rows=list(reader)
    if len(rows)!=188:raise ValueError("Expected 188 original observation rows")
    levels={}
    for k in ("experiment","trial ","demonstrator","phase","attempt","naive"):
        levels[k]=dict(sorted(collections.Counter(str(r[k]) for r in rows).items()))
    unique_subjects=len({r["bat"] for r in rows if r["bat"].strip()})
    blank_subject_rows=sum(not r["bat"].strip() for r in rows)
    exp_subjects={k:len({r["bat"] for r in rows if r["experiment"]==k and r["bat"].strip()}) for k in levels["experiment"]}
    phase_subjects={k:len({r["bat"] for r in rows if r["phase"]==k and r["bat"].strip()}) for k in levels["phase"]}
    dphase=dict(sorted(collections.Counter((r["demonstrator"],r["phase"]) for r in rows).items()))
    return {"original_n_rows":len(rows),"n_distinct_nonblank_bat_ids":unique_subjects,
            "n_blank_bat_id_rows":blank_subject_rows,
            "factor_level_counts":levels,
            "n_individuals_per_experiment":exp_subjects,
            "n_individuals_per_phase":phase_subjects,
            "demonstrator_by_phase":[{"demonstrator":k[0],"phase":k[1],"rows":v} for k,v in dphase.items()],
            "outcomes_opened":False,
            "participant_identifiers_in_receipt":False}

def main():
    raw,status=fetch()
    out={"status":"VERIFIED_ORIGINAL_SCHEMA_AND_DESIGN_ONLY",
         "article_doi":"10.6084/m9.figshare.6466022.v2",
         "original_md5":EXPECTED_MD5,"original_sha256":hashlib.sha256(raw).hexdigest(),
         "original_source_bytes":len(raw),"original_file_download_status":status,
         "source":URL,"design":analyse_design(raw)}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
