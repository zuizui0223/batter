#!/usr/bin/env python3
from pathlib import Path

PATH=Path("manuscript/generated/JAE_REVIEW_V0_3_8.md")
FORBIDDEN=(
    "zuizui0223",
    "github.com/zuizui0223",
    "[INSERT FINAL AUTHOR LIST]",
    "[INSERT AFFILIATIONS]",
    "[INSERT NAME, POSTAL ADDRESS, EMAIL, ORCID]",
)

def main():
    text=PATH.read_text(encoding="utf-8").lower()
    hits=[x for x in FORBIDDEN if x.lower() in text]
    if hits:
        print("JAE v0.3.8 anonymous-review gate: BLOCKED")
        for x in hits:
            print(f" - leaked token: {x}")
        return 1
    print("JAE v0.3.8 anonymous-review gate: PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
