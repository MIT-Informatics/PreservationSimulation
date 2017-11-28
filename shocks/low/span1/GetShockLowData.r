# GetShockLowData.r

source("./DataUtil.r")

# G E T   D A T A  
rm(results)
rm(dat.shock,tbl.shock)
rm(foo,foo2,tbl2,tbl3)
rm(bar.small,bar.melted,bar.recast)

results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.shock <- fndfGetShockData(results)

# S U B D I V I D E   D A T A 

# Shock selection functions.
fndfShockDat <- function(input, freq, impact, duration) {
    res1 <- input[input$copies>1 & 
                input$shockfreq==freq & 
                input$shockimpact==impact & 
                input$shockmaxlife==duration,]
}

f <- dat.shock

# Freq 1 yr
f1i50dh <- fndfShockDat(f, 10000, 50, 5000)
f1i90dh <- fndfShockDat(f, 10000, 90, 5000)
f1i100dh <- fndfShockDat(f, 10000, 100, 5000)
f1i50d1 <- fndfShockDat(f, 10000, 50, 10000)
f1i90d1 <- fndfShockDat(f, 10000, 90, 10000)
f1i100d1 <- fndfShockDat(f, 10000, 100, 10000)

# Freq 2 yr
f2i50dh <- fndfShockDat(f, 20000, 50, 5000)
f2i90dh <- fndfShockDat(f, 20000, 90, 5000)
f2i100dh <- fndfShockDat(f, 20000, 100, 5000)
f2i50d1 <- fndfShockDat(f, 20000, 50, 10000)
f2i90d1 <- fndfShockDat(f, 20000, 90, 10000)
f2i100d1 <- fndfShockDat(f, 20000, 100, 10000)
f2i50d1 <- fndfShockDat(f, 20000, 50, 20000)
f2i90d1 <- fndfShockDat(f, 20000, 90, 20000)
f2i100d1 <- fndfShockDat(f, 20000, 100, 20000)

# Freq 5 yr
f5i50dh <- fndfShockDat(f, 50000, 50, 5000)
f5i90dh <- fndfShockDat(f, 50000, 90, 5000)
f5i100dh <- fndfShockDat(f, 50000, 100, 5000)
f5i50d1 <- fndfShockDat(f, 50000, 50, 10000)
f5i90d1 <- fndfShockDat(f, 50000, 90, 10000)
f5i100d1 <- fndfShockDat(f, 50000, 100, 10000)
f5i50dh <- fndfShockDat(f, 50000, 50, 20000)
f5i90dh <- fndfShockDat(f, 50000, 90, 20000)
f5i100dh <- fndfShockDat(f, 50000, 100, 20000)

# T A B U L A T E   D A T A 
# Tabulate columns by copies and sector lifetime.

# Pretty-print a table to a file with explanatory headings.
sOutputFilename <- "./Data_ShockLow.txt"
sTitle <- "XXX Document losses with single copy and varying document size"
sSubtitle <- "XXX Table of percentage loss of collection tabulated\n" %+% 
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
bar.small <- dat.shock[,c("lifem", "copies", "mdmlosspct")]
bar.melted <- melt(bar.small, id=c("copies", "lifem"))
bar.recast <- dcast(bar.melted, copies~lifem, fun.aggregate=max)
print(bar.recast)
sink()

# Also print the raw table for use in a spreadsheet of comparisons.
sComparisonDataFilename <- "XXX Data_Scaling_shockSpreadsheetData.txt"
sink(sComparisonDataFilename)
cat(sTitle, "\n\n")
print(bar.small, n=nrow(bar.small))
sink()


if(0){
# P L O T   D A T A 
library(ggplot2)

# Show lines for shocks 5, 50, 500, 5000 MB; copies=1; over wiiiide range.
nCopies <- 3; trows <- dat.shock[dat.shock$copies==nCopies,]
gp <- ggplot(data=trows,aes(x=lifem,y=safe(mdmlosspct))) 
gp <- gp + 
        scale_x_log10() + scale_y_log10() +
        annotation_logticks()

# copies=3
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=("5")) +
        geom_line(data=trows, 
            linetype="dashed", color="blue", size=1)

# copies=4
nCopies <- 4; trows <- dat.shock[dat.shock$copies==nCopies,]
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=("B")) +
        geom_line(data=trows, linetype="dashed", color="blue", size=1) 

# copies=5
nCopies <- 5; trows <- dat.shock[dat.shock$copies==nCopies,]
gp <- gp + 
        aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
        geom_point(data=trows, 
            color="red", size=5, shape=("C")) +
        geom_line(data=trows, linetype="dashed", color="black", size=1) 


gp <- gp + ggtitle("XXX Larger documents are larger targets to random errors\n" %+%
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
fnPlotMakeFile(gp, "baseline-shocklow.png")
}


# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}