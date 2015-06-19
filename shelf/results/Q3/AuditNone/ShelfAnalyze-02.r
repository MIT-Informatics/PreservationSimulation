# R script to set up PreservationSimulation/shelf data
# RBLandau 20141214

# REQUIRES:
# - sInputFilename
# - sOutputFilemane
# - sTitle

# I N P U T 
dat <- data.frame(read.table(sInputFilename, header=TRUE))
# Use dataset with only the interesting columns: docsize, lifem, copies, lost
# because we don't want to aggregate anything else.
datn = data.frame(dat$docsize,dat$lifem,dat$copies,dat$lost)
sink()
cat("Input data from ",sInputFilename,"\n")
cat("Output analysis into ",sOutputFilename,"\n\n")
cat(sTitle,"\n")
cat("\n")

# F U N C T I O N S 

trimean <-  function(vect)  { foo = fivenum(vect); ans <- 0.5*foo[3] + 0.25*foo[2] + 0.25*foo[4]; ans }
midmean <-  function(vect)  { ans <- mean(vect,trim=0.25); ans }

WhateverSampleSadisticsYouWant <- function(docsize,lifem,copies,shelfsize,vect)
{
    cat("=== ","docsize",docsize,"lifem",lifem,"copies",copies,"shelfsize",shelfsize,"N",length(vect),"\n")
    stem(vect)
    cat("docsize",docsize,"lifem",lifem,"copies",copies,"shelfsize",shelfsize,"N",length(vect),"\n")
    cat("median","\t\t",median(vect),"\n")
    cat("trimean","\t",trimean(vect),"\n")
    cat("midmean","\t",midmean(vect),"\n")
    stat_mean <- mean(vect)
    cat("mean","\t\t",stat_mean,"\n")
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

# T A B L E S 
# Summary table with medians.
#summ <- data.frame(cbind(0,0,1,2,3,4,5,8,10,14,16,20))
summ <- data.frame(rbind(numeric(13)))
colnames(summ) <- c("docsize","lifem","shelfsize","c1","c2","c3","c4","c5","c8","c10","c14","c16","c20")
datn = data.frame(dat$docsize,dat$lifem,dat$shelfsize,dat$copies,dat$lost)

for (ss in levels(factor(datn$dat.shelfsize)))
{
    for (ds in levels(factor(datn$dat.docsize)))
    {
        tmp <- data.frame(datn[datn$dat.docsize==ds & datn$dat.shelfsize==ss,]);
        for (lfm in levels(factor(tmp$dat.lifem))) 
        {
            tmp2 <- tmp[tmp$dat.lifem==lfm & tmp$dat.shelfsize==ss,]
            tmp3 = aggregate(tmp2, by=list(tmp2$dat.copies), FUN=median)
            newrow <- c(ds,lfm,ss,tmp3$dat.lost)
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
}
summ <- summ[-1,]
rownames(summ) <- NULL


if(FALSE)
{
# Summary table with trimeans.
#sumt <- data.frame(cbind(0,0,1,2,3,4,5,8,10,14,16,20))
sumt <- data.frame(rbind(numeric(13)))
colnames(sumt) <- c("docsize","lifem","shelfsize","c1","c2","c3","c4","c5","c8","c10","c14","c16","c20")
datn = data.frame(dat$docsize,dat$lifem,dat$shelfsize,dat$copies,dat$lost)

for (ss in levels(factor(datn$dat.shelfsize)))
{
    for (ds in levels(factor(datn$dat.docsize))){
        tmp <- data.frame(datn[datn$dat.docsize==ds & datn$dat.shelfsize==ss,]);
        for (lfm in levels(factor(tmp$dat.lifem))) {
            tmp2 <- tmp[tmp$dat.lifem==lfm & tmp$dat.shelfsize==ss,]
            tmp3 = aggregate(tmp2, by=list(tmp2$dat.copies), FUN=trimean)
            newrow <- c(ds,lfm,ss,tmp3$dat.lost)
            if (length(newrow) < length(colnames(sumt)))
            {
                filler <- rep(0,length(colnames(sumt)) - length(newrow))
                newrow <- c(newrow,filler)
            }
            #print(newrow)
            sumt <- rbind(sumt,as.numeric(newrow))
        }
    }
}
sumt <- sumt[-1,]
rownames(sumt) <- NULL
}



# O U T P U T 
# Leave tracks for the console user.
#cat("Input data from ",sInputFilename,"\n")
#cat("Output analysis into ",sOutputFilename,"\n\n")
#cat(sTitle,"\n")
#cat("\n")
#cat("\n")

# Send output to a file so we can read it later. 
sink(sOutputFilename)
cat(sTitle,"\n")
cat("Input data from ",sInputFilename,"\n")
cat("Output analysis into ",sOutputFilename,"\n\n")

# Show results.
cat("Question 0 Summary losses (medians)\n")
print(summ)
cat("\n")
if(FALSE){
cat("Question 0 Summary losses (trimeans)\n")
print(sumt)
}
cat("\n")

# Let's look at the distributions of the samples.  
# The order of nesting here makes some comparisons easier than others.  
for (ds in levels(factor(datn$dat.docsize)))
{
    tmp1 <- data.frame(datn[datn$dat.docsize==ds,]);
    for (lfm in levels(factor(tmp1$dat.lifem))) 
    {
        tmp2 <- tmp1[tmp1$dat.lifem==lfm,]
        for (cp in levels(factor(tmp2$dat.copies)))
        {
            tmp3 <- tmp2[tmp2$dat.copies==cp,]
            for (ss in levels(factor(tmp3$dat.shelfsize)))
            {
                tmp4 <- tmp3[tmp3$dat.shelfsize==ss,]
                WhateverSampleSadisticsYouWant(ds,lfm,cp,ss,tmp4$dat.lost)
            }
        }
    }
}

        
sink()


#END
