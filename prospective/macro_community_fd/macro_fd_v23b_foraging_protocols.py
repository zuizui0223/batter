"""V23b: actual foraging monitoring protocol table census; no paired-height inference."""
import collections as C,hashlib,io,json,re
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
import openpyxl
from macro_fd_v23_protocol_registry import RID,NAME,MD5,get
OUT=Path("macro_fd_v23b_result.json")
PIN="b5597730000d23b2a5b1e87cfd11cbbf03c08619d8c420de82a169f8ced4b58e"
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V23B_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def text(c):
    return str(c.value).strip() if c.value is not None else ""
def norm(x):
    return re.sub(r"\s+"," ",x.strip().rstrip(":")).casefold()
def public_url(c):
    x=(c.hyperlink.target if c.hyperlink and c.hyperlink.target else text(c))
    p=urlsplit(x)
    if p.scheme not in ("https","http") or not p.netloc or p.username or p.password or "@" in x:return None
    # Preserve public landing path only; never export query parameters.
    return urlunsplit((p.scheme,p.netloc,p.path,"",""))
def main():
    o={"stage":"European foraging protocol table structural census","status":"START","limits":["program metadata only, not observed bats","no evidence of paired height from any rows","public links are candidate programme pages, not verified public raw files"]}
    try:
        j=json.loads(get(f"https://zenodo.org/api/records/{RID}",2*1024**2,o,"metadata"))
        assert int(j["id"])==RID
        f=[x for x in j["files"] if x["key"]==NAME]
        assert len(f)==1 and f[0]["checksum"]=="md5:"+MD5
        f=f[0];raw=get(f["links"].get("content") or f["links"]["self"],2*1024**2,o,"workbook")
        assert len(raw)==f["size"] and hashlib.md5(raw).hexdigest()==MD5 and hashlib.sha256(raw).hexdigest()==PIN
        wb=openpyxl.load_workbook(io.BytesIO(raw),read_only=False,data_only=True,keep_links=False)
        s=wb["Bat foraging activity monitorin"]
        h=[text(c) for c in s[1]]
        o["headers"]=[{"column":i+1,"name":x} for i,x in enumerate(h) if x]
        assert norm(h[0])=="country" and norm(h[6])=="method" and norm(h[27])=="link"
        # Read only designated programme-level metadata. Do not print other free text.
        candidates=[i for i,x in enumerate(h) if re.search(r"project|programme|program|protocol",x,re.I) and re.search(r"name|title",x,re.I) and not re.search(r"contact|person|author|coordinator|email|telephone",x,re.I)]
        o["project_name_field_candidates"]=[{"column":i+1,"name":h[i]} for i in candidates]
        country=None;records=[];unknown_country=0;empty_method=0;all_rows=0
        for row in s.iter_rows(min_row=2):
            a=[text(c) for c in row]
            if not any(a):continue
            all_rows+=1
            if a[0]:country=a[0]
            if not a[6]:empty_method+=1;continue
            if not country:unknown_country+=1
            m=a[6]
            if len(m)>250 or "@" in m:raise ValueError("unexpected method field")
            project=a[candidates[0]] if len(candidates)==1 else None
            if project and (len(project)>180 or "@" in project):project=None
            u=public_url(row[27])
            # Classification is a transparent method-text flag, not a claim of standardized data.
            acoustic=bool(re.search(r"acoustic|ultraso(?:und|nic)|bat\s*detector|echolocation|audio",m,re.I))
            fixed=bool(re.search(r"static|stationary|fixed|passive|automati[cs]|point|recorder",m,re.I))
            mobile=bool(re.search(r"transect|car[- ]?based|walking|mobile|driving",m,re.I))
            records.append({"row":row[0].row,"country":country,"method":m,"programme":project,"public_programme_url":u,"acoustic_method_flag":acoustic,"fixed_method_flag":fixed,"mobile_method_flag":mobile})
        o["source_rows"]={"nonempty":all_rows,"method_nonempty":len(records),"method_empty":empty_method,"country_unresolved":unknown_country,"countries":len({x["country"] for x in records if x["country"]}),"public_url_rows":sum(x["public_programme_url"] is not None for x in records)}
        o["method_counts"]=dict(C.Counter(x["method"] for x in records))
        o["acoustic_rows"]=sum(x["acoustic_method_flag"] for x in records)
        o["acoustic_fixed_flags"]=sum(x["acoustic_method_flag"] and x["fixed_method_flag"] for x in records)
        o["acoustic_programme_candidates"]=[x for x in records if x["acoustic_method_flag"] or x["fixed_method_flag"]]
        o["status"]="COMPLETE_CENSUS";save(o)
    except Exception as e:
        o["status"]="STOP";o["error_type"]=type(e).__name__
        if isinstance(e,ValueError):o["validation"]=str(e)[:150]
        save(o)
if __name__=="__main__":main()
