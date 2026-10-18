#!/usr/bin/env node
// Figure S1 v2: primary display is exact cohort medians and dependent-dyad spreads.
// Post-outcome DESCRIPTIVE ONLY; reuses frozen summary values, adds NO new source outcome.
"use strict";
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
function cohortFig(meta, sensitivity){
const panels=["eidolon","hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"];
const labels={eidolon:"E. helvum",hypsignathus:"H. monstrosus",phyllostomus_2022:"P. hastatus 2022",phyllostomus_2023:"P. hastatus 2023",phyllostomus_2016:"P. hastatus 2016"};
const cohorts={
"Burkina Faso, Ouagadougou::2013":"Burkina Faso / Ouagadougou 2013",
"Burkina Faso, Ouagadougou::2014":"Burkina Faso / Ouagadougou 2014",
"Ghana, Accra::2009":"Ghana / Accra 2009",
"Ghana, Accra::2011":"Ghana / Accra 2011",
"Ghana, Kibi (Old Tafo)::2013":"Ghana / Kibi (Old Tafo) 2013",
"Zambia, Kasanka::2014":"Zambia / Kasanka 2014",
"Lek Njoukou::2020":"Lek Njoukou 2020",
"Aj-cave (Colony 2)::2022":"Aj-cave (Colony 2) 2022",
"La Gruta (Colony 1)::2022":"La Gruta (Colony 1) 2022",
"Aj-cave (Colony 2)::2023":"Aj-cave (Colony 2) 2023",
"La Gruta (Colony 1)::2023":"La Gruta (Colony 1) 2023",
"La Gruta::2016":"La Gruta 2016"
};
if(meta.schema_version!==2||meta.n_source_panel_profile_records!==103||meta.total_within_cohort_pairs!==684)throw Error("Original overlap frozen summary mismatch");
if(sensitivity.schema_version!==1||sensitivity.source_profile_records!==103||sensitivity.total_within_cohort_nonindependent_pairs!==684)throw Error("Cohort sensitivity summary mismatch");
if(meta.cohort_summary.length!==12||sensitivity.by_cohort.length!==12)throw Error("Twelve source cohort rows required");
const esc=v=>String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const ink="#293640",accent="#286e7c",muted="#586b78",rule="#dce5ea",light="#f7f9fa";
let svg=[];
const W=1770,H=1550,x0=767,x1=1385,plotX=p=>x0+(x1-x0)*p;
svg.push('<svg xmlns="http://www.w3.org/2000/svg" width="177mm" height="155mm" viewBox="0 0 1770 1550" role="img" aria-label="Figure S1: cohort-specific descriptive 1D centered-height profile overlap for 103 panel-indexed profiles; no confidence intervals">');
svg.push('<title>Figure S1. Within-cohort relative-height probability shape similarity</title>');
svg.push('<desc>Eleven within-cohort pair medians in five original tracking panels, plus one source cohort with a single profile and no eligible pair. Ten-to-ninety percentile bars depict dependent-dyad variation, not confidence intervals. Small hollow circles represent single-pair cohorts. All metrics are one-dimensional, session-centered, and not geographic 3D overlap.</desc>');
svg.push(`<rect x="0" y="0" width="${W}" height="${H}" fill="#fff"/>`);
function textAt(x,y,value,size=24,strong=false,color=ink,anchor="start"){svg.push(`<text x="${x}" y="${y}" font-family="Arial,Helvetica,sans-serif" font-size="${size}" font-weight="${strong?700:400}" text-anchor="${anchor}" fill="${color}">${esc(value)}</text>`)}
function line(x,y,x2,y2,color=rule,width=2){svg.push(`<line x1="${x}" y1="${y}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}"/>`)}
function circle(x,y,r=11,fill=accent,stroke="#fff",width=2){svg.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${width}"/>`)}
textAt(56,63,"FIGURE S1  |  COHORT-RESOLVED VERTICAL PROFILE SIMILARITY",40,true);
textAt(56,104,"Ten original session-centered height bins; 103 individual-by-panel records",24,false,muted);
line(56,131,1713,131,rule,3);
textAt(56,193,"Panel",25,true);
textAt(260,193,"Original collection cohort",25,true);
textAt(1060,193,"1D overlap O",25,true,ink,"middle");
textAt(1479,193,"Median",24,true,ink,"middle");
textAt(1608,193,"Profiles",24,true,ink,"middle");
textAt(1724,193,"Pairs",24,true,ink,"end");
const lookup=new Map(sensitivity.by_cohort.map(r=>[r.panel+"|"+r.cohort,r]));
const rows=[];
for(const panel of panels){for(const a of meta.cohort_summary.filter(x=>x.panel===panel)){const t=lookup.get(panel+"|"+a.cohort);if(!t||t.n_unordered_pairs!==a.n_pairs||t.n_source_panel_records!==a.n_individuals)throw Error("Cohort-level source mismatch: "+panel+" "+a.cohort);if(a.median!==null&&Math.abs(a.median-t.dyad_median)>1e-12)throw Error("median mismatch");if(!cohorts[a.cohort])throw Error("Unknown cohort label "+a.cohort);rows.push({...a,cohort_label:cohorts[a.cohort]});}}
if(rows.length!==12)throw Error("Expected 12 cohort rows");
const y0=268,dy=88,yEnd=y0+dy*(rows.length-1),axisY=1345;
for(let k=0;k<=5;k++){let x=plotX(k/5);line(x,229,x,1312,rule,1);textAt(x,axisY,(k/5).toFixed(1),23,false,muted,"middle")}
let last=null;
for(let idx=0;idx<rows.length;idx++){
 const r=rows[idx],y=y0+dy*idx;
 if(r.panel!==last){if(idx>0)line(54,y-47,1713,y-47,"#b8c9d2",2);last=r.panel}
 else if(idx%2===0)svg.push(`<rect x="55" y="${y-37}" width="1657" height="69" fill="${light}"/>`);
 textAt(57,y+9,idx===0||rows[idx-1].panel!==r.panel?labels[r.panel]:"",25,idx===0||rows[idx-1].panel!==r.panel,ink);
 textAt(260,y+9,r.cohort_label,24,false,ink);
 if(r.n_pairs===0){textAt(1085,y+9,"no pair",25,false,muted,"middle");textAt(1479,y+9,"—",24,false,muted,"middle")}
 else {
   if(r.n_pairs>=3){line(plotX(r.p10),y,plotX(r.p90),y,accent,9)}
   circle(plotX(r.median),y,r.n_pairs===1?10:12,r.n_pairs===1?"#fff":accent,accent,3);
   textAt(1479,y+9,r.median.toFixed(3),24,true,ink,"middle");
 }
 textAt(1608,y+9,String(r.n_individuals),24,false,ink,"middle");
 textAt(1724,y+9,String(r.n_pairs),24,false,ink,"end");
}
line(x0,1317,x1,1317,ink,2);
textAt(55,1415,"Bar = dependent-pair 10th–90th percentiles (NOT a confidence interval); hollow dot = one pair.",22,false,muted);
textAt(55,1454,"One original cohort has n = 1 and cannot yield pair overlap; different panels/year are not pooled.",22,false,muted);
textAt(55,1493,"Session-centered relative-height SHAPE only: NOT real 3D co-use, prey sharing, or competition.",22,false,muted);
svg.push("</svg>");
return svg.join("\n")+"\n";
}
const root=__dirname;
const source=fs.readFileSync(path.join(root,"original_jae/centered_shape_individual_profiles_v1.json"));
const digest=crypto.createHash("sha256").update(source).digest("hex");
if(digest!=="9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2")throw Error("Original source SHA changed");
const meta=JSON.parse(fs.readFileSync(path.join(root,"FROZEN_PROFILE_OVERLAP_DESCRIPTIVE_V1.json"),"utf8"));
const sens=JSON.parse(fs.readFileSync(path.join(root,"COHORT_WEIGHT_SENSITIVITY_V1.json"),"utf8"));
const svg=cohortFig(meta,sens);
const output=path.join(root,"FIGURE_S1_WITHIN_COHORT_VERTICAL_SHAPE_OVERLAP_V1.svg");
fs.writeFileSync(output,svg,"utf8");
console.log("PASS rewritten cohort-resolved Figure S1, 12 source cohort rows; original source SHA",digest,"svg bytes",Buffer.byteLength(svg));
