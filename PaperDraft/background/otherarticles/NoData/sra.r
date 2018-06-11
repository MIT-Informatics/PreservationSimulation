
RStudio = FALSE

##########################################################################
# Monte Carlo Simulation S4 Library for the R Language                
#                                                                          
# Proprietary software of Applied Biomathematics (www.ramas.com)           
# Author: Scott Ferson, Applied Biomathematics, sandp8@gmail.com                             
# Copyright 2015 Applied Biomathematics; All rights reserved worldwide     
##########################################################################
#
# Place this file on your computer and, from within R, select 
# File/Source R code... from the main menu.  Select this file and
# click the Open button to read it into R.  You should see the 
# completion message ":sra> library loaded".  Once the library 
# has been loaded, you can define probability distributions 
#
#       a = normal(5,1)
#       b = uniform(2,3)
#
# and perform mathematical operations on them, including
# convolutions such as 
#
#       a  +  b
#
# or generalized convolutions such as 
#
#       a + b * beta(2,3) / a 
#
# Many different distribution shapes are supported via the following
# functions
#
#       bernoulli, beta (B), binomial (Bin), cauchy, chi, chisquared, 
#       delta, dirac, discreteuniform, exponential, exponentialpower, 
#       extremevalue, F, f, fishersnedecor, fishertippett, fisk, frechet, 
#       gamma, gaussian, geometric, generalizedextremevalue (GEV), 
#       generalizedpareto, gumbel, histogram, inversegamma, laplace, 
#       logistic, loglogistic, lognormal (L), logtriangular, loguniform, 
#       negativebinomial, normal (N), pareto, pascal, powerfunction, 
#       poisson, quantiles, rayleigh, reciprocal, shiftedloglogistic, 
#       skewnormal (SN), student, trapezoidal, triangular (T), 
#       uniform (U), weibull 
#
# Note that the quantiles and histogram functions allow you to 
# create distributions of arbitrary shape.
#
# You can use regular mathematical operations such as +, -, *, /, 
# and ^ to compute with these distributions. In addition to these 
# standard operations, several other unary and binary functions
# are also supported 
#
# Several standard and new mathematical transformations and 
# binary functions have also been defined or extended to handle 
# probability distributions, including
#
#       exp, log, sqrt, abs, round, trunc, ceiling, floor, sign, 
#       sin, cos, tan, asin, acos, atan, atan2, reciprocate, negate, 
#       mixture, pmin, pmax, and, or, not, complement
#
# By default, separately constructed distributions such as a and 
# b above are assumed to be independent.  Distributions arising
# in calculations are typically independent of one another unless 
# one depends on the other, which happens if one was created 
# as a function of the other. For instance, assigning a variable 
# containing a probability distribution to another variable makes 
# the two variables perfectly dependent.  To create a copy of the
# values distribution that is independent of it, you can use the
# samedistribution function, e.g., c = samedistribution(a). 
#
# You can account for perfect or opposite dependencies between 
# distributions by mentioning their dependence when you 
# construct them with expressions like 
#
#       d = beta(2,5, r=a)  # perfect dependence (comonotonicity)
# or
#       d = beta(2,5, r=-a) # opposite dependence (countermonotonicity)
#
# In the first example, the variable d will be perfectly dependent 
# with the variable a.  In the second case, because of the minus 
# sign in front of the a, the variables d and a will be oppositely 
# dependent.
#
# Perfect and opposite dependencies are automatically mutual, 
# so it is not necessary to explicitly make any reciprocal 
# assignments.  Thus
#
#       a = N(5,1)
#       b = U(2,3, r=a)
#       c = N(15,2, r=b)
#
# suffices to link c with a and vice versa.  The assignments
# automatically make a, b, and c mutually perfectly dependent.  
# Naturally, it is not possible to be perfectly (or oppositely) 
# dependent on more than one quantity unless they are also 
# mutually dependent in the same way.  
#
# It is also possible to specify intermediate correlations 
# (between opposite and perfect that are not independent) 
# although the method for doing this is approximate, so you
# should always check that your realized correlations are close
# to the correlations you planned. Generating these intermediate 
# correlations requires that you install the MASS package for R.
# Specify intermediate dependencies among several variables in 
# a matrix of Pearson correlation coefficients, and call the # correlations function to produce "r" vectors for use in 
# constructing each variable, deploying them as in the following 
# example:
#
# # planned correlation matrix
# s = c( 1.00,  0.60, -0.30,
#        0.60,  1.00, -0.40,
#       -0.30, -0.40,  1.00)
# 
# correlations(s)   # read corr matrix s to generate "r" vectors
# 
# w = uniform(2,5, r=MC$r[,1])    
# x = poisson(5,   r=MC$r[,2])
# y = gumbel(2,3,  r=MC$r[,3])
# 
# # pairwise bivariate plots
# plotcorrs(c(w,x,y),names=c('w','x','y'))  
# corrs(c(w,x,y))
# 
# Dependence between variables can have dramatic effects
# on any calculations that involve these variables.  Typically
# the Monte Carlo simulations take account of the dependence
# automatically.  You can alternatively force the software to 
# assume two variables have perfect or opposite dependence 
# when you do operations on them.  For instance, you may
# assume perfect dependence with an expression like
#
#       perfectconv.mc(a, b, '*')
#
# or assume oposite dependence with an expression like
#
#       oppositeconv.mc(a, b, '+')
#
# After making the calculations, however, a and b are not 
# correlated with each other.
#
# Several standard commands allow you to see the resulting
# distributions, such as
#
#       show(c)
#       summary(d)
#       plot(a)
#       lines(b, col='blue')
#
# By default, entering a distribution's name will also show
# it graphically.  Set MC$plotting to FALSE to turn this off.
#
# There are a variety of standard and new functions you can 
# use with distributions to characterize them, such as 
#
#       mean, sd, var, median, quantile, fivenum, left, right,
#       prob, cut, percentile, iqr, IQR, random, specific, cor
#
# Programming in R is imperfect.  Although distributions 
# can be mixed together with real values in most operations, 
# this is not possible with some functions including pmin, 
# pmax, log, and mixture.  If you need to include real values 
# among the argument for these functions, you may need 
# to wrap the real values with the mc function. For instance, 
# pmin(mc(5), normal(5,1)) works as expected, but 
# pmin(5, normal(5,1)) will precipitate an error.
# 
##########################################################################


##########################################################################
# Global constants #
##########################################################################
MC <- new.env()
MC$many <- 20000                # Monte Carlo replications (increase for better precision)
MC$plotting <- TRUE              # if TRUE, distributions are plotted whenever they are "show"n
MC$plotting.every <- FALSE    # if TRUE, every distribution that's created is automatically plotted
MC$cumulative <- TRUE          # if TRUE, plot CDFs, if FALSE, plot CCDFs (exceedance risks)
MC$distribs = 0                      # number of Monte Carlo distributions that have been created
MC$verbose = 2                     # how much warning messaging is wanted
MC$r = 0                               # place for the correlations function to put its correlated sequences

# minimize footprint
if ("quiet" %in% ls()) MC$scott.used.to.be.quiet <- quiet

####################################
# Some ancillary utility functions 
####################################

Gamma <- gammafunc <- function(x) .Primitive("gamma")(x)  # 'gamma' is redefined to be a distribution

ami <- function(i,j) isTRUE(all.equal(i,j)) 

##########################################################################
# Class specification and general MC distribution constructor 
##########################################################################

quiet <- setClass('mc',representation(x='numeric', n='integer', bob='integer', id='character')) 

uniquemc <- function() { MC$distribs <- MC$distribs + 1; return(paste(MC$distribs)) }

mc <- function(x, perfect=NULL, opposite=NULL, bob=NULL, interpolation='linear') {
  if (missing(x)) x <- rep(0,MC$many) 
  if (inherits(x,'mc')) p <- x  else
    {
      if (!is.number(x)) stop('Monte Carlo distribution must be numerical') 
      if (length(x) != MC$many) x <- interpolate(x,interpolation); 
      unique <- uniquemc()
      id <- paste('MC',unique,sep='')
      if (!missing(bob)) unique <- bob
      p <- new("mc", x=x, n=as.integer(MC$many), bob=as.integer(unique), id=id)
    }
  class(p) <- c('mc')
  if (MC$plotting.every) try(plot.mc(p))
  p
  }

