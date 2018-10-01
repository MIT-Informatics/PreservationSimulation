# GetShockSpan1Server1234Data.r
source("../common/DataUtil.r")
library(ggplot2)
source("../common/PlotUtil.r")


# P A R A M S
sPlotFile <- "shockspan1server1234.png"
fnGroupBy <- function(dfIn) {group_by(dfIn, copies, lifem
                                    , serverdefaultlife
                                    , shockfreq, shockspan, shockimpact
                                    , shockmaxlife
                                    )}
fnSubset <- function(dfIn)  {subset(dfIn, copies==1 & lifem<=10000)}
want.varnames <- c("copies","lifem","lost","docstotal","serverdefaultlife"
                ,"shockfreq","shockimpact","shockspan","shockmaxlife"
                ,"auditfrequency","audittype","auditsegments"
                ,"deadserversactive","deadserversall")
fnNarrow <- function(dfIn)  {dfIn[want.varnames]}  
sTitleLine <-   (   ""
                %+% "Shocks span1 serverdefaultlife1234yrs "
                %+% " "
                %+% " "
                %+% "\n"
                %+% "\n(Copies=3, annual total auditing)"
                )
sLegendLabel <- "Document\n size (MB)"
lLegendItemLabels <- c("5", "50", "500", "5000")
sXLabel <- ("1MB sector half-life (megahours)"
            %+% "                           (lower error rate =====>)")
sYLabel <- ("permanent document losses (%)")
# Also change summarize function and ggplot(color=...).


# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
newdat <- alldat.df %>% fnGroupBy() %>% 
summarize(losspct=round(mean(lost/docstotal/n())*100.0, 2), n=n()) %>%
fnSubset()
trows <- newdat


# P L O T   D A T A 
gp <- ggplot(data=trows
            , aes(x=lifem,y=safe(mdmlosspct), color=factor(docsize))
            ) 
gp <- gp + labs(color=sLegendLabel)

gp <- fnPlotLogScales(gp, x="YES", y="YES"
                ,xbreaks=c(2,5,10,100,1000,10000)
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

gp <- gp + theme(legend.position=c(0.15,0.3))
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
