"""V39: public source admission only. No behavior or numeric altitude response fit."""
import csv,hashlib,io,json,pathlib,re,urllib.parse
import pandas as pd
from bayer_field_join_v17 import fetch
from acoustic_foraging_source_v35 import inspect_csv
BASE="https://datarepository.movebank.org/server/api"
DOI="10.5441/001/1.kk3bg2f4";HANDLE="10255/move.891"
BIT="8c34b3fd-d746-4716-bc67-8c770810d1dd"
SIZE=2462362;MD5="07d8e34a973c361dada5dc46da90ed80"
OUT=pathlib.Path("results/hurme_acoustic_source_v39.json")
HOSTS={"datarepository.movebank.org","www.datarepository.movebank.org"}
def js(url):
    raw,_=fetch(url,5_000_000);return json.loads(raw)
def safe(url):
    p=urllib.parse.urlsplit(url)
    assert p.scheme=="https" and p.hostname in HOSTS and p.path.startswith("/server/api/")
    assert not p.username and not p.password
    return url
def fields(m,k):return [str(x.get("value","")) for x in m.get(k,[])]
def link(o,k):
    u=o.get("_links",{}).get(k,{}).get("href")
    return safe(u) if u else None
def exact_item(o):
    m=o.get("metadata",{})
    vals=fields(m,"dc.identifier.doi")+fields(m,"dc.identifier.uri")+fields(m,"dc.identifier")
    return any(x.strip().lower().rstrip("/")==DOI or x.lower().rstrip("/").endswith("/"+DOI) for x in vals) or str(o.get("handle","")).rstrip("/")==HANDLE
def struct(raw):
    x=inspect_csv(raw)
    d=pd.read_csv(io.BytesIO(raw),sep=x["delimiter"],dtype=str,keep_default_na=False,encoding="utf-8-sig")
    cols={re.sub(r"[^a-z0-9]+","_",c.lower()).strip("_"):c for c in d.columns}
    x["candidate_fields"]={k:[c for c in d.columns if re.search(p,c,re.I)] for k,p in {
      "altitude":"height|altitude|elevation|vertical",
      "audio_or_buzz":"buzz|sound|audio|acoustic|ultrasonic|call",
      "behavior":"behavio|forag|commut|state|prey|feed|attack",
      "quality":"accuracy|hdop|vdop|satellite|quality|visible",
      "sampling":"duty|sampling|duration|interval|effort"}.items()}
    x["candidate_nonblank"]={c:int(d[c].str.strip().ne("").sum()) for c in set(sum(x["candidate_fields"].values(),[]))}
    for k in ("individual_local_identifier","animal_id","individual_id","tag_local_identifier","tag_id"):
        if k in cols:x[k+"_distinct"]=int(d[cols[k]].str.strip().replace("",pd.NA).nunique())
    if "timestamp" in cols:
        t=pd.to_datetime(d[cols["timestamp"]],format="mixed",utc=True,errors="coerce")
        x["valid_timestamps"]=int(t.notna().sum())
        x["timestamp_min"]=str(t.min());x["timestamp_max"]=str(t.max())
    return x
