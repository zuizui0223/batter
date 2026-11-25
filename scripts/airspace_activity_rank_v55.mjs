// V55 descriptive published-table analysis.
function audit(){
 const t=[[19,24,12],[24,43,13],[324,20,13],[291,7,4],[79,3,2],[36,19,3],[229,47,21],[330,27,9],[2,56,0],[7,24,1],[7,13,1],[3,17,1],[3,22,0],[1,20,0],[30,15,5],[74,16,3],[496,243,232],[347,107,49],[157,32,10],[76,29,4]];
 const sum=a=>a.reduce((x,y)=>x+y,0), mean=a=>sum(a)/a.length;
 const check=(x,s)=>{if(!x)throw Error(s);};
 function pearson(a,b){const x=mean(a),y=mean(b);const u=a.map(v=>v-x),v=b.map(v=>v-y);return sum(u.map((z,i)=>z*v[i]))/Math.sqrt(sum(u.map(z=>z*z))*sum(v.map(z=>z*z)));}
 function ranks(a){let ix=a.map((_,i)=>i).sort((i,j)=>a[i]-a[j]),r=Array(a.length);for(let i=0;i<ix.length;){let j=i+1;while(j<ix.length&&a[ix[j]]===a[ix[i]])j++;for(let k=i;k<j;k++)r[ix[k]]=(i+j+1)/2;i=j;}return r;}
 function kendall(a,b){let c=0,d=0,ta=0,tb=0;for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){let x=Math.sign(a[i]-a[j]),y=Math.sign(b[i]-b[j]);if(!x&&!y)continue;if(!x)ta++;else if(!y)tb++;else if(x===y)c++;else d++;}return (c-d)/Math.sqrt((c+d+ta)*(c+d+tb));}
 function top(a,b,k){function ix(x){const o=x.map((_,i)=>i).sort((i,j)=>x[j]-x[i]);if(o.length<=k||x[o[k-1]]===x[o[k]])return null;return o.slice(0,k);}const u=ix(a),v=ix(b);if(u===null||v===null)return {status:"boundary_tie"};let n=u.filter(x=>v.includes(x)).length;return {status:"defined",intersection:n,jaccard:n/(2*k-n)};}
 check(JSON.stringify(ranks([1,2,2,4]))==="[1,2.5,2.5,4]","ties");
 check(Math.abs(pearson([1,2,3],[3,2,1])+1)<1e-12,"reverse");
 check(Math.abs(kendall([1,2,2],[1,2,2])-1)<1e-12,"kendall ties");
 check(Math.abs(kendall([1,2,2],[3,2,1])+2/Math.sqrt(6))<1e-12,"kendall partial tie");
 check(top([4,3,2,1],[4,3,2,1],2).intersection===2&&top([4,3,2,1],[1,2,3,4],2).intersection===0,"top sets");
 check(top([4,3,3,1],[1,2,3,4],2).status==="boundary_tie","cutoff tie");
 check(t.length===20&&sum(t.map(r=>r[0]))===2535&&sum(t.map(r=>r[1]))===784&&sum(t.map(r=>r[2]))===383,"source totals");
 function calc(rows){const a=rows.map(r=>r[0]),b=rows.map(r=>r[1]);return {raw_pearson:pearson(a,b),log1p_pearson:pearson(a.map(Math.log1p),b.map(Math.log1p)),spearman:pearson(ranks(a),ranks(b)),kendall_tau_b:kendall(a,b),top5:top(a,b,5)};}
 const full=calc(t);check(Math.abs(full.raw_pearson-.64)<=.01,"published Pearson replay");
 const omissions=t.map((_,i)=>calc(t.filter((_,j)=>i!==j))),summary={};
 for(const k of ["raw_pearson","log1p_pearson","spearman","kendall_tau_b"]){const a=omissions.map(x=>x[k]);summary[k]={min:Math.min(...a),max:Math.max(...a),positive_count:a.filter(x=>x>0).length};}
 const tops=omissions.map(x=>x.top5).filter(x=>x.status==="defined");
 summary.top5={defined_omissions:tops.length,intersection_range:[Math.min(...tops.map(x=>x.intersection)),Math.max(...tops.map(x=>x.intersection))],jaccard_range:[Math.min(...tops.map(x=>x.jaccard)),Math.max(...tops.map(x=>x.jaccard))]};
 return {status:"published_table_exploratory_only",doi:"10.1002/ece3.3196",nights:20,tests:"PASS",full,leave_one_night_omission:summary,claim_boundary:"Nightly recorded event counts; not effort-normalized, true activity, independent site validation, or causal detection."};
}
console.log(JSON.stringify(audit(),null,2));
