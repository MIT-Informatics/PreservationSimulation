# GetNoAuditData.r

source("../../shelf/R/new/GetData.r")

rm(results)
results <- fndfGetGiantData("./")
# Get fewer columns to work with, easier to see.
dat.noaudit <- fndfGetAuditData(results)
# Tabulate columns by copies and sector lifetime.
tbl.noaudit <- data.frame(with(dat.noaudit, 
            tapply(mdmlosspct, list(copies, lifem), FUN=identity)))

tbl<-cbind.data.frame(dat.noaudit$copies, tbl.noaudit)
tbl<-cbind.data.frame(levels(factor(dat.noaudit$copies)), tbl.noaudit)
        colnames(tbl)<-c("copies",colnames(tbl.noaudit))

foo<-(with(dat.noaudit, 
       tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(results$copies))), foo)
colnames(foo2)<-c("copies",as.numeric(colnames(foo2[,2:ncol(foo2)])))
#tbl<-data.frame(foo2)

# Plot something.
library(ggplot2)

gp <- ggplot() 

nCopies <- 3
trow <- fnSelectCopies(tbl, nCopies)
gp <- gp + 
        aes(tbl, x=(tbl$lifem), y=(safelog(tbl$mdmlosspct))) +
        geom_point(data=trow, 
            color="red", size=5, shape=(48+nCopies)) +
        geom_line(linetype="dashed", color="black", size=1) +
        scale_x_log10() + scale_y_log10() +
        annotation_logticks()


plot(gp)

