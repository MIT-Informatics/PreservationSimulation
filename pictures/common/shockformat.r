# S T A N D A R D   S H O C K   F O R M A T T I N G 

# This code is very specific to drawing shock pictures. 
# I apologize for the spaghettiness and redundancy of this code; 
#  it evolved over a looong period of time and optimizing it 
#  did not seem a good use of my time.  Works; don't fix it.  
# 
# Requires that the following constants be defined by the caller:
# 
# nServerDefaultLife  server default half-life in years.  (Recall that this
#                      must be nonzero for all shock scenarios.)
# nShockspan          span of shocks when they occur: 0,1,2,3,4.  
# nShockImpactMin     minimum percent value of shock impact for this picture; 
#                      the interval is closed (inclusive) at both ends.
# nShockImpactMax     maximum percent value of shock impact.  
#                      (To consider only fatal shocks, e.g., set both min
#                      and max to 100.)
# nSegments           number of audit segments per year: 1,2,4,10,50.  
#                      (Audit cycles are always annual.)
# 

sPlotFile <- (  sprintf("shockspan%d",nShockspan)
            %+% sprintf("server%d",nServerDefaultLife)
            %+% sprintf("seg%d",nSegments)
            %+% ".png"
            )
fnGroupBy <- function(dfIn) {group_by(dfIn, copies, lifem
                                    , serverdefaultlife
                                    , shockfreq, shockspan, shockimpact
                                    , auditfrequency, auditsegments
                                    )}
fnSubset <- function(dfIn)  {subset(dfIn, 
                                      serverdefaultlife==nServerDefaultLife * 10000
                                    & shockspan==nShockspan
                                    & shockimpact>=nShockImpactMin
                                    & shockimpact<=nShockImpactMax
                                    & copies>=5
                                    & auditfrequency==10000
                                    & auditsegments==nSegments
                                    )}
want.varnames <- c("copies","lifem","lost","docstotal","serverdefaultlife"
                ,"shockfreq","shockimpact","shockspan","shockmaxlife"
                ,"auditfrequency","audittype","auditsegments"
                ,"deadserversactive","deadserversall")
fnNarrow <- function(dfIn)  {dfIn[want.varnames]}  

# G E T   D A T A  
# Get the data into the right form for these plots.
alldat.df <- fndfGetGiantDataRaw("")
allnewdat <- alldat.df %>% fnNarrow() %>% fnGroupBy() %>% 
summarize(losspct=round(mean(lost/docstotal)*100.0, 2), n=n()) 
newdat <- fnSubset(allnewdat)
trows <- newdat
# ************ Also may need to change summarize function and ggplot(color=...).
# E N D   O F   S T A N D A R D   S H O C K   F O R M A T T I N G 
