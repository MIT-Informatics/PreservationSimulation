# GetShockData_high_span3.r
#                                       RBLandau 20180129
# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/shocks/high/span3")
# 
# For copies=3,4,5,6: what are the failure rates at shock span3?
# 


source("./DataUtil.r")
source("./PlotUtil.r")


# G E T   D A T A  
if (exists("results")) {rm(results)}
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.shockallcopies <- as.data.frame(fndfGetShockData(results))
dat.shockall <- dat.shockallcopies[dat.shockallcopies$copies>=3
                & dat.shockallcopies$copies<=6,]

# S U B S E T S 

if (nrow(dat.shockall) > 0)
{
    source("./ShockLowPlots.r")
    
    # freq 2yr dur 6mo
    dat.shockspan3 <- dat.shockall[dat.shockall$shockspan==3
                        & dat.shockall$shockfreq==20000
                        & dat.shockall$shockmaxlife==5000
                        & dat.shockall$shockimpact==50,]
    gp <- fnPlotShock1(dat.shockspan3, nFreq=2, nDuration=6, nSpan=3, nImpact=50)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur6mo_span3_impact50.png")

    dat.shockspan3 <- dat.shockall[dat.shockall$shockspan==3
                        & dat.shockall$shockfreq==20000
                        & dat.shockall$shockmaxlife==5000
                        & dat.shockall$shockimpact==90,]
    gp <- fnPlotShock1(dat.shockspan3, nFreq=2, nDuration=6, nSpan=3, nImpact=90)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur6mo_span3_impact90.png")
    
    dat.shockspan3 <- dat.shockall[dat.shockall$shockspan==3
                        & dat.shockall$shockfreq==20000
                        & dat.shockall$shockmaxlife==5000
                        & dat.shockall$shockimpact==100,]
    gp <- fnPlotShock1(dat.shockspan3, nFreq=2, nDuration=6, nSpan=3, nImpact=100)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur6mo_span3_impact100.png")

    
    # freq 2yr dur 12mo
    dat.shockspan3 <- dat.shockall[dat.shockall$shockspan==3
                        & dat.shockall$shockfreq==20000
                        & dat.shockall$shockmaxlife==10000
                        & dat.shockall$shockimpact==50,]
    gp <- fnPlotShock1(dat.shockspan3, nFreq=2, nDuration=12, nSpan=3, nImpact=50)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur12mo_span3_impact50.png")

    dat.shockspan3 <- dat.shockall[dat.shockall$shockspan==3
                        & dat.shockall$shockfreq==20000
                        & dat.shockall$shockmaxlife==10000
                        & dat.shockall$shockimpact==90,]
    gp <- fnPlotShock1(dat.shockspan3, nFreq=2, nDuration=12, nSpan=3, nImpact=90)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur12mo_span3_impact90.png")
    
    dat.shockspan3 <- dat.shockall[dat.shockall$shockspan==3
                        & dat.shockall$shockfreq==20000
                        & dat.shockall$shockmaxlife==10000
                        & dat.shockall$shockimpact==100,]
    gp <- fnPlotShock1(dat.shockspan3, nFreq=2, nDuration=12, nSpan=3, nImpact=100)
    plot(gp)
    fnPlotMakeFile(gp, "Shock_compare_copvar_freq2yr_dur12mo_span3_impact100.png")





}



# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}


#END
