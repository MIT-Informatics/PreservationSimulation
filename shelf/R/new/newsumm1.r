# try this

trimean <-  function(vect)  { foo <- fivenum(vect); ans <- 0.5*foo[3] + 0.25*foo[2] + 0.25*foo[4]; ans }
midmean <-  function(vect)  { ans <- mean(vect,trim=0.25,na.rm=TRUE); ans }

foo<-dat
bar<-data.frame(foo$copies,foo$lifem,foo$lost,
                foo$shockfreq,foo$shockimpact,
                foo$shockspan,foo$shockmaxlife)
d0<-bar
datsumm<-data.frame(rbind(numeric(6)))
colnames(datsumm)<-c("span","lifem","cop2","cop3","cop4","cop5")

c1<-d0$foo.shockspan
f1<-levels(factor(c1))
for (s1 in f1) {d1<-data.frame(d0[c1==s1,])
  
  c2<-d1$foo.lifem
  f2<-levels(factor(c2))
  for (s2 in f2) {d2<-data.frame(d1[c2==s2,])
      
      tmp11 <- aggregate(d2, by=list(d2$foo.copies), 
        FUN=midmean)
      newrow<-c(s1,s2,round(tmp11$foo.lost,1))
      #print(newrow)
      datsumm <- rbind(datsumm,as.numeric(newrow))
  }
}

datsumm<-datsumm[-1,]
print(datsumm)
while (sink.number() > 0) {sink()}


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
      FUN=midmean)
    newrowrev<-c(s1,s2,round(tmp11$foo.lost,1))
    #print(newrowrev)
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

