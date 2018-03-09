# PlotUtil.r

# Helper functions to make using ggplot slightly less obscure --
#  at the cost of passing way too many arguments to these functions.

source("./DataUtil.r")
library(ggplot2)

# f n P l o t B e g i n 
#fnPlotBegin <- function(dat, xcol, ycol) {
#    gp <- ggplot(data=trows,aes(x=xcol, y=ycol)) 
fnPlotBegin <- function(dat, xcol, ycol) {
    gp <- ggplot(data=dat, mapping=aes(x=(xcol), y=(ycol)))
    return(gp)
}

# f n P l o t A d d L i n e 
fnPlotAddLine <- function(gp, dat, xcol, ycol, dotcolor, dotsize, dotshape, 
                        linecolor, linesize, lineshape) {
    if (is.null(gp)) {print("ERROR: missing first argument = plot in progress")}
    gp <- gp + 
#            aes(data=dat, x=(xcol), y=(ycol)) +
            aes(dat, x=(xcol), y=(ycol)) +
            geom_point(data=dat, aes(x=(xcol), y=(ycol)), 
#            geom_point(dat, aes(x=(xcol), y=(ycol)), 
                    color=dotcolor, size=dotsize, shape=dotshape) +
            geom_line(data=dat, aes(x=(xcol), y=(ycol)), 
                    linetype=lineshape, color=linecolor, size=linesize)
    return(gp)
}

# f n P l o t L o g S c a l e X 
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
fnPlotTitles <- function(gp, titleline, titlesize=22, xlabel, ylabel, labelsize=18) {
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
fnPlotMakeFile <- function(plotname, sFilename, sSize="small") {
# Capture graph in 16:9 aspect and reasonable size.
    if (is.null(plotname)) {print("ERROR: missing first argument = plot in progress")}
    if (sSize == "large")
        { png(sFilename,width=1600,height=900) }
    else if (sSize == "medium")
        { png(sFilename,width=1200,height=675) }
    else
        { png(sFilename,width=800,height=450) } 
      print(plotname)
      dev.off()
} #endfunction


if (0){
# TEST ONLY
nCopies <- 1
trows <- fnSelectCopies(dat.noaudit, nCopies)
#g <- fnPlotBegin(dat=dat.noaudit, xcol=dat.noaudit$lifem, ycol=safe(dat.noaudit$mdmlosspct))
g <- fnPlotBegin(dat=trows, xcol=trows$lifem, ycol=safe(trows$mdmlosspct))
#g <- fnPlotBegin(dat=trows, xcol=lifem, ycol=safe(mdmlosspct))
g <- fnPlotLogScales(g, x="yes", y="yes")
g <- fnPlotAddLine(g, dat=trows, xcol=lifem, ycol=safe(mdmlosspct), 
            dotcolor="red", dotsize=5, dotshape=(48+nCopies), 
            linecolor="black", linesize=1, lineshape="dashed")
g <- fnPlotTitles(g, titleline="Unaudited Permanent Losses", 
                xlabel="sector half-life (megahours)", 
                ylabel="percentage of collection permanently lost")
nCopies <- 2; trows <- fnSelectCopies(dat.noaudit, nCopies)
g <- fnPlotAddLine(g, dat=trows, xcol=lifem, ycol=safe(mdmlosspct), 
            dotcolor="red", dotsize=5, dotshape=(48+nCopies), 
            linecolor="black", linesize=1, lineshape="dashed")
nCopies <- 3; trows <- fnSelectCopies(dat.noaudit, nCopies)
g <- fnPlotAddLine(g, dat=trows, xcol=lifem, ycol=safe(mdmlosspct), 
            dotcolor="red", dotsize=5, dotshape=(48+nCopies), 
            linecolor="black", linesize=1, lineshape="dashed")
nCopies <- 5; trows <- fnSelectCopies(dat.noaudit, nCopies)
g <- fnPlotAddLine(g, dat=trows, xcol=lifem, ycol=safe(mdmlosspct), 
            dotcolor="red", dotsize=5, dotshape=(48+nCopies), 
            linecolor="black", linesize=1, lineshape="dashed")
nCopies <- 9; trows <- fnSelectCopies(dat.noaudit, nCopies)
g <- fnPlotAddLine(g, dat=trows, xcol=lifem, ycol=safe(mdmlosspct), 
            dotcolor="red", dotsize=5, dotshape=(48+nCopies), 
            linecolor="black", linesize=1, lineshape="dashed")

plot(g)
}

