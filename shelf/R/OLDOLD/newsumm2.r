# try this
foo<-dat
bar<-data.frame(foo$copies,foo$lifem,foo$lost,
                foo$shockfreq,foo$shockimpact,
                foo$shockspan,foo$shockmaxlife)
d0<-bar
datsumm<-data.frame(rbind(numeric(6)))
colnames(datsumm)<-c("span","lifem","cop2","cop3","cop4","cop5")


sVar1 = "shockspan"
sVar2 = "lifem"

groupby2 <- function(sVar1, sVar2, sLabel1, sLabel2)
{

assign(paste0("d0$foo.",sVar1), get(paste0("d0$foo.",sVar1)))
assign(paste0("mine.",sVar1), get(paste0("d0$foo.",sVar1)))



    c1<-d0$foo.shockspan
    f1<-levels(factor(c1))
    for (s1 in f1) {d1<-data.frame(d0[c1==s1,])
      
      c2<-d1$foo.lifem
      f2<-levels(factor(c2))
      for (s2 in f2) {d2<-data.frame(d1[c2==s2,])
          
          tmp11 <- aggregate(d2, by=list(d2$foo.copies), 
            FUN=mean)
          newrow<-c(s1,s2,round(tmp11$foo.lost,1))
          print(newrow)
          datsumm <- rbind(datsumm,as.numeric(newrow))
      }
    }

    datsumm<-datsumm[-1,]
    print(datsumm)
    while (sink.number() > 0) {sink()}





}




if(1){
# now do it in the other order.
datsummrev<-data.frame(rbind(numeric(6)))
colnames(datsummrev)<-c("lifem","span","cop2","cop3","cop4","cop5")

c1<-d0$foo.lifem
f1<-levels(factor(c1))
for (s1 in f1) {d1<-data.frame(d0[c1==s1,])
  
  c2<-d1$foo.shockspan
  f2<-levels(factor(c2))
  for (s2 in f2) {d2<-data.frame(d1[c2==s2,])

    tmp11 <- aggregate(d2, by=list(d2$foo.copies), 
      FUN=mean)
    newrowrev<-c(s1,s2,round(tmp11$foo.lost,1))
    print(newrowrev)
    datsummrev <- rbind(datsummrev,as.numeric(newrowrev))
  }
}

datsummrev<-datsummrev[-1,]
print(datsummrev)
while (sink.number() > 0) {sink()}
}#ENDIFFALSE

sink("tmp.txt")
print(datsumm)
print(datsummrev)
sink()

while (sink.number() > 0) {sink()}


#conclusion 20170321.1345: nope, the aggregation is being done on 
#some other planet.  closer examination required.  the shape is right, 
#though.  
#conclusion 20170321.1620: almost seems to work!  bronze it and try more!

if(0){
# hint from stackoverflow "r string as variable"
eval(parse(text="somestring"))
#that might have been paste0-ed from parts.

# someone said as.name() is useful, too.  haven't tried.  
# i think they meant as.symbol() which goes the other way.
# nope.

# also assign
assign("somestring", somevalue)
# this actually works
assign(paste0("dx$foo.","crud"), d0$foo.lifem)
# might be the answer

# this perverted piece of crap sort of does what i want
name2<-assign("anystring", eval(parse(text= )))

# and get() may avoid the evil eval
levels(factor(get(paste0("d0$foo.","lifem"))))

# and this might help get the labels associated with columns
original_string <- c("x=123", "y=456")
pairs <- strsplit(original_string, "=")
lapply(pairs, function(x) assign(x[1], as.numeric(x[2]), envir = globalenv()))
ls()

# also check this out
#> mydf <- data.frame( g=c('a','b','c') )
#> ID <- 1
#> 
#> mydf[[ sprintf("VAR%02d",ID) ]] <- 1:3
#> mydf
#  g VAR01
#1 a     1
#2 b     2
#3 c     3

obj<-list(a=1,b=2)

# or this pernicious example
x <- as.list(rnorm(10))
names(x) <- paste("a", 1:length(x), sep = "")
list2env(x , envir = .GlobalEnv)

# tres simple ideas from Micah
# boy, am i embarrassed that i didn't remember or try these.

varname<-"lifem"
d0[varname]
# and yes, varname can be pasted together from pieces parts.

d0[c('a','b')]

seq(1:length(foo))

d0[d0["lifem"]==100 & d0["shockspan"]==1]

?subset()

# look at tidyverse package, esp. spread and gather
# look at reshape2, esp. melt and cast (already did at some length)

# put labels and varnames into a data.frame, dummy.
name<-c("shockspan","lifem")
label<-c("span","lifetime")
nx<-data.frame(cbind(name,label))

seq_len(thing) 
# gets right range even if zero elements in thing

# and the simple way
for(i in 1:nrow(dataFrame)) {
    row <- dataFrame[i,]
    # do something
}
for(i in seq_len(nrow(nx))) {
     rrow <- data.frame(nx[i,])
     print(rrow$name); print(rrow$label)
}

by(dataFrame, 1:nrow(dataFrame), function(row) dostuff)
by(dataFrame, seq_len(nrow(dataFrame)), function(row) dostuff)

apply(Data, 1, function(row) {
    name <- row["name"]
    age <- row["age"]
    #do something cool here
})
# woiks

midmean <-  function(vect)  { ans <- mean(vect,trim=0.25,na.rm=TRUE); ans }
x <- ddply(foo, .(shockfreq, shockimpact,shockspan,lifem,copies), summarise,(lostdocs = midmean(lost)))
y = arrange(x,lifem,shockspan)
z = arrange(x,shockspan,lifem)
# the midmeans seem to be wrong, but at least it didn't fail horribly.

x <- ddply(dat, .(shockfreq, shockimpact,shockspan,lifem,copies), summarise,lost=midmean(lost), docslost=midmean(docslost))
y = arrange(x,shockimpact,lifem,shockspan)
z = arrange(x,shockimpact,shockspan,lifem)

q=subset(dat, subset=(seed==919028296))

q=subset(d0, subset=(foo$shockspan==1 & foo$lifem==10 & foo$copies==3))[1:3,]




dfx <- data.frame(
  group = c(rep('A', 8), rep('B', 15), rep('C', 6)),
  sex = sample(c("M", "F"), size = 29, replace = TRUE),
  age = runif(n = 29, min = 18, max = 54)
)

a = ddply(dfx, .(group), summarise, N=length(age), avg=mean(age))
a = ddply(dfx, .(group), summarise, N=length(age), avg=mean(age), max=max(age), min=min(age), med=median(age))





# TADA!!! this incredibly seems to work!
require(plyr)
x <- ddply(dat, 
    .(shockfreq, shockimpact,shockmaxlife,shockspan,lifem,copies), 
    summarise, 
    N=length(copies), sum=sum(lost), mean=mean(lost), mid=midmean(lost), med=median(lost)
)
# fix the ordering of columns
x <- ddply(dat, 
    .(shockfreq, shockimpact,shockmaxlife,shockspan,lifem,copies), 
    summarise, 
    midmean.lost=midmean(lost), median=median(lost), mean=mean(lost), N=length(copies)
)
zz<-arrange(x, shockimpact, shockmaxlife, shockspan, copies, lifem)
yy<-arrange(x, shockimpact, shockmaxlife, shockspan, lifem, copies)

# separate the column list from the work.
collist<-.(shockfreq, shockimpact,shockmaxlife,shockspan,lifem,copies)
aa<-ddply(dat, collist, summarise, mid.lost=midmean(lost))




}