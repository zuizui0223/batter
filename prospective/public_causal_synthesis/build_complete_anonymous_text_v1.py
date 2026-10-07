#!/usr/bin/env python3
"""Build the Behavioral Ecology complete anonymous text from source files."""

from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
FULL = HERE / "MANUSCRIPT_DRAFT_V1.md"
LAY = HERE / "LAY_SUMMARY_V1.md"
CAPTIONS = HERE / "FIGURE_CAPTIONS_V1.md"
OUT = HERE / "COMPLETE_ANONYMOUS_TEXT_V1.md"

manuscript = FULL.read_text(encoding="utf-8")
lay = LAY.read_text(encoding="utf-8")
captions = CAPTIONS.read_text(encoding="utf-8")

lay_body = "\n".join(
    line for line in lay.splitlines()
    if not line.startswith("#")
).strip()

# Remove internal manuscript metadata.
manuscript = "\n".join(
    line for line in manuscript.splitlines()
    if not re.match(r"^\*\*(Article type|Working target|Status|Author metadata):", line)
)

# Remove internal figure-file inventory.
manuscript = re.sub(
    r"\n## Figure files\n[\s\S]*?\n---\n\n# References — working list",
    "\n\n# References",
    manuscript,
)

# Remove internal trailing draft note.
manuscript = re.sub(
    r"\n## Disclosure note — draft[\s\S]*$",
    "",
    manuscript,
).strip()

# Replace author-owned repository identity with anonymous review placeholder.
manuscript = manuscript.replace(
    "Source-level analysis contracts, structural audit records, executable scripts, "
    "exact/randomization logic, result receipts, synthesis files and figure-generation "
    "code are version controlled in `zuizui0223/batter`.",
    "Source-level analysis contracts, structural audit records, executable scripts, "
    "exact/randomization logic, result receipts, synthesis files and figure-generation "
    "code will be supplied in an anonymized review archive: "
    "`[ANONYMIZED_REVIEW_ARCHIVE_URL]` (Anonymous 2026).",
)

# Behavioral Ecology requests an anonymized data/archive citation in References
# during double-anonymized review.
anonymous_archive_ref = (
    "- Anonymous. 2026. Reproducibility archive for: Individual organization remains "
    "detectable across acute perturbations in bats. "
    "`[ANONYMIZED_REVIEW_ARCHIVE_URL]`."
)
manuscript = manuscript.replace(
    "# References — working list\n",
    "# References — working list\n\n" + anonymous_archive_ref + "\n",
    1,
)

# Remove the internal draft label from reviewer-facing manuscript.
manuscript = manuscript.replace(
    "# References — working list",
    "# References",
    1,
)

# Internal file-path authority details are not useful to reviewers.
manuscript = re.sub(
    r"\nThe authoritative manuscript-level numeric ledger is:[\s\S]*?"
    r"`figures/public_causal/`\.\n",
    "\n",
    manuscript,
)

captions = re.sub(r"^# Figure captions v1\s*", "", captions).strip()

out = (
    "# Lay Summary\n\n"
    + lay_body
    + "\n\n"
    + manuscript
    + "\n\n# Figure legends\n\n"
    + captions
    + "\n"
)

OUT.write_text(out, encoding="utf-8")
print(f"wrote {OUT} ({len(out)} chars)")
