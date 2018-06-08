################# testing
test.mc <- function() {
show(bernoulli(.3))
show(B(2,3))
show(beta(2,3))
show(beta(0.1,0.1))
show(Bin(10,.2))
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
show(generalizedpareto(4,3,2))
show(gev(2,4,5))
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
show(quantiles(v = c(3, 6, 10, 16, 25, 40), p = c(0, 0.2, 0.4, 0.5, 0.7, 1)))
# show(quantiles(v = c(3, 6, 10, 16, 25, 40), p = c(0.1, 0.2, 0.4, 0.5, 0.7, 0.9)))  # p doesn't start at zero or end at one
show(mc(c(1,1.2,3, 6, 10, 16, 25, 40)))  # default pointlist constructor
show(betapert(20,60,25))
show(MEminmax(2,5))
show(MEminmaxmean(10, 20, 12))
show(MEmeansd(5,1))
show(MEminmean(0,5))
#show(MEmeangeomean(10,5))  #####
show(MEdiscretemean(1:10,2.3))
show(MEquantiles(v = c(3, 6, 10, 16, 25, 40), p = c(0, 0.2, 0.4, 0.5, 0.7, 1)))
show(MEdiscreteminmax(0,10))
show(MEmeanvar(0.2,0.02))
show(MEminmaxmeansd(0,1,0.2,0.02))
show(MEminmaxmeanvar(0,1,0.2,0.02))
return(TRUE)
}


plot(runif(1000))
par(mfrow=c(4,5))
test.mc()


par(mfrow=c(1,1))
a = N(5,1)
b = exp(a)
exp(a)


r = sort(runif(15))
r = c(0.019764379132539, 0.0324148465879261, 0.321962385904044, 0.384120133006945,0.448278494412079, 0.545291637070477, 0.643749186070636, 0.714126582955942, 0.744521557586268, 0.753784047439694, 0.803039125632495, 0.895463747903705, 0.897065195254982, 0.908547935541719, 0.941706892568618)
c = d = mc(r)
if ("package:splines" %in% search()) d = mc(r,interpolation='spline')
plot(c)
lines(d,col='red')
edf(r,new=FALSE)
points(r,0:14/14)


a = N(5,1)
b = U(2,6)
c = conv.mc(a,b)
d = conv.mc(a,b,'*')
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
pmin(mc(4),a)
pmin(a,a)
pmin(a,N(5,1))

pmax(a,4)
pmax(mc(4),a)
pmax(a,a)
pmax(a,N(5,1))

a = N(5,1); b = U(9,11); c = histogram(c(23,24,25,33,35))
m = mixture(c(a,b,c))
m

bb = conv.mc(a,a)
cc = perfectconv.mc(a,a)
dd = perfectconv.mc(a,N(5,1))
ee = oppositeconv.mc(a,a)
ff = oppositeconv.mc(a, N(5,1))
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
ab = perfectconv.mc(a,b)
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
atan(a)
atan2(a,b)
ceiling(a)
complement(a/10)
cor(a,b)
cut(a, 0.3)
exp(a)
fivenum(a)
fractile(a, 0.3)
iqr(a) 
IQR(a)
left(a)
log(a)
log(a,mc(3))
log(a,U(2,3))
max(a)
mean(a)
median(a)
min(a)
mixture(c(a,b),c(2,3))
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
reps(a)
round(a)
right(a)
samedistribution(a)
specific(a)
sd(a)
shift(-1,a)
sign(a)
sqrt(a)
trunc(a) 
truncate(a,3,6)
var(a)
xprob.mc(a,0.3)


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
pl(range(x1),range(x1+30))
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
tan(x1+32)


S = c(
  1.00,  0.83,  0.83,  0.83, 
  0.83,  1.00,  0.83,  0.83, 
  0.83,  0.83,  1.00,  0.83, 
  0.83,  0.83,  0.83,  1.00)

S = c(  # this matrix is not positive definite
  1.00,  0.30,  0.83, -0.20, 
  0.30,  1.00,  0.00,  0.25, 
  0.83,  0.00,  1.00,  0.25, 
 -0.20,  0.25,  0.25,  1.00)

S = c(                        
  1.00,  0.60, -0.30,  0.40, 
  0.60,  1.00, -0.40,  0.90, 
 -0.30, -0.40,  1.00, -0.25, 
  0.40,  0.90, -0.25,  1.00)

correlations(S)

w = uniform(2,5, r=MC$r[,1])
x = poisson(5,   r=MC$r[,2])
y = gumbel(2,3,  r=MC$r[,3])
z = normal(6,1,  r=MC$r[,4])

# alternatively, you can define a little function:
R = function(i,corrs=MC$r) return(corrs[,i])

W = uniform(2,5, r=R(1))
X = poisson(5,   r=R(2))
Y = gumbel(2,3,  r=R(3))
Z = normal(6,1,  r=R(4))

cor(w,W)
cor(x,X)
cor(y,Y)
cor(z,Z)

plot(x)
plot(x,'Weight')
plot(x,z)

Sigma

cor(w,x)
cor(w,y)
cor(w,z)

plotcorrs(c(w,x,y),names=c('w','x','y'),MC$many)
plotcorrs(c(w,x,y),names=c('w','x','y'),col='red')
plotcorrs(c(w,x,y),names=c('w','x','y'))
plotcorrs(c(w,x,y,z),names=c('w','x','y','z'))
plotcorrs(c(w,x,y,z,z),names=c('w','x','y','z','a'))


S = c(
  1.00,  0.83, 
  0.83,  1.00)
correlations(S)
a = mc(MC$r[,1])
b = mc(MC$r[,2])
cor(a,b)
plotcorrs(c(a,b))

