// Node >=18; run with the four exact source files (in order) in cwd. No network.
const fs=require('node:fs'); const crypto=require('node:crypto');
const spec=[["Matriz_sub-bosque.txt","a2c51fce68cac27f920f5cace74395521db1f6af"],["Matriz_sub-dossel.txt","9a3fe231f611914a88bb09eb6ecb6d97d294aac2"],["Matriz_dossel.txt","47676a5696d5d00b869b95aa8a4c0055297410d7"],["Matriz_tres_estratos.txt","bba476c853eca0602b6321055ec3ce53e2aed60b"]];
const files=spec.map(([path,sha])=>{let b=fs.readFileSync(path);let got=crypto.createHash('sha1').update(Buffer.from('blob '+b.length+'\0')).update(b).digest('hex');if(got!==sha)throw Error('blob mismatch '+path);return {path,sha,c:b.toString('utf8')}});
function analyze(files){
  const must=(cond,msg)=>{if(!cond)throw Error(msg)};
  const sum=x=>x.reduce((s,v)=>s+v,0);
  const parse=d=>{let l=d.c.trimEnd().split(/\r?\n/).map(s=>s.split("\t").map(x=>x.trim()));let bats=l.shift().slice(1),plants=[],m=new Map();must(new Set(bats).size===bats.length,"bat labels");for(let r of l){must(r.length===bats.length+1&&!plants.includes(r[0])&&r.slice(1).every(x=>/^\d+$/.test(x)),"table schema");plants.push(r[0]);r.slice(1).forEach((n,i)=>{if(+n)m.set(bats[i]+"|"+r[0],+n)})}return {bats,plants,m,n:sum([...m.values()])}};
  let d=files.map(parse),bat=[...new Set(d.slice(0,3).flatMap(x=>x.bats))].sort(),plant=[...new Set(d.slice(0,3).flatMap(x=>x.plants))].sort(),B=bat.length,P=plant.length;
  must(B===9&&P===37&&d.map(v=>v.n).join()==="154,109,61,324"&&d.map(v=>v.m.size).join()==="58,46,31,89","published totals");
  let all=new Map();for(let t of d.slice(0,3))for(let [k,n] of t.m)all.set(k,(all.get(k)||0)+n);
  must(all.size===d[3].m.size&&[...all].every(([k,n])=>d[3].m.get(k)===n),"three-way exact merge");
  let x=Array.from({length:3},(_,h)=>Array.from({length:B},(_,b)=>Array.from({length:P},(_,p)=>d[h].m.get(bat[b]+"|"+plant[p])||0)));
  function info(t,equal=false,detail=false){
    const H=t.length,K=t[0].length,J=t[0][0].length;
    let htot=t.map(h=>sum(h.map(sum))),wt=htot.map(n=>equal?1/n:1);
    let HB=Array.from({length:H},()=>new Float64Array(K)), HP=Array.from({length:H},()=>new Float64Array(J)),BP=Array.from({length:K},()=>new Float64Array(J)),bt=new Float64Array(K),pt=new Float64Array(J),ht=new Float64Array(H);
    let N=0;for(let h=0;h<H;h++)for(let b=0;b<K;b++)for(let p=0;p<J;p++){let a=t[h][b][p]*wt[h];if(a){HB[h][b]+=a;HP[h][p]+=a;BP[b][p]+=a;bt[b]+=a;pt[p]+=a;ht[h]+=a;N+=a}}
    let iB=0,iP=0,iBP=0,cP=0,cB=0,contri=new Float64Array(K);
    for(let h=0;h<H;h++){for(let b=0;b<K;b++){let a=HB[h][b];if(a)iB+=a*Math.log(a*N/(ht[h]*bt[b]));for(let p=0;p<J;p++){let a=t[h][b][p]*wt[h];if(a){iBP+=a*Math.log(a*N/(ht[h]*BP[b][p]));let k=a*Math.log(a*bt[b]/(HB[h][b]*BP[b][p]));cP+=k;contri[b]+=k;cB+=a*Math.log(a*pt[p]/(HP[h][p]*BP[b][p]))}}}
    for(let p=0;p<J;p++){let a=HP[h][p];if(a)iP+=a*Math.log(a*N/(ht[h]*pt[p]))}}
    must(Math.abs(iBP-iB-cP)<1e-8&&Math.abs(iBP-iP-cB)<1e-8,"chain identity");
    return {joint:iBP/N,bat:iB/N,plant:iP/N,plant_given_bat:cP/N,bat_given_plant:cB/N,conditional_fraction:iBP>0?cP/iBP:null, ...(detail?{bat_mass:[...bt],bat_contrib:[...contri],total_weight:N}: {})};
  }
  function rng(seed){return ()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296}}
  function summary(a,obs){let s=a.slice().sort((a,b)=>a-b);let q=p=>{let u=p*(s.length-1),j=Math.floor(u);return s[j]+(s[Math.min(j+1,s.length-1)]-s[j])*(u-j)};let mean=sum(a)/a.length;return {observed:obs,mean,excess:obs-mean,p025:q(.025),p975:q(.975),rank_le:a.filter(v=>v<=obs+1e-12).length/a.length,n:a.length}}
  function caseRun(name,hs,bs,leave=false){let t=hs.map(h=>bs.map(b=>x[h][b].slice())),H=hs.length,K=bs.length;let obs=info(t,false,true),eq=info(t,true),rand=rng(20261127),tokens=[],slots=[];
    for(let b=0;b<K;b++){let a=[],ns=[];for(let h=0;h<H;h++){ns.push(sum(t[h][b]));for(let p=0;p<P;p++)for(let j=0;j<t[h][b][p];j++)a.push(p)}tokens.push(a);slots.push(ns)}
    let nulls=[],nullE=[],nullLeave=bs.map(()=>[]);
    for(let rep=0;rep<10000;rep++){let z=Array.from({length:H},()=>Array.from({length:K},()=>new Uint32Array(P)));for(let b=0;b<K;b++){let a=tokens[b].slice();for(let j=a.length-1;j>0;j--){let k=Math.floor(rand()*(j+1));[a[k],a[j]]=[a[j],a[k]]}let k=0;for(let h=0;h<H;h++)for(let j=0;j<slots[b][h];j++)z[h][b][a[k++]]++;must(k===a.length,"tokens")}
      if(rep===0||rep===9999){for(let b=0;b<K;b++){for(let h=0;h<H;h++)must(sum([...z[h][b]])===slots[b][h],"bat-layer margins");for(let p=0;p<P;p++)must(sum(z.map(h=>h[b][p]))===sum(t.map(h=>h[b][p])),"bat-plant margins")}}
      let s=info(z,false,leave),e=info(z,true);nulls.push(s.plant_given_bat);nullE.push(e.plant_given_bat);
      if(leave)for(let b=0;b<K;b++)nullLeave[b].push((s.plant_given_bat*s.total_weight-s.bat_contrib[b])/(s.total_weight-s.bat_mass[b]));
    }
    let clean=({bat_mass,bat_contrib,total_weight,...rest})=>rest;
    return {name,layer_counts:t.map(h=>sum(h.map(sum))),n_bats:K,n_plants:plant.filter((_,p)=>t.some(h=>h.some(b=>b[p]>0))).length,observed:clean(obs),equal_layer:clean(eq),null:summary(nulls,obs.plant_given_bat),null_equal_layer:summary(nullE,eq.plant_given_bat),...(leave?{leave_one_bat:bs.map((b,j)=>({bat:bat[b],n_events:obs.bat_mass[j],...summary(nullLeave[j],(obs.plant_given_bat*obs.total_weight-obs.bat_contrib[j])/(obs.total_weight-obs.bat_mass[j]))}))}:{})}
  }
  const bs=bat.map((_,i)=>i),shared=bs.filter(b=>x.every(h=>sum(h[b])>0));
  const results=[caseRun("all_layers",[0,1,2],bs,true),caseRun("common_bats",[0,1,2],shared),caseRun("understory_subcanopy",[0,1],bs.filter(b=>[0,1].some(h=>sum(x[h][b])>0))),caseRun("understory_canopy",[0,2],bs.filter(b=>[0,2].some(h=>sum(x[h][b])>0))),caseRun("subcanopy_canopy",[1,2],bs)];
  return {status:"complete_descriptive_only",seed:20261127,n_null:10000,files:files.map(({path,sha})=>({path,sha})),source_counts:{bats:B,plants:P,links:all.size,events:324,common_bats:shared.length,exact_merged:true},results};
}
console.log(JSON.stringify(analyze(files),null,2));
