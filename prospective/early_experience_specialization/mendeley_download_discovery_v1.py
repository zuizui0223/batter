#!/usr/bin/env python3
"""Discover public Mendeley download endpoints without opening research values."""

from __future__ import annotations
import json, re, pathlib, urllib.request
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL="https://data.mendeley.com/datasets/wh7c636y3t/1"
HERE=pathlib.Path(__file__).resolve().parent
OUT=HERE/"MENDELEY_DOWNLOAD_DISCOVERY_V1.json"
OUTMD=HERE/"MENDELEY_DOWNLOAD_DISCOVERY_V1.md"

def uniq(xs):
    seen=set(); out=[]
    for x in xs:
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

def main():
    result={"url":URL,"raw":{},"browser":{}}

    # Raw HTML discovery.
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        html=r.read().decode("utf-8","replace")
    soup=BeautifulSoup(html,"html.parser")

    hrefs=[x.get("href") for x in soup.find_all(["a","link"]) if x.get("href")]
    srcs=[x.get("src") for x in soup.find_all(["script","img"]) if x.get("src")]
    candidates=[u for u in hrefs+srcs if re.search(r"(download|file|dataset|wh7c636y3t)",u,re.I)]

    script_snips=[]
    for s in soup.find_all("script"):
        txt=s.string or s.get_text(" ",strip=True)
        if txt and re.search(r"(wh7c636y3t|Download All|download|public-files)",txt,re.I):
            script_snips.append(txt[:10000])

    result["raw"]={
        "status":"ok",
        "html_chars":len(html),
        "title":soup.title.get_text(" ",strip=True) if soup.title else None,
        "candidate_urls":uniq(candidates)[:500],
        "script_snippets":script_snips[:20],
        "contains_download_all":"Download All" in html,
        "contains_public_files":"public-files" in html,
    }

    # Browser DOM discovery, no clicking yet.
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        page.goto(URL,wait_until="domcontentloaded",timeout=120000)
        page.wait_for_timeout(15000)
        body=page.locator("body").inner_text(timeout=30000)
        links=page.locator("a").evaluate_all(
            "(els)=>els.map(e=>({text:(e.innerText||'').trim(),href:e.href||''}))"
        )
        buttons=page.locator("button").evaluate_all(
            "(els)=>els.map(e=>({text:(e.innerText||'').trim(),disabled:!!e.disabled}))"
        )
        result["browser"]={
            "title":page.title(),
            "final_url":page.url,
            "body_prefix":body[:5000],
            "links":[x for x in links if re.search(r"(download|file|dataset|wh7c636y3t)",x["text"]+" "+x["href"],re.I)][:500],
            "buttons":buttons[:200],
            "has_download_all_text":"Download All" in body,
        }
        browser.close()

    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    lines=[
        "# Mendeley download discovery v1","",
        "**STRUCTURAL WEB DISCOVERY ONLY — NO RESEARCH VALUES OPENED.**","",
        f"- raw HTML chars: {result['raw']['html_chars']}",
        f"- raw contains Download All: {result['raw']['contains_download_all']}",
        f"- raw contains public-files: {result['raw']['contains_public_files']}",
        f"- browser final URL: {result['browser'].get('final_url')}",
        f"- browser contains Download All: {result['browser'].get('has_download_all_text')}",
        "",
        "## Raw candidate URLs","",
    ]
    for u in result["raw"]["candidate_urls"]:
        lines.append(f"- `{u}`")
    lines += ["","## Browser buttons",""]
    for b in result["browser"]["buttons"]:
        lines.append(f"- {b}")
    lines += ["","## Browser candidate links",""]
    for x in result["browser"]["links"]:
        lines.append(f"- {x}")
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
