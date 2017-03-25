# shelf_call.r
# Edit me and run me.  
# In R Studio, 
# - edit the filenames and title strings below, then 
# - save the file (ctrl-S), 
# - select all (ctrl-A), and 
# - execute the script (ctrl-Enter).

sInputFilename  <- "../hl/data/GiantOutput_shock2yr_len1yr_00.txt"
sOutputFilename <- "../hl/tabs/shocktest3_freq2yr_lenvar_seed21_analysis_20170324_00.txt"
sTitle <- "shocktest3 HL copies=var Audit=1yr Glitch=0 Shock=2yr len=1yr lifem=var seed21"
sSubtitle <- "(impact=50,100pct len=1yr; copies grouped vertically)"
sSummarizeFilename <- "./summ-shock-3.r"
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

