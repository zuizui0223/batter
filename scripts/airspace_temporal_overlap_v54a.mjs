// V54A hypothetical reference, not empirical false-match estimation.
function reference(){
 const t=[[19,24,12],[24,43,13],[324,20,13],[291,7,4],[79,3,2],[36,19,3],[229,47,21],[330,27,9],[2,56,0],[7,24,1],[7,13,1],[3,17,1],[3,22,0],[1,20,0],[30,15,5],[74,16,3],[496,243,232],[347,107,49],[157,32,10],[76,29,4]];
 const sum=a=>a.reduce((s,x)=>s+x,0);
 const a=sum(t.map(x=>x[0])),v=sum(t.map(x=>x[1])),m=sum(t.map(x=>x[2]));
 if(t.length!==20||a!==2535||v!==784||m!==383)throw Error("published totals");
 const scenarios=[10,12,14].map(h=>{
   const f=60/(3600*h);
   const p=t.map(([n])=>1-Math.pow(1-f,n));
   const multi=t.map(([n],i)=>p[i]-n*f*Math.pow(1-f,n-1));
   const wmean=x=>sum(x.map((p,i)=>p*t[i][1]))/v;
   return {hypothetical_session_hours:h,window_plus_minus_seconds:30,equal_night_mean_chance_overlap:sum(p)/t.length,visual_weighted_chance_overlap:wmean(p),expected_visual_records_with_at_least_one_candidate:v*wmean(p),equal_night_multiple_candidate_probability:sum(multi)/t.length,visual_weighted_multiple_candidate_probability:wmean(multi),chance_overlap_night_range:[Math.min(...p),Math.max(...p)]};
 });
 return {status:"hypothetical_reference_only",source:"Gorresen et al. 2017, published Table 1, doi:10.1002/ece3.3196",source_totals:{nights:20,acoustic:a,visual:v,matched:m},reported_match_rate:{equal_night:sum(t.map(x=>x[2]/x[1]))/t.length,visual_weighted:m/v},scenarios,assumptions:"Fixed acoustic counts independently uniform on circular sessions, independent visual times, assumed durations; NOT estimated false-positive rates; no subtraction from observed matches",tests:"published totals verified"};
}
console.log(JSON.stringify(reference(),null,2));