as.mc <- as.mc.numeric <- as.mc.interval <- mc

makemc <- function(...) {  #  works for a bunch of args separated by commas, or for a single list of args
  elts <- list(...)
  if (mode(elts[[1]])=='list') elts <- elts[[1]]
  if (ami(1,length(elts))) return(mc(...))
  for (i in seq(along=elts)) if (!is.mc(elts[[i]])) elts[[i]] <- mc(elts[[i]])
  elts
  }


##########################################################################
# Interpolation schemes            
##########################################################################

# The mc() constructor accepts lists of x-values to define
# the distribution.  Both linear and spline interpolation 
# schemes can be used with these lists. The spline 
# interpolation scheme requires the splines library to be 
# loaded and needs at least 4 values.  
#    See also the quantiles() constructor when you have
# quantiles (or percentiles or fractiles).

interpolate <- function(u, interpolation='linear') switch(interpolation, "spline"={spline.interpolate(u)}, {linear.interpolate(u)})

# needs at least 4 points and the interpSpline function from the library(splines)
spline.interpolate <- function(u) {library(splines); return(predict(interpSpline(1:length(u),u),nseg=MC$many-1)$y)}  # needs the splines library

linear.interpolate <- function(V) {
  m <- length(V) - 1
  if (ami(m,0)) return(rep(V,MC$many))
  if (ami(MC$many,1)) return(c(min(V),max(V)))
  d <- 1/m
  n <- round(d * MC$many * 20)
  if (n==0) c = V else {
  c <- NULL
  for (i in 1:m) {
    v <- V[[i]]     
    w <- V[[i+1]]   
    c <- c(c, seq(from=v, to=w, length.out=n))
    } }
  u <- rep(0,MC$many)
  for (k in 1:MC$many) u[[k]] <-c[[1+round((length(c)-1)*(k-1)/(MC$many-1))]]
  u
  }

##########################################################################
# Access methods #
##########################################################################

left       <- function(x,...) {UseMethod("left")};         left.default    <- function(x) return(min(x))
right      <- function(x,...) {UseMethod("right")};        right.default   <- function(x) return(max(x))
min        <- function(...,na.rm=FALSE){UseMethod("min")}; min.default     <- function(..., na.rm = FALSE) base::min(..., na.rm = na.rm)
max        <- function(...,na.rm=FALSE){UseMethod("max")}; max.default     <- function(..., na.rm = FALSE) base::max(..., na.rm = na.rm)
pmin       <- function(...,na.rm=FALSE){UseMethod("pmin")};pmin.default    <- function(..., na.rm = FALSE) base::pmin(..., na.rm = na.rm)
pmax       <- function(...,na.rm=FALSE){UseMethod("pmax")};pmax.default    <- function(..., na.rm = FALSE) base::pmax(..., na.rm = na.rm)
prob       <- function(x,s,...) {UseMethod("prob")}
alpha      <- function(x,s,...) {UseMethod("prob")}
shuffle    <- function(x) {UseMethod("shuffle")}; shuffle.default <- function(x) x[order(runif(length(x)))]
iqr          <- function(x) {UseMethod("iqr")}
IQR        <- function(x, na.rm = FALSE, type = 7) {UseMethod("IQR")}; IQR.default <- function(x, na.rm = FALSE, type = 7) stats::IQR(x,na.rm,type)
fivenum   <- function(x, na.rm = TRUE) {UseMethod("fivenum")}; fivenum.default <- function(x, na.rm = TRUE) stats::fivenum(x,na.rm)
shift        <- function(ss,x) {UseMethod("shift")};shift.default <- function(ss,x) ss*x
mult       <- function(m,x) {UseMethod("mult")};mult.default <- function(m,x) m*x
atan2      <- function(y,x) {UseMethod("atan2")};atan2.default    <- function(y,x) base::atan2(y,x)
fractile     <- function(x,p,...) {UseMethod("fractile")}
percentile <- function(x,p,...) {UseMethod("percentile")}
negate     <- function(x,...) {UseMethod("negate")};       negate.default  <- function(x,...) return(-x)
reciprocate<- function(x,...) {UseMethod("reciprocate")};  reciprocate.default  <- function(x,...) return(1/x)
complement <- function(x,...) {UseMethod("complement")};   complement.default  <- function(x,...) return(1-x)
and        <- function(x,y,...) {UseMethod("and")};        and.default  <- function(x,y,...) and.mc(x,y)
or         <- function(x,y,...) {UseMethod("or")};         or.default   <- function(x,y,...) or.mc(x,y)
not        <- function(x,...)   {UseMethod("not")};        not.default  <- function(x,...)   complement.mc(x)
cor          <- function(x, y = NULL, use = "everything", method = c("pearson", "kendall", "spearman")) {UseMethod("cor")}; cor.default <- function(x, y = NULL, use = "everything", method = c("pearson", "kendall", "spearman")) stats::cor(x,y,use,method)
#cut         <- function(x,s,...) {UseMethod("fractile")}
#trunc      <- function(x,m,M,...) {UseMethod("truncate")}; truncate.default<- function(x,...) return(base::truncate(x,...))
#round      <- function(x,...) {UseMethod("round")};        round.default   <- function(x,...) return(base::round(x,...))
#ceiling    <- function(x,...) {UseMethod("ceiling")};      ceiling.default <- function(x,...) return(.Primitive("ceiling")(x,...))
#sign       <- function(x,...) {UseMethod("sign")};         sign.default    <- function(x,...) return(.Primitive("sign")(x,...))

reps <- function(x) if (x@n==length(x@x)) x@n else "Internal step count error"

min.mc <- left.mc <- function(x) base::min(x@x)

max.mc <- right.mc <- function(x) base::max(x@x)

# function revised to be unary transformation
#sign.mc <- function(x) if (right(x)<0) -1 else if (0<left(x)) +1 else if (is.scalar(x) && identical(x@x[[1]],0)) 0 else if (right(x)<=0) c(-1,0) else if (0<=left(x)) c(0,1) else c(-1,1)

range.mc <- function(x, na.rm = FALSE) base::range(x@x)  # hard to believe I need to have the na.rm argument!

iqr.mc <- function(x) c(percentile.mc(x,0.25), percentile.mc(x,0.75))

IQR.mc <- function(x) diff(iqr.mc(x))

cut.mc <- quantile.mc <- fractile.mc <- percentile.mc <- function(x, p, tight=TRUE) {
  if ((p<0) | (1<p)) stop('Second argument must be a probability between zero and one')
  sort(x@x)[round(x@n*p)]
  }

random <- function(x,n=1) x@x[shuffle(1:MC$many)[1:n]]

randomrange <- function(x,n=1) left(x)+runif(n)*(right(x)-left(x))

#specific <- function(x) randomrange(random(x))

prob.mc <- alpha.mc <- function(x, s) {
#  x <- makemc(x)
  length(x@x[x@x<s])/MC$many
  }

xprob.mc <- function(x, s) {    # required by the inequality comparisons
#  x <- makemc(x); 
  length(x@x[x@x<=s])/MC$many
  }

right.mc <- function(x) max(x@x)

left.mc <- function(x) min(x@x)

median.mc <- function(x, na.rm = FALSE) percentile.mc(x,0.5)

fivenum.mc <- function(x, na.rm = FALSE) c(minimum=left(x), firstquartile=percentile.mc(x,0.25), median=median.mc(x), thirdquartile=percentile.mc(x,0.75), maximum=right(x))

mean.mc <- function(x) mean(x@x)

var.mc <- function(x) var(x@x)

sd.mc <- function(x) sd(x@x)   

cor.mc = function(a,b) stats::cor(a@x,b@x)

##########################################################################
# Wrap access methods
##########################################################################

#quiet <- setMethod('==', c('mc','mc'), function(e1, e2){ same(e1, e2) })

