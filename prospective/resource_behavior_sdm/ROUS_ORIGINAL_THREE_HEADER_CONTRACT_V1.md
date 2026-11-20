# Rousettus Dryad original 2020: three small CSV headers (frozen admission)

Date 2026-11-20. This stage follows the completed official Dryad API dataset/version/file metadata PASS [Actions #44681870365](https://github.com/zuizui0223/batter/actions/runs/44681870365). It does NOT inspect original treatment/visit/fruit-tree values, which would require separate frozen outcomes/eligibility.

Exactly three publicly listed tiny original files are allowed: `Field_Manipulation_Table.csv`, `manipulations_trees_locations.csv`, `Tags_manipulated_and_visiting.csv`. The original Dryad version, public file IDs, original reported digest and byte lengths must be obtained from its official v2 API. File downloads must start at the official `/api/v2/files/{file_id}/download` path, be under a 100,000 byte cap per file, and match the exact publisher digest before the *first CSV row only* is parsed. No file rows past the header, original tag/animal IDs, original tree coordinates, original treatment data, or original SQLite movements may be stored.

The returned artifact has permitted public column names, bytes, digest strings and a PASS/STOP record only. A PASS proves provenance and source header shape, **not** that the three tables share a valid individual×date×tree key; the latter needs a pre-outcome structural support audit after source access. Source correction/retry should preserve the initial failure history.

Never read/distribute the 285-MB original SQLite tracks in this stage. Resource-context exposure here is an experimental odor cue for **fruitless** Ficus trees, not demonstrated fruit supply, 3-D flight height or a universal mutualism law. Any true higher-D ecological prediction remains NOT ESTIMATED.
