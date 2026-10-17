#!/usr/bin/env node
// Reproducible 177mm-wide printable Figure 5A+B from original source rows.
// Does NOT add any statistical test. Runs on Node built-ins only.
"use strict";
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
function renderComposite(s,o){
const v=[],esc=x=>String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const COL={ink:"#1D303E",gray:"#5C7180",rule:"#D6E0E7",teal:"#277F83",rust:"#A16C60",pale:"#F2F6F8",white:"#FFFFFF"};
const rect=(x,y,w,h,fill,stroke="none",sw=0)=>v.push(`<rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${w.toFixed(2)}" height="${h.toFixed(2)}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);
const text=(x,y,t,size=30,weight=400,color=COL.ink,anchor="start",extra="")=>v.push(`<text x="${x.toFixed(2)}" y="${y.toFixed(2)}" font-family="Arial, Helvetica, sans-serif" font-size="${size}" font-weight="${weight}" fill="${color}" text-anchor="${anchor}" ${extra}>${esc(t)}</text>`);
const line=(x1,y1,x2,y2,color=COL.rule,w=2)=>v.push(`<line x1="${x1.toFixed(2)}" y1="${y1.toFixed(2)}" x2="${x2.toFixed(2)}" y2="${y2.toFixed(2)}" stroke="${color}" stroke-width="${w}"/>`);
const circle=(x,y,r,fill,stroke=COL.white)=>v.push(`<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`);
const sign=(x,n=3)=>(x>=0?"+":"")+x.toFixed(n);
v.push('<svg xmlns="http://www.w3.org/2000/svg" width="177mm" height="238mm" viewBox="0 0 1770 2380" role="img" aria-label="Figure 5. Centered-shape identity and 103 original individual-by-panel vertical probability profiles">');
v.push("<title>Figure 5. Identity tests and descriptive probability profiles for vertical space use</title>");
v.push("<desc>Panel A shows calibrated whole-profile tests, including the non-supporting Tadarida case. Panel B contains the unmodified underlying probability vectors for 103 original individual-by-panel records across five comparative panels, with ten height bins; the profiles are descriptive only.</desc>");
rect(0,0,1770,2380,COL.white);
text(55,76,"FIGURE 5  |  VERTICAL-USE PROBABILITY SHAPES",45,700);
text(55,118,"Inferential whole-profile results (A) and descriptive individual profiles (B)",28,400,COL.gray);
line(55,137,1710,137,COL.rule,3);
text(55,186,"A   Identity persists after session-median centering",37,700);
text(55,227,"Calibrated excess (observed − permutation-null mean), nats per fix",28,400,COL.gray);
const xLeft=525,xRight=1328,lo=-0.08,hi=0.65,mx=z=>xLeft+(z-lo)/(hi-lo)*(xRight-xLeft),zero=mx(0);
if(s.centered.length!==6)throw Error("Centered test panel n");
s.centered.forEach((r,i)=>{const y=282+i*53,x=mx(r.calibrated_excess);if(i%2===0)rect(55,y-31,1640,47,COL.pale);
text(65,y+3,r.label,29);line(zero,y-29,zero,y+19,COL.rule,2);
line(Math.min(zero,x),y,Math.max(zero,x),y,r.supported?COL.teal:COL.rust,5);
circle(x,y,8,r.supported?COL.teal:COL.white,r.supported?COL.white:COL.rust);
text(1351,y+6,`${sign(r.calibrated_excess)}   p=${r.p_upper.toFixed(4)}   n=${r.n}`,25,500,r.supported?COL.ink:COL.rust);
});
line(xLeft,604,xRight,604,COL.rule,2);
[-0.05,0,0.2,0.4,0.6].forEach(q=>{const x=mx(q);line(x,597,x,613,COL.gray,1);text(x,647,q.toFixed(2),24,400,COL.gray,"middle");});
text(935,680,"Five comparative panels PASS; focal Tadarida FAIL (p = 0.5121)",28,500,COL.rust,"middle");
line(55,713,1710,713,COL.rule,3);
text(55,761,"B   Individual-specific probability profiles",37,700);
text(55,801,"Original self-predictor profiles (103 individual-by-panel records)",27,400,COL.gray);
if(o.study_id!=="batter-centered-shape-profile-descriptive-v1"||o.individual_profiles.length!==103)throw Error("Original JAE 103-row source mismatch");
if(o.claim_boundary.new_hypothesis_test!==false)throw Error("Source description not solely descriptive");
const specs=[["eidolon","E. helvum",20],["hypsignathus","H. monstrosus",24],["phyllostomus_2022","P. hastatus 2022",33],["phyllostomus_2023","P. hastatus 2023",16],["phyllostomus_2016","P. hastatus 2016",10]];
const probs=o.individual_profiles;for(const row of probs){const a=row.bin_probabilities;if(a.length!==10||a.some(x=>x<0||x>1||!Number.isFinite(x))||Math.abs(a.reduce((p,q)=>p+q,0)-1)>1e-9)throw Error("Invalid original probability row");}
const vMax=Math.max(...probs.flatMap(x=>x.bin_probabilities));
const anchors=["#440154","#414487","#2A788E","#22A884","#7AD151","#FDE725"];
const rgb=h=>[1,3,5].map(k=>parseInt(h.slice(k,k+2),16));
const viridis=x=>{let t=Math.max(0,Math.min(1,x))*(anchors.length-1),i=Math.min(anchors.length-2,Math.floor(t)),p=t-i,c=rgb(anchors[i]),d=rgb(anchors[i+1]);return "#"+c.map((z,k)=>Math.round(z+(d[k]-z)*p).toString(16).padStart(2,"0")).join("");};
const x0=350,x1=1473,wbin=(x1-x0)/10,y0=850,yHeight=1280,gap=22,hRow=(yHeight-4*gap)/103;let yy=y0;
for(const [id,name,n] of specs){const group=probs.filter(p=>p.panel===id);if(group.length!==n)throw Error("Original individual n changed "+id);
for(let i=1;i<n;i++)if(group[i].upper_tail_mass_ge_100m+1e-10<group[i-1].upper_tail_mass_ge_100m)throw Error("Original panel row sort");
let boxH=n*hRow;text(332,yy+boxH/2-11,name,29,400,COL.ink,"end");text(332,yy+boxH/2+24,`(n = ${n})`,25,400,COL.gray,"end");
group.forEach((row,j)=>row.bin_probabilities.forEach((p,k)=>rect(x0+k*wbin,yy+j*hRow,wbin+.02,hRow+.02,viridis(p/vMax))));
line(x0+5*wbin,yy,x0+5*wbin,yy+boxH,"#267480",2.5);line(x0,yy,x1,yy,COL.ink,1.5);line(x0,yy+boxH,x1,yy+boxH,COL.ink,1.5);yy+=boxH+gap;}
const cbx=1527,cby=934,cbw=24,cbh=1010,N=130;
for(let k=0;k<N;k++){let t=k/(N-1);rect(cbx,cby+(1-t)*cbh,cbw,cbh/N+1,viridis(t));}
rect(cbx,cby,cbw,cbh,"none",COL.ink,1.5);
[0,.2,.4,.6].filter(x=>x<=vMax).forEach(t=>{const y=cby+cbh*(1-t/vMax);line(cbx+cbw,y,cbx+cbw+9,y,COL.ink,1.4);text(cbx+cbw+13,y+10,t.toFixed(1),25);});
text(1659,1440,"Self-profile probability",28,400,COL.ink,"middle",`transform="rotate(-90 1659 1440)"`);
const binLabels=["below −400","−400:−200","−200:−100","−100:−50","−50:0","0:50","50:100","100:200","200:400","above 400"];
binLabels.forEach((str,k)=>{const x=x0+(k+.5)*wbin;const by=2189;text(x,by,str,25,400,COL.ink,"end",`transform="rotate(-42 ${x.toFixed(2)} ${by})"`);});
text(930,2335,"Session-centered residual-height bin (m)",28,400,COL.gray,"middle");
text(57,2363,"B: no component-wise significance test; color scale shared by all individual profiles.",23,400,COL.gray);
v.push("</svg>");return v.join("\n")+"\n";
}
const dir=__dirname;
const source=fs.readFileSync(path.join(dir,"original_jae/centered_shape_individual_profiles_v1.json"));
const digest=crypto.createHash("sha256").update(source).digest("hex");
if(digest!=="9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2")throw Error("Archived original profile JSON SHA mismatch");
const sanitized=source.toString("utf8").replace(/-Infinity/g,'"negative infinity"').replace(/\bInfinity\b/g,'"positive infinity"');
const original=JSON.parse(sanitized),summary=JSON.parse(fs.readFileSync(path.join(dir,"FROZEN_FIGURE_DATA_V1.json"),"utf8"));
const svg=renderComposite(summary,original);
const target=path.join(dir,"FIGURE_5_COMPOSITE_177x238MM_V2.svg");
fs.writeFileSync(target,svg,"utf8");
console.log("Rendered Figure 5 A+B",target,"n=",original.individual_profiles.length,"size=",Buffer.byteLength(svg));
