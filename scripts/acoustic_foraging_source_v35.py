"""V35: source admission only; no ecological outcome fit or raw track publication."""
import concurrent.futures as cf,csv,hashlib,io,json,pathlib,re,urllib.parse
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/acoustic_foraging_source_v35.json")
def js(url):
    return json.loads(fetch(url,5_000_000)[0])
def inspect_csv(raw):
    s=raw.decode("utf-8-sig")
    dialect=csv.Sniffer().sniff(s[:30000],delimiters=",;\t")
    r=csv.reader(io.StringIO(s),dialect);h=next(r);n=0;bad=0
    for row in r:
        if not row:continue
        n+=1;bad+=len(row)!=len(h)
    return {"headers":h,"delimiter":dialect.delimiter,"rows":n,"unequal_width_rows":bad,
       "height_fields":[c for c in h if re.search(r"height|altitude|elevation|(^|[_. -])z($|[_. -])",c,re.I)],
       "buzz_fields":[c for c in h if re.search(r"buzz|attack|prey|feed|acoustic|forag",c,re.I)],
       "group_fields":[c for c in h if re.search(r"site|traj|animal|individual|session|species|guild|tag|timestamp|date|time",c,re.I)]}
def zenodo():
    doi="10.5281/zenodo.10149959";name="data_bats_barre et al 2023.csv";expected="60ce63b79fd8a5b9bc4771997de97839"
    o={"doi":doi,"scope":"3D acoustic positions and buzz score candidate"}
    try:
        m=js("https://zenodo.org/api/records/10149959")
        assert m["id"]==10149959 and (m.get("doi")==doi or m["metadata"].get("doi")==doi)
        meta=m["metadata"];lic=meta.get("license") or meta.get("rights")
        o.update(title=meta["title"],license=lic,version=meta.get("version"))
        assert re.search(r"cc[- ]?(?:by|zero|0)",json.dumps(lic),re.I),"license not admitted"
        f=[f for f in m["files"] if f["key"]==name];assert len(f)==1
        f=f[0];assert f["checksum"]=="md5:"+expected and f["size"]<=10_000_000
        url="https://zenodo.org/api/records/10149959/files/"+urllib.parse.quote(name,safe="")+"/content"
        b,_=fetch(url,f["size"])
        assert len(b)==f["size"] and hashlib.md5(b).hexdigest()==expected
        o.update(status="HASH_VERIFIED_CSV",file=name,bytes=len(b),md5=expected,sha256=hashlib.sha256(b).hexdigest(),schema=inspect_csv(b))
    except Exception as e:o.update(status="STOP",error=repr(e))
    return o
def fields(m,k):return [v.get("value","") for v in m.get(k,[])]
def hurme():
    doi="10.5441/001/1.kk3bg2f4";base="https://datarepository.movebank.org/server/api"
    o={"doi":doi,"scope":"existing main inventory, acoustic behavior crosswalk, not independent replication"}
    try:
        a=js("https://api.datacite.org/dois/"+doi)["data"]["attributes"]
        assert a["doi"].lower()==doi
        o["datacite"]={k:a.get(k) for k in ("titles","url","rightsList","relatedIdentifiers")}
        x=js(base+"/discover/search/objects?"+urllib.parse.urlencode({"query":doi,"dsoType":"item","size":20}))
        rr=x.get("_embedded",{}).get("searchResult",{}).get("_embedded",{}).get("objects",[])
        found=[r.get("_embedded",{}).get("indexableObject",{}) for r in rr]
        selected=[]
        for i in found:
            m=i.get("metadata",{});z=fields(m,"dc.identifier.doi")+fields(m,"dc.identifier.uri")+fields(m,"dc.identifier")
            if any(s.lower().rstrip("/")==doi or s.lower().rstrip("/").endswith("/"+doi) for s in z):selected.append(i)
        assert len(selected)==1
        uid=selected[0]["uuid"];m=js(base+"/core/items/"+uid)["metadata"]
        rights=fields(m,"dc.rights")+fields(m,"dc.rights.uri")
        o.update(item_uuid=uid,rights=rights)
        assert re.search(r"creativecommons.org/(?:licenses/by(?:-nc)?/|publicdomain/zero/)", " ".join(rights),re.I),"license not admitted"
        bundles=js(base+"/core/items/"+uid+"/bundles?size=100").get("_embedded",{}).get("bundles",[])
        files=[]
        for bu in bundles:
            if bu["name"]!="ORIGINAL":continue
            files+=js(base+"/core/bundles/"+bu["uuid"]+"/bitstreams?size=100").get("_embedded",{}).get("bitstreams",[])
        assert files
        o["files"]=[]
        for f in files:
            r={k:f.get(k) for k in ("uuid","name","sizeBytes","checkSum")};o["files"].append(r)
            if f["sizeBytes"]>10_000_000 or not f["name"].lower().endswith((".csv",".tsv",".txt")):continue
            try:
                ck=f["checkSum"];algorithm=ck["checkSumAlgorithm"].lower().replace("-","")
                assert algorithm in ("md5","sha1","sha256")
                b,_=fetch(base+"/core/bitstreams/"+f["uuid"]+"/content",f["sizeBytes"])
                assert len(b)==f["sizeBytes"] and hashlib.new(algorithm,b).hexdigest()==ck["value"]
                if f["uuid"]=="8c34b3fd-d746-4716-bc67-8c770810d1dd":
                    assert len(b)==2462362 and hashlib.md5(b).hexdigest()=="07d8e34a973c361dada5dc46da90ed80"
                r.update(status="HASH_VERIFIED",sha256=hashlib.sha256(b).hexdigest())
                if f["name"].lower().endswith((".csv",".tsv")):r["schema"]=inspect_csv(b)
            except Exception as e:r.update(status="STOP",error=repr(e))
        o["status"]="ORIGINAL_FILE_AUDIT"
    except Exception as e:o.update(status="STOP",error=repr(e))
    return o
def main():
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        f=ex.submit(zenodo);g=ex.submit(hurme)
        result={"scope":"independent acoustic source admission, no response fit","barre":f.result(),"hurme":g.result()}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
