#!/usr/bin/env node
// Build review-facing source-control-free text from the coherent unified scientific
// manuscript. This does NOT provide an anonymized data archive or journal PDF.
"use strict";
const fs=require("node:fs"),path=require("node:path");
function anon(s){
  const between=(a,b)=>{const p=s.indexOf(a),q=s.indexOf(b,p+a.length);if(p<0||q<0)throw Error("Missing section: "+a+" -> "+b);return s.slice(p+a.length,q).trim();};
  const title=s.match(/^# (.+)$/m)?.[1]?.trim();
  const lay=between("## Lay Summary\n","## Abstract\n");
  let abstract=between("## Abstract\n","## Introduction\n");
  const keywordList="bats; behavioral individuality; individual specialization; development; three-dimensional space use; context dependence; spatial partitioning";
  const body=("## Introduction\n"+between("## Introduction\n","## Figure legends (rendered source-backed SVGs)"));
  const refs=between("## Consolidated working references\n","**These 34 scholarly entries");
  const figureLegends=between("## Figure legends (rendered source-backed SVGs)\n","## Consolidated working references\n");
  const w=x=>x.trim().split(/\s+/).length;
  if(w(abstract)>250||w(lay)>75||title.length>100)throw Error("Journal length check failed");
  if(!figureLegends.includes("**Figure 6.")||!body.includes("**post-outcome**"))throw Error("Critical scientific result missing");
  const stripLinks=text=>text.replace(/\[([^\]]+)\]\([^)]+\)/g,"$1");
  // Preserve the empirical claim but remove internal repository paths and private source-provenance links.
  let figure=stripLinks(figureLegends)
    .replace(/Original-file checksums and biological provenance are recorded in source recovery receipt\./g,"Original profile source data and reconstruction rules are provided in the anonymized supplementary analysis archive.")
    .replace(/See source recovery receipt\./g,"The original individual-profile source and checksum receipts are identified in the anonymized analysis archive.");
  figure=figure.replace(/figure atlas/gi,"figures");
  let main=stripLinks(body);
  main=main.replace(/\bcombined Supporting Information draft\b/g,"Supplementary Material");
  main=main.replace(/the \[?combined Supporting Information draft\]?/g,"Supplementary Material");
  const note="All study data were originally collected and publicly released by the cited source studies. This is a secondary analysis and involved no new handling of animals. Source DOI identifiers, frozen analysis protocols, reproducibility code, and exact data-access instructions are listed in the separately submitted Supplementary Material and anonymized analysis archive. The intended archive review link is [ANONYMIZED_REVIEW_ARCHIVE_URL] (pending placement). Redistribution of source files will respect the original licence and permissions.";
  const ethics="The original animal experiments and wild tracking programmes were conducted by their source-study investigators under the ethics and permits described in the original publications. The present comparative reanalysis involved no new animal manipulation.";
  const ai="Automated tools assisted with portions of literature triage, code review and drafting, figure production, and manuscript editing. Human authors must review, verify, and finalize the specific tool/version/date and accountability disclosure for the journal submission. These tools did not create or alter the original source measurements.";
  const output=`## Lay Summary\n\n${lay}\n\n# ${title}\n\n## Abstract\n\n${abstract}\n\n**Keywords:** ${keywordList}\n\n${main.trim()}\n\n## Data availability\n\n${note}\n\n## Ethics\n\n${ethics}\n\n## Automated-assistance disclosure (author verification pending)\n\n${ai}\n\n## References\n\n${refs.trim()}\n\n## Figure legends\n\n${figure.trim()}\n`;
  const bad=["zuizui0223","release/jae","prospective/public-causal-synthesis","github.com/zuizui","manuscript blob SHA","JAE v0.4.0 rc2","BE v1 manuscript"];
  for(const x of bad)if(output.includes(x))throw Error("Anonymous text contains source identifier: "+x);
  if(output.match(/^## Lay Summary/)===null||output.indexOf("## References")>output.indexOf("## Figure legends"))throw Error("Section order invalid");
  return {text:output,abstract_words:w(abstract),lay_words:w(lay),title_length:title.length,ref_count:(refs.match(/10\.\d{4,9}\//g)||[]).length};
}
const root=__dirname,source=fs.readFileSync(path.join(root,"INTEGRATED_MANUSCRIPT_V1.md"),"utf8");
const built=anon(source);
const dest=path.join(root,"COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md");
fs.writeFileSync(dest,built.text,"utf8");
console.log("Anonymous manuscript draft",dest,"lay",built.lay_words,"abstract",built.abstract_words,"references",built.ref_count);
