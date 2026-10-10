#!/usr/bin/env python3
"""Source-metadata-only OSF audit for 2026 Myotis spatial overlap records.

No receiver detections, individual times, elevations, positions or bat outcomes
are opened. No file-content URLs are followed. Fail closed on unauthorized APIs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import urllib.error

ID="sg6dz"
VIEW_ONLY="4624cf1757b34e87bf7a4aca9d889319"  # publicly printed in the paper
BASE="https://api.osf.io/v2/nodes/sg6dz/"
TARGETS=(
    ("project",BASE),
    ("providers",BASE+"files/"),
    ("osfstorage_root",BASE+"files/osfstorage/"),
    ("proximity_UD_folder",BASE+"files/osfstorage/698dbd04bb73abf03bdfc98c/"),
    ("data_folder",BASE+"files/osfstorage/698dac7afa739fb04ee258a4/"),
    ("sn_prox_folder",BASE+"files/osfstorage/698dad08eb682af8bcc73651/"),
    ("day_20240515",BASE+"files/osfstorage/698dad6fab12904856dfcacd/"),
    ("day_20240516",BASE+"files/osfstorage/698dada20d35ac498ec72cef/"),
)
MAX_RESPONSE=1_200_000
UA="batter-2026-myotis-source-metadata-v1/1.0"


class StrictRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        parsed=urllib.parse.urlsplit(newurl)
        if parsed.scheme!="https" or parsed.hostname not in ("osf.io","api.osf.io"):
            raise ValueError("STOP_DISALLOWED_REDIRECT")
        return super().redirect_request(request,fp,code,msg,headers,newurl)


def source_get(url, view_only):
    if url not in [v for _n,v in TARGETS]:
        raise ValueError("Unexpected API endpoint")
    if view_only:
        url=url+("?view_only="+VIEW_ONLY)
    req=urllib.request.Request(url,headers={"Accept":"application/vnd.api+json, application/json",
                                              "User-Agent":UA})
    opener=urllib.request.build_opener(StrictRedirect())
    try:
        with opener.open(req,timeout=16) as response:
            body=response.read(MAX_RESPONSE+1)
            ct=response.headers.get("Content-Type","")
            status=response.status
            final=response.geturl()
    except urllib.error.HTTPError as e:
        return {"http_status":e.code,"error":"HTTP_ERROR","json_ok":False}
    except Exception as e:
        return {"http_status":None,"error":type(e).__name__,"json_ok":False}
    if len(body)>MAX_RESPONSE:
        return {"http_status":status,"error":"OVERSIZE_STOP","json_ok":False}
    p=urllib.parse.urlsplit(final)
    if p.scheme!="https" or p.hostname not in ("osf.io","api.osf.io"):
        return {"http_status":status,"error":"BAD_REDIRECT_TARGET","json_ok":False}
    try:
        o=json.loads(body)
    except Exception:
        return {"http_status":status,"error":"INVALID_JSON","json_ok":False}
    if not isinstance(o,dict):
        return {"http_status":status,"error":"NOT_JSON_OBJECT","json_ok":False}
    return {"http_status":status,"error":None,"json_ok":True,
            "digest_sha256":hashlib.sha256(body).hexdigest(),
            "json":o,"content_type":ct[:80]}


def safe_metadata(result,kind):
    data=result.pop("json",None)
    if not result.get("json_ok") or not isinstance(data,dict):
        return result
    entries=data.get("data")
    if kind=="project":
        d=entries if isinstance(entries,dict) else {}
        result["source_project_id"]=d.get("id")
        a=d.get("attributes") if isinstance(d.get("attributes"),dict) else {}
        result["project_title"]=str(a.get("title") or "")[:150]
        result["project_public"]=a.get("public")
        result["project_category"]=a.get("category")
    else:
        if isinstance(entries,dict):entries=[entries]
        if not isinstance(entries,list):entries=[]
        safe=[]
        for item in entries[:100]:
            if not isinstance(item,dict):continue
            a=item.get("attributes") if isinstance(item.get("attributes"),dict) else {}
            name=a.get("name") or ""
            safe.append({"resource_id":str(item.get("id") or "")[:100],
                         "resource_type":str(item.get("type") or "")[:30],
                         "filename":str(name)[:150],
                         "declared_size_bytes":a.get("size") if isinstance(a.get("size"),int) else None,
                         "kind":str(a.get("kind") or "")[:25],
                         "provider":str(a.get("provider") or "")[:30]})
        result["listed_resource_count_page1"]=len(entries)
        result["safe_file_metadata"]=safe
        result["pagination_next_present"]=bool((data.get("links") or {}).get("next"))
    return result


def self_test():
    demo={"http_status":200,"json_ok":True,"json":{"data":[
        {"id":"fake","type":"files","attributes":{"name":"bat_data.csv",
         "size":4200,"kind":"file","download_url":"SHOULD_NOT_PRINT"}}]}}
    d=safe_metadata(demo,"osfstorage_root")
    assert d["safe_file_metadata"][0]["filename"]=="bat_data.csv"
    assert "download_url" not in json.dumps(d)
    assert "SHOULD_NOT_PRINT" not in json.dumps(d)
    assert not d.get("json")
    return "PASS_METADATA_REDACTION"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_OSF_SOURCE_METADATA_RECEIPT_V1.json")
    args=p.parse_args()
    check=self_test()
    if args.self_test:
        print(json.dumps({"self_test":check,"numeric_bat_records_opened":False}))
        return
    records={}
    for label,url in TARGETS:
        no_token=safe_metadata(source_get(url,False),label)
        # View-only token is printed publicly by the paper; only try as fallback
        # when anonymous metadata retrieval fails.
        with_token=None
        if not no_token.get("json_ok"):
            with_token=safe_metadata(source_get(url,True),label)
        records[label]={"public":no_token}
        if with_token is not None:records[label]["public_author_view_only"]=with_token
    project=records["project"]
    project_pass=any(d.get("json_ok") and d.get("source_project_id")==ID
             for d in project.values())
    root=records["osfstorage_root"]
    root_access=any(d.get("json_ok") for d in root.values())
    if not project_pass or not root_access:
        status="STOP_OSF_METADATA_INACCESSIBLE"
    else:
        status="HOLD_DYAD_NIGHT_CROSSING_NOT_VERIFIED"
    out={
      "original_paper_doi":"10.1002/ece3.73604",
      "osf_node_id":ID,
      "source_gate":"MYOTIS_2026_OSF_TEMPORAL_CO_USE_SOURCE_GATE_V1.md",
      "timestamp_utc":datetime.now(timezone.utc).isoformat(),
      "status":status,
      "n_individuals_from_paper_only":25,
      "n_individuals_multiple_nights_from_paper_only":21,
      "stable_bat_tag_identity_verified":False,
      "same_dyad_multiple_nights_verified":False,
      "receiver_event_timestamp_headers_verified":False,
      "quantitative_bat_events_opened":False,
      "source_file_download_links_followed":False,
      "statistical_tests_on_bats":0,
      "self_test":check,
      "metadata_results":records
    }
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    osfroot=next((x for x in root.values() if x.get("json_ok")), {})
    folder=next((x for x in records["proximity_UD_folder"].values() if x.get("json_ok")), {})
    datafolder=next((x for x in records["data_folder"].values() if x.get("json_ok")), {})
    snprox=next((x for x in records["sn_prox_folder"].values() if x.get("json_ok")), {})
    datesamples={
       day:next((x for x in records[day].values() if x.get("json_ok")), {})
       for day in ("day_20240515","day_20240516")
    }
    print(json.dumps({
      "status":status,
      "project_metadata_verified":project_pass,
      "osfstorage_metadata_accessible":root_access,
      "osfstorage_root_resource_count":osfroot.get("listed_resource_count_page1"),
      "osfstorage_root_filenames":[x.get("filename") for x in osfroot.get("safe_file_metadata",[])],
      "osfstorage_root_kinds":[x.get("kind") for x in osfroot.get("safe_file_metadata",[])],
      "osfstorage_root_metadata":[
          {"filename":x.get("filename"),"kind":x.get("kind"),
           "resource_id":x.get("resource_id"),"declared_size_bytes":x.get("declared_size_bytes")}
          for x in osfroot.get("safe_file_metadata",[])
      ],
      "osfstorage_root_has_more_pages":osfroot.get("pagination_next_present"),
      "proximity_UD_folder_metadata_accessible":bool(folder),
      "proximity_UD_folder_resource_count":folder.get("listed_resource_count_page1"),
      "proximity_UD_folder_resources":[
          {"filename":x.get("filename"),"kind":x.get("kind"),
           "resource_id":x.get("resource_id"),"size":x.get("declared_size_bytes")}
          for x in folder.get("safe_file_metadata",[])
      ],
      "proximity_UD_folder_more_pages":folder.get("pagination_next_present"),
      "data_folder_metadata_accessible":bool(datafolder),
      "data_folder_resources":[
          {"filename":x.get("filename"),"kind":x.get("kind"),
           "resource_id":x.get("resource_id"),"size":x.get("declared_size_bytes")}
          for x in datafolder.get("safe_file_metadata",[])
      ],
      "data_folder_more_pages":datafolder.get("pagination_next_present"),
      "sn_prox_folder_metadata_accessible":bool(snprox),
      "sn_prox_folder_resource_count":snprox.get("listed_resource_count_page1"),
      "sn_prox_folder_resource_preview":[
          {"filename":x.get("filename"),"kind":x.get("kind"),
           "resource_id":x.get("resource_id"),"size":x.get("declared_size_bytes")}
          for x in snprox.get("safe_file_metadata",[])[:40]
      ],
      "sn_prox_folder_more_pages":snprox.get("pagination_next_present"),
      "dated_folder_samples":{
          day:{"metadata_accessible":bool(folder),
               "count_page1":folder.get("listed_resource_count_page1"),
               "more_pages":folder.get("pagination_next_present"),
               "resources":[{"filename":x.get("filename"),"kind":x.get("kind"),
                    "size":x.get("declared_size_bytes")} for x in
                    folder.get("safe_file_metadata",[])[:25]]}
          for day,folder in datesamples.items()
      },
      "numeric_bat_events_opened":False,
      "receipt":args.out
    },sort_keys=True))


if __name__=="__main__":
    main()
