# DataUtil.r
# Functions to get data for selection and analysis.

# From Micah Altman 20170726
# Adapted RBLlandau 20171002

library(tidyverse)

# H A C K S 

# Absurd hack in here to make lifem print reasonably.
#  Increase the penalty for printing in scientific 
#  (exponential) format, and limit the number of digits
#  so that there are no places after the radix point.  
options("scipen"=100, "digits"=1)
# End of absurd hack.  

# Enable printing wide tables.
options("width"=120)

# Add an infix concatenation operator for strings.
`%+%` <- function(a,b) paste0(a,b)


# U T I L I T Y   F U N C T I O N S 

# Better functions for summarizing the loss data.
# These are more robust than just mean, and more broadly estimated
#  than median.  
# midmean is just a trimmed mean of the middle half of the sample.
# trimean is a less efficient but easier trimmed central measure, 
#  and was a JWT favorite.  
trimean <-  function(vect)  
{   foo <- fivenum(vect); 
    ans <- 0.5*foo[3] + 0.25*foo[2] + 0.25*foo[4]; 
    ans 
}
midmean <-  function(vect)  
{   ans <- mean(vect, trim=0.25, na.rm=TRUE); 
    ans 
}

# Select only the dataframe rows with N copies.
fnSelectCopies <- function(dfIn, nCopies)
{   dfIn[dfIn$copies==nCopies,]
}

# Safe functions for plotting.
# Note that safelog(0) returns 0, as needed for sensible axis labeling.  
safelog <- function(x) {return(log10(x+1))}
safe    <- function(x) {return(x+0.5)}

# Shock tabulation functions.
fntShockTab <- function(input, freq, impact, duration) {
    res1 <- input[input$copies>1 & 
                input$shockfreq==freq & 
                input$shockimpact==impact & 
                input$shockmaxlife==duration,]
    assign("res.shocktdat", res1, envir=globalenv())
    #print(paste("res.shockdat",length(res.shockdat$copies)))
    restab <- dcast(res1, copies~lifem, value.var="mdmlosspct")
    return(restab)
}

# f n d f G e t G i a n t D a t a 
fndfGetGiantData <- function(dir.string)
{
    # L O A D   F I L E S 

    # Load & merge all files in directory
    if (dir.string == "") {dir.string <- "./"}
    filesList <- grep(pattern="^Giant.*\\.txt$", dir(dir.string), 
                perl=TRUE, value = TRUE)
# !!! I need to get fully qualified names out of grep here.  How?  
# !!! As it is, works only for current directory.  
    sims.df.ls = lapply( filesList, 
          function(x)read.table(x,
                                header=TRUE,sep=" ", na.strings="nolinefound")
    ) # NOTE MISSING PARAMETER ENTRIES in na.strings
    sims.merged.df <- bind_rows(sims.df.ls)

    # Set up namesets for dependent, independent, ignored vars.
    #  Many of the columns are not relevant to data analysis, only tracking.
    allVarNames <- colnames(sims.merged.df)
    ignoreVarNames <- c("timestamp","seed","walltime","cputime","logfilename",
        "logfilesize","instructionfilename","todaysdatetime","extractorversion",
        "cpuinfo","mongoid")
    resultVarNames <- c("docslost","docsrepairedmajority","docsrepairedminority",
        "lost","nshocks","nglitches","deadserversactive","deadserversall",
        "docsokay","auditmajority","auditminority","auditlost","auditrepairs",
        "auditcycles")
    coreResultVarNames<- c("docslost","docsrepairedmajority",
        "docsrepairedminority")
    paramVarNames<- setdiff(setdiff(allVarNames, resultVarNames), ignoreVarNames)
    testVarNames<-c("copies", "lifem")
    nonIgnoreVarNames<-setdiff(allVarNames, ignoreVarNames)

    # Select, group, and aggregate.
    sims.selected.df <- sims.merged.df[nonIgnoreVarNames]
    gp_sims.merged<-eval(parse(text=paste("group_by(sims.selected.df,",
        paste(collapse=",", paramVarNames),")")))
    results <- summarise(gp_sims.merged, 
                mdmlosspct=round(midmean(docslost/docstotal)*100,1), n=n())
    selectedresults <- results[which(results[["copies"]]!=1),]

    return(results)
}

# f n d f G e t S u b s e t D a t a 
fndfGetSubsetData <- function(results, lColumnNames)
{
    subset <- results[lColumnNames]
    return(subset)
}

# f n d f G e t A u d i t D a t a 
fndfGetAuditData <- function(results)
{
    # Specific to audit analyses: 
    lNamesIWant <- c("copies","lifem","mdmlosspct",
                    "auditfrequency","auditsegments",    
                                            #"audittype", too, needs fixed
                    "docsize","shelfsize")
    results.narrow <- fndfGetSubsetData(results, lNamesIWant)
    results.plausible <- results.narrow[results.narrow$lifem>=2,]
    return(results.plausible)
}

# f n d f G e t S h o c k D a t a 
fndfGetShockData <- function(results)
{
    # Specific to shock analyses: 
    lNamesIWant <- c("copies","lifem","mdmlosspct",
                    "shockfreq","shockimpact","shockmaxlife","shockspan",
                    "docsize","shelfsize")
    shockresults <- results[lNamesIWant]
    return(shockresults)
}

# f n d f G e t G l i t c h D a t a 
fndfGetGlitchData <- function(results)
{
    # Specific to shock analyses: 
    lNamesIWant <- c("copies","lifem","mdmlosspct",
                    "glitchfreq","glitchspan","glitchimpact","glitchmaxlife",
                    "docsize","shelfsize")
    shockresults <- results[lNamesIWant]
    return(shockresults)
}

# f n d f G e t D o c s i z e D a t a 
fndfGetDocsizeData <- function(results)
{
    lNamesIWant <- c("copies","lifem","mdmlosspct",
                    "auditfreq","auditsegments", 
                                            #"audittype", too, needs fixed
                    "docsize","shelfsize")
}

# f n d f G e t S h e l f s i z e D a t a 
fndfGetShelfsizeData <- function(results)
{
    lNamesIWant <- c("copies","lifem","mdmlosspct",
                    "auditfreq","auditsegments",
                                            #"audittype", too, needs fixed
                    "docsize","shelfsize")
}

# Edit history:
# 20171002  RBL Copy from Altman original ExploreGiantOutputs.r.
#               Add functions to select data for specific analyses.
# 
# 