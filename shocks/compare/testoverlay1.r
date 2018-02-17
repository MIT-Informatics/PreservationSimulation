source("./DataUtil.r")
source("./PlotUtil.r")
nCopies<-5

results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.shockallcopies <- as.data.frame(fndfGetShockData(results))
dat.shockall <- dat.shockallcopies[dat.shockallcopies$copies>=3
                & dat.shockallcopies$copies<=5,]
dat.shock5.3 <- dat.shockall[dat.shockall$copies==5 
                            & dat.shockall$shockspan==3,
                            ]

trows <- dat.shock5.3
 
    trows50 <- trows[trows$shockimpact==50,]
    trows80 <- trows[trows$shockimpact==80,]
    trows100 <- trows[trows$shockimpact==100,]

    gp <- ggplot(mapping=aes(x=lifem, y=safelog(mdmlosspct)))

    gp <- gp + 
            geom_point(data=trows50, 
                    color="blue", size=8, shape=16) +
            geom_line(data=trows50, 
                    linetype="solid", color="blue", size=2)

    gp <- gp + 
            geom_point(data=trows80, 
                    color="red", size=8, shape=16) +
            geom_line(data=trows80, 
                    linetype="solid", color="red", size=2)


p<-gp

    p <- fnPlotLogScales(p, x='yes', y='yes')

    p <- p + scale_colour_discrete(name="Impact\n(percent)", labels=c("50","80","100"))
    p <- p + geom_hline(yintercept=1.0, linetype="dashed")
    
    sParams <- sprintf("copies=%s", 
                    nCopies)

    p <- fnPlotTitles(p, title=("Shocks " %+% sParams), titlesize=16, 
                xlabel="sector half-life (megahours)", 
                ylabel="percent permanent document losses", 
                labelsize=14) 

    