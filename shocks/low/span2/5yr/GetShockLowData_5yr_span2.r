# GetShockLowData_5yr_span2.r
#                                       RBLandau 20171230
# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/shocks/low/span2/5yr")

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
if (nrow(dat.shock) > 0) 
{
    dat.shock50 <- dat.shock[dat.shock$shockimpact==50,]
    dat.shock90 <- dat.shock[dat.shock$shockimpact==90,]
    dat.shock100 <- dat.shock[dat.shock$shockimpact==100,]

    # P L O T   D A T A 
    library(ggplot2)
    source("./ShockLowPlots.r")
    gp <- fnPlotShock1(dat.shock90, 5, 6, 2, 90)
    fnPlotMakeFile(gp, "Shock_freq5dur5kspan2impact90.png")
    gp <- fnPlotShock1(dat.shock50, 5, 6, 2, 50)
    fnPlotMakeFile(gp, "Shock_freq5dur5kspan2impact50.png")
    gp <- fnPlotShock1(dat.shock100, 5, 6, 2, 100)
    fnPlotMakeFile(gp, "Shock_freq5dur5kspan2impact100.png")

    # S U M M A R Y   T A B L E S 
    source("ShockLowTables.r")
    fnSaveSmallLossTable(dat.shock50, "ShockLow5yrdur5kspan2impact50.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur5k span2 impact 50% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
    fnSaveSmallLossTable(dat.shock90, "ShockLow5yrdur5kspan2impact90.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur5k span2 impact 90% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
    fnSaveSmallLossTable(dat.shock100, "ShockLow5yrdur5kspan2impact100.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur5k span2 impact 100% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
}

# Then, full year durations.
dat.shock <- dat.shockall[dat.shockall$lifem<=100 & dat.shockall$shockmaxlife==10000,]
if (nrow(dat.shock) > 0)
{
    dat.shock50 <- dat.shock[dat.shock$shockimpact==50,]
    dat.shock90 <- dat.shock[dat.shock$shockimpact==90,]
    dat.shock100 <- dat.shock[dat.shock$shockimpact==100,]

    # P L O T   D A T A 
    library(ggplot2)
    #source("./ShockLowPlots.r")
    gp <- fnPlotShock1(dat.shock90, 5, 12, 2, 90)
    fnPlotMakeFile(gp, "Shock_freq5dur10kspan2impact90.png")
    gp <- fnPlotShock1(dat.shock50, 5, 12, 2, 50)
    fnPlotMakeFile(gp, "Shock_freq5dur10kspan2impact50.png")
    gp <- fnPlotShock1(dat.shock100, 5, 12, 2, 100)
    fnPlotMakeFile(gp, "Shock_freq5dur10kspan2impact100.png")

    # S U M M A R Y   T A B L E S 
    # Print small summary tables.
    #source("ShockLowTables.r")
    fnSaveSmallLossTable(dat.shock50, "ShockLow5yrdur10kspan2impact50.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur10k span2 impact 50% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
    fnSaveSmallLossTable(dat.shock90, "ShockLow5yrdur10kspan2impact90.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur10k span2 impact 90% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
    fnSaveSmallLossTable(dat.shock100, "ShockLow5yrdur10kspan2impact100.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur10k span2 impact 100% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
}

# Then, two-year durations.
dat.shock <- dat.shockall[dat.shockall$lifem<=100 & dat.shockall$shockmaxlife==20000,]
if (nrow(dat.shock) > 0)
{
    dat.shock50 <- dat.shock[dat.shock$shockimpact==50,]
    dat.shock90 <- dat.shock[dat.shock$shockimpact==90,]
    dat.shock100 <- dat.shock[dat.shock$shockimpact==100,]

    # P L O T   D A T A 
    library(ggplot2)
    #source("./ShockLowPlots.r")
    gp <- fnPlotShock1(dat.shock90, 5, 24, 2, 90)
    fnPlotMakeFile(gp, "Shock_freq5dur20kspan2impact90.png")
    gp <- fnPlotShock1(dat.shock50, 5, 24, 2, 50)
    fnPlotMakeFile(gp, "Shock_freq5dur20kspan2impact50.png")
    gp <- fnPlotShock1(dat.shock100, 5, 24, 2, 100)
    fnPlotMakeFile(gp, "Shock_freq5dur20kspan2impact100.png")

    # S U M M A R Y   T A B L E S 
    # Print small summary tables.
    #source("ShockLowTables.r")
    fnSaveSmallLossTable(dat.shock50, "ShockLow5yrdur20kspan2impact50.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur20k span2 impact 50% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
    fnSaveSmallLossTable(dat.shock90, "ShockLow5yrdur20kspan2impact90.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur20k span2 impact 90% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
    fnSaveSmallLossTable(dat.shock100, "ShockLow5yrdur20kspan2impact100.txt", 
        "Percent Permanent Losses, Shock Low 5yr dur20k span2 impact 100% "
        %+% "\n(percent loss by copies vs sector half-life in megahours)")
}




if(0){ # comment out old code

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


#END
