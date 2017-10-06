# GetAuditAnnuallyData.r

source("./DataUtil.r")

# G E T   D A T A  
rm(results)
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.auditannually <- fndfGetAuditData(results)

# T A B U L A T E   D A T A 
# Tabulate columns by copies and sector lifetime.
tbl.auditannually <- data.frame(with(dat.auditannually, 
            tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
# Re-form the data into a table for printing.  
foo<-(with(dat.auditannually, 
       tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(results$copies))), foo)
tbl2<-data.frame(foo2)
colnames(tbl2)<-c("copies",as.numeric(colnames(foo2[,2:ncol(foo2)])))
# Pretty-print this table into a separate file, with explanatory headings.  
#print(tbl2)

# Micah succeeded in bending dcast to his will, thanks; see email.
library(reshape2)
bar.small <- dat.auditannually[,c("copies", "lifem", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("copies", "lifem"))
bar.recast <- dcast(bar.melted, copies~lifem)

# P L O T   D A T A 
library(ggplot2)

# Show lines for 3, 4, 5 copies, with annual total auditing, over wiiiide range.
nCopies <- 3
trows <- fnSelectCopies(dat.auditannually, nCopies)
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

nCopies <- 4; trows <- fnSelectCopies(dat.auditannually, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

nCopies <- 5; trows <- fnSelectCopies(dat.auditannually, nCopies)
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(data=trows, linetype="dashed", color="black", size=1) 

gp <- gp + ggtitle("With annual auditing, we need only a few copies\nto minimize permanent losses over a wide range")
gp <- gp + xlab("sector half-life (megahours)")
gp <- gp + ylab("percent permanent document losses")
gp <- gp + theme(
            axis.text=element_text(size=12),
            axis.title=element_text(size=18),
            plot.title=element_text(size=20,face="bold"),
            panel.border = element_rect(color = "black", fill=NA, size=1)
            )

plot(gp)
fnPlotMakeFile(gp, "baseline-auditannually.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
