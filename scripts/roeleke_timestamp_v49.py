"""V49 timestamp-only adapter for exact V48 public data."""
import hashlib,json,pathlib,re,itertools
from collections import Counter
import numpy as np
import pandas as pd
import roeleke_json_export_v48 as v48
import roeleke_functional_space_v46 as v46
OUT=pathlib.Path("results/roeleke_timestamp_v49.json")
DATES=["%Y-%m-%d","%Y/%m/%d","%Y.%m.%d","%d.%m.%Y","%d/%m/%Y","%m/%d/%Y","%d-%m-%Y","%m-%d-%Y","%Y%m%d","%m.%d.%Y"]
CLOCKS=["%H:%M","%H:%M:%S","%H:%M:%S.%f","%H:%M:%S,%f","%H:%M:%S%z","%H:%M:%S %z","%H:%M:%S.%f%z","%H:%M:%S.%f %z"]
FORMATS=["ISO8601"]+[d+s+c for d,s,c in itertools.product(DATES,[" ","T"],CLOCKS)]
def shape(s):
    s=re.sub(r"\d","D",s.strip())
    return s if len(s)<=70 and re.fullmatch(r"[D .:/,TtZz+\-]+",s) else "OTHER"
def decode(s):
    s=s.astype(str).str.strip()
    o={"lexical_shapes":dict(Counter(s.map(shape))),"candidates_with_parsed_values":[]}
    # Parse unique tokens once; map back to the original records.
    u=pd.Series(s.unique());mapping={};good=[]
    for fmt in FORMATS:
        t=pd.to_datetime(u,format=fmt,errors="coerce",utc=True)
        if not t.notna().any():continue
        if not t.notna().all():
            full=t.iloc[pd.Index(u).get_indexer(s)].reset_index(drop=True)
        else:
            full=t.iloc[pd.Index(u).get_indexer(s)].reset_index(drop=True)
        ok=full.notna()
        n=int(ok.sum())
        y=full[ok].dt.year;m=full[ok].dt.month
        within=bool(y.between(2016,2018).all())
        may=float(m.eq(5).mean())
        qualify=n/len(s)>=.95 and within and may>=.95
        o["candidates_with_parsed_values"].append({"format":fmt,"parsed":n,"all_years_2016_2018":within,"may_fraction":may,"qualifies":qualify})
        if qualify:
            key=hashlib.sha256(full.astype("int64").to_numpy().tobytes()).hexdigest()
            if key not in mapping:mapping[key]=full
            good.append((fmt,key))
    o["qualifying_formats"]=[f for f,k in good]
    o["distinct_qualifying_timestamp_vectors"]=len(mapping)
    if len(mapping)!=1:
        o["status"]="STOP_AMBIGUOUS_OR_UNSUPPORTED";return None,o
    t=next(iter(mapping.values()))
    o["status"]="UNIQUE_TIMESTAMP_VECTOR"
    o["parsed_rows"]=int(t.notna().sum())
    o["year_counts"]={str(int(k)):int(v) for k,v in t.dt.year.value_counts().items()}
    o["month_counts"]={str(int(k)):int(v) for k,v in t.dt.month.value_counts().items()}
    # Keep subsecond resolution, preserve relative archived clock, no local-time interpretation.
    out=t.map(lambda v:v.isoformat() if pd.notna(v) else "")
    return out,o
def test():
    t,o=decode(pd.Series(["23.05.2016 21:00:31","23.05.2016 21:01:02"]))
    assert t is not None and o["parsed_rows"]==2
    t,o=decode(pd.Series(["05/06/2018 21:00:31","05/07/2018 21:01:02"]))
    assert t is not None and o["month_counts"]=={"5":2}
    t,o=decode(pd.Series(["1234567","1234568"]));assert t is None
    t,o=decode(pd.Series(["23.06.2021 21:00:31"]));assert t is None
def run():
    test();v48.test()
    v46.fetch_table=v48.exact_json
    original=v46.prepare
    audit={}
    def prepare(d,role,meta):
        d=d.copy()
        assert len(d)==5627
        t,o=decode(d.timestamp);audit.update(o)
        if t is None:return None,{"raw_rows":len(d)},"STOP_TIMESTAMP_FORMAT"
        d["timestamp"]=t.to_numpy()
        return original(d,role,meta)
    v46.prepare=prepare
    r=v46.run()
    r["version"]="V49";r["timestamp_audit"]=audit;r["synthetic_tests"]="PASS"
    r["source_boundary"]="Exact permission-verified V48 GeoJSON, clock-format repair only; V46 analytical rules unchanged."
    return r
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":type(e).__name__+":"+str(e)[:250]}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
