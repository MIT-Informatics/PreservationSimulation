# GetGlitchData_year.r
#                                       RBLandau 20180211
# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/glitch/year")
# 
# For copies=3,4,5: what are the failure rates with glitches?
# 


source("./DataUtil.r")
source("./PlotUtil.r")


# G E T   D A T A  
if (exists("results")) {rm(results)}
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.glitchallcopies <- as.data.frame(fndfGetGlitchData(results))
dat.glitchall <- dat.glitchallcopies[
                    dat.glitchallcopies$copies>=3
                &   dat.glitchallcopies$copies<=6,
                ]

# S U B S E T S 

if (nrow(dat.glitchall) > 0)
{
    source("./GlitchPlots.r")
    
    # freq 12mo dur 6mo
    dat.glitchspan1 <- data.frame(dat.glitchall[dat.glitchallcopies$glitchfreq>0
                        & dat.glitchall$glitchfreq==10000
                        & dat.glitchall$glitchmaxlife==5000
                        & dat.glitchall$glitchimpact==50
                        ,]
                        )
    gp <- fnPlotGlitch1(dat.glitchspan1, nFreq=10000, nDuration=5000, nSpan=1, nImpact=50)
    plot(gp)
    fnPlotMakeFile(gp, "Glitch_compare_copvar_freq12mo_dur6mo_span1_impact50.png")




    # freq 12mo dur 6mo
    dat.glitchspan1 <- dat.glitchall[dat.glitchall$glitchdecay==0
                        & dat.glitchall$glitchfreq==10000
                        & dat.glitchall$glitchmaxlife==5000
                        & dat.glitchall$glitchimpact==33
                        ,]
    gp <- fnPlotGlitch1(dat.glitchspan1, nFreq=10000, nDuration=5000, nSpan=1, nImpact=33)
    plot(gp)
    fnPlotMakeFile(gp, "Glitch_compare_copvar_freq12mo_dur6mo_span1_impact33.png")

    # freq 12mo dur 6mo
    dat.glitchspan1 <- dat.glitchall[dat.glitchall$glitchdecay==0
                        & dat.glitchall$glitchfreq==10000
                        & dat.glitchall$glitchmaxlife==5000
                        & dat.glitchall$glitchimpact==67
                        ,]
    gp <- fnPlotGlitch1(dat.glitchspan1, nFreq=10000, nDuration=5000, nSpan=1, nImpact=67)
    plot(gp)
    fnPlotMakeFile(gp, "Glitch_compare_copvar_freq12mo_dur6mo_span1_impact67.png")



}



# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}


#END
