# plot-01.r
# RBLandau 20150922
# Using the basic R plotting functions, do a few graphs
#  for the NDSA meeting.


dall <- data.frame(read.table("dataforndsa-00.txt",header=TRUE))
d <- dall[dall$lifem>=10,]
c1 <- d[d$copies==1,]
c2 <- d[d$copies==2,]
c3 <- d[d$copies==3,]
c4 <- d[d$copies==4,]
c5 <- d[d$copies==5,]
safelog <- function(x){return(log10(x+1)) }
safe    <- function(x){return(x+1)}

# C2
png("c2.png",width=860,height=452,pointsize=16)
plot(c2$lifem,safe(c2$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses out of 10000 docs",
    xlab="sector lifetime (megahours)",
    main="For copies = 2, \nlosses decline a lot with increased auditing")
points(c2$lifem,safe(c2$loss.ay),type="b",pch=16,col="red")
points(c2$lifem,safe(c2$loss.aq),type="b",pch=16,col="blue")
legend(300,700,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(18,1500,"No audit",col="black")
text(14,350,"Annual audit",col="red")
text(13,40,"Quarterly audit",col="blue")
dev.off()

# C3
png("c3.png",width=860,height=452,pointsize=16)
plot(c3$lifem,safe(c3$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses out of 10000 docs",
    xlab="sector lifetime (megahours)",
    main="For copies = 3, \nlosses decline slightly with increased auditing")
points((c3$lifem),safe(c3$loss.ay),type="b",pch=16,col="red")
points((c3$lifem),safe(c3$loss.aq),type="b",pch=16,col="blue")
legend(300,300,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(15,500,"No audit",col="black")
text(15,15,"Annual audit",col="red")
text(12,1.4,"Quarterly audit",col="blue")
dev.off()

# C4
png("c4.png",width=860,height=452,pointsize=16)
plot(c4$lifem,safe(c4$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses out of 10000 docs",
    xlab="sector lifetime (megahours)",
    main="For copies = 4, \nlosses decline only very slightly with increased auditing")
points(c4$lifem,safe(c4$loss.ay),type="b",pch=16,col="red")
points(c4$lifem,safe(c4$loss.aq),type="b",pch=16,col="blue")
legend(300,100,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(15,210,"No audit",col="black")
text(14,2.4,"Annual audit",col="red")
text(12,1.4,"Quarterly audit",col="blue")
dev.off()

# C5
png("c5.png",width=860,height=452,pointsize=16)
plot(c5$lifem,safe(c5$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses out of 10000 docs",
    xlab="sector lifetime (megahours)",
    main="For copies = 5, \nlosses are probably negligible with any auditing")
points(c5$lifem,safe(c5$loss.aq),type="b",pch=16,col="blue")
points(c5$lifem,safe(c5$loss.ay),type="b",pch=16,col="red")
legend(300,100,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(14,90,"No audit",col="black")
text(12,1.8,"Annual audit or",col="red")
text(12,1.4,"Quarterly audit",col="blue")
dev.off()


#END
