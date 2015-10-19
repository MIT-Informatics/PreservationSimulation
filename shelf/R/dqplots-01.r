dq = data.frame(read.csv("QuarterlySystematicVsTotalAudits-01.csv", header=TRUE))

safelog <- function(x){return(log10(x+1)) }
safe    <- function(x){return(x+1)}

png("dqsegmentvsuniform.png",width=800,height=450,pointsize=16)
plot(dq$lifem, safe(dq$c3unif), log="xy", type="b", pch=16, col="red",
    ylab="log permanent losses out of 10000 docs",
    xlab="log sector lifetime (megahours)",
    main="Auditing random selection each quarter is not as effective\n as auditing a fixed one-fourth of the collection each quarter"
)
points(dq$lifem,safe(dq$c3qtly), type="b", pch=16, col="green")
points(dq$lifem,safe(dq$c3annual), type="b", pch=16, col="black")
legend(150,700,c("Quarterly random 1/4th","Quarterly total audit","Annual total"), col=c("red","green","black"),pch=c(16,16,16))
dev.off()



#END
