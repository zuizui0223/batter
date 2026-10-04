#!/usr/bin/env python3
"""Outcome-blind Mendeley metadata inventory for ontogenetic path-dependence v1.

Allowed:
- public dataset-page HTML metadata,
- OAI-PMH metadata,
- authenticated/public API metadata if available.

Forbidden:
- downloading dataset file contents,
- opening route geometry,
- calculating any route similarity or biological endpoint.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API_BASE = "https://api.data.mendeley.com"
PUBLIC_API_BASE = "https://data.mendeley.com/public-api"
OAI_BASE = "https://data.mendeley.com/oai"
PAGE_BASE = "https://data.mendeley.com/datasets"
DATASETS = [
    {
        "label": "source_A_maternal",
        "id": "gpcg9m5758",
        "version": 1,
        "doi": "10.17632/gpcg9m5758.1",
        "title": "Mother bats facilitate pup navigation learning",
        "publish_date": "2021-11-24",
    },
    {
        "label": "source_B_first_flight",
        "id": "n9d8gbz3xr",
        "version": 1,
        "doi": "10.17632/n9d8gbz3xr.1",
        "title": "The ontogeny of a mammalian cognitive map in the real world",
        "publish_date": "2020-05-29",
    },
]
OUT = Path("prospective/ontogenetic_path_dependence/schema_inventory_v1.json")

UA = "batter-ontogenetic-path-dependence-schema-preflight/1.1"

def get_bytes(url: str, accept: str = "*/*") -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def get_json(url: str):
    return json.loads(get_bytes(
        url,
        "application/json, application/vnd.mendeley-public-dataset.1+json",
    ).decode("utf-8"))

def page_metadata(d: dict) -> dict:
    url = f"{PAGE_BASE}/{d['id']}/{d['version']}"
    raw = get_bytes(url, "text/html").decode("utf-8", errors="replace")
    # Metadata only: inspect embedded structured data / identifiers, never follow file links.
    scripts = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        raw, flags=re.I | re.S
    )
    jsonld = []
    for s in scripts:
        try:
            jsonld.append(json.loads(html.unescape(s.strip())))
        except Exception:
            pass
    uuid_candidates = sorted(set(re.findall(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b",
        raw
    )))
    key_snippets = []
    for pat in [r'.{0,100}datasetId.{0,180}', r'.{0,100}"files".{0,180}', r'.{0,100}gpcg9m5758.{0,180}', r'.{0,100}n9d8gbz3xr.{0,180}']:
        for m in re.findall(pat, raw, flags=re.I | re.S):
            one = re.sub(r"\s+", " ", m).strip()
            if one not in key_snippets:
                key_snippets.append(one[:300])
    return {
        "page_url": url,
        "html_bytes": len(raw.encode("utf-8")),
        "jsonld": jsonld,
        "uuid_candidates": uuid_candidates[:50],
        "metadata_snippets": key_snippets[:20],
    }

def oai_url(params: dict) -> str:
    return OAI_BASE + "?" + urllib.parse.urlencode(params)

def oai_list_records_for_date(d: dict) -> list[dict]:
    day = dt.date.fromisoformat(d["publish_date"])
    start = (day - dt.timedelta(days=3)).isoformat()
    end = (day + dt.timedelta(days=3)).isoformat()
    url = oai_url({
        "verb": "ListRecords",
        "metadataPrefix": "oai_dc",
        "from": start,
        "until": end,
    })
    raw = get_bytes(url, "application/xml, text/xml")
    root = ET.fromstring(raw)
    records = []
    for rec in root.findall(".//{http://www.openarchives.org/OAI/2.0/}record"):
        header = rec.find("{http://www.openarchives.org/OAI/2.0/}header")
        ident = header.findtext("{http://www.openarchives.org/OAI/2.0/}identifier") if header is not None else None
        datestamp = header.findtext("{http://www.openarchives.org/OAI/2.0/}datestamp") if header is not None else None
        texts = [" ".join((e.text or "").split()) for e in rec.iter() if e.text and e.text.strip()]
        blob = "\n".join(texts)
        if d["doi"].lower() in blob.lower() or d["id"].lower() in blob.lower() or d["title"].lower() in blob.lower():
            dc_fields = []
            for e in rec.iter():
                if e.text and e.text.strip() and e.tag.startswith("{http://purl.org/dc/elements/1.1/}"):
                    dc_fields.append({
                        "field": e.tag.split("}", 1)[1],
                        "value": " ".join(e.text.split()),
                    })
            records.append({
                "oai_identifier": ident,
                "datestamp": datestamp,
                "dc_fields": dc_fields,
            })
    return records

def oai_formats(identifier: str) -> list[dict]:
    raw = get_bytes(oai_url({"verb": "ListMetadataFormats", "identifier": identifier}), "application/xml, text/xml")
    root = ET.fromstring(raw)
    out = []
    ns = "{http://www.openarchives.org/OAI/2.0/}"
    for m in root.findall(f".//{ns}metadataFormat"):
        out.append({
            "metadataPrefix": m.findtext(f"{ns}metadataPrefix"),
            "schema": m.findtext(f"{ns}schema"),
            "metadataNamespace": m.findtext(f"{ns}metadataNamespace"),
        })
    return out

def api_metadata(d: dict) -> dict:
    """Use anonymous Mendeley frontend endpoints for METADATA only."""
    snapshot_url = f"{PUBLIC_API_BASE}/datasets/{d['id']}/snapshot/{d['version']}"
    meta = get_json(snapshot_url)

    folders = []
    folder_error = None
    try:
        folders_url = f"{PUBLIC_API_BASE}/datasets/{d['id']}/folders/{d['version']}"
        folders_raw = get_json(folders_url)
        folders = folders_raw if isinstance(folders_raw, list) else (
            folders_raw.get("results") or folders_raw.get("items") or folders_raw.get("folders") or []
        )
    except Exception as e:
        folder_error = repr(e)

    def fetch_file_rows(folder_id=None):
        q = f"version={d['version']}&$start=0&$limit=1000"
        if folder_id is not None:
            q = f"folder_id={urllib.parse.quote(str(folder_id))}&" + q
        url = f"{PUBLIC_API_BASE}/datasets/{d['id']}/files?{q}"
        rows = get_json(url)
        if isinstance(rows, dict):
            rows = rows.get("results") or rows.get("items") or rows.get("files") or []
        return rows or []

    # First ask for unscoped metadata. If the endpoint requires folder_id, fall back to root.
    unscoped_error = None
    try:
        file_rows = fetch_file_rows()
    except Exception as e:
        unscoped_error = repr(e)
        file_rows = fetch_file_rows("root")

    # Add explicit folder results only when the folder listing was cheaply available.
    for x in folders:
        if x.get("id") is not None:
            try:
                file_rows.extend(fetch_file_rows(x.get("id")))
            except Exception:
                pass

    dedup = {}
    for row in file_rows:
        dedup[row.get("id") or (row.get("filename"), row.get("folder_id"))] = row
    file_rows = list(dedup.values())

    slim = []
    for f in file_rows:
        cd = f.get("content_details") or {}
        slim.append({
            "id": f.get("id"),
            "filename": f.get("filename") or f.get("name"),
            "folder_id": f.get("folder_id"),
            "size": f.get("size") or cd.get("size"),
            "content_type": cd.get("content_type") or f.get("content_type"),
            "sha256_hash": cd.get("sha256_hash"),
            "description": f.get("description"),
        })
    return {
        "resolved_id": meta.get("id") if isinstance(meta, dict) else None,
        "name": meta.get("name") if isinstance(meta, dict) else None,
        "version": meta.get("version") if isinstance(meta, dict) else d["version"],
        "metadata_endpoint": "public-frontend-anonymous",
        "folder_error": folder_error,
        "unscoped_file_error": unscoped_error,
        "folder_count": len(folders),
        "folders": [
            {
                "id": x.get("id"),
                "name": x.get("name"),
                "parent_id": x.get("parent_id"),
                "description": x.get("description"),
            }
            for x in folders
        ],
        "file_count": len(slim),
        "files": slim,
    }

