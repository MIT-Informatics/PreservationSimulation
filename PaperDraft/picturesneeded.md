<head>
<style>
th {
background-color: yellow;
font-family: sans-serif;
}
td {
border: 1px solid black;
}
table {
width: 80%;
border-collapse: collapse;
}
</style>
</head>

# Pictures we need for the paper

--- 
(Note: the numbers are just for reference during discussions and editing.)


| | idea | basics | details | wayzit | 
|-|-----------------|------------|-----------------------|-----------|
|1| no audit requires too many copies | losses by #copies | copies=1,2,3,5,10, lifem2-1000 | |
|2a| describe data plots | #copies, losses, error injection | log scales x and y, percent losses, trimmed means (25%=midmean, maybe only 10%) of sample size=21, colors=black or blue usually best case recommendation |  |
|2b| describe model: boxes and lines picture | client, collection, documents, servers, copies | errors and failures injected by time, glitches, shocks |  |
|3| random auditing is less effective than total auditing | total annual vs random | random segments=4,10, dotted lines; total=solid line |  |
|4| annual auditing suffices | total annual vs total qtly | copies=3,4,5 |  |
|5| segmented total auditing is slightly better | annual with varying segments | segments=1,2,4,10 show only marginal improvements |  |
|6| 5 copies and annual auditing is effective | lifem-losses plot, losses show zero from 10 to 1000 mhr lifetimes | notes about "you wouldn't use a disk this bad" for <10 and "you can't buy a disk this good" for >1000 |  |
|7| docsize and error rates scale together linearly | lifem-losses plot | separate lines and colors for various doc sizes |  |
|8| glitches the same as increased error rates | copies=3,4,5 | lines for no glitch, medium, and bad |  |
|9| copies=1 losses over time | copies=1 from garbage can lids to immortal disks | lifem2-10000 |  | 
|10| 5 is enough but 4 is not | lifem-losses copies4,5  | show errors down to 2 or 1 mhr |  |
|11a| severe shocks may require 6 copies | copies=4,5,6 | freq2yr dur1yr span3 imp50,80 |  | 
|11b| severe shocks may require 6 copies | copies=4,5,6 | freq2yr dur1yr span2 imp50,80 |  | 
|11c| severe shocks may require 6 copies | copies=4,5,6 | freq1yr dur0.5yr span2 imp50,80 |  | 
|12| how long before lose 1% of collection | lifem-losses plot | separate lines for 5,10,15,20 years, copies3,4,5 with annual audit |  |
|13| table: small vs large docs | small matrix, cols=lifem, rows=5,50,500,5000MB | losses in ppm |  |
|14| table: calibration | theoretical vs simulated results | copies=1, 100 samples, vs straight Poisson, in ppm |  |
|15|  |  |  |  |
|16|  |  |  |  |
||  |  |  |  |
||  |  |  |  |
||  |  |  |  |
