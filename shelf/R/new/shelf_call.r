# shelf_call.r
# Edit me and run me.  
# In R Studio, 
# - edit the filenames and title strings below, then 
# - save the file (ctrl-S), 
# - select all (ctrl-A), and 
# - execute the script (ctrl-Enter).

sInputFilename  <- "../hl/data/GiantOutput_gl3333andhilocomplete_dur1000impvar_copyvar_lifvar_00.txt"
sOutputFilename <- "../hl/tabs/glitchtest_f3333andhilocomplete_d1000ivar_analysis_20170421_00.txt"
sTitle <- "glitchtest4 HL copies=var Audit=1yr Glitch=3333 len=1000 imp=var lifem=var seed21"
sSubtitle <- "(impact=10,33,67,90pct len=1mo; copies grouped vertically)"
sSummarizeFilename <- "./summ-glitch-4.r"
sAnalyzeFilename <- "./ShelfAnalyze.r"
bTablesOnly <- 0
options(max.print=9999)
options(width=100)

source(sAnalyzeFilename)
main()
# Unwind any remaining sink()s to close output files.  
# Particularly important in case of errors.  
while (sink.number() > 0) {sink()}
#END

