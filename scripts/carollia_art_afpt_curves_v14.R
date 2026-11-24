# Conditional power curves; source and per-record curves stay in temporary runner.
library(afpt)
stopifnot(as.character(packageVersion("afpt"))=="1.1.0.4")
args<-commandArgs(trailingOnly=TRUE)
d<-read.table(args[1],header=TRUE,stringsAsFactors=FALSE,check.names=FALSE)
k<-!duplicated(tolower(d$ID))&!duplicated(tolower(d$ID),fromLast=TRUE)
d<-d[k,]
stopifnot(nrow(d)==489,sum(d$ART=="T")==49,sum(d$ART=="NT")==156,sum(d$ART=="F")==284)
u<-seq(5,7,by=.1)
flags<-c("flags.redFreqLo","flags.redFreqHi","flags.thrustHi","flags.speedLo")
p<-matrix(NA_real_,nrow(d),length(u));valid<-matrix(FALSE,nrow(d),length(u))
errors<-0
for(i in seq_len(nrow(d))){
  tryCatch({
    b<-Bird(massTotal=d$BMass[i]/1000,wingSpan=d$WSpan[i]/1000,wingArea=d$WArea[i]/1e6,
      wingbeatFrequency=9,coef.bodyDragCoefficient=.4,type="bat")
    z<-computeFlappingPower(b,u)
    stopifnot(all(c("power","speed",flags)%in%names(z)),max(abs(z$speed-u))<1e-9)
    p[i,]<-z$power
    valid[i,]<-is.finite(z$power)&z$power>0&rowSums(is.na(z[,flags,drop=FALSE]))==0&
      rowSums(z[,flags,drop=FALSE],na.rm=TRUE)==0
  },error=function(e){errors<<-errors+1})
}
common<-apply(valid,2,all)
cat("AFPT records",nrow(d),"errors",errors,"common speeds",sum(common),"/",length(u),"\n")
write.csv(data.frame(speed=u,n_valid=colSums(valid),common=common),file.path(args[2],"afpt_support.csv"),row.names=FALSE)
write.csv(p,file.path(args[2],"afpt_curves.csv"),row.names=FALSE)
