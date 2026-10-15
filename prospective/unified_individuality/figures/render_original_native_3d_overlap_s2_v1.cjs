#!/usr/bin/env node
// Deterministically redraw the original JAE native 3D overlap source-result summary.
// This is historical source recovery, NOT a new bat analysis or hypothesis test.
"use strict";
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const root=__dirname;
const source=fs.readFileSync(path.join(root,"ORIGINAL_NATIVE_3D_OVERLAP_SUMMARY_V1.json"));
const got=crypto.createHash("sha1").update(Buffer.concat([Buffer.from("blob "+source.length+"\0"),source])).digest("hex");
if(got!=="c1d37e42f72f59e5aba364daec9aef68b47778b6")throw Error("Original native 3D source Git blob hash drift: "+got);
const original=JSON.parse(source.toString("utf8"));
function renderNative3D(d){
  if(d.study_id!=="batter-3d-niche-partition-v1"||d.workflow?.run_id!==36881187913)throw Error("Unexpected source");
  const keys=["hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"];
  const labels={hypsignathus:"H. monstrosus",phyllostomus_2022:"P. hastatus 2022",phyllostomus_2023:"P. hastatus 2023",phyllostomus_2016:"P. hastatus 2016"};
  const ns=[8,5,6,9];
  const W=1770,H=1400,plot0=540,plot1=1380;
  const x=v=>plot0+v/.8*(plot1-plot0);
  const esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  const out=['<svg xmlns="http://www.w3.org/2000/svg" width="177mm" height="140mm" viewBox="0 0 1770 1400" role="img" aria-label="Figure S2: original 500-m horizontal versus joint native 3D overlap, same animal versus other animal session pairs. Source descriptive values, not co-use or terrain-corrected metrics.">',
    '<title>Figure S2. Original horizontal versus three-dimensional probability overlap</title>',
    '<desc>Four original eligible bat panels, each with same-animal and other-animal session comparisons. Hollow markers show O_XY and filled markers show O_XYZ, both source pair-and-individual averaged. The reduction when native session-centered altitude is added is shown by the connecting line. Raw source result, not calibrated partitioning inference or real-time encounter.</desc>',
    '<rect width="1770" height="1400" fill="#fff"/>'];
  const ink="#263a46",muted="#657785",sea="#236879",rule="#d5dfe5",bg="#f3f7f9";
  const text=(xx,yy,value,size=25,strong=false,color=ink,anchor="start")=>out.push(`<text x="${xx}" y="${yy}" font-family="Arial,Helvetica,sans-serif" font-size="${size}" font-weight="${strong?700:400}" text-anchor="${anchor}" fill="${color}">${esc(value)}</text>`);
  const line=(x1,y1,x2,y2,color=rule,width=2)=>out.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}"/>`);
  const circle=(xx,yy,r,fill,stroke=sea,w=3)=>out.push(`<circle cx="${xx}" cy="${yy}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${w}"/>`);
  text(62,72,"FIGURE S2  |  HORIZONTAL vs. JOINT 3D OVERLAP",40,true);
  text(62,117,"Original 500-m cell analysis; native heights, session-median centered; NOT terrain corrected",24,false,muted);
  line(62,142,1708,142,rule,3);
  text(62,206,"Study / n",28,true);
  text(346,206,"Session pairing",26,true);
  text(950,206,"Probability overlap coefficient",28,true,ink,"middle");
  text(1685,206,"O_XY  /  O_XYZ",26,true,ink,"end");
  for(let k=0;k<=4;k++){const p=k*.2;const xx=x(p);line(xx,244,xx,1139,rule,2);text(xx,1189,p.toFixed(1),25,false,muted,"middle")}
  keys.forEach((key,i)=>{
    const drow=d.panels[key];
    if(!drow.supported||drow.eligible_individuals!==ns[i])throw Error("Panel source changed "+key);
    const y0=330+i*217;
    out.push(`<rect x="62" y="${y0-69}" width="1648" height="192" rx="8" fill="${i%2===0?bg:"#ffffff"}"/>`);
    text(68,y0+21,labels[key],27,true,ink);
    text(68,y0+60,`n=${ns[i]}`,23,false,muted);
    for(const [j,type,label] of [[0,"self","Same animal"],[1,"other","Other animals"]]){
      const y=y0+(j?78:0);
      const xy=drow[type+"_oxy"],xyz=drow[type+"_oxyz"];
      if(!Number.isFinite(xy)||!Number.isFinite(xyz)||xy<xyz||xy>.8||xyz<0)throw Error("Overlap range invalid "+key+" "+type);
      const xxy=x(xy),xxz=x(xyz);
      text(352,y+11,label,25,false,ink);
      line(xxz,y,xxy,y,"#9eb9c1",10);
      circle(xxy,y,11,"#fff",sea,4);circle(xxz,y,11,sea,"#fff",2);
      text(1685,y+9,`${xy.toFixed(3)} / ${xyz.toFixed(3)}`,26,j===1,ink,"end");
    }
  });
  line(plot0,1139,plot1,1139,ink,3);
  circle(73,1261,11,"#ffffff",sea,4); text(96,1271,"Open = horizontal O_XY",26);
  circle(552,1261,11,sea,"#fff",2);text(575,1271,"Filled = joint 3D O_XYZ",26);
  text(65,1330,"Source-evaluable session comparisons; 4 panels, only 2 species. Values are descriptive, not CIs or p-values.",22,false,muted);
  text(65,1371,"Vertical effect must be tested separately: terrain-relative S_rel (0/4 positive) and co-use I (1/4 positive).",22,false,muted);
  out.push("</svg>");
  return out.join("\n")+"\n";
}
const result=renderNative3D(original);
const dest=path.join(root,"FIGURE_S2_NATIVE_HORIZONTAL_AND_JOINT_3D_OVERLAP_V1.svg");
fs.writeFileSync(dest,result,"utf8");
console.log("Source-calibrated-original Figure S2 (descriptive only)",dest,"bytes",Buffer.byteLength(result),"source SHA",got);
