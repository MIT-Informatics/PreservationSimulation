# GetNoAuditData.r

source("../common/DataUtil.r")

# G E T   D A T A  
rm(results)
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.noaudit <- fndfGetAuditData(results)

# T A B U L A T E   D A T A 
# Tabulate columns by copies and sector lifetime.
tbl.noaudit <- data.frame(with(dat.noaudit, 
            tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
# Re-form the data into a table for printing.  
#tbl<-cbind.data.frame(dat.noaudit$copies, tbl.noaudit)
#tbl<-cbind.data.frame(levels(factor(dat.noaudit$copies)), tbl.noaudit)
#colnames(tbl)<-c("copies",colnames(tbl.noaudit))
foo<-(with(dat.noaudit, 
       tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(results$copies))), foo)
tbl2<-data.frame(foo2)
colnames(tbl2)<-c("copies",as.numeric(colnames(foo2[,2:ncol(foo2)])))

# Pretty-print this to a file with explanatory headings.
sOutputFilename <- "./Data_NoAudit.txt"
sTitle <- "Document losses with multiple copies and no auditing"
sSubtitle <- "Table of percentage loss of collection tabulated\n" %+% 
    "by number of copies and sector half-lifetime"
sink(sOutputFilename)
cat("MIT Preservation Simulation Project", "\n\n")
cat(sOutputFilename, format(Sys.time(),"%Y%m%d_%H%M%S%Z"), "\n\n")
cat(sTitle, "\n\n")
cat(sSubtitle, "\n\n")
cat("\n")
print(tbl2)
sink()

# Micah finally bent dcast to his will, thanks; see email.
# Gets the same answer for this simple case.
library(reshape2)
bar.small <- dat.noaudit[,c("copies", "lifem", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("copies", "lifem"))
bar.recast <- dcast(bar.melted, copies~lifem)

# P L O T   D A T A 
library(ggplot2)
source("../common/PlotUtil.r")

nCopies <- 1
trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- ggplot(data=trows,aes(x=lifem,y=safe(mdmlosspct))) 
gp <- gp + 
        scale_x_log10() + scale_y_log10() +
        annotation_logticks()
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, 
            linetype="dashed", color="black", size=1)

nCopies <- 2; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

nCopies <- 3; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

nCopies <- 5; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

nCopies <- 9; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

gp <- gp + ggtitle("Without auditing, we need many copies\nto minimize permanent losses")
gp <- gp + xlab("sector half-life (megahours)")
gp <- gp + ylab("percent permanent document losses")
gp <- gp + theme(
            axis.text=element_text(size=12),
            axis.title=element_text(size=18),
            plot.title=element_text(size=22,face="bold"),
            panel.border = element_rect(color = "black", fill=NA, size=1)
            )
gp <- fnPlotPercentLine(gp)

plot(gp)
fnPlotMakeFile(gp, "baseline-noaudit.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
