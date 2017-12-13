#RandomTables.r
#                   RBLandau 20171113


fnPrintTableRandom <- function(dfdat, sOutputFilename, sTitle, sSubtitle){

# Tabulate columns by copies and sector lifetime.
tbl.auditrandom <- data.frame(with(dfdat, 
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
