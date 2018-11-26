# GetShockSpan1Server2Data.r
source("../common/DataUtil.r")
library(ggplot2)
source("../common/PlotUtil.r")


# P A R A M S
sPlotFile <- "shockspan1server2.png"
fnGroupBy <- function(dfIn) {group_by(dfIn, copies, lifem
                                    , serverdefaultlife
                                    , shockfreq, shockspan, shockimpact
                                    , shockmaxlife
                                    )}
fnSubset <- function(dfIn)  {subset(dfIn, serverdefaultlife==20000)}
want.varnames <- c("copies","lifem","lost","docstotal","serverdefaultlife"
                ,"shockfreq","shockimpact","shockspan","shockmaxlife"
                ,"auditfrequency","audittype","auditsegments"
                ,"deadserversactive","deadserversall")
fnNarrow <- function(dfIn)  {dfIn[want.varnames]}  
sTitleLine <-   (   ""
                %+% "Shocks duration=0.5yr span=1 serverdefaultlife=2yrs "
                %+% " "
                %+% " "
                %+% "\n"
                %+% "\n(Copies=4,5,6, annual total auditing)"
                )
sLegendLabel <- "  Number of \nAudited Copies"
lLegendItemLabels <- c("4", "5", "6")
sXLabel <- ("Shock Frequency (half-life) in hours "
            %+% "                           (less frequent shocks =====>)")
sYLabel <- ("probability of losing the entire collection (%)")
# ************ Also change summarize function and ggplot(color=...).


# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
newdat <- alldat.df %>% fnGroupBy() %>% 
summarize(losspct=round(mean(lost/docstotal)*100.0, 2), n=n()) %>%
fnSubset()
trows <- newdat


# P L O T   D A T A 
gp <- ggplot(data=trows
            , aes(x=shockfreq,y=safe(losspct), color=factor(copies))
            ) 
gp <- gp + labs(color=sLegendLabel)

gp <- fnPlotLogScales(gp, x="YES", y="YES"
#                ,xbreaks=c(50,67,75,80,90,100)
                ,xbreaks=c(5000,10000,15000,20000,25000,30000)
                ,ybreaks=c(0.01,0.10,1.00,10,100)
                )
#gp <- gp + scale_x_reverse(breaks=c(50,67,75,80,90,100))
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
