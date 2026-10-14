#!/usr/bin/env node

// Post-outcome descriptive 1D centered height-profile pair-overlap, never a new null or 3D segregation inference.

"use strict";

function assertTrue(ok,msg){if(!ok)throw Error(msg)}

function overlap(p,q){
  assertTrue(p.length===10&&q.length===10,"10 expected bins");
  let o=0,tv=0;
  for(let k=0;k<10;k++){o+=Math.min(p[k],q[k]);tv+=Math.abs(p[k]-q[k])}
  const complementary=1-tv/2;
  assertTrue(Math.abs(o-complementary)<1e-9,"Overlap not 1 - total variation: "+o+" vs "+complementary);
  assertTrue(o>=-1e-9&&o<=1+1e-9,"Overlap outside [0,1]");
  return o;
}

function quantile(values,p){
  if(!values.length)return null;
  const q=(values.length-1)*p,lower=Math.floor(q),upper=Math.ceil(q),weight=q-lower;
  return values[lower]*(1-weight)+values[upper]*weight;
}

function describe(arr){
  const v=arr.slice().sort((a,b)=>a-b);
  return {n_pairs:v.length,min:v.length?v[0]:null,p10:quantile(v,.1),median:quantile(v,.5),p90:quantile(v,.9),max:v.length?v[v.length-1]:null};
}

function derive(original){
  assertTrue(original.study_id==="batter-centered-shape-profile-descriptive-v1","wrong study");
  assertTrue(original.claim_boundary.new_hypothesis_test===false,"Source new inference forbidden");
  const labels=[
    {key:"eidolon",label:"E. helvum",n:20,expected:41},
    {key:"hypsignathus",label:"H. monstrosus",n:24,expected:276},
    {key:"phyllostomus_2022",label:"P. hastatus 2022",n:33,expected:262},
    {key:"phyllostomus_2023",label:"P. hastatus 2023",n:16,expected:60},
    {key:"phyllostomus_2016",label:"P. hastatus 2016",n:10,expected:45}
  ];
  const individuals=original.individual_profiles;
  assertTrue(individuals.length===103,"Need 103 panel-indexed profiles");
  assertTrue(new Set(individuals.map(r=>r.panel)).size===5,"Exactly 5 panels");
  for(const row of individuals){
    const p=row.bin_probabilities;
    assertTrue(Array.isArray(p)&&p.length===10,"Invalid profile bins");
    assertTrue(p.every(x=>Number.isFinite(x)&&x>=0&&x<=1),"Invalid bin probability");
    assertTrue(Math.abs(p.reduce((a,b)=>a+b,0)-1)<1e-9,"Probabilities don't sum to 1");
    assertTrue(row.cohorts&&typeof row.cohorts==="string","Source cohort required");
    assertTrue(Number.isInteger(row.evaluable_sessions)&&row.evaluable_sessions>=1,"Source sessions invalid");
    assertTrue(Math.abs(p.slice(7).reduce((a,b)=>a+b,0)-row.upper_tail_mass_ge_100m)<1e-9,"Original tail not preserved");
  }
  let panel_summary=[],cohort_summary=[],pair_rows=[];
  for(const entry of labels){
    const people=individuals.filter(r=>r.panel===entry.key).map((r,i)=>({ ...r,source_panel_row_order:i+1}));
    assertTrue(people.length===entry.n,"Unexpected number of bats "+entry.key);
    assertTrue(new Set(people.map(r=>r.individual)).size===entry.n,"Duplicate individual in panel "+entry.key);
    const cohorts=new Map();
    for(const person of people){
      if(!cohorts.has(person.cohorts))cohorts.set(person.cohorts,[]);
      cohorts.get(person.cohorts).push(person);
    }
    let all=[],nCohortsWithPairs=0;
    for(const cohort of [...cohorts.keys()].sort()){
      const peopleHere=cohorts.get(cohort);let values=[];
      if(peopleHere.length>=2)nCohortsWithPairs++;
      for(let i=0;i<peopleHere.length;i++)for(let j=i+1;j<peopleHere.length;j++){
        const x=peopleHere[i],y=peopleHere[j],o=overlap(x.bin_probabilities,y.bin_probabilities);
        const idA=Math.min(x.source_panel_row_order,y.source_panel_row_order);
        const idB=Math.max(x.source_panel_row_order,y.source_panel_row_order);
        pair_rows.push({panel:entry.key,cohort,source_row_order_i:idA,source_row_order_j:idB,overlap:o});
        values.push(o);all.push(o);
      }
      cohort_summary.push({panel:entry.key,cohort,n_individuals:peopleHere.length,...describe(values)});
    }
    assertTrue(all.length===entry.expected,"Structural pair count drift for "+entry.key+": "+all.length);
    panel_summary.push({panel:entry.key,label:entry.label,n_individuals:entry.n,n_source_cohorts:cohorts.size,n_cohorts_with_pairs:nCohortsWithPairs,...describe(all)});
  }
  assertTrue(pair_rows.length===684,"Wrong pair count "+pair_rows.length);
  assertTrue(cohort_summary.length===12,"Wrong source cohort count "+cohort_summary.length);
  return {
    schema_version:2,
    analysis_tier:"post-outcome descriptive vertical profile similarity; no new null, permutation, hypothesis test or biological evidence family",
    original_study_id:original.study_id,
    original_source_sha256:"9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2",
    target:"10-bin equal-session, source-person-specific, session-median-centered altitude self-profiles; same exact panel and cohort only",
    definition:"Overlap=sum(min(p_i[b],p_j[b]))=1-0.5*sum(abs(p_i[b]-p_j[b]))",
    quantiles:"linear interpolation on sorted unordered within-cohort dyads at index (n-1)*q",
    scientific_limits:"One-dimensional centered vertical-profile SHAPE overlap, not geographic 3D habitat overlap, same horizontal support, co-use, foraging or independent biological replication; dyads are nonindependent and distributions arise from self-derived common-cell weights",
    n_source_panel_profile_records:103,n_distinct_literal_source_identifiers:101,global_animal_identity_verified:false,total_within_cohort_pairs:pair_rows.length,
    panel_summary,cohort_summary,pair_rows
  };
}

