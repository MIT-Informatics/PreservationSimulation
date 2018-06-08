################# testing
test.pba <- function() {
show(bernoulli(.3))
show(beta(2,3))         # B always gets clobbered
show(beta(0.1,0.1))
show(binomial(10,.2))
show(cauchy(10,1))
show(chi(4))
show(chisquared(14))
show(delta(3))
show(dirac(3))
show(discreteuniform(20))
show(exponential(2))
show(F(4,5))
show(f(4,5))
show(frechet(9,1))
show(gamma(2,3))
show(gamma1(5,1))
show(gamma2(3,2))
show(histogram(c(3,4,5,22,32)))
show(inversegamma(4,4))
show(geometric(.3))
#show(generalizedpareto(4,3,2))
#show(gev(2,4,5))
show(pascal(.3))
show(gumbel(2,3))
show(extremevalue(2,3))
show(laplace(2,3))
show(logistic(2,3))
show(L(5,1) )
show(lognormal(5,1) )
show(negativebinomial(10,.2))
show(N(5,1) )
show(normal(5,1))
show(gaussian(5,1))
show(pareto(5,1))
show(powerfunction(5,1))
show(powerfunction(5,10))
show(poisson(4))
show(rayleigh(4))
show(reciprocal(12))
show(reciprocal())
show(shiftedloglogistic(5,4,6))
if ("package:sn" %in% search()) show(skewnormal(6,1,2))
show(weibull(5,2))
show(U(2,4))
show(uniform(2,4))
show(rectangular(2,4) )
show(loguniform(2,4))
show(triangular(.2, .6, 1.2))
show(logtriangular(.2, .6, 1.2))
show(quantiles(c(3, 6, 10, 16, 25, 40), c(0, 0.2, 0.4, 0.5, 0.7, 1)))
show(quantiles(c(3, 6, 10, 16, 25, 40), c(0.1, 0.2, 0.4, 0.5, 0.7, 0.9)))  # p doesn't start at zero or end at one
show(pbox(c(1,1.2,3, 6, 10, 16, 25, 40)))  # default pointlist constructor
return(TRUE)
}


plot(runif(1000))
par(mfrow=c(4,5))
test.pba()


# testing poissonbinomial
p = rep(0.2, 20)
a = poissonbinomial(p)
b = binomial(20, 0.2)
plot(b,col='tan',lwd=4)
lines(a,col='blue')

testpb <- function(p) {
  if (class(p) == 'numeric')  p1 = p2 = p else {p1 = left(p); p2 = right(p)}
  a = poissonbinomial(p)
  pl(a)
  many = 10000
  s = rep(0,many)
  for (i in 1:length(p)) s = s + (runif(many) <= p1[i])
  edf.numeric(s,col='yellow',new=FALSE,lwd=4)
  s = rep(0,many)
  for (i in 1:length(p)) s = s + (runif(many) <= p2[i])
  edf.numeric(s,col='tan',new=FALSE,lwd=4)
  lines(a,col='red')
  }

testpb( c(0.1, 0.2, 0.3, 0.4, 0.5) )
testpb( c(0.1, interval(0.2, 0.3), interval(0.4, 0.5), I(0.1,0.3), I(.2,.24), I(0.19,0.23)) )
testpb( rep(c(I(0.1,0.14),I(0.7,0.8)),25) )


par(mfrow=c(1,1))
a = N(5,1)
b = exp(a)
exp(a)


r = sort(runif(15))
r = c(0.019764379132539, 0.0324148465879261, 0.321962385904044, 0.384120133006945,0.448278494412079, 0.545291637070477, 0.643749186070636, 0.714126582955942, 0.744521557586268, 0.753784047439694, 0.803039125632495, 0.895463747903705, 0.897065195254982, 0.908547935541719, 0.941706892568618)
c = d = pbox(r)
if ("package:splines" %in% search()) d = pbox(r,interpolation='spline')
plot(c)
lines(d,col='red')
edf(r,new=FALSE)
points(r,0:14/14)


a = N(5,1)
b = U(2,6)
c = conv.pbox(a,b)
d = conv.pbox(a,b,'*')
cc = a + b
dd = a * b
c;cc
d;dd


a = N(5,1)
b = U(2,6)
a < b       # 0.26 or so


a = N(5,1)
a + 2
2 + a
a + a
a + N(5,1)  # smaller variance

