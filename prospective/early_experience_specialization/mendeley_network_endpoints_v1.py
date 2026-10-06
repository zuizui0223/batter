#!/usr/bin/env python3
"""Capture public Mendeley page network endpoint URLs/statuses only.

No research data values or response bodies are opened.
"""

from pathlib import Path
import json, re
from playwright.sync_api import sync_playwright

URL="https://data.mendeley.com/datasets/wh7c636y3t/1"
HERE=Path(__file__).resolve().parent
OUT=HERE/"MENDELEY_NETWORK_ENDPOINTS_V1.json"
OUTMD=HERE/"MENDELEY_NETWORK_ENDPOINTS_V1.md"

def main():
    requests=[]
    responses=[]

    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()

        def on_request(req):
            u=req.url
            if re.search(r"(api|dataset|file|zip|download)",u,re.I):
                requests.append({"method":req.method,"url":u,"resource_type":req.resource_type})

        def on_response(resp):
            u=resp.url
            if re.search(r"(api|dataset|file|zip|download)",u,re.I):
                responses.append({"status":resp.status,"url":u})

        page.on("request",on_request)
        page.on("response",on_response)
        page.goto(URL,wait_until="domcontentloaded",timeout=120000)

        # Accept cookies if the banner exists, then allow app traffic to settle.
        for label in ("Accept all cookies","Allow all"):
            try:
                loc=page.get_by_role("button",name=label)
                if loc.count():
                    loc.first.click(timeout=5000)
                    break
            except Exception:
                pass

        page.wait_for_timeout(20000)
        final_url=page.url
        title=page.title()
        browser.close()

    # Deduplicate exact records without opening bodies.
    def dedup(rows):
        seen=set(); out=[]
        for row in rows:
            key=tuple(sorted(row.items()))
            if key not in seen:
                seen.add(key); out.append(row)
        return out

    requests=dedup(requests)
    responses=dedup(responses)

    result={
        "page":URL,
        "final_url":final_url,
        "title":title,
        "requests":requests,
        "responses":responses,
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Mendeley network endpoint capture v1","",
        "**NETWORK URL/STATUS ONLY — NO RESPONSE BODY / RESEARCH VALUES OPENED.**","",
        f"- page: {URL}",
        f"- final URL: {final_url}",
        "",
        "## Responses","",
    ]
    for x in responses:
        lines.append(f"- {x['status']}  {x['url']}")
    lines += ["","## Requests",""]
    for x in requests:
        lines.append(f"- {x['method']} [{x['resource_type']}] {x['url']}")
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
