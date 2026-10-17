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
    csv:pairCsv(result)
  };
  fs.writeFileSync(path.join(dir,"FROZEN_PROFILE_OVERLAP_DESCRIPTIVE_V1.json"),output.summary,"utf8");
  fs.writeFileSync(path.join(dir,"ORIGINAL_PROFILE_WITHIN_COHORT_OVERLAP_PAIRS_V1.csv"),output.csv,"utf8");
  console.log("PASS original profile SHA",digest,"individuals",result.n_source_panel_profile_records,"dyads",result.total_within_cohort_pairs);
  for(const r of result.panel_summary)console.log(r.panel,"individuals",r.n_individuals,"dyads",r.n_pairs,"median",r.median.toFixed(6),"q10",r.p10.toFixed(6),"q90",r.p90.toFixed(6));
}

saveFiles();

