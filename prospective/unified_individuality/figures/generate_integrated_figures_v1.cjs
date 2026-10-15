#!/usr/bin/env node
// Rebuild six source-backed SVG manuscript figures from FROZEN_FIGURE_DATA_V1.json.
// No new inferential tests. Uses only built-in Node.js modules and source-pinned summary values.
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
function plotAll(d, nativeSource) {
  const C={ink:"#1F2D3B",navy:"#245473",teal:"#287E86",amber:"#B17D35",rust:"#9A6252",light:"#F4F7F9",pale:"#E7EFF3",rule:"#D9E2E8",muted:"#526679",soft:"#A0B3BE",white:"#FFFFFF",gray:"#78909C"};
  const escape=(s)=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  const fmt=(x,n=3)=>Number(x).toFixed(n).replace("-0.000","0.000");
  const sign=(x,n=3)=>`${x>=0?"+":""}${fmt(x,n)}`;
  const label=(s)=>escape(s);
  function fig(title,subtitle,w,h,desc) {
    const b=[`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${escape(title)}">`,
    `<title>${escape(title)}</title><desc>${escape(desc)}</desc>`,
    `<rect width="${w}" height="${h}" fill="${C.white}"/>`];
    function rect(x,y,ww,hh,fill=C.white,stroke="none",sw=0,rx=0){b.push(`<rect x="${x}" y="${y}" width="${ww}" height="${hh}" rx="${rx}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);}
    function line(x,y,x2,y2,color=C.rule,sw=1,dash=""){b.push(`<line x1="${x}" y1="${y}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${sw}" ${dash?`stroke-dasharray="${dash}"`:""}/>`);}
    function circ(x,y,r,fill=C.navy,stroke=C.white,sw=0){b.push(`<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);}
    function txt(x,y,s,size=17,weight=400,color=C.ink,anchor="start",other=""){b.push(`<text x="${x}" y="${y}" font-family="Arial,Helvetica,sans-serif" font-size="${size}" font-weight="${weight}" fill="${color}" text-anchor="${anchor}" ${other}>${label(s)}</text>`);}
    function end(){b.push("</svg>");return b.join("\n")+"\n";}
    txt(46,61,title,32,700);
    txt(47,93,subtitle,17,400,C.muted);
    line(46,110,w-46,110,C.rule,2);
    return {b,rect,line,circ,txt,end,C,w,h};
  }
  function axis(f,x0,x1,y,lo,hi,ticks,tickFmt){const {line,txt}=f;line(x0,y,x1,y,C.rule,2);for(const v of ticks){const x=x0+(v-lo)/(hi-lo)*(x1-x0);line(x,y-6,x,y+6,C.muted,1);txt(x,y+27,tickFmt?tickFmt(v):fmt(v),14,400,C.muted,"middle");}if(lo<0&&hi>0){const x=x0+(0-lo)/(hi-lo)*(x1-x0);line(x,y-13,x,y-60,C.rule,1,"3,5");}}
  function range(x,min,max,a,b){return x+(min-a)/(b-a)*(max-x);}
  const out={};
  // Fig 1: Distinct propositions. Dashed conceptual connectors, no causal arrows.
  {
    const f=fig("One individuality, several empirical questions","Parallel inferential layers across different bat systems (not a single demonstrated causal chain)",1560,660,"Conceptual diagram with separate empirical results and failed transfer from laboratory to wild settings.");
    const groups=[
      {x:47,title:"01  FORMATION / HISTORY",lines:["Late personal history informative","Monotonic formation gate: FAIL","Developmental total-dispersion rule:","not supported"],foot:"BE juvenile and randomized experiments",accent:C.amber},
      {x:430,title:"02  MAINTENANCE",lines:["Identity correspondence retained","across four controlled sensory","and navigation programmes"],foot:"BE, biological n = 3–6 per programme",accent:C.teal},
      {x:813,title:"03  EXPRESSION / TRANSFER",lines:["Coarse movement representation:","transfers across tasks/systems","Fixed detailed geometry: unsupported"],foot:"Rhinolophus and Carollia",accent:C.navy},
      {x:1196,title:"04  FIELD CONSEQUENCE",lines:["Terrain-relative fidelity: 4/4","Positive added segregation: 0/4","Co-use deviation: 1/4 nominal"],foot:"JAE, 2 species / 4 field panels",accent:C.teal}
    ];
    groups.forEach(g=>{f.rect(g.x,155,350,265,C.light,C.rule,1.5,11);f.rect(g.x,155,350,7,g.accent);f.txt(g.x+17,202,g.title,19,700,C.ink);g.lines.forEach((l,i)=>f.txt(g.x+17,249+i*31,l,18,i===0?600:400,C.ink));f.txt(g.x+17,395,g.foot,13,400,C.muted);});
    for(let i=0;i<3;i++){f.line(groups[i].x+350,283,groups[i+1].x,283,C.soft,3,"5,7");}
    f.rect(52,464,1454,104,"#FBFBFC",C.rule,1.5,10);
    f.txt(76,506,"DIRECT LAB → FIELD CARRIER TEST",19,700,C.ink);
    f.txt(575,506,"PASS  /  PASS  /  FAIL  /  STRUCTURAL STOP",20,600,C.rust);
    f.txt(76,542,"Frozen criterion: ≥3/4 panels; observed 2/4 → overall FAIL. Laboratory identity cannot be assumed to explain wild vertical niches.",17,400,C.muted);
    f.txt(55,617,"Source: BE public-causal-synthesis v1 and JAE v0.4.0 rc2. Cross-layer links are conceptual; no shared universal bat policy identified.",14,400,C.muted);
    out["FIGURE_1_INFERENTIAL_LAYERS_V1.svg"]=f.end();
  }
  // Fig 2: Actual B_i individual slopes, developmental null results in separate cards.
  {
    const f=fig("History is predictive, formation law unresolved","The frozen first-flight composite rule fails even though its mean slope is positive",1480,850,"Fourteen source-derived juvenile Spearman slopes, predeclared sign gate, and two separate randomized developmental effect summaries.");
    const {names,slopes_rounded}=d.lab.juvenile;
    const x0=240,x1=772,y0=190,step=37.5,lo=-0.6,hi=1.0;
    f.txt(64,149,"A   Juvenile first-flight experience slopes",20,700,C.ink);
    for (const v of [-.5,0,.5,1]){const x=x0+(v-lo)/(hi-lo)*(x1-x0);f.line(x,179,x,716,v===0?C.muted:C.rule,v===0?1.8:1,v===0?"":"3,5");f.txt(x,746,fmt(v,1),14,400,C.muted,"middle");}
    slopes_rounded.forEach((v,i)=>{const y=y0+i*step;f.txt(73,y+6,`Juvenile ${String(i+1).padStart(2,"0")}`,16,400,C.ink);const x=x0+(v-lo)/(hi-lo)*(x1-x0),xzero=x0+(0-lo)/(hi-lo)*(x1-x0);f.line(Math.min(xzero,x),y,Math.max(xzero,x),y,C.soft,2);f.circ(x,y,7,v>0?C.teal:C.rust,C.white,1.5);f.txt(790,y+5,sign(v,3),14,500,v>0?C.teal:C.rust);});
    f.txt(502,795,"Bᵢ: Spearman slope (source Figure 2A values rounded to 3 decimals)",15,400,C.muted,"middle");
    f.rect(865,143,560,153,C.light,C.rule,1,12);f.txt(889,181,"FROZEN PRIMARY: FAIL",22,700,C.rust);f.txt(889,218,"8/14 positive vs required 10/14",20,600);f.txt(889,255,"Mean B = +0.16733; p = 0.0102",17,400,C.muted);
    f.rect(865,319,560,119,"#EEF5F5",C.rule,1,12);f.txt(889,356,"LATE-HISTORY SECONDARY: SUPPORTED",19,700,C.teal);f.txt(889,395,"12/14 positive; L = +112.5554; p = 0.0001",17);
    f.txt(870,489,"B   Randomized developmental contrasts",20,700);
    f.rect(865,512,560,106,C.light,C.rule,1,10);f.txt(887,541,"Early-environment enrichment (n=29)",17,650);
    f.txt(887,576,"D = +0.734699; p = 0.167785",18,700,C.ink);f.txt(887,602,"Increased total individuality not supported",15,400,C.muted);
    f.rect(865,627,560,106,C.light,C.rule,1,10);f.txt(887,657,"Developmental auditory feedback (n=10)",17,650);f.txt(887,689,"D = −1.425497; p = 0.716667",18,700);f.txt(887,714,"Total individuality difference not supported",15,400,C.muted);
    f.txt(864,786,"Distinct D representations; do not compare their sizes directly.",14,400,C.muted);
    f.txt(49,835,"Source: BE frozen ledger and original Figure 2A script. Unsupported developmental contrasts do not establish treatment equivalence.",13,400,C.muted);
    out["FIGURE_2_HISTORY_AND_DEVELOPMENT_V1.svg"]=f.end();
  }
  // Fig 3: same-individual positive fractions and n/p/rank without pooling unlike estimands.
  {
    const f=fig("Identity remains detectable under acute perturbation","Four independent source-level tests; proportions summarize within-source individual directions only",1510,660,"Four bat experiments showing positive individual fractions, biological n, source-specific exact assignment p values and mapping details.");
    const xs=720,xe=1050,lo=0,hi=1,yy=[212,303,394,485],rows=d.lab.acute;
    f.txt(52,151,"EXPERIMENT / SPECIES",16,700,C.muted);
    f.txt(723,151,"POSITIVE INDIVIDUAL FRACTION",16,700,C.muted);
    f.txt(1085,151,"BIOLOGICAL n  /  EXACT p",16,700,C.muted);
    rows.forEach((a,i)=>{
      const y=yy[i];f.rect(47,y-35,1417,69,i%2===0?C.light:C.white,"none",0,7);
      f.txt(66,y-4,a.name,21,650,C.ink);f.txt(68,y+23,a.species,16,400,C.muted);
      f.line(xs,y,xe,y,C.rule,8);f.line(xs,y,xs+(xe-xs)*a.positive/a.n,y,C.teal,8);f.circ(xs+(xe-xs)*a.positive/a.n,y,8,C.teal,C.white,2);
      f.txt(1061,y+6,`${a.positive}/${a.n}`,19,650,C.teal);
      f.txt(1162,y-4,`n=${a.n};  p=${a.p>=.01?fmt(a.p,5):fmt(a.p,6)}`,17,600);
      f.txt(1162,y+23,a.null_label,15,400,C.muted);
    });
    axis(f,xs,xe,547,0,1,[0,.25,.5,.75,1],v=>`${Math.round(v*100)}%`);
    f.rect(46,592,1418,50,C.light,C.rule,1,8);
    f.txt(67,624,"Foam-controlled masker contrast: 5/5 positive; exact p = 0.025 (same Pipistrellus source, not a fifth independent programme).",16,400,C.ink);
    out["FIGURE_3_ACUTE_CORRESPONDENCE_V1.svg"]=f.end();
  }
  // Fig 4: portable coarse vs unsupported detailed; bridge.
  {
    const f=fig("A portable description is not a fixed trajectory","Prediction under a frozen representation versus direct transfer to wild vertical individuality",1500,660,"Comparison of Rhino and Carollia source-specific predictive tests with unsuccessful frozen field carrier threshold.");
    f.txt(56,150,"A   Fixed representation across controlled movement contexts",21,700,C.ink);
    const cards=[
      {x:55,obj:d.lab.portability[0],fill:"#EEF6F5",edge:C.teal},
      {x:541,obj:d.lab.portability[1],fill:"#EEF6F5",edge:C.teal},
      {x:1027,obj:d.lab.portability[2],fill:C.light,edge:C.rust}
    ];
    cards.forEach(({x,obj,fill,edge})=>{
      f.rect(x,182,415,207,fill,C.rule,1,12);f.rect(x,182,415,6,edge);f.txt(x+20,225,obj.name,24,700);
      f.txt(x+20,257,obj.representation,19,500);
      f.txt(x+20,306,obj.status,22,700,edge);
      f.txt(x+20,339,`K = ${sign(obj.K,5)}; p = ${fmt(obj.p,4)}`,18,500,C.muted);
      f.txt(x+20,369,`biological n = ${obj.n}`,16,400,C.muted);
    });
    f.txt(58,451,"B   Scalar laboratory-style → wild field carrier gate (separate, frozen test)",20,700);
    const states=d.lab.bridge.outcomes, x=58;
    states.forEach((v,i)=>{const xx=x+i*350;const ok=v==="PASS",stop=v==="STRUCTURAL STOP",edge=ok?C.teal:(stop?C.gray:C.rust);
      f.rect(xx,472,324,70,ok?"#EEF6F5":C.light,edge,1.6,7);
      f.txt(xx+162,516,`Panel ${i+1}:  ${v}`,18,700,edge,"middle");
    });
    f.txt(65,582,"Overall FAIL: 2/4 passed; required ≥3/4. This bridge did not test the same bats in laboratory and wild conditions.",19,650,C.rust);
    f.txt(57,627,"K values refer to different source-specific estimands; card widths and spacing do not encode comparative effect magnitude.",14,400,C.muted);
    out["FIGURE_4_PORTABILITY_AND_BRIDGE_V1.svg"]=f.end();
  }
  // Fig 5: source-calibrated centered-shape identity (A) and descriptive central mass range (B).
  {
    const f=fig("Individuals retain the shape of vertical-use probability","Session-median centering removes additive altitude zero-point differences; all tests use their own null calibration",1610,870,"Six original panels and their centered-shape identity above the pipeline-specific null. Descriptive spread of central mass is not separately calibrated.");
    const centered=d.centered, rowsY=[215,298,381,464,547,630];const a0=375,a1=1145,lo=-.10,hi=.65;
    f.txt(62,147,"A   Calibrated excess identity, nats per fix",22,700);f.txt(1175,147,"n  /  p-value",17,700,C.muted);
    for (const v of [-.1,0,.2,.4,.6]){const x=a0+(v-lo)/(hi-lo)*(a1-a0);f.line(x,181,x,679,v===0?C.gray:C.rule,v===0?2:1,v===0?"":"4,5");f.txt(x,706,fmt(v,1),15,400,C.muted,"middle");}
    centered.forEach((o,i)=>{const y=rowsY[i],x=a0+(o.calibrated_excess-lo)/(hi-lo)*(a1-a0),base=a0+(0-lo)/(hi-lo)*(a1-a0);f.rect(51,y-29,1513,59,i%2===0?C.light:C.white,"none",0,7);
      // Repaint baseline for local clarity (bands cover previously drawn reference)
      f.line(base,y-28,base,y+26,C.rule,2);
      f.txt(69,y+6,o.label,20,600,C.ink);f.line(Math.min(x,base),y,Math.max(x,base),y,o.supported?C.teal:C.rust,4);
      f.circ(x,y,9,o.supported?C.teal:C.white,o.supported?C.teal:C.rust,2.4);
      f.txt(Math.min(a1+8,Math.max(a0+12,x+17)),y+5,sign(o.calibrated_excess,3),17,700,o.supported?C.teal:C.rust);
      f.txt(1190,y+5,`n=${o.n}  |  p=${fmt(o.p_upper,4)}`,16,500,o.supported?C.ink:C.rust);
    });
    f.line(a0,686,a1,686,C.rule,2);f.txt(760,756,"Observed score minus within-panel permutation-null mean",16,400,C.muted,"middle");
    f.rect(53,780,1510,54,C.light,C.rule,1,8);
    f.txt(73,813,"Five comparative panels PASS. The motivating Tadarida panel FAILS (p=0.5121). No individual tail component is separately tested.",18,500,C.ink);
    out["FIGURE_5_CENTERED_VERTICAL_IDENTITY_V1.svg"]=f.end();
  }
  // Fig 6: ecologically decisive side-by-side separate estimands.
  {
    const f=fig("Repeatable centered-height use vs added segregation","Two tropical bat species · four eligible tracking panels · post-outcome diagnostic family",1780,866,"Centered relative-height fidelity: original 4/4; positive added S_rel: 0/4; co-use residual-deviation dissimilarity: 1/4 nominal. Not physical between-bat height separation.");
    const rows=d.terrain, yv=[231,352,473,594], labelsX=57;
    if(nativeSource.workflow?.run_id!==36881187913)throw Error("Original geometry source mismatch");
    const xa0=320,xa1=695,xb0=780,xb1=1145,xc0=1250,xc1=1680;
    f.rect(294,126,422,64,"#EEF6F5",C.rule,1,8);f.txt(318,153,"A   Individual fidelity",22,700,C.teal);f.txt(318,179,"V_rel · 4 / 4 supported",17,500,C.ink);
    f.rect(761,126,401,64,C.light,C.rule,1,8);f.txt(781,153,"B   Added segregation",22,700,C.navy);f.txt(781,179,"S_rel · 0 / 4 positive supported",17,500,C.ink);
    f.rect(1231,126,473,64,C.light,C.rule,1,8);f.txt(1250,153,"C   Co-use deviations",22,700,C.ink);f.txt(1250,179,"Centered residuals · 1 / 4 nominal",17,500,C.ink);
    const map=(v,a,b,l,h)=>a+(v-l)/(h-l)*(b-a);
    for (const v of [0,.05,.1,.15]){const x=map(v,xa0,xa1,0,.15);f.line(x,209,x,675,v===0?C.soft:C.rule,v===0?2:1,"3,5");}
    for (const v of [-.1,-.05,0,.05,.1]){const x=map(v,xb0,xb1,-.10,.10);f.line(x,209,x,675,v===0?C.soft:C.rule,v===0?2:1,"3,5");}
    for (const v of [-6,0,6,12]){const x=map(v,xc0,xc1,-6,12);f.line(x,209,x,675,v===0?C.soft:C.rule,v===0?2:1,"3,5");}
    rows.forEach((o,i)=>{
      const y=yv[i],bg=i%2===0?C.light:C.white;f.rect(50,y-43,1660,93,bg,"none",0,8);
      const geometry_n=nativeSource.panels[o.panel]?.eligible_individuals;
      const couse_n=o.couse_n_bats;
      if(!Number.isInteger(geometry_n)||!Number.isInteger(couse_n)||geometry_n<5||couse_n<5)throw Error("Cross-estimand eligible bat n missing "+o.panel);
      f.txt(labelsX,y-7,o.label,19,700,C.ink);
      f.txt(labelsX,y+16,`V/S n=${geometry_n} · I n=${couse_n}`,14,500,C.muted);
      f.txt(labelsX,y+38,`${o.couse_tolerance_s}s · ${o.couse_scope==="all_space"?"all space":"endpoint excl."}`,13,400,C.muted);
      // V_rel: raw retained configuration, not a standardized common effect.
      const xv=map(o.v_rel,xa0,xa1,0,.15);f.line(xa0,y,xv,y,C.teal,4);f.circ(xv,y,8,C.teal,C.white,2);f.txt(xv+13,y-12,sign(o.v_rel,3),16,700,C.teal);
      f.txt(692,y+29,`p=${fmt(o.v_p_upper,4)}`,13,400,C.muted,"end");
      // S_rel: observed point and the label-permutation null 95% envelope (not a sampling CI).
      const xS=map(o.s_rel,xb0,xb1,-.10,.10),qs0=map(o.s_q025,xb0,xb1,-.10,.10),qs1=map(o.s_q975,xb0,xb1,-.10,.10);
      f.line(qs0,y,qs1,y,C.soft,11);f.line(qs0,y-8,qs0,y+8,C.soft,2);f.line(qs1,y-8,qs1,y+8,C.soft,2);
      f.circ(xS,y,8,C.navy,C.white,2);f.txt(xS+12,y-14,sign(o.s_rel,3),15,700,C.navy);
      f.txt(1141,y+29,`p2=${fmt(o.s_p_two_sided,3)}`,13,400,C.muted,"end");
      // Co-use: observed excess with dyad-bootstrap 95% compatibility interval (not formal equivalence).
      const xl=map(o.couse_boot_q025_m,xc0,xc1,-6,12),xh=map(o.couse_boot_q975_m,xc0,xc1,-6,12),xi=map(o.couse_excess_m,xc0,xc1,-6,12);
      f.line(xl,y,xh,y,C.soft,11);f.line(xl,y-9,xl,y+9,C.soft,2);f.line(xh,y-9,xh,y+9,C.soft,2);
      f.circ(xi,y,9,o.couse_supported?C.amber:C.ink,C.white,2);f.txt(xi+11,y-15,`${sign(o.couse_excess_m,2)} m`,15,700,o.couse_supported?C.amber:C.ink);
      f.txt(1681,y+29,`p+ = ${fmt(o.couse_p_upper,4)}`,13,400,C.muted,"end");
    });
    axis(f,xa0,xa1,694,0,.15,[0,.05,.1,.15],v=>fmt(v,2));
    axis(f,xb0,xb1,694,-.10,.10,[-.10,-.05,0,.05,.10],v=>fmt(v,2));
    axis(f,xc0,xc1,694,-6,12,[-6,0,6,12],v=>`${v} m`);
    f.txt(505,751,"V_rel (terrain-relative fidelity)",16,500,C.muted,"middle");
    f.txt(962,751,"S_rel (added segregation)",16,500,C.muted,"middle");
    f.txt(1468,751,"Excess centered-height deviation (m)",16,500,C.muted,"middle");
    f.line(58,778,1714,778,C.rule,1.5);
    f.txt(59,812,"A/B n and C n differ in 3/4 panels; IDs are not cross-matched. B grey = S permutation null; C grey = dyad bootstrap.",16,500,C.ink);
    f.txt(59,841,"Panel C: deviation mismatch, NOT physical gap. 2016 also uses 600s; 2023 all-space. Nulls/intervals differ.",15,400,C.muted);
    out["FIGURE_6_FIDELITY_VS_PARTITIONING_V1.svg"]=f.end();
  }
  return out;
}
const figureDir = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(figureDir, "FROZEN_FIGURE_DATA_V1.json"), "utf8"));
const nativeBytes=fs.readFileSync(path.join(figureDir,"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json"));
const blobSha=crypto.createHash("sha1").update(Buffer.concat([Buffer.from("blob "+nativeBytes.length+"\0"),nativeBytes])).digest("hex");
if(blobSha!=="c1d37e42f72f59e5aba364daec9aef68b47778b6")throw Error("Native 3D source hash drift");
const nativeSource=JSON.parse(nativeBytes.toString("utf8"));
const figures = plotAll(data,nativeSource);
for (const [name, svg] of Object.entries(figures)) {
  if (!/^FIGURE_[1-6]_.*_V1\.svg$/.test(name) || !svg.startsWith("<svg")) throw new Error("Unexpected SVG figure: "+name);
  fs.writeFileSync(path.join(figureDir, name),svg,"utf8");
  process.stdout.write(name+" bytes="+Buffer.byteLength(svg)+"\n");
}
