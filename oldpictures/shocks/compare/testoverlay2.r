# testoverlay2.r
# Demonstrate the problem of initiating ggplot inside a function.  I hope.  


if(0){
    # Function copied here for clarity, from PlotUtil.r.

    # f n P l o t B e g i n 
    fnPlotBegin <- function(dat=NULL, xcol=NULL, ycol=NULL, context=NULL) {
        gp <- ggplot(data=dat, mapping=aes(x=xcol, y=ycol))
        return(gp)
    }
} else
{
    source("./PlotUtil.r")
}#ENDIF0


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

if(1){  # 
    gp <- fnPlotBegin(
                    dat=NULL
                    , xcol=lifem, ycol=safe(mdmlosspct)
                    , context=trows
                    )
} else
{   # 
    gp <- ggplot(data=NULL, mapping=aes(x=lifem, y=safe(mdmlosspct)))
}#ENDIF0

    gp <- gp + 
            geom_point(data=trows50, 
                    color="green", size=8, shape=point.DOT) +
            geom_line(data=trows50, 
                    linetype="solid", color="green", size=2)

    gp <- gp + 
            geom_point(data=trows80, 
                    color="blue", size=5, shape=point.TRIANGLE) +
            geom_line(data=trows80, 
                    linetype="solid", color="blue", size=2)

    gp <- gp + 
            geom_point(data=trows100, 
                    color="red", size=3, shape=point.SQUARE) +
            geom_line(data=trows100, 
                    linetype="solid", color="red", size=2)


p<-gp

    p <- fnPlotLogScales(p, x='yes', y='yes')

    p <- p + scale_colour_discrete(name="Impact\n(percent)", labels=c("50","80","100"))
    p <- p + geom_hline(yintercept=1.0, linetype="dashed")
    
    sParams <- sprintf("copies=%s", 
                    nCopies)

    p <- fnPlotTitles(p, title=("Shocks " %+% sParams 
                %+% ", freq=2yr, dur=1yr"
                %+% ", 50-80-100% G-B-R") 
                ,titlesize=16 
                ,xlabel="sector half-life (megahours)"
                ,ylabel="percent permanent document losses"
                ,labelsize=14
                ) 

 plot(p)   
 fnPlotMakeFile(p, "Shock_compare_cop5_freq2yr_dur1yr_span3_50-80-100.png")

 
 
 