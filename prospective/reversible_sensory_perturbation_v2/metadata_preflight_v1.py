#!/usr/bin/env python3
"""HEAD-only metadata preflight for source-declared Dropbox shared folder."""
from __future__ import annotations
import json, urllib.parse, urllib.request, urllib.error

URL="https://www.dropbox.com/sh/met5cvcq9nmvxdd/AAAF4saT9FZl01FwWyRgD1pqa?dl=1"
UA="batter-reversible-sensory-metadata/1.0"

class TrackingRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        super().__init__(); self.chain=[]
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({"code":code,"from":safe(req.full_url),"to":safe(newurl)})
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def safe(url):
    p=urllib.parse.urlsplit(url)
    q=urllib.parse.parse_qs(p.query)
    keep={}
    if "dl" in q: keep["dl"]=q["dl"][:1]
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode(keep,doseq=True),""))

def main():
    rh=TrackingRedirect()
    opener=urllib.request.build_opener(rh)
    req=urllib.request.Request(URL,method="HEAD",headers={"User-Agent":UA,"Accept":"*/*"})
    try:
        r=opener.open(req,timeout=60)
        status=getattr(r,"status",None);headers=r.headers;final=r.geturl()
        r.close()
        out={
          "contract":"METADATA_PREFLIGHT_CONTRACT_V1.md",
          "body_bytes_consumed":0,
          "requested_url":safe(URL),
          "final_url":safe(final),
          "status":status,
          "redirects":rh.chain,
          "response_headers":{
            "content_type":headers.get("Content-Type"),
            "content_length":headers.get("Content-Length"),
            "content_disposition":headers.get("Content-Disposition"),
            "accept_ranges":headers.get("Accept-Ranges"),
          },
          "verdict":"PASS_PUBLIC_RESOLUTION" if status and 200<=status<400 else "STOP_PUBLIC_RESOLUTION"
        }
    except urllib.error.HTTPError as e:
        out={"contract":"METADATA_PREFLIGHT_CONTRACT_V1.md","body_bytes_consumed":0,
             "requested_url":safe(URL),"status":e.code,"redirects":rh.chain,
             "verdict":"STOP_HEAD_HTTP_ERROR"}
    except Exception as e:
        out={"contract":"METADATA_PREFLIGHT_CONTRACT_V1.md","body_bytes_consumed":0,
             "requested_url":safe(URL),"redirects":rh.chain,
             "error_type":type(e).__name__,"error":str(e),
             "verdict":"STOP_NETWORK"}
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
