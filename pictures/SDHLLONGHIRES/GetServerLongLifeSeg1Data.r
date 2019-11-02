# GetServerDefLifeSeg1Data.r
source("../common/DataUtil.r")
library(ggplot2)
source("../common/PlotUtil.r")

# P A R A M S
nSegments <- 1
nCopies <- 5
# ************ Also change summarize function and ggplot(color=...) and
#               lLegendItemLabels and xaxis logs and xaxis breaks!!!

# S T A N D A R D   F O R M A T T I N G 
sPlotFile <- (  "serverdeflife"
            %+% sprintf("seg%d",nSegments)
            %+% ".png"
            )
fnGroupBy <- function(dfIn) {group_by(dfIn, copies, lifem
                                    , serverdefaultlife
                                    , simlength
                                    , auditfrequency, auditsegments
                                    )}
fnSubset <- function(dfIn)  {subset(dfIn, serverdefaultlife>=10000
#                                    & shockfreq==0
                                    & copies==nCopies
                                    & auditfrequency==10000
                                    & auditsegments==nSegments
                                    )}
want.varnames <- c("copies","lifem","lost","docstotal"
                ,"serverdefaultlife","simlength"
                ,"shockfreq","shockimpact","shockspan","shockmaxlife"
                ,"auditfrequency","audittype","auditsegments"
                ,"deadserversactive","deadserversall")
fnNarrow <- function(dfIn)  {dfIn[want.varnames]}  


# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
allnewdat <- alldat.df %>% fnNarrow() %>% fnGroupBy() %>% 
summarize(losspct=round(mean(lost/docstotal)*100.0, 2), n=n()) 
newdat1 <- fnSubset(allnewdat)
newdat2 <- subset(newdat1, serverdefaultlife<=60*10000)
newdat3 <- subset(newdat2, simlength<20*10000)          
trows <- newdat3


sCopies <- sprintf("Copies=%.0f; ", nCopies)
sSegments <- sprintf("%d segment)", nSegments)
sTitleLine <-   (   ""
                %+% "Collection maintained on servers with finite lifetimes (varying, shown as half-life). "
                %+% "\n(Equivalent to random minor shocks that kill only one server) "
                %+% " "
                %+% "\n\n"
                %+% sCopies
                %+% "annual total auditing in "
                %+% sSegments
                )
sLegendLabel <- "  Length of\nSimulation\n   (years)"
lLegendItemLabels <- levels(factor(trows$simlength/10000))

sTimestamp <- fngettime()
sSamples <- sprintf("samples=%.0f ", mean(trows$n))     #min(trows$n)
sXLabel <- ("Server default life or shock arrival rate (half-life) in hours "
            %+% "      (one metric year = 10,000 hours) "
            %+% "                           (less frequent shocks =====>)"
            )
sXLabel <- sXLabel %+% ("\n\n                                  " # cheapo rjust.
            %+% sprintf("          %s   %s   %s", sPlotFile,sTimestamp,sSamples)
            )
sYLabel <- ("probability of losing the entire collection (%)")
# E N D   O F   S T A N D A R D   F O R M A T T I N G 


# P L O T   D A T A 
gp <- ggplot(data=trows
            , aes(x=serverdefaultlife,y=safe(losspct), color=factor(simlength))
            ) 
gp <- gp + labs(color=sLegendLabel)

gp <- fnPlotLogScales(gp, y="YES"
#                ,xbreaks=c(50,67,75,80,90,100)
                ,xbreaks=c(10000,20000,30000,40000,50000,80000,100000,200000)
                ,ybreaks=c(0.01,0.10,1.00,10,100)
                )
#gp <- gp + scale_x_reverse(breaks=c(50,67,75,80,90,100))
if(debugprint){fnhere("after LogScales")}
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
if(debugprint){fnhere("after scalecolor")}

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
if(debugprint){fnhere("after lines")}

plot(gp)
if(debugprint){fnhere("after plot")}
fnPlotMakeFile(gp, sPlotFile)
if(debugprint){fnhere("after plotfile")}

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
