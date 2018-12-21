# GetShockData_compare_pct67.r
#                                       RBLandau 20171230
# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/shocks/compare/pct67")
# 
# For copies=3,4,5, what are the failure rates at shock impact 67%?
# 


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

if (nrow(dat.shockall) > 0)
{
    source("./ShockLowPlots.r")
    
    dat.shockspan2 <- dat.shockall[dat.shockall$shockspan==2,]
    gp <- fnPlotShock1(dat.shockspan2, nFreq=2, nDuration=12, nSpan=2, nImpact=67)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur1yr_span2_impact67.png")

    dat.shockspan3 <- dat.shockall[dat.shockall$shockspan==3,]
    gp <- fnPlotShock1(dat.shockspan3, nFreq=2, nDuration=12, nSpan=3, nImpact=67)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur1yr_span3_impact67.png")



}



# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}


#END
