# GetAuditAnnuallyData.r

source("../common/DataUtil.r")

# G E T   D A T A  
if (exists("results")) {rm(results)}
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.auditannually <- fndfGetAuditData(results)

# T A B U L A T E   D A T A 
# Tabulate columns by copies and sector lifetime.
tbl.auditannually <- data.frame(with(dat.auditannually, 
            tapply(mdmlosspct, list(copies, lifem), FUN=identity)))

if(0){
# Re-form the data into a table for printing.  
foo<-(with(dat.auditannually, 
       tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(results$copies))), foo)
tbl2<-data.frame(foo2)
colnames(tbl2)<-c("copies",as.numeric(colnames(foo2[,2:ncol(foo2)])))
# Pretty-print this to a file with explanatory headings.
sOutputFilename <- "./Data_AuditAnnually.txt"
sTitle <- "Document losses with multiple copies and annual total auditing"
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
}#ENDIF0

# Micah succeeded in bending dcast to his will, thanks; see email.
library(reshape2)
bar.small <- dat.auditannually[,c("copies", "lifem", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("copies", "lifem"))
bar.recast <- dcast(bar.melted, copies~lifem)

# P L O T   D A T A 
library(ggplot2)
source("../common/PlotUtil.r")

# Show lines for 3, 4, 5 copies, with annual total auditing, over wiiiide range.
nCopies <- 3; trows3 <- fnSelectCopies(dat.auditannually, nCopies)
nCopies <- 4; trows4 <- fnSelectCopies(dat.auditannually, nCopies)
nCopies <- 5; trows5 <- fnSelectCopies(dat.auditannually, nCopies)
trows <- rbind(trows3, trows4, trows5)

gp <- ggplot(data=trows
            , aes(x=lifem,y=safe(mdmlosspct), color=factor(copies))
            ) 
gp <- gp + labs(color="Number of\nCopies")

gp <- fnPlotLogScales(gp, x="YES", y="YES"
                ,xbreaks=c(2,5,10,100,1000)
                ,ybreaks=c(0.01,0.10,1.00)
                )
gp <- gp + geom_line(
                  size=3
                , show.legend=TRUE
                )
gp <- gp + geom_point(data=trows
                , size=6
                , show.legend=TRUE
                , color="black"
                ) 

gp <- gp + theme(legend.position=c(0.8,0.7))
gp <- gp + theme(legend.background=element_rect(fill="lightgray", 
                                  size=0.5, linetype="solid"))
gp <- gp + theme(legend.key.size=unit(0.3, "in"))
gp <- gp + theme(legend.key.width=unit(0.6, "in"))
gp <- gp + theme(legend.text=element_text(size=16))
gp <- gp + theme(legend.title=element_text(size=14))

gp <- fnPlotTitles(gp
            , titleline="With auditing, in a peaceful world, "
                %+% "we need only a few copies"
                %+% "\nto minimize permanent losses over a wide range"
                %+% "\n"
                %+% "\n(Annual total auditing, duration = 10 years)"
            , xlabel="1MB sector half-life (megahours)"
                %+% "                           (lower error rate =====>)"
            , ylabel="permanent document losses (%)"
        ) 
# Label the percentage lines out on the right side.
xlabelposition <- log10(800)
gp <- fnPlotPercentLine(gp, xloc=xlabelposition)
gp <- fnPlotMilleLine(gp, xloc=xlabelposition)
gp <- fnPlotSubMilleLine(gp, xloc=xlabelposition)

plot(gp)
fnPlotMakeFile(gp, "baseline-auditannually.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}