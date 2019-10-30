# shocktitles.r
#               RBLandau 20190204
# The guts of making the titles and legend for shock plots.  
# Extracted from previous working code, to be slid back in.
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
# sPlotFile           (string) name of the file to write plots into.  
# 
# Uses trows$simlength to calculate simulation duration.  
# Also uses the fngettime() function from PlotUtil, 
#  which must be included first.
# 

sLegendLabel <- "  Number of \nAudited Copies"
lLegendItemLabels <- levels(factor(trows$copies))

sCopiesList <- paste0(lLegendItemLabels, sep=",", collapse="")
sTitleLine <-   (   ""
                %+% sprintf("Shocks: span=%d", nShockspan)
                %+% sprintf(", impacts [%d%%,%d%%]", 
                            nShockImpactMin, nShockImpactMax)
                %+% sprintf(", ServerDefaultHalflife=%dyrs", nServerDefaultLife)
                %+% sprintf(", Duration=%dyrs", as.integer(min(trows$simlength)/10000))
                %+% " "
                %+% "\n"
                %+% sprintf("\n(Copies=%s ", sCopiesList)
                %+% "annual systematic auditing in "
                %+% sprintf("%d segment(s))", nSegments)
                )

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