#if(!isGeneric("fivenum")) quiet <- setGeneric("fivenum", function (x, na.rm = FALSE) standardGeneric("fivenum"))
#quiet <- setMethod('fivenum', 'mc', function (x, na.rm = FALSE) fivenum.mc(x, na.rm = FALSE))
 
# there is no generic function iqr;  IQR returns the length of the iqr

if(!isGeneric("sd")) quiet <- setGeneric("sd", function(x, na.rm = FALSE) standardGeneric("sd"))
quiet <- setMethod('sd', 'mc', function(x, na.rm = FALSE) sd.mc(x))

if(!isGeneric("var")) quiet <- setGeneric("var", function(x, y = NULL, na.rm = FALSE, use) standardGeneric("var"))
quiet <- setMethod('var', 'mc', function(x, y, na.rm, use) var.mc(x))

#this replaced the following hack, which appeared to work, but might collide with other packages 
#var <- function(x, ...) if (is.mc(x)) var.mc(x) else stats::var(x, ...)


##########################################################################
# Typing functions 
##########################################################################

is.mc <- function(x) inherits(x,'mc')

is.interval <- function(x) return(inherits(x,'interval') || (inherits(x,'pbox') && (x@d[[1]]==x@d[[steps(x)]]) &&  (x@u[[1]]==x@u[[steps(x)]])))

is.scalar <- function(x) {
  if (is.mc(x) && isTRUE(all.equal(left(x),right(x)))) return(TRUE)
  if (is.interval(x) && isTRUE(all.equal(left(x),right(x)))) return(TRUE)
# if (is.numeric(x) && identical(1,length(x))) return(TRUE)
  if (is.numeric(x) && isTRUE(1 == length(x))) return(TRUE)
  FALSE
  }

# whether it can be involved in a convolution
is.uncnum <- is.number <- function(x) is.numeric(x) || is.scalar(x) || is.interval(x) || is.mc(x) 

# whether it has epistemic or aleatory uncertainty
is.uncertain <- function(x) is.interval(x) || is.mc(x) 

is.vacuous <- function(s,...) {UseMethod("is.vacuous")};         is.vacuous.default    <- function(s) return(all(is.nan(s)) || all(is.na(s)))
is.vacuous.mc     <- function(s) all(s@u==-Inf) && all(s@d==Inf)
is.vacuous.interval <- function(s) all(s@lo==-Inf) && all(s@hi==Inf)
#is.vacuous.numeric  use default method

##########################################################################
# Unary transformations 
##########################################################################

exp.mc <- function(x) mc(exp(x@x))

log.mc <- function(x, expo=exp(1)) if (expo == exp(1)) mc(log(x@x)) else mc(log(x@x,expo))    # expo must be a scalar

log.mc <- function(x, expo=mc(exp(1))) mc(log(x@x,expo@x))    
  	
reciprocate.mc <- function(x) mc(1/x@x)

sqrt.mc <- function(x) mc(base::sqrt(x@x)) 
  
sin.mc <- function(x) mc(base::sin(x@x))   
cos.mc <- function(x) mc(base::cos(x@x))   
tan.mc <- function(x) mc(base::tan(x@x))   
asin.mc <- function(x) mc(base::asin(x@x))   
acos.mc <- function(x) mc(base::acos(x@x))   
atan.mc <- function(x) mc(base::atan(x@x))   
atan2.mc <- function(y,x) mc(base::atan2(y@x,x@x))   

`-.mc` <- negate.mc <- function(x) mc(-x@x) 

complement.mc <- function(x) mc(1-x@x) 

mult.mc <- function(m, x) if (m < 0) negate.mc(mult(abs(m),x)) else mc(m*x@x)

shift.mc <- function(ss,x) mc(ss+x@x) 

sign.mc <- function(x) mc(sign(x@x))

trunc.mc <- function(x) mc(base::trunc(x@x)) 
round.mc <- function(x,...) mc(base::round(x@x,...)) 
ceiling.mc <- function(x) mc(base::ceiling(x@x)) 

truncate.mc <- function(x,min,max) mc(base::pmin(max, base::pmax(min,x@x))) 

samedistribution <- function(x) mc(shuffle(x@x))

shuffle.mc <- function(x) mc(shuffle(x@x))


##########################################################################
# Mass reassignments functions 
##########################################################################

lowest <- function(x, p) {   # exclude all but the lowest p% of x, useful for Will Powley's rejection rescaling
  if (!is.mc(x)) stop('The argument to the lowest truncation must be a distribution')
  z = sort(x@x)[1:(MC$many*(p/100))]
  mc(z[trunc(runif(MC$many,1,length(z)+1))])
  }

highest <- function(x, p) {   # exclude all but the highest p% of x, useful for Will Powley's rejection rescaling
  if (!is.mc(x)) stop('The argument to the highest truncation must be a distribution')  
  z = sort(x@x)[(MC$many*((100-p)/100)):MC$many]
  mc(z[trunc(runif(MC$many,1,length(z)+1))])
  }

below <- function(x, s) {   # exclude all values from x but those below or equal to s
  if (!is.mc(x)) stop('The argument to the below truncation must be a distribution')
  z = x@x[x@x <= s]
  mc(z[trunc(runif(MC$many,1,length(z)+1))])
  }

above <- function(x, s){   # exclude all values from x but those above or equal to s
  if (!is.mc(x)) stop('The argument to the above truncation must be a distribution')
  z = x@x[s <= x@x]
  mc(z[trunc(runif(MC$many,1,length(z)+1))])
  }

between <- function(x, m, M) below(above(x, m), M)   # exclude all values from x except those between m and M

rescale <- function(x, m, M)  m + (M-m) * (x - left(x))/ diff(range(x))  # linearly rescale x to the specified range [m,M]

##########################################################################
# K-fold binary convolutions and mixtures
##########################################################################

# pmin, pmax are convolutions, corresponding to minI, maxI in Risk Calc

pmin.mc <- function (..., na.rm = FALSE) {  
  elts <- makemc(...)
  m <- elts[[1]]
  for (each in elts[-1]) m <- conv.mc(m, each, 'pmin')
  m
  }

pmax.mc <- function (..., na.rm = FALSE) {  
  elts <- makemc(...)
  m <- elts[[1]]
  for (each in elts[-1]) m <- conv.mc(m, each, 'pmax')
  m
  }

smax = function (..., na.rm = FALSE) {  
  elts <- makemc(...)
  x <- sort(elts[[1]]@x)
  for (each in elts[-1]) {
    x <- pmax(x,sort(each@x),na.rm=na.rm)
    }
  mc(shuffle(x))
  }
  
smin = function (..., na.rm = FALSE) {  
  elts <- makemc(...)
  x <- sort(elts[[1]]@x)
  for (each in elts[-1]) {
    x <- pmin(x,sort(each@x),na.rm=na.rm)
    }
  mc(shuffle(x))
  }
  
mixture <- function(x, w=rep(1,length(x)), ...) {
  k <- length(x)
  if (k != length(w)) stop('Need same number of weights as arguments to mix')
  w = w / sum(w)
  z <- NULL
  for (i in 1:k)  z <- c(z,random(x[[i]],w[[i]]*MC$many))
  if (length(z)>MC$many) z = z[1:MC$many] else if (length(z)<MC$many) z = c(z, z[shuffle(z)[1:(MC$many - length(z))]])
  mc(shuffle(z))
  }
 

##########################################################################
# Binary convolution operations 
##########################################################################

conv.mc <- function(x,y,op='+') mc(do.call(op, list(x@x, y@x)))

perfectconv.mc <- function(x,y,op='+')  mc(shuffle(do.call(op, list(sort(x@x), sort(y@x)))))

oppositeconv.mc <- function(x,y,op='+')  mc(shuffle(do.call(op, list(sort(x@x), sort(y@x,decreasing=TRUE)))))


#####################
# correlation functions 
#####################

