# GetAuditVsNotData.r
source("../common/DataUtil.r")
library(ggplot2)
source("../common/PlotUtil.r")

# Params
sPlotFile <- "auditvsnot.png"
fnGroupBy <- function(dfIn) {group_by(dfIn, copies, lifem, auditfrequency)}
fnSubset <- function(dfIn) {subset(dfIn, copies==5 & lifem<=1000)}
sTitleLine <-   (   "Auditing dramatically decreases "
                %+% "permanent document losses "
                %+% "over a wide range "
                %+% "\n"
                %+% "\n(Copies=5, "
                %+% "annual total auditing vs no auditing, "
                %+% "duration = 10 years)"
                )
sLegendLabel <- "Audited? Y/N"
lLegendItemLabels <- c("Not audited", "Yes, audited")
sXLabel <- ("1MB sector half-life (megahours)"
            %+% "                           (lower error rate =====>)")
sYLabel <- ("permanent document losses (%)")


# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
newdat <- alldat.df %>% fnGroupBy() %>% 
summarize(mdmlosspct=round(midmean(lost/docstotal)*100.0, 2), n=n()) %>%
fnSubset()
trows <- newdat


# P L O T   D A T A 

gp <- ggplot(data=trows
            , aes(x=lifem,y=safe(mdmlosspct), color=factor(auditfrequency))
            ) 
gp <- gp + labs(color=sLegendLabel)

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
gp <- gp + scale_color_discrete(labels=lLegendItemLabels)

gp <- fnPlotTitles(gp
            , titleline=sTitleLine
            , xlabel=sXLabel
            , ylabel=sYLabel
        ) 
# Label the percentage lines out on the right side.
xlabelposition <- log10(800)
gp <- fnPlotPercentLine(gp, xloc=xlabelposition)
gp <- fnPlotMilleLine(gp, xloc=xlabelposition)
gp <- fnPlotSubMilleLine(gp, xloc=xlabelposition)

plot(gp)
fnPlotMakeFile(gp, sPlotFile)

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}