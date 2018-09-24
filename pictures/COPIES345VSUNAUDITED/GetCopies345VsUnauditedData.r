# GetCopies345VsUnauditedData.r
source("../common/DataUtil.r")
library(ggplot2)
source("../common/PlotUtil.r")


# P A R A M S
sPlotFile <- "copies345vsunaudited.png"
fnGroupBy <- function(dfIn) {group_by(dfIn, copies, lifem
                                    , auditfrequency)}
fnSubset <- function(dfIn) {subset(dfIn, copies>=3 & copies<=5 
                                    & lifem<=1000
                                    & auditfrequency==10000)}
sTitleLine <-   (   ""
                %+% "With regular auditing, only a few copies are required "
                %+% "to minimize losses over a wide range. "
                %+% "\nFailure to audit the collection is worse than keeping "
                %+% "\nonly a small number of audited copies "
                %+% "\n"
                %+% "\n(Copies=3,4,5 with annual auditing vs "
                %+% "copies=5 with no auditing, duration=10 years)"
                )
sLegendLabel <- "Number of\n  Audited\n  Copies"
lLegendItemLabels <- c("3", "4", "5")
sXLabel <- ("1MB sector half-life (megahours)"
            %+% "                           (lower error rate =====>)")
sYLabel <- ("permanent document losses (%)")
# Also change summarize function and ggplot(color=...).


# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
newdat <- alldat.df %>% fnGroupBy() %>% 
summarize(mdmlosspct=round(midmean(lost/docstotal)*100.0, 2), n=n()) %>%
fnSubset()
trows <- newdat


# P L O T   D A T A 

gp <- ggplot(data=trows
            , aes(x=lifem,y=safe(mdmlosspct), color=factor(copies))
            ) 
gp <- gp + labs(color=sLegendLabel)

gp <- fnPlotLogScales(gp, x="YES", y="YES"
                ,xbreaks=c(2,5,10,100,1000)
                ,ybreaks=c(0.01,0.10,1.00,10,100)
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

gp <- gp + theme(legend.position=c(0.8,0.8))
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

# Unaudited line separate.
undat = subset(alldat.df, auditfrequency==0 & copies==5 & lifem<=1000) %>%
fnGroupBy() %>%
summarize(mdmlosspct=round(midmean(lost/docstotal)*100.0, 2), n=n()) 
gp <- fnPlotAddLine(gp, undat, dotsize=6, linesize=1, lineshape="dotted")
gp <- gp + annotate(geom="text", x=6, y=11, label="5 copies with\nno auditing"
                    , color="black", size=7)
gp <- gp + annotate(geom="text", x=2.6, y=0.005, label="5 copies \nwith auditing"
                    , color="black", size=7)


plot(gp)
fnPlotMakeFile(gp, sPlotFile)

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
