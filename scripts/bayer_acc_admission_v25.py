"""V25 source gate. Aggregate structural information only. No inferred flight labels."""
import csv, collections, hashlib, io, json, pathlib, re, urllib.request, zipfile
import pandas as pd
import numpy as np
from bayer_field_join_v17 import original,table
URL="https://datarepository.movebank.org/server/api/core/bitstreams/d35bb3ba-59fd-4d09-ac56-ac59c2ea6eff/content"
SIZE=55465865
MD5="1549392b1c51da65acce2d960efcfd6c"
OUT=pathlib.Path("results/bayer_acc_admission_v25.json")
def main():
    result={"scope":"accelerometer source schema and timing only; no response analysis","source_doi":"10.5441/001/1.754","file_number":7,"expected_md5":MD5}
    try:
        with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"batter-noncommercial-research-source-audit/1.0"}),timeout=120) as r:
            raw=r.read(SIZE+1)
        assert len(raw)==SIZE and hashlib.md5(raw).hexdigest()==MD5
        result["sha256"]=hashlib.sha256(raw).hexdigest();result["bytes"]=len(raw)
        z=zipfile.ZipFile(io.BytesIO(raw))
        assert sum(x.file_size for x in z.infolist())<1_500_000_000
        assert all(not x.filename.startswith(("/","\\")) and ".." not in pathlib.PurePosixPath(x.filename).parts for x in z.infolist())
        result["members"]=[{"name":x.filename,"bytes":x.file_size} for x in z.infolist()]
        members=[x for x in z.infolist() if x.filename.lower().endswith(".csv")]
        assert len(members)==1
        m=members[0]
        with z.open(m) as f:
            header=next(csv.reader(io.TextIOWrapper(f,encoding="utf-8-sig")))
        result["header"]=header
        tcol="timestamp"
        aid="individual-local-identifier";tag="tag-local-identifier"
        assert all(k in header for k in (tcol,aid,tag))
        axis=[c for c in header if re.search(r"acceleration|accelerometer",c,re.I)]
        result["acceleration_columns"]=axis
        assert axis
        # Parse timestamp/IDs and presence of all acceleration columns only.
        use=[tcol,aid,tag]+axis
        ids=set();tags=set();rows=0;badtime=0;missingaxis=collections.Counter();nonnum=collections.Counter()
        first=None;last=None;backwards=0;equal=0;delta_counts=collections.Counter();persec=collections.Counter()
        # Chronology for each tag; second-level counts computed from all rows.
        last_by_tag={}
        with z.open(m) as f:
            for d in pd.read_csv(f,usecols=use,dtype=str,keep_default_na=False,chunksize=250000,encoding="utf-8-sig"):
                rows+=len(d);ids.update(d[aid]);tags.update(d[tag])
                t=pd.to_datetime(d[tcol],format="mixed",utc=True,errors="coerce").dt.as_unit("ns")
                badtime+=int(t.isna().sum())
                q=t.dropna()
                if len(q):
                    first=q.min() if first is None else min(first,q.min());last=q.max() if last is None else max(last,q.max())
                for c in axis:
                    missingaxis[c]+=int(d[c].eq("").sum())
                    nonnum[c]+=int((pd.to_numeric(d[c],errors="coerce").isna()&d[c].ne("")).sum())
                d["_t"]=t
                for k,x in d.dropna(subset=["_t"]).groupby(tag,sort=False):
                    a=x._t.astype("int64").to_numpy()
                    if k in last_by_tag:a=np.r_[last_by_tag[k],a]
                    if len(a)>1:
                        delta=np.diff(a)
                        backwards+=int((delta<0).sum());equal+=int((delta==0).sum())
                        vals,cnt=np.unique(delta,return_counts=True)
                        delta_counts.update({int(v):int(n) for v,n in zip(vals,cnt)})
                    last_by_tag[k]=int(a[-1])
                    sec=(x._t.astype("int64").to_numpy()//1_000_000_000)
                    vals,cnt=np.unique(sec,return_counts=True)
                    persec.update({(k,int(v)):int(n) for v,n in zip(vals,cnt)})
        ref=table(original("ref")[0]);hr=table(original("hr")[0]);gps=table(original("gps")[0])
        # Source document field definitions: print only relevant lines, no identifiers.
        readme=original("readme")[0].decode("utf-8-sig",errors="replace")
        lines=readme.splitlines();selected=[]
        for i,l in enumerate(lines):
            if re.search(r"acceleration|accelerometer|sampling frequency|sample rate|burst|milliseconds",l,re.I):
                selected.extend(lines[max(0,i-1):min(len(lines),i+4)])
        definitions=list(dict.fromkeys(selected))
        norm=lambda a:{str(v).strip().casefold() for v in a if str(v).strip()}
        counts=np.array(list(persec.values()),dtype=int)
        result.update(status="HASH_VERIFIED_ACC_STRUCTURAL_AUDIT",rows=rows,
            animal_count=len(norm(ids)),tag_count=len(norm(tags)),
            missing_timestamps=badtime,first_timestamp=str(first),last_timestamp=str(last),
            nonmonotonic_intervals=backwards,duplicate_timestamp_intervals=equal,
            common_intervals_seconds=[{"seconds":k/1e9,"count":v} for k,v in delta_counts.most_common(12)],
            seconds_with_samples=len(counts),samples_per_second_quantiles=np.quantile(counts,[0,.05,.5,.95,1]).tolist(),
            full_25_sample_seconds=int((counts==25).sum()),missing_axis_cells=dict(missingaxis),nonnumeric_axis_cells=dict(nonnum),
            shared_animals_hr=len(norm(ids)&norm(hr[aid])),shared_animals_gps=len(norm(ids)&norm(gps[aid])),
            acc_tags_in_ref=len(norm(tags)&norm(ref["tag-id"])),readme_acceleration_definitions=definitions[:80])
        # Only explicit source definitions can establish scale. No biological metrics yet.
        result["interpretation"]="Timing and schema only; acceleration scale and flight classification not inferred from numeric distribution."
    except Exception as e:
        result.update(status="STOP",error=repr(e))
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
    if result["status"]=="STOP":raise SystemExit(2)
if __name__=="__main__":main()
