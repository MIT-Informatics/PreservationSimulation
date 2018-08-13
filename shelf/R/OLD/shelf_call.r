# shelf_call.r
# Edit me and run me.  
# In R Studio, 
# - edit the filenames and title strings below, then 
# - save the file (ctrl-S), 
# - select all (ctrl-A), and 
# - execute the script (ctrl-Enter).

sInputFilename  <- "../shock/data/5yr/GiantOutput_shk50000durvarimpvarspan1_20170612_00.txt"
sOutputFilename <- "../shock/tabs/5yr/analysis_shockvslife_5yr_20170619_00.txt"
sTitle <- "shockvslife tests SHOCK copies=var Audit=1yr Shock=50000, dur=var lifem=var svrdeflife=100000 seed21"
sSubtitle <- "(how bad is medium shock?)"
sSummarizeFilename <- "./summ-shockvslife-4.r"
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

