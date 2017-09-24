# ExploreGiantOutputs.r

# From Micah Altman 20170726
# Trying to understand it, RBLandau 20170920


library(tidyverse)

# Absurd hack in here to make lifem print reasonably.
#  Increase the penalty for printing in scientific 
#  (exponential) format, and limit the number of digits
#  so that there are no places after the radix point.  
options("scipen"=100, "digits"=1)
# End of absurd hack.  

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

# L O A D   F I L E S 

# Load & merge all files in directory
filesList <- grep(pattern = "^Giant.*\\.txt$", dir(), value = TRUE)
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
coreResultVarNames<- c("docslost","docsrepairedmajority","docsrepairedminority")
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

library(reshape2)
basicdata <- data.frame(cbind(results$copies,results$lifem,results$mdmlosspct))
colnames(basicdata)<-c("copies","lifem","lossp")
#basictable <- dcast(basicdata, copies~lifem, FUN=identity(basicdata$lossp))
basictable <- dcast(results, copies~lifem,  value.var="mdmlosspct")
#audittable <- basictable <- dcast(results, auditfrequency+copies~lifem,  value.var="mdmlosspct")

# P L O T S 

library(ggplot2)

nCopies <- 3
gp<-(ggplot(fnSelectCopies(results, nCopies), 
    aes(x=(lifem), y=(safelog(mdmlosspct))))
    + geom_point(color="red",size=4)
    + geom_line(linetype="dashed",color="black",size=1)
    + scale_x_log10()
    + annotation_logticks()
    )
plot(gp)

if (0) {
# plot a regression plot between copies, and loss
gp<-ggplot(selectedresults, aes(x=log10(lifem), y=mdmlosspct)) +
  geom_point(shape=1) +    
  geom_smooth(method = lm)
plot(gp)

# plot multiples of the plot above, faceted by different values 
#  of schockimpact and nshocks
gp<-ggplot(selectedresults, aes(x=copies, y=mdmlosspct)) +
  geom_point(shape=1) +    
  geom_smooth(method = lm) + facet_wrap(~shockimpact)
plot(gp)

gp<-ggplot(selectedresults, aes(x=copies, y=mdmlosspct)) +
  geom_point(shape=1) +    
  geom_smooth(method = lm) + facet_grid(~shockimpact~lifem)
plot(gp)
}

if (0) {
# pairwise comparison plot of multiple variables -- just for fun
library(GGally)
ggpairs(res,columns=c("copies", "mdmlosspct", "shockimpact", "lifem"))
}



# Edit history:
# 20170726  MA  Original version.
# 20170923  RBL Un-abbreviate variable names for clarity.
#               Change loss factor to midmean percentage.
#               Force big integers to print as integers rather than
#                exponentials.
#               Nuke all the plotting, which didn't give interesting results
#                in any case.  Need three dimensions: life, copies, losses.
#                Concentrate on getting the data in for later processing.  
# 20170924  RBL Move all functions to the top
# 



