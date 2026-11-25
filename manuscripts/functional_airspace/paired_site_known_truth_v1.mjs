// Synthetic known-truth verification; no empirical records.
function run(){
 const logf=[0];for(let i=1;i<=500;i++)logf[i]=logf[i-1]+Math.log(i);
 const lc=(n,k)=>logf[n]-logf[k]-logf[n-k];
 function prepare(nN,nP,f,k,loc,g){
  const lo=Math.max(0,f-nP),hi=Math.min(f,nN),terms=[];
  if(![nN,nP,f,k].every(Number.isInteger)||nN<1||nP<1||f<=0||f>=nN+nP||k<lo||k>hi||nN+nP>500)throw Error("invalid or uninformative stratum");
  for(let x=lo;x<=hi;x++)terms.push([x,lc(nN,x)+lc(nP,f-x)]);
  return {nN,nP,f,k,loc,g,terms,base:lc(nN,k)+lc(nP,f-k)};
 }
 function stats(r,b){
  let m=-Infinity;for(let [k,c] of r.terms)m=Math.max(m,c+b*k);
  let z=0,e=0;for(let [k,c] of r.terms){const v=Math.exp(c+b*k-m);z+=v;e+=k*v;}
  return {lp:r.base+b*r.k-m-Math.log(z),mean:e/z};
 }
 function fit(rows,g=null){
  const counts={};for(let r of rows)counts[r.loc]=(counts[r.loc]||0)+1;
  const L=Object.keys(counts).length;if(!L)throw Error("no training groups");
  const grad=b=>{let v=.2*b;for(let r of rows)if(g===null||r.g===g)v+=(stats(r,b).mean-r.k)/(L*counts[r.loc]);return v;};
  if(grad(-6)>=0)return -6;if(grad(6)<=0)return 6;
  let lo=-6,hi=6;for(let i=0;i<36;i++){let m=(lo+hi)/2;if(grad(m)>0)hi=m;else lo=m;}return (lo+hi)/2;
 }
 function evaluate(rows){
  const locs=[...new Set(rows.map(r=>r.loc))];const per=locs.map(loc=>{
   const tr=rows.filter(r=>r.loc!==loc),te=rows.filter(r=>r.loc===loc);
   const b1=fit(tr),b2={SRE:fit(tr,"SRE"),LRE:fit(tr,"LRE")};
   let s=[0,0,0];for(const r of te){s[0]+=stats(r,0).lp;s[1]+=stats(r,b1).lp;s[2]+=stats(r,b2[r.g]).lp;}s=s.map(x=>x/te.length);
   return {loc,b1,b2,m1_m0:s[1]-s[0],m2_m1:s[2]-s[1],m2_m0:s[2]-s[0]};
  });
  const mean=(a,k)=>a.reduce((s,x)=>s+x[k],0)/a.length;
  const omission=per.map((_,i)=>mean(per.filter((_,j)=>j!==i),"m2_m0"));
  const pos=per.filter(r=>r.m2_m0>0).length;
  return {n_localities:locs.length,n_strata:rows.length,m1_m0:mean(per,"m1_m0"),m2_m1:mean(per,"m2_m1"),m2_m0:mean(per,"m2_m0"),positive_localities:pos,omission_min:Math.min(...omission),gate:mean(per,"m2_m0")>0&&Math.min(...omission)>0&&pos>=5,folds:per};
 }
 let seed=20261125;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
 function draw(nN,nP,f,b){
  const t=prepare(nN,nP,f,Math.max(0,f-nP),0,"SRE").terms;
  const m=Math.max(...t.map(([k,c])=>c+b*k)),w=t.map(([k,c])=>Math.exp(c+b*k-m));
  let u=rand()*w.reduce((a,b)=>a+b,0);
  for(let i=0;i<w.length;i++){u-=w[i];if(u<=0)return t[i][0];}return t.at(-1)[0];
 }
 const test=prepare(17,23,10,4,0,"SRE");let norm=0;
 for(const [k] of test.terms)norm+=Math.exp(stats({...test,k,base:lc(17,k)+lc(23,10-k)},.7).lp);
 const swapped=prepare(23,17,10,6,0,"SRE");
 if(Math.abs(norm-1)>1e-12||Math.abs(stats(test,.7).lp-stats(swapped,-.7).lp)>1e-12||Math.abs(stats(test,0).mean-10*17/40)>1e-12)throw Error("conditional distribution invariant failed");
 const worlds={null:()=>0,common:()=>1.1,guild_contrast:(_l,g)=>g==="SRE"?1.2:-1.0,locality_heterogeneity:(l,g)=>(l%2===0?1:-1)*(g==="SRE"?1.2:1.0)};
 const out={scope:"Synthetic software check only; no real bats; one fixed pseudo-dataset per world, not power or empirical results",seed:20261125,invariants:{normalization:norm,swap_symmetry:true,null_expectation:true},worlds:{}};
 for(const [name,fn] of Object.entries(worlds)){let rows=[];for(let l=0;l<7;l++)for(let t=0;t<30;t++)for(const g of ["SRE","LRE"]){let nN=10+Math.floor(rand()*25),nP=10+Math.floor(rand()*25),f=3+Math.floor(rand()*8);let k=draw(nN,nP,f,fn(l,g));rows.push(prepare(nN,nP,f,k,l,g));}out.worlds[name]=evaluate(rows);}
 return out;
}
console.log(JSON.stringify(run(),null,2));
