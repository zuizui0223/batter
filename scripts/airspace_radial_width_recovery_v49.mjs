// V49 frozen source-free known-truth benchmark; node scripts/airspace_radial_width_recovery_v49.mjs
function benchmark(){
 const a=.33209534860027967,s=.0416532765335591,tau=.2,v=tau*tau;
 const muList=[4,6,8],sizes=[30,100,300],B=1000;
 function rng(seed){let x=seed>>>0;return ()=>{x=(x+0x6D2B79F5)>>>0;let t=x;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
 function normal(u){return Math.sqrt(-2*Math.log(Math.max(u(),1/4294967296)))*Math.cos(2*Math.PI*u());}
 function moments(y){let m=0,M2=0,n=0;for(const z of y){n++;let d=z-m;m+=d/n;M2+=d*(z-m);}return [m,M2/(n-1)];}
 function estimates(m,S,n){return {naive:S,constant:S-a*a,proportional:(S-s*s*(m*m-S/n))/(1+s*s)};}
 const close=(x,y)=>Math.abs(x-y)<1e-10;
 if(!close(moments([1,2,3])[0],2)||!close(moments([1,2,3])[1],1))throw Error("moment test");
 const q1=rng(20261125),q2=rng(20261125);for(let i=0;i<100;i++)if(q1()!==q2())throw Error("seed test");
 const population=[];
 for(const mu of muList)for(const generator of ["proportional","constant"]){
  const V=v+(generator==="proportional"?s*s*(v+mu*mu):a*a);
  const expected={naive:V,constant:V-a*a,proportional:(V-s*s*mu*mu)/(1+s*s)};
  if(!close(expected[generator],v))throw Error("population inversion");
  population.push({mu_m:mu,generator,true_variance_m2:v,observed_variance_m2:V,observed_sd_m:Math.sqrt(V),expected,bias:Object.fromEntries(Object.entries(expected).map(([k,x])=>[k,x-v]))});
 }
 const rand=rng(20261125),results=[];
 for(const mu of muList)for(const n of sizes){
  const acc={};
  for(const gen of ["proportional","constant"])acc[gen]={outside:0,negative:0,total:0,methods:Object.fromEntries(["naive","constant","proportional"].map(k=>[k,{err:0,se:0,negative:0}]))};
  for(let j=0;j<B;j++){
   const p=[],c=[];
   for(let i=0;i<n;i++){const r=mu+Math.sqrt(3)*tau*(2*rand()-1),z=normal(rand);p.push(r+s*r*z);c.push(r+a*z);}
   for(const [gen,y] of [["proportional",p],["constant",c]]){
    const g=acc[gen];for(const z of y){if(!Number.isFinite(z))throw Error("nonfinite");g.total++;if(z<0)g.negative++;if(z<2.997||z>10.217)g.outside++;}
    const [m,S]=moments(y);if(S<0||!Number.isFinite(S))throw Error("variance");
    for(const [k,x] of Object.entries(estimates(m,S,n))){const h=g.methods[k];h.err+=x-v;h.se+=(x-v)**2;h.negative+=+(x<0);}
   }
  }
  for(const [generator,g] of Object.entries(acc)){
   const methods={};for(const [k,h] of Object.entries(g.methods))methods[k]={bias_m2:h.err/B,rmse_m2:Math.sqrt(h.se/B),negative_fraction:h.negative/B};
   for(const k of ["constant","proportional"])methods[k].rmse_reduction_vs_naive=1-methods[k].rmse_m2/methods.naive.rmse_m2;
   results.push({mu_m:mu,n,generator,reps:B,observations_outside_calibration_support:g.outside,negative_observations:g.negative,total_observations:g.total,methods});
  }
 }
 return {status:"synthetic_known_truth_only",seed:20261125,replicates_per_cell:B,true_sd_m:tau,true_variance_m2:v,constant_scale_m:a,relative_scale:s,population,results,tests:"PASS"};
}
console.log(JSON.stringify(benchmark(),null,2));
