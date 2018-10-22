# GetCopies1HQData.r

library(png)
source("../common/DataUtil.r")

# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
newdat <- alldat.df %>%
group_by(copies, lifem
        ) %>%
summarize(mdmlosspct=round(midmean(lost/docstotal)*100.0, 2), n=n()) 

# Params today: quarterly auditing, five copies.
NCOPIES <- 1
results <- newdat
trows <- filter(results, copies==NCOPIES)

# P L O T   D A T A 
library(ggplot2)
source("../common/PlotUtil.r")

gp <- ggplot(data=trows
            , aes(x=lifem,y=safe(mdmlosspct)
            , color=factor(copies)
                    ) 
            )

# Plots
gp <- fnPlotLogScales(gp, x="YES", y="YES"
                ,xbreaks=c(2,5,10,100,1000,10000)
                ,ybreaks=c(0.01,0.10,1.00,10,100)
                )
gp <- gp + geom_line(
                  size=3
                , show.legend=TRUE
                , color="blue"
                )
gp <- gp + geom_point(data=trows
                , size=6
                , show.legend=TRUE
                , color="black"
                ) 

# Legends
gp <- gp + labs(color="Number of\nCopies"
                )
gp <- gp + theme(legend.position=c(0.55,0.90))
gp <- gp + theme(legend.background=element_rect(fill="lightgray", 
                                  size=0.5, linetype="solid"))
gp <- gp + theme(legend.key.size=unit(0.3, "in"))
gp <- gp + theme(legend.key.width=unit(0.6, "in"))
gp <- gp + theme(legend.text=element_text(size=16))
gp <- gp + theme(legend.title=element_text(size=14))

# Titles
gp <- fnPlotTitles(gp
            , titleline="One copy of a collection has unacceptable losses "
                %+% "\nover time, even with very high quality storage "
                %+% "\n "
                %+% "\n(Copies = 1, no auditing/repair is possible, duration = 10 years)"
#            , titlesize=22
            , xlabel="1MB sector half-life (megahours)"
                %+% "                           (lower error rate =====>)"
            , ylabel="permanent document losses (%)"
#            , labelsize=18
        ) 

# Limit lines
# Label the percentage lines out on the right side.
xlabelposition <- log10(6000)
gp <- fnPlotPercentLine(gp, xloc=xlabelposition)
gp <- fnPlotMilleLine(gp, xloc=xlabelposition)
gp <- fnPlotSubMilleLine(gp, xloc=xlabelposition)

# Annotations
gp <- gp + annotate(geom="text", x=12, y=60, label="No auditing/repair"
                    , color="black", size=7)
gp <- gp + annotate(geom="text", x=20, y=0.03
                    , label="Increasing \"quality\" of storage"
                    , color="red", size=10)
gp <- gp + annotate(geom="text", x=20, y=0.015
                    , label="Length of time for storage to deteriorate "
                            %+% "and lose a document"
                    , color="red", size=8)
gp <- gp + annotate(geom="text", x=400, y=0.03
                    , label="3-o'clock arrow goes here ========>>"
                    , color="red", size=5)
rightimg <- readPNG(source='../ARROWS/right_8.png', native=FALSE)
#img <- readPNG(system.file("img", "Rlogo.png", package="png"))

gp <- gp + annotation_raster(raster=rightimg, 
#                    ymin = 0.0015,ymax= 0.002,xmin = 100,xmax = 1000) + geom_point()
                    ymin = 1,ymax= 2,xmin = 100,xmax = 1000) + geom_point()

gp <- gp + annotate(geom="text", x=5000, y=20
                    , label="Decreasing\ndocument\nlosses"
                    , color="red", size=10)
gp <- gp + annotate(geom="text", x=10000, y=2
                    , label="6-o'clock arrow goes here ========>>"
                    , color="red", size=5, angle=270)
downimg <- readPNG(source='../ARROWS/right_8.png', native=FALSE)
gp <- gp + annotation_raster(raster=downimg, 
                    ymin = 1,ymax= 10,xmin = 10,xmax = 20) + geom_point()

# -------------- test --------------
blobimg <- readPNG(source='../ARROWS/blob1.png')
gp <- gp + annotation_raster(raster=blobimg, 
                    ymin = 1,ymax= 10,xmin = 10,xmax = 20) + geom_point()
# -------------- end test --------------



plot(gp)
fnPlotMakeFile(gp, "copies1hq.png")

# Unwind any remaining sink()s to close output files.  
while (sink.number() > 0) {sink()}
