// V45 source-free exact-moment diagnostic. Run: node scripts/airspace_error_identifiability_v45.mjs
// Inputs are published aggregate V44 job logs, not raw trajectories.
const panels = [
  {
    "lag_s": 0.1,
    "n_sites": 8,
    "n_paths": 397,
    "n_windows": 2095,
    "mse_common": 0.08864051786184156,
    "mse_axis": 0.08793116749878409,
    "h_median": 0.9580216861845143,
    "v_median": 0.8927005027628088,
    "min_fold_gap": 0.05992504552443689,
    "max_h": 0.9658887585033533
  },
  {
    "lag_s": 0.2,
    "n_sites": 8,
    "n_paths": 364,
    "n_windows": 938,
    "mse_common": 0.16914047354545272,
    "mse_axis": 0.15985213899099676,
    "h_median": 0.9668591479648557,
    "v_median": 0.7567677766010268,
    "min_fold_gap": 0.1882692182070389,
    "max_h": 0.9755176627542135
  }
];
function audit(panels) {
 const check=(b,m)=>{if(!b)throw Error(m)};
 const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
 const slope=(u,v)=>mean(u.map((x,i)=>x*v[i]))/mean(u.map(x=>x*x));
 // Fixed finite factorial ensemble: independent mean-zero unit-variance signs.
 // This reproduces first/second moments exactly, not the full distribution.
 function witness(rho,q) {
  check(q>=0&&q<.5&&Math.abs(rho)<=1,"invalid covariance parameters");
  const u=[],v=[],U=[],V=[];
  for(let j=0;j<32;j++){
   const [a,b,c,d,e]=Array.from({length:5},(_,k)=>(j&(1<<k))?1:-1);
   const latentU=Math.sqrt(1-2*q)*a;
   const latentV=Math.sqrt(1-2*q)*(rho*a+Math.sqrt(1-rho*rho)*b);
   u.push(latentU);v.push(latentV);
   U.push(latentU+Math.sqrt(q)*(d-c));V.push(latentV+Math.sqrt(q)*(e-d));
  }
  return {latent_slope:slope(u,v),observed_slope:slope(U,V),
   observed_prior_second_moment:mean(U.map(x=>x*x)),observed_next_second_moment:mean(V.map(x=>x*x))};
 }
 return panels.map(p=>{
  const h=p.h_median,v=p.v_median;
  // rho*=h, no horizontal measurement error, vertical noise alone accounts for the observed gap.
  const q=(h-v)/(1+2*h);
  // This is a sufficient bound across all folds from reported ranges, not an estimate of actual error.
  const qLower=p.min_fold_gap/(1+2*p.max_h);
  const W_h=witness(h,0),W_v=witness(h,q);
  check(Math.abs(W_h.observed_slope-h)<1e-12,"horizontal witness");
  check(Math.abs(W_v.observed_slope-v)<1e-12,"vertical witness");
  check(Math.abs(W_v.latent_slope-h)<1e-12,"common true persistence");
  check(Math.abs(W_v.observed_prior_second_moment-1)<1e-12,"normalization");
  check(Math.abs(W_v.observed_next_second_moment-1)<1e-12,"stationary second moment");
  // Under the illustrative homogeneous population, separate slopes yield exactly this excess MSE.
  const excess=2*(h-v)**2/9;
  return {...p,observed_mse_relative_gain_pct:100*(p.mse_common-p.mse_axis)/p.mse_common,
   example_common_latent_rho:h,vertical_error_variance_fraction_of_observed_prior_increment_m2:q,
   vertical_position_error_sd_over_observed_prior_increment_rms:Math.sqrt(q),
   sufficient_all_fold_error_variance_fraction_bound:qLower,
   sufficient_all_fold_error_sd_ratio_bound:Math.sqrt(qLower),
   illustrative_population_excess_mse_common_vs_axis:excess,
   exact_synthetic_moment_witness:{horizontal:W_h,vertical:W_v}};
 });
}
const report = {status:"aggregate_identifiability_audit_only",source_run:45524948853,source_job:138905862482,source_commit:"d74264265e0bb979128fd725300af6d90d902cea",synthetic_exact_moment_checks:"pass",new_empirical_fits:false,claim_boundary:"Median coefficients are illustrative, not a paired fold. Each scale is a separate counterexample. No calibrated error, no cross-lag compatibility claim.",results:audit(panels)};
console.log(JSON.stringify(report,null,2));
