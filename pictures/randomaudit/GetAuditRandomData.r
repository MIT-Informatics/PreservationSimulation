# GetAuditRandomData.r

source("../common/DataUtil.r")
source("../common/PlotUtil.r")

# G E T   D A T A  
rm(results)
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.auditrandom <- as.data.frame(fndfGetAuditData(results))

# S U B S E T S 
dat.auditrandom <- dat.auditrandom[dat.auditrandom$lifem<=100,]
dat.auditbaseline <- dat.auditrandom[dat.auditrandom$auditsegments==1 
                                    & dat.auditrandom$lifem>=3,]
dat.auditrandom.monthly <- dat.auditrandom[dat.auditrandom$auditsegments==10,]
dat.auditrandom.quarterly <- dat.auditrandom[dat.auditrandom$auditsegments==4,]
dat.auditrandom.semiannually <- dat.auditrandom[dat.auditrandom$auditsegments==2,]

source("./RandomTables.r")

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

# Micah succeeded in bending dcast to his will, thanks; see email.
library(reshape2)
bar.small <- dat.auditrandom[,c("copies", "lifem", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("copies", "lifem"))
bar.recast <- dcast(bar.melted, copies~lifem)

# P L O T   D A T A 
library(ggplot2)

# Compare random qtly and monthly against total annual.

source("./RandomPlots.r")

# R A N D O M   V S   B A S E L I N E 

# Show lines for 3 copies, with random segmented auditing, over wiiiide range.
nCopies <- 3
gp <- fnPlotRandomMonthlyVsBaseline(nCopies)
plot(gp)
fnPlotMakeFile(gp, "baseline-auditrandomvsbaseline-c3.png")

# Show lines for 4 copies, with random segmented auditing, over wiiiide range.
nCopies <- 4
gp <- fnPlotRandomMonthlyVsBaseline(nCopies)
plot(gp)
fnPlotMakeFile(gp, "baseline-auditrandomvsbaseline-c4.png")

# Show lines for 5 copies, with random segmented auditing, over wiiiide range.
nCopies <- 5
gp <- fnPlotRandomMonthlyVsBaseline(nCopies)
plot(gp)
fnPlotMakeFile(gp, "baseline-auditrandomvsbaseline-c5.png")




# M O R E   R A N D O M   S E G M E N T S 

# Compare random semiannual, quarterly, and monthly.

# Show lines for 3 copies, with random segmented auditing, over wiiiide range.
nCopies <- 3
gp <- fnPlotRandomVariousSegments(nCopies)
plot(gp)
fnPlotMakeFile(gp, "baseline-auditrandomvarioussegments-c3.png")

# Show lines for 4 copies, with random segmented auditing, over wiiiide range.
nCopies <- 4
gp <- fnPlotRandomVariousSegments(nCopies)
plot(gp)
fnPlotMakeFile(gp, "baseline-auditrandomvarioussegments-c4.png")

# Show lines for 5 copies, with random segmented auditing, over wiiiide range.
nCopies <- 5
gp <- fnPlotRandomVariousSegments(nCopies)
plot(gp)
fnPlotMakeFile(gp, "baseline-auditrandomvarioussegments-c5.png")


# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
