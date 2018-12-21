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

trows <- dat.noaudit
gp <- ggplot(data=trows,aes(x=lifem,y=safe(mdmlosspct))) 

nCopies <- 1
trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="black", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, 
            linetype="dashed", color="red", size=1)

nCopies <- 2; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="black", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

nCopies <- 3; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="black", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="purple", size=1) 

nCopies <- 5; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="black", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="green", size=1) 

nCopies <- 10; trows <- fnSelectCopies(dat.noaudit, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="black", size=5, shape=(point.DIAMOND)) +
        geom_line(data=trows, linetype="dashed", color="black", size=1) 

gp <- fnPlotLogScales(gp, x="YES", y="YES"
        , xbreaks=c(2,5,10,50,100,1000,10000)
        , ybreaks=c(0.1,1,10,100)
        )
gp <- fnPlotTitles(gp 
        ,titleline="Without auditing, we need many copies"
            %+% "\nto minimize permanent losses, " 
            %+% "even with high quality disks"
            %+% "\n(shown for copies=1,2,3,5,10)"
        ,titlesize=16
        ,xlabel="1MB sector half-life (megahours)"
            %+% "                     (lower error rate ====>)"
        ,ylabel="permanent document losses (%)"
        ,labelsize=14
        )
gp <- fnPlotPercentLine(gp)

plot(gp)
fnPlotMakeFile(gp, "baseline-noaudit.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
