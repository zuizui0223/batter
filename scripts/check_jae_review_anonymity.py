#!/usr/bin/env python3
"""Fail if the generated JAE review manuscript leaks obvious author identity."""

from pathlib import Path

PATH = Path("manuscript/generated/JAE_REVIEW_V0_3_4.md")

FORBIDDEN = (
    "zuizui0223",
    "github.com/zuizui0223",
    "[INSERT FINAL AUTHOR LIST]",
    "[INSERT AFFILIATIONS]",
    "[INSERT NAME, POSTAL ADDRESS, EMAIL, ORCID]",
)

def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN if token.lower() in text.lower()]
    if hits:
        print("JAE anonymous-review gate: BLOCKED")
        for token in hits:
            print(f" - leaked identifying token: {token}")
        return 1
    print("JAE anonymous-review gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
