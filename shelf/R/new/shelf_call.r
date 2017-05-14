# shelf_call.r
# Edit me and run me.  
# In R Studio, 
# - edit the filenames and title strings below, then 
# - save the file (ctrl-S), 
# - select all (ctrl-A), and 
# - execute the script (ctrl-Enter).

sInputFilename  <- "../hl/data/GiantOutput_cop12-a10000-lifvar-gf0-sf0_00.txt"
sOutputFilename <- "../hl/tabs/calibtest_c1+2-a10000-lifvar-gf0-sf0_analysis_20170514_00.txt"
sTitle <- "glitchtest4 HL copies=1,2 Audit=1yr Glitch=none lifem=var seed21"
sSubtitle <- "(no glitch, no shock, calibrarion; calibrarion c=1,2 only)"
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

