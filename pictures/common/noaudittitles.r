# noaudittitles.r
#               RBLandau 20191016
# The guts of making the titles and legend for no-auditplots.  
# Extracted from previous working code, to be slid back in.
# 
# Requires that the following constants be defined by the caller:
# 
# sPlotFile           (string) name of the file to write plots into.  
# 
# Also uses the fngettime() function from PlotUtil, 
#  which must be included first.
# 

sLegendLabel <- "  Number of \n Copies"
lLegendItemLabels <- levels(factor(trows$copies))

sCopiesList <- paste0(lLegendItemLabels, sep=",", collapse="")
sTitleLine <-   (   ""
                %+% ""
                %+% "Without auditing, in a peaceful world, "
                %+% "too many copies are required "
                %+% "\nto reduce permanent errors "
                %+% "to acceptable levels"
                %+% "\n"
                %+% "\n(No auditing, duration = "
                %+% sprintf("%s ", min(trows$simlength/10000.0))
                %+% "years)"
                )
sTimestamp <- fngettime()
sSamples <- sprintf("samples=%d ", min(trows$n))
sXLabel <- ("Sector (half-life) in megahours "
            %+% "      (one metric year = 10,000 hours) "
            %+% "                           (less frequent shocks =====>)"
            )
sXLabel <- sXLabel %+% ("\n\n                                  " # cheapo rjust.
            %+% sprintf("          %s   %s   %s", sPlotFile,sTimestamp,sSamples)
            )

sYLabel <- ("permanent document losses (% of collection)")
