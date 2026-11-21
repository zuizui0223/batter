# 3D habitat and directly measured fruit availability — original small-file byte gate

2026-11-20. Run the canonical Dryad dataset→version→file metadata gate again within the same session, then **one** publisher official GET each for the original `Raw_movement_data.zip` of Trujillo et al. 2026 and the original `Bats_Ducke_data_metadata.xlsx` of Capaverde et al. 2018.

**Always fail closed:** Original publisher `digestType`+`digest` must verify against downloaded bytes; filename, file ID and exact size come from current official version and are never guessed. Bytes are never committed. ZIP contents are restricted to first CSV header lines, not animal GPS observations, plus extension counts. XLSX gets only workbook sheet names, not capture or fruit counts. No individual identifiers, original XY, coordinate-bearing member filenames, biological values or source rows are printed.

**Stop conditions:** Original byte download HTTP 401/403, metadata/version drift, publisher digest disagreement, unexpectedly large archive, ZIP traversal or decompression bomb, worksheet schema unknown. Any failed source remains inaccessible; do not try unverified mirrors, invent measured resource values, or report a negative biological result.

**If both source structures pass:** separate original-source exploratory models may be fitted only after a new response-blind table schema and testing contract has been frozen. The 49-plot true-food source addresses regional/local resource composition and does not contain flight altitude; the 2026 3D source addresses height and landscape and does not contain measured food abundance.
