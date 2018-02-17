# PlotUtil.r

# Helper functions to make using ggplot slightly less obscure --
#  at the cost of passing way too many arguments to these functions.

source("./DataUtil.r")
library(ggplot2)


# f n P l o t B e g i n 
#fnPlotBegin <- function(dat, xcol, ycol) {
#    gp <- ggplot(data=trows,aes(x=xcol, y=ycol)) 
fnPlotBegin <- function(dat=NULL, xcol=NULL, ycol=NULL) {
#fnPlotBegin <- function() {
    if (is.null(dat))
    {    gp <- ggplot()
    } else
    {    gp <- ggplot(data=dat, mapping=aes(x=xcol, y=ycol))
    }
    return(gp)
}


# f n P l o t A d d L i n e 
fnPlotAddLine <- function(gp=NULL, dat=NULL, xcol=NULL, ycol=NULL, dotcolor, dotsize, dotshape, 
                        linecolor, linesize, lineshape) {
    if (is.null(gp)) {print("ERROR: missing first argument = plot in progress")}
    else {if (debugprint) cat("enter addline\n")}
    
    gp <- gp + 
            geom_point(data=dat, mapping=aes(x=xcol, y=ycol), 
                    color=dotcolor, size=dotsize, shape=dotshape) +
            geom_line(data=dat, aes(x=xcol, y=ycol), 
                    linetype=lineshape, color=linecolor, size=linesize)
    if (debugprint) cat("exit addline\n")
    return(gp)
}


# f n P l o t L o g S c a l e s 
fnPlotLogScales <- function(gp, x=NULL, y=NULL) {
    if (is.null(gp)) {print("ERROR: missing first argument = plot in progress")}
    if (!is.null(x)) {
        gp <- gp + scale_x_log10() + annotation_logticks()
    }
    if (!is.null(y)) {
        gp <- gp + scale_y_log10() + annotation_logticks()
    }
    return(gp)
}


# f n P l o t T i t l e s 
fnPlotTitles <- function(gp, titleline, titlesize=22, xlabel, ylabel, 
                    labelsize=18) {
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


