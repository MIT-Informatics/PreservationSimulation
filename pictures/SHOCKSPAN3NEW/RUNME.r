# where to run?
# setwd("C:/cygwin64/home/landau/working/PreservationSimulation/pictures/SHOCKSPAN3NEW")
setTimeLimit(elapsed=300)
debugprint<-0
# Quarterly audits
source("./GetShockSpan3Server3Seg4Data.r")
source("./GetShockSpan3Server4Seg4Data.r")
#source("./GetShockSpan3Server5Seg4Data.r")
#source("./GetShockSpan3Server8Seg4Data.r")
#source("./GetShockSpan3Server10Seg4Data.r")
# Monthly audits
source("./GetShockSpan3Server3Seg10Data.r")
source("./GetShockSpan3Server4Seg10Data.r")
# Weekly audits
source("./GetShockSpan3Server3Seg50Data.r")
source("./GetShockSpan3Server4Seg50Data.r")
