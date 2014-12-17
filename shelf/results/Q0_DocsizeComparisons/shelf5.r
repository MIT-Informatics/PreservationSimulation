# R script to set up PreservationSimulation/shelf data
# RBLandau 20140621

dat <- data.frame(read.table("s:/landau/python/dev/preservationsimulation/shelf/q0-alldata-medians-00.txt", header=TRUE))

# New dataset with only the interesting columns: docsize, berid, copies, lost
# because we don't want to aggregate anything else.
#datn = data.frame(dat$docsize,dat$berid,dat$copies,dat$lost)

trimean <-  function(vect) { foo = fivenum(vect); ans <- 0.5*foo[3] + 0.25*foo[2] + 0.25*foo[4]}

# Summary table with medians.
#summ <- data.frame(cbind(0,0,1,2,3,4,5,8,10,14,16,20))
summ <- data.frame(rbind(numeric(12)))
colnames(summ) <- c("docsize","berid","c1","c2","c3","c4","c5","c8","c10","c14","c16","c20")
datn = data.frame(dat$docsize,dat$berid,dat$copies,dat$lost)
for (ds in levels(factor(datn$dat.docsize)))
{
    tmp <- data.frame(datn[datn$dat.docsize==ds,]);
    for (be in levels(factor(tmp$dat.berid))) 
    {
        tmp2 <- tmp[tmp$dat.berid==be,]
        tmp3 = aggregate(tmp2, by=list(tmp2$dat.copies), FUN=median)
        newrow <- c(ds,be,tmp3$dat.lost)
        if (length(newrow) < length(colnames(summ)))
        {
            filler <- rep(0,length(colnames(summ)) - length(newrow))
            #print(c(length(filler),"=>",filler))
            #print(c(length(newrow),"=>",newrow))
            newrow <- c(newrow,filler)
        }
        #print(newrow)
        summ <- rbind(summ,as.numeric(newrow))
    }
}
summ <- summ[-1,]
rownames(summ) <- NULL

# Summary table with trimeans.
sumt <- data.frame(cbind(0,0,1,2,3,4,5,8,10,14,16,20))
colnames(sumt) <- c("docsize","berid","c1","c2","c3","c4","c5","c8","c10","c14","c16","c20")
datn = data.frame(dat$docsize,dat$berid,dat$copies,dat$lost)
for (ds in levels(factor(datn$dat.docsize))){
    tmp <- data.frame(datn[datn$dat.docsize==ds,]);
    for (be in levels(factor(tmp$dat.berid))) {
        tmp2 <- tmp[tmp$dat.berid==be,]
        tmp3 = aggregate(tmp2, by=list(tmp2$dat.copies), FUN=trimean)
        newrow <- c(ds,be,tmp3$dat.lost)
        if (length(newrow) < length(colnames(summ)))
        {
            filler <- rep(0,length(colnames(summ)) - length(newrow))
            newrow <- c(newrow,filler)
        }
        #print(newrow)
        sumt <- rbind(sumt,as.numeric(newrow))
    }
}
sumt <- sumt[-1,]
rownames(sumt) <- NULL

# Send output to a file so we can read it later. 
sink("shelf5_output.txt")

# Show results.
cat("Question 0 Summary losses (medians)\n")
print(summ)
cat("\n")
cat("Question 0 Summary losses (trimeans)\n")
print(sumt)
cat("\n")

# Let's look at the distributions of the samples.
for (ds in levels(factor(datn$dat.docsize)))
{
    tmp1 <- data.frame(datn[datn$dat.docsize==ds,]);
    for (be in levels(factor(tmp1$dat.berid))) 
    {
        tmp2 <- tmp1[tmp1$dat.berid==be,]
        for (cp in levels(factor(tmp2$dat.copies)))
        {
            tmp3 <- tmp2[tmp2$dat.copies==cp,]
            cat("docsize",ds,"berid",be,"copies",cp,"\n")
            stem(tmp3$dat.lost)
        }
    }
}
        
sink()


#END