S = c(
  1.00,  0.83,  0.83,   
  0.83,  1.00,  0.83,   
  0.83,  0.83,  1.00)
correlations(S)
a = mc(MC$r[,1])
b = mc(MC$r[,2])
c = mc(MC$r[,3])
plotcorrs(c(a,b,c),c('a','b','c'))

S = c(                        
  1.00,  0.60, -0.30,  0.40,  0.00,
  0.60,  1.00, -0.40,  0.90,  0.00, 
 -0.30, -0.40,  1.00, -0.25,  0.00, 
  0.40,  0.90, -0.25,  1.00,  0.00,
  0.00,  0.00,  0.00,  0.00,  1.00)
correlations(S)
a = mc(MC$r[,1])
b = mc(MC$r[,2])
c = mc(MC$r[,3])
d = mc(MC$r[,4])
e = mc(MC$r[,5])
plotcorrs(c(a,b,c,d,e),c('a','b','c','d','e'))


checkMM = function(x, MM) {
  d = MM(x)
  m = mean(x)
  s = sd(x)
  mm = mean(d)
  ss = sd(d)
  cat(signif(m,4),'  ',signif(s,4),'\n')
  cat(signif(mm,4),'  ',signif(ss,4),'\n\n')
  }

some = 1:25
checkMM((runif(some)<0.25)[some],MMbernoulli) 
checkMM(beta(2,3)@x[some],MMbeta) 
checkMM(binomial(30,0.3)@x[some],MMbinomial) 
checkMM(chisquared(5)@x[some],MMchisquared) 
checkMM(exponential(4)@x[some],MMexponential) 
checkMM(F(12,13)@x[some],MMF )
checkMM(gamma(2,3)@x[some],MMgamma) 
checkMM(geometric(0.25,6)@x[some],MMgeometric) 
checkMM(gumbel(2,3)@x[some],MMgumbel) 
checkMM(lognormal(4,1)@x[some],MMlognormal) 
checkMM(laplace(3,2)@x[some],MMlaplace)
checkMM(logistic(2,3)@x[some],MMlogistic)
#checkMM(loguniform(1,100)@x[some],MMloguniform) ##########
checkMM(normal(5,1)@x[some],MMnormal)
checkMM(pareto(2,3)@x[some],MMpareto) 
checkMM(poisson(4)@x[some],MMpoisson) 
checkMM(powerfunction(2,3)@x[some],MMpowerfunction )
checkMM(student(3)@x[some],MMstudent)
checkMM(uniform(6,18)@x[some],MMuniform) 


above(a,5.5)
highest(a,70)

massreassignexamples <- function(a = N(5,1), b = U(4,5), th = 4, ith = c(4,5), pth = 25) {
  splot <- function(s, xlab='', ylab='Cumulative probability', cumulative=MC$cumulative, ...) {
    if (!cumulative) ylab = 'Exceedance probability'
    plot(c(min(s@x),sort(s@x)),updown(cumulative,seq(0,1,length.out=1+length(s@x))),type='s', xlab=xlab,ylab=ylab,...)
    bringToTop(-1) # return focus to R console
    }
  abelow = below(a,th)
  aabove = above(a,th)
  alowest = lowest(a,pth)
  ahighest = highest(a,pth)
  apmin = pmin(a,b)
  apmax = pmax(a,b)
  asmin = smin(a,b)
  asmax = smax(a,b)
  abetween = between(a,left(ith),right(ith))
  abetween2 = between(a, left(cut(a,pth/100)), right(cut(a,1-pth/100)))
  atruncate = truncate(a,left(ith),right(ith))
  arescale = rescale(a,left(ith),right(ith))
  atrunc = trunc(a)
  around = round(a)
  aceiling = ceiling(a)
  old.par <- par(mfrow=c(4,4),mar=c(2,4,3,1))
  splot(a,col='gray',main='lowest');  lines(c(0,10),c(pth,pth)/100,lty='dotted',col='blue'); lines(alowest,lwd=3)
  splot(a,col='gray',main='below');   lines(c(th,th),c(0,1),lty='dotted',col='blue'); lines(abelow,lwd=3)
  splot(a,col='gray',main='above');   lines(c(th,th),c(0,1),lty='dotted',col='blue'); lines(aabove,lwd=3)
  splot(a,col='gray',main='highest'); lines(c(0,10),1-c(pth,pth)/100,lty='dotted',col='blue'); lines(ahighest,lwd=3)
  splot(a,col='gray',main='truncate');lines(atruncate,lwd=3);lines(c(left(ith),right(ith)),c(0,0),col='blue',lty='dotted')
  splot(a,col='gray',main='rescale'); lines(arescale,lwd=3); lines(c(left(ith),right(ith)),c(0,0),col='blue',lty='dotted')
  splot(a,col='gray',main='between(cut,cut)'); lines(abetween2,lwd=3); lines(c(2.5,2.5),c(pth/100,1-pth/100),col='blue',lty='dotted')
  splot(a,col='gray',main='between'); lines(abetween,lwd=3); lines(c(left(ith),right(ith)),c(0,0),col='blue',lty='dotted')
  splot(a,col='gray',main='pmin');    lines(b,col='blue');   lines(apmin,lwd=3)
  splot(a,col='gray',main='pmax');    lines(b,col='blue');   lines(apmax,lwd=3)
  splot(a,col='gray',main='smin');    lines(b,col='blue');   lines(asmin,lwd=3)
  splot(a,col='gray',main='smax');    lines(b,col='blue');   lines(asmax,lwd=3)
  splot(a,col='gray',main='ceiling'); lines(aceiling,lwd=3); 
  splot(a,col='gray',main='round');   lines(around,lwd=3); 
  splot(a,col='gray',main='trunc');   lines(atrunc,lwd=3); 
  par(old.par)
  }

massreassignexamples()
