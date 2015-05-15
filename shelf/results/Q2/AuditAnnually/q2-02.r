# R script to set up PreservationSimulation/shelf data
# RBLandau 20141130

# I N P U T 
dat <- data.frame(read.table("s:/landau/python/dev/preservationsimulation/shelf/q2-output-03.txt", header=TRUE))
datn = data.frame(dat$docsize,dat$lifem,dat$copies,dat$docslost,dat$auditlost)

aprop = datn$dat.auditlost / datn$dat.docslost
hist(aprop)

# T A B L E S 
# Summary table with medians.
#summ <- data.frame(cbind(0,0,1,2,3,4,5,8,10,14,16,20))
summ <- data.frame(rbind(numeric(12)))
colnames(summ) <- c("docsize","lifem","c1","c2","c3","c4","c5","c8","c10","c14","c16","c20")
datn = data.frame(dat$docsize,dat$lifem,dat$copies,dat$docslost)
for (ds in levels(factor(datn$dat.docsize)))
{
    tmp <- data.frame(datn[datn$dat.docsize==ds,]);
    for (lfm in levels(factor(tmp$dat.lifem))) 
    {
        tmp2 <- tmp[tmp$dat.lifem==lfm,]
        tmp3 = aggregate(tmp2, by=list(tmp2$dat.copies), FUN=median)
        newrow <- c(ds,lfm,tmp3$dat.docslost)
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

# O U T P U T 
# Send output to a file so we can read it later. 
sink("q2-shelf-output.txt")

# Show results.
cat("Question 2 Summary losses (medians) with annual total audits\n")
print(summ)
cat("\n")

sink()


#END

