"""V18: quality metadata only and original STRI weather file provenance.
No HR response values, flight coordinates, individual IDs or raw files redistributed.
"""
import concurrent.futures as cf, hashlib, json, pathlib, re, urllib.parse
from bayer_field_join_v17 import original, table, fetch
DOIS={"direction":"10.60635/C3VD0T","speed":"10.60635/C3QP70"}
OUT=pathlib.Path("results/bayer_weather_qi_v18.json")
def getjson(url):
    b,_=fetch(url,8_000_000)
    return json.loads(b)
def weather(pair):
    key,doi=pair
    result={"doi":doi}
    try:
        a=getjson("https://api.datacite.org/dois/"+doi)["data"]["attributes"]
        assert a["doi"].casefold()==doi.casefold()
        result["datacite"]={k:a.get(k) for k in ("titles","url","rightsList","publicationYear","dates","descriptions","publisher","version")}
        url=a["url"]; parsed=urllib.parse.urlsplit(url)
        origin=parsed.scheme+"://"+parsed.netloc
        # Source station links resolve to a persistent DOI on a Dataverse repository.
        endpoint=origin+"/api/datasets/:persistentId/?"+urllib.parse.urlencode({"persistentId":"doi:"+doi})
        x=getjson(endpoint)
        data=x.get("data",{}); v=data.get("latestVersion",{})
        if not v:raise ValueError("No Dataverse latest version")
        assert str(data.get("persistentUrl","")).lower().endswith(doi.lower()) or str(data.get("identifier","")).lower()==doi.split("/")[-1].lower()
        result["provider_version"]={k:v.get(k) for k in ("versionNumber","versionMinorNumber","versionState","releaseTime","license","termsOfUse")}
        citation=v.get("metadataBlocks",{}).get("citation",{}).get("fields",[])
        result["provider_citation"]=[f for f in citation if f.get("typeName") in ("title","dsDescription","timePeriodCovered","dateOfCollection","dataSources","otherId")]
        result["files"]=[{"label":f.get("label"),"restricted":f.get("restricted"),"description":f.get("description"),
            "dataFile":{k:f.get("dataFile",{}).get(k) for k in ("id","filename","contentType","filesize","checksum","originalFileName")}} for f in v.get("files",[])]
        result["status"]="METADATA_READ"
    except Exception as e: result.update(status="SOURCE_STOP",error=repr(e))
    return key,result
def qi():
    rawh,_=original("hr");rawr,_=original("ref")
    h=table(rawh);r=table(rawr)
    spec=h["tag-tech-spec"].astype(str).str.strip()
    # Report quality-like category values only; unexpected free text gets hashed.
    levels={}
    for x,n in spec.value_counts(dropna=False).items():
        k=x if re.fullmatch(r"(?i)(?:(?:QI|quality(?:\s*index)?)\s*[:=]?\s*)?[0-3](?:\.0)?",x) else "other_"+hashlib.sha256(x.encode()).hexdigest()[:12]
        levels[k]=int(n)
    evidence=[]
    for c in ["tag-settings","tag-comments","deployment-comments","animal-comments","attachment-comments","duty-cycle","deploy-on-measurements"]:
        if c not in r:continue
        for x in r[c].unique():
            # Extract only clauses specifically defining quality or time, no unrelated identifiers or coordinates.
            for line in re.split(r"[\n;]",x):
                if re.search(r"quality index|quality score|tag.tech.spec|\bQI\b|time.?zone|\bUTC\b|\bEST\b",line,re.I):
                    if re.search(r"latitude|longitude|PIT|Phyl\s*\d+|\d{6,}",line,re.I):continue
                    evidence.append({"column":c,"text":line[:400]})
    mass=r["animal-mass"].astype(str)
    return {"levels":levels,"reference_semantics":evidence[:50],"mass_unit_suffixes":sorted({re.sub(r"[\d. +,-]","",x) for x in mass}),
            "note":"Exact 0–3 category match alone does not establish documented QI semantics. Do not fit HR until confirmed or explicitly sensitivity-only."}
def main():
    result={"scope":"metadata only, no outcome fit","article":"10.1242/jeb.251521"}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        futures=[ex.submit(weather,p) for p in DOIS.items()]; q=ex.submit(qi)
        result["weather"]=dict(f.result() for f in futures)
        try:result["heart_rate_quality"]=q.result()
        except Exception as e:result["heart_rate_quality"]={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
