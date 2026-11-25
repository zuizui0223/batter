"""V43: exact-DOI public metadata only, no raw data or response fitting."""
import concurrent.futures as cf, json,pathlib,urllib.error
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/functional_space_external_v43.json")
CANDIDATES=[
 ("roeleke","10.4228/ZALF.DK.112","landscape structure influences","10.1111/oik.07158"),
 ("stidsholt","10.17632/smx7n93syw.1","high risk-high gain","10.7554/elife.84190"),
 ("niga_reserve","10.5061/dryad.mgqnk993n","nyctalus aviator","10.1098/rsos.230035")]
def js(url):return json.loads(fetch(url,5_000_000)[0])
def inspect(spec):
    key,doi,phrase,article=spec
    out={"candidate":key,"doi":doi,"article":article}
    try:
        a=js("https://api.datacite.org/dois/"+doi)["data"]["attributes"]
        assert a["doi"].lower()==doi.lower()
        titles=[t["title"] for t in a.get("titles",[])]
        match=phrase in " ".join(titles).lower()
        out.update(status="METADATA_VERIFIED" if match else "STOP_TITLE_REVIEW",titles=titles,url=a.get("url"),rights=a.get("rightsList",[]),related_identifiers=a.get("relatedIdentifiers",[]),sizes=a.get("sizes"),formats=a.get("formats"),version=a.get("version"))
        if not match:return out
        if key=="stidsholt":
            try:
                p=js("https://data.mendeley.com/public-api/datasets/smx7n93syw/files?version=1")
                items=p if isinstance(p,list) else p.get("files",p.get("data",[]))
                assert isinstance(items,list) and items
                out["public_file_inventory"]=[{"name":f.get("filename",f.get("name")),"size":f.get("size"),"content_type":f.get("content_type"),"id":f.get("id"),"content_details":{k:v for k,v in (f.get("content_details") or {}).items() if k in ("sha256_hash","size","content_type","checksum")}} for f in items]
                out["inventory_status"]="PUBLIC_LIST_RETRIEVED"
            except Exception as e:out["inventory_status"]="STOP_FILE_LIST";out["inventory_error"]=repr(e)
        else:out["inventory_status"]="METADATA_ONLY; inspect repository-provided exact file links"
    except Exception as e:out.update(status="STOP_METADATA",error=repr(e))
    return out
def run():
    with cf.ThreadPoolExecutor(max_workers=3) as ex:r=list(ex.map(inspect,CANDIDATES))
    return {"scope":"independent source admission; no numerical outcomes examined","candidates":r,"status":"REVIEW_REQUIRED"}
if __name__=="__main__":
    o=run();OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(o,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
