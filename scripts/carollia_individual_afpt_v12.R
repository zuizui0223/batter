# Usage: Rscript scripts/carollia_individual_afpt_v12.R WingMorph.txt 9
library(afpt)
stopifnot(as.character(packageVersion("afpt"))=="1.1.0.4")
args <- commandArgs(trailingOnly=TRUE)
d <- read.delim(args[1],check.names=FALSE)
freq <- as.numeric(args[2])
stopifnot(freq %in% c(7,9,11),nrow(d)==116,!anyDuplicated(d$ID),
  all(is.finite(as.matrix(d[,c("M","B","S")]))),all(as.matrix(d[,c("M","B","S")])>0))
u <- seq(5,7,by=.1)
flags <- c("flags.redFreqLo","flags.redFreqHi","flags.thrustHi","flags.speedLo")
powers <- matrix(NA_real_,nrow(d),length(u)); valid <- matrix(FALSE,nrow(d),length(u))
for(i in seq_len(nrow(d))){
  b<-Bird(massTotal=d$M[i],wingSpan=d$B[i],wingArea=d$S[i],
       wingbeatFrequency=freq,coef.bodyDragCoefficient=.4,type="bat")
  z<-computeFlappingPower(b,u)
  stopifnot(all(c("power","speed",flags)%in%names(z)),max(abs(z$speed-u))<1e-9)
  powers[i,]<-z$power
  valid[i,]<-is.finite(z$power)&z$power>0&rowSums(is.na(z[,flags,drop=FALSE]))==0&
             rowSums(z[,flags,drop=FALSE],na.rm=TRUE)==0
}
keep<-apply(valid,2,all)
cat("frequency assumption",freq,"common speeds",sum(keep),"/",length(u),"individual valid min/max",range(rowSums(valid)),"\n")
dir.create("results",showWarnings=FALSE)
receipt<-data.frame(freq=freq,n_records=nrow(d),n_common=sum(keep),full_band=mean(keep)>=.8&&keep[1]&&tail(keep,1),
                    min_valid=min(rowSums(valid)),max_valid=max(rowSums(valid)))
write.csv(receipt,paste0("results/afpt_individual_support_",freq,"_v12.csv"),row.names=FALSE)
if(sum(keep)<2)quit(status=0)
v<-u[keep];p<-powers[,keep,drop=FALSE];theta<-seq(0,2*pi,length.out=181)[1:180]
rad<-function(w){
  rr<-matrix(NA_real_,nrow(p),length(theta)); bounds<-0
  for(j in seq_along(theta)){
    g<-sqrt(v^2-(w*sin(theta[j]))^2)
    gp<-g+w*cos(theta[j]);gm<-g-w*cos(theta[j])
    stopifnot(all(gp>0),all(gm>0))
    cp<-sweep(p,2,gp,"/");cm<-sweep(p,2,gm,"/")
    rr[,j]<-1/(apply(cp,1,min)+apply(cm,1,min))
    bounds<-bounds+sum(apply(cp,1,which.min)%in%c(1,length(v)))+sum(apply(cm,1,which.min)%in%c(1,length(v)))
  }
  list(r=rr,bound= bounds/(2*nrow(p)*length(theta)))
}
r0<-rad(0);r4<-rad(4)
gm<-exp(mean(log(d$M))); mass<-d$M/gm
casekeep<-!duplicated(tolower(d$ID))&!duplicated(tolower(d$ID),fromLast=TRUE)
cv<-function(x)sd(x)/mean(x)
medjac<-function(r){
  pairs<-combn(nrow(r),2)
  median(apply(pairs,2,function(x)sum(pmin(r[x[1],]^2,r[x[2],]^2))/sum(pmax(r[x[1],]^2,r[x[2],]^2))))
}
one<-function(alpha,idx,jaccard=FALSE){
  a<-sweep(r0$r[idx,,drop=FALSE],1,mass[idx]^alpha,"*")
  b<-sweep(r4$r[idx,,drop=FALSE],1,mass[idx]^alpha,"*")
  ca<-pi*rowMeans(a*a);wa<-pi*rowMeans(b*b)
  data.frame(alpha=alpha,n=sum(idx),cv0=cv(ca),cv4=cv(wa),delta=cv(wa)-cv(ca),
    j0=if(jaccard)medjac(a) else NA_real_,j4=if(jaccard)medjac(b) else NA_real_,
    retention_median=median(wa/ca),boundary0=r0$bound,boundary4=r4$bound)
}
alphas<-seq(0,1.5,by=.05)
out<-do.call(rbind,lapply(alphas,function(a)one(a,rep(TRUE,nrow(d)),any(abs(a-c(0,.75,1))<1e-8))))
sens<-do.call(rbind,lapply(c(0,.75,1),function(a)one(a,casekeep,TRUE)))
write.csv(out,paste0("results/afpt_individual_budget_",freq,"_v12.csv"),row.names=FALSE)
write.csv(sens,paste0("results/afpt_individual_id_sensitivity_",freq,"_v12.csv"),row.names=FALSE)
print(out[!is.na(out$j0),],row.names=FALSE)
cross<-which(head(out$delta,-1)*tail(out$delta,-1)<0)
cat("crossing intervals:",paste(paste(out$alpha[cross],out$alpha[cross+1],sep="-"),collapse=","),"\n")
print(receipt,row.names=FALSE)