a - 2
2 - a
a - a
a - N(5,1)   # bigger variance

a * 2
2 * a
a * a
a * N(5,1)

a / 2
2 / a
a / a
a / N(5,1)     # bigger variance

a ^ 2
2 ^ a
a ^ a
a ^ N(5,1)

pmin(a,4)
#pmin(4,a)
pmin(pbox(4),a)
pmin(a,a)
pmin(a,N(5,1))

pmax(a,4)
#pmax(4,a)
pmax(pbox(4),a)
pmax(a,a)
pmax(a,N(5,1))

a = N(5,1); b = U(9,11); c = histogram(c(23,24,25,33,35))
mixture(a,b)
m = mixture.list(c(a,b,c))
m

bb = conv.pbox(a,a)
cc = perfectconv.pbox(a,a)
dd = perfectconv.pbox(a,N(5,1))
ee = oppositeconv.pbox(a,a)
ff = oppositeconv.pbox(a, N(5,1))
bb
cc
dd
ee
ff
bb
lines(cc,col='red')
lines(dd,col='blue')
lines(ee)
lines(ff,col='gray')


a = N(5,1)
b = U(2,3)
ab = perfectconv.pbox(a,b)
c = U(2,3,r=a)
ac = a+c
ab
lines(ac,col='blue')


a = N(5,1)
b = U(2,6)
-a
acos(a/10)
alpha(a,4)
and(U(0.1, 0.2), U(0.5,0.6))
asin(a/10)
#atan2(a,b)    #####
atan(a)
ceiling(a)
complement(a/10)
#cor(a,b)   #####
cut(a, 0.3)
exp(a)
#fivenum(a)  #####
fractile(a, 0.3)
iqr(a) 
#IQR(a)  #####
left(a)
log(a)
log(a,3)
#log(a,pbox(3))  #####
#log(a,U(2,3))  #####
max(a)
mean(a)
median(a)
min(a)
mixture.list(c(a,b),c(2,3))
mult(-2,a)
negate(a)
not(U(0.1, 0.2))        
or(U(0.1, 0.2), U(0.5,0.6))
percentile(a, 0.3)
pmax(a,b)
pmin(a,b)
prob(a,4)
random(a)
randomrange(a)
range(a)
reciprocate(a)
rep(a,3)
round(a)
right(a)
samedistribution(a)
specific(a)
sd(a)
#shift(-1,a)  #####
shift.pbox(-1,a)
sign(a)
sqrt(a)
steps(a)
trunc(a) 
truncate(a,3,6)
var(a)
xprob.pbox(a,0.3)


# make sure the old functions still work
-4.5
acos(0.45)
asin(0.45)
atan(4.5)
atan2(4,5)
ceiling(4.5)
cor(sort(runif(10)), sort(runif(10)))
exp(4.5)
fivenum(runif(45))
IQR(runif(45))
log(4.5)
log(4.5,3)
max(runif(14))
mean(runif(14))
median(runif(14))
min(runif(45))
pmax(runif(14),runif(14))
pmin(runif(14),runif(14))
range(runif(14))
rep(c(12,11),4)
round(4.5)
sd(runif(14))
sign(runif(14)-0.3)
sqrt(9)
trunc(4.5) 
var(runif(14))


par(mfrow=c(1,1))
x1 = poisson(5)
pl(range(min(x1),max(x1+30)))
bla(x1)
red(x1+2)
blu(x1+4) 
gre(x1+6)
kha(x1+8) 
nav(x1+10) 
pur(x1+12) 
bro(x1+14) 
oli(x1+16) 
gra(x1+18) 
ora(x1+20) 
pin(x1+22) 
cya(x1+24) 
cha(x1+26)
gol(x1+28)
bri(x1+30)
ecr(x1+32)


above(a,5.5)
highest(a,70)

