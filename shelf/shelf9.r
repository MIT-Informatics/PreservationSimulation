# R script to set up PreservationSimulation/shelf data
# RBLandau 20140914

# I N P U T 
dat <- data.frame(read.table("s:/landau/python/dev/preservationsimulation/shelf/q0b-alllife-allsize-allcop-seed11-noaudits-megahours.txt", header=TRUE))
# Use dataset with only the interesting columns: docsize, berid, copies, lost
# because we don't want to aggregate anything else.
#datn = data.frame(dat$docsize,dat$berid,dat$copies,dat$lost)

# F U N C T I O N S 

WhateverSampleSadisticsYouWant <- function(docsize,lifem,copies,vect)
{
    cat("=== ","docsize",docsize,"lifem",lifem,"copies",copies,"\n")
    stem(vect)
    cat("    ","docsize",docsize,"lifem",lifem,"copies",copies,"\n")
    stat_mean <- mean(vect)
    cat("mean","\t\t",stat_mean,"\n")
    cat("midmean","\t",midmean(vect),"\n")
    cat("median","\t\t",median(vect),"\n")
    cat("trimean","\t",trimean(vect),"\n")
    cat("stddev","\t\t",sd(vect),"\n")
    cat("IQR","\t\t",IQR(vect),"\n")
    cat("mad","\t\t",mad(vect),"\n")
    stat_SEM <- (sd(vect)/sqrt(length(vect)))
    cat("SEM","\t\t",stat_SEM,"\n")
    stat_MeanOverSEM <- stat_mean / stat_SEM
    stat_LogMeanOverSEM <- log10(stat_mean / stat_SEM)
    cat("MeanOverSEM","\t",stat_MeanOverSEM,"\n")
    cat("LogMeanOverSEM","\t",stat_LogMeanOverSEM,"\n")
    cat("\n")
}

trimean <-  function(vect)  { foo = fivenum(vect); ans <- 0.5*foo[3] + 0.25*foo[2] + 0.25*foo[4]; ans }
midmean <-  function(vect)  { ans <- mean(vect,trim=0.25); ans }

# T A B L E S 
# Summary table with medians.
#summ <- data.frame(cbind(0,0,1,2,3,4,5,8,10,14,16,20))
summ <- data.frame(rbind(numeric(12)))
colnames(summ) <- c("docsize","lifem","c1","c2","c3","c4","c5","c8","c10","c14","c16","c20")
datn = data.frame(dat$docsize,dat$lifem,dat$copies,dat$lost)
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
#sumt <- data.frame(cbind(0,0,1,2,3,4,5,8,10,14,16,20))
sumt <- data.frame(rbind(numeric(12)))
colnames(sumt) <- c("docsize","lifem","c1","c2","c3","c4","c5","c8","c10","c14","c16","c20")
datn = data.frame(dat$docsize,dat$lifem,dat$copies,dat$lost)
for (ds in levels(factor(datn$dat.docsize))){
    tmp <- data.frame(datn[datn$dat.docsize==ds,]);
    for (lm in levels(factor(tmp$dat.lifem))) {
        tmp2 <- tmp[tmp$dat.lifem==lm,]
        tmp3 = aggregate(tmp2, by=list(tmp2$dat.copies), FUN=trimean)
        newrow <- c(ds,lm,tmp3$dat.lost)
        if (length(newrow) < length(colnames(sumt)))
        {
            filler <- rep(0,length(colnames(sumt)) - length(newrow))
            newrow <- c(newrow,filler)
        }
        #print(newrow)
        sumt <- rbind(sumt,as.numeric(newrow))
    }
}
sumt <- sumt[-1,]
rownames(sumt) <- NULL

# O U T P U T 
# Send output to a file so we can read it later. 
sink("shelf9_output.txt")

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
            WhateverSampleSadisticsYouWant(ds,be,cp,tmp3$dat.lost)
        }
    }
}
        
sink()


#END
