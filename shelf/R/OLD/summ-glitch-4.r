# summ-glitch-4.r
#                   RBL 20170421
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

library(plyr)

#midmean <-  function(vect)  { ans <- mean(vect,trim=0.25,na.rm=TRUE); ans }

fnTableMid <- function(dat)
{
    # REQUIREMENT: there are no confounding variables outside this list, 
    #  e.g., no variations in auditing strategies, frequencies, glitches, etc.
    #  If there is anything else in the data that varies, it MUST be included 
    #  in this list of things to be grouped, or the combined data will be
    #  corrupted, useless, dangerous.
 
    # E D I T M E :  C O L U M N S   T O   B E   G R O U P E D    
    column.list <- .(
         glitchfreq
        ,glitchimpact
        ,glitchmaxlife
#        ,glitchspan
        ,lifem
        ,copies
    )
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

    # Get the summary table.  
    summ.first <- ddply(dat, column.list, summarise
        ,"lost midmean"=midmean(lost)
        ,median=median(lost)
#        ,mean=mean(lost)
        ,Nreps=length(lost)
    )

    # E D I T M E :  R E O R D E R I N G S   F O R   E A S Y   C O M P A R I S O N
    # Reorder data rows for easier comparisons.
    head.reorder1 <- "Summary losses (midmeans), reordering 1: copies impact freq life "
    summ.reorder1 <- arrange(summ.first 
                ,glitchmaxlife
                ,copies
                ,glitchimpact
                ,glitchfreq
                ,lifem
#                ,glitchspan
                )
    head.reorder2 <- "Summary losses (midmeans), reordering 2: copies impact life freq "
    summ.reorder2 <- arrange(summ.first
                ,glitchmaxlife
                ,copies
                ,glitchimpact
#                ,glitchspan
                ,lifem
                ,glitchfreq
                )
    head.reorder3 <- "Summary losses (midmeans), reordering 3: freq copies impact life "
    summ.reorder3 <- arrange(summ.first
                ,glitchmaxlife
                ,glitchfreq
                ,copies
                ,glitchimpact
                ,lifem
#                ,glitchspan
                )
    head.reorder4 <- "Summary losses (midmeans), reordering 4: freq copies life impact "
    summ.reorder4 <- arrange(summ.first
                ,glitchmaxlife
                ,glitchfreq
                ,copies
                ,lifem
                ,glitchimpact
#                ,glitchspan
                )

    # How do we make this printing similar to the old style???
    sink("../hl/tabs/summ-glitch-4_reordering.txt")

    fnPageHeading(first=TRUE)
    cat("\nReordered tables based on \n")
    fnHeadingInfo(sMynameIs)
    
    cat("\n\nSummary losses (midmeans), normal order: freq impact life copies \n")
    cat("(varying from slowest to fastest, i.e., copies varies most quickly) \n\n")
#    colnames(summ.first) <- column.labels
    colnames(summ.first) <- column.shortlabels
    print(summ.first)

    fnPageHeading()
    cat("\n\n", head.reorder1, "\n\n")
    colnames(summ.reorder1) <- column.shortlabels
    print(summ.reorder1)

    fnPageHeading()
    cat("\n\n", head.reorder2, "\n\n")
    colnames(summ.reorder2) <- column.shortlabels
    print(summ.reorder2)

    fnPageHeading()
    cat("\n\n", head.reorder3, "\n\n")
    colnames(summ.reorder3) <- column.shortlabels
    print(summ.reorder3)

    fnPageHeading()
    cat("\n\n", head.reorder4, "\n\n")
    colnames(summ.reorder4) <- column.shortlabels
    print(summ.reorder4)

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
}#ENDFN fnTableMid


while (sink.number() > 0) {sink()}

# f n S e l e c t C o l u m n s 
# What data items are we going to be analyzing by grouping and aggregation?
# Return a new data frame containing only those.  They will be used in 
#  all the summarization and detailed stats functions below.
fnSelectColumns <- function(dat)
{
    datn <- data.frame(dat$glitchfreq,dat$glitchimpact,dat$glitchmaxlife,dat$lifem,dat$copies,dat$lost,dat$docsize)
    return(datn)
}


fnDetailedSampleStats <- function(datn)
{
if(0){ # comment out to do nothing.
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
                for (gi in levels(factor(tmp3$dat.glitchimpact)))
                {
                    tmp4 <- tmp3[tmp3$dat.glitchimpact==gi,]
#                    WhateverSampleSadisticsYouWant(c("docsize",ds,"lifem",lfm,"copies",cp,"glitchimpact",gi), tmp4$dat.lost))
                }
            }
        }
    }
}#ENDIF0
}#ENDFN fnDetailedSampleStats


#END


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
# 20170421  RBL Change from shock to glitch.
#               Since span=1 for all glitch tests, use impact instead.
# 20170507  RBL Remove meaningful names from reordering table names.
#               And add another reordering just in case we need it.
#               Put fnDetailedSampleStats function back in, I hope.  
# 
# 

#END
