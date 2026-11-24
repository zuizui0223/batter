"""Public per-file source fallback, pre-outcome schema and methods audit only."""
import concurrent.futures, json, pathlib, hashlib, urllib.request, urllib.parse
from scripts.carollia_sources_v7 import EXPECTED
OUT=pathlib.Path("results/carollia_thermal_public_files_v8.json")
def one(item):
    name,md5=item
    url="https://zenodo.org/records/7126170/files/"+urllib.parse.quote(name)+"?download=1"
    d={"url":url,"publisher_md5":md5}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"batter-research-source-audit/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r:
            b=r.read(100001)
        if len(b)>100000 or hashlib.md5(b).hexdigest()!=md5:
            raise ValueError("size or original MD5 mismatch")
        d.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        s=b.decode("utf-8-sig")
        if name.endswith(".txt"):
            lines=[l for l in s.splitlines() if l.strip()]
            d["header"]=lines[0];d["data_rows"]=len(lines)-1
            d["first_data_field_count"]=len(lines[1].split()) if len(lines)>1 else 0
        else:
            d["methods_code"]=s if name in ("PowFlight.R","HeatLoss.R") else "\n".join(l for l in s.splitlines() if any(k in l for k in ("read.table","read.csv","merge(","HeatLoss","PowFlight","lm(","glm(","source(","rename(","colnames(","rownames(")))[:10000]
        d["status"]="HASH_VERIFIED"
    except Exception as e:d["status"]="STOP";d["error"]=repr(e)
    return name,d
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        files=dict(ex.map(one,EXPECTED.items()))
    x={"scope":"published_file_admission_schema_only","doi":"10.5281/zenodo.7126170","files":files,
       "verified":sum(f["status"]=="HASH_VERIFIED" for f in files.values())}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
    if x["verified"]!=len(EXPECTED):raise SystemExit(1)
if __name__=="__main__":main()
