# GetShockData_compare_cop5.r
#                                       RBLandau 20171230
# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/shocks/compare/cop5")
# 
# For copies=5, what are the failure rates at shock impacts 50, 80, 100%?
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
    
    dat.shock5.3 <- dat.shockall[dat.shockall$copies==5 
                            & dat.shockall$shockspan==3,
                            ]
    gp <- fnPlotShock4(trows=dat.shock5.3, nCopies=5)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_cop5_freq2yr_dur1yr_span3.png")



}



# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}


#END
