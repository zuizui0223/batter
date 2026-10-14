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
  const refs=between("## Consolidated working references\n","**These 35 scholarly entries");
  const figureLegends=between("## Figure legends (rendered source-backed SVGs)\n","## Consolidated working references\n");
  const w=x=>x.trim().split(/\s+/).length;
  if(w(abstract)>250||w(lay)>75||title.length>100)throw Error("Journal length check failed");
  if(!figureLegends.includes("**Figure 6.")||!body.includes("**post-outcome**"))throw Error("Critical scientific result missing");
  const stripLinks=text=>text.replace(/\[([^\]]+)\]\([^)]+\)/g,"$1");
  // Preserve the empirical claim but remove internal repository paths and private source-provenance links.
  let figure=stripLinks(figureLegends)
    .replace(/Original-file checksums and biological provenance are recorded in source recovery receipt\./g,"Original profile source data and reconstruction rules are provided in the anonymized supplementary analysis archive.")
    .replace(/See source recovery receipt\./g,"The source-profile archive and checksum receipts are included in the anonymized supplementary analysis package.");
  figure=figure.replace(/figure atlas/gi,"figures");
  let main=stripLinks(body);
  main=main.replace(/the combined Supporting Information draft/g,"Supplementary Material");
  main=main.replace(/the \[combined Supporting Information draft\]/g,"Supplementary Material");
  const note="All primary datasets were originally collected and publicly shared by the cited source studies. This study is a secondary reanalysis with no new animal manipulation. Exact original source DOIs and frozen analysis protocols are described in the independently submitted Supplementary Material. Analysis code and legally distributable derived products will be provided through [ANONYMIZED_REVIEW_ARCHIVE_URL] after placement on a double-anonymized research archive.";
  const ethics="The original experiments and wild tracking programmes were conducted by their source-study investigators under the ethics and permits reported in those publications. The present reanalysis required no new bat handling or experimental manipulation.";
  const ai="Automated assistance was used for parts of literature triage, source-code/figure drafting, provenance organization and scientific text editing. Exact model/version/date details and human accountability statements are subject to final author verification before submission; original source observations were not created or altered by these tools.";
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
