"""Independent 64-site Black Forest bats × insects: publisher ORIGINAL source gate.

Official Dryad REST v2 metadata, then one canonical whole-dataset public
download attempt. Verify all original file bytes against publisher digests
before reading only XLSX sheet names and first-row headers. NEVER save
original site rows, acoustic activity, prey quantities or site locations.

As of previous Ducke tests, /api/v2/files/<id>/download returns HTTP401;
this tries the *different*, documented official /datasets/<DOI>/download.
Do not try mirrors or retry the same blocked endpoint repeatedly.
"""
from __future__ import annotations
import argparse,hashlib,io,json,pathlib,re,urllib.parse,urllib.request,zipfile
import xml.etree.ElementTree as ET

DOI="doi:10.5061/dryad.xksn02vr1"
BASE="https://datadryad.org"
ENTRY=BASE+"/api/v2/datasets/"+urllib.parse.quote(DOI,safe="")
DOWNLOAD=ENTRY+"/download"
EXPECTED={"Hendel_etal_2024_Data_DRYAD.xlsx","README.md"}
API_STATUS="PUBLISHER_VERSION_FILELIST_VERIFIED"
CONTENT_STATUS="ORIGINAL_PUBLISHER_XLSX_CHECKSUM_AND_HEADERS_VERIFIED"
MAX_METADATA=2_000_000
MAX_ARCHIVE=180_000
MAX_XLSX_UNCOMPRESSED=25_000_000
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def official_api(href):
    if not isinstance(href,str) or not href: raise ValueError("SOURCE_API_URL_MISSING")
    url=urllib.parse.urljoin(BASE,href)
    p=urllib.parse.urlparse(url)
    if (p.scheme!="https" or p.hostname!="datadryad.org" or
        p.username or p.password or not p.path.startswith("/api/v2/")):
        raise ValueError("STOP_NONOFFICIAL_SOURCE_ENDPOINT")
    return url


def get_json(url):
    target=official_api(url)
    request=urllib.request.Request(target,headers={
        "Accept":"application/json","User-Agent":"batter-independent-hendel-sourcegate/1.0"})
    with urllib.request.urlopen(request,timeout=35) as response:
        if response.status!=200 or official_api(response.url)!=target:
            raise RuntimeError("STOP_SOURCE_METADATA_REDIRECT_OR_NON200")
        raw=response.read(MAX_METADATA+1)
    if len(raw)>MAX_METADATA:raise RuntimeError("STOP_SOURCE_METADATA_TOO_LARGE")
    val=json.loads(raw.decode("utf-8"))
    if not isinstance(val,dict):raise RuntimeError("STOP_METADATA_JSON_NOT_OBJECT")
    return val


def link(obj,key):
    return official_api(obj["_links"][key]["href"])


def metadata(fetch=get_json):
    d=fetch(ENTRY)
    if str(d.get("identifier","")).lower()!=DOI.lower():
        raise ValueError("STOP_SOURCE_DOI_MISMATCH")
    ver=fetch(link(d,"stash:version"))
    if not isinstance(ver,dict) or not ver.get("id"):
        raise ValueError("STOP_SOURCE_VERSION_UNVERIFIED")
    url=link(ver,"stash:files")
    files={}
    seen=set()
    total=None
    pages=0
    while url:
        pages+=1
        if pages>10:raise ValueError("STOP_SOURCE_FILE_PAGINATION")
        page=fetch(url)
        ct=page.get("total")
        if type(ct) is not int:raise ValueError("STOP_SOURCE_TOTAL_NOT_INTEGER")
        if total is None:total=ct
        elif ct!=total:raise ValueError("STOP_SOURCE_TOTAL_DRIFT")
        records=page.get("_embedded",{}).get("stash:files")
        if not isinstance(records,list):raise ValueError("STOP_SOURCE_NO_FILE_RECORD_LIST")
        for item in records:
            name=item.get("path")
            size=item.get("size")
            identifier=item.get("_links",{}).get("self",{}).get("href")
            parsed=urllib.parse.urlparse(official_api(identifier))
            match=re.fullmatch(r"/api/v2/files/([0-9]+)",parsed.path)
            if (not match or not isinstance(name,str) or
                type(size) is not int or size<=0 or name in files):
                raise ValueError("STOP_SOURCE_FILE_INVENTORY_INVALID")
            digest=item.get("digest")
            dtype=str(item.get("digestType") or "").lower().replace("-","")
            if dtype not in ("sha256","md5") or not isinstance(digest,str):
                raise ValueError("STOP_PUBLISHER_FILE_DIGEST_MISSING")
            if not re.fullmatch(r"[0-9a-fA-F]{64}" if dtype=="sha256" else
                                r"[0-9a-fA-F]{32}",digest):
                raise ValueError("STOP_SOURCE_DIGEST_BAD_LENGTH")
            files[name]={"public_file_id":int(match.group(1)),
                         "original_file_bytes":size,
                         "original_digest_type":dtype,
                         "original_digest":digest.lower()}
        nxt=page.get("_links",{}).get("next",{})
        url=official_api(nxt["href"]) if isinstance(nxt,dict) and isinstance(nxt.get("href"),str) else None
    if set(files)!=EXPECTED or len(files)!=total:
        raise ValueError("STOP_UNEXPECTED_PUBLISHED_FILE_ROSTER")
    if type(d.get("storageSize")) is int and sum(f["original_file_bytes"] for f in files.values())!=d["storageSize"]:
        raise ValueError("STOP_PUBLISHED_STORAGE_SUM_DRIFT")
    return {
        "status":API_STATUS,"doi":DOI,"dataset_version_id":ver["id"],
        "version_number":ver.get("versionNumber"),
        "publisher_files":files,
        "source_biological_rows_read":False
    }


