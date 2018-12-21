# GetShockLowData_2yr_span1.r
#                                       RBLandau 20171213
# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/shocks/low/span1/2yr")

# Trickier now because shocks have varying duration, too.  

source("./DataUtil.r")
source("./PlotUtil.r")

# G E T   D A T A  
if (exists("results")) {rm(results)}
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.shockallcopies <- as.data.frame(fndfGetShockData(results))
dat.shockall <- dat.shockallcopies[dat.shockallcopies$copies>=3
                & dat.shockallcopies$copies<=5,]

# S U B S E T S 

# First, half-year durations.
dat.shock <- dat.shockall[dat.shockall$lifem<=100 & dat.shockall$shockmaxlife==5000,]
dat.shock50 <- dat.shock[dat.shock$shockimpact==50,]
dat.shock90 <- dat.shock[dat.shock$shockimpact==90,]
dat.shock100 <- dat.shock[dat.shock$shockimpact==100,]

# P L O T   D A T A 
library(ggplot2)
source("./ShockLowPlots.r")
gp <- fnPlotShock1(dat.shock90, 2, 6, 1, 90)
fnPlotMakeFile(gp, "Shock_freq2dur5kspan1impact90.png")
gp <- fnPlotShock1(dat.shock50, 2, 6, 1, 50)
fnPlotMakeFile(gp, "Shock_freq2dur5kspan1impact50.png")
gp <- fnPlotShock1(dat.shock100, 2, 6, 1, 100)
fnPlotMakeFile(gp, "Shock_freq2dur5kspan1impact100.png")

# S U M M A R Y   T A B L E S 
source("ShockLowTables.r")
fnSaveSmallLossTable(dat.shock50, "ShockLow2yrdur5kspan1impact50.txt", 
    "Percent Permanent Losses, Shock Low 2yr dur5k span1 impact 50% "
    %+% "\n(percent loss by copies vs sector half-life in megahours)")
fnSaveSmallLossTable(dat.shock90, "ShockLow2yrdur5kspan1impact90.txt", 
    "Percent Permanent Losses, Shock Low 2yr dur5k span1 impact 90% "
    %+% "\n(percent loss by copies vs sector half-life in megahours)")
fnSaveSmallLossTable(dat.shock100, "ShockLow2yrdur5kspan1impact100.txt", 
    "Percent Permanent Losses, Shock Low 2yr dur5k span1 impact 100% "
    %+% "\n(percent loss by copies vs sector half-life in megahours)")

# Then, full year durations.
dat.shock <- dat.shockall[dat.shockall$lifem<=100 & dat.shockall$shockmaxlife==10000,]
dat.shock50 <- dat.shock[dat.shock$shockimpact==50,]
dat.shock90 <- dat.shock[dat.shock$shockimpact==90,]
dat.shock100 <- dat.shock[dat.shock$shockimpact==100,]

# P L O T   D A T A 
library(ggplot2)
#source("./ShockLowPlots.r")
gp <- fnPlotShock1(dat.shock90, 2, 12, 1, 90)
fnPlotMakeFile(gp, "Shock_freq2dur10kspan1impact90.png")
gp <- fnPlotShock1(dat.shock50, 2, 12, 1, 50)
fnPlotMakeFile(gp, "Shock_freq2dur10kspan1impact50.png")
gp <- fnPlotShock1(dat.shock100, 2, 12, 1, 100)
fnPlotMakeFile(gp, "Shock_freq2dur10kspan1impact100.png")

# S U M M A R Y   T A B L E S 
# Print small summary tables.
#source("ShockLowTables.r")
fnSaveSmallLossTable(dat.shock50, "ShockLow2yrdur10kspan1impact50.txt", 
    "Percent Permanent Losses, Shock Low 2yr dur10k span1 impact 50% "
    %+% "\n(percent loss by copies vs sector half-life in megahours)")
fnSaveSmallLossTable(dat.shock90, "ShockLow2yrdur10kspan1impact90.txt", 
    "Percent Permanent Losses, Shock Low 2yr dur10k span1 impact 90% "
    %+% "\n(percent loss by copies vs sector half-life in megahours)")
fnSaveSmallLossTable(dat.shock100, "ShockLow2yrdur10kspan1impact100.txt", 
    "Percent Permanent Losses, Shock Low 2yr dur10k span1 impact 100% "
    %+% "\n(percent loss by copies vs sector half-life in megahours)")





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