correlations <- function(S) {
  require('MASS'); 
  Sigma = matrix(S, nrow=sqrt(length(S))); 
  MC$r <- pnorm(mvrnorm(n=MC$many, mu=rep(0,nrow(Sigma)), Sigma=Sigma)); 
  return(invisible(NULL))}

R = function(i,corrs=MC$r) return(corrs[,i])

corrs = function(X,names=rep('',length(X))) {  
  x = NULL
  k = length(X)
  for (i in 1:k) x = c(x,X[[i]]@x)
  C = cor(matrix(x,ncol=k))
  dimnames(C) <- list(names,names)
  C
  }

plotcorrs = function(X,names=rep('',length(X)),some=300,lwd=2,...) {
  x = NULL
  k = length(X)
  for (i in 1:k) x = c(x,X[[i]]@x)
  C = cor(matrix(x,ncol=k))
  par(mfcol=c(k,k))
  w = shuffle(1:MC$many)[1:some]
  for (i in 1:k) for (j in 1:k) if (i==j) plot.mc(X[[i]],xlab=names[[i]],ylab='Cum.Prob.',lwd=lwd,...) else plot(X[[i]]@x[w],X[[j]]@x[w],xlab=names[[i]],ylab=names[[j]],main=paste(sep='','r=',signif(C[i,j],3)),...)
  invisible(NULL)
  }

# The caracel function generate deviates with an exact specified sample (rather than population) correlation
# This function will not work if the %*% matrix multiplication operation has been hijacked.  Use rm(list-ls())
# to restore its functionality.  The approach used by the caracel function seems only to work with bivariate 
# normal variables.  For instance, it does not work with discrete random variable, because the trick used is 
# rotation (try plotting x1 and x that result from letting x2=rpois(2000,2); the resulting x2 is not Poisson).
# This was caracal's answer on http://stats.stackexchange.com/questions/15011/generate-a-random-variable-with-a-defined-correlation-to-an-existing-variable
# See also http://www.r-bloggers.com/modelling-dependence-with-copulas-in-r/
# Use these lines to test the caracel function:
#    n = 2000
#    x1=rnorm(n,1,1)
#    x2=rpois(n, 2)
#    x2=rexp(n, 2)
#    x2=rnorm(n, 2, 0.5)
#    o = caracel(0.6, x1, x2)
#    X1 = o$x1
#    X2 = o$x2
#    cor(x1, X1); plot(sort(x1),1:n,type='s'); lines(sort(X1),1:n,type='s',col='red')
#    cor(x2, X2); lines(sort(x2),1:n,type='s',col='blue'); lines(sort(X2),1:n,type='s',col='tan')
#    cor(X1, X2)
caracel <- function(rho=0.6, x1=rnorm(2000,1,1), x2=rpois(2000, 2)) { # rho is the desired correlation = cos(angle)
  n = length(x1)                                               # n=20,000 almost crashed the computer!
  if (n!=length(x2)) stop('Mismatched vectors in caracel function')
  theta <- acos(rho)                                          # corresponding angle
  X     <- cbind(x1, x2)                                     # matrix
  Xctr  <- scale(X, center=TRUE, scale=FALSE)   # centered columns (mean 0)
  Id   <- diag(n)                                               # identity matrix
  Q    <- qr.Q(qr(Xctr[ , 1, drop=FALSE]))          # QR-decomposition, just matrix Q
  P    <- tcrossprod(Q)                                      # = Q Q'     # projection onto space defined by x1
  x2o  <- (Id-P) %*% Xctr[ , 2]                         # x2ctr made orthogonal to x1ctr
  Xc2  <- cbind(Xctr[ , 1], x2o)                          # bind to matrix
  Y <- Xc2 %*% diag(1/sqrt(colSums(Xc2^2)))  # scale columns to length 1   # needs the native R %*% matrix multiplication operator
  x <- Y[ , 2] + (1 / tan(theta)) * Y[ , 1]             # final new vector
  x = ((x-mean(x))  / sd(x)) * sd(x2) + mean(x2)             # rescale to dispersion and location [added by Scott]
  list(x1=x1,x2=x,cor=cor(x1, x))                          # check correlation = rho
  }


#####################
# Logical functions 
#####################

are.logicals.mc <- function(a,b) {
  a <- makemc(a)
  b <- makemc(b)
  # must be dimensionless too, but we cannot check that
  ((0 <= left.mc(a)) && (right.mc(a) <= 1) && (0 <= left.mc(b)) && (right.mc(b) <= 1))
  }

# complement.mc (already defined) is logical negation

and.mc <- function(a,b) conv.mc(a,b,'*');

or.mc <- function(a,b) complement.mc(conv.mc(complement.mc(a), complement.mc(b),'*'))

# We don't support ==, &, &&, |, || as infix operators for p-boxes because 
# we cannot be comprehensive in doing so.  The first problem is that && 
# and || (which would be the natural operators to use) are sealed and 
# can't be changed.  The second problem is that & and I cannot be applied
# when the left argument is an atomic numeric for similar reasons.  Finally,
# & and | won't work on vectors of distributions, or rather, we cannot invoke 
# them that way, because an array of distributions does not have the class mc.
# Instead, we define the functions and.mc and or.mc.


##########################################################################
# In-fix Operators #
##########################################################################

# addition 
quiet <- setMethod('+', c('mc','numeric'),  function(e1, e2){ shift.mc(e2, e1) })    # what happens if e2 is a vector??
quiet <- setMethod('+', c('numeric','mc'),  function(e1, e2){ shift.mc(e1, e2) })
quiet <- setMethod('+', c('mc','mc'),function(e1,e2){  return( conv.mc(e1,e2,'+') )})   

# multiplication
quiet <- setMethod('*', c('mc','numeric'), function(e1, e2){ mult.mc(e2, e1) })   # what happens if e2 is a vector??
quiet <- setMethod('*', c('numeric','mc'), function(e1, e2){ mult.mc(e1, e2) })
quiet <- setMethod('*', c('mc','mc'),function(e1,e2){ return( conv.mc(e1,e2,'*') )})   

# subtraction
quiet <- setMethod('-', c('mc','numeric'), function(e1, e2){mc(e1@x - e2) })   # what happens if e2 is a vector??
quiet <- setMethod('-', c('numeric','mc'), function(e1, e2){ mc(e1 + negate.mc(e2), opposite=e2) })
quiet <- setMethod('-', c('mc','mc'),function(e1,e2){ return( conv.mc(e1,negate.mc(e2),'+') )})   

# division
quiet <- setMethod('/', c('mc','numeric'), function(e1, e2){ mult.mc(1/e2, e1) })   # what happens if e2 is a vector??
quiet <- setMethod('/', c('numeric','mc'), function(e1, e2){ mult.mc(e1, reciprocate.mc(e2)) })
quiet <- setMethod('/', c('mc','mc'),function(e1,e2){ return( conv.mc(e1,reciprocate.mc(e2),'*') )})   

# raising to a power
quiet <- setMethod('^', c('mc','numeric'), function(e1, e2){ mc(e1@x ^ e2) })      # what happens if e2 is a vector??
quiet <- setMethod('^', c('numeric','mc'), function(e1, e2){ mc(e1 ^ e2@x)})
quiet <- setMethod('^', c('mc','mc'),function(e1,e2){ return( conv.mc(e1,e2,'^') )})   


ilt <- function(x,y) if (right(x) < left(y)) return(1) else if (right(y) < left(x)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(x)<left(y)) else return(prob.mc(conv.mc(x,y,'-'),0))
igt <- function(x,y) if (right(y) < left(x)) return(1) else if (right(x) < left(y)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(y)<left(x)) else return(prob.mc(conv.mc(y,x,'-'),0))
ilte <- function(x,y) if (right(x) <= left(y)) return(1) else if (right(y) < left(x)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(x)<=left(y)) else return(xprob.mc(conv.mc(x,y,'-'),0))
igte <- function(x,y) if (right(y) <= left(x)) return(1) else if (right(x) < left(y)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(y)<=left(x)) else return(xprob.mc(conv.mc(y,x,'-'),0))