def xlsx_headers(xlsx):
    with zipfile.ZipFile(io.BytesIO(xlsx)) as archive:
        entries=archive.infolist()
        if len(entries)>250 or sum(r.file_size for r in entries)>MAX_XLSX_UNCOMPRESSED:
            raise ValueError("STOP_SOURCE_XLSX_DECOMPRESSION")
        names={z.filename for z in entries}
        if ("xl/workbook.xml" not in names or "[Content_Types].xml" not in names or
            any("vbaProject" in n or "externalLinks" in n for n in names)):
            raise ValueError("STOP_ORIGINAL_XLSX_SCHEMA_UNSAFE")
        root=ET.fromstring(archive.read("xl/workbook.xml"))
        sheets=root.findall(".//"+NS+"sheets/"+NS+"sheet")
        if len(sheets)!=1:
            raise ValueError("STOP_SOURCE_WORKSHEET_COUNT_NOT_ONE")
        shared=[]
        if "xl/sharedStrings.xml" in names:
            text=ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared=["".join(t.text or "" for t in r.iter(NS+"t"))
                    for r in text.findall(NS+"si")]
        if "xl/worksheets/sheet1.xml" not in names:
            raise ValueError("STOP_SOURCE_FIRST_SHEET_NOT_FOUND")
        ws=ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        header=ws.find(".//"+NS+"sheetData/"+NS+"row")
        if header is None:raise ValueError("STOP_SOURCE_EMPTY_HEADER")
        names_out=[]
        for cell in header.findall(NS+"c"):
            t=cell.get("t")
            if t=="s":
                x=cell.find(NS+"v")
                if x is None or not (x.text or "").isdigit() or int(x.text)>=len(shared):
                    raise ValueError("STOP_SOURCE_SHARED_HEADER_INVALID")
                label=shared[int(x.text)]
            elif t=="inlineStr":
                label="".join(v.text or "" for v in cell.iter(NS+"t"))
            else:
                raise ValueError("STOP_SOURCE_HEADER_NOT_STRING")
            label=label.strip()
            if not label or len(label)>100 or label in names_out:
                raise ValueError("STOP_SOURCE_BAD_HEADER_VALUE")
            names_out.append(label)
        desired={"plotID","mothcount","carabidae","SRE","MRE","Ppip","LRE",
                 "elevation","ndsm_sd","Opn_mean","DOY","temp_min"}
        if not desired.issubset(names_out):
            raise ValueError("STOP_REQUIRED_PREY_ACTIVITY_FOREST_FIELDS_ABSENT")
        return {"sheet_names":[r.get("name") for r in sheets],
                "original_source_headers":names_out,
                "predeclared_key_fields_present":sorted(desired),
                "source_64_field_rows_opened":False}


