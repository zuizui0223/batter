// V57 source-free partial identification. No empirical fitting.
function audit(){
 const check=(c,msg)=>{if(!c)throw Error(msg);};
 const near=(a,b)=>Math.abs(a-b)<1e-11;
 function bounds(q,G){check(Number.isFinite(q)&&q>=0&&q<=1&&Number.isFinite(G)&&G>=1,"invalid domain");return [q/(q+G*(1-q)),G*q/(G*q+1-q)];}
 function marked(f,d1,d0){return f*d1/(f*d1+(1-f)*d0);}
 function tvmax(G){return (Math.sqrt(G)-1)/(Math.sqrt(G)+1);}
 const rows=[];const p=.4;
 for(const q of [.5,.7,.9])for(const G of [1,1.5,2,4]){
  const [L,U]=bounds(q,G),oddsRatio=q/(1-q)/(p/(1-p));
  check(near(marked(L,1,1/G),q)&&near(marked(U,1/G,1),q),"sharp endpoints");
  check((L>p)===(oddsRatio>G)||near(L,p),"enrichment criterion");
  rows.push({reference_share:p,marked_share:q,Gamma:G,latent_share_lower:L,latent_share_upper:U,observed_odds_ratio:oddsRatio,strict_enrichment:L>p+1e-12,strict_depletion:U<p-1e-12,sharp_max_TV:tvmax(G)});
 }
 let gridChecks=0;
 for(const G of [1,1.5,2,4,10,100]){
  const z=Math.sqrt(G)/(1+Math.sqrt(G));
  check(near(z-bounds(z,G)[0],tvmax(G)),"sharp TV construction");
  for(let i=0;i<=1000;i++){
   const q=i/1000,[L,U]=bounds(q,G),[L2,U2]=bounds(q,2*G);
   check(L<=q+1e-12&&q<=U+1e-12,"containment");
   check(L2<=L+1e-12&&U2>=U-1e-12,"monotone");
   check(near(marked(L,1,1/G),q)&&near(marked(U,1/G,1),q),"endpoint recovery");
   check(Math.max(q-L,U-q)<=tvmax(G)+1e-12,"TV bound");
   check(bounds(q,1).every(v=>near(v,q)),"identity");
   gridChecks++;
  }
 }
 return {status:"exact_theory_only",tests:"PASS",grid_checks:gridChecks,assumptions:"Common support, correctly attributed events, no false positives or spatial mislocalization, bounded positive relative detection, population distribution; calibration not estimated.",illustrative_rows:rows};
}
console.log(JSON.stringify(audit(),null,2));