massreassignexamples <- function(a = N(5,1), b = U(4,5), th = 4, ith = interval(4,5), pth = 25) {
  splot <- function(s,name=NULL,cumulative=Pbox$cumulative, col=NULL, ...) {
   if (!is.vacuous(s)) {
    if (missing(name)) name <- s@name
    i = 0:(s@n-1) / s@n
    if (cumulative) ylab = '' else ylab = ''
    if ("xlim" %in% attributes(list(...))$names) 
      plot(c(s@u[[1]],s@d[[s@n]]),c(0,1),xlab=name, ylab=ylab, col='white', ...) else 
      plot(c(s@u[[1]],s@d[[s@n]]),c(0,1),xlim=range(c(s@u[is.finite(s@u)],s@d[is.finite(s@d)])),xlab=name, ylab=ylab, col='white', ...)
    if (is.infinite(s@u[[1]])) text(min(s@u[is.finite(s@u)]),-.01,"-Inf")
    if (is.infinite(s@d[[s@n]])) text(max(s@d[is.finite(s@d)]),1.02,"Inf")
    if (is.null(col)) color <- 'red' else color <- col
    lines(c(s@u,s@u[[s@n]],s@d[[s@n]]),updown(cumulative,c(i,1,1)),type="S", col=color, ...)
    i = 1:(s@n) / s@n
    if (is.null(col)) color <- 'black'
    lines(c(s@u[1],s@d[1],s@d),updown(cumulative,c(0,0,i)),type="s", col=color, ...)
    # bringToTop(-1) # return focus to R console
    }}
  abelow = below(a,th)
  aabove = above(a,th)
  alowest = lowest(a,pth)
  ahighest = highest(a,pth)
  apmin = pmin(a,b)
  apmax = pmax(a,b)
  apmini = a %|m|% b
  apmaxi = a %|M|% b
  asmin = smin(a,b)
  asmax = smax(a,b)
  abetween = between(a,left(ith),right(ith))
  abetween2 = between(a, left(cut(a,pth/100)), right(cut(a,1-pth/100)))
  atruncate = truncate(a,left(ith),right(ith))
  arescale = rescale(a,left(ith),right(ith))
  aenv = env(a,b)
  atrunc = trunc(a)
  aint = int(a)
  around = round(a)
  aceiling = ceiling(a)
  acensor = censor(a,left(ith),right(ith))
  old.par <- par(mfrow=c(4,5),mar=c(2,4,3,1))
  splot(a,col='gray',main='highest'); lines(c(0,10),1-c(pth,pth)/100,lty='dotted',col='blue'); lines(ahighest,lwd=3)
  splot(a,col='gray',main='above');   lines(c(th,th),c(0,1),lty='dotted',col='blue'); lines(aabove,lwd=3)
  splot(a,col='gray',main='smax');    lines(b,col='blue');   lines(asmax,lwd=3)
  splot(a,col='gray',main='%|M|%');   lines(b,col='blue');   lines(apmaxi,lwd=3)
  splot(a,col='gray',main='pmax');    lines(b,col='blue');   lines(apmax,lwd=3)
  splot(a,col='gray',main='lowest');  lines(c(0,10),c(pth,pth)/100,lty='dotted',col='blue'); lines(alowest,lwd=3)
  splot(a,col='gray',main='below');   lines(c(th,th),c(0,1),lty='dotted',col='blue'); lines(abelow,lwd=3)
  splot(a,col='gray',main='smin');    lines(b,col='blue');   lines(asmin,lwd=3)
  splot(a,col='gray',main='%|m|%');   lines(b,col='blue');   lines(apmini,lwd=3)
  splot(a,col='gray',main='pmin');    lines(b,col='blue');   lines(apmin,lwd=3)
  splot(a,col='gray',main='between(cut,cut)'); lines(abetween2,lwd=3); lines(c(2.5,2.5),c(pth/100,1-pth/100),col='blue',lty='dotted')
  splot(a,col='gray',main='between'); lines(abetween,lwd=3); lines(c(left(ith),right(ith)),c(0,0),col='blue',lty='dotted')
  splot(a,col='gray',main='truncate');lines(atruncate,lwd=3);lines(c(left(ith),right(ith)),c(0,0),col='blue',lty='dotted')
  splot(a,col='gray',main='rescale'); lines(arescale,lwd=3); lines(c(left(ith),right(ith)),c(0,0),col='blue',lty='dotted')
  splot(a,col='gray',main='env');     lines(aenv,lwd=3)
  splot(a,col='gray',main='ceiling'); lines(aceiling,lwd=3); 
  splot(a,col='gray',main='round');   lines(around,lwd=3); 
  splot(a,col='gray',main='trunc');   lines(atrunc,lwd=3); 
  splot(a,col='gray',main='int');     lines(aint,lwd=3); 
  splot(a,col='gray',main='censor');  lines(acensor,lwd=3); 
  par(old.par)
  }

massreassignexamples()
