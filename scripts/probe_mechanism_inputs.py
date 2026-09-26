#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import urllib.request

README_URL = "https://datarepository.movebank.org/server/api/core/bitstreams/7bd3cd13-6db4-4a63-9f60-76a594ad3e37/content"
README_MD5 = "d035547e9c17298298d95cabea24cd87"
ANNOTATED_URL = "https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
ANNOTATED_MD5 = "e0f6faedfd1f21bac222d9da430ea5d8"


def download(url: str) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"batter-mechanism-preflight/0.1"})
    with urllib.request.urlopen(req,timeout=120) as response:
        return response.read()


def verify(data: bytes, md5: str):
    observed=hashlib.md5(data).hexdigest()
    if observed != md5:
        raise RuntimeError(f"checksum mismatch {observed} != {md5}")
    return observed


def main():
    readme=download(README_URL)
    annotated=download(ANNOTATED_URL)
    verify(readme,README_MD5)
    verify(annotated,ANNOTATED_MD5)

    text=annotated.decode("utf-8-sig")
    reader=csv.reader(io.StringIO(text, newline=""))
    header=next(reader)
    row_count=sum(1 for _ in reader)

    payload={
        "preflight_id":"batter-mechanism-input-preflight-v1",
        "readme_md5":README_MD5,
        "annotated_md5":ANNOTATED_MD5,
        "annotated_size_bytes":len(annotated),
        "annotated_row_count":row_count,
        "annotated_columns":header,
        "numeric_values_summarized":False,
        "readme_text":readme.decode("utf-8",errors="replace"),
    }
    out=Path("results/mechanism_input_preflight_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "annotated_row_count":row_count,
        "annotated_columns":header,
        "readme_text":payload["readme_text"],
        "numeric_values_summarized":False,
    }))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
