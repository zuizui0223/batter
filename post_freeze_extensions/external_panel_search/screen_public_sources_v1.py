#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math, re, sys, zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "post_freeze_extensions/external_panel_search/public_source_screen_v1.json"
OUT_MD = ROOT / "post_freeze_extensions/external_panel_search/PUBLIC_SOURCE_SCREEN_V1.md"

HEADERS = {"User-Agent": "batter-external-panel-search-v1/1.0"}

SOURCES = [
    {
        "id": "zenodo_noctule_7535030",
        "repository": "Zenodo",
        "doi": "10.5281/zenodo.7535030",
        "api": "https://zenodo.org/api/records/7535030",
        "kind": "zenodo",
    },
    {
        "id": "figshare_iaio_28845701",
        "repository": "Figshare",
        "doi": "10.6084/m9.figshare.28845701.v1",
        "api": "https://api.figshare.com/v2/articles/28845701",
        "kind": "figshare",
    },
    {
        "id": "figshare_iaio_21717086",
        "repository": "Figshare",
        "doi": "10.6084/m9.figshare.21717086.v3",
        "api": "https://api.figshare.com/v2/articles/21717086",
        "kind": "figshare",
    },
]

VERT_PATTERNS = re.compile(r"^(height|altitude|elevation)(_|$)|(^|_)z($|_)|^(asl|agl)(_|$)", re.I)
ID_PATTERNS = re.compile(r"(bat.?id|individual|animal|ring|track.?animal|subject)", re.I)
TRACK_PATTERNS = re.compile(r"(track.?id|flight.?path|trip.?id|session|night)", re.I)
TIME_PATTERNS = re.compile(r"(timestamp|date.?time|datetime|time|date)", re.I)
X_PATTERNS = re.compile(r"(^x$|longitude|lon$|utm.?x|easting)", re.I)
Y_PATTERNS = re.compile(r"(^y$|latitude|lat$|utm.?y|northing)", re.I)

MAX_DOWNLOAD = 100 * 1024 * 1024

def norm(x):
    return re.sub(r"[^a-z0-9]+", "_", str(x).strip().lower()).strip("_")

def get_json(url):
    r = requests.get(url, headers=HEADERS, timeout=90)
    r.raise_for_status()
    return r.json()

def download(url):
    r = requests.get(url, headers=HEADERS, timeout=180)
    r.raise_for_status()
    data = r.content
    if len(data) > MAX_DOWNLOAD:
        raise RuntimeError(f"download > {MAX_DOWNLOAD} bytes")
    return data

def file_entries(src):
    meta = get_json(src["api"])
    if src["kind"] == "zenodo":
        out = []
        for f in meta.get("files", []):
            links = f.get("links", {})
            url = links.get("content") or links.get("self")
            out.append({
                "name": f.get("key") or f.get("filename"),
                "size": int(f.get("size") or 0),
                "url": url,
                "checksum": f.get("checksum"),
            })
        return meta, out
    out = []
    for f in meta.get("files", []):
        out.append({
            "name": f.get("name"),
            "size": int(f.get("size") or 0),
            "url": f.get("download_url"),
            "checksum": f.get("computed_md5") or f.get("md5"),
        })
    return meta, out

def header_flags(columns):
    cols = [str(c) for c in columns]
    return {
        "columns": cols,
        "native_vertical_fields": [c for c in cols if VERT_PATTERNS.search(norm(c))],
        "candidate_id_fields": [c for c in cols if ID_PATTERNS.search(norm(c))],
        "candidate_track_fields": [c for c in cols if TRACK_PATTERNS.search(norm(c))],
        "candidate_time_fields": [c for c in cols if TIME_PATTERNS.search(norm(c))],
        "candidate_x_fields": [c for c in cols if X_PATTERNS.search(norm(c))],
        "candidate_y_fields": [c for c in cols if Y_PATTERNS.search(norm(c))],
    }

