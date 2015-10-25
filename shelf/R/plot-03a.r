# plot-03.r
# RBLandau  20150922
# revised   20151025
# Using the basic R plotting functions, do a few graphs
#  for the NDSA meeting.

nDocs <- 10000
dall <- data.frame(read.table("dataforndsa-00.txt",header=TRUE))
d <- dall[dall$lifem>=10,]
c1 <- d[d$copies==1,]
c2 <- d[d$copies==2,]
c3 <- d[d$copies==3,]
c4 <- d[d$copies==4,]
c5 <- d[d$copies==5,]
safelog <- function(x){return(log10(x+1)) }
safe    <- function(x){return(x+1)}
c1p <- c1 / nDocs * 100
c2p <- c2 / nDocs * 100
c3p <- c3 / nDocs * 100
c4p <- c4 / nDocs * 100
c5p <- c5 / nDocs * 100


# C1a
png("c1a.png",width=860,height=452,pointsize=16)
plot(c1$lifem,safe(c1p$loss.a0),type="b",lty="dashed",log="xy",pch=16,
     ylab="permanent losses (percentage of collection)",
     xlab="sector lifetime (megahours)",
     main="For copies = 1, \nlosses are unacceptable (auditing can't help)")
#points(c2$lifem,safe(c2$loss.ay),type="b",pch=16,col="red")
#points(c2$lifem,safe(c2$loss.aq),type="b",pch=16,col="blue")
#legend(300,700,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(35,25,"No auditing",col="black")
#text(14,350,"Annual audit",col="red")
#text(13,40,"Quarterly audit",col="blue")
dev.off()

# C1aNoLog
png("c1anolog.png",width=860,height=452,pointsize=16)
plot(c1$lifem,safe(c1p$loss.a0),type="b",lty="dashed",pch=16,
     ylab="permanent losses (percentage of collection)",
     xlab="sector lifetime (megahours)",
     main="For copies = 1, \nlosses are unacceptable (auditing can't help)")
#points(c2$lifem,safe(c2$loss.ay),type="b",pch=16,col="red")
#points(c2$lifem,safe(c2$loss.aq),type="b",pch=16,col="blue")
#legend(300,700,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(80,35,"No auditing",col="black")
#text(14,350,"Annual audit",col="red")
#text(13,40,"Quarterly audit",col="blue")
dev.off()

# C2a
png("c2a.png",width=860,height=452,pointsize=16)
plot(c2$lifem,safe(c2p$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses (percentage of collection)",
    xlab="sector lifetime (megahours)",
    main="For copies = 2, \nlosses decline a lot with increased auditing")
points(c2$lifem,safe(c2p$loss.ay),type="b",pch=16,col="red")
points(c2$lifem,safe(c2p$loss.aq),type="b",pch=16,col="blue")
legend(300,700,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(20,10,"No audit",col="black")
text(18,3,"Annual audit",col="red")
text(12,2,"Quarterly audit",col="blue")
dev.off()

# C3a
png("c3a.png",width=860,height=452,pointsize=16)
plot(c3$lifem,safe(c3p$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses (percentage of collection)",
    xlab="sector lifetime (megahours)",
    main="For copies = 3, \nlosses decline even more with increased auditing")
points((c3$lifem),safe(c3p$loss.ay),type="b",pch=16,col="red")
points((c3$lifem),safe(c3p$loss.aq),type="b",pch=16,col="blue")
legend(300,300,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(15,6,"No audit",col="black")
text(12,1.4,"Annual audit",col="red")
text(12,1.2,"Quarterly audit",col="blue")
dev.off()

# C4a
png("c4a.png",width=860,height=452,pointsize=16)
plot(c4$lifem,safe(c4p$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses (percentage of collection)",
    xlab="sector lifetime (megahours)",
    main="For copies = 4, \nlosses decline only very slightly with increased auditing")
points(c4$lifem,safe(c4p$loss.ay),type="b",pch=16,col="red")
points(c4$lifem,safe(c4p$loss.aq),type="b",pch=16,col="blue")
legend(300,100,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(20,3,"No audit",col="black")
text(12,1.2,"Annual audit",col="red")
text(12,1.1,"Quarterly audit",col="blue")
dev.off()

# C4aNoPct
png("c4anopct.png",width=860,height=452,pointsize=16)
plot(c4$lifem,safe(c4$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses out of 10,000 docs",
    xlab="sector lifetime (megahours)",
    main="For copies = 4, \nlosses decline only very slightly with increased auditing")
points(c4$lifem,safe(c4p$loss.ay),type="b",pch=16,col="red")
points(c4$lifem,safe(c4p$loss.aq),type="b",pch=16,col="blue")
legend(300,100,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(20,100,"No audit",col="black")
text(12,2.0,"Annual audit",col="red")
text(12,1.5,"Quarterly audit",col="blue")
dev.off()

# C5a
png("c5a.png",width=860,height=452,pointsize=16)
plot(c5$lifem,safe(c5p$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses (percentage of collection)",
    xlab="sector lifetime (megahours)",
    main="For copies = 5, \nlosses are probably negligible with any auditing")
points(c5$lifem,safe(c5p$loss.aq),type="b",pch=16,col="blue")
points(c5$lifem,safe(c5p$loss.ay),type="b",pch=16,col="red")
legend(300,100,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(14,1.8,"No audit",col="black")
text(12,1.1,"Annual audit or",col="red")
text(12,1.05,"Quarterly audit",col="blue")
dev.off()

# C5aNoPct
png("c5anopct.png",width=860,height=452,pointsize=16)
plot(c5$lifem,safe(c5$loss.a0),type="b",lty="dashed",log="xy",pch=16,
    ylab="permanent losses out of 10,000 docs",
    xlab="sector lifetime (megahours)",
    main="For copies = 5, \nlosses are probably negligible with any auditing")
points(c5$lifem,safe(c5$loss.aq),type="b",pch=16,col="blue")
points(c5$lifem,safe(c5$loss.ay),type="b",pch=16,col="red")
legend(300,100,c("No audit","Annual audit","Quarterly audit"),col=c("black","red","blue"),pch=c(16,16,16))
text(20,50,"No audit",col="black")
text(12.5,2.0,"Annual audit or",col="red")
text(12,1.4,"Quarterly audit",col="blue")
dev.off()


#END
