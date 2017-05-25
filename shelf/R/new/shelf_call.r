# shelf_call.r
# Edit me and run me.  
# In R Studio, 
# - edit the filenames and title strings below, then 
# - save the file (ctrl-S), 
# - select all (ctrl-A), and 
# - execute the script (ctrl-Enter).

sInputFilename  <- "../hl/data/GiantOutput_glitchvslife_20170522_edited_03.txt"
sOutputFilename <- "../hl/tabs/analysis_glitchvslife_20170524_edited_03.txt"
sTitle <- "glitchvslife tests HL copies=var Audit=1yr Glitch=0,3333, dur=250,1000 lifem=var svrdeflife=0,100000 seed21"
sSubtitle <- "(is bad glitch worse than server finite life?)(data merged and subsetted)"
sSummarizeFilename <- "./summ-glitchvslife-4.r"
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

