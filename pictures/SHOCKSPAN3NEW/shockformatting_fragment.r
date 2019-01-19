# P A R A M S
nShockspan <- 3
nServerDefaultLife <- 3
nSegments <- 1

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

sTitleLine <-   (   ""
                %+% "Shocks: "
                %+% sprintf("span=%d; ", nShockspan) 
                %+% sprintf("ServerDefaultHalflife=%dyrs ", nServerDefaultLife)
                %+% " "
                %+% "\n"
                %+% "\n(Copies=5+; annual systematic auditing in "
                %+% sprintf("%d segment(s))", nSegments)
                )
sLegendLabel <- "  Number of \nAudited Copies"
lLegendItemLabels <- c("5","6","7")
sTimestamp <- fngettime()
sSamples <- sprintf("samples=%d ", min(trows$n))
sXLabel <- ("Shock Frequency (half-life) in hours "
            %+% "      (one metric year = 10,000 hours) "
            %+% "                           (less frequent shocks =====>)"
            )
sXLabel <- sXLabel %+% ("\n\n                                  " # cheapo rjust.
            %+% sprintf("          %s   %s   %s", sPlotFile,sTimestamp,sSamples)
            )
sYLabel <- ("probability of losing the entire collection (%)")
# ************ Also change summarize function and ggplot(color=...).
# E N D   O F   S T A N D A R D   F O R M A T T I N G 
