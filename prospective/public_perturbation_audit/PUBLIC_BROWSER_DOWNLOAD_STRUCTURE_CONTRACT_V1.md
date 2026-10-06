# Public browser-download structure contract v1

## Status

**OUTCOME-BLIND PUBLIC-UI STRUCTURAL OPENING.**

The Mendeley public API requires authentication and returned HTTP 401 in the source audit.

This route uses only the public dataset landing page and its visible "Download All" control.

Authorized operations:
- render the public page in a headless browser;
- click Download All;
- save the public archive in the ephemeral CI runner;
- list archive member names and sizes;
- inspect MATLAB variable names/shapes/classes without loading arrays;
- inspect MATLAB script identifiers and file references without executing code or printing numeric arrays.

Forbidden:
- calculate research outcomes;
- print MATLAB array values;
- execute MATLAB;
- run source analysis scripts;
- choose hypotheses using numeric data.

Aharon proceed:
- identify files containing source-described bat/condition/trial variables;
- recover >=4 bat identifiers and >=2 conditions structurally.

Ma proceed:
- determine whether analysis scripts embed or load individual/trial data;
- determine whether raw 3-D files are in the public archive.

All downloaded bytes are discarded at the end of the CI job.
