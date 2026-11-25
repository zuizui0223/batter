"""V46 known-position acoustic calibration: immutable archive metadata gate only."""
import hashlib,io,json,re,stat
from collections import Counter
from pathlib import PurePosixPath
import py7zr,requests
from roost_fd_source_audit_v2 import OUT
RECORD=7414956
NAME="Plecotus_amplitude.7z"
MD5="145114d5ce1ad1f33082da5aed599f6b"
CAP=30_000_000
HEAD={"User-Agent":"batter-independent-calibration-audit-v46/1.0"}
def run():
    r=requests.get(f"https://zenodo.org/api/records/{RECORD}",headers=HEAD,timeout=(10,30))
    r.raise_for_status();j=r.json()
    assert int(j["id"])==RECORD
    assert j["metadata"]["doi"]=="10.5281/zenodo.7414956"
    assert j["metadata"].get("access_right")=="open"
    m=[f for f in j["files"] if f["key"]==NAME];assert len(m)==1
    f=m[0];assert f["checksum"]=="md5:"+MD5
    size=int(f["size"]);assert 0<size<=CAP
    b=bytearray()
    with requests.get(f["links"]["self"],headers=HEAD,stream=True,timeout=(15,90)) as rr:
        rr.raise_for_status()
        for x in rr.iter_content(1024*1024):
            b.extend(x)
            if len(b)>size or len(b)>CAP:raise ValueError("size_cap")
    b=bytes(b);assert len(b)==size and hashlib.md5(b).hexdigest()==MD5
    o={"status":"archive_listing_only","doi":"10.5281/zenodo.7414956",
       "bytes":size,"md5_verified":True,"sha256":hashlib.sha256(b).hexdigest(),
       "license":j["metadata"].get("license"),"numeric_outcomes_analyzed":False,
       "archive_payload_extracted":False}
    with py7zr.SevenZipFile(io.BytesIO(b),mode="r") as z:
        infos=z.list()
        counts=Counter();cal=Counter();entries=[];unsafe=0;expanded=0;nested=0
        for i,f in enumerate(infos):
            name=str(f.filename);p=PurePosixPath(name.replace("\\","/"))
            if p.is_absolute() or ".." in p.parts or re.match(r"^[A-Za-z]:",name) or getattr(f,"is_symlink",False):unsafe+=1
            if f.is_directory:continue
            n=int(f.uncompressed or 0);expanded+=n
            ext=p.suffix.lower();counts[ext]+=1
            iscal=bool(re.search(r"calibrat|calib|speaker|loudspeaker|test.?position|reference|known.?position",name,re.I))
            if ext in (".7z",".zip",".tar",".gz",".rar",".xz",".bz2"):nested+=1
            if iscal:
                cal[ext]+=1
                if ext not in (".wav",".mp3",".flac",".aiff",".avi",".mp4"):
                    # Public field-like tokens only, not literal identifiers, dates, or locations.
                    tok=sorted(set(re.findall(r"calibration|calibrat|calib|array|speaker|loudspeaker|reference|known|position|distance|angle|azimuth|elevation|amplitude|localization|localisation|coordinate|raw|data|result|readme|analysis|code|measure|estimate|source|signal|true|real|calculated|actual|microphone|error|table",name,re.I)))
                    entries.append({"index":i,"path_sha256":hashlib.sha256(name.encode()).hexdigest(),"extension":ext,"bytes":n,"tokens":tok})
        o["archive"]={"members_including_dirs":len(infos),"uncompressed_file_bytes":expanded,
          "file_extension_counts":dict(counts),"calibration_extension_counts":dict(cal),
          "calibration_nonmedia_candidates":entries[:150],"nonmedia_candidate_count":len(entries),
          "unsafe_path_or_symlink_count":unsafe,"nested_archive_count":nested,
          "future_extraction_admissible_under_caps":bool(unsafe==0 and nested==0 and len(infos)<=2000 and expanded<=200_000_000)}
    return o
def main():
    try:o=run()
    except Exception as e:
        import traceback
        o={"status":"blocked","error_type":type(e).__name__,"failure_functions":[x.name for x in traceback.extract_tb(e.__traceback__)[-5:]],"numeric_outcomes_analyzed":False}
    dest=OUT/"audit_v46_known_position_calibration.json"
    dest.write_text(json.dumps(o,indent=2,allow_nan=False));print(dest.read_text())
    return 0 if o["status"]=="archive_listing_only" else 2
if __name__=="__main__":raise SystemExit(main())
