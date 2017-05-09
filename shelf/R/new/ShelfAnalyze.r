# R script to set up PreservationSimulation/shelf data
# RBLandau 20141214
# revised 20150619
# 

# REQUIRES the following to be defined as global strings before invoking
#  this script:
# - sInputFilename
# - sOutputFilename
# - sTitle
# - sSubtitle
# - sSummarizeFilename
# - sAnalyzeFilename
# This is all done in the shelf_call.r script.  Just edit the filenames and
#  title strings, and blast off.  

# f n H e a d i n g I n f o 
# Print a bunch of identifying information at the top of the report.
# Actually, also called to print the same info on the console to 
#  reassure the user that we haven't gone haywire for many seconds.  
fnHeadingInfo <- function(myfilename) 
{
    sMynameIs <- myfilename
    cat(sTitle,"\n")
    cat(sSubtitle,"\n")
    cat("\n")
    cat("Input data from \t\t", sInputFilename, "\n")
    cat("Output analysis into \t", sOutputFilename, "\n\n")
    cat("analysis tables by \t\t", sMynameIs, "\t", 
        format(file.mtime(sMynameIs),"%Y%m%d_%H%M%S%Z"), "\n")
    cat("and summarize script \t", sSummarizeFilename, "\t", 
        format(file.mtime(sSummarizeFilename),"%Y%m%d_%H%M%S%Z"), "\n")
    cat("at \t",format(Sys.time(),"%Y%m%d_%H%M%S%Z"),"\n")
    cat("\n")
}#ENDFN fnHeadingInfo

# f n P a g e H e a d i n g 
# Just a formfeed and couple identifying lines on each page, 
#  for those who might be stapler-impaired.  
fnPageHeading <- function(first=FALSE)
{
    if (! first){
        cat("\x0C")
    }
    cat(sOutputFilename, format(Sys.time(),"%Y%m%d_%H%M%S%Z"), "\n")
    cat(sTitle, "\n")
}

# F U N C T I O N S 

# W h a t e v e r S a m p l e S a d i s t i c s Y o u W a n t 
# Prints a header line and then all these stats.  
# The header line is anything you want, usually pairs of name and value.  
WhateverSampleSadisticsYouWant <- function(headerline,vect)
{
    # for the grouping variables, args include name (p1n) and then value (p1).
    cat("====== ",headerline,"N",length(vect)," ======","\n")
    stem(vect)
    cat(headerline,"N",length(vect),"\n")
    cat("median","\t\t",median(vect,na.rm=TRUE),"\n")
    cat("trimean","\t",trimean(vect),"\n")
    cat("midmean","\t",midmean(vect),"\n")
    stat_mean <- mean(vect,na.rm=TRUE)
    cat("mean","\t\t",stat_mean,"\n")
    cat("stddev","\t\t",sd(vect,na.rm=TRUE),"\n")
    cat("IQR","\t\t",IQR(vect,na.rm=TRUE),"\n")
    cat("mad","\t\t",mad(vect,na.rm=TRUE),"\n")
    stat_SEM <- (sd(vect,na.rm=TRUE)/sqrt(length(vect)))
    cat("SEM","\t\t",stat_SEM,"\n")
    stat_MeanOverSEM <- stat_mean / stat_SEM
    stat_LogMeanOverSEM <- log10(stat_mean / stat_SEM)
    cat("MeanOverSEM","\t",stat_MeanOverSEM,"\n")
    cat("LogMeanOverSEM","\t",stat_LogMeanOverSEM,"\n")
    cat("\n")
}#ENDFN WhateverSampleSadisticsYouWant

# A couple particular functions for summarizing the loss data.
# These might be slightly more robust than just mean, and slightly
#  more broadly estimated than median.  
# trimean was a JWT favorite.  
trimean <-  function(vect)  { foo <- fivenum(vect); ans <- 0.5*foo[3] + 0.25*foo[2] + 0.25*foo[4]; ans }
midmean <-  function(vect)  { ans <- mean(vect,trim=0.25,na.rm=TRUE); ans }

# s u m m a r i z e 
# Summarize function removed to separate file because it is extremely
#  grouping-dependent.  
source(sSummarizeFilename)

