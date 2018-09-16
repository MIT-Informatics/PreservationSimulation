# GetGlitchErrorRates.r

source("../common/DataUtil.r")

# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
newdat <- alldat.df %>%
group_by(copies, lifem
        , auditfrequency, audittype, auditsegments
        , glitchfreq, glitchimpact) %>%
summarize(mdmlosspct=round(midmean(lost/docstotal)*100.0, 2), n=n()) 

# Params today: quarterly auditing, five copies.
IMPACTLO <- 67
IMPACTHI <- 90
NCOPIES <- 5
results0 <- filter(newdat, glitchimpact==0)
results1 <- filter(newdat, glitchimpact==IMPACTLO)
results2 <- filter(newdat, glitchimpact==IMPACTHI)
results <- rbind(results0, results1, results2)
trows <- filter(results, copies==NCOPIES)

# P L O T   D A T A 
library(ggplot2)
source("../common/PlotUtil.r")

gp <- ggplot(data=trows
            , aes(x=lifem,y=safe(mdmlosspct)
            , color=factor(glitchimpact)
#            , shape=factor(copies)
                    ) 
            )

# Plots
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

# Legends
gp <- gp + labs(color="Glitch impacts"
                )
gp <- gp + theme(legend.position=c(0.75,0.7))
gp <- gp + theme(legend.background=element_rect(fill="lightgray", 
                                  size=0.5, linetype="solid"))
gp <- gp + theme(legend.key.size=unit(0.3, "in"))
gp <- gp + theme(legend.key.width=unit(0.6, "in"))
gp <- gp + theme(legend.text=element_text(size=16))
gp <- gp + theme(legend.title=element_text(size=14))
gp <- gp + scale_color_discrete(labels=c("none", "moderate", "high"))

# Titles
gp <- fnPlotTitles(gp
            , titleline="Occasional temporary glitches "
                %+% "increase the server error rate for some period, "
                %+% "\nbut otherwise are not substantially different "
                %+% "from normal operation "
                %+% "\n "
                %+% "\n(Total annual auditing, 5 copies, duration = 10 years)"
            , xlabel="1MB sector half-life (megahours)"
                %+% "                           (lower error rate =====>)"
            , ylabel="permanent document losses (%)"
        ) 

# Limit lines
# Label the percentage lines out on the right side.
xlabelposition <- log10(800)
gp <- fnPlotPercentLine(gp, xloc=xlabelposition)
gp <- fnPlotMilleLine(gp, xloc=xlabelposition)
gp <- fnPlotSubMilleLine(gp, xloc=xlabelposition)

plot(gp)
fnPlotMakeFile(gp, "glitcherrorrates.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