# default less-than comparison 
quiet <- setMethod('<', c('mc','numeric'), function(e1, e2){ lt(e1,e2) })     # what happens if e2 is a vector??
quiet <- setMethod('<', c('numeric','mc'), function(e1, e2){ lt(e1,e2) })
quiet <- setMethod('<', c('mc','mc'), function(e1, e2){ prob.mc(conv.mc(e1,negate.mc(e2),'+'),0) })

# default greater-than comparison 
quiet <- setMethod('>', c('mc','numeric'),   function(e1, e2){ gt(e1,e2) })   # what happens if e2 is a vector??
quiet <- setMethod('>', c('numeric','mc'),  function(e1, e2){ gt(e1,e2) })
quiet <- setMethod('>', c('mc','mc'),  function(e1, e2){ xprob.mc(conv.mc(e2,negate.mc(e1),'+'),0) })

# default less-than-or-equal-to comparison 
quiet <- setMethod('<=', c('mc','numeric'), function(e1, e2){ lte(e1,e2) })     # what happens if e2 is a vector??
quiet <- setMethod('<=', c('numeric','mc'), function(e1, e2){ lte(e1,e2) })
quiet <- setMethod('<=', c('mc','mc'), function(e1, e2){ xprob.mc(conv.mc(e1,negate.mc(e2),'+'),0) })

# default greater-than-or-equal-to comparison (used by automatic dependency tracking)
quiet <- setMethod('>=', c('mc','numeric'),   function(e1, e2){ gte(e1,e2) })   # what happens if e2 is a vector??
quiet <- setMethod('>=', c('numeric','mc'),  function(e1, e2){ gte(e1,e2) })
quiet <- setMethod('>=', c('mc','mc'),  function(e1, e2){ prob.mc(conv.mc(e2,negate.mc(e1),'+'),0) })


##########################################################################
# Some inverse probability distributions not already implemented in R 
##########################################################################

qexponentialpower <- function(p, lambda, kappa) return(exp(-(log(lambda) - log(log(1-log(1-p)))) / kappa))

qfrechet <- function(p, b, c) b*exp((-1/c)*log(log(1/p)))               # Castillo, page 207

qgev <- function(p,a,b,c) if (c==0) qgumbel(p,a,b) else a + b * (exp(-c*log(-log(p))) - 1) / c   # c must be a scalar

qgeneralizedpareto <- function(p,mu,sigma,scale) mu - sigma * (1-exp(-scale*log(1-p))) / scale

qgumbel <- function(p, a, b) a - b * log(log(1.0/p))                    # Evans et al., page 65

qlaplace <- function(p, a, b) ifelse(p<=0.5, a + b * log(2.0 * p),a - b * log(2.0 * (1.0 - p))) # Evans et al., page 92

qloglogistic <- function(p, lambda, kappa) return(exp(-(log(lambda) - log(-p/(p-1))/ kappa)))

qlogtriangular <- function(p, i_min, i_mode, i_max){
  a = log(i_min)
  b = log(i_mode)       # could this really be correct?
  c = log(i_max)
  exp(qtriangular(p, a, b, c))
  }

qloguniform <- function(p, one, two) {
  m = log(one)
  exp((log(two) - m) * p + m);
  }

qreciprocal <- function(p, a=10.0) exp(p * log(a))

qpareto <- function(p, mode, c) mode * exp((-1.0/c) * log(1.0 - p))     # Evans et al., page 119

qpowerfunction <- function(p, b, c) b * exp((1.0/c) * log(p))           # Evans et al., page 128

qrayleigh <- function(p, b) sqrt(-2.0 * b * b * log(1.0 - p))           # Evans et al., page 134

sawinconradalpha01 <- function(mu) {
  if (abs(mu-0.5)<0.000001) return(0)
  f = function(alpha) 1/(1-1/exp(alpha)) - 1/alpha - mu
  uniroot(f,c(-500,500))$root
  }

qsawinconrad <- function(p, min, mu, max){
  alpha = sawinconradalpha01((mu-min)/(max-min))
  if (abs(alpha)<0.000001) return(min+(max-min)*p) else
  min+(max-min)*((log(1+p*(exp(alpha)-1)))/alpha)
  }
 
qshiftedloglogistic <- function(p, a,b,c) a + b * (exp(c*log(1/(1/p-1))) - 1) / c

qtrapezoidal <- function(p, a, b, c, d){
  if (abs(d-a)<1e-10) return(rep(a,length.out=length(p)))
  if (abs(c-b)<1e-10) return(qtriangular(p,a,b,d))
  h = 2 / (c+d-b-a)
  p1 = h * (b-a)/2
  p2 = p1 + h * (c-b)
  r <- ifelse(p <= p2, (p - p1) / h + b, d - sqrt(2 * (1-p) * (d-c) / h))
  r[p<=p1] <- a + sqrt(2 * p[p<=p1] * (b-a)/h)   
  r
  }

qtriangular <- function(p, min, mid, max){
  pm = (mid-min) / (max-min)
  ifelse(p<=pm, min + sqrt(p * (max - min) * (mid - min)), max - sqrt((1.0 - p) * (max - min) * (max - mid)))
  }

##########################################################################
# Distribution constructors 
##########################################################################

r_ <- function(r) if (!inherits(r,'mc')) return(r) else return(((1:MC$many)/(MC$many+1))[rank(r@x)])  # is this one slightly better?
r_ <- function(r) if (!inherits(r,'mc')) return(r) else return(rank(r@x)/MC$many) 

bernoulli = function(p,r=runif(MC$many))  mc((r_(r) < p) + 0)
 
B <- beta  <- function(shape1, shape2,r=runif(MC$many)) mc(qbeta(r_(r), shape1, shape2))

beta1 <- function(mean,sd) return(beta(mean * (mean * (1 - mean) / (sd^2) - 1), (mean * (mean * (1 - mean) / (sd^2) - 1)) * (1/mean - 1)))

Bin <- binomial <- function(size=NULL, prob=NULL, mean=NULL, std=NULL, r=runif(MC$many)){
  if (is.null(size) & !is.null(mean) & !is.null(std)) size <- mean/(1-std^2/mean)
  if (is.null(prob) & !is.null(mean) & !is.null(std)) prob <- 1-std^2/mean
  mc(qbinom(r_(r), size, prob))
  }

cauchy <- function(location, scale, r=runif(MC$many)) mc(qcauchy(r_(r), location, scale))

chi <- function(n, r=runif(MC$many)) mc(sqrt(chisquared(n)))

chisquared <- function(df, r=runif(MC$many)) mc(qchisq(r_(r),df))

delta <- dirac <- function(x, r=runif(MC$many)) mc(rep(x,MC$many))

discreteuniform <- function(max=NULL, mean=NULL, r=runif(MC$many)) {
  if (is.null(max) & !is.null(mean)) max <- 2 * mean
  mc(trunc(uniform(0, max+1)))
  }

exponential <- function(mean, r=runif(MC$many)) mc(qexp(r_(r),1/mean))

exponentialpower <- function(lambda, kappa, r=runif(MC$many)) mc(qexponentialpower(r_(r),lambda, kappa))
  
F <- f <- fishersnedecor <- function(df1, df2, r=runif(MC$many)) mc(qf(r_(r), df1, df2))

frechet <- function(b, c, r=runif(MC$many)) mc(qfrechet(r_(r), b, c))

# N.B. the parameters are scale and shape, which are reordered and different from rgamma's parameters which are shape and rate (1/scale)
gamma <- function(scale, shape, r=runif(MC$many)) mc(qgamma(r_(r), shape=shape, scale=scale)) 

gamma1 <- function(mu, sigma) return(gamma(sigma^2/mu, (mu/sigma)^2)) 

gamma2 <- function(shape, scale, r=runif(MC$many)) mc(qgamma(r_(r), shape=shape, scale=scale))  

inversegamma <- function(a, b, r=runif(MC$many)) mc(1/qgamma(r_(r), shape=a, scale=1/b))  

geometric <- pascal <- function(prob=NULL, mean=NULL, r=runif(MC$many)){
  if (is.null(prob) & !is.null(mean)) prob <- 1/(1+ mean)
  mc(qgeom(r_(r),prob))
  }

