# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/pictures/SHOCKSPAN3NEW4")
setTimeLimit(elapsed=300)
debugprint<-0
# Quarterly audits
source("./GetShockSpan3Server4Seg4Data.r")
# Monthly audits
source("./GetShockSpan3Server4Seg10Data.r")
# Weekly audits
source("./GetShockSpan3Server4Seg50Data.r")
