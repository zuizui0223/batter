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
    "# References\n",
    "# References\n\n" + anonymous_archive_ref + "\n",
    1,
)

# Safety: remove the internal draft label if an upstream manuscript ever retains it.
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

def normalize_submission_markdown(text: str) -> str:
    """Normalize Markdown for stable Pandoc -> DOCX conversion.

    This changes presentation only:
    - simple equation blocks become plain submission-safe text;
    - common ASCII/placeholder math symbols become readable Unicode;
    - list blocks get explicit blank-line boundaries;
    - reference entries become hanging-indent-ready paragraphs rather than bullets.
    """
    # Simple manuscript equation blocks use [ / ] delimiters rather than full LaTeX.
    text = re.sub(
        r"\n\[\n([^\n]+)\n\]\n",
        lambda m: "\n\n" + m.group(1).strip() + "\n\n",
        text,
    )

    # Submission-safe plain mathematical notation.
    text = re.sub(r"([A-Za-z])_\{([^}]+)\}", r"\1(\2)", text)
    text = text.replace("^circ", "°")
    text = text.replace("<=", "≤").replace(">=", "≥")
    text = re.sub(r"\bP\s+le\s+", "P ≤ ", text)
    text = text.replace("(4!)^2", "(4!)²")
    text = re.sub(r"\bD>0\b", "D > 0", text)

    lines = text.splitlines()
    out_lines = []
    in_references = False

    def is_list_item(line: str) -> bool:
        return bool(re.match(r"^\s*-\s+\S", line))

    for line in lines:
        stripped=line.strip()

        if stripped == "# References":
            in_references=True
        elif in_references and stripped.startswith("# ") and stripped != "# References":
            in_references=False

        # References are styled as hanging paragraphs in the DOCX builder.
        if in_references and is_list_item(line):
            line=re.sub(r"^\s*-\s+", "", line, count=1)
            stripped=line.strip()

        current_list=is_list_item(line) and not in_references
        previous_list=bool(out_lines and is_list_item(out_lines[-1]))

        if current_list and out_lines and out_lines[-1].strip() and not previous_list:
            out_lines.append("")
        elif (not current_list) and previous_list and stripped:
            out_lines.append("")

        out_lines.append(line)

    return "\n".join(out_lines).strip() + "\n"


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

out = normalize_submission_markdown(out)
OUT.write_text(out, encoding="utf-8")
print(f"wrote {OUT} ({len(out)} chars)")
