# S T A N D A R D   S H O C K   F O R M A T T I N G 
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
# ************ Also change summarize function and ggplot(color=...).
# E N D   O F   S T A N D A R D   S H O C K   F O R M A T T I N G 
