# dsplots-01.r  size-life comparisons
# RBLandau 20151016
# Using the basic R plotting functions, do a few graphs
#  


ds <- data.frame(read.table("DocsizeVsLifetime-Combined.prn",header=TRUE))
safelog <- function(x){return(log10(x+1)) }
safe    <- function(x){return(x+1)}

# Docsize = 5
png("dslife5.png",width=800,height=450,pointsize=16)
plot(ds$lifetime,ds$lost5,type="b",log="xy",pch=16,
    ylab="log permanent losses out of 10000 docs",
    xlab="log sector lifetime (megahours)",
    main="DocSize = 5 MB, permanent losses vs lifetime"
)
#points(ds$lifetime,ds$lost50,type="b",col="red",pch=16)
#points(ds$lifetime,ds$lost500,type="b",col="blue",pch=16)
#points(ds$lifetime,ds$lost5000,type="b",col="green",pch=16)
legend(300,2000,c("5 MB","50 MB","500 MB", "5000 MB"),col=c("black","red","blue","green"),pch=c(16,16,16,16))
dev.off()

# Docsize = 50
png("dslife50.png",width=800,height=450,pointsize=16)
#plot(ds$lifetime,ds$lost5,type="b",log="xy",pch=16)
plot(ds$lifetime*10,ds$lost50,type="b",log="xy",col="red",pch=16,
    ylab="log permanent losses out of 10000 docs",
    xlab="log sector lifetime (megahours)",
    main="DocSize = 50 MB"
)
#points(ds$lifetime,ds$lost500,type="b",col="blue",pch=16)
#points(ds$lifetime,ds$lost5000,type="b",col="green",pch=16)
legend(300*10,2000,c("5 MB","50 MB","500 MB", "5000 MB"),col=c("black","red","blue","green"),pch=c(16,16,16,16))
dev.off()

# Docsize = 500
png("dslife500.png",width=800,height=450,pointsize=16)
#plot(ds$lifetime,ds$lost5,type="b",log="xy",pch=16)
#points(ds$lifetime,ds$lost50,type="b",col="red",pch=16)
plot(ds$lifetime*100,ds$lost500,type="b",log="xy",col="blue",pch=16,
    ylab="log permanent losses out of 10000 docs",
    xlab="log sector lifetime (megahours)",
    main="DocSize = 500 MB"
)
#points(ds$lifetime,ds$lost5000,type="b",col="green",pch=16)
legend(300*100,2000,c("5 MB","50 MB","500 MB", "5000 MB"),col=c("black","red","blue","green"),pch=c(16,16,16,16))
dev.off()

# Docsize = 5000
png("dslife5000.png",width=800,height=450,pointsize=16)
#plot(ds$lifetime,ds$lost5,type="b",log="xy",pch=16)
#points(ds$lifetime,ds$lost50,type="b",col="red",pch=16)
#points(ds$lifetime,ds$lost500,type="b",col="blue",pch=16)
plot(ds$lifetime*1000,ds$lost5000,type="b",log="xy",col="green",pch=16,
    ylab="log permanent losses out of 10000 docs",
    xlab="log sector lifetime (megahours)",
    main="DocSize = 5000 MB"
)
legend(300*1000,2000,c("5 MB","50 MB","500 MB", "5000 MB"),col=c("black","red","blue","green"),pch=c(16,16,16,16))
dev.off()

# Docsize = all of them superimposed
png("dslifeall.png",width=800,height=450,pointsize=16)
plot(ds$lifetime,ds$lost5,type="b",log="xy",pch=16,
    ylab="log permanent losses out of 10000 docs",
    xlab="log sector lifetime (megahours)",
    main="DocSize comparison, all overlaid on scaled lifetimes: \n 10x larger file with 10x longer lifetime yields same results"
)
points(ds$lifetime,ds$lost50,type="b",col="red",pch=16)
points(ds$lifetime,ds$lost500,type="b",col="blue",pch=16)
points(ds$lifetime,ds$lost5000,type="b",col="green",pch=16)
legend(300,2000,c("5 MB","50 MB","500 MB", "5000 MB"),col=c("black","red","blue","green"),pch=c(16,16,16,16))
dev.off()


# Old leftovers we use for cribbing example code that works.
if (0)
{
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
}

#END
