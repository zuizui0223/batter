# Species-level published S2 morphology; no HR input.
library(afpt)
stopifnot(as.character(packageVersion("afpt"))=="1.1.0.4")
b <- Bird(massTotal=.093,wingSpan=.56,wingArea=.0417,
          wingbeatFrequency=9.6,coef.bodyDragCoefficient=.4,type="bat")
u <- seq(3,15,by=.05)
z <- computeFlappingPower(b,u)
flags <- c("flags.redFreqLo","flags.redFreqHi","flags.thrustHi","flags.speedLo")
stopifnot(all(c("speed","power",flags)%in%names(z)),nrow(z)==length(u),max(abs(z$speed-u))<1e-9)
valid <- is.finite(z$power)&z$power>0&rowSums(is.na(z[,flags,drop=FALSE]))==0&rowSums(z[,flags,drop=FALSE],na.rm=TRUE)==0
dir.create("external",showWarnings=FALSE)
write.csv(data.frame(speed=u,power=z$power,valid=valid,z[,flags,drop=FALSE]),"external/bayer_afpt_curve_v23.csv",row.names=FALSE)
cat("Valid speed nodes",sum(valid),"/",length(u),"\n")
if(any(valid))cat("Valid node endpoints",range(u[valid]),"\n")
print(Bird(massTotal=.093,wingSpan=.56,wingArea=.0417,wingbeatFrequency=9.6,coef.bodyDragCoefficient=.4,type="bat"))
