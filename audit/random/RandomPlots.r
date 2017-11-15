# RandomPlots.r
#               RBLandau 20171112

# f n P l o t R a n d o m M o n t h l y V s B a s e l i n e 
fnPlotRandomMonthlyVsBaseline <- function(nCopies){

    #  M O N T H L Y  ( M )
    trows <- fnSelectCopies(dat.auditrandom.monthly, nCopies)
    gp <- ggplot(data=trows, aes(trows,x=(lifem),y=safe(mdmlosspct))) 
    gp <- gp +  
            scale_x_continuous() + scale_y_continuous() + 
            scale_x_log10("sector half-life (megahours) A") + 
            scale_y_log10("% permanent document losses B") +
            ylim(0,5) + 
            annotation_logticks()

    gp <- gp + 
            aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
            geom_point(data=trows, 
                color="red", size=5, shape='M') +
            geom_line(data=trows, 
                linetype="dashed", color="blue", size=1)

    # B A S E L I N E   T O T A L   A U D I T  ( number ) 
    trows <- fnSelectCopies(dat.auditbaseline, nCopies)
    gp <- gp +  aes(trows, x=(lifem), y=(safe(mdmlosspct))) 
    gp <- gp + 
            scale_x_continuous() + scale_y_continuous() + 
            scale_x_log10("sector half-life (megahours) C") + 
            scale_y_log10("% permanent document losses D") + 
            ylim(0,5) + 
            annotation_logticks()

    gp <- gp + 
            aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
            geom_point(data=trows, 
                color="red", size=5, shape=(48+nCopies)) +
            geom_line(data=trows, 
                linetype="dashed", color="blue", size=1)

    gp <- gp + ggtitle(sprintf("(copies = %s)",nCopies) 
                        %+% " With random auditing,"
                        %+% "\nsampling WITH replacement," 
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

    #  M O N T H L Y  ( M )
    trows <- fnSelectCopies(dat.auditrandom.monthly, nCopies)
    gp <- ggplot(data=trows,aes(trows, x=(lifem), y=(safe(mdmlosspct)))) 
    gp <- gp + 
            scale_x_log10("sector half-life (megahours) G") + 
            scale_y_log10("% permanent document losses H") +
            ylim(0,5) + 
            annotation_logticks()

    gp <- gp + 
            aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
            geom_point(data=trows, 
                color="red", size=5, shape='M') +
            geom_line(data=trows, 
                linetype="dashed", color="blue", size=1)

    # Q U A R T E R L Y  ( Q ) 
    trows <- fnSelectCopies(dat.auditrandom.quarterly, nCopies)
    gp <- gp +  aes(trows, x=(lifem), y=(safe(mdmlosspct))) 
    gp <- gp + 
            scale_x_log10("sector half-life (megahours) I") + 
            scale_y_log10("% permanent document losses J") +
            annotation_logticks()

    gp <- gp + 
            aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
            geom_point(data=trows, 
                color="red", size=5, shape='Q') +
            geom_line(data=trows, 
                linetype="dashed", color="blue", size=1)

    # S E M I A N N U A L L Y  ( S ) 
    trows <- fnSelectCopies(dat.auditrandom.semiannually, nCopies)
    gp <- gp +  aes(trows, x=(lifem), y=(safe(mdmlosspct))) 
    gp <- gp + 
            scale_x_log10("sector half-life (megahours) K") + 
            scale_y_log10("% permanent document losses L") +
            annotation_logticks()

    gp <- gp + 
            aes(trows, x=(lifem), y=(safe(mdmlosspct))) +
            geom_point(data=trows, 
                color="red", size=5, shape='S') +
            geom_line(data=trows, 
                linetype="dashed", color="blue", size=1)

    gp <- gp + ggtitle(sprintf("(copies = %s)",nCopies) 
                        %+% " With random auditing,"
                        %+% "\nsampling WITH replacement," 
                        %+% "\nmore frequent small segments are actually worse")
    gp <- gp + xlab("sector half-life (megahours)")
    gp <- gp + ylab("% permanent document losses")
    gp <- gp + theme(
                axis.text=element_text(size=12),
                axis.title=element_text(size=18),
                plot.title=element_text(size=20,face="bold"),
                panel.border = element_rect(color = "black", fill=NA, size=1)
                )

    return(gp)
}



#END
