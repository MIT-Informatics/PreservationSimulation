# PlotUtil.r

# Helper functions to make using ggplot slightly less obscure --
#  at the cost of passing way too many arguments to these functions.

source("../common/DataUtil.r")
library(ggplot2)


# Constants for ggplot point shapes.
point.DOT       <- 16
point.SQUARE    <- 15
point.TRIANGLE  <- 17
point.DIAMOND   <- 18
point.HDOT      <- 0
point.HSQUARE   <- 1
point.HTRIANGLE <- 2
point.HDIAMOND  <- 5


# f n P l o t B e g i n 
# WARNING: DO NOT USE until we figure out why it doesn't work as expected.
# Us the naked ggplot() call for the time being.  
#fnPlotBegin <- function(dat, xcol, ycol) {
#    gp <- ggplot(data=trows,aes(x=xcol, y=ycol)) 
fnPlotBegin <- function(dat=NULL, xcol=NULL, ycol=NULL, context=NULL) {
    gp <- ggplot(data=dat, mapping=aes(x=xcol, y=ycol))
    return(gp)
}


# f n P l o t A d d L i n e 
fnPlotAddLine <- function(gp=NULL, dat=NULL, 
                        dotcolor="black", dotsize=2, dotshape=point.DOT, 
                        linecolor="black", linesize=2, lineshape) {
    if (is.null(gp)) {print("ERROR: missing first argument = plot in progress")}
    else {if (debugprint) cat("enter addline\n")}
    
    gp <- gp + 
            geom_line(data=dat, 
                    color=linecolor, size=linesize, linetype=lineshape
                    , show.legend=TRUE) +
            geom_point(data=dat, 
                    color=dotcolor, size=dotsize, shape=dotshape
                    , show.legend=TRUE) 
    if (debugprint) cat("exit addline\n")
    return(gp)
}


# f n P l o t L o g S c a l e s 
# Example: fnPlotLogScales(x="YES", xbreaks=c(2,3,5,10,100,1000))
fnPlotLogScales <- function(gp, x=NULL, y=NULL, xbreaks=NULL, ybreaks=NULL) {
    if (is.null(gp)) {print("ERROR: missing first argument = plot in progress")}
    if (!is.null(x)) {
        if (!is.null(xbreaks)){
            gp <- gp + scale_x_log10(breaks=xbreaks) + annotation_logticks()
        }else{
            gp <- gp + scale_x_log10() + annotation_logticks()
        }
    }
    if (!is.null(y)) {
        if (!is.null(ybreaks)){
            gp <- gp + scale_y_log10(breaks=ybreaks) + annotation_logticks()
        }else{
            gp <- gp + scale_y_log10() + annotation_logticks()
        }
    }
    return(gp)
}


# f n P l o t T i t l e s 
fnPlotTitles <- function(gp, titleline, titlesize=22, 
                    xlabel="XXX", ylabel="YYY", labelsize=18) {
    if (is.null(gp)) {print("ERROR: missing first argument = plot in progress")}
    gp <- gp + labs(title=titleline, x=xlabel, y=ylabel)
    gp <- gp + theme(
                axis.text=element_text(size=12),
                axis.title=element_text(size=labelsize),
                plot.title=element_text(size=titlesize,face="bold"),
                panel.border = element_rect(color = "black", fill=NA, size=1)
                )
    return(gp)
}


# f n P l o t P e r c e n t L i n e 
# Seems a bizarre way to do this, to create a fake data point
#  and then plot it using text centered there instead of just a dot.  
fnPlotPercentLine <- function(gp, 
                    xloc=log10(1.7), yloc=log10(1.2), 
                    labeltext="1%", labelsize=4, 
                    percent=1.0){
    gp <- gp + geom_hline(yintercept=percent, linetype="dashed")
    gp <- gp + geom_text(x=xloc, y=yloc, label=labeltext, size=labelsize, 
                    fontface="plain", family="mono")
    return(gp)
}


# f n P l o t M a k e F i l e 
fnPlotMakeFile <- function(plotname, sFilename, sSize="4x3") {
# Capture graph in 16:9 aspect and reasonable size.
    if (is.null(plotname)) {print("ERROR: missing first argument = plot in progress")}
    if (sSize == "large")
        { png(sFilename,width=1600,height=900) }
    else if (sSize == "mediumlarge")
        { png(sFilename,width=1200,height=675) }
    else if (sSize == "mediumsmall")
        { png(sFilename,width=960,height=540) }
    else if (sSize == "4x3")
        { png(sFilename,width=800,height=600) } 
    else 
        { png(sFilename,width=800,height=450) } 
      print(plotname)
      dev.off()
} #endfunction



