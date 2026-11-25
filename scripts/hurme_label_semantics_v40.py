"""V40 semantic admission only; aggregate source receipts, never raw tracking rows."""
import concurrent.futures as cf,hashlib,io,json,pathlib,re
import numpy as np
import pandas as pd
from bayer_field_join_v17 import fetch
BASE="https://datarepository.movebank.org/server/api/core/bitstreams/"
SPECS={
"gps":("8c34b3fd-d746-4716-bc67-8c770810d1dd",2462362,"07d8e34a973c361dada5dc46da90ed80","38fdeda4a588f86f6f3f4d83dabed71c7e74dcbed1fe055a0aa9d8216be3ddcc"),
"readme":("e0b86f15-796b-4bef-8cad-0e2ace15a381",12586,"4deda336d00f1d563ffc9eebca154b37","b02a0b83fe6bbb7174ba7a2ef2f9ce8a3c67e3fe56d0e469701529d65f30c84f"),
"reference":("c429364a-802b-4fe5-9bcc-abe6fffe8062",7150,"dac2b22f48c653b52398b86fac3d5801",None)}
OUT=pathlib.Path("results/hurme_label_semantics_v40.json")
PAT=r"behavio[u]?ral.classification|behavio[u]?r according to|feeding buzz|buzz|acoustic|audio|duty.cycle|sampling|trip definition|recording|non.detect|no.detect|effort"
def get(k):
    uid,size,md5,sha=SPECS[k]
    try:
        b,_=fetch(BASE+uid+"/content",size)
        assert len(b)==size and hashlib.md5(b).hexdigest()==md5
        digest=hashlib.sha256(b).hexdigest()
        assert sha is None or sha==digest
        return b,{"status":"HASH_VERIFIED","sha256":digest,"bytes":size}
    except Exception as e:return None,{"status":"STOP","error":repr(e)}
def safe_text(s):
    # Do not print personal contacts, raw coordinates, or tag/animal identifiers.
    return not re.search(r"@|\b(?:lat(?:itude)?|lon(?:gitude)?)\b.*[-+]?\d{1,3}\.\d{3,}|\bviv\s*\d+|\b(?:animal|tag)[-_ ]?(?:id|identifier)\s*[:=]\s*\S+|\b\d{4}-\d{2}-\d{2}\b",s,re.I)
def docs(b):
    lines=b.decode("utf-8-sig",errors="replace").splitlines()
    idx=set()
    for i,l in enumerate(lines):
        if re.search(PAT,l,re.I):idx.update(range(max(0,i-1),min(len(lines),i+4)))
    return {"line_count":len(lines),"definition_context":[{"line":i+1,"text":lines[i][:700]} for i in sorted(idx) if safe_text(lines[i])][:55]}
def cat_counts(s):
    s=s.astype(str).str.strip()
    allowed=r"(?i)(?:|[-+]?\d{1,4}(?:\.\d{1,3})?|true|false|yes|no|na|nan|unknown|unclassified|missing|forag(?:e|ing)|commut(?:e|ing)|rest(?:ing)?|flight|flying|non.?flight|feeding|non.?feeding|buzz(?:es)?|no buzz(?:es)?|feeding buzz(?:es)?|no feeding buzz(?:es)?|not recorded|recorded|roost(?:ing)?|transit|travel(?:ing|ling)?|search(?:ing)?|no data|no audio|no call(?:s)?|call(?:s)?|no foraging|not foraging|foraging attempt|prey capture attempt)"
    ok=s.str.fullmatch(allowed)
    return {"distinct":int(s.nunique()),"recognized_tokens":{str(k):int(v) for k,v in s[ok].value_counts().items()},"other_token_rows":int((~ok).sum()),"other_distinct":int(s[~ok].nunique())}
def read(b):return pd.read_csv(io.BytesIO(b),dtype=str,keep_default_na=False,encoding="utf-8-sig")
def gps(b):
    d=read(b);assert len(d)==14328
    x=d.assign(id=d["individual-local-identifier"].str.strip(),t=pd.to_datetime(d.timestamp,utc=True,format="mixed",errors="coerce"))
    assert x.t.notna().all() and x.id.ne("").all() and x.id.nunique()==11
    x=x.sort_values(["id","t"],kind="stable")
    dt=x.groupby("id").t.diff().dt.total_seconds();p=dt[dt>0]
    out={"rows":len(x),"animals":int(x.id.nunique()),"unique_event_id":int(x["event-id"].nunique()),
      "duplicate_animal_timestamp_rows":int(x.duplicated(["id","t"],keep=False).sum()),
      "label_vocabulary":cat_counts(x["behavioural-classification"]),
      "visible":cat_counts(x.visible),"interval_quantiles_seconds":np.quantile(p,[0,.05,.5,.95,1]).tolist(),
      "interval_14_16_fraction":float(p.between(14,16).mean()),"segments":{}}
    for gap in (60,300,900):
        n=(dt.isna()|dt.gt(gap)).cumsum()
        sizes=x.groupby(n).size()
        out["segments"][str(gap)]={"count":len(sizes),"atleast100_fixes":int(sizes.ge(100).sum()),"size_quantiles":np.quantile(sizes,[0,.5,1]).tolist()}
    return out
def ref(b):
    d=read(b)
    out={"rows":len(d),"headers":list(d.columns),"candidate_fields":[]}
    for c in d.columns:
        if not re.search(r"behavio[u]?r|audio|acoustic|sampling|duty|recording|tag.settings|effort|trip",c,re.I):continue
        vals=d[c].str.strip();v=sorted(set(x for x in vals if x))
        # Only documentation strings explicitly related to the source observation semantics.
        accepted=[s[:700] for s in v if re.search(PAT,s,re.I) and safe_text(s)]
        out["candidate_fields"].append({"field":c,"nonblank":int(vals.ne("").sum()),"distinct_nonblank":len(v),"definition_text":accepted[:20]})
    return out
def main():
    out={"scope":"label semantics and effort provenance only; no fitted response","status":"SEMANTIC_REVIEW_REQUIRED","source_doi":"10.5441/001/1.kk3bg2f4","files":{}}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        result=dict(zip(SPECS,ex.map(get,SPECS)))
    for k,(b,r) in result.items():
        out["files"][k]=r
        if b is not None:
            try:r["audit"]={"gps":gps,"readme":docs,"reference":ref}[k](b)
            except Exception as e:r.update(status="STOP_PARSE",error=repr(e))
    out["response_fit"]="NOT_RUN; verify label source, effort and trip grouping first"
    return out
if __name__=="__main__":
    r=main();OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+"\n");print(OUT.read_text())
