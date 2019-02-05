# shocktitles.r
#               RBLandau 20190204
# The guts of making the titles and legend for shock plots.  
# Extracted from previous working code, to be slid back in.
# 

sLegendLabel <- "  Number of \nAudited Copies"
#lLegendItemLabels <- c("5","6","7")
lLegendItemLabels <- levels(factor(trows$copies))

sCopiesList <- paste0(lLegendItemLabels, sep=",", collapse="")
sTitleLine <-   (   ""
                %+% sprintf("Shocks: span=%d, ", nShockspan)
                %+% sprintf("ServerDefaultHalflife=%dyrs ", nServerDefaultLife)
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
