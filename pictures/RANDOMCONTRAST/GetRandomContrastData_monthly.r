# GetRandomContrastData_monthly.r

source("../common/DataUtil.r")

# G E T   D A T A  
if (exists("results")) {rm(results)}
alldata.df <- fndfGetGiantDataRaw("")
newdat <- alldata.df %>%
group_by(copies, lifem, auditfrequency, audittype, auditsegments) %>%
summarize(mdmlosspct=round(midmean(lost/docstotal)*100.0, 2), n=n())

# Params today: quarterly auditing, five copies.
SEGMENTS <- 10
NCOPIES <- 5
results <- filter(newdat, auditsegments==SEGMENTS)
trows <- filter(results, copies==NCOPIES)

# P L O T   D A T A 
library(ggplot2)
source("../common/PlotUtil.r")

gp <- ggplot(data=trows
            , aes(x=lifem,y=safe(mdmlosspct)
            , color=factor(audittype)
            , shape=factor(copies)
            , segs=factor(auditsegments)
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
gp <- gp + labs(color="Audit type"
                , shape="Copies"
                , segs="Audit segments\nper year"
                )
gp <- gp + theme(legend.position=c(0.8,0.7))
gp <- gp + theme(legend.background=element_rect(fill="lightgray", 
                                  size=0.5, linetype="solid"))
gp <- gp + theme(legend.key.size=unit(0.3, "in"))
gp <- gp + theme(legend.key.width=unit(0.6, "in"))
gp <- gp + theme(legend.text=element_text(size=16))
gp <- gp + theme(legend.title=element_text(size=14))
gp <- gp + scale_color_discrete(labels=c("systematic","random"))

# Titles
gp <- fnPlotTitles(gp
            , titleline="Random auditing WITH replacement "
                %+% "misses many documents "
                %+% "that are then vulnerable to error, "
                %+% "\ncompared with auditing "
                %+% "WITHOUT replacement segmented at the same frequency "
                %+% "\n"
                %+% "\n(Uniform random vs total systematic auditing, monthly, duration = 10 years)"
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
fnPlotMakeFile(gp, "randomcontrast_monthly.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
