// V51 published aggregate descriptive arithmetic only.
function audit(){
 const cells=[[[153,114],[116,29],[15,7]],[[22,122],[45,78],[9,33]],[[5,0],[11,11],[7,7]]];
 const sum=a=>a.reduce((s,x)=>s+x,0);
 const map=(a,f)=>a.map((r,i)=>r.map((v,j)=>f(v,i,j)));
 const flatten=a=>a.flat();
 const row=a=>a.map(sum),col=a=>[0,1,2].map(j=>sum(a.map(r=>r[j])));
 const n=map(cells,v=>sum(v)),y=map(cells,v=>v[0]);
 const N=sum(flatten(n)),Y=sum(flatten(y));
 if(N!==784||Y!==383||N-Y!==401||JSON.stringify(row(n))!=="[434,309,41]"||JSON.stringify(col(n))!=="[416,290,78]")throw Error("published margins mismatch");
 const norm=a=>{const z=sum(flatten(a));return map(a,x=>x/z)};
 const P=norm(n),Q=norm(y);
 const H=a=>-sum(a.map(x=>x>0?x*Math.log(x):0));
 const js=(p,q)=>H(p.map((x,i)=>(x+q[i])/2))-(H(p)+H(q))/2;
 const tv=(p,q)=>sum(p.map((x,i)=>Math.abs(x-q[i])))/2;
 const describe=(p,q)=>({visual:p,acoustically_marked:q,representation_ratio:p.map((x,i)=>q[i]/x),percentage_point_change:p.map((x,i)=>100*(q[i]-x)),TV:tv(p,q),JS_nats:js(p,q),effective_categories_visual:Math.exp(H(p)),effective_categories_marked:Math.exp(H(q))});
 const pr=row(y).map((x,i)=>x/row(n)[i]),pc=col(y).map((x,i)=>x/col(n)[i]);
 const R=norm(map(n,(v,i,j)=>v*pr[i])),F=norm(map(n,(v,i,j)=>v*pc[j]));
 const rate=map(n,(v,i,j)=>y[i][j]/v);
 const standardized=(rows)=>[0,1,2].map(j=>sum(rows.map(i=>row(n)[i]*rate[i][j]))/sum(rows.map(i=>row(n)[i])));
 const out={status:"source_open_published_table_descriptive_only",doi:"10.1002/ece3.3196",published_table:2,N_visual:N,N_synchronous:Y,N_not_acoustically_marked:N-Y,
  detection_fraction_by_distance:pr,detection_fraction_by_flight_type:pc,cell_detection_fraction:rate,
  distance:describe(row(P),row(Q)),flight_type:describe(col(P),col(Q)),joint:describe(flatten(P),flatten(Q)),
  distance_only_reference:{flight_type_distribution:col(R),full_Q_minus_reference_flight_type_pp:col(Q).map((x,i)=>100*(x-col(R)[i])),JS_joint:js(flatten(Q),flatten(R))},
  flight_type_only_reference:{distance_distribution:row(F),full_Q_minus_reference_distance_pp:row(Q).map((x,i)=>100*(x-row(F)[i])),JS_joint:js(flatten(Q),flatten(F))},
  standardized_detection_all_distances:standardized([0,1,2]),standardized_detection_near_mid:standardized([0,1]),tests:"published marginals verified"};
 if(Math.abs(sum(flatten(P))-1)>1e-12||Math.abs(sum(flatten(Q))-1)>1e-12)throw Error("normalization");
 return out;
}
console.log(JSON.stringify(audit(),null,2));