GEV <- gev <- generalizedextremevalue <- fishertippett <- function(a=0,b=1,c=0, r=runif(MC$many)) if (c==0) return(gumbel(a,b)) else mc(qgev(r_(r),a,b,c)) # http://en.wikipedia.org/wiki/Generalized_extreme_value_distribution

generalizedpareto <- function(mu,sigma,scale, r=runif(MC$many)) mc(qgeneralizedpareto(r_(r),mu,sigma,scale))

gumbel <- extremevalue <- function(a=NULL, b=NULL, mean=NULL, std=NULL, var=NULL, r=runif(MC$many)){  
  if (missing(std) && !missing(var)) std <- sqrt(var)
  if (missing(a) && missing(b)) {a <- mean-std*0.577215665*sqrt(6)/base::pi; b <- std*sqrt(6)/base::pi}
  mc(qgumbel(r_(r), a, b))
  }

laplace <- function(a, b, r=runif(MC$many)) mc(qlaplace(r_(r), a, b))  

logistic <- function(location, scale, r=runif(MC$many)) mc(qlogis(r_(r),location, scale))

loglogistic <- fisk <- function(lambda, kappa, r=runif(MC$many)) mc(qloglogistic(r_(r),lambda, kappa))

lognormal0 <- function(meanlog, stdlog, r=runif(MC$many)) mc(qlnorm(r_(r),meanlog,stdlog)) 

L <- lognormal <- function(mean=NULL, std=NULL, meanlog=NULL, stdlog=NULL, median=NULL, cv=NULL, r=runif(MC$many)){
  if (is.null(meanlog) & !is.null(median)) meanlog = log(median)
  if (is.null(stdlog) & !is.null(cv)) stdlog = sqrt(log(cv^2 + 1))
  # lognormal(a, b) ~ lognormal2(log(a^2/sqrt(a^2+b^2)),sqrt(log((a^2+b^2)/a^2)))
  if (is.null(meanlog) & (!is.null(mean)) & (!is.null(std))) meanlog = log(mean^2/sqrt(mean^2+std^2))
  if (is.null(stdlog) & !is.null(mean) & !is.null(std)) stdlog = sqrt(log((mean^2+std^2)/mean^2))
  if (!is.null(meanlog) & !is.null(stdlog)) lognormal0(meanlog,stdlog,r) else stop('Not enough information to specify the lognormal distribution')
  }

logtriangular <- function(min=NULL, mode=NULL, max=NULL, minlog=NULL, midlog=NULL, maxlog=NULL, r=runif(MC$many)){
  if (is.null(min) & !is.null(minlog)) min = exp(minlog)  ###place in arglist
  if (is.null(max) & !is.null(maxlog)) max = exp(maxlog)  ###place in arglist
  mc(qlogtriangular(r_(r), min, mode, max))
  }

loguniform <- function(min=NULL, max=NULL, minlog=NULL, maxlog=NULL, mean=NULL, std=NULL, r=runif(MC$many)){
  if (is.null(min) & !is.null(minlog)) min <- exp(minlog)
  if (is.null(max) & !is.null(maxlog)) max <- exp(maxlog)
  if (is.null(max) &  !is.null(mean) & !is.null(std) & !is.null(min)) max = 2.0 * (mean^2 +std^2)/mean - min
  mc(qloguniform(r_(r), min, max))
  }

negativebinomial <- function(size, prob, r=runif(MC$many)) mc(qnbinom(r_(r), size, prob))

normal0 <- function(normmean, normstd, r=runif(MC$many)) mc(qnorm(r_(r),normmean,normstd))

N <- normal <- gaussian <- function(mean=NULL, std=NULL, median=NULL, mode=NULL, cv=NULL, iqr=NULL, var=NULL, r=runif(MC$many)){
  if (is.null(mean) & !is.null(median)) mean = median
  if (is.null(mean) & !is.null(mode)) mean = mode
  if (is.null(std) & !is.null(cv) & !is.null(mean)) std = mean * cv
  if (!is.null(mean) & !is.null(std)) normal0(mean,std,r) else stop('Not enough information to specify the normal distribution')
  }

sawinconrad <- function(min, mu, max, r=runif(MC$many)){
  a <- left(min);   b <- right(max)
  c <- left(mu);    d <- right(mu)
  if (c<a) c <- a   # implicit constraints
  if (b<d) d <- b
  mc(qsawinconrad(r_(r), min, mu, max))
  }

SN <- skewnormal <- function(location, scale, skew, r=runif(MC$many)) if (require('sn')) mc(qsn(r_(r),location,scale,skew)) else stop('Need to install the sn package to use skewnormal')

pareto <- function(mode, c, r=runif(MC$many))  mc(qpareto(r_(r), mode, c))

powerfunction <- function(b, c, r=runif(MC$many)) mc(qpowerfunction(r_(r), b, c))

poisson <- function(lambda, r=runif(MC$many)) mc(qpois(r_(r),lambda))

rayleigh <- function(b, r=runif(MC$many)) mc(qrayleigh(r_(r), b)) 

reciprocal <- function(a=10.0, r=runif(MC$many)) mc(qreciprocal(r_(r), a))

shiftedloglogistic <- function(a=0,b=1,c=0, r=runif(MC$many))  {
  if (c==0) return(Slogistic(a,b))
  csc <- function(x) 1/sin(x)
  m <- a + b * (base::pi*c*csc(base::pi*c)) / c
  v <- b^2  * (2*base::pi*c*csc(2*base::pi*c)-(base::pi*c*csc(base::pi*c))^2) / (c^2)
  mc(qshiftedloglogistic(r_(r),a,b,c))
  }

student <- function(df, r=runif(MC$many)) mc(qt(r_(r),df))

trapezoidal <- function(min, lmode, rmode, max, r=runif(MC$many)) mc(qtrapezoidal(r_(r), min, lmode, rmode, max))
  
T <- triangular <- function(min, mode, max, r=runif(MC$many)) mc(qtriangular(r_(r), min, mode, max))
  
U <- uniform <- rectangular <- function(min, max, r=runif(MC$many)) mc(qunif(r_(r),min,max))
    
weibull <- function(scale, shape, r=runif(MC$many)) mc(qweibull(r_(r), shape, scale))   # argument order disagrees with R's qweibull function, but agrees with Wikipedia (in November 2013)



##########################################################################
# Custom distribution constructors 
##########################################################################

histogram = function(x) { #sample values are in an array x 
  n <- length(x)
  i <- shuffle(rep(1:n, ceiling(MC$many/n)))[1:MC$many]
  # k <- rep(0,n); for (j in 1:n) k[j] <- length(i[i==j]); if (length(i)!=MC$many) cat(n,' ',length(i),' ',k,'\n')
  mc(x[i])
  }
  
quantiles <- function(v,p,r=runif(MC$many))  {
  if (length(v) != length(p)) stop('Inconsistent array lengths for quantiles')
  if ((min(p) < 0) || (1 < max(p))) stop('Improper probability for quantiles') # ensure 0 <= p <= 1
  if (!identical(range(p),c(0,1))) stop('Probabilities must start at zero and go to one for quantiles')
  if (any(diff(p)<0)) stop('Probabilities must increase for quantiles') # ensure montone probabilities
  if (any(diff(v)<0)) stop('Quantiles values must increase') # ensure montone quantiles
  r = r_(r)
  x = rep(Inf,MC$many)
  for (i in 1:(length(p)-1)) x = ifelse((p[[i]]<=r) & (r<p[[i+1]]), v[[i]]+(r-p[[i]])*(v[[i+1]]-v[[i]])/(p[[i+1]]-p[[i]]),  x)
  mc(x)
  }
#quantiles(v = c(3, 6,   10,  16,  25,  40), p = c(0, 0.2, 0.4, 0.5, 0.7, 1))
#quantiles(v = c(3,   6,   10,  16,  25,  40), p = c(0.1, 0.2, 0.4, 0.5, 0.7, 0.9))


