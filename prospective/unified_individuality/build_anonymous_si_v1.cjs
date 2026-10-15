#!/usr/bin/env node
// Anonymize publication-origin metadata in the working SI without changing the
// underlying experimental/field numeric source tables.
"use strict";
const fs=require("node:fs"),path=require("node:path");
function anonSI(source) {
  let s=source;
  const first=s.indexOf("## Supplementary Table U1.");
  if(first<0||s.indexOf("## Scientific scope and dual-source provenance")<0)throw Error("Wrong SI source document");
  const intro=`# Supplementary Material — anonymous review draft

**Associated manuscript:** Persistent behavioral individuality and the limits of 3D niche inference in bats (anonymous draft).

**Contents:** experimental source metadata and frozen source-specific nulls, original six-panel wild vertical identity, terrain-relative fidelity and segregation tests, contemporaneous co-use uncertainty, external boundary cases, and evidence-tier rules.

**Review status:** source tables and estimands are retained; anonymous computational archive URL and author approvals are pending. This file is not the final submission version.

## Study scope and source-provenance principles

The study reanalyzes publicly archived bat experiments and independent repeated field tracking datasets. The individual bat is the biological replication unit; trial, call, GPS fix, session, dyad and permutation counts are not substitutes for independent biological individuals. Study-specific statistical endpoints and exchangeability nulls were recorded before their corresponding result values were opened, whereas the across-source synthesis was iteratively developed and not preregistered as a prospective multisystem meta-analysis. Field terrain-relative and co-use analyses were explicitly **post-outcome diagnostics**.

The detailed reproducibility contracts and legally redistributable data-derived tables will be linked from the anonymized source archive when placed: [ANONYMIZED_REVIEW_ARCHIVE_URL]. Original source data are cited under their public source DOIs.

`;
  s=intro+s.slice(first);
  // Treat this as the SI for one manuscript, rather than names of earlier working papers.
  s=s.replace(/Supplementary Table U([1-9][0-9]*)/g,"Supplementary Table S$1")
     .replace(/Supplementary Methods U([1-9][0-9]*)/g,"Supplementary Methods S$1")
     .replace(/\bTable U([1-9][0-9]*)\b/g,"Table S$1")
     .replace(/\bU([1-9][0-9]*)\b/g,"S$1") // Catch plural/table-range references, not only singular headings
     .replace(/original JAE/g,"original tracking")
     .replace(/JAE original/g,"original tracking")
     .replace(/the JAE original/g,"the original tracking")
     .replace(/in the JAE original source receipts/g,"in the original tracking source receipts")
     .replace(/JAE rc2 branch/g,"later frozen tracking source")
     .replace(/workflow run \*\*36881187913\*\*/g,"original archived execution")
     .replace(/commit 676ae76aec952a38410766577d51c5eca438a6c1/g,"its frozen source-control state")
     .replace(/commit 819acc829d615485b57033f1ddcbebf64b4b49a0/g,"the later original terrain-source state")
     .replace(/original Git blob SHA \*\*c1d37e42f72f59e5aba364daec9aef68b47778b6\*\*/g,"original source digest kept in the blinded audit receipt")
     .replace(/BE audit/g,"original source audit")
     .replace(/\bBE\b/g,"experimental")
     .replace(/the \[Figure 5B\]\(figures\/original_jae\/figure6_individual_centered_shape_profiles.png\)/g,"Figure 5B")
     .replace(/\[ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md\]\(ORIGINAL_PROFILE_RECOVERY_RECEIPT_V1.md\)/g,"the source-profile archive receipt");
  // Repair grammatical collisions caused by metadata anonymization; leave scientific values untouched.
  s=s.replace(/original tracking 500-m native-height tracking original archived execution/g,
              "original archived 500-m native-height tracking execution")
     .replace(/historical subsequent terrain workflow the later original terrain-source state/g,
              "the subsequent historical terrain source-control state")
     .replace(/the later later frozen tracking source/g,"the later frozen tracking source");
  const header="## Supplementary publication and data-provenance boundary";
  const position=s.indexOf(header);
  if(position<0)throw Error("No licensing section");
  s=s.slice(0,position)+`## Supplementary data access, redistribution and ethics

Original bat datasets remain governed by source-level licences and permit conditions. For example, the Taub and Yovel public Dropbox archive is linked in the original research publication but no independent redistribution permission was established by the present reanalysis. Raw third-party datasets should not be duplicated into the anonymized archive without source permission or editorial authorization. Public source DOIs and retrieval instructions are provided above; code and legally distributable derived products will be placed at [ANONYMIZED_REVIEW_ARCHIVE_URL].

The present study involved no new handling or manipulation of animals. Ethical oversight and permits for the underlying studies are reported by the original source investigators. The final anonymized archive link and source-data redistribution statements require author and journal verification.
`;
  s=s.replace(/`node figures\/generate_integrated_figures_v1\.cjs`/g,"the anonymized figure-generation script")
     .replace(/`figures\/FROZEN_FIGURE_DATA_V1\.json`/g,"the locked source-summary record")
     .replace(/`Unified manuscript figures \(source-summary guard\)`/g,"the accompanying reproducibility audit")
     .replace(/`INTEGRATION_QA_V1\.md`/g,"the source result audit")
     .replace(/`release\/jae[^`]*`/g,"the frozen tracking archive")
     .replace(/`prospective\/public[^`]*`/g,"the frozen experimental archive");
  for(const key of ["zuizui0223","release/jae","prospective/public-causal-synthesis","JAE v0.4.0 rc2","manuscript SHA"]){
     if(s.includes(key))throw Error("Source identity leak: "+key);
  }
  for(const key of ["Supplementary Table S1","Supplementary Table S7","Supplementary Table S13","Supplementary Methods S2","0.0362","0.0231","post-outcome","terrain-relative proxy","[ANONYMIZED_REVIEW_ARCHIVE_URL]"]){
    if(!s.includes(key))throw Error("Missing mandatory source/claim: "+key);
  }
  return s;
}
const root=__dirname,source=fs.readFileSync(path.join(root,"SUPPORTING_INFORMATION_DRAFT_V1.md"),"utf8");
const result=anonSI(source);
const dest=path.join(root,"SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md");
fs.writeFileSync(dest,result,"utf8");
console.log("Anonymous SI working draft",dest,"words",result.trim().split(/\s+/).length);