# M A I N L I N E  
# Code that executes rather than just defines other functions.  
# There really should not be any top-level executable code outside this routine.  
main <- function(){

    # W H A T ' S   M Y   N A M E 
    # What is the name of this script?
    #  (There ought to be a way to introspect this, a la $0, but I can't find it 
    #  in StackOverflow or Rblogs, rats.)
    sMynameIs <- sAnalyzeFilename   # Dumb, dumb, dumb.
    assign("sMynameIs", sMynameIs, envir=globalenv())

    # I N P U T 
    dat <- data.frame(read.table(sInputFilename, header=TRUE))
    # Use dataset with only the interesting columns: docsize, lifem, glitchimpact, copies, lost
    # because we don't want to aggregate anything else.
    datn <- fnSelectColumns(dat)
    #print(datn)

    # Expose the data so I can at least see them in R Studio for debugging.
    assign("dat", dat, envir=globalenv())
    assign("datn", datn, envir=globalenv())

    # How many documents in the collection?  Default = 10K.
    # Can be overridden by defining before this script is called.  
    if (! exists("nDocs")) {nDocs <- 10000}
    assign("nDocs", nDocs, envir=globalenv())

    # Absurd hack in here to make lifem print reasonably.
    #  Increase the penalty for printing in scientific 
    #  (exponential) format, and limit the number of digits
    #  so that there are no places after the radix point.  
    options("scipen"=100, "digits"=1)
    # End of absurd hack.  

    # H E A D I N G S 
    # Put out headings immediately to reassure the R user
    fnHeadingInfo(sMynameIs)

    # T A B L E S 
    # Tables function removed to separate file.
    # Establish the table names in this context so they can be used
    #  inside the functions.

    # O U T P U T 
    # Send output to a file so we can read it later. 
    sink(sOutputFilename)
    # Include heading info in file
    fnHeadingInfo(sMynameIs)

    # Show results.
    # L O S S   C O U N T S  M I D M E A N 
    if(TRUE){
        fnPageHeading(first=FALSE)
        cat("\nSummary losses (midmeans)\n\n")
        summid <- fnTableMid(dat)
        print(summid)
        cat("\n")
        assign("summid", summid, envir=globalenv())
    }#ENDIFFALSE

    # L O S S   P E R C E N T A G E S 
    if(TRUE){
        fnPageHeading()
        cat("\nPercentage losses (midmeans)\n\n")
        summidpct <- fnTableMidPct(dat)
        print(summidpct)
        cat("\n")
        assign("summidpct", summidpct, envir=globalenv())
    }#ENDIFFALSE

    # L O S S   C O U N T S  M E D I A N 
    if(0){
        fnPageHeading()
        cat("\nSummary losses (medians)\n\n")
        summed <- fnTableMed(dat)
        print(summed)
        cat("\n")
    }#ENDIFFALSE

    # L O S S   C O U N T S  T R I M E A N 
    if(0){
        fnPageHeading()
        cat("\nSummary losses (trimeans)\n\n")
        sumtri <- fnTableTri(dat)
        print(sumtri)
        cat("\n")
    }#ENDIFFALSE

    cat("\n")

    if(0){
        # All the grouping and aggregation dependent code has been moved
        #  to a separate file.  
        if (exists("bTablesOnly") & (! bTablesOnly))
        {
            cat("============================================\n\n")
            # Let's look at the distributions of the samples.  
            fnDetailedSampleStats(datn)
        }
    }#ENDIFFALSE
    
    # Close the output sink manually.  
    # Is there a way to do this automatically so it doesn't linger?
    sink()

}#ENDFN main

# Edit history:
# 20150701  RBL group by glitch impact (outside).
# 20150810  RBL ignore missing data (NA) values in most calcs.
# 20150918  RBL include more data in datn.
# 20160827  RBL include better header info in file.
# 20161006  RBL print lifem sanely when it has large values.  
# 20170302  RBL narrow copies to 8 instead of 20.
# 20170310  RBL remove summarize function to separate file.
# 20170312  RBL remove the dump-stats, too, to grouping-specific file.
# 20170315  RBL repair some local data references.
# 20170318  RBL Add table of percentage losses.
# 20170322  RBL Slight changes to accommodate new new new summary code.
# 20170324  RBL More changes to accommodate new new new summary code.
#               Add page headings between long tables.
#               Export main data tables to global for later use.
# 20170507  RBL Turn detailed stats back on, if I can get it to work right.  
# 
# 

#END
