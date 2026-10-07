#!/usr/bin/env python3
"""Download and verify the exact CC0 Carollia source subset used in validation."""

from pathlib import Path
import hashlib
import json
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "CAROLLIA_CC0_MIRROR_MANIFEST_V1.json"


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "batter-carollia-cc0-mirror/1.0"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def mirror_into(build_root: Path) -> dict:
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    repo = spec["source_repository"]
    commit = spec["pinned_commit"]
    expected = spec["files"]
    base = "https://raw.githubusercontent.com/" + repo + "/" + commit + "/"

    target = build_root / "source_data" / "carollia_cc0"
    trial_dir = target / "Trial_Data_Carolia"
    trial_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    total = 0

    for name, expected_size in expected.items():
        rel = "Trial_Data_Carolia/" + name
        url = base + urllib.parse.quote(rel)
        data = get_bytes(url)
        if len(data) != int(expected_size):
            raise SystemExit(
                f"Carollia source-size drift for {name}: "
                f"{len(data)} != {expected_size}"
            )
        out = trial_dir / name
        out.write_bytes(data)
        total += len(data)
        rows.append(
            {
                "filename": name,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    if total != int(spec["expected_total_bytes"]):
        raise SystemExit(
            f"Carollia total-size drift: {total} != {spec['expected_total_bytes']}"
        )

    license_bytes = get_bytes(base + "LICENSE")
    (target / "LICENSE").write_bytes(license_bytes)

    receipt = {
        "source_repository": repo,
        "pinned_commit": commit,
        "source_paper_doi": spec["source_paper_doi"],
        "license": spec["license"],
        "n_files": len(rows),
        "total_bytes": total,
        "selection_rule": (
            "Exact C2-C8 trial files used by the frozen Carollia analyses; "
            "C1 excluded prospectively because only two public trials existed."
        ),
        "files": rows,
    }
    (target / "SOURCE_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "SOURCE_PIN.txt").write_text(
        "Carollia CC0 source mirror\n"
        f"repository: {repo}\n"
        f"pinned commit: {commit}\n"
        f"source paper DOI: {spec['source_paper_doi']}\n"
        f"license: {spec['license']}\n"
        f"mirrored trial files: {len(rows)}\n"
        f"mirrored trial bytes: {total}\n"
        "C1 excluded prospectively; mirrored subset is C2-C8 only.\n",
        encoding="utf-8",
    )
    return receipt


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("build_root")
    args = ap.parse_args()
    receipt = mirror_into(Path(args.build_root))
    print(json.dumps({
        "n_files": receipt["n_files"],
        "total_bytes": receipt["total_bytes"],
        "pinned_commit": receipt["pinned_commit"],
    }, indent=2))