function csvQuote(v){
  const s=String(v);return /[,"\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;
}

function pairCsv(derived){
  const keys=["panel","cohort","source_row_order_i","source_row_order_j","overlap"];
  return [keys.join(","),...derived.pair_rows.map(r=>keys.map(k=>csvQuote(r[k])).join(","))].join("\n")+"\n";
}

function renderSvg(derived){
  const esc=x=>String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  const ink="#233947",accent="#286F7A",muted="#667888",rule="#D7E2E8",bg="#F3F7F9";
  const v=['<svg xmlns="http://www.w3.org/2000/svg" width="177mm" height="108mm" viewBox="0 0 1770 1080" role="img" aria-label="Within-cohort centered vertical-profile overlap: descriptive nonindependent dyads">',
   '<title>Figure S1. Within-cohort similarity of original centered vertical-use probability profiles</title>',
   '<desc>Five groups of previously estimated individual relative-height probability profiles; points are descriptive within-cohort unordered-dyad medians and horizontal lines are 10th to 90th descriptive percentiles, not confidence intervals. No source-based ecological spatial overlap or new statistical test is represented.</desc>',
   '<rect width="1770" height="1080" fill="#FFFFFF"/>'];
  function tx(x,y,text,size=30,bold=false,color=ink,anchor="start"){v.push('<text x="'+x+'" y="'+y+'" font-family="Arial,Helvetica,sans-serif" font-size="'+size+'" font-weight="'+(bold?"700":"400")+'" fill="'+color+'" text-anchor="'+anchor+'">'+esc(text)+'</text>')}
  function line(x,y,x2,y2,color=rule,w=2){v.push('<line x1="'+x+'" y1="'+y+'" x2="'+x2+'" y2="'+y2+'" stroke="'+color+'" stroke-width="'+w+'"/>')}
  function circle(x,y,r,color=accent){v.push('<circle cx="'+x+'" cy="'+y+'" r="'+r+'" fill="'+color+'" stroke="#FFFFFF" stroke-width="3"/>')}
  const X0=430,X1=1380,map=p=>X0+(X1-X0)*p;
  tx(60,75,"FIGURE S1  |  WITHIN-COHORT VERTICAL PROFILE OVERLAP",46,true);
  tx(60,115,"Source-frozen self-predictor profiles, 10 height bins; 103 panel-indexed records",26,false,muted);
  line(60,141,1710,141);
  tx(61,210,"Original tracking panel",29,true);
  tx(890,210,"Centered 1D overlap coefficient  O = sum(min(p_i, p_j))",28,true,ink,"middle");
  tx(1675,210,"Dyads",28,true,ink,"end");
  for(let k=0;k<=5;k++){const p=k/5,x=map(p);line(x,252,x,823,rule,1);tx(x,869,p.toFixed(1),28,false,muted,"middle")}
  derived.panel_summary.forEach((r,i)=>{
    const y=306+i*114;
    if(i%2===0)v.push('<rect x="53" y="'+(y-52)+'" width="1661" height="101" fill="'+bg+'"/>');
    for(let k=0;k<=5;k++){const x=map(k/5);line(x,y-51,x,y+49,rule,1)}
    tx(64,y+11,r.label,29,false,ink);
    line(map(r.min),y,map(r.max),y,"#98B6BE",3);
    line(map(r.p10),y,map(r.p90),y,accent,10);
    circle(map(r.median),y,11,accent);
    tx(1550,y+8,"median "+r.median.toFixed(3),25,false,ink,"end");
    tx(1694,y+8,String(r.n_pairs),28,true,ink,"end");
  });
  line(X0,823,X1,823,ink,3);
  tx(905,940,"0 = no shared probability mass; 1 = identical normalized shape",27,false,muted,"middle");
  tx(61,1001,"Bars: 10th–90th dependent-pair percentiles, NOT confidence intervals.",26,false,muted);
  tx(61,1042,"Larger cohorts dominate pooled medians; different supports; NOT 3D co-use.",26,false,muted);
  v.push("</svg>");
  return v.join("\n")+"\n";
}

function saveFiles(){
  const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
  const dir=__dirname,source=fs.readFileSync(path.join(dir,"original_jae/centered_shape_individual_profiles_v1.json"));
  const digest=crypto.createHash("sha256").update(source).digest("hex");
  assertTrue(digest==="9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2","Original source bytes changed: "+digest);
  const text=source.toString("utf8");
  assertTrue((text.match(/-Infinity/g)||[]).length===1,"Expected one metadata lower infinite edge");
  assertTrue((text.match(/\bInfinity\b/g)||[]).length===2,"Expected two infinite metadata edges");
  const data=JSON.parse(text.replace(/-Infinity/g,"null").replace(/\bInfinity\b/g,"null"));
  assertTrue(data.centered_edges_m[0]===null&&data.centered_edges_m[10]===null,"Only height bin metadata may be nonfinite");
  const result=derive(data);
  const output={
    summary:JSON.stringify({...result,pair_rows:undefined},null,2)+"\n",
    csv:pairCsv(result),
    figure:renderSvg(result)
  };
  fs.writeFileSync(path.join(dir,"FROZEN_PROFILE_OVERLAP_DESCRIPTIVE_V1.json"),output.summary,"utf8");
  fs.writeFileSync(path.join(dir,"ORIGINAL_PROFILE_WITHIN_COHORT_OVERLAP_PAIRS_V1.csv"),output.csv,"utf8");
  fs.writeFileSync(path.join(dir,"FIGURE_S1_WITHIN_COHORT_VERTICAL_SHAPE_OVERLAP_V1.svg"),output.figure,"utf8");
  console.log("PASS original profile SHA",digest,"individuals",result.n_source_panel_profile_records,"dyads",result.total_within_cohort_pairs);
  for(const r of result.panel_summary)console.log(r.panel,"individuals",r.n_individuals,"dyads",r.n_pairs,"median",r.median.toFixed(6),"q10",r.p10.toFixed(6),"q90",r.p90.toFixed(6));
}

saveFiles();

