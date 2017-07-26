library(tidyverse)

# load & merge all files in directory
filesList <- grep(pattern = ".*\\.txt$",dir(),value = TRUE)
sims.df.ls = lapply( filesList, 
      function(x)read.table(x,
                            header=TRUE,sep=" ",na.strings="nolinefound")
) #NOTE MISSING PARAMETER ENTRIES in na.strings
sims.merged.df <- bind_rows(sims.df.ls)

#set up namesets for dependent, independent, ignored vars

allVarNames <- colnames(sims.merged.df)
ignoreVarNames <- c("timestamp","seed","walltime","cputime","logfilename","logfilesize","instructionfilename","todaysdatetime","extractorversion","cpuinfo","mongoid")
resultVarNames <- c("docslost","docsrepairedmajority","docsrepairedminority","lost","nshocks","nglitches","deadserversactive","deadserversall","docsokay","auditmajority","auditminority","auditlost","auditrepairs","auditcycles")
coreResultVarNames<- c("docslost","docsrepairedmajority","docsrepairedminority")
paramVarNames<- setdiff(setdiff(allVarNames,resultVarNames),ignoreVarNames)
testVarNames<-c("copies","lifem")
nonIgnoreVarNames<-setdiff(allVarNames,ignoreVarNames)

# select, group, and aggregate
sims.selected.df <- sims.merged.df[nonIgnoreVarNames]
gp_sims.merged<-eval(parse(text=paste("group_by(sims.selected.df,",paste(collapse=",",paramVarNames),")")))
res<-summarise(gp_sims.merged,mnlossfrac=mean(docslost/docstotal),n=n())
sres<-res[which(res[["copies"]]!=1),]


#plot a regression plot between copies, and loss
library(ggplot2)

gp<-ggplot(sres, aes(x=copies, y=mnlossfrac)) +
  geom_point(shape=1) +    
  geom_smooth(method = lm)
plot(gp)

#plot multiples of the plot above, faceted by different values of schockimpact and nshocks
gp<-ggplot(sres, aes(x=copies, y=mnlossfrac)) +
  geom_point(shape=1) +    
  geom_smooth(method = lm) + facet_wrap(~shockimpact)
plot(gp)

gp<-ggplot(sres, aes(x=copies, y=mnlossfrac)) +
  geom_point(shape=1) +    
  geom_smooth(method = lm) + facet_grid(~shockimpact~lifem)
plot(gp)

# pairwise comparison plot of multiple variables -- just for fun
library(GGally)
ggpairs(res,columns=c("copies","mnlossfrac","shockimpact","lifem"))



