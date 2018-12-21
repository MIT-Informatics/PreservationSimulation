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


fnPlotAuditFreq1 <- function(trows, nCopies){

    p <- ggplot(data=trows
                , mapping=aes(x=lifem, y=safe(mdmlosspct)
                #    , color=factor(auditfrequency)
                    )
                )

    p <- p + geom_line(data=trows, size=2
                , mapping=aes(color=factor(auditfrequency))
                )
    p <- p + geom_point(data=trows, shape=(point.DOT), size=4
#                , mapping=aes(color=factor(auditfrequency))
                )
    p <- p + theme(legend.position=c(1,0.8)
                , legend.justification=c(1,0.5)
                )
    p <- p + labs(color="Audit frequency")
    p <- p + scale_color_manual(
                labels=c("month","quarter","half-year","1 year", "2 years")
                , values = c("black","purple","green","blue","red")
                )

    p <- fnPlotLogScales(p, x='yes', y='yes')
    p <- fnPlotPercentLine(p)

    sParams <- sprintf("copies=%s", 
                    nCopies)

    p <- fnPlotTitles(p, title=("Audit frequency comparisons, " %+% sParams 
                            %+% "\nIncreasing auditing frequency beyond annually "
                            %+% "yields small benefits "
                            %+% "\nbut at greatly increased cost in bandwidth"
                            ) 
                ,titlesize=16 
                ,xlabel="1MB sector half-life (megahours)"
                    %+% "                  (lower error rate \u2192)"
                ,ylabel="permanent document losses (%)"
                ,labelsize=14
                ) 
}


# S U B S E T S 

if (nrow(dat.auditall) > 0)
{
#    source("./AuditFreqPlots.r")

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


# Edit history:
# longago   RBL Original version.
# 20180326  RBL Put in unbelievably obscure and horrible syntax to control
#                legend title, colors, labels.  Who would guess that 
#                "scale_color_manual()" would be the function to control
#                the line colors and the legend labels for the variable
#                factor(auditfrequency)?  
#               Move fnPlotAuditFreq1() function into here from the 
#                subsidiary file.  
# 
# 

#END
