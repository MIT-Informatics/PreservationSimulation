# GetNoAuditCalibrationCopies1Data.r


# G E T   D A T A  

source("../common/DataUtil.r")

if (!exists('dir.string') || (is.null(dir.string))) {dir.string <- "./"}
filesList <- grep(pattern="^Giant.*\\.txt$", dir(dir.string), 
                perl=TRUE, value = TRUE)
dat.noaudit <- read.table(filesList[1],
                        header=TRUE,sep=" ", na.strings="nolinefound")
mdmlosspct <- dat.noaudit$EmpiricalLosses / 100.0
newdat <- cbind(dat.noaudit,mdmlosspct)
dat.noaudit <- newdat


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
            color="red", size=3, shape=(point.DOT)) +
        geom_line(data=trows, 
            linetype="dashed", color="black", size=1)

gp <- fnPlotLogScales(gp, x="YES", y="YES"
        , xbreaks=c(2,5,10,50,100,1000,10000)
        , ybreaks=c(0.1,1,10,100)
        )
gp <- fnPlotTitles(gp 
        ,titleline="With a single copy, losses are unacceptable, "
            %+% "even with high quality disks"
            %+% "\n(document losses over 10 years)"
        ,titlesize=16
        ,xlabel="1MB sector half-life (megahours)"
            %+% "                     (lower error rate \u2192)"
        ,ylabel="permanent document losses (% of collection)"
        ,labelsize=14
        )
gp <- fnPlotPercentLine(gp)
gp <- fnPlotMilleLine(gp)
#gp <- fnPlotSubMilleLine(gp)


# A N N O T A T I O N S 

labelsize <- 10
gp <- gp + geom_text(x=log10(150.0), y=log10(0.04) 
                ,label="Increasing quality of storage    \u2192 \u2192 \u2192"
                ,size=labelsize, color="red"
                ,fontface="plain", family="sans")

gp <- gp + geom_text(x=log10(10000.0), y=log10(1.2)
                ,label="Decreasing\ndocument\nlosses "
                %+% "\n\u2193\n\u2193\n\u2193"
                ,size=labelsize, color="red"
                ,fontface="plain", family="sans"
                ,hjust=1)


plot(gp)
fnPlotMakeFile(gp, "baseline-noaudit.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
