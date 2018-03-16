# GetAuditFreqData.r
#                                       RBLandau 20171230
# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/audit/frequency")
# 
# For copies 3,4,5, what is the impact of more frequent total audits?
# 


source("../common/DataUtil.r")
source("../common/PlotUtil.r")


# G E T   D A T A  
if (exists("results")) {rm(results)}
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.auditallcopies <- as.data.frame(fndfGetAuditData(results))
dat.auditall <- dat.auditallcopies[dat.auditallcopies$copies>=3
                & dat.auditallcopies$copies<=5,]

# S U B S E T S 

if (nrow(dat.auditall) > 0)
{
    source("./AuditFreqPlots.r")

    dat.audit3 <- subset(dat.auditall, copies==3)
    gp <- fnPlotAuditFreq1(trows=dat.audit3, nCopies=3)
    plot(gp)
    fnPlotMakeFile(gp, "Audit_FrequencyComparisons_copies3_MonthToBiennial.png")

    dat.audit4 <- subset(dat.auditall, copies==4)
    gp <- fnPlotAuditFreq1(trows=dat.audit4, nCopies=4)
    plot(gp)
    fnPlotMakeFile(gp, "Audit_FrequencyComparisons_copies4_MonthToBiennial.png")

    dat.audit5 <- subset(dat.auditall, copies==5)
    gp <- fnPlotAuditFreq1(trows=dat.audit5, nCopies=5)
    plot(gp)
    fnPlotMakeFile(gp, "Audit_FrequencyComparisons_copies5_MonthToBiennial.png")


}



# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}


#END
