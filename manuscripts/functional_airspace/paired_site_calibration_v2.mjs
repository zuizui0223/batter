// Synthetic only; fixed design in PAIRED_SITE_CALIBRATION_CONTRACT_V2.md
function simulate(){
 const N=1000,L=7,T=30,G=2,K=8,seed0=2026112502;let seed=seed0>>>0;
 const rng=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return (seed+.5)/4294967296};
 const normal=()=>Math.sqrt(-2*Math.log(rng()))*Math.cos(2*Math.PI*rng());
 let lf=[0];for(let i=1;i<=40;i++)lf[i]=lf[i-1]+Math.log(i);
 const choose=(n,k)=>lf[n]-lf[k]-lf[n-k],base=Array.from({length:9},(_,k)=>choose(20,k)+choose(20,8-k));
 function moments(b){let m=-Infinity;for(let k=0;k<=8;k++)m=Math.max(m,base[k]+b*k);let z=0,e=0;for(let k=0;k<=8;k++){let w=Math.exp(base[k]+b*k-m);z+=w;e+=k*w;}return {logZ:m+Math.log(z),mean:e/z}}
 const nullZ=moments(0).logZ;
 function pmf(b){let z=moments(b).logZ;return base.map((x,k)=>Math.exp(x+b*k-z))}
 function draws(b){let p=pmf(b),c=p.map((_,i)=>p.slice(0,i+1).reduce((s,x)=>s+x,0));let a=0;for(let i=0;i<T;i++){let u=rng(),k=0;while(k<8&&u>c[k])k++;a+=k}return a}
 const memo=new Map();
 function fit(sum,n,weight){let key=[sum,n,weight].join(",");if(memo.has(key))return memo.get(key);let grad=b=>weight*(moments(b).mean-sum/n)+.2*b,lo=-6,hi=6;if(grad(lo)>=0)hi=lo;else if(grad(hi)<=0)lo=hi;else for(let i=0;i<36;i++){let m=(lo+hi)/2;if(grad(m)>0)hi=m;else lo=m;}let b=(hi+lo)/2;let r={b,z:moments(b).logZ-nullZ};memo.set(key,r);return r}
 const gain=(fit,k)=>fit.b*k-fit.z;
 function evaluate(rows){let totals=[0,0];rows.forEach(r=>r.forEach((x,g)=>totals[g]+=x));let f=rows.map(r=>{let a=totals.map((x,g)=>x-r[g]);let common=fit(a[0]+a[1],(L-1)*T*G,1),distinct=a.map(x=>fit(x,(L-1)*T,.5));let m1=gain(common,(r[0]+r[1])/(T*G)),m2=(gain(distinct[0],r[0]/T)+gain(distinct[1],r[1]/T))/2;return [m1,m2-m1,m2]});let avg=[0,1,2].map(j=>f.reduce((s,x)=>s+x[j],0)/L);let count=f.filter(x=>x[2]>0).length;let min=Math.min(...f.map(x=>(avg[2]*L-x[2])/(L-1)));return {avg,pass:avg[2]>0&&min>0&&count>=5}}
 function summarize(arr){arr.sort((a,b)=>a-b);const quant=q=>{let x=q*(arr.length-1),i=Math.floor(x);return arr[i]+(arr[Math.min(i+1,arr.length-1)]-arr[i])*(x-i)};return {mean:arr.reduce((a,b)=>a+b,0)/arr.length,q05:quant(.05),median:quant(.5),q95:quant(.95)}}
 const worlds={sharp_null:(l,g)=>0,mean_zero_heterogeneous:(l,g)=>.9*normal(),common_effect:(l,g)=>.9,opposite_guild:(l,g)=>g===0?.9:-.9,opposite_plus_heterogeneity:(l,g)=>(g===0?.9:-.9)+.9*normal()};
 const nrm=pmf(.7).reduce((a,b)=>a+b,0),swap=Math.max(...pmf(.7).map((x,k)=>Math.abs(x-pmf(-.7)[8-k]))),nullMean=moments(0).mean;
 const artificial=[1,2,5,8], b=.4, a=artificial.reduce((s,k)=>s+b*k-moments(b).logZ,0)/artificial.length, bgroup=b*artificial.reduce((s,k)=>s+k,0)/artificial.length-moments(b).logZ;
 if(Math.abs(nrm-1)>1e-12||swap>1e-12||Math.abs(nullMean-4)>1e-12||Math.abs(a-bgroup)>1e-12)throw Error("invariants failed");
 let out={scope:"Synthetic fixed-count diagnostic; not field power or real effect",seed:seed0,reps:N,localities:L,nights:T,passes_per_side:20,feeding_total:8,invariants:{normalization:nrm,swap_max_error:swap,null_mean:nullMean,grouped_loglik_error:Math.abs(a-bgroup)},worlds:{}};
 for(let [name,fn] of Object.entries(worlds)){let scores=[[],[],[]],pass=0;for(let i=0;i<N;i++){let rows=Array.from({length:L},(_,l)=>Array.from({length:G},(_,g)=>draws(fn(l,g))));let z=evaluate(rows);z.avg.forEach((x,j)=>scores[j].push(x));pass+=z.pass?1:0;}let p=pass/N;out.worlds[name]={m1_m0:summarize(scores[0]),m2_m1:summarize(scores[1]),m2_m0:summarize(scores[2]),gate_count:pass,gate_fraction:p,mcse:Math.sqrt(p*(1-p)/N)};}
 return out;
}
console.log(JSON.stringify(simulate(),null,2));