def read_tables(name, data):
    low = name.lower()
    tables = []
    if low.endswith((".csv", ".txt", ".tsv")):
        # Parse all columns as strings. This deliberately avoids numeric conversion,
        # especially for native vertical columns.
        sep = "\t" if low.endswith((".txt", ".tsv")) else ","
        try:
            df = pd.read_csv(io.BytesIO(data), sep=sep, dtype=str, low_memory=False)
        except Exception:
            try:
                df = pd.read_csv(io.BytesIO(data), sep=None, engine="python", dtype=str)
            except Exception as e:
                return [{"table": name, "error": f"read failed: {e}"}]
        tables.append((name, df))
    elif low.endswith((".xlsx", ".xls")):
        try:
            book = pd.ExcelFile(io.BytesIO(data))
            for sheet in book.sheet_names:
                try:
                    df = pd.read_excel(book, sheet_name=sheet, dtype=str)
                    tables.append((f"{name}::{sheet}", df))
                except Exception as e:
                    tables.append((f"{name}::{sheet}", None, str(e)))
        except Exception as e:
            return [{"table": name, "error": f"excel open failed: {e}"}]
    elif low.endswith(".zip"):
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            for member in z.namelist():
                if member.lower().endswith((".csv", ".txt", ".tsv", ".xlsx", ".xls")) and not member.endswith("/"):
                    b = z.read(member)
                    tables.extend([(x["table"], x.get("_df"), x.get("error")) for x in []])
                    sub = read_tables(member, b)
                    # sub already summarized, so return alongside any later members
                    for x in sub:
                        x["table"] = f"{name}::{x['table']}"
                        tables.append((x["table"], x))
        except Exception as e:
            return [{"table": name, "error": f"zip open failed: {e}"}]
    else:
        return []
    return tables

def choose_col(cols, pats):
    for p in pats:
        for c in cols:
            if re.search(p, norm(c), re.I):
                return c
    return None

def infer_structural(df, flags):
    if df is None or not hasattr(df, "columns"):
        return {}
    cols = list(df.columns)
    id_col = choose_col(cols, [r"^bat_id$", r"^batid$", r"^individual.*id$", r"^animal.*id$", r"^ring_number$", r"^id$"])
    track_col = choose_col(cols, [r"^trackid$", r"flight.*path", r"^trip.*id$", r"^session.*id$", r"^night.*id$"])
    time_col = choose_col(cols, [r"^timestamp$", r"datetime", r"date.*time", r"^date$", r"^time$"])
    x_col = choose_col(cols, [r"^longitude$", r"^lon$", r"^x_$", r"^x$", r"easting"])
    y_col = choose_col(cols, [r"^latitude$", r"^lat$", r"^y_$", r"^y$", r"northing"])
    out = {
        "row_count": int(len(df)),
        "selected_id_field": id_col,
        "selected_track_field": track_col,
        "selected_time_field": time_col,
        "selected_x_field": x_col,
        "selected_y_field": y_col,
    }
    if id_col:
        ids = df[id_col].dropna().astype(str)
        out["individual_count"] = int(ids.nunique())
    # Track/session structure can be counted without looking at any vertical value.
    if id_col and track_col:
        d = df[[id_col, track_col]].dropna().astype(str)
        counts = d.groupby([id_col, track_col]).size()
        eligible = counts[counts >= 50]
        repeat = eligible.reset_index().groupby(id_col)[track_col].nunique()
        out["track_count"] = int(d[track_col].nunique())
        out["tracks_ge50"] = int((counts >= 50).sum())
        out["repeat_individuals_ge2_tracks_ge50"] = int((repeat >= 2).sum())
        out["individuals_with_any_track_ge50"] = int(repeat.size)
        out["structural_gate_pass_from_explicit_tracks"] = bool(
            d[id_col].nunique() >= 8 and (repeat >= 2).sum() >= 5
        )
    elif id_col and time_col:
        # Night-based fallback from timestamp. We only parse timestamps; vertical is untouched.
        times = pd.to_datetime(df[time_col], errors="coerce", utc=True)
        tmp = pd.DataFrame({"iid": df[id_col].astype(str), "t": times}).dropna()
        if not tmp.empty:
            # shifted-night convention used elsewhere in batter
            night = (tmp["t"] - pd.Timedelta(hours=12)).dt.date.astype(str)
            counts = pd.DataFrame({"iid": tmp["iid"], "night": night}).groupby(["iid", "night"]).size()
            eligible = counts[counts >= 50]
            repeat = eligible.reset_index().groupby("iid")["night"].nunique()
            out["night_count"] = int(counts.size)
            out["nights_ge50"] = int((counts >= 50).sum())
            out["repeat_individuals_ge2_nights_ge50"] = int((repeat >= 2).sum())
            out["individuals_with_any_night_ge50"] = int(repeat.size)
            out["structural_gate_pass_from_shifted_nights"] = bool(
                tmp["iid"].nunique() >= 8 and (repeat >= 2).sum() >= 5
            )
    return out

