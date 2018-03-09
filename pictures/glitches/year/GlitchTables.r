#GlitchTables.r
#                   RBLandau 20190130


fnPrintTableShockLow <- function(dfdat, sOutputFilename, sTitle, sSubtitle){

# Tabulate columns by copies and sector lifetime.
tbl.shocklow <- data.frame(with(dfdat, 
            tapply(mdmlosspct, list(copies, lifem), FUN=identity)))

# Re-form the data into a table for printing.  
foo<-(with(dfdat, 
       tapply(mdmlosspct, list(copies, lifem), FUN=identity)))
foo2<-cbind(as.numeric(levels(factor(dfdat$copies))), foo)
tbl2<-data.frame(foo2)
colnames(tbl2)<-c("copies",as.numeric(colnames(foo2[,2:ncol(foo2)])))

# Pretty-print this to a file with explanatory headings.
sink(sOutputFilename)
cat("MIT Preservation Simulation Project", "\n\n")
cat(sOutputFilename, format(Sys.time(),"%Y%m%d_%H%M%S%Z"), "\n\n")
cat(sTitle, "\n\n")
cat(sSubtitle, "\n\n")
cat("\n")
print(tbl2)
sink()

return(tbl2)

}


# f n M a k e S m a l l L o s s T a b l e 
fnMakeSmallLossTable <- function(dfIn) {
    library(reshape2)
    bar.small <- dfIn[,c("copies", "lifem", "mdmlosspct")]
    bar.melted <- melt(bar.small, id=c("copies", "lifem"))
    bar.recast <- dcast(bar.melted, copies~lifem)
    return(bar.recast)
}


# f n S a v e S m a l l L o s s T a b l e 
fnSaveSmallLossTable <- function(dfIn, sFilename, sHeading) {
    dfTemp <- fnMakeSmallLossTable(dfIn)
    sink(sFilename)
    cat("MIT Preservation Simulation Project", "\n")
    cat(sFilename, format(Sys.time(),"%Y%m%d_%H%M%S%Z"), "\n\n")
    cat(sHeading, "\n\n")
    cat("        half-life-------------------->","\n")
    print(dfTemp)
    sink()
}




#END
