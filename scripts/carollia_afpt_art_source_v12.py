"""V12 source gate; no raw source committed. Official API file content endpoint."""
import concurrent.futures, csv, hashlib, io, json, pathlib, urllib.request
P=pathlib.Path("results"); P.mkdir(exist_ok=True)
SOURCES={"WingMorph.txt":(7126170,"83c25901480df694ab049016955ce130"),
         "CarolliaWings.txt":(20738264,"a7bb180dc8db5e66a116ba55929fa8c5")}
def obtain(item):
    name,(record,md5)=item
    url=f"https://zenodo.org/api/records/{record}/files/{name}/content"
    d={"url":url,"expected_md5":md5}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"batter-research-source-audit/1.0"}),timeout=25) as r:
            b=r.read(100001)
        assert len(b)<100001 and hashlib.md5(b).hexdigest()==md5
        d.update(status="HASH_VERIFIED",bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        lines=b.decode("utf-8-sig").strip().splitlines()
        rows=[line.split() for line in lines]
        assert all(len(x)==len(rows[0]) for x in rows)
        ids=[row[0].strip('"') for row in rows[1:]]
        d.update(header=rows[0],rows=len(ids),exact_unique=len(set(ids)),casefold_unique=len({s.casefold() for s in ids}))
        if name=="CarolliaWings.txt":
            from collections import Counter
            h=[x.strip('"') for x in rows[0]]
            assert "ART" in h and "Sex" in h
            d["ART_counts"]=dict(Counter(r[h.index("ART")].strip('"') for r in rows[1:]))
            d["sex_counts"]=dict(Counter(r[h.index("Sex")].strip('"') for r in rows[1:]))
        (P/name).write_bytes(b)
        return name,d,ids
    except Exception as e:
        d.update(status="STOP",error=repr(e)); return name,d,[]
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: rows=list(ex.map(obtain,SOURCES.items()))
    result={"scope":"source_admission_no_biological_outcomes","files":{n:d for n,d,i in rows}}
    if all(d["status"]=="HASH_VERIFIED" for _,d,_ in rows):
        a,b=rows[0][2],rows[1][2]
        result["exact_id_overlap"]=len(set(a)&set(b))
        result["casefold_id_overlap"]=len({i.casefold() for i in a}&{i.casefold() for i in b})
        result["note"]="ID match is candidate overlap, not proof of identity; no automatic merging"
    (P/"carollia_source_v12.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