##########################################################################
# PERT and MaxEnt distribution constructors 
##########################################################################

betapert <- function(min, max, mode) {
  mu = (min + max + 4*mode)/6
  alpha1 = (mu - min)*(2*mode - min - max)/((mode - mu)*(max - min))
  alpha2 = alpha1*(max - mu)/(mu - min)
  min + (max - min) * beta(alpha1, alpha2)
  }
  
MEminmax <- function(min, max) uniform(min,max)

MEminmaxmean <- function(min, max, mean) sawinconrad(min,mean,max) #http://mathoverflow.net/questions/116667/whats-the-maximum-entropy-probability-distribution-given-bounds-a-b-and-mean, http://www.math.uconn.edu/~kconrad/blurbs/analysis/entropypost.pdf for discussion of this solution.

MEmeansd = function(mean, sd) normal(mean, sd)

MEminmean<- function(min,mean) min+exponential(mean-min)

#MEmeangeomean <- function(mean, geomean)

MEdiscretemean <- function(x,mu,steps=10,iterations=50) {
  fixc = function(x,r) return(1/sum(r^x))
  r = br = 1
  c = bc = fixc(x,r)
  d = bd = (mu - sum((c*r^x)*x))^2
  for (j in 1:steps) {
    step = 1/j
    for (i in 1:iterations) {
      r = abs(br + (runif(1) - 0.5) * step)
      c = fixc(x,r)
      d = (mu - sum((c*r^x)*x))^2
      if (d < bd) {
        br = r
        bc = c
        bd = d
        }
      }
    }
  w = bc*br^x
  w = w / sum(w) # needed?
  z <- NULL
  k = length(x)
  for (i in 1:k)  z <- c(z,rep(x[[i]],w[[i]]*MC$many))
  if (length(z)>MC$many) z = z[1:MC$many] else if (length(z)<MC$many) z = c(z, z[shuffle(z)[1:(MC$many - length(z))]])
  mc(shuffle(z))
  }

MEquantiles <- quantiles

MEdiscreteminmax <- function(min,max) return(pmin(trunc(uniform(min,max+1)),max))

MEmeanvar <- function(mean, var) return(MEmeansd(mean,sqrt(var)))

MEminmaxmeansd <- function(min, max, mean, sd) return(beta1((mean- min) / (max - min),  sd/(max - min) ) * (max - min) + min)

MEmmms <- MEminmaxmeansd

MEminmaxmeanvar <- function(min, max, mean, var) return(MEminmaxmeansd(min,max,mean,sqrt(var)))


##########################################################################
# Method-of-Moment distribution constructors (match moments of the data x)
##########################################################################

MMbernoulli <- function(x) bernoulli(mean(x)) # assumes x is zeros and ones
MMbeta <- function(x) beta1(mean(x), sd(x))
MMbinomial <- function(x) {a = mean(x); b= sd(x); binomial(round(a/(1-b^2/a)), 1-b^2/a)} 
MMchisquared <- function(x) chisquared(round(mean(x)))
MMexponential <- function(x) exponential(mean(x))
MMF <- function(x) {w = 2/(1-1/mean(x)); F(round((2*w^3 - 4*w^2) / ((w-2)^2 * (w-4) * sd(x)^2 - 2*w^2)), round(w))}
MMgamma <- function(x) {a = mean(x); b= sd(x); gamma(b^2/a, (a/b)^2)}  #gamma1(a, b) ~ gamma(b²/a, (a/b)²)
MMgeometric <- MMpascal <- function(x) geometric(1/(1+mean(x)))
MMgumbel <- MMextremevalue <- function(x) gumbel(mean(x) - 0.57721* sd(x) * sqrt(6)/ pi, sd(x) * sqrt(6)/ pi)
MMlognormal <- function(x) lognormal(mean(x), sd(x))
MMlaplace <- MMdoubleexponential <- function(x) laplace(mean(x), sd(x)/sqrt(2))
MMlogistic <-  function(x) logistic(mean(x), sd(x) * sqrt(3)/pi)
MMloguniform <- function(x) loguniform1(mean(x), sd(x))   #############
MMnormal <- MMgaussian <- function(x) normal(mean(x), sd(x))
MMpareto <- function(x) {a = mean(x); b= sd(x); pareto(a/(1+1/sqrt(1+a^2/b^2)), 1+sqrt(1+a^2/b^2))}
MMpoisson <- function(x) poisson(mean(x))
MMpowerfunction <- function(x) {a = mean(x); b= sd(x); powerfunction(a/(1-1/sqrt(1+(a/b)^2)), sqrt(1+(a/b)^2)-1)}
MMt <- MMstudent <- function(x) if (1<sd(x)) student(2/(1-1/sd(x)^2)) else stop('Improper standard deviation for student distribution')
MMuniform <- MMrectangular <- function(x) {a = mean(x); b= sd(x); uniform(a-sqrt(3)*b, a+sqrt(3)*b)}


##########################################################################
# Maximum likelihood estimation constructors
##########################################################################

MLbernoulli <- function(x) bernoulli(mean(x))
MLnormal <- MLgaussian <- MMnormal
MLexponential <- MMexponential
MLpoisson <- MMpoisson
MLgeometric <- MLpascal <- MMgeometric
MLuniform <- MLrectangular <- function(x) uniform(min(x), max(x))
MLpareto <- function(x) pareto(min(x), length(x)/sum(log(x)-log(min(x))))
MLlaplace <- MLdoubleexponential <- function(x) laplace(median(x), sum(abs(x-median(x))/length(x)))
MLlognormal <- function(x) {n = length(x); mu = sum(log(x))/n; lognormal(meanlog=mu, stdlog=sum((log(x)-mu)^2)/n)}
MLweibull <- function(x, shapeinterval=c(0.001,500)) { 
  f = function(k) sum(x^k * log(x)) / sum(x^k) - sum(log(x)) / length(x) - 1/k  
  k = uniroot(f, shapeinterval)$root
  el = exp(log(sum(x^k)/length(x))/k)
  weibull(scale=el, shape=k)
  }


##########################################################################
# Validation and distance metrics and norms
##########################################################################

wasserstein = areametric = function(x,y) sum(abs(sort(x@x) - sort(y@x))) / MC$many

smirnov = function(x,y) {
  nx = length(x@x)
  ny = length(y@x)
  o = order(c(x@x,y@x))
  r = c(rep(1,nx),rep(0,ny))
  cx = cumsum(r[o])/nx
  cy = cumsum((1-r)[o])/ny
  # w = which.max(abs(cx-cy)); lines(rep(c(x@x,y@x)[o][[w]],2), c(cx[[w]], cy[[w]]), col='red')
  return(max(abs(cx-cy)))
  }



##########################################################################
# Replicate and sequence operations 
##########################################################################

rep.mc <- function(x, ...) {
  r = NULL
  for (i in 1:list(...)[[1]]) r = c(r,x)
  return(r) 
  }


##########################################################################
# Exporting, writing, printing, plotting, summary, and str functions 
##########################################################################

summary.mc <- function (object, ...) {
  if (!is.mc(object)) stop('Object is not an MC distribution')
  ans <- list(mean='', variance='', sd='', iqr='', iqr.width=0, range='', left=0, 
   percentile.01='', percentile.05='', percentile.25='', median='',
   percentile.75='', percentile.95='', percentile.99='', right=0, replications=0)
  ans$mean              <- mean.mc(object)
  ans$variance          <- var.mc(object)
  ans$sd                   <- sd.mc(object)
  ans$iqr                  <- iqr.mc(object)
  #ans$iqr.width       <- width.interval(iqr.mc(object))
  ans$range              <- range.mc(object)
  ans$left                  <- left.mc(object)
  ans$percentile.01    <- cut.mc(object, 0.01)
  ans$percentile.05    <- cut.mc(object, 0.05)
  ans$percentile.25    <- cut.mc(object, 0.25)
  ans$median            <- cut.mc(object, 0.50)
  ans$percentile.75    <- cut.mc(object, 0.75)
  ans$percentile.95    <- cut.mc(object, 0.95)
  ans$percentile.99    <- cut.mc(object, 0.99)
  ans$right                <- right.mc(object)
  ans$replications      <- object@n
  class(ans)               <- "summary.mc"
  ans
  }

