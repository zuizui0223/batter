// Reproduce the source-safe manuscript SVGs from audited aggregate JSON.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
function render(d){
 const colors={vivesi:"#007A78",noctule:"#6F4597"}, labels={vivesi:"M. vivesi",noctule:"N. noctula"}, names=Object.keys(colors), weights=["count","positive_fix"], scales=[500,1000,2000], m="concentration_log_effective_cell_ratio";
 const txt=(x,y,s,extra="")=>`<text x="${x}" y="${y}" ${extra}>${s}</text>`, line=(x1,y1,x2,y2,extra="")=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" ${extra}/>`, circle=(x,y,r,extra="")=>`<circle cx="${x}" cy="${y}" r="${r}" ${extra}/>`, rect=(x,y,w,h,extra="")=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" ${extra}/>`, diamond=(x,y,c)=>`<path d="M${x} ${y-5}L${x+5} ${y}L${x} ${y+5}L${x-5} ${y}Z" fill="${c}"/>`;
 const wrap=(w,h,title,body)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img"><title>${title}</title><rect width="100%" height="100%" fill="white"/><g font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#17212b">${body}</g></svg>\n`;
 let g=txt(30,30,"Activity concentration beyond the recorded-path reference",'font-size="20" font-weight="bold"');
 g+=txt(30,50,"Four grid origins (small points); equal-origin estimate (diamond)",'fill="#475569"');
 const y=v=>350-v/0.45*250;
 weights.forEach((w,p)=>{const left=95+p*395,right=left+335;
 g+=txt(left,77,p===0?"a  Count marks":"b  Positive fixes",'font-weight="bold" font-size="15"');
 for(let k=0;k<=4;k++){let v=k/10;g+=line(left,y(v),right,y(v),`stroke="${k===0?"#64748b":"#e2e8f0"}"`);g+=txt(left-9,y(v)+4,v.toFixed(1),'text-anchor="end"');}
 g+=line(left,100,left,350,'stroke="#64748b"');
 scales.forEach((s,i)=>{let x=left+58+i*107;g+=txt(x,372,String(s/1000),'text-anchor="middle"');
 names.forEach((n,j)=>{let v=d.cohorts[n].concentration[`${w}_${s}m`], xx=x+(j===0?-15:15), c=colors[n];for(const [k,o] of v.origins.entries()){g+=circle(xx+(k-1.5)*5,y(o.metrics[m].excess),3.4,`fill="white" stroke="${c}" stroke-width="1.4"`);}g+=diamond(xx,y(v.equal_origin[m].excess),c);});});
 g+=txt((left+right)/2,399,"Grid size (km)",'text-anchor="middle"');
 });
 g+=txt(20,225,"Excess concentration (nats)",'transform="rotate(-90 20 225)" text-anchor="middle"');
 names.forEach((n,j)=>{g+=diamond(240+j*200,431,colors[n])+txt(253+j*200,435,labels[n]+(j===0?" (n = 11)":" (n = 22)"),'font-style="italic"');});
 g+=txt(30,460,"All 24 cohort × scale × weight × origin-group comparisons are not independent tests.",'font-size="11" fill="#475569"').replace("24 cohort × scale × weight × origin-group comparisons","Grid-origin, scale and weighting sensitivities");
 const fig2=wrap(850,480,"Concentration relative to a time-conditioned recorded-path reference",g);
 let h=txt(30,30,"Earlier-to-later conditional prediction of detected marks",'font-size="20" font-weight="bold"');
 h+=txt(30,50,"Reference interval: rotation 5th–95th percentiles (not a confidence interval)",'fill="#475569"');
 const X=v=>240+(v+.025)/.045*500;
 const ys=[125,185,280,340];
 for(const v of [-.02,-.01,0,.01,.02]){h+=line(X(v),90,X(v),372,`stroke="${v===0?"#64748b":"#e2e8f0"}" ${v===0?'stroke-dasharray="4 3"':""}`);h+=txt(X(v),392,v.toFixed(2),'text-anchor="middle"');}
 names.forEach((n,j)=>{h+=txt(34,ys[j*2]-24,labels[n]+(j===0?" (n = 7)":" (n = 20)"),'font-style="italic" font-weight="bold"');
 weights.forEach((w,k)=>{let v=d.cohorts[n].prediction[w].equal_origin,y=ys[j*2+k],c=colors[n],q=v.reference_q05_median_q95;h+=txt(34,y+4,k===0?"Count marks":"Positive fixes");h+=line(X(q[0]),y,X(q[2]),y,'stroke="#94a3b8" stroke-width="5" stroke-linecap="round"');h+=line(X(q[0]),y-7,X(q[0]),y+7,'stroke="#94a3b8"');h+=line(X(q[2]),y-7,X(q[2]),y+7,'stroke="#94a3b8"');h+=circle(X(v.reference_mean),y,5,'fill="white" stroke="#64748b" stroke-width="1.5"');h+=diamond(X(v.mean_gain_nats_per_mark),y,c);h+=txt(759,y+4,`${v.passing_origins}/4 origins`,'font-size="12"');});});
 h+=txt(490,422,"Held-out log-score gain (nats per mark)",'text-anchor="middle"');
 h+=diamond(215,452,"#334155")+txt(228,456,"Observed gain")+circle(370,452,5,'fill="white" stroke="#64748b" stroke-width="1.5"')+txt(383,456,"Reference mean");
 h+=txt(30,479,"Neither cohort met the robust prediction criterion; the held-out GPS path and mark totals are conditioned on.",'font-size="11" fill="#475569"');
 const fig3=wrap(865,498,"Forward prediction relative to training-only rotation reference",h);
 return {fig2,fig3};
}
const root=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(fs.readFileSync(path.join(root,'results/audited_aggregate_v1.json'),'utf8'));
const {fig2,fig3}=render(data);
fs.mkdirSync(path.join(root,'figures'),{recursive:true});
fs.writeFileSync(path.join(root,'figures/fig2_concentration.svg'),fig2);
fs.writeFileSync(path.join(root,'figures/fig3_forward_prediction.svg'),fig3);
