# summ-glitch-1.r
#                   RBL 20170322
# Take the tons of output from simulations, in suitably small bites, 
#  and make summary tables of them.  
# Grouping function used is ddply from plyr package, 
#  thanks to Hadley Wickham for writing such a simple interface,
#  and to Micah Altman for strongly suggesting that I look at it.  
#  The syntax appears simple, but there are so many options it's 
#  hard to find the right combinations at first.  How does the 
#  underlying code parse all the possibilities?

# This is laid out to be easily edited by someone who simply wants
#  to choose slightly different statistics or a different ordering
#  of columns to facilitate easier comparisons.  
#  Anywhere it says    E D I T M E    you might want to do something.

# Assume that the dat dataframe has already been read by the caller.

require(plyr)

#midmean <-  function(vect)  { ans <- mean(vect,trim=0.25,na.rm=TRUE); ans }

fnTableMid <- function(dat)
{
    # REQUIREMENT: there are no confounding variables outside this list, 
    #  e.g., no variations in auditing strategies, frequencies, glitches, etc.
    #  If there is anything else in the data that varies, it MUST be included 
    #  in this list of things to be grouped, or the combined data will be
    #  corrupted, useless, dangerous.
 
    # E D I T M E :  C O L U M N S   T O   B E   G R O U P E D    
print("before get column.list")
    column.list <- .(
         glitchfreq
        ,glitchimpact
        ,glitchmaxlife
#        ,glitchspan
        ,lifem
        ,copies
    )
print("after  get column.list")
    
    # E D I T M E :  C O L U M N   L A B E L S   F O R   H U M A N S 
    column.labels <- c(
         "glitch frequency (hrs)"
        ,"glitch impact (pct)"
        ,"glitch duration (hrs)"
#        ,"# servers affected"
        ,"sector half-life (megahours)"
        ,"# of copies"
        ,"lost midmean"
        ,"median"
#        ,"mean"
        ,"Nsamples"
    )

    # E D I T M E :  C O L U M N   L A B E L S   F O R   P R I N T I N G 
    column.shortlabels <- c(
         "glitchfreq"
        ,"impact"
        ,"duration"
#        ,"span"
        ,"lifem"
        ,"copies"
        ,"lost midmean"
        ,"median"
#        ,"mean"
        ,"Nreps"
    )
print("before get first table")
    # Get the summary table.  
    summ.first <- ddply(dat, column.list, summarise
        ,"lost midmean"=midmean(lost)
        ,median=median(lost)
#        ,mean=mean(lost)
        ,Nreps=length(lost)
    )
print("after  get first table")

    # E D I T M E :  R E O R D E R I N G   F O R   E A S Y   C O M P A R I S O N S 
    # Reorder data rows for easier comparisons.
    summ.span.before.copies <- arrange(summ.first 
                ,glitchfreq
                ,glitchimpact
                ,glitchmaxlife
#                ,glitchspan
                ,copies
                ,lifem
                )
    summ.span.before.life <- arrange(summ.first
                ,glitchfreq
                ,glitchimpact
                ,glitchmaxlife
#                ,glitchspan
                ,lifem
                ,copies
                )
    summ.life.before.span <- arrange(summ.first
                ,glitchfreq
                ,glitchimpact
                ,glitchmaxlife
                ,lifem
#                ,glitchspan
                ,copies
                )

    # How do we make this printing similar to the old style???
    sink("summ-glitch-1_reordering.txt")

    fnPageHeading(first=TRUE)
    cat("\n\nSummary losses (midmeans), normal order\n\n")
#    colnames(summ.first) <- column.labels
    colnames(summ.first) <- column.shortlabels
    print(summ.first)

    fnPageHeading()
    cat("\n\nSummary losses (midmeans), span before copies\n\n")
    colnames(summ.span.before.copies) <- column.shortlabels
    print(summ.span.before.copies)

    fnPageHeading()
    cat("\n\nSummary losses (midmeans), span before life\n\n")
    colnames(summ.span.before.life) <- column.shortlabels
    print(summ.span.before.life)

    fnPageHeading()
    cat("\n\nSummary losses (midmeans), life before span\n\n")
    colnames(summ.life.before.span) <- column.shortlabels
    print(summ.life.before.span)

    sink()

    return(summ.first)

}

fnTableMidPct <- function(dat)
{
    if(TRUE){
        # Summary table with midmeans.
        tsummid <- fnTableMid(dat)
        
        # E D I T M E :  C O L U M N S   C O N T A I N I N G   P E R C E N T A G E S 
        # These columns have to be divided by 100 to make counts into percentages.
        columns.with.loss.numbers <- c(
             "lost midmean"
            ,"median"
#            ,"mean"
        )
        for (col in columns.with.loss.numbers)
        {
            # Convert loss numberss to percentages of collection size.
            tsummid[,col] <- tsummid[,col] / nDocs * 100.0
        }
        return(tsummid)
    }#ENDIFFALSE
}#ENDFN fnTableMidPct


while (sink.number() > 0) {sink()}

fnSelectColumns <- function(dat){}
fnDetailedSampleStats <- function(datn){}


# Edit history:
# 20170322  RBL Original version that limped.
# 20170324  RBL Actually works.
#               Move columns.with.loss.numbers inside the routine that
#                uses it, grumble.
#               Do not include mean in results; almost meaningless for 
#                data this skewed.  But it's just commented out, so 
#                if someone wants to resurrect it, that's easy.  
#               Still need to get R to word-wrap the column headings.
#                RStudio does that for the view pane, but R..., grumble.
# 20170502  RBL Change from shock to glitch.  
#               Hope hope hope it's just a name change.  
# 
# 

#END
