# RandomPlots.r
#               RBLandau 20171112


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



#END