# specify other args by calling this DIRECTLY. as "print.summary.mc(summary.mc(x), digits=4)"

print.summary.mc <- function(x, ...) {  
  replaceempty <- function(s,r) if (s=='') r else s
  cat('\nMonte Carlo distribution summary',
      '\n  Mean: ',format(x$mean,...),
      '\n  Variance: ',format(x$variance,...),
      '\n  Std Deviation: ',format(x$sd,...),
      '\n  Width of interquartile range: ',format(diff(x$iqr),...),
      '\n  Width of overall range: ',format(diff(x$range),...),
      '\n  Order statistics',
      '\n     Left (min) value: ',format(x$left,...),
      '\n     1st percentile: ', format(x$percentile.01,...),
      '\n     5th percentile: ', format(x$percentile.05,...),
      '\n     25th percentile: ', format(x$percentile.25,...),
      '\n     Median (50th%ile): ', format(x$median,...),
      '\n     75th percentile: ', format(x$percentile.75,...),
      '\n     95th percentile: ', format(x$percentile.95,...),
      '\n     99th percentile: ', format(x$percentile.99,...),
      '\n     Right (max) value: ', format(x$right,...),
      '\n  Replications: ', format(x$replications,...),
      '\n',sep = '')
  invisible(x)
  }

as.character.mc <- function(x, ...) paste(sep='','MC (min=',min.mc(x),', median=',median.mc(x),', mean=',mean.mc(x),', max=',max.mc(x),')')

print.mc <- function(x, ...) cat(as.character.mc(x, ...),'\n')

show.mc <- function(x, ...) {
  try(plot.mc(x, ...))
  print.mc(x, ...)
  }
 
quiet <- setMethod("show", "mc", function(object)show.mc(object))
 
updown <- function(cumulative, x) if (cumulative) x else 1-x

cumulative <- function(yes=TRUE) MC$cumulative <- yes

#plot.mc <- function(s, xlab='', ylab='Cumulative probability', cumulative=MC$cumulative, ...) {
#  if (!cumulative) ylab = 'Exceedance probability'
#  plot(c(min(s@x),sort(s@x)),updown(cumulative,seq(0,1,length.out=1+length(s@x))),type='s', xlab=xlab,ylab=ylab,...)
#  bringToTop(-1) # return focus to R console
#  }

# if first two args are both mc, bivariate plot is made, else the edf is displayed using the second arg, if provided, as the label 
plot.mc <- function(x, t=NULL, xlab=t, ylab='Cumulative probability', cumulative=MC$cumulative, ...) {
  if (is.mc(t)) {
        xlab <- deparse(substitute(x))
        ylab <- deparse(substitute(t))
        plot(x@x,t@x,xlab=xlab,ylab=ylab, ...)
        } else { 
        if (missing(xlab)) xlab <- deparse(substitute(x))
        if (!cumulative) ylab = 'Exceedance probability'
        plot(c(min(x@x),sort(x@x)),updown(cumulative,seq(0,1,length.out=1+length(x@x))),type='s', xlab=xlab,ylab=ylab,...)
        }
  if (.Platform$OS.type=='windows') if(!RStudio) bringToTop(-1) # return focus to R console
  }

edf.numeric <- function(x, new=dev.cur()==1, xlab='', ylab='Cumulative probability', xlim=range(x), ylim=c(0,1), ...) {
  if (new) {plot(NULL,NULL,xlab=xlab,ylab=ylab,xlim=xlim,ylim=ylim, ...); if (.Platform$OS.type=='windows') if(!RStudio) bringToTop(-1)}
  lines(c(min(x),sort(x)),seq(0,1,length.out=1+length(x)),type='s', ...)
  }
  
edf.mc <- function(b,xlab=deparse(substitute(b)),new=dev.cur()==1,...) edf.numeric(b@x,xlab=xlab,new=new,...)

if(!isGeneric("edf")) quiet <- setGeneric("edf", function(x, ...) standardGeneric("edf"))
quiet <- setMethod('edf', 'mc', function(x, ...) edf.mc(x,...))
quiet <- setMethod('edf', 'numeric', function(x, ...) edf.numeric(x,...))

lines.mc <- points.mc <- function(s,xlab='',cumulative=MC$cumulative, ...) {
  lines(c(min(s@x),sort(s@x)),updown(cumulative,seq(0,1,length.out=1+length(s@x))),type='s',...)
  if (.Platform$OS.type=='windows') if(!RStudio) bringToTop(-1) # return focus to R console
  }

plot.mc.scale <- function(min, max, name='',cumulative=MC$cumulative, col=NULL, ...) {
  if (cumulative) ylab = 'Cumulative probability' else ylab = 'Exceedance probability'
  plot(c(min,max),c(0,1),xlab=name, ylab=ylab, col='white', ...)
  }

plot.mclist <- function(A,...) {
  rm <-  Inf; for (i in 1:length(A)) {r <-  left.mc(A[[i]]); if (is.finite(r)) rm <- base::min(r,rm) }
  rM <- -Inf; for (i in 1:length(A)) {r <- right.mc(A[[i]]); if (is.finite(r)) rM <- base::max(r,rM) }
  if ("xlim" %in% attributes(list(...))$names) plot.mc.scale(list(...)$xlim[1],list(...)$xlim[2],...) else plot.mc.scale(rm, rM, ...)    
  for (i in 1:length(A)) lines(A[[i]], ...)
  }

pl <- function(...) plot(NULL,ylim=c(0,1),xlim=range(...),xlab='',ylab='Cumulative probability')

black      = bla = function(x,lwd=3,col='black',...)      edf(x,lwd=lwd,col=col,...)
red        = red = function(x,lwd=3,col='red',...)        edf(x,lwd=lwd,col=col,...)
blue       = blu = function(x,lwd=3,col='blue',...)       edf(x,lwd=lwd,col=col,...)
green      = gre = function(x,lwd=3,col='green3',...)     edf(x,lwd=lwd,col=col,...)
khaki      = kha = function(x,lwd=3,col='khaki2',...)     edf(x,lwd=lwd,col=col,...)
navy       = nav = function(x,lwd=3,col='navy',...)       edf(x,lwd=lwd,col=col,...)
purple     = pur = function(x,lwd=3,col='purple',...)     edf(x,lwd=lwd,col=col,...)
brown      = bro = function(x,lwd=3,col='sienna',...)     edf(x,lwd=lwd,col=col,...)
olive      = oli = function(x,lwd=3,col='olivedrab4',...) edf(x,lwd=lwd,col=col,...) 
gray       = gra = function(x,lwd=3,col='gray',...)       edf(x,lwd=lwd,col=col,...)
orange     = ora = function(x,lwd=3,col='darkorange',...) edf(x,lwd=lwd,col=col,...)
pink       = pin = function(x,lwd=3,col='deeppink',...)   edf(x,lwd=lwd,col=col,...)
cyan       = cya = function(x,lwd=3,col='cyan',...)       edf(x,lwd=lwd,col=col,...)
chartreuse = cha = function(x,lwd=3,col='chartreuse',...) edf(x,lwd=lwd,col=col,...)
gold       = gol = function(x,lwd=3,col='gold',...)       edf(x,lwd=lwd,col=col,...)
ecru       = ecr = function(x,lwd=3,col='tan',...)        edf(x,lwd=lwd,col=col,...)
brick      = bri = function(x,lwd=3,col='firebrick3',...) edf(x,lwd=lwd,col=col,...)

units = function(s) return(1) # the R library doesn't support units or units checking like RAMAS Risk Calc does

if ("MC$scott.used.to.be.quiet" %in% ls()) {quiet <- MC$scott.used.to.be.quiet; rm("MC$scott.used.to.be.quiet")} else rm("quiet")
cat(':sra> library loaded\n')

##########################################################################
# End of Monte Carlo Simulation S4 Library for the R Language                
##########################################################################