def summarize_table(label, df_or_summary):
    if isinstance(df_or_summary, dict):
        return df_or_summary
    df = df_or_summary
    flags = header_flags(df.columns)
    return {
        "table": label,
        **flags,
        "structure": infer_structural(df, flags),
        "vertical_numeric_values_inspected": False,
    }

def main():
    payload = {
        "schema_version": 1,
        "study_id": "batter-external-bat-panel-search-v1",
        "vertical_numeric_values_read_for_admission": False,
        "sources": {},
    }

    for src in SOURCES:
        rec = {
            "repository": src["repository"],
            "doi": src["doi"],
            "api": src["api"],
            "files": [],
        }
        try:
            meta, files = file_entries(src)
            rec["metadata_title"] = meta.get("metadata", {}).get("title") if src["kind"] == "zenodo" else meta.get("title")
            for f in files:
                fr = {k: f.get(k) for k in ("name", "size", "url", "checksum")}
                name = f.get("name") or ""
                # Inspect only plausible tabular archives, within size cap.
                if f.get("url") and int(f.get("size") or 0) <= MAX_DOWNLOAD and name.lower().endswith((".csv",".txt",".tsv",".xlsx",".xls",".zip")):
                    try:
                        data = download(f["url"])
                        fr["downloaded_size"] = len(data)
                        fr["sha256"] = hashlib.sha256(data).hexdigest()
                        table_objs = read_tables(name, data)
                        summaries = []
                        for item in table_objs:
                            if isinstance(item, tuple):
                                if len(item) == 2:
                                    label, obj = item
                                    summaries.append(summarize_table(label, obj))
                                elif len(item) == 3:
                                    label, obj, err = item
                                    if isinstance(obj, dict):
                                        summaries.append(obj)
                                    elif obj is None:
                                        summaries.append({"table": label, "error": err})
                            elif isinstance(item, dict):
                                summaries.append(item)
                        fr["tables"] = summaries
                    except Exception as e:
                        fr["inspect_error"] = str(e)
                rec["files"].append(fr)
        except Exception as e:
            rec["source_error"] = str(e)
        payload["sources"][src["id"]] = rec

    # Derive source-level structural admissions from table-level evidence.
    for sid, rec in payload["sources"].items():
        passing = []
        vertical_tables = []
        for f in rec.get("files", []):
            for t in f.get("tables", []):
                if t.get("native_vertical_fields"):
                    vertical_tables.append(t.get("table"))
                st = t.get("structure", {})
                if t.get("native_vertical_fields") and (
                    st.get("structural_gate_pass_from_explicit_tracks") or
                    st.get("structural_gate_pass_from_shifted_nights")
                ):
                    passing.append(t.get("table"))
        rec["tables_with_native_vertical"] = vertical_tables
        rec["passing_tables"] = passing
        rec["admission_status"] = "PASS" if passing else "NO_PASS_FROM_INSPECTED_PUBLIC_TABLES"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Prospective external public-source structural screen v1",
        "",
        "**Outcome-blind:** numeric vertical magnitudes were not used or summarized.",
        "",
        "| source | files discovered | tables with native vertical | structural PASS table |",
        "|---|---:|---|---|",
    ]
    for sid, rec in payload["sources"].items():
        lines.append(
            f"| {sid} | {len(rec.get('files', []))} | "
            f"{', '.join(rec.get('tables_with_native_vertical', [])) or 'none'} | "
            f"{', '.join(rec.get('passing_tables', [])) or 'none'} |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        sid: {
            "admission_status": rec.get("admission_status"),
            "passing_tables": rec.get("passing_tables"),
            "tables_with_native_vertical": rec.get("tables_with_native_vertical"),
            "source_error": rec.get("source_error"),
        }
        for sid, rec in payload["sources"].items()
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
