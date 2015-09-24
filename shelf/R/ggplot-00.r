# ggplot-00.r
# RBLandau 20150923


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

# C3
p <- ggplot(data=c3,aes(x=lifem,y=safe(loss.a0)))
p <- p + scale_x_log10() + scale_y_log10()
p <- p + annotation_logticks()
# Axis labels and title.
p <- p + labs(
        x="sector lifetime (megahours)", 
        y="permanent document losses from 10,000 docs", 
        title="Copies = 3\nLosses decline slightly with increased auditing"
        )
p <- p + theme(
        axis.text=element_text(size=12),
        axis.title=element_text(size=18),
        plot.title=element_text(size=26,face="bold"),
        panel.border = element_rect(color = "black", fill=NA, size=1)
        )
# Unaudited points.
p <- p+geom_point(color="black",size=4) + geom_line(linetype="dashed",color="black",size=1)
# Annual audit points
p <- p+geom_point(data=c3,aes(x=lifem,y=safe(loss.ay)),color="red",size=4)
p <- p+geom_line(data=c3,aes(x=lifem,y=safe(loss.ay)),color="red",size=1)
# Quarterly audit points
p <- p+geom_point(data=c3,aes(x=lifem,y=safe(loss.aq)),color="blue",size=4)
p <- p+geom_line(data=c3,aes(x=lifem,y=safe(loss.aq)),color="blue",size=1)
# Annotations
p <- p+annotate("text",x=21,y=300,label="Unaudited",size=7)
p <- p+annotate("text",x=16,y=12,label="Annual audit",color="red",size=7)
p <- p+annotate("text",x=13,y=1.0,label="Quarterly audit",color="blue",size=7)


# Show it.
p


