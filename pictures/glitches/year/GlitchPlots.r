# GlitchPlots.r
#               RBLandau 20180130

if (debugprint) cat("Entering GlitchPlots.r\n")
source("../../common/PlotUtil.r")
if (debugprint) cat("got common/PlotUtil.r\n")

# f n P l o t G l i t c h 1 
# Simple line plot for copies=3,4,5 (sorry, that's built in).
fnPlotGlitch1 <- function(trows, nFreq, nDuration, nSpan=1, nImpact) {
    p <- ggplot(trows, aes(x=lifem, y=safe(mdmlosspct), color=factor(copies)))

    p <- p + geom_line(data=trows, size=2)
    p <- p + geom_point(data=trows, shape=(point.SQUARE), size=5)
    p <- fnPlotLogScales(p, x="YES", y="YES"
            , xbreaks=c(2,5,10,50,100,1000)
            , ybreaks=c(0.01,0.1,1)
            )
    p <- p + scale_colour_discrete(name="Number \nof Copies", labels=c("3","4","5"))
    p <- p + geom_hline(yintercept=1.0, linetype="dashed")
    
    sParams <- sprintf("freq(hl)=%shr, len=%shr, impact=%s%%", 
                    nFreq, nDuration, nImpact)
    p <- p + ggtitle("Glitches " %+% sParams)
    p <- p + xlab("1MB sector half-life (megahours)"
                %+% "                  (lower error rate ===>)"
                )
    p <- p + ylab("permanent document losses (%)")
    p <- p + theme(
            axis.text=element_text(size=10),
            axis.title=element_text(size=14),
            plot.title=element_text(size=16,face="bold"),
            panel.border = element_rect(color = "black", fill=NA, size=1)
            )
    p <- p + theme(legend.position=c(1.0,0.8)
                , legend.justification=c(1.1,0.35)
                )

    plot(p)
    return(p)
}