def main():
    o={"scope":"public source and structural annotation audit only","doi":DOI}
    try:
        dc=js("https://api.datacite.org/dois/"+DOI)["data"]["attributes"]
        assert dc["doi"].lower()==DOI and "Acoustic evaluation" in dc["titles"][0]["title"]
        assert any(z["relatedIdentifier"].lower()=="10.1186/s40462-019-0163-7" for z in dc["relatedIdentifiers"])
        assert any("creativecommons.org/licenses/by-nc/4.0" in z.get("rightsUri","") for z in dc["rightsList"])
        assert urllib.parse.urlsplit(dc["url"]).path.rstrip("/").endswith("/"+HANDLE)
        o["license"]="CC BY-NC 4.0";o["datacite_url"]=dc["url"]
        raw,_=fetch(BASE+"/core/bitstreams/"+BIT+"/content",SIZE)
        assert len(raw)==SIZE and hashlib.md5(raw).hexdigest()==MD5
        o["pinned_original"]={"bytes":SIZE,"md5":MD5,"sha256":hashlib.sha256(raw).hexdigest(),"schema":struct(raw)}
        o["status"]="PINNED_GPS_VERIFIED"
        item=None;errors=[]
        try:
            meta=js(BASE+"/core/bitstreams/"+BIT)
            assert meta.get("uuid")==BIT and meta["sizeBytes"]==SIZE and meta["checkSum"]["value"].lower()==MD5
            bu=js(link(meta,"bundle") or BASE+"/core/bitstreams/"+BIT+"/bundle")
            item=js(link(bu,"item") or BASE+"/core/bundles/"+bu["uuid"]+"/item")
            assert exact_item(item)
            o["item_route"]="bitstream-bundle-item"
        except Exception as e:
            errors.append(repr(e));item=None
        if item is None:
            try:
                candidate=js(BASE+"/pid/find?"+urllib.parse.urlencode({"id":HANDLE}))
                assert exact_item(candidate)
                item=candidate;o["item_route"]="exact_handle"
            except Exception as e:errors.append(repr(e))
        if item is None:
            o.update(status="PINNED_GPS_VERIFIED_PARENT_UNRESOLVED",parent_errors=errors);return o
        uid=item["uuid"];o["item_uuid"]=uid
        m=item.get("metadata",{})
        o["item_rights"]=fields(m,"dc.rights")+fields(m,"dc.rights.uri")
        assert any("creativecommons.org/licenses/by-nc/4.0" in s.lower() for s in o["item_rights"])
        bundles=js(BASE+"/core/items/"+uid+"/bundles?size=100").get("_embedded",{}).get("bundles",[])
        fs=[]
        for bu in bundles:
            if bu.get("name")=="ORIGINAL":
                fs+=js(BASE+"/core/bundles/"+bu["uuid"]+"/bitstreams?size=100").get("_embedded",{}).get("bitstreams",[])
        assert any(f.get("uuid")==BIT for f in fs)
        o["original_files"]=[]
        for f in fs:
            entry={k:f.get(k) for k in ("uuid","name","sizeBytes","checkSum")};o["original_files"].append(entry)
            name=f["name"].lower()
            if f["sizeBytes"]>10_000_000 or not name.endswith((".csv",".txt",".tsv")):continue
            try:
                ck=f["checkSum"];algorithm=ck["checkSumAlgorithm"].lower().replace("-","")
                assert algorithm in ("md5","sha1","sha256")
                b=raw if f["uuid"]==BIT else fetch(BASE+"/core/bitstreams/"+f["uuid"]+"/content",f["sizeBytes"])[0]
                assert len(b)==f["sizeBytes"] and hashlib.new(algorithm,b).hexdigest()==ck["value"].lower()
                entry.update(status="HASH_VERIFIED",sha256=hashlib.sha256(b).hexdigest())
                if name.endswith((".csv",".tsv")):entry["schema"]=struct(b)
                else:
                    lines=b.decode("utf-8-sig",errors="replace").splitlines()
                    hits=[l.strip() for l in lines if re.search(r"buzz|acoustic|audio|altitude|height|sampling|duty cycle",l,re.I)]
                    # Generic README fields are not ground-truth behavior annotations.
                    entry["definition_line_count"]=len(hits)
                    entry["mentions_buzz"]=any(re.search(r"buzz",x,re.I) for x in hits)
                    entry["mentions_audio"]=any(re.search(r"audio|acoustic",x,re.I) for x in hits)
                    entry["mentions_altitude"]=any(re.search(r"altitude|height",x,re.I) for x in hits)
            except Exception as e:entry.update(status="STOP",error=repr(e))
        o["status"]="VERIFIED_PARENT_AND_FILE_INVENTORY"
    except Exception as e:o.update(status="STOP",error=repr(e))
    return o
if __name__=="__main__":
    r=main();OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n");print(OUT.read_text())
