# GetShockLowData_1yr_span1.r

# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/shocks/low/span1/1yr")

source("./DataUtil.r")
source("./PlotUtil.r")

# G E T   D A T A  
rm(results)
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.shockall <- as.data.frame(fndfGetShockData(results))

# S U B S E T S 
dat.shock <- dat.shockall[dat.shockall$lifem<=100,]
dat.shock50 <- dat.shock[dat.shock$shockimpact==50,]
dat.shock90 <- dat.shock[dat.shock$shockimpact==90,]
dat.shock100 <- dat.shock[dat.shock$shockimpact==100,]

# Micah succeeded in bending dcast to his will, thanks; see email.
library(reshape2)
bar.small <- dat.shock90[,c("copies", "lifem", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("copies", "lifem"))
bar.recast <- dcast(bar.melted, copies~lifem)

# P L O T   D A T A 
library(ggplot2)
source("./ShockLowPlots.r")

gp <- fnPlotShock1(dat.shock90, 1, 1, 90)
fnPlotMakeFile(gp, "Shock_freq1span1impact90.png")

gp <- fnPlotShock1(dat.shock50, 1, 1, 50)
fnPlotMakeFile(gp, "Shock_freq1span1impact50.png")

gp <- fnPlotShock1(dat.shock100, 1, 1, 100)
fnPlotMakeFile(gp, "Shock_freq1span1impact100.png")


# not working yet
#fnPlotShock2(dat.shock90)







if(0){

source("./ShockTables.r")

# T A B U L A T E   D A T A  A S   T E X T 

# M O N T H L Y 
sOutputFilename <- "./Data_AuditRandom_Monthly.txt"
sTitle <- "Document losses with multiple copies and MONTHLY random auditing"
sSubtitle <- "Table of percentage loss of collection tabulated\n" %+% 
    "by number of copies and sector half-lifetime"
dat.tmp <- dat.auditrandom.monthly
tbl.tmp <- fnPrintTableRandom(dat.tmp, sOutputFilename, sTitle, sSubtitle
)

# IF THAT WORKS, DO SOME MORE.

# Re-form the data into a table for printing.  
foo<-(with(dat.auditrandom, 
       tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(results$copies))), foo)
tbl2<-data.frame(foo2)
colnames(tbl2)<-c("copies",as.numeric(colnames(foo2[,2:ncol(foo2)])))
# Pretty-print this to a file with explanatory headings.
sink(sOutputFilename)
cat("MIT Preservation Simulation Project", "\n\n")
cat(sOutputFilename, format(Sys.time(),"%Y%m%d_%H%M%S%Z"), "\n\n")
cat(sTitle, "\n\n")
cat(sSubtitle, "\n\n")
cat("\n")
print(tbl2)
sink()

}#endif0




# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
