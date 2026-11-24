"""V20: source repair, exact identity mapping, unchanged blocked baseline.
No original records redistributed. Noncommercial scholarly analysis.
"""
import concurrent.futures as cf
import hashlib, io, json, pathlib, re, zipfile
import numpy as np
import pandas as pd
from bayer_field_join_v17 import original, table, fetch
import bayer_wind_hr_v19 as v19
OUT=pathlib.Path("results/bayer_archive_id_v20.json")
FILES={"speed":(43182042,13429555,"1ed123fb1f7fce6686bd5b8a26cc67a6"),
       "direction":(43182093,8760445,"43790488bac295a468c076fd78b3d56e")}
def archive(item):
    role,(fid,size,md5)=item
    o={"file_id":fid,"md5":md5}
    try:
        raw,_=fetch(f"https://ndownloader.figshare.com/files/{fid}",size)
        assert len(raw)==size and hashlib.md5(raw).hexdigest()==md5
        o["sha256"]=hashlib.sha256(raw).hexdigest()
        z=zipfile.ZipFile(io.BytesIO(raw));members=z.infolist()
        assert sum(x.file_size for x in members)<250_000_000
        assert all(not x.filename.startswith(("/","\\")) and ".." not in pathlib.PurePosixPath(x.filename).parts for x in members)
        o["members"]=[{"name":x.filename,"bytes":x.file_size} for x in members][:150]
        files=[x for x in members if x.filename.lower().endswith((".csv",".txt",".dat",".tsv"))]
        chosen=[x for x in files if "2023" in x.filename] or files
        out=[]
        for x in chosen[:40]:
            if x.file_size>100_000_000:continue
            with z.open(x) as f:
                lines=[]
                for _ in range(8):
                    l=f.readline()
                    if not l:break
                    lines.append(l.decode("utf-8-sig",errors="replace").strip())
                # Header text; numerical rows summarized by date-like tokens and field counts.
                rowinfo=[]
                for l in lines:
                    cells=re.split(r"[,;\t]",l)
                    tokens=[s.strip('" ') for s in cells]
                    if re.search(r"[A-Za-z]{3,}",l) and not re.match(r'^\s*"?\d{4}[-/,]',l):
                        rowinfo.append({"header":l[:350]})
                    else:
                        rowinfo.append({"field_count":len(cells),"date_tokens":[t for t in tokens if re.fullmatch(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?|\d{1,2}[-/]\d{1,2}[-/]\d{4}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?|\d{1,2}:\d{2}(?::\d{2})?",t)]})
                # Count lines with an explicit August 2023 date, without reading values into analysis.
                aug=0;n=len(lines)
                last=""
                for l in f:
                    n+=1
                    t=l.decode("utf-8",errors="replace")
                    if re.search(r"2023[-/]0?8[-/]|0?8[-/]\d{1,2}[-/]2023|\d{1,2}[-/]0?8[-/]2023",t):aug+=1
                    last=t
                out.append({"member":x.filename,"sample_schema":rowinfo,"lines":n,"aug2023_explicit_date_rows_after_first8":aug,
                            "last_date_tokens":re.findall(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?",last)[:2]})
        o.update(status="HASH_VERIFIED_ZIP",inspected=out)
    except Exception as e:o.update(status="STOP",error=repr(e))
    return role,o
def named(s):
    return bool(re.fullmatch(r"phyl[\s_\-]*0*30",str(s).strip(),re.I))
def resolve():
    g=table(original("gps")[0]);r=table(original("ref")[0])
    g["aid"]=v19.idnorm(g["individual-local-identifier"]);g["tag"]=v19.idnorm(g["tag-local-identifier"])
    r["aid"]=v19.idnorm(r["animal-id"]);r["tag"]=v19.idnorm(r["tag-id"])
    valid=set(g.aid)
    matches={}
    for c in ["individual-local-identifier","tag-local-identifier"]:
        matches["gps:"+c]=set(g.loc[g[c].map(named),"aid"])
    for c in ["animal-id","tag-id"]:
        matches["ref:"+c]=set(r.loc[r[c].map(named),"aid"])&valid
    # Only explicit named token in a GPS deployment row; no inference from activity.
    gps_tags=set(g.tag)
    for c in ["tag-comments","deployment-comments","tag-settings","animal-comments"]:
        hits=r[c].str.contains(r"(?i)(?<![A-Za-z0-9])phyl[\s_\-]*0*30(?!\d)",regex=True)
        matches["ref:"+c]=set(r.loc[hits&r.tag.isin(gps_tags),"aid"])&valid
    candidates=set.union(set(),*matches.values())
    report={"candidate_count":len(candidates),"evidence_counts":{k:len(v) for k,v in matches.items()},
            "gps_tag_matches_reference":len(set(g.tag)&set(r.tag)),"status":"UNRESOLVED"}
    if len(candidates)!=1:return report
    aid=next(iter(candidates));tagset=set(g.loc[g.aid==aid,"tag"])
    if len(tagset)!=1 or not ((r.aid==aid)&r.tag.isin(tagset)).any():return report
    report["status"]="UNIQUE_EXPLICIT_GPS_CROSSWALK"
    # Keep original V19 frozen comparison except exact mapping. Instead of modifying
    # data, use a wrapper of original table loader that maps the named animal to
    # 'phyl30' consistently in GPS and HR; the original source hashes still checked.
    loader=v19.table
    def rename(raw):
        d=loader(raw)
        if "individual-local-identifier" in d.columns:
            k=v19.idnorm(d["individual-local-identifier"]).eq(aid)
            d.loc[k,"individual-local-identifier"]="phyl30"
        return d
    v19.table=rename
    try:report["baseline"]=v19.baseline()
    except Exception as e:report["baseline"]={"status":"STOP","error":repr(e)}
    finally:v19.table=loader
    return report
def main():
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        f=[ex.submit(archive,x) for x in FILES.items()];i=ex.submit(resolve)
        result={"scope":"source repair; baseline only if published exclusion exactly resolved","weather":dict(x.result() for x in f)}
        try:result["identity"]=i.result()
        except Exception as e:result["identity"]={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
