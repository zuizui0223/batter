# V6: published fit replication, not new empirical evidence
library(afpt)
stopifnot(as.character(packageVersion("afpt"))=="1.1.0.4")
traits <- read.csv("results/afpt_traits_v6.csv", check.names=FALSE)
stopifnot(nrow(traits)==8, !anyDuplicated(traits$species))
u <- seq(5,9,by=.05)
flags <- c("flags.redFreqLo","flags.redFreqHi","flags.thrustHi","flags.speedLo")
focal <- traits[traits$species=="Pipistrellus nathusii",]
stopifnot(nrow(focal)==1, focal$mass==.0088, focal$frequency==9.9,
          focal$span==.23, focal$area==.0077, focal$cdb==.4)
calc <- function(t, scenario="default", mass=t$mass) {
  b <- Bird(massTotal=mass,wingSpan=t$span,wingArea=t$area,
            wingbeatFrequency=t$frequency,coef.bodyDragCoefficient=t$cdb,type="bat")
  if(scenario=="opt_stroke") z <- computeFlappingPower(b,u,strokeplane="opt") else
    z <- computeFlappingPower(b,u)
  stopifnot(all(c("speed","power",flags)%in%names(z)),nrow(z)==length(u),
            max(abs(z$speed-u))<1e-9)
  valid <- is.finite(z$power)&z$power>0&rowSums(is.na(z[,flags,drop=FALSE]))==0&
           rowSums(z[,flags,drop=FALSE],na.rm=TRUE)==0
  data.frame(species=t$species,scenario=scenario,mass=mass,speed=u,
    power=z$power,valid=valid,z[,flags,drop=FALSE],
    strokeplane=z$strokeplane,frequency=z$frequency)
}
# Strict common support; compare only valid speeds of each AFPT scenario.
ref <- 9.21e-5*u^3+.176/u+.0297
proxy <- 2*1.2*(focal$mass*9.81)^2/(1.2*pi*focal$span^2)/u+
          .5*1.2*focal$area*.08*u^3
metric <- function(p, ref) {
  if(!length(p)) return(c(MAE=NA,RMSE=NA,bias=NA))
  c(MAE=mean(abs(p-ref)),RMSE=sqrt(mean((p-ref)^2)),bias=mean(p-ref))
}
geom <- function(v,p,w) {
  if(length(v)<2)return(c(area=NA,boundary_fraction=NA,unsupported=NA))
  theta <- seq(0,2*pi,length.out=1441)
  calm <- min(p/v)
  boundary <- 0
  unavailable <- 0
  radius2 <- sapply(theta,function(a) {
    cross <- w*sin(a)
    g <- sqrt(pmax(0,v^2-cross^2))
    gi <- list(g+w*cos(a),g-w*cos(a))
    costs <- lapply(gi,function(s) ifelse(v>=abs(cross)&s>0,p/pmax(s,1e-300),Inf))
    if(any(!is.finite(sapply(costs,min)))) {
      unavailable <<- unavailable+1
      return(NA_real_)
    }
    boundary <<- boundary+sum(sapply(costs,function(q) which.min(q)%in%c(1,length(v))))
    (2*calm/sum(sapply(costs,min)))^2
  })
  if(anyNA(radius2))return(c(area=NA,boundary_fraction=NA,unsupported=unavailable/length(theta)))
  c(area=mean((head(radius2,-1)+tail(radius2,-1))/2),
    boundary_fraction=boundary/(2*length(theta)),unsupported=0)
}
summ <- function(z,p=z$power,mask=z$valid) {
  v <- u[mask]; y <- p[mask]
  if(length(v)<2)return(data.frame(n_valid=length(v),full_band=FALSE,min_speed=NA,range_speed=NA,
    optimum_boundary=NA,area_w2=NA,area_w4=NA,boundary_w4=NA,unsupported_w4=NA))
  i <- which.min(y); j <- which.min(y/v)
  ix <- which(mask); boundary <- function(k) k==1||k==length(ix)||ix[k+1]-ix[k]!=1||ix[k]-ix[k-1]!=1
  a <- geom(v,y,2); b <- geom(v,y,4)
  data.frame(n_valid=length(v),full_band=mean(mask)>=.8&&mask[1]&&tail(mask,1),
    min_speed=v[i],range_speed=v[j],optimum_boundary=boundary(i)||boundary(j),
    area_w2=unname(a["area"]),area_w4=unname(b["area"]),boundary_w4=unname(b["boundary_fraction"]),
    unsupported_w4=unname(b["unsupported"]))
}
zs <- list(calc(focal),calc(focal,"opt_stroke"),calc(focal,"capture_mass",.0076),
           calc(focal,"literal_methods_mass_diagnostic",.089))
rows <- list()
for(z in zs) {
  mask <- z$valid
  for(model in c("AFPT","V5_reduced","published_equation")) {
    p <- switch(model,AFPT=z$power,V5_reduced=proxy,published_equation=ref)
    mm <- metric(p[mask],ref[mask])
    rows[[length(rows)+1]] <- cbind(data.frame(scenario=z$scenario[1],model=model,
      MAE=unname(mm["MAE"]),RMSE=unname(mm["RMSE"]),bias=unname(mm["bias"])),summ(z,p,mask))
  }
}
result <- do.call(rbind,rows)
write.csv(result,"results/afpt_focal_metrics_v6.csv",row.names=FALSE)
write.csv(do.call(rbind,zs),"results/afpt_focal_curve_v6.csv",row.names=FALSE)
print(result,row.names=FALSE,digits=6)
print(colSums(zs[[1]][,flags,drop=FALSE],na.rm=TRUE))
# Eight taxa scenario only; output even if no interpretation allowed.
z8 <- lapply(seq_len(nrow(traits)),function(i)calc(traits[i,]))
r8 <- do.call(rbind,lapply(z8,function(z)cbind(data.frame(species=z$species[1]),summ(z))))
write.csv(do.call(rbind,z8),"results/afpt_eight_curves_v6.csv",row.names=FALSE)
write.csv(r8,"results/afpt_eight_metrics_v6.csv",row.names=FALSE)
print(r8,row.names=FALSE,digits=6)
default <- result[result$scenario=="default",]
cat("Focal fixed benchmark AFPT lower MAE:",with(default,MAE[model=="AFPT"]<MAE[model=="V5_reduced"]),"\n")
print(Bird(massTotal=focal$mass,wingSpan=focal$span,wingArea=focal$area,
 wingbeatFrequency=focal$frequency,coef.bodyDragCoefficient=focal$cdb,type="bat"))
cat("Package version",as.character(packageVersion("afpt")),"\n")
print(sessionInfo())
