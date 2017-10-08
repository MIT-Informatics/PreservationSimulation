# GetAuditAnnuallyData.r

source("./DataUtil.r")

# G E T   D A T A  
rm(results)
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.docsize <- fndfGetDocsizeData(results)

# T A B U L A T E   D A T A 
# Tabulate columns by copies and sector lifetime.
tbl.docsize <- data.frame(with(dat.docsize, 
            tapply(mdmlosspct, list(docsize, lifem), FUN=identity)))
# Re-form the data into a table for printing.  
foo<-(with(dat.docsize, 
       tapply(mdmlosspct, list(docsize, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(results$docsize))), foo)
tbl2<-data.frame(foo2)
colnames(tbl2)<-c("docsize",as.numeric(colnames(foo2[,2:ncol(foo2)])))

# Pretty-print this to a file with explanatory headings.
sOutputFilename <- "./Data_ScalingDocsize.txt"
sTitle <- "Document losses with single copy and varying document size"
sSubtitle <- "Table of percentage loss of collection tabulated\n" %+% 
    "by document size (MB) and sector half-lifetime" %+% "\n\n" %+%
    "Note how document size and sector life scale together" %+% "\n\n\n" %+%
    "               sector half-life (megahours)"
sink(sOutputFilename)
cat("MIT Preservation Simulation Project", "\n\n")
cat(sOutputFilename, format(Sys.time(),"%Y%m%d_%H%M%S%Z"), "\n\n")
cat(sTitle, "\n\n")
cat(sSubtitle, "\n\n")
cat("\n")
# Micah succeeded in bending dcast to his will, thanks; see email.
library(reshape2)
bar.small <- dat.docsize[,c("lifem", "docsize", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("docsize", "lifem"))
bar.recast <- dcast(bar.melted, docsize~lifem)
print(bar.recast)
sink()






#if(0){
# P L O T   D A T A 
library(ggplot2)

# Show lines for 3, 4, 5 copies, with annual total auditing, over wiiiide range.
nDocsize <- 5; trows <- dat.docsize[dat.docsize$docsize==nDocsize,]
gp <- ggplot(data=trows,aes(x=lifem,y=safe(mdmlosspct))) 
gp <- gp + 
        scale_x_log10() + scale_y_log10() +
        annotation_logticks()

gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=("5")) +
        geom_line(data=trows, 
            linetype="dashed", color="blue", size=1)

nDocsize <- 50; trows <- dat.docsize[dat.docsize$docsize==nDocsize,]
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=("B")) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

nDocsize <- 500; trows <- dat.docsize[dat.docsize$docsize==nDocsize,]
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=("C")) +
        geom_line(data=trows, linetype="dashed", color="black", size=1) 

nDocsize <- 5000; trows <- dat.docsize[dat.docsize$docsize==nDocsize,]
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=("D")) +
        geom_line(data=trows, linetype="dashed", color="black", size=1) 

gp <- gp + ggtitle("Larger documents are larger targets to random errors\n" %+%
                "and therefore are lost more frequently.\n\n" %+%
                "Losses for collection with copies=1")
gp <- gp + xlab("sector half-life (megahours)")
gp <- gp + ylab("percent permanent document losses")
gp <- gp + theme(
            axis.text=element_text(size=12),
            axis.title=element_text(size=18),
            plot.title=element_text(size=18,face="bold"),
            panel.border = element_rect(color = "black", fill=NA, size=1)
            )

plot(gp)
fnPlotMakeFile(gp, "baseline-scalingdocsize.png")
#}




# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