if(0){

# f n P l o t S h o c k 3 
# Simple line plot for impact=50,80,100 (sorry, that's built in).
fnPlotShock3 <- function(trows, nFreq, nDuration, nSpan, nCopies) {
    p <- ggplot(trows, aes(x=lifem, y=safe(mdmlosspct), color=factor(shockimpact)))

    p <- p + geom_line(data=trows, size=2)
    p <- p + geom_point(data=trows, shape=(16), size=5)
    p <- p + scale_x_log10() + scale_y_log10() + annotation_logticks()
    p <- p + scale_colour_discrete(name="Impact\n(percent)", labels=c("50","80","100"))
    p <- p + geom_hline(yintercept=1.0, linetype="dashed")
    
    sParams <- sprintf("freq(hl)=%syr, len=%smo, span=%s, copies=%s", 
                    nFreq, nDuration, nSpan, nCopies)
    p <- p + ggtitle("Shocks " %+% sParams)
    p <- p + xlab("sector half-life (megahours)")
    p <- p + ylab("percent permanent document losses")
    p <- p + theme(
            axis.text=element_text(size=10),
            axis.title=element_text(size=14),
            plot.title=element_text(size=16,face="bold"),
            panel.border = element_rect(color = "black", fill=NA, size=1)
            )

    plot(p)
    return(p)
}


# f n P l o t S h o c k 4 
# Simple line plot for impact=50,80,100 (sorry, that's built in).
# nCopies is in the data subset we are given, usually 5.
# Try using the pieces/parts PlotUtil functions.
fnPlotShock4 <- function(trows, nCopies) {

    trows50 <- trows[trows$shockimpact==50,]
    trows80 <- trows[trows$shockimpact==80,]
    trows100 <- trows[trows$shockimpact==100,]

    p <- fnPlotBegin(data=NULL, x=trows50$nLifem, y=trows50$mdmlosspct)
    cat("begin done.\n")

    p <- fnPlotAddLine(p, data=trows50, #x=trows50$nLifem, y=trows50$mdmlosspct, 
                dotcolor="blue", dotsize=3, dotshape=16, 
                linecolor="blue", linesize=2, lineshape="solid")

    plot(p)

#    p <- fnPlotAddLine(p, trows80, trows80$nLifem, trows80$mdmlosspct, 
#                dotcolor="green", dotsize=3, dotshape=16, 
#                linecolor="green", linesize=2, lineshape="solid")
#    p <- fnPlotAddLine(p, trows100, trows100$nLifem, trows100$mdmlosspct, 
#                dotcolor="red", dotsize=3, dotshape=16, 
#                linecolor="red", linesize=2, lineshape="solid")

    p <- fnPlotLogScales(p, x='yes', y='yes')

#    p <- p + scale_colour_discrete(name="Impact\n(percent)", labels=c("50","80","100"))
    p <- p + geom_hline(yintercept=1.0, linetype="dashed")
    
    sParams <- sprintf("copies=%s", 
                    nCopies)

    p <- fnPlotTitles(p, title=("Shocks " %+% sParams), titlesize=16, 
                xlabel="sector half-life (megahours)", 
                ylabel="percent permanent document losses", 
                labelsize=14) 

#    p <- p + ggtitle("Shocks " %+% sParams)
#    p <- p + xlab("sector half-life (megahours)")
#    p <- p + ylab("percent permanent document losses")
#    p <- p + theme(
#            axis.text=element_text(size=10),
#            axis.title=element_text(size=14),
#            plot.title=element_text(size=16,face="bold"),
#            panel.border = element_rect(color = "black", fill=NA, size=1)
#            )


    return(p)
}


# f n P l o t R a n d o m M o n t h l y V s B a s e l i n e 
fnPlotRandomMonthlyVsBaseline <- function(nCopies){

    trows.m <- fnSelectCopies(dat.auditrandom.monthly, nCopies)
    trows.t <- fnSelectCopies(dat.auditbaseline, nCopies)
    lossmax.m <- max(trows.m$mdmlosspct)
    lossmax.t <- max(trows.t$mdmlosspct)
    lossmax <- max(lossmax.m, lossmax.t) + 0.5

    #  M O N T H L Y  ( M )
    gp <- ggplot(data=trows.m, aes(trows.m, x=(lifem), y=safe(mdmlosspct))) 
    gp <- gp +  
            scale_x_log10("sector half-life (megahours) A") + 
            scale_y_log10("% permanent document losses B") +
            ylim(0, lossmax) + 
            annotation_logticks()
    gp <- gp + 
            geom_point(data=trows.m, 
                color="red", size=5, shape='M') +
            geom_line(data=trows.m, 
                linetype="dashed", color="blue", size=1)

    # B A S E L I N E   T O T A L   A U D I T  ( number ) 
    gp <- gp +  aes(trows.t, x=(lifem), y=(safe(mdmlosspct))) 
    gp <- gp + 
            annotation_logticks()
    gp <- gp + 
            geom_point(data=trows.t, 
                color="red", size=5, shape=(48+nCopies)) +
            geom_line(data=trows.t, 
                linetype="dashed", color="blue", size=1)

    # I D E N T I F Y I N G   G I N G E R B R E A D 
    gp <- gp + ggtitle(sprintf("(copies = %s)",nCopies) 
                        %+% " With RANDOM auditing sampling WITH replacement,"
                        %+% "\ninstead of TOTAL auditing of collection," 
                        %+% "\nsome docs are missed entirely, increasing losses")
    gp <- gp + xlab("sector half-life (megahours) E")
    gp <- gp + ylab("% permanent document losses F")
    gp <- gp + theme(
                axis.text=element_text(size=12),
                axis.title=element_text(size=18),
                plot.title=element_text(size=20,face="bold"),
                panel.border = element_rect(color = "black", fill=NA, size=1)
                )

    return(gp)
}


# f n P l o t R a n d o m V a r i o u s S e g m e n t s 
fnPlotRandomVariousSegments <- function(nCopies){

    trows.m <- fnSelectCopies(dat.auditrandom.monthly, nCopies)
    trows.q <- fnSelectCopies(dat.auditrandom.quarterly, nCopies)
    trows.s <- fnSelectCopies(dat.auditrandom.semiannually, nCopies)
    lossmax.m <- max(trows.m$mdmlosspct)
    lossmax.q <- max(trows.q$mdmlosspct)
    lossmax.s <- max(trows.s$mdmlosspct)
    lossmax <- max(lossmax.m, lossmax.q, lossmax.s) + 0.5

    #  M O N T H L Y  ( M )
    gp <- ggplot(data=trows.m,aes(trows.m, x=(lifem), y=(safe(mdmlosspct)))) 
    gp <- gp + 
            scale_x_log10("sector half-life (megahours) G") + 
            scale_y_log10("% permanent document losses H") +
            ylim(0, lossmax) + 
            annotation_logticks()
    gp <- gp + 
            geom_point(data=trows.m, 
                color="red", size=5, shape='M') +
            geom_line(data=trows.m, 
                linetype="dashed", color="blue", size=1)

    # Q U A R T E R L Y  ( Q ) 
    gp <- gp +  aes(trows.q, x=(lifem), y=(safe(mdmlosspct))) 
    gp <- gp + 
            annotation_logticks()
    gp <- gp + 
            geom_point(data=trows.q, 
                color="red", size=5, shape='Q') +
            geom_line(data=trows.q, 
                linetype="dashed", color="blue", size=1)

    # S E M I A N N U A L L Y  ( S ) 
    gp <- gp +  aes(trows.s, x=(lifem), y=(safe(mdmlosspct))) 
    gp <- gp + 
            annotation_logticks()
    gp <- gp + 
            geom_point(data=trows.s, 
                color="red", size=5, shape='S') +
            geom_line(data=trows.s, 
                linetype="dashed", color="blue", size=1)

    # I D E N T I F Y I N G   G I N G E R B R E A D 
    gp <- gp + ggtitle(sprintf("(copies = %s)",nCopies) 
                        %+% " With RANDOM auditing"
                        %+% " sampling WITH replacement," 
                        %+% "\nmore frequent small segments are actually worse")
    gp <- gp + xlab("sector half-life (megahours) M")
    gp <- gp + ylab("% permanent document losses N")
    gp <- gp + theme(
                axis.text=element_text(size=12),
                axis.title=element_text(size=18),
                plot.title=element_text(size=20,face="bold"),
                panel.border = element_rect(color = "black", fill=NA, size=1)
                )

    return(gp)
}




}#endif0





# Edit history
# 20171211  RBL Copied from auditing in segments and modified.
#               Added shock plot routines. 
# 20180403  RBL Call fnPlotLogScales to set up breaks.
# 
# 

#END
