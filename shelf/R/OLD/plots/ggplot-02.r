# ggplot-01.r
# RBLandau 20150923
# Try ggplot2 to see if it makes prettier pictures than vanilla plot.

library(ggplot2)

dall <- data.frame(read.table("dataforndsa-00.txt",header=TRUE))
d <- dall[dall$lifem>=10,]
c1 <- d[d$copies==1,]
c2 <- d[d$copies==2,]
c3 <- d[d$copies==3,]
c4 <- d[d$copies==4,]
c5 <- d[d$copies==5,]
safelog <- function(x){return(log10(x+1)) }
safe    <- function(x){return(x+0.5)}


#qplot(x=lifem,y=loss.a0,data=c3) + scale_x_log10() + scale_y_log10() + annotation_logticks()

# Construct graph with one or more data lines, labels, etc.
makeplot <- function(ncopies,cdata,titlelines,a0x,a0y,ayx,ayy,aqx,aqy) {
    p <- ggplot(data=cdata,aes(x=lifem,y=safe(loss.a0)))
    p <- p + scale_x_log10() + scale_y_log10()
    p <- p + annotation_logticks()
    # Axis labels and title.
    p <- p + labs(
            x="sector lifetime (megahours)", 
            y="permanent document losses from 10,000 docs", 
            title=titlelines
            )
    p <- p + theme(
            axis.text=element_text(size=12),
            axis.title=element_text(size=18),
            plot.title=element_text(size=22,face="bold"),
            panel.border = element_rect(color = "black", fill=NA, size=1)
            )
    # Unaudited points.
    p <- p+geom_point(color="black",size=4) + geom_line(linetype="dashed",color="black",size=1)
    if (ncopies > 1)
    {
        # Quarterly audit points
        p <- p+geom_point(data=cdata,aes(x=lifem,y=safe(loss.aq)),color="blue",size=4)
        p <- p+geom_line(data=cdata,aes(x=lifem,y=safe(loss.aq)),color="blue",size=1)
        # Annual audit points
        p <- p+geom_point(data=cdata,aes(x=lifem,y=safe(loss.ay)),color="red",size=4)
        p <- p+geom_line(data=cdata,aes(x=lifem,y=safe(loss.ay)),color="red",size=1)
    } #endif ncopies>1
    # Annotations
    p <- p+annotate("text",x=a0x,y=a0y,label="Unaudited",size=7)
    if (ncopies > 1)
    {
        p <- p+annotate("text",x=ayx,y=ayy,label="Annual audit",color="red",size=7)
        p <- p+annotate("text",x=aqx,y=aqy,label="Quarterly audit",color="blue",size=7)
        p <- p+annotate("text",x=500,y=0.7,label="(zero failures)")
    } #endif ncopies>1
    gplot <- p
    return(gplot)
} #endfunction

# Capture graph in 16:9 aspect and reasonable size.
makefile <- function(plotname,sFilename) {
  png(sFilename,width=800,height=450)
  print(plotname)
  dev.off()
} #endfunction


# C1
g1plot <- makeplot(1,c1,"Copies = 1 \n All losses are permanent losses", 35,500,0,0,0,0)
makefile(g1plot,"g1.png")

# C2
g2plot <- makeplot(2,c2,"Copies = 2 \n Losses decline a lot with increased auditing", 35,500,19,200,15,9)
makefile(g2plot,"g2.png")

# C3
g3plot <- makeplot(3,c3,"Copies = 3 \n Losses decline slightly with increased auditing", 21,300,16,12,13,1.0)
makefile(g3plot,"g3.png")

# C4
g4plot <- makeplot(4,c4,"Copies = 4 \n Losses decline only very slightly with increased auditing", 20,100,16,1.8,13,0.8)
makefile(g4plot,"g4.png")

# C5
g5plot <- makeplot(5,c5,"Copies = 5 \n Losses are probably negligible with any auditing", 21,20,12,1.2,13,0.8)
makefile(g5plot,"g5.png")


#END
