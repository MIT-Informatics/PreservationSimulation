# GetAuditRandomData.r

source("./DataUtil.r")
source("./PlotUtil.r")

# G E T   D A T A  
rm(results)
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.auditrandom <- fndfGetAuditData(results)

# T A B U L A T E   D A T A 
# Tabulate columns by copies and sector lifetime.
tbl.auditrandom <- data.frame(with(dat.auditrandom, 
            tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
# Re-form the data into a table for printing.  
foo<-(with(dat.auditrandom, 
       tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(results$copies))), foo)
tbl2<-data.frame(foo2)
colnames(tbl2)<-c("copies",as.numeric(colnames(foo2[,2:ncol(foo2)])))
# Pretty-print this to a file with explanatory headings.
sOutputFilename <- "./Data_AuditRandom.txt"
sTitle <- "Document losses with multiple copies and levels of random auditing"
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

# Micah succeeded in bending dcast to his will, thanks; see email.
library(reshape2)
bar.small <- dat.auditrandom[,c("copies", "lifem", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("copies", "lifem"))
bar.recast <- dcast(bar.melted, copies~lifem)

# P L O T   D A T A 
library(ggplot2)

# TMP
dat.auditrandom <- dat.auditrandom[dat.auditrandom$lifem<=100,]
dat.auditbaseline <- dat.auditrandom[dat.auditrandom$auditsegments==1,]
dat.auditrandom.monthly <- dat.auditrandom[dat.auditrandom$auditsegments==10,]
dat.auditrandom.quarterly <- dat.auditrandom[dat.auditrandom$auditsegments==4,]
dat.auditrandom.semiannually <- dat.auditrandom[dat.auditrandom$auditsegments==2,]

# Compare random qtly and monthly against total annual.



# Compare random semiannual, quarterly, and monthly.



# Show lines for 3, 4, 5 copies, with random segmented auditing, over wiiiide range.
nCopies <- 3
trows <- fnSelectCopies(dat.auditrandom, nCopies)
gp <- ggplot(data=trows,aes(x=lifem,y=safe(mdmlosspct))) 
gp <- gp + 
        scale_x_log10() + scale_y_log10() +
        annotation_logticks()

gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, 
            linetype="dashed", color="blue", size=1)

nCopies <- 4; trows <- fnSelectCopies(dat.auditrandom, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

nCopies <- 5; trows <- fnSelectCopies(dat.auditrandom, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="black", size=1) 

gp <- gp + ggtitle("With random auditing, sampling WITH replacement,\nsome docs are missed entirely, increasing losses")
gp <- gp + xlab("sector half-life (megahours)")
gp <- gp + ylab("percent permanent document losses")
gp <- gp + theme(
            axis.text=element_text(size=12),
            axis.title=element_text(size=18),
            plot.title=element_text(size=20,face="bold"),
            panel.border = element_rect(color = "black", fill=NA, size=1)
            )

plot(gp)
fnPlotMakeFile(gp, "baseline-auditrandom.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