def get_publisher_archive():
    request=urllib.request.Request(DOWNLOAD,headers={
        "Accept":"application/zip, application/octet-stream",
        "User-Agent":"batter-independent-hendel-sourcegate/1.0"})
    with urllib.request.urlopen(request,timeout=40) as response:
        if response.status!=200:
            raise RuntimeError("STOP_SOURCE_CANONICAL_DOWNLOAD_HTTP_NON200")
        final=urllib.parse.urlparse(response.url)
        if final.scheme!="https" or not final.hostname:
            raise RuntimeError("STOP_ORIGINAL_DOWNLOAD_REDIRECT_INSECURE")
        body=response.read(MAX_ARCHIVE+1)
    if len(body)>MAX_ARCHIVE or not body.startswith(b"PK\x03\x04"):
        raise RuntimeError("STOP_ORIGINAL_ARCHIVE_MISSING_OR_OVERSIZE")
    return body


def original_archive_audit(meta,fetch=get_publisher_archive):
    if meta.get("status")!=API_STATUS:raise ValueError("STOP_UNAUTHENTICATED_SOURCE_METADATA")
    blob=fetch()
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        infos=z.infolist()
        if len(infos)>100 or sum(e.file_size for e in infos)>MAX_XLSX_UNCOMPRESSED:
            raise ValueError("STOP_SOURCE_BUNDLE_ZIP_BOMB")
        if any(e.filename.startswith("/") or ".." in e.filename.split("/") for e in infos):
            raise ValueError("STOP_ORIGINAL_ZIP_MEMBER_PATH")
        items={}
        for entry in infos:
            if entry.is_dir():continue
            name=pathlib.PurePosixPath(entry.filename).name
            if name in EXPECTED:
                if name in items:raise ValueError("STOP_DUPLICATE_SOURCE_ORIGINAL")
                raw=z.read(entry)
                m=meta["publisher_files"][name]
                if len(raw)!=m["original_file_bytes"]:
                    raise ValueError("STOP_ORIGINAL_BYTE_SIZE_MISMATCH")
                kind=m["original_digest_type"]
                actual=getattr(hashlib,kind)(raw).hexdigest()
                if actual.lower()!=m["original_digest"]:
                    raise ValueError("STOP_ORIGINAL_PUBLISHER_DIGEST_MISMATCH")
                items[name]=raw
        if set(items)!=EXPECTED:raise ValueError("STOP_CANONICAL_ARCHIVE_MISSING_SOURCE_FILES")
        head=xlsx_headers(items["Hendel_etal_2024_Data_DRYAD.xlsx"])
        return {"status":CONTENT_STATUS,"source_doi":DOI,
                "source_file_digest_publisher_verified":True,
                "source_xlsx_sha256":hashlib.sha256(items["Hendel_etal_2024_Data_DRYAD.xlsx"]).hexdigest(),
                "original_archive_bytes_saved":False,
                "headers_only":head,
                "source_outcomes_read":False,
                "guild_activity_moth_preyscale_effect":None}


def run():
    try:
        meta=metadata()
    except Exception as e:
        return {"status":"SOURCE_METADATA_STOP",
                "reason":(type(e).__name__+":"+str(e))[:210],
                "doi":DOI,"original_bat_data_opened":False,
                "external_biological_transfer_gain":None}
    try:
        content=original_archive_audit(meta)
    except Exception as e:
        content={"status":"SOURCE_CONTENT_STOP","reason":(type(e).__name__+":"+str(e))[:210],
                 "original_bat_data_opened":False,"external_biological_transfer_gain":None}
    return {"schema":"batter.hendel_independent_prey_bat_activity.v1",
            "metadata":meta,"original_source_attempt":content,
            "original_bat_activity_values_read":False,
            "external_biological_transfer_gain":None}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="prospective/resource_behavior_sdm/hendel_external_original_source_receipt_v1.json")
    v=ap.parse_args()
    result=run()
    target=pathlib.Path(v.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("HENDEL_META",result.get("metadata",{}).get("status",result.get("status")))
    print("HENDEL_ORIGINAL",result.get("original_source_attempt",{}).get("status","STOP"))
    if "reason" in result.get("original_source_attempt",{}):
        print("HENDEL_STOP_REASON",result["original_source_attempt"]["reason"])
    return 0 if result.get("original_source_attempt",{}).get("status")==CONTENT_STATUS else 3


if __name__=="__main__":
    raise SystemExit(main())
