"""V16 public field-data admission; DOI exact match, license and file metadata before response extraction."""
import concurrent.futures, csv, hashlib, io, json, pathlib, urllib.parse, urllib.request
BASE="https://datarepository.movebank.org/server/api"
DOI="10.5441/001/1.754"
OLD={"10.5441/001/1.282","10.5441/001/1.321","10.5441/001/1.322"}
OUT=pathlib.Path("results/bayer_field_source_v16.json")
def get(url,limit=2_000_000):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"batter-source-audit/1.0","Accept":"*/*"}),timeout=30) as r:
        b=r.read(limit+1)
        if len(b)>limit:raise ValueError("size limit")
        return b,r.geturl()
def js(url):return json.loads(get(url)[0])
def fields(m,key):return [v.get("value","") for v in m.get(key,[])]
def items(x):return x.get("_embedded",{}).get("searchResult",{}).get("_embedded",{}).get("objects",[])
def main():
    result={"scope":"field_source_admission_no_ecological_outcome","doi":DOI,"prior_used_dois":sorted(OLD)}
    try:
        a=js("https://api.datacite.org/dois/"+DOI)["data"]["attributes"]
        assert a["doi"].lower()==DOI.lower()
        result["datacite"]={k:a.get(k) for k in ("doi","titles","publicationYear","url","rightsList","relatedIdentifiers","descriptions")}
    except Exception as e:result["datacite_error"]=repr(e)
    try:
        queries=[DOI, "Heart rate supports accelerometry"]
        selected=None
        for q in queries:
            x=js(BASE+"/discover/search/objects?"+urllib.parse.urlencode({"query":q,"dsoType":"item","size":20}))
            found=[o.get("_embedded",{}).get("indexableObject",{}) for o in items(x)]
            result.setdefault("search_candidates",[]).append({"query":q,"items":[{"uuid":i.get("uuid"),"name":i.get("name"),"doi":fields(i.get("metadata",{}),"dc.identifier.doi")} for i in found]})
            for i in found:
                m=i.get("metadata",{})
                identifiers=fields(m,"dc.identifier.doi")+fields(m,"dc.identifier.uri")+fields(m,"dc.identifier")
                if any(z.lower().rstrip("/")==DOI or z.lower().rstrip("/").endswith("/"+DOI) for z in identifiers):
                    selected=i;break
            if selected:break
        if not selected:raise ValueError("No exact DOI match in public search")
        uuid=selected["uuid"]; x=js(BASE+"/core/items/"+uuid)
        m=x.get("metadata",{})
        result["item"]={"uuid":uuid,"name":x.get("name"),"rights":fields(m,"dc.rights"),"rights_uri":fields(m,"dc.rights.uri"),"doi":fields(m,"dc.identifier.doi"),"date":fields(m,"dc.date.issued")}
        rights=" ".join(result["item"]["rights"]+result["item"]["rights_uri"]).lower()
        if "creativecommons.org/licenses/by-nc/4.0" not in rights:
            raise ValueError("Expected specific CC BY-NC 4.0 license not verified")
        result["usage"]="Noncommercial scholarly source audit; attribution retained; no original records redistributed"
        bundles=js(BASE+"/core/items/"+uuid+"/bundles?size=100").get("_embedded",{}).get("bundles",[])
        files=[]
        for b in bundles:
            if b.get("name","").upper()!="ORIGINAL":continue
            stream=js(BASE+"/core/bundles/"+b["uuid"]+"/bitstreams?size=100").get("_embedded",{}).get("bitstreams",[])
            for f in stream:
                item={k:f.get(k) for k in ("uuid","name","sizeBytes","checkSum")}
                item["content_url"]=BASE+"/core/bitstreams/"+f["uuid"]+"/content"
                files.append(item)
        result["files"]=files
        if not files:raise ValueError("No ORIGINAL files")
        for f in files:
            if not f["name"].lower().endswith(".csv") or not isinstance(f["sizeBytes"],int) or f["sizeBytes"]>60_000_000:continue
            try:
                b,_=get(f["content_url"],60_000_000)
                ck=f["checkSum"] or {}
                algorithm=ck.get("checkSumAlgorithm","").lower().replace("-","")
                if algorithm not in ("md5","sha256","sha1"):raise ValueError("No supported publisher checksum")
                assert hashlib.new(algorithm,b).hexdigest()==ck["value"].lower() and len(b)==f["sizeBytes"]
                reader=csv.reader(io.StringIO(b.decode("utf-8-sig")))
                h=next(reader)
                f.update(status="HASH_VERIFIED",sha256=hashlib.sha256(b).hexdigest(),headers=h,n_rows=sum(1 for _ in reader))
            except Exception as e:f.update(status="STOP",error=repr(e))
        result["status"]="PUBLIC_ITEM_METADATA_READ" if all(f.get("status")=="HASH_VERIFIED" for f in files if f["name"].lower().endswith(".csv") and f["sizeBytes"]<=60_000_000) else "PUBLIC_ITEM_PARTIAL"
    except Exception as e:result.update(status="SOURCE_STOP",error=repr(e))
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
