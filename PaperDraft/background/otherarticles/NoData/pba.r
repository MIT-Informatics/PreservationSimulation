
RStudio = FALSE

############################################################################
# Probability Bounds Analysis S4 library for the R Language                
#                                                                          
# Proprietary software of Applied Biomathematics (www.ramas.com)           
# Authors: Scott Ferson and Jason O'Rawe, Applied Biomathematics                             
# Dates: episodically updated and extended since February 2006
# Copyright 2006-2015 Applied Biomathematics; All rights reserved worldwide     
############################################################################
#
# Place this file on your computer and, from within R, select 
# File/Source R code... from the main menu.  Select this file and
# click the Open button to read it into R.  You should see the 
# completion message ":pbox> library loaded".  Once the library 
# has been loaded, you can define probability distributions 
#
#       a = normal(5,1)
#       b = uniform(2,3)
#
# and  p-boxes 
#
#       c = meanvariance(0,2)
#       d = lognormal(interval(6,7), interval(1,2))
#       e = mmms(0,10,3,1)
#
# and perform mathematical operations on them, including the 
# Frechet convolution such as 
#
#       a  %+%  b
#
# or a traditional convolution assuming independence
#
#       a  %|+|%  b
#
# If you do not enclose the operator inside percent signs or 
# vertical bars, the software tries to figure out how the
# arguments are related to one another. Expressions such as
#
#       a + b
#       a + log(a) * b
#       
# autoselect the convolution to use.  If the software cannot 
# tell what dependence the arguments have, it uses a Frechet 
# convolution.  
#
# Variables containing probability distributions or p-boxes 
# are assumed to be independent of one another unless one 
# formally depends on the other, which happens if one was 
# created as a function of the other. Assigning a variable 
# containing a probability distribution or a p-box to another 
# variable makes the two variables perfectly dependent.  To 
# make an independent copy of the distribution or p-box, use 
# the samedistribution function, e.g., c = samedistribution(a).
#
# By default, separately constructed distributions such as 
#
#       a = normal(5,1)
#       b = uniform(2,3)
#
# will be assumed to be independent (so their convolution a+b 
# will be a precise distribution).  You can acknowledge any
# dependencies between uncertain numbers by mentioning their 
# dependence when you construct them with expressions like 
#
#       b = pbox(uniform(2,3), depends=a)
#
# You can also make an existing uncertain number dependent on 
# another with an assignment like
#
#       b = pbox(b, depends=a)
#
# If the variables are mutually dependent, be sure to make the 
# reciprocal assignment
#
#       a = pbox(a, depends=b)
#
# You can acknowledge several dependencies at a time, as with
#
#       d = pbox(d, depends=c(a,b))
#
# but you can't mention an uncertain number in the 'depends' 
# array before the uncertain number exists.
#
# As alternatives to independence and (unspecified) dependence, 
# you can also specify that an uncertain number is perfectly or 
# oppositely dependent on another.
#
#       d = beta(2,5, perfect=a)
# or
#       d = beta(2,5, opposite=a)
#
# Perfect and opposite dependencies are automatically mutual, 
# so it is not necessary to explicitly make the reciprocal 
# assignment.  Thus
#
#       a = N(5,1)
#       b = U(2,3, perfect=a)
#       c = N(15,2, perfect=b)
#
# suffices to link c with a and vice versa.  The assignments
# automatically make a, b, and c mutually perfectly dependent.  
# Naturally, it is not possible to be perfectly (or oppositely) 
# dependent on more than one quantity unless they are also 
# mutually dependent in the same way.  The indep, perfect, 
# opposite and depends functions check whether their two 
# arguments are independent, perfectly dependent, oppositely 
# dependent, or dependent, respectively.  The depends function 
# returns an interval code that is zero if its arguments are 
# independent, +1 if they are perfect, etc.
#
# The defined mathematical operators include 
#
#               Auto  Frechet  Perfect Opposite Independent
# Addition:    	 +	%+%	%/+/%	%o+o%	  %|+|%		 	 
# Subtraction:   -	%-%   	%/-/%	%o-o%	  %|-|%		 	 
# Product: 	 *	%*%	%/*/%	%o*o%	  %|*|%		 	 
# Division: 	 /	%/%  	%///%	%o/o%	  %|/|%	 		 
# Minimum: 		%m%	%/m/%	%omo%	  %|m|%		 	 
# Maximum:		%M%	%/M/%	%oMo%	  %|M|%		 	
# Powers:	 ^	%^%	%/^/%	%o^o%	  %|^|%		 	 
# Less than:	 <	%<%	%/</%	%o<o%	  %|<|%		
# Greater than:	 >	%>%	%/>/%	%o>o%	  %|>|%		 
# Less or equal: <=	%<=%	%/<=/%	%o<=o%	  %|<=|%		
# Greater/equal: >=	%>=%	%/>=/%	%o>=o%	  %|>=|%		 
# Conjunction:		%&%			  %|&|%		 
# Disjunction:		%|%			  %|||%		 
#
# Note that the operators %*% and %/% (which in R normally
# invoke matrix multiplication and integer division) have 
# been reassigned.  Also notice that &, |, &&, || have not 
# been extended for uncertain numbers.  You must use the 
# operators with percent signs to compute conjunctions or 
# disjunctions.
# 
# In addition to these "in-fix" operators, several binary 
# functions are also defined such as 
#
#       env, imp, pmin, pmax, smin, smax, and, or, not
#
# Note that the imp function gives the intersection of uncertain
# numbers.  Several standard mathematical transformations have 
# also been extended to handle p-boxes, including
#
#       exp, log, sqrt, atan, abs, negate, reciprocate, int
# 
# Use the output commands to see the resulting uncertain numbers, 
# such as
#
#       show(c)
#       summary(d)
#       plot(a)
#       lines(b, col='blue')
#
# There are a variety of standard functions you can use with 
# distributions and p-boxes, such as 
#
#       mean(a)
#       sd(b)
#       var(b)
#       median(c)
#
# as well as some new functions such as
#
#       breadth(d)
#       leftside(c)
#       left(a)
#       prob(a, 3)
#       cut(a, 0.2)
#
###############################################################


####################
# Global constants #
####################
Pbox <- new.env()
Pbox$steps <- 200              # discretization levels of probability
Pbox$bOt <- 0.001              # smallest quamtile to use if left tail is unbounded
Pbox$tOp <- 0.999              # largest quamtile to use if right tail is unbounded
Pbox$plotting <- TRUE          # if TRUE, p-pboxes are plotted whenever they are "show"n
Pbox$plotting.every <- FALSE    # if TRUE, every p-box that's created is automatically plotted
Pbox$cumulative <- TRUE        # if TRUE, plot CDFs, if FALSE, plot CCDFs (exceedance risks)
Pbox$pboxes = 0                # number of p-boxes that have been created
Pbox$verbose = 2                 # how much warning messaging is wanted
Pbox$meandisagreementmessage = "Disagreement between theoretical and observed mean\n"
Pbox$vardisagreementmessage = "Disagreement between theoretical and observed variance\n"

# minimize footprint
if ("quiet" %in% ls()) Pbox$scott.used.to.be.quiet <- quiet


########################################################
# Class specification and general interval constructor #
########################################################

interval.autocorrecting <- TRUE

quiet <- setClass('interval',representation(lo='numeric', hi='numeric')) 

print.interval <- function(x, ...) {cat(sep='','Interval: [',x@lo,', ',x@hi,']\n') }

show.interval <- function(x, ...) print.interval(x, ...)

I <- i <- interval <- function(low, high=NULL) {
  if (missing(low) && missing(high)) return(new("interval",lo=-Inf,hi=Inf))
  if (inherits(low,'pbox')) return(range(low))
  debug <- FALSE
  if (debug) cat('Entering with') #,low, high)
  lo =-Inf
  hi = Inf
  if (is.null(high)) 
    {if (debug) cat('AA')
     if (is.interval(low))    {if (debug) cat('BB'); lo <- low@lo;   hi <- low@hi}
     else if (length(low)==1) {if (debug) cat('CC'); lo <- low;      hi <- low}
     else if (length(low)==2) {if (debug) cat('DD'); lo <- low[[1]]; hi <- low[[2]]}
    }
  else 
    {if (debug) cat('EE'); 
     lo <- low
     if (is.interval(low)) lo <- low@lo           
     if (length(lo)==2)    lo <- low[[1]]

     hi <- high
     if (is.interval(high)) hi <- high@hi
     if (length(lo)==2)     hi <- high[[2]]
    }
# if (hi < lo) if (interval.autocorrecting) {swap <- lo; lo <- hi; hi <- swap} else throw.error('Unordered interval')
  new("interval", lo=lo, hi=hi)
  }

quiet <- setMethod("show", "interval", function(object)show.interval(object))


####################################
# Some ancillary utility functions #
####################################

nothing <- function(nearZero) abs(nearZero) < 1.0e-100
ami <- function(i,j) isTRUE(all.equal(i,j)) #what kind of a construction is this that it doesn't already have a shortcut?

present <- function(...) {
  el <- list(...)
  ok <- TRUE
  for (i in 1:length(el)) if (identical(el[[i]],NULL)) ok <- FALSE    
  ok    
  }

edf.numeric <- function(x, new=dev.cur()==1, xlab='', ylab='Cumulative probability', xlim=range(x), ylim=c(0,1), ...) {
  if (new) plot(NULL,NULL,xlab=xlab,ylab=ylab,xlim=xlim,ylim=ylim, ...); if (.Platform$OS.type=='windows') if(!RStudio) bringToTop(-1)
  lines(c(min(x),sort(x)),seq(0,1,length.out=1+length(x)),type='s', ...)
  }

edf.pbox <- function(b, new=dev.cur()==1, ...) if (new) plot(b,...) else lines(b,...)


##################
# Access methods #
##################

left.interval <- function(x) x@lo

right.interval <- function(x) x@hi

min.interval <- function(x) x@lo

max.interval <- function(x) x@hi

midpoint <- midpoint.interval <- function(x) (x@hi+x@lo)/2

width <- width.interval <- function(x) x@hi - x@lo 

as.vector.interval <- function(i,mode='numeric') return(c(left(i),right(i)))

as.interval.interval <- function(x) x

rep.interval <- function(x, ...) {r = NULL; for (i in 1:list(...)[[1]]) r = c(r,x); return(r) }

specific.interval <- function(x) runif(1,left(x),right(x))

# wrap access methods

quiet <- setMethod('==', c('interval','interval'), function(e1, e2){ same(e1,e2) })
quiet <- setMethod('==', c('interval','numeric'), function(e1, e2){ same(e1,e2) })
quiet <- setMethod('==', c('numeric','interval'), function(e1, e2){ same(e1,e2) })


#############################################################
# Mathematical transformations and operations for intervals #
#############################################################

exp.interval <- function(x) interval(lo=exp(x@lo), hi=exp(x@hi)) 
 
log.interval <- function(x, expo = 2.7182818284590) {
  if (expo == 2.7182818284590) interval(lo=log(x@lo), hi=log(x@hi)) else 
  interval(lo=log(x@lo,expo), hi=log(x@hi,expo)) 
  }

sqrt.interval <- function(x) interval(lo=sqrt(x@lo), hi=sqrt(x@hi)) 
  
negate.interval <- function(x) interval(lo=-x@hi, hi=-x@lo) 
  
complement.interval <- function(x) interval(lo=1-x@hi, hi=1-x@lo) 
  
sign.interval <- function(x) if (right(x)<0) -1 else if (0<left(x)) +1 else if (is.scalar(x) && identical(x@lo,0)) 0 else if (right(x)<=0) interval(-1,0) else if (0<=left(x)) interval(0,1) else interval(-1,1)

abs.interval <- function(x) {r = abs(range.interval(x)); if (straddles(x)) interval(0, max(r)) else return(interval(min(r),max(r))) }

reciprocate.interval <- function(x) interval(lo=1/rev(x@hi), hi=1/rev(x@lo))   # unless straddling!!
 
mult.interval <- function(m, x) if (m < 0) negate.interval(mult.interval(abs(m),x)) else interval(lo=+m*x@lo, hi=m*x@hi)

int.interval <- trunc.interval <- function(x) interval(lo=trunc(x@lo), hi=trunc(x@hi)) 
round.interval <- function(x) interval(lo=round(x@lo), hi=round(x@hi)) 
ceiling.interval <- function(x) interval(lo=ceiling(x@lo), hi=ceiling(x@hi)) 
is.finite.interval <- function(x) all(c(is.finite(left(x)),is.finite(right(x))))

asin.interval <- function(x) interval(lo=asin(x@lo), hi=asin(x@hi)) 
acos.interval <- function(x) interval(lo=acos(x@hi), hi=acos(x@lo)) 
atan.interval <- function(x) interval(lo=atan(x@lo), hi=atan(x@hi)) 

truncate.interval <- function(x,m,M) {
  interval(pmin(M, pmax(m,x@lo)), pmin(M, pmax(m,x@hi))) 
  }

imp.interval <- function (..., na.rm = FALSE) {  
  elts <- list(...)
  mmm <- elts[[1]]
  for (each in elts[-1])
    mmm <- interval(lo = max(left(mmm),left(each),na.rm=na.rm), hi = min(right(mmm),right(each),na.rm=na.rm))
  # should check whether they now cross
  if (mmm@hi < mmm@lo) {warning('Imposition is empty'); mmm <- NULL}
  mmm
  }

env.interval <- function (..., na.rm = FALSE) {  
  elts <- list(...)
  mmm <- elts[[1]]
  for (each in elts[-1])
    mmm <- interval(lo = min(left(mmm),left(each),na.rm=na.rm), hi = max(right(mmm),right(each),na.rm=na.rm))
  mmm
  }

pmin.interval <- lesser.interval <- function (..., na.rm = FALSE) {  
  elts <- list(...)
  mmm <- elts[[1]]
  for (each in elts[-1])
    mmm <- interval(lo = min(left(mmm),left(each),na.rm=na.rm), hi = min(right(mmm),right(each),na.rm=na.rm))
  mmm
  }

pmax.interval <- bigger.interval <- function (..., na.rm = FALSE) {  
  elts <- list(...)
  mmm <- elts[[1]]
  for (each in elts[-1])
    mmm <- interval(lo = max(left(mmm),left(each),na.rm=na.rm), hi = max(right(mmm),right(each),na.rm=na.rm))
  mmm
  }


###########################
# Convolutions operations for intervals #
###########################

conv.interval <- function(x,y,op='+') {
  if (op=='-') return(conv.interval(x,negate.interval(y),'+'))
  if (op=='/') return(conv.interval(x,reciprocate.interval(y),'*'))

  if (op == '+') {
    lo <- x@lo + y@lo
    hi <- x@hi + y@hi
    }

  if (op == '*') {
    lo <- min(x@lo * y@lo,x@lo * y@hi,x@hi * y@lo,x@hi * y@hi)
    hi <- max(x@lo * y@lo,x@lo * y@hi,x@hi * y@lo,x@hi * y@hi)
    }
  interval(lo, hi)
  }


####################
# In-fix Operators #
####################

# default addition

quiet <- setMethod('+', c('interval','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){interval(lo=e1@lo + e2, hi=e1@hi + e2) })

quiet <- setMethod('+', c('numeric','interval'),
  function(e1, e2){e2 + e1})

quiet <- setMethod('+', c('interval','interval'),function(e1,e2){
  return( conv.interval(e1,e2,'+')  )})   



# default multiplication

quiet <- setMethod('*', c('interval','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){ mult.interval(e2, e1) })

quiet <- setMethod('*', c('numeric','interval'),
  function(e1, e2){ mult.interval(e1, e2) })

quiet <- setMethod('*', c('interval','interval'),function(e1,e2){
  return(  conv.interval(e1,e2,'*')  )})   



# default subtraction

quiet <- setMethod('-', c('interval','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){interval(lo=e1@lo - e2, hi=e1@hi - e2) })

quiet <- setMethod('-', c('numeric','interval'),
  function(e1, e2){ e1 + negate.interval(e2) })

quiet <- setMethod('-', c('interval','interval'),function(e1,e2){
  return(  conv.interval(e1,negate.interval(e2),'+')  )})   



# default division

quiet <- setMethod('/', c('interval','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){ mult.interval(1/e2, e1) })

quiet <- setMethod('/', c('numeric','interval'),
  function(e1, e2){ mult.interval(e1, reciprocate.interval(e2)) })

quiet <- setMethod('/', c('interval','interval'),function(e1,e2){
  return(  conv.interval(e1,reciprocate.interval(e2),'*')  )})   

quiet <- setMethod('^', c('interval','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){
#cat('Exponentiating...')
         ans <- interval(lo=e1@lo ^ e2, hi=e1@hi ^ e2) 
         if (identical(e2,0)) ans <- 1
    else if (identical(e2,1))  ans <- e1
    else if (identical(e2 %% 2, 0)) {
#cat('Even...')
                if (0 <= e1@lo)                  ans <- interval(lo=e1@lo ^ e2, hi=e1@hi ^ e2)
                if ((e1@lo < 0) & (0 < e1@hi))   ans <- interval(lo=0,hi=max(e1@lo ^ e2, e1@hi ^ e2))
                if (e1@hi <= 0)                  ans <- interval(lo=e1@hi ^ e2, hi=e1@lo ^ e2)
                }
    ans}
    )


#####################################################
# Class specification and general p-box constructor #
#####################################################

quiet <- setClass('pbox',representation(id='character', u='numeric', d='numeric', n='integer', shape='character', ml='numeric', mh='numeric', vl='numeric', vh='numeric', name='character', dids='character', bob='integer')) 

uniquepbox <- function() { Pbox$pboxes <- Pbox$pboxes + 1; return(paste(Pbox$pboxes)) }

pbox <- function(u, d=u, shape=NULL, name=NULL, ml=NULL, mh=NULL, vl=NULL, vh=NULL, dids=NULL, interpolation='linear', other=NULL, bob=NULL, perfect=NULL, opposite=NULL, depends=NULL) {
  if (missing(u) && missing(d)) { u <- -Inf; d <- Inf } 
  if (inherits(u,'pbox')) p <- u                else
    {
      if (!is.number(d) || !is.number(u)) stop('Bounds of a p-box must be numeric')   # cat('PBOX says d =',d,' which is mode',mode(d),'\n')
      d <- d + 0  # remedies what seems to be a bug (a feature?); without it, pbox(interval(1,2)) returns a scalar 1
      if (inherits(u,'interval')) u <- left(u)   #myvectormin(as.vector(u),as.vector(d))
      if (inherits(d,'interval')) d <- right(d)  

#      if (ami(Pbox$steps,1) || (ami(min(u),max(u)) && ami(min(d),max(d))) )
#         { u <- min(u[is.finite(u)]); d <- max(d[is.finite(d)]); other = c(other,"interval")} 
#      else 
         {
          if (!ami(length(u),Pbox$steps)) u <- interpolate(u,interpolation,TRUE); 
          if (!ami(length(d),Pbox$steps)) d <- interpolate(d,interpolation,FALSE)
         }
      unique <- uniquepbox()
      id <- paste('PB',unique,sep='')
      if (!missing(bob)) unique <- bob
      p <- new("pbox", id=id, u=u, d=d, n=as.integer(Pbox$steps), shape='', name='', ml=-Inf, mh=Inf, vl=0, vh=Inf, dids=paste(id, dids), bob=as.integer(unique))
    }
#  class(p) <- c(other,'pbox','numeric')
  class(p) <- c('pbox')
  p <- computemoments(p)
  if (!missing(shape))    p@shape <- shape
  if (!missing(ml))       p@ml <- pmax(ml,p@ml)
  if (!missing(mh))       p@mh <- pmin(mh,p@mh)
  if (!missing(vl))       p@vl <- pmax(vl,p@vl)
  if (!missing(vh))       p@vh <- pmin(vh,p@vh)
  if (!missing(dids))      p@dids <- paste(p@id,dids)          
  if (!missing(opposite)) p@bob <- -opposite@bob 
  if (!missing(perfect))  p@bob <- perfect@bob
  if (!(missing(depends) || is.null(depends)))  p@dids <- paste(p@id,dids(depends))
  if (!missing(name))     p@name <- name
  if (Pbox$plotting.every) try(plot.pbox(p))
  checkmoments(p)
  }

as.pbox <- as.pbox.numeric <- as.pbox.interval <- pbox

makepbox <- function(...) {  #  works for a bunch of args separated by commas, or for a single list of args
  elts <- list(...)
  if (mode(elts[[1]])=='list') elts <- elts[[1]]
  if (ami(1,length(elts))) return(pbox(...))
  for (i in seq(along=elts)) if (!is.pbox(elts[[i]])) elts[[i]] <- pbox(elts[[i]])
  elts
  }

####################################
# Some ancillary utility functions #
####################################

nothing <- function(nearZero) abs(nearZero) < 1.0e-100

Gamma <- gammafunc <- function(x) .Primitive("gamma")(x)

lambertW <- function(x) {  # argument must be larger than -1/e
  prec = 1e-12
  w = rep(NA,length(x))
  w = ifelse(500 < x, log(x - 4.0) - (1.0 - 1.0/log(x)) * log(log(x)), w)
  lx1 = log(x + 1.0)
  w = ifelse((-1/exp(1) < x) & (x <= 500), 0.665 * (1 + 0.0195 * lx1) * lx1 + 0.04, w)
  i = 1
  diff = rep(1,length(x))
  while (i < 100) {
                i = i + 1
                wew = w * exp(w)
                wpew = (w+1) * exp(w)
                diff = abs((x-wew)/wpew)
                w = w-(wew-x)/(wpew-(w+2)*(wew-x)/(2*w+2))
                }
  w
  }

####################################
# Interpolation schemes            #
####################################

# The pbox() constructor accepts lists of x-values for
# the left and right bounds.  Four different interpolation 
# schemes can be used with these lists, including linear, 
# spline, step and outward interpolations. The spline 
# interpolation scheme requires the splines library to be 
# loaded.  See also the quantiles() constructor when 
# you have quantiles (or percentiles or fractiles), or 
# the pointlist() constructor when you have a point 
# list description of the p-box.

interpolate <- function(u, interpolation='linear',left=TRUE) switch(interpolation, "outer"={outer.interpolate(u,left)}, "spline"={spline.interpolate(u)}, "step"={step.interpolate(u)}, {linear.interpolate(u)})

step.interpolate <- function(u) return(unlist(u)[trunc(seq(from=1,to=length(u)+0.99999,length.out=Pbox$steps))])

spline.interpolate <- function(u) {library(splines); return(predict(interpSpline(1:length(u),u),nseg=Pbox$steps-1)$y)}  # needs the splines library

left.interpolate <- function(u) return(qleftquantiles(ii(), u, 0:(length(u)-1)/(length(u)-1)))

right.interpolate <- function(d) return(qrightquantiles(jj(), d, 0:(length(d)-1)/(length(d)-1)))

outer.interpolate <- function(x,left) if (left) return(left.interpolate(x)) else return(right.interpolate(x))

linear.interpolate <- function(V) {
  m <- length(V) - 1
  if (ami(m,0)) return(rep(V,Pbox$steps))
  if (ami(Pbox$steps,1)) return(c(min(V),max(V)))
  d <- 1/m
  n <- round(d * Pbox$steps * 20)
  if (n==0) c = V else {
  c <- NULL
  for (i in 1:m) {
    v <- V[[i]]     
    w <- V[[i+1]]   
    c <- c(c, seq(from=v, to=w, length.out=n))
    } }
  u <- rep(0,Pbox$steps)
  for (k in 1:Pbox$steps) u[[k]] <-c[[1+round((length(c)-1)*(k-1)/(Pbox$steps-1))]]
  u
  }

interpolationexamples <- function() {
  dopb <- function(u,d,interpolation) {
    b = pbox(u,d,interp=interpolation)
    plot(b)
    lines (u, 0:(length(u)-1)/(length(u)-1), col='lightgray')
    lines (d, 0:(length(d)-1)/(length(d)-1), col='lightgray')
    points(c(u,d), c(0:(length(u)-1)/(length(u)-1),0:(length(d)-1)/(length(d)-1)),cex=1.5,pch=19,col='gray')
    lines(b)
    }
  library(splines)
  save = Pbox$steps
  Pbox$steps <- 50
  old.par <- par(mfrow=c(2,2),mar=c(2,4,3,1))
  u=c(1,2,4,5)
  d=c(2,3,6,7)
  dopb(u,d,'linear')
  dopb(u,d,'spline')  # needs at least 4 points and the interpSpline function from the library(splines)
  dopb(u,d,'step')
  dopb(u,d,'outer')
  par(old.par)
  Pbox$steps <- save
  }
  
discretizationexamples <- function() {
  dopb <- function(n) {
    save = Pbox$steps
    Pbox$steps <- n
    b = pbox(u=c(1,2,4),d=c(2,3,6,7))
    plot(b)
    lines (c(1,2,4), c(c(0,1,2)/2), col='lightgray')
    lines (c(2,3,6,7), c(0,1,2,3)/3, col='lightgray')
    points(c(1,2,4,     2,3,6,7), c(c(0,1,2)/2,c(0,1,2,3)/3),cex=1.5,pch=19)
    lines(b)
    Pbox$steps <- save
    }
  for (n in rev(10:100)) dopb(n)
  }

#interpolationexamples()
#discretizationexamples()


##########################################
# Interacting with the R-package "distr" #
##########################################

# If the R-package 'distr', including its extention the 'distrEx' package, have been loaded, 
# their objects can be incorporated into expressions with p-boxes.

# If you have already installed these packages, you can load them with the 'require' function
#options("StartupBanner"=NULL)
#distr.loaded <- require("distr")  
#distrEx.loaded <- require("distrEx")  
#distroptions("WarningArith" = FALSE)  # switches off warnings as to arithmetics

distr.loaded <- "package:distrEx" %in% search()

################################
# Functions to compute moments #
################################

dwMean <- function(x) return(interval(mean(x@u),mean(x@d))) # page 126 Williamson & Downs

sideVariance <- function(w,mu=NULL) { if (missing(mu)) mu <- mean(w); return(max(0,mean((w - mu)^2))) }

#dwVariance <- function(x) {  # this is my own algorithm;  cf. page 126 Williamson & Downs
#  # assumes that u and d are the same length
##  if (any(!is.finite((x@u[2:(length(x@u)-1)]))) || any(!is.finite((x@d[2:(length(x@d)-1)])))) return(interval(0,Inf))   
#  if (any(!is.finite(x@u)) || any(!is.finite(x@d))) return(interval(0,Inf))   
#  if ((all(x@u[1] == x@u)) && (all(x@d[1] == x@d))) return(interval(0,(x@d[[1]]-x@u[[1]])^2/4))
#  vr = sideVariance(x@u,mean(x@u))  # should this use the theoretical rather than observed mean?
#  w = x@u
#  n = length(x@u)
#  for (i in rev(1:n))
#    {
#        w[[i]] = x@d[[i]]
#        v = sideVariance(w,mean(w))
#        #cat(vr,' ',v,'\n')	  # if error (missing value where TRUE/FALSE is needed), the problem is that sideVariance can't compute var of array of Inf or -Inf
#        if (vr<v) vr = v
#    }
#  if (x@u[[n]] <= x@d[[1]]) vl = 0.0 else {
#            w = x@d;
#            vl = sideVariance(w,mean(w));
#            for (i in rev(1:n))
#            {
#                here = w[[i]] = x@u[[i]]
#                if (1<i) for (j in rev(1:(i-1))) if (w[[i]]<w[[j]]) w[[j]] = here
#                v = sideVariance(w,mean(w))
#                if (v<vl) vl = v
#            }
#         }
#  return(interval(vl, vr))
#  }

dwVariance <- function(x) {  # this is my own algorithm;  cf. page 126 Williamson & Downs
  # assumes that u and d are the same length
#  if (any(!is.finite((x@u[2:(length(x@u)-1)]))) || any(!is.finite((x@d[2:(length(x@d)-1)])))) return(interval(0,Inf))   
  if (any(!is.finite(x@u)) || any(!is.finite(x@d))) return(interval(0,Inf))   
  if ((all(x@u[1] == x@u)) && (all(x@d[1] == x@d))) return(interval(0,(x@d[[1]]-x@u[[1]])^2/4))
  vr = sideVariance(x@u,mean(x@u))  # should this use the theoretical rather than observed mean?
  w = x@u
  n = length(x@u)
  for (i in rev(1:n))
    {
        w[[i]] = x@d[[i]]
        v = sideVariance(w,mean(w))
        #cat(vr,' ',v,'\n')	  # if error (missing value where TRUE/FALSE is needed), the problem is that sideVariance can't compute var of array of Inf or -Inf
        #if (vr<v) vr = v
	if (is.na(vr) | is.na(v)) vr = Inf else if (vr<v) vr = v
    }
  if (x@u[[n]] <= x@d[[1]]) vl = 0.0 else {
            w = x@d;
            vl = sideVariance(w,mean(w));
            for (i in rev(1:n))
            {
                here = w[[i]] = x@u[[i]]
                if (1<i) for (j in rev(1:(i-1))) if (w[[i]]<w[[j]]) w[[j]] = here
                v = sideVariance(w,mean(w))
                if (is.na(vl) | is.na(v)) vl = 0 else if (v<vl) vl = v
            }
         }
  return(interval(vl, vr))
  }

checkmoments <- function(x) {
  a = mean(x)
  b = dwMean(x)  
  x@ml = max(left(a),left(b))
  x@mh = min(right(a),right(b))
  if (x@mh < x@ml) {
      # use the observed mean    
      x@ml = left(b)
      x@mh = right(b)
      if (1<Pbox$verbose) cat(Pbox$meandisagreementmessage);
      }
  a = var(x)
  b = dwVariance(x)
  x@vl = max(left(a),left(b))
  x@vh = min(right(a),right(b))
  if (x@vh < x@vl) {
      # use the observed variance
      x@vl = left(b)
      x@vh = right(b)
      if (1<Pbox$verbose) cat(Pbox$vardisagreementmessage);
      }
  x # should we also tighten the u and d arrays with mmms?
  } 

computemoments <- function(x) {    # should we compute mean if it is a Cauchy, var if it's a t distribution?
  x@ml <- max(x@ml, mean(x@u))
  x@mh <- min(x@mh, mean(x@d))
  if (is.interval(x)) { 
    x@vl <- max(x@vl, 0)
    x@vh <- min(x@vh, (x@u-x@d)^2/4)
    return(x) 
    }
  if (any(x@u <= -Inf) || any(Inf <= x@d)) return(x)  # unbounded mean, so skip calculation of variance
  # variance 
  V <- 0
  JJ <- 0
  j <- 1:x@n
  for (J in 0:x@n) { 
    ud <- c(x@u[j < J], x@d[J <= j])
    v <- sideVariance(ud)    ## was sidevar
    if (V < v) { JJ <- J; V <- v }
    }
  x@vh <- V # * (x@n / 100)
  x
  }

forgetmoments <- function(b, family=FALSE){ 
  b@ml=-Inf
  b@mh=Inf
  b@vl=0
  b@vh=Inf 
  if (family) b@shape=''     # should we forget the shape too?
  b
  }


##################
# Access methods #
##################

dids        <- function(x,...) {UseMethod("dids")}
shape      <- function(x,...) {UseMethod("shape")}
steps      <- function(x,...) {UseMethod("steps")}
name       <- function(x,...) {UseMethod("name")}
left       <- function(x,...) {UseMethod("left")};         left.default    <- function(x) return(myvectormin(x))
right      <- function(x,...) {UseMethod("right")};        right.default   <- function(x) return(myvectormax(x))
min        <- function(...,na.rm=FALSE){UseMethod("min")}; min.default     <- function(..., na.rm = FALSE) myvectormin(..., na.rm = na.rm)
max        <- function(...,na.rm=FALSE){UseMethod("max")}; max.default     <- function(..., na.rm = FALSE) myvectormax(..., na.rm = na.rm)
env        <- function(...,na.rm=FALSE){UseMethod("env")}; env.default    <- function(..., na.rm = FALSE) env(..., na.rm = na.rm)
imp        <- function(...,na.rm=FALSE){UseMethod("imp")}; imp.default    <- function(..., na.rm = FALSE) imp(..., na.rm = na.rm)
mixture        <- function(...,na.rm=FALSE){UseMethod("mixture")}; mixture.default    <- function(..., na.rm = FALSE) mixture(..., na.rm = na.rm)
mix.equal  <- function(...,na.rm=FALSE){UseMethod("mix.equal")}; mix.default    <- function(..., na.rm = FALSE) mix.equal(..., na.rm = na.rm)
pmin       <- function(...,na.rm=FALSE){UseMethod("pmin")};pmin.default    <- function(..., na.rm = FALSE) base::pmin(..., na.rm = na.rm)
pmax       <- function(...,na.rm=FALSE){UseMethod("pmax")};pmax.default    <- function(..., na.rm = FALSE) base::pmax(..., na.rm = na.rm)
smin       <- function(...,na.rm=FALSE){UseMethod("smin")};smin.default    <- function(..., na.rm = FALSE) base::pmin(..., na.rm = na.rm)
smax       <- function(...,na.rm=FALSE){UseMethod("smax")};smax.default    <- function(..., na.rm = FALSE) base::pmax(..., na.rm = na.rm)
leftside   <- function(x,...) {UseMethod("leftside")} 
rightside  <- function(x,...) {UseMethod("rightside")}
breadth    <- function(x,...) {UseMethod("breadth")};      breadth.default <- function(x) return(max(x)-min(x))
prob       <- function(x,s,...) {UseMethod("prob")}
alpha      <- function(x,s,...) {UseMethod("prob")}
poss       <- function(x,s,...) {UseMethod("prob")}
#cut        <- function(x,s,...) {UseMethod("fractile")}
fractile   <- function(x,p,...) {UseMethod("fractile")}
percentile <- function(x,p,...) {UseMethod("percentile")}
int        <- function(x,...) {UseMethod("int")};          int.default     <- function(x) return(trunc(x))
truncate   <- function(x,m,M,...) {UseMethod("truncate")}; truncate.default<- function(x,...) return(base::truncate(x,...))
round      <- function(x,...) {UseMethod("round")};        round.default   <- function(x,...) return(base::round(x,...))
ceiling    <- function(x,...) {UseMethod("ceiling")};      ceiling.default <- function(x,...) return(.Primitive("ceiling")(x,...))
sign       <- function(x,...) {UseMethod("sign")};         sign.default    <- function(x,...) return(.Primitive("sign")(x,...))
negate     <- function(x,...) {UseMethod("negate")};       negate.default  <- function(x,...) return(-x)
reciprocate<- function(x,...) {UseMethod("reciprocate")};  reciprocate.default  <- function(x,...) return(1/x)
complement <- function(x,...) {UseMethod("complement")};   complement.default  <- function(x,...) return(1-x)
same       <- function(x,y,...) {UseMethod("same")};       same.default <- function(x,y,...) return(isTRUE(all.equal(x,y,...)))
and        <- function(x,y,...) {UseMethod("and")};        and.default  <- function(x,y,...) and.pbox(x,y)
or         <- function(x,y,...) {UseMethod("or")};         or.default   <- function(x,y,...) or.pbox(x,y)
not        <- function(x,...)   {UseMethod("not")};        not.default  <- function(x,...)   complement.pbox(x)
andI       <- function(x,y,...) {UseMethod("andI")};       andI.default <- function(x,y,...) andI.pbox(x,y)
orI        <- function(x,y,...) {UseMethod("orI")};        orI.default  <- function(x,y,...) orI.pbox(x,y)

as.interval<- function(x,...) {UseMethod("as.interval")}
as.pbox    <- function(x,...) {UseMethod("as.pbox")}

myvectormax <- function(..., na.rm = FALSE) {  
  a <- c(...)
  if (((isTRUE(all.equal(0,length(which.max(a)))))) || (isTRUE(all.equal(0,length(a))))) -Inf else if (!na.rm && any(is.na(a))) NA else a[[which.max(a)]]
  }

myvectormin <- function(..., na.rm = FALSE) {  
  a <- c(...)
  if (((isTRUE(all.equal(0,length(which.min(a)))))) || (isTRUE(all.equal(0,length(a))))) +Inf else if (!na.rm && any(is.na(a))) NA else a[[which.min(a)]]
  }

dids.pbox <- function(x) x@dids

dids.list = function(x,...) { 
  d = NULL 
  for (i in seq(along=x)) d <- paste(d, x[[i]]@dids)
  d
  }

shape.pbox <- function(x) x@shape

name.pbox <- function(x) x@name

steps.pbox <- function(x) if (same(x@n,length(x@d))) x@n else "Internal step count error"

left.pbox <- function(x) x@u[[1]]

right.pbox <- function(x) x@d[[x@n]]

min.pbox <- function(x) x@u[[1]]

max.pbox <- function(x) x@d[[x@n]]

sign.pbox <- function(x) if (right(x)<0) -1 else if (0<left(x)) +1 else if (is.scalar(x) && identical(x@u[[1]],0)) 0 else if (right(x)<=0) interval(-1,0) else if (0<=left(x)) interval(0,1) else interval(-1,1)

leftside.pbox <- function(x) pbox(x@u)

rightside.pbox <- function(x) pbox(x@d)

#range.pbox <- function(x, na.rm = FALSE) interval(c(x@u[[1]], x@d[[x@n]]))  # hard to believe I need to have the na.rm argument!
range.pbox <- function(..., na.rm = FALSE) {  #  works for a bunch of args separated by commas, or for a single list of args
  elts <- list(...)
  if (mode(elts[[1]])=='list') elts <- elts[[1]]
  r = c(left(elts[[1]]), right(elts[[1]]))
  if (ami(1,length(elts))) return(interval(r))
  for (i in seq(along=elts)) r = range(r, left(elts[[i]]), right(elts[[i]]))
  interval(r)
  }

iqr <- iqr.pbox <- function(x) interval(c(x@u[[round(0.25*x@n)]], x@d[[round(0.75*x@n)]]))

# OLD
#cut.pbox <- quantile.pbox <- fractile.pbox <- percentile.pbox <- function(x, p) { 
#  x <- makepbox(x)
#  if ((p<0) | (1<p)) stop('Second argument must be a probability between zero and one')
#  interval(c(x@u[[round(p*x@n)]], x@d[[round(p*x@n)]]))
#  }

cut.pbox <- quantile.pbox <- fractile.pbox <- percentile.pbox <- function(x, p, tight=TRUE) {
  # o = B@u[[i]] is the right (lower) bound on the quantile associated with probability level c = (i-1)/B@n, for all i in {1,2,...,B@n}.  
  # o = B@d[[j]] is the left (upper) bound on the quantile associated with probability level c = j/B@n, for j in {1,2,...,B@n}.
  x <- makepbox(x)  # makebox shows (and replots) the argument...is that a good idea?
  if ((p<0) | (1<p)) stop('Second argument must be a probability between zero and one')
  long = x@n
  if (tight) return(interval(c(x@u[[min(long,(((p*long) %% 1)==0)+ceiling(p*x@n))]], x@d[[max(1,ceiling(p*x@n))]])))
  if (p==1) lower = long else if ((p %% (1/long)) == 0) lower = round(p*long) else lower = ceiling(p*long)
  if (p==0) upper = 1 else if ((p %% (1/long)) == 0) upper = round(p*long)+1 else upper = floor(p*long)+1
  interval(x@u[[max(lower,1)]], x@d[[min(upper,long)]])
  }

random <- function(x,n=1) if (n==1) return(cut(x,runif(1))) else {c=NULL; for (i in 1:n) c=c(c,cut(x,runif(1))); return(c)}
randomrange <- function(x,n=1) return(left(x)+runif(n)*(right(x)-left(x)))
specific <- function(x,n=1) {c=NULL; for (i in 1:n) c=c(c,randomrange(cut(x,runif(1)))); return(c)}  # return(randomrange(random(x)))

# OLD
#prob.pbox <- alpha.pbox <- poss.pbox <- function(x, s) {
#  x <- makepbox(x)
#  interval(c(length(x@d[x@d<s]),length(x@u[x@u<s]))/Pbox$steps)
#  }
 
prob.pbox <- alpha.pbox <- poss.pbox <- function(x, s) {
  x <- makepbox(x)
  interval(c(length(x@d[x@d<s]),length(x@u[x@u<=s]))/Pbox$steps)
  }

xprob.pbox <- function(x, s) {    # required by the inequality comparisons
  x <- makepbox(x); 
  interval(c(length(x@d[x@d<=s]),length(x@u[x@u<s]))/Pbox$steps) 
  }

median.pbox <- function(x, na.rm = FALSE) percentile.pbox(x,0.5)

# actually returns a vector of EIGHT numbers, because the quartiles are intervals
fivenum.pbox <- function(x, na.rm = FALSE) c(minimum=left.pbox(x), firstquartile=percentile.pbox(x,0.25), median=median.pbox(x), thirdquartile=percentile.pbox(x,0.75), maximum=right.pbox(x))

mean.pbox <- function(x) interval(c(x@ml,x@mh))

var.pbox <- function(x) interval(c(x@vl,x@vh))

sd.pbox <- function(x) interval(sqrt(c(x@vl,x@vh)))   

as.vector.pbox <- function(x,mode='numeric',pairs=FALSE) {
  if (pairs) return(0) else return(as.vector(c(x@u,x@d),mode=mode))
  }

as.matrix.pbox <- function(x, ...) matrix(c(x@u, x@d), nrow = x@n, dimnames = list(as.character(1:x@n), c("Left", "Right")))

as.interval.pbox <- function(x, ...) interval(x@u[[1]],x@d[[x@n]])

all.equal.pbox <- all.equal.interval <- function(x,y, tol=1e-6, check.moments=TRUE, check.shape=TRUE, ...) {
  x <- makepbox(x)
  y <- makepbox(y)
  b <- all.equal.numeric(c(x@u,x@d), c(y@u,y@d), ...)
  if (!isTRUE(b)) return(paste('bounds differ (',b,')'))
  if (check.moments) b <- all.equal.numeric(c(x@ml,x@mh,x@vl,x@vh), c(y@ml,y@mh,y@vl,y@vh), ...)
  if (!isTRUE(b)) return(paste('moments differ (',b,')'))
  if (check.shape) b <- all.equal.character(x@shape, y@shape, ...) 
  if (!isTRUE(b)) return('shape families differ') 
  return(b)
  }

same.pbox <- same.interval <- function(x,y,...) return (isTRUE(all.equal(x,y,...)))

severalsame <- function(e1,e2) {
  l1 <- length(e1); if (same(l1,1)) e1 <- c(e1,e1)
  l2 <- length(e2); if (same(l2,1)) e2 <- c(e2,e2)
  m <- max(l1,l2)
  i <- j <- k <- 0
  b <- NULL
  while (k < m) {
    k <- k + 1
    i <- ((i ) %% l1) + 1
    j <- ((j ) %% l2) + 1
    b <- c(b, same(e1[i], e2[j]))
    }
  return(b)
  }

breadth.pbox <- function(b) {
  b <- makepbox(b)
  s = 1 / length(b@d)
  c <- sum(s * (b@d - b@u))
  c
  }


edit.pbox <- function (name = NULL, file = "", title = NULL, editor = getOption("editor"), 
    ...) 
{
    if (is.pbox(name)) 
    {
        if (is.null(title)) 
            title <- deparse(substitute(name))
        .Internal(edit(name, file, title, editor))
    }
}


# wrap access methods

quiet <- setMethod('==', c('pbox','pbox'), function(e1, e2){ same(e1, e2) })

##if(!isGeneric("fivenum")) quiet <- setGeneric("fivenum", function (x, na.rm = FALSE) standardGeneric("fivenum"))
##quiet <- setMethod('fivenum', 'pbox', function (x, na.rm = FALSE) fivenum.pbox(x, na.rm = FALSE))
 
# there is no generic function iqr;  IQR returns the length of the iqr

if(!isGeneric("sd")) quiet <- setGeneric("sd", function(x, na.rm = FALSE) standardGeneric("sd"))
quiet <- setMethod('sd', 'pbox', function(x, na.rm = FALSE) sd.pbox(x))

if(!isGeneric("var")) quiet <- setGeneric("var", function(x, y = NULL, na.rm = FALSE, use) standardGeneric("var"))
quiet <- setMethod('var', 'pbox', function(x, y, na.rm, use) var.pbox(x))

#this replaced the following hack, which appeared to work, but might collide with other packages 
#var <- function(x, ...) if (is.pbox(x)) var.pbox(x) else stats::var(x, ...)

# replacement functions

if(!isGeneric("shape<-")) quiet <- setGeneric("shape<-", function(object, value) standardGeneric("shape<-"))
quiet <- setReplaceMethod("shape", "pbox", function(object, value){ object@shape = value; object})

if(!isGeneric("name<-")) quiet <- setGeneric("name<-", function(object, value) standardGeneric("name<-"))
quiet <- setReplaceMethod("name", "pbox", function(object, value){ object@name = value; object})


##########################################################################
# Typing functions                                                       #
##########################################################################

is.pbox <- function(x) inherits(x,'pbox')

is.interval <- function(x) return(inherits(x,'interval') || (inherits(x,'pbox') && (x@d[[1]]==x@d[[steps(x)]]) &&  (x@u[[1]]==x@u[[steps(x)]])))

is.scalar <- function(x) {
  if (is.pbox(x) && isTRUE(all.equal(left(x),right(x)))) return(TRUE)
  if (is.interval(x) && isTRUE(all.equal(left(x),right(x)))) return(TRUE)
# if (is.numeric(x) && identical(1,length(x))) return(TRUE)
  if (is.numeric(x) && isTRUE(1 == length(x))) return(TRUE)
  FALSE
  }

is.distr <- function(x) isTRUE(identical(attributes(class(x))$package,'distr'))

# whether it can be involved in a convolution
is.uncnum <- is.number <- function(x) is.numeric(x) || is.scalar(x) || is.interval(x) || is.pbox(x) || is.distr(x)

# whether it has epistemic or aleatory uncertainty
is.uncertain <- function(x) is.interval(x) || is.pbox(x) || is.distr(x)

is.vacuous <- function(s,...) {UseMethod("is.vacuous")};         is.vacuous.default    <- function(s) return(all(is.nan(s)) || all(is.na(s)))
is.vacuous.pbox     <- function(s) all(s@u==-Inf) && all(s@d==Inf)
is.vacuous.interval <- function(s) all(s@lo==-Inf) && all(s@hi==Inf)
#is.vacuous.numeric  use default method

##########################################################################
# Functions to manage dependence and autoselection of convolution method #
##########################################################################

perfectdep <- function(x) x@bob

oppositedep <- function(x) -x@bob

perfectopposite <- function(m, x) if (m<0) oppositedep(x) else perfectdep(x)

# don't think this will work to modify the arguments in place;  is assign any better?
# probably have to return entire pbox

depends <- function(x,y) {          
  if (indep(x,y)) return(0)
  if (perfect(x,y)) return(1)
  if (opposite(x,y)) return(-1)
#  if (positive(x,y)) return(interval(0,1))
#  if (negative(x,y)) return(interval(-1,0))
  return(interval(-1,1))
  }

indep <- function(x,y,quiet=TRUE) {
  s <- strsplit(dids.pbox(x),' ')
  t <- strsplit(dids.pbox(y),' ')
  if (!quiet) cat('Checking dependence between |',toString(s),'| and |',toString(t),'|\n',sep='')
  p = (!any(s[[1]] %in% t[[1]])) & (!any(t[[1]] %in% s[[1]]))   # not really sure why the [['s are needed
  return(p & !perfect(x,y) & !opposite(x,y))
  }

perfect <- function(x,y) {
  return (x@bob == y@bob) 
  }

opposite <- function(x,y) {
  return (x@bob == -y@bob) 
  }

autoselect <- function(x,y,op='+') 
  if (indep(x,y)) conv.pbox(x,y,op) else
  if (perfect(x,y)) perfectconv.pbox(x,y,op) else
  if (opposite(x,y)) oppositeconv.pbox(x,y,op) else 
  frechetconv.pbox(x,y,op)



#############################################################
# Rowe bounding for means and variances                     #
#############################################################

pow <- function(b,e) return(b^e)  ################################# temporary

RoweLinear <- function(mu,m,M,t) return(env(t(mu), t(m)+(t(M)-t(m))*(mu-m)/(M-m)))   # mu isn't repeated

Rowebit <- function(mu,m,M,v,t) {
  if (nothing(v) || nothing(mu-m) || nothing(M-mu)) return(t(mu)) # return the transformed interval mean if there'd be a division by zero
  pm = 1/(1+pow(mu-m,2)/v)
  pM = 1/(1+pow(M-mu,2)/v)
  #return env.interval(  pm*t(m)+(1-pm)*t(mu+(v/(mu-m))),   pM*t(M)+(1-pM)*t(mu-(v/(M-mu)))    ))  # can M-mu be zero?
  return(env.interval(  pm*t(m)+(1-pm)*t(mu+(v/(mu-m))),   pM*t(M)+(1-pM)*t(mu+(v/(M-mu)))    ))  # can M-mu be zero?
  }

Rowe <- function(mu,m,M,v,t)
  return(env.interval(env.interval(env.interval(Rowebit(left(mu),m,M,left(v),t),Rowebit(left(mu),m,M,right(v),t)),Rowebit(right(mu),m,M,left(v),t)),Rowebit(right(mu),m,M,right(v),t)))

RoweOrder <- function(u,d,t) 
  return(env.interval(cumsum(t(u)/length(u)), cumsum(t(d)/length(d))))

Rowe52 <- function(nu,mu,variance,m,M,t) 
  return(env.interval(sqrt(variance+pow(left(nu)-mu,2))*(t(left(nu))-t(m))/(left(nu)-m), sqrt(variance+pow(right(nu)-mu,2))*(t(right(nu))-t(M))/(right(nu)-M)))

Rowemean <- function(x, t, nu, mymean) {
  mymean = imp( mymean, RoweLinear(mean(x),left(x),right(x),t) )
  imp( mymean, RoweOrder(x@u,x@d,t) )
  }

Rowevar <- function(x, t, nu, mymean) {
  if (nothing(left(nu)-left(x)) || nothing(right(nu)-right(x)))
    myvar = interval(0.0, pow(right(mymean) - left(mymean),2)/4) else
      myvar = pow(Rowe52(nu, mean(x), var(x), left(x), right(x),t),2)
  pmax(interval(0.0),myvar)
  }


#############################################################
# Mathematical transformations and operations for p-boxes   #
#############################################################

transformedMean <- function(B, t, posderiv, pos2ndderiv) {

	
	if (is.null(pos2ndderiv)) {

		return(transformedMeanNull2ndDeriv(B, t, posderiv) )
	}	else if (pos2ndderiv) {

		return(transformedMeanPos2ndDeriv(B, t, posderiv) )
    
	} else {

		newT <- function(x) (-1) * t(x)
		tempResult = transformedMeanPos2ndDeriv(B, newT, !posderiv)
		
		if (!is.null(tempResult)) {
			transformedMean_lower = (-1) * (tempResult@hi)
			transformedMean_upper = (-1) * (tempResult@lo)
			return (interval(transformedMean_lower, transformedMean_upper))
		} else {
			return (NULL)
		} 		
	}
}

transformedMeanNull2ndDeriv <- function(B, t, posderiv) { 

	transformedMean_lower = NULL
	transformedMean_upper = NULL

	transformedSum = 0     
	for (i in 1:(B@n)) {		
		transformedSum = transformedSum + t(B@u[[i]])      
	}

	if (posderiv) { 
		transformedMean_lower = transformedSum/(B@n)    
	} else {
		transformedMean_upper = transformedSum/(B@n)
	}

	transformedSum = 0      
	for (i in 1:(B@n)) {
		transformedSum = transformedSum + t(B@d[[i]])     
	}

	if (posderiv) { 
		transformedMean_upper = transformedSum/(B@n)    
	} else {
		transformedMean_lower = transformedSum/(B@n)
	}
	###############################

	return(interval(transformedMean_lower,transformedMean_upper))   
}

transformedMeanPos2ndDeriv <- function(B, t, posderiv) { 

	mu_lower = B@ml
	mu_upper = B@mh    

	sum = 0
	transformedSum = 0     
	for (i in 1:(B@n)) {
		sum = sum + B@u[[i]]
		transformedSum = transformedSum + t(B@u[[i]])      
	}
	computedMu_lower = sum/(B@n)
	if (posderiv) { 
		transformedMean_lower = transformedSum/(B@n)    
	} else {
		transformedMean_upper = transformedSum/(B@n)
	}
	
	sum = 0
	transformedSum = 0      
	for (i in 1:(B@n)) {
		sum = sum + B@d[[i]] 
		transformedSum = transformedSum + t(B@d[[i]])     
	}
	computedMu_upper = sum/(B@n)
	if (posderiv) { 
		transformedMean_upper = transformedSum/(B@n)    
	} else {
		transformedMean_lower = transformedSum/(B@n)
	}

	if (computedMu_lower > mu_upper || computedMu_upper < mu_lower) {
		return(NULL)
	} else if (computedMu_lower >= mu_lower && computedMu_upper <= mu_upper) {
		return(interval(transformedMean_lower,transformedMean_upper))
	} else {
           	
		if (posderiv) {
			if (computedMu_lower < mu_lower) {          
				transformedMean_lower = NULL
			}
			if (computedMu_upper > mu_upper) {          
				transformedMean_upper = NULL
			}
		} else {
			if (computedMu_lower < mu_lower) {          
				transformedMean_upper = NULL
			}
			if (computedMu_upper > mu_upper) {          
				transformedMean_lower = NULL
			}
		}
	}

	###############################
	if (is.null(transformedMean_lower)) {     

		if (posderiv) {  
			mu =  mu_lower;
		} else {
			mu =  mu_upper;
		} 

		endingPoints = getBoundEndingPoints(B) 
  
		sum = 0
		transformedSum = 0 
		for (i in 1:(B@n)) {
			sum = sum + B@u[[i]]
			transformedSum = transformedSum + t(B@u[[i]])
		}
		num_middle = 0
    
		computedMu = sum/(B@n)
		if ( computedMu >= mu_lower && computedMu <= mu_upper) {
			transformedMean_lower = transformedSum/(B@n)             
		}

		for (i in 1:(2*(B@n))) {
    	
			if (endingPoints[2, i] < 0) {
				sum = sum - endingPoints[1, i]
				transformedSum = transformedSum - t(endingPoints[1, i])
				num_middle = num_middle + 1
			} else {
				sum = sum + endingPoints[1, i]
				transformedSum = transformedSum + t(endingPoints[1, i])
				num_middle = num_middle - 1
        		}


			if (num_middle == 0) {

				computedMu = sum/(B@n) 
				if ( computedMu >= mu_lower && computedMu <= mu_upper) {
					currentTransformedMean = transformedSum/(B@n)
             
					if(is.null(transformedMean_lower)) {
						transformedMean_lower = currentTransformedMean
                  		} else {
                       			transformedMean_lower = 
                         		min (transformedMean_lower, currentTransformedMean)
                  		}
             		}

        		} else {

             		value_middle = (mu * (B@n) - sum ) / num_middle
         
				if ( value_middle >= endingPoints[1, i] &&  value_middle <= endingPoints[1, i+1]) {
                  		currentTransformedMean = (transformedSum + 
                        		t(value_middle)*num_middle)/(B@n)
             
                  		if(is.null(transformedMean_lower)) {
                       			transformedMean_lower = currentTransformedMean
                  		} else {
                       			transformedMean_lower = 
                          			min (transformedMean_lower, currentTransformedMean)
                  		}           
       	     		}	
        		}	
     		}
	}

	###############################
    	if (is.null(transformedMean_upper)) {  

    		if (posderiv) {  
        		mu =  mu_upper;
    		} else {
        		mu =  mu_lower;
    		}

		sum = mu * (B@n)	 

    		sum_lower = 0
    		transformedSum_lower = 0 
    		for (i in 1:(B@n)) {
  	 		sum_lower = sum_lower + B@d[[i]]
         		transformedSum_lower = transformedSum_lower + t(B@d[[i]])
    		}
		
    		for (i in 1:(B@n)) {
			sum_upper = sum_lower
			transformedSum_upper = transformedSum_lower  
			sum_lower = sum_lower +  B@u[[i]] - B@d[[i]]
			transformedSum_lower = transformedSum_lower + t(B@u[[i]]) - t(B@d[[i]])

    	 		if ( sum >= sum_lower &&  sum <= sum_upper) {             
             		
				a = (sum_upper - sum) / (B@d[[i]] - B@u[[i]])

				currentTransformedMean = (transformedSum_upper - a * ( t(B@d[[i]]) - t(B@u[[i]]) ) )/(B@n)             

             		if(is.null(transformedMean_upper)) {
                      		transformedMean_upper = currentTransformedMean
             		} else {
                      		transformedMean_upper = 
                          		max (transformedMean_upper, currentTransformedMean)
             		} 
         		}
    		}
    	}
    	###############################

    	return(interval(transformedMean_lower,transformedMean_upper))   
}

transformedVariance <- function(B, t, posderiv, pos2ndderiv, transformedMean) {

	if(is.null(pos2ndderiv)) {
		
		return(transformedVarianceByIntervalComp(B, t, posderiv, transformedMean) )

	} else if (pos2ndderiv) {

		return(transformedVariancePos2ndDeriv(B, t, posderiv, transformedMean) )
    
	} else {

		newT <- function(x) (-1) * t(x)
		newTransformedMean = interval((-1) * (transformedMean@hi), (-1) * (transformedMean@lo) )

		return( transformedVariancePos2ndDeriv(B, newT, !posderiv, newTransformedMean) )		
	}
}

transformedVariancePos2ndDeriv <- function(B, t, posderiv, transformedMean) { 
	
	result1 = transformedVarianceByIntervalComp(B, t, posderiv, transformedMean)
	
      if (is.null(result1) ) {
		return(NULL)
	} else {

      	result2 = transformedVarianceByRowesPos2ndDeriv(B, t, posderiv, transformedMean)  

      	result_lower = max (result1@lo, result2@lo)
      	result_upper = min (result1@hi, result2@hi)

      	return(interval(result_lower, result_upper))
	}
}

transformedVarianceByRowesPos2ndDeriv <- function(B, t, posderiv, transformedMean) { 

  m = B@u[[1]]
  M = B@d[[B@n]]

  mu_lower = B@ml
  mu_upper = B@mh

  v_lower = B@vl
  v_upper = B@vh	
  
  transformedMean_lower = transformedMean@lo
  transformedMean_upper = transformedMean@hi
  
  eta_lower = (uniroot(function(x) t(x) - transformedMean_lower, 
             lower = m, upper = M, tol = 0.0001))$root

  eta_upper = (uniroot(function(x) t(x) - transformedMean_upper, 
             lower = m, upper = M, tol = 0.0001))$root


  if (posderiv){
  	transformedVariance_lower = (transformedMean_lower - t(m) )^2 / (eta_lower - m)^2 * 
                                   (v_lower + 
                                        (( getIntervalDistance(eta_lower, 
                                                             eta_lower,
                                                             mu_lower, mu_upper) )@lo )^2
                                   )
      transformedVariance_upper = (transformedMean_upper - t(M) )^2 / (eta_upper - M)^2 * 
                                   (v_upper + 
                                        (( getIntervalDistance(eta_upper, 
                                                             eta_upper,
                                                             mu_lower, mu_upper) )@hi )^2
                                   )
  } else {
      transformedVariance_lower = (transformedMean_upper - t(M) )^2 / (eta_upper - M)^2 * 
                                   (v_upper + 
                                        (( getIntervalDistance(eta_upper, 
                                                             eta_upper,
                                                             mu_lower, mu_upper) )@lo )^2
                                   )
      transformedVariance_upper = (transformedMean_lower - t(m) )^2 / (eta_lower - m)^2 * 
                                   (v_lower + 
                                        (( getIntervalDistance(eta_lower, 
                                                             eta_lower,
                                                             mu_lower, mu_upper) )@hi )^2
                                   )   
  }  	

  return(interval(transformedVariance_lower,transformedVariance_upper))
}

transformedVarianceByIntervalComp <- function(B, t, posderiv, transformedMean) {

  transformedMean_lower = transformedMean@lo
  transformedMean_upper = transformedMean@hi

  ###############################
  transformedSum = 0   
  for (j in 1:(B@n)) {
	transformedSum = transformedSum + t(B@u[[j]])     
  } 
  currentTransformedMean = transformedSum /(B@n)

  if (posderiv) {
  	if (currentTransformedMean > transformedMean_upper) {
		return (NULL)
	}
  } else {
  	if (currentTransformedMean < transformedMean_lower) {
		return (NULL)
	}
  }
  	
  transformedSum = 0   
  for (j in 1:(B@n)) {
	transformedSum = transformedSum + t(B@d[[j]])     
  } 
  currentTransformedMean = transformedSum /(B@n)

  if (posderiv) {
  	if (currentTransformedMean < transformedMean_lower) {
		return (NULL)
	}
  } else {
  	if (currentTransformedMean > transformedMean_upper) {
		return (NULL)
	}
  }

  ###############################

  transformedVariance_lower = transVarLowerByIntervalCompPos2ndDeriv(B, t, posderiv, transformedMean)
  transformedVariance_upper = transVarUpperByIntervalCompPos2ndDeriv(B, t, posderiv, transformedMean)

  if(is.null(transformedVariance_lower) || is.null(transformedVariance_upper)) {
  	return (NULL)
  } else {
  	return(interval(transformedVariance_lower,transformedVariance_upper))
  }
}

transVarUpperByIntervalCompPos2ndDeriv <- function(B, t, posderiv, transformedMean) {
  
  transformedMean_lower = transformedMean@lo
  transformedMean_upper = transformedMean@hi

  ###############################  
  
  transformedVariance_upper = NULL  
  
  transformedSum = 0 
  transformedSquareSum = 0 

  for (j in 1:(B@n)) {
	transformedSum = transformedSum + t(B@d[[j]])
      transformedSquareSum = transformedSquareSum + (t(B@d[[j]]) )^2
  }

  currentTransformedMean = transformedSum /(B@n)
  
  if (currentTransformedMean >= transformedMean_lower && currentTransformedMean <= transformedMean_upper) {

      currentTransformedVariance = transformedSquareSum/(B@n) - currentTransformedMean^2
      transformedVariance_upper = currentTransformedVariance
  } 

  for (i in 1:(B@n)) {             

	     transformedSum = transformedSum + t(B@u[[i]]) - t(B@d[[i]])
           transformedSquareSum = transformedSquareSum + (t(B@u[[i]]))^2 - (t(B@d[[i]]))^2
           currentTransformedMean = transformedSum /(B@n)


	     if (currentTransformedMean >= transformedMean_lower && currentTransformedMean <= transformedMean_upper) {

               currentTransformedVariance = transformedSquareSum/(B@n) - currentTransformedMean^2
               
		   if (is.null(transformedVariance_upper)) {
                   transformedVariance_upper = currentTransformedVariance                   
               } else {                
                   transformedVariance_upper = 
                          max (transformedVariance_upper, currentTransformedVariance)
               } 
           }
           else {

	            value_middle = (B@n) * transformedMean_lower - (transformedSum - t(B@u[[i]]) )
                  currentTransformedMean = (transformedSum - t(B@u[[i]]) +  value_middle)/(B@n) 
                  if ( (value_middle >= t(B@d[[i]]) && value_middle <= t(B@u[[i]]) && posderiv) || 
                       (value_middle >= t(B@u[[i]]) && value_middle <= t(B@d[[i]]) && !posderiv) ) {
              
                              currentTransformedVariance = (transformedSquareSum - t(B@u[[i]])^2 + value_middle^2)/(B@n) 
                                           - currentTransformedMean^2
               
		   			if (is.null(transformedVariance_upper)) {
                   			transformedVariance_upper = currentTransformedVariance                   
               			} else {                
                   			transformedVariance_upper = 
                          		max (transformedVariance_upper, currentTransformedVariance)
               			}   
                  } 

                  value_middle = (B@n) * transformedMean_upper - (transformedSum - t(B@u[[i]]) )
                  currentTransformedMean = (transformedSum - t(B@u[[i]]) +  value_middle)/(B@n) 
                  if ( (value_middle >= t(B@d[[i]]) && value_middle <= t(B@u[[i]]) && posderiv) || 
                       (value_middle >= t(B@u[[i]]) && value_middle <= t(B@d[[i]]) && !posderiv) ) {
              
                              currentTransformedVariance = (transformedSquareSum - t(B@u[[i]])^2 + value_middle^2)/(B@n) 
                                           - currentTransformedMean^2
               
		   			if (is.null(transformedVariance_upper)) {
                   			transformedVariance_upper = currentTransformedVariance                   
               			} else {                
                   			transformedVariance_upper = 
                          		max (transformedVariance_upper, currentTransformedVariance)
               			}   
                  }
           }       
  }
 
  ###############################  
  return(transformedVariance_upper)  
}

transVarLowerByIntervalCompPos2ndDeriv <- function(B, t, posderiv, transformedMean) {
  
  transformedMean_lower = transformedMean@lo
  transformedMean_upper = transformedMean@hi
 
  ###############################
  
  transformedVariance_lower = NULL
  
  endingPoints = getTransformedBoundEndingPoints(B, t, posderiv)  
  
  transformedSum = 0 
  transformedSquareSum = 0 
  
  if (posderiv) {
  	for (j in 1:(B@n)) {
		transformedSum = transformedSum + t(B@u[[j]])
      	transformedSquareSum = transformedSquareSum + (t(B@u[[j]]) )^2
  	}
  } else {
    	for (j in 1:(B@n)) {
		transformedSum = transformedSum + t(B@d[[j]])
      	transformedSquareSum = transformedSquareSum + (t(B@d[[j]]) )^2
  	}
  }

  currentTransformedMean = transformedSum /(B@n)
  
  if (currentTransformedMean >= transformedMean_lower && currentTransformedMean <= transformedMean_upper) {

      currentTransformedVariance = transformedSquareSum/(B@n) - currentTransformedMean^2
      transformedVariance_lower = currentTransformedVariance
  }

  num_middle = 0

  for (i in 1: (2*(B@n) -1)){           
             if (endingPoints[2, i] < 0) {
                 transformedSum = transformedSum - endingPoints[1, i]
                 transformedSquareSum = transformedSquareSum - (endingPoints[1, i])^2
                 num_middle = num_middle + 1 
             } else {
                 transformedSum = transformedSum + endingPoints[1, i]
                 transformedSquareSum = transformedSquareSum + (endingPoints[1, i])^2
                 num_middle = num_middle - 1 
             }
             
             currentTransformedMean_lower = (transformedSum + num_middle * endingPoints[1, i])/(B@n)
             currentTransformedMean_upper = (transformedSum + num_middle * endingPoints[1, i+1])/(B@n)  
             

		 if (currentTransformedMean_upper >= transformedMean_lower && currentTransformedMean_lower <= transformedMean_upper) {

                  currentTransformedMean_lower = max (currentTransformedMean_lower, transformedMean_lower)
                  currentTransformedMean_upper = min (currentTransformedMean_upper, transformedMean_upper)
                  
                  cuurentTransformedMean = transformedSum / (B@n - num_middle)

               	if (currentTransformedMean >= currentTransformedMean_lower && currentTransformedMean <= currentTransformedMean_upper) { 
                            
                            value_middle = currentTransformedMean
                            currentTransformedVariance = (transformedSquareSum + num_middle * value_middle^2)/(B@n) - currentTransformedMean^2
               
		   			if (is.null(transformedVariance_lower)) {
                   			transformedVariance_lower = currentTransformedVariance                   
               			} else {                
                   			transformedVariance_lower = 
                          		min (transformedVariance_lower, currentTransformedVariance)
               			}
                  }  else {
                  
                            value_middle = (currentTransformedMean_lower * (B@n) - transformedSum) / num_middle
                            currentTransformedVariance = (transformedSquareSum + num_middle * value_middle^2)/(B@n) - currentTransformedMean_lower^2
                            value_middle = (currentTransformedMean_upper * (B@n) - transformedSum) / num_middle
                            currentTransformedVariance = min (currentTransformedVariance, 
                                                         (transformedSquareSum + num_middle * value_middle^2)/(B@n) - currentTransformedMean_upper^2
                                                          ) 

		   			if (is.null(transformedVariance_lower)) {
                   			transformedVariance_lower = currentTransformedVariance                   
               			} else {                
                   			transformedVariance_lower = 
                          		min (transformedVariance_lower, currentTransformedVariance)
               			}                 
                  }   
		 }
  }

  transformedSum = transformedSum + endingPoints[2*(B@n)]
  transformedSquareSum = transformedSquareSum + ( endingPoints[2*(B@n)] )^2

  currentTransformedMean = transformedSum /(B@n)
  
  if (currentTransformedMean >= transformedMean_lower && currentTransformedMean <= transformedMean_upper){
  		
				currentTransformedVariance = transformedSquareSum/(B@n) - currentTransformedMean^2
             
		   		if (is.null(transformedVariance_lower)) {
                   		transformedVariance_lower = currentTransformedVariance                   
               		} else {                
                   		transformedVariance_lower = 
                        	min (transformedVariance_lower, currentTransformedVariance)
               		}  
  }  

  ###############################
  return(transformedVariance_lower)
}

getBoundEndingPoints <- function(B) {

  	endingPoints = c();   
  	i_u = 1
  	i_d = 1
  	for (i in 1:(2*(B@n))) {	
		if (i_u > B@n) {

            	endingPoints =c(endingPoints, c(B@d[[i_d]]) )
            	endingPoints =c(endingPoints, 1 )
            	i_d = i_d +1		
      
      	} else if (B@u[[i_u]] < B@d[[i_d]]) {

	    		endingPoints =c(endingPoints, c(B@u[[i_u]]) )
            	endingPoints =c(endingPoints, -1 )
            	i_u = i_u +1
      
      	} else {
 
            	endingPoints =c(endingPoints, c(B@d[[i_d]]) )
            	endingPoints =c(endingPoints, 1 )
            	i_d = i_d +1      
      	}	
   	}

   	dim(endingPoints) <- c(2, (2*(B@n)))

   	return(endingPoints)
}

getTransformedBoundEndingPoints <- function(B, t, posderiv) {

  	endingPoints = c();   
  	i_u = 1
  	i_d = 1
  	for (i in 1:(2*(B@n))) {	
		if (i_u > B@n) {

            	endingPoints =c(endingPoints, c( t(B@d[[i_d]])) )
            	endingPoints =c(endingPoints, 1 )
            	i_d = i_d +1		
      
      	} else if (B@u[[i_u]] < B@d[[i_d]]) {

	    		endingPoints =c(endingPoints, c( t(B@u[[i_u]])) )
            	endingPoints =c(endingPoints, -1 )
            	i_u = i_u +1
      
      	} else {
 
            	endingPoints =c(endingPoints, c( t(B@d[[i_d]])) )
            	endingPoints =c(endingPoints, 1 )
            	i_d = i_d +1      
      	}	
   	}

	dim(endingPoints) <- c(2, (2*(B@n)))

	if (!posderiv) {
		newEndingPoints = c();
		for (i in 1:(2*(B@n))) {
			newEndingPoints =c(newEndingPoints, endingPoints[1, ( (2*(B@n)) + 1 - i ) ] )
			newEndingPoints =c(newEndingPoints, -1 * endingPoints[2, ( (2*(B@n)) + 1 - i ) ] )			
		}  
   		dim(newEndingPoints) <- c(2, (2*(B@n)))
   		return(newEndingPoints)

	} else {
   		
   		return(endingPoints)
	}
}

compareInterval <- function(lower1, upper1, lower2, upper2) {
   
   	result = 0
   	if(upper1 <= lower2){
      	result = -1
   	} else if (lower1 >= upper2) {
      	result = 1
   	} else {
      	result = 0
   	}
   
   	return (result)  
}

getIntervalDistance <- function(lower1, upper1, lower2, upper2) {

   	dis_lower = 0
   	dis_upper = 0

   	if(upper1 <= lower2){
      	dis_lower = lower2 - upper1
      	dis_upper = upper2 - lower1
   	} else if (lower1 >= upper2) {
      	dis_lower = lower1 - upper2
      	dis_upper = upper1 - lower2
   	} else {
      	dis_lower = 0
      	dis_upper = max (abs(lower1 - upper2), abs(lower2 - upper1))
   	}
   
   	return (interval(dis_lower, dis_upper))
}

testPd <- function(f, B) {
 
    n = 100
 
    lower_x = left(B)
    upper_x =  right(B) 
    x = c(lower_x)
 
    for (i in 1:n) { 
           middle_x = lower_x + (upper_x -lower_x) * i /100
           x=c(x, c(middle_x) )
    }
 
    pd = (f(x) - f(x+0.01) < 0)
 
    if (all(pd))  {
        return (TRUE)
    } else if (all(!pd)) {
        return (FALSE)
    } else {
        return (NULL)
    }
}

testP2d <- function(f, B) { 
    
    n = 100
 
    lower_x = left(B)    
    upper_x = right(B) 
    x = c(lower_x)
     
    for (i in 1:n) { 
        middle_x = lower_x + (upper_x -lower_x) * i /100
        x=c(x, c(middle_x) )
    }
  
    p2d = (f(x) + f(x+0.02) > 2*f(x+0.01))     
 
    if (all(p2d)) {
        return (TRUE)
    } else if (all(!p2d)) {
        return (FALSE)
    } else {
        return (NULL)
    }
}

exp.pbox <- function(x) {
  if (x@shape %in% c('uniform','normal','triangular')) sh <- paste('log',x@shape,sep='') else 
  if (x@shape %in% c('{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else
  #if (x@shape %in% 'Gumbel') sh <- 'exponential' else 
  if (x@shape %in% 'exponential') sh <- 'Pareto' else sh <- ''
  t = exp 
  mymean = transformedMean(x, t, TRUE, TRUE)
  #cat('Gang: ',sayint(mymean),'\n')
  #nu = log(mymean)
  #myvar = Rowevar(x, t, nu, mymean)
  myvar = transformedVariance(x, t, TRUE, TRUE, mymean)
  pbox(u=exp(x@u), d=exp(x@d), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x)) 
  }

log.pbox <- function(x, expo=exp(1)) {  # expo must be scalar
  if (x@shape %in% c('loguniform','lognormal','logtriangular')) sh <- substr(x@shape,4,255) else 
  if (x@shape %in% c('{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else
  if ((x@shape %in% 'Pareto') && (left(x)==1)) sh <- 'exponential' else 
  if (x@shape %in% 'exponential') sh <- 'Gumbel' else sh <- ''
  t = function(x) return(log(x,expo))

#	if(left(x) <= 0) {
#		return(NULL)
#	}
	
  mymean = transformedMean(x, t, TRUE, FALSE)
  #nu = interval(expo^left(mymean), expo^right(mymean))
  #myvar = Rowevar(x, t, nu, mymean)
  myvar = transformedVariance(x, t, TRUE, FALSE, mymean)
  if (expo == exp(1)) pbox(u=log(x@u), d=log(x@d), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x)) else 
  	pbox(u=log(x@u,expo), d=log(x@d,expo), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x)) 
  	
  }

reciprocate.pbox <- function(x) {
  if (x@shape %in% c('Cauchy','{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else
  if (x@shape %in% 'Pareto') sh <- 'power function' else 
  if (x@shape %in% 'power function') sh <- 'Pareto' else sh <- ''
  t = reciprocate; 

  	if(left(x) <= 0 && right(x) >= 0) {
		return(NULL)
	} else if (left(x) > 0){
  		mymean = transformedMean(x, t, FALSE, TRUE)
		myvar = transformedVariance(x, t, FALSE, TRUE, mymean)
	} else { 
            # the case that right(x) < 0
		mymean = transformedMean(x, t, FALSE, FALSE)
		myvar = transformedVariance(x, t, FALSE, FALSE, mymean)
	}
  		
  #nu = reciprocate(mymean)
  #myvar = Rowevar(x, t, nu, mymean)
  pbox(u=1/rev(x@d), d=1/rev(x@u), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=oppositedep(x)) 		 
 }

sqrt.pbox <- function(x) {
  if (x@shape %in% c('{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else sh <- ''
  t = sqrt;
  	
	if (left(x) < 0) {
		return(NULL)  
	}

  mymean = transformedMean(x, t, TRUE, FALSE)
  #nu = pow(mymean,2)
  #myvar = Rowevar(x, t, nu, mymean)
  myvar = transformedVariance(x, t, TRUE, FALSE, mymean)

  pbox(u=sqrt(x@u), d=sqrt(x@d), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x)) 
  }

square.pbox <- function(x) {
  #if (left(x) < 0) stop('Cannot currently apply square function to negative values')
  if (x@shape %in% c('{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else sh <- ''
  t = function(x) return(pow(x,2))

	if (left(x) >= 0) {
        	mymean = transformedMean(x, t, TRUE, TRUE)
		myvar = transformedVariance(x, t, TRUE, TRUE, mymean)
  		pbox(u=sort(pow(x@u,2)), d=sort(pow(x@d,2)), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x))

      } else if (right(x) <= 0) {		
		mymean = transformedMean(x, t, FALSE, TRUE)
		myvar = transformedVariance(x, t, FALSE, TRUE, mymean)
   		pbox(u=sort(pow(x@d,2)), d=sort(pow(x@u,2)), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x))
      } else {
		return(NULL) # !!! A proper way to handle transform mean and variance need to be figure out  
	}

  #nu = sqrt(mymean)  
  #myvar = Rowevar(x, t, nu, mymean)
  #pbox(u=sort(pow(x@u,2)), d=sort(pow(x@d,2)), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x))
  }

asin.pbox <- function(x) {  # BUT SEE # restore functions BELOW
  if (x@shape %in% c('{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else sh <- ''
  t = asin
  
  	if ( left(x) < -1 || right(x) > 1) {
		return(NULL)
	} else if (right(x) <= 0){	
		mymean = transformedMean(x, t, TRUE, FALSE)
            myvar = transformedVariance(x, t, TRUE, FALSE, mymean)
	} else if (left(x) >=0 ) {
		mymean = transformedMean(x, t, TRUE, TRUE)
            myvar = transformedVariance(x, t, TRUE, TRUE, mymean)
	} else {
		mymean = transformedMean(x, t, TRUE, NULL)
            myvar = transformedVariance(x, t, TRUE, NULL, mymean)
	}

  #nu = sin(mymean)
  #myvar = Rowevar(x, t, nu, mymean)
  pbox(u=asin(x@u), d=asin(x@d), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x)) 
  }

acos.pbox <- function(x) {  # BUT SEE # restore functions BELOW
  if (x@shape %in% c('{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else sh <- ''
  t = acos

  	if ( left(x) < -1 || right(x) > 1) {
		return(NULL)
	} else if (right(x) <= 0){	
		mymean = transformedMean(x, t, FALSE, TRUE)
            myvar = transformedVariance(x, t, FALSE, TRUE, mymean)
	} else if (left(x) >=0 ) {
		mymean = transformedMean(x, t, FALSE, FALSE)
            myvar = transformedVariance(x, t, FALSE, FALSE, mymean)
	} else {
		mymean = transformedMean(x, t, FALSE, NULL)
            myvar = transformedVariance(x, t, FALSE, NULL, mymean)
	}
  #nu = cos(mymean)
  #myvar = Rowevar(x, t, nu, mymean)
  pbox(u=acos(rev(x@d)), d=acos(rev(x@u)), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=oppositedep(x)) 
  }

atan.pbox <- function(x) {  # BUT SEE # restore functions BELOW
  if (x@shape %in% c('{min, max, median}','{min, max, percentile}','{min, max}')) sh <- x@shape else sh <- ''
  t = atan
	if (right(x) <= 0){	
		mymean = transformedMean(x, t, TRUE, TRUE)
            myvar = transformedVariance(x, t, TRUE, TRUE, mymean)
	} else if (left(x) >=0 ) {
		mymean = transformedMean(x, t, TRUE, FALSE)
            myvar = transformedVariance(x, t, TRUE, FALSE, mymean)
	} else {
		mymean = transformedMean(x, t, TRUE, NULL)
            myvar = transformedVariance(x, t, TRUE, NULL, mymean)
	}
  #nu = tan(mymean) 
  #myvar = Rowevar(x, t, nu, mymean)
  pbox(u=atan(x@u), d=atan(x@d), shape=sh, name='', ml=left(mymean), mh=right(mymean), vl=left(myvar), vh=right(myvar), dids=dids(x), bob=perfectdep(x)) 
  }

`-.pbox` <- negate.pbox <- function(x) {
  if (x@shape %in% c('uniform','normal','cauchy','triangular','skew-normal')) s <- x@shape else s <- ''
  pbox(u=-rev(x@d), d=-rev(x@u), shape=s, name='', ml=-x@mh, mh=-x@ml, vl=x@vl, vh=x@vh, dids=dids(x), bob=oppositedep(x)) 
  }

complement.pbox <- function(x) {
  x <- pbox(x)   # omit this line when intervals are degenerate pbox objects
  if (x@shape %in% c('uniform','normal','cauchy','triangular')) s <- x@shape else s <- ''
  pbox(u=1-rev(x@d), d=1-rev(x@u), shape=s, name='', ml=1-x@mh, mh=1-x@ml, vl=x@vl, vh=x@vh, dids=dids(x), bob=oppositedep(x)) 
  }

mult <- mult.pbox <- function(m, x) {
  multipliable <- (x@shape %in% c('uniform','normal','cauchy','triangular','skew-normal'))
  scalable <- (x@shape %in% c('exponential','lognormal'))
  if (multipliable || (scalable & (0 <= x@u[[1]]))) s <- x@shape else s <- ''
  if (m < 0) negate(mult(abs(m),x)) else 
  pbox(u=m*x@u, d=m*x@d, shape=s, name='', ml=m*x@ml, mh=m*x@mh, vl=(m^2)*x@vl, vh=(m^2)*x@vh, dids=dids(x), bob=perfectopposite(m,x))   ################## mean if m<0
  }

shift.pbox <- function(ss,x) {
  if (x@shape %in% c('uniform','normal','cauchy','triangular','skew-normal')) s <- x@shape else s <- ''
  pbox(u=ss+x@u, d=ss+x@d, shape=s, name='', ml=x@ml+ss, mh=x@mh+ss, vl=x@vl, vh=x@vh, dids=dids(x), bob=perfectdep(x)) 
  }

int.pbox <- trunc.pbox <- function(x) pbox(u=trunc(x@u), d=trunc(x@d), dids=dids(x), bob=perfectdep(x)) 
round.pbox <- function(x,...) pbox(u=round(x@u,...), d=round(x@d,...), dids=dids(x), bob=perfectdep(x)) 
ceiling.pbox <- function(x) pbox(u=ceiling(x@u), d=ceiling(x@d), dids=dids(x), bob=perfectdep(x)) 

truncate.pbox <- function(x,min,max) {
  pbox(u=pmin(max, pmax(min,x@u)), d=pmin(max, pmax(min,x@d)), ml=min, mh=max, dids=dids(x), bob=perfectdep(x)) 
  }

square <- function(...,na.rm=FALSE){UseMethod("square")}

square.numeric <- function(x) return(x^2)

# restore functions ##################################################  temporary

asin.pbox <- function(x) {
  s <- ''  #  if (x@shape=='') s <- '' else s <- ''
  pbox(u=asin(x@u), d=asin(x@d), shape=s, name='', ml=0, mh=Inf, vl=0, vh=Inf, dids=dids(x), bob=perfectdep(x)) 
  }

acos.pbox <- function(x) {
  s <- ''  #  if (x@shape=='') s <- '' else s <- ''
  pbox(u=acos(rev(x@d)), d=acos(rev(x@u)), shape=s, name='', ml=0, mh=Inf, vl=0, vh=Inf, dids=dids(x), bob=oppositedep(x)) 
  }

atan.pbox <- function(x) {
  s <- ''  #  if (x@shape=='') s <- '' else s <- ''
  pbox(u=atan(x@u), d=atan(x@d), shape=s, name='', ml=0, mh=Inf, vl=0, vh=Inf, dids=dids(x), bob=perfectdep(x)) 
  }


samedistribution <- samedistribution.pbox <- function(x,name='',dids=NULL) {
  p=x
  unique <- uniquepbox()
  p@bob=as.integer(unique)
  p@id <- paste('PB',unique,sep='')
  p@name <- name
  p@dids=paste(p@id, dids)
  p}

imp <- imp.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)                       
  u <- elts[[1]]@u
  d <- elts[[1]]@d
  ml <- elts[[1]]@ml
  mh <- elts[[1]]@mh
  vl <- elts[[1]]@vl
  vh <- elts[[1]]@vh
  dids <- elts[[1]]@dids
  for (each in elts[-1]) {
    u <- pmax(u,each@u,na.rm=na.rm)
    d <- pmin(d,each@d,na.rm=na.rm)    
    ml <- myvectormax(ml,each@ml,na.rm=na.rm)
    mh <- myvectormin(mh,each@mh,na.rm=na.rm)
    vl <- myvectormax(vl,each@vl,na.rm=na.rm)
    vh <- myvectormin(vh,each@vh,na.rm=na.rm)
    dids <- paste(dids,each@dids) 
    }
  # check whether they cross
  if (any(d < u)) stop('Imposition does not exist') else pbox(u=u, d=d, ml=ml, mh=mh, vl=vl, vh=vh, dids=dids)
  }

env <- env.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)
  u <- elts[[1]]@u
  d <- elts[[1]]@d
  ml <- elts[[1]]@ml
  mh <- elts[[1]]@mh
  vl <- elts[[1]]@vl
  vh <- elts[[1]]@vh
  dids <- elts[[1]]@dids
  na <- elts[[1]]@name
  sh <- elts[[1]]@shape
  for (each in elts[-1]) {
    u <- pmin(u,each@u,na.rm=na.rm)
    d <- pmax(d,each@d,na.rm=na.rm)    
    ml <- myvectormin(ml,each@ml,na.rm=na.rm)
    mh <- myvectormax(mh,each@mh,na.rm=na.rm)
    vl <- myvectormin(vl,each@vl,na.rm=na.rm)
    vh <- myvectormax(vh,each@vh,na.rm=na.rm)
    dids <- paste(dids,each@dids) 
    if (each@name != na) na = ''    
    if (each@shape != sh) sh = ''    
    }
  pbox(u=u, d=d, ml=ml, mh=mh, vl=vl, vh=vh, dids=dids, name=na, shape=sh)
  }

# pmin, pmax, pminI, pmaxI are convolutions, corresponding to min, max, minI, maxI in Risk Calc

pmin.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)
  m <- elts[[1]]
  for (each in elts[-1]) m <- frechetconv.pbox(m, each, 'pmin')
  m
  }

pmax.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)
  m <- elts[[1]]
  for (each in elts[-1]) m <- frechetconv.pbox(m, each, 'pmax')
  m
  }

pminI.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)
  m <- elts[[1]]
  for (each in elts[-1]) m <- conv.pbox(m, each, 'pmin')
  m
  }

pmaxI.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)
  m <- elts[[1]]
  for (each in elts[-1]) m <- conv.pbox(m, each, 'pmax')
  m
  }

# smin and smax are not convolutions but rather distribution-level manipulations like mixture; they have no analogs in Risk Calc (but can be computed there as perfect min or max convolutions)

smin <- smin.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)
  u <- elts[[1]]@u
  d <- elts[[1]]@d
  ml <- elts[[1]]@ml
  mh <- elts[[1]]@mh
  vl <- elts[[1]]@vl
  vh <- elts[[1]]@vh
  dids <- elts[[1]]@dids
  for (each in elts[-1]) {
    u <- pmin(u,each@u,na.rm=na.rm)
    d <- pmin(d,each@d,na.rm=na.rm)    
    ml <- myvectormin(ml,each@ml,na.rm=na.rm)
    mh <- myvectormin(mh,each@mh,na.rm=na.rm)
    vl <- myvectormin(vl,each@vl,na.rm=na.rm)
    vh <- myvectormin(vh,each@vh,na.rm=na.rm)
    dids <- paste(dids,each@dids) 
    }
  pbox(u=u, d=d, ml=ml, mh=mh, vl=vl, vh=vh, dids=dids)
  }

smax <- smax.pbox <- function (..., na.rm = FALSE) {  
  elts <- makepbox(...)
  u <- elts[[1]]@u
  d <- elts[[1]]@d
  ml <- elts[[1]]@ml
  mh <- elts[[1]]@mh
  vl <- elts[[1]]@vl
  vh <- elts[[1]]@vh
  dids <- elts[[1]]@dids
  for (each in elts[-1]) {
    u <- pmax(u,each@u,na.rm=na.rm)
    d <- pmax(d,each@d,na.rm=na.rm)    
    ml <- myvectormax(ml,each@ml,na.rm=na.rm)
    mh <- myvectormax(mh,each@mh,na.rm=na.rm)
    vl <- myvectormax(vl,each@vl,na.rm=na.rm)
    vh <- myvectormax(vh,each@vh,na.rm=na.rm)
    dids <- paste(dids,each@dids) 
    }
  pbox(u=u, d=d, ml=ml, mh=mh, vl=vl, vh=vh, dids=dids)
  }


###################################
# Mixture functions 
###################################

mix.equal.numeric <- function(x,y=NULL) { #argument is one or two arrays of scalars
  n <- length(x)
  sx <- sort.list(x)
  u <- x[sx[1+0:(Pbox$steps-1)/((Pbox$steps)/n)]]
  d <- x[sx[1+1:Pbox$steps/((Pbox$steps)/(n))]]; d <- c(head(d,n=-1),max(x))
  if (isTRUE(all.equal(0, Pbox$steps %% n))) d <- u
#  if (missing(y)) pbox(u,d,shape='mixture') else setShape(env(pbox(u,d), mix.equal.numeric(y)),shape='mixture')
  if (missing(y)) pbox(u,d,shape='mixture') else env(pbox(u,d), mix.equal.numeric(y))
  }

left.list <- function(x) {
  bunch <- NULL
  for (i in 1:length(x)) bunch <- c(bunch,left(x[[i]]))
  bunch
  }

right.list <- function(x) {
  bunch <- NULL
  for (i in 1:length(x)) bunch <- c(bunch,right(x[[i]]))
  bunch
  }

#argument is a list of intervals
#mix.equal.interval <- function(x) setShape(env(mix.equal.numeric(left(x)), mix.equal.numeric(right(x))),shape='mixture')
mix.equal.interval <- function(x) env(mix.equal.numeric(left(x)), mix.equal.numeric(right(x)))

# mix.equal.pbox <- function(x, ...) {
#   k <- length(x)
#   y <- NULL
#   for (i in 1:k) y <- c(y,x[[i]]@u)
#   y = sort(y)
#   m = 1:Pbox$steps
#   u = y[(m-1)*k + 1]
#   y <- NULL
#   for (i in 1:k) y <- c(y,x[[i]]@d)
#   y = sort(y)
#   m = 1:Pbox$steps
#   d = y[(m-1)*k + k]
#   pbox(u,d)
#   }

mix.equal.pbox <- function(x, ...) return(mix.pbox(x))

mix.equal.list <- function(x) { 
  if (!all(unlist(lapply(x,is.uncnum)))) stop('Arguments to mixture must be (a list of) scalars, intervals, probability distributions or p-boxes')
  k = length(x)
  A = rep(list(pbox(0)),k)
  for (i in 1:k) A[[i]] = pbox(x[[i]])
  mix.equal.pbox(A)
  }  

mix.equal <- function(x, ...) {
  el <- list(...)
  k = length(el)
  A = rep(list(pbox(0)),k+1)
  A[[1]] = pbox(x)
  for (i in 1:k) A[[1+i]] = pbox(el[[i]])
  mix.equal.pbox(A)
  }

mix.equal <- function(...) {
  el <- list(...)
  k = length(el)
  A = rep(list(pbox(0)),k)
  for (i in 1:k) A[[i]] = pbox(el[[i]])
  mix.equal.pbox(A)
  }

mixture.pbox <- function(x, w=rep(1,length(x)), ...) {
  k <- length(x)
  if (k != length(w)) stop('Need same number of weights as arguments to mixture')
  w = w / sum(w)
  u <- d <- n <- ml <- mh <- m <- vl <- vh <- v <- NULL
  for (i in 1:k) {
    u <- c(u,x[[i]]@u)
    d <- c(d,x[[i]]@d)
    n <- c(n,w[[i]]*rep(1/steps(x[[i]]),steps(x[[i]])))
    mu <- mean(x[[i]])
    ml <- c(ml, left(mu))
    mh <- c(mh, right(mu))
    m <- c(m,mu)
    sigma2 <- var(x[[i]])
    vl <- c(vl, left(sigma2))
    vh <- c(vh, right(sigma2))
    v <- c(v,sigma2)
    }
  n = n / sum(n)
  su = sort(u); su = c(su[[1]],su)
  pu = c(0,cumsum(n[order(u)]))
  sd = sort(d); sd = c(sd,sd[[length(sd)]])
  pd = c(cumsum(n[order(d)]),1)
  u = d = NULL
  j = length(pu)
  for (p in rev(ii())) {
    repeat {if (pu[[j]] <= p) break; j = j - 1}
    u = c(su[[j]],u)
    }
  j = 1
  for (p in jj()) {
    repeat {if (p <= pd[[j]]) break; j = j + 1}
    d = c(d,sd[[j]])
    }
  #lines(su,pu,col='blue',type='S')  
  #lines(sd,pd,col='blue',type='s')  
  mu = interval(sum(w*ml), sum(w*mh))
  s2 = 0
  for (i in 1:k) s2  = s2 + w[[i]] * (v[[i]] + pow(m[[i]],2))
  s2 = s2 - pow(mu,2);
  pbox(u,d, ml=left(mu), mh=right(mu), vl=left(s2), vh=right(s2))
  }

mixture.list <- function(x, w=rep(1,length(x))) { 
  if (!all(unlist(lapply(x,is.uncnum)))) stop('Arguments to mixture.list must be (a list of) scalars, intervals, probability distributions or p-boxes')
  k = length(x)
  A = rep(list(pbox(0)),k)
  for (i in 1:k) A[[i]] = pbox(x[[i]])
  mixture.pbox(A, w=w)
  }  

mixture <- function(..., w=NULL) {
  # if one arg, it is probably a list or array, and w should be a vector of 1's of the same length
  # if just two args they may be either two mixturands to be evenly mixed, or one array of mixturands and one array of weights
  el <- list(...)
  k = length(el) 
  A = rep(list(pbox(0)),k)
  for (i in 1:k) A[[i]] = pbox(el[[i]])
  if (missing(w)) w = rep(1,k)
  mixture.pbox(A, w=w)
  }

mixtureexamples <- function() {
  everysafe = Pbox$plotting.every 
  Pbox$plotting.every <- FALSE
  old.par <- par(mfrow=c(2,3))
  a = mixture(interval(1,2), U(3,4), N(5,1), 3, 5);  plot(a)
  a = mixture(5, interval(1,2), U(3,4), N(5,1), 3);  plot(a)
  a = mixture(U(3,4), interval(1,2), N(5,1), 3, 5);  plot(a)
  #a = mixture(pbox(1,2), U(3,4), N(5,1), 3, 5);  plot(a)
  a = mixture.list(list(interval(1,2), U(3,4), N(5,1), 3, 5));  plot(a)
  # last example simulation confirms rigor (but also reveals apparent puffiness on the u-side)
  topsafe = Pbox$tOp
  botsafe = Pbox$bOt
  stepssafe = Pbox$steps
  Pbox$tOp <- 0.995
  Pbox$bOt <- 0.005
  ru = 1; rv = 2; rm = 5; rs = 1
  Pbox$steps <- 100
  a = mixture.list(list(uniform(ru,rv),normal(rm,rs)));  plot(a)
  #write(a,'c:/jerry.prn')
  many = 10000
  ra = rnorm(many,rm,rs)
  ra = ra[qnorm(Pbox$bOt,rm,rs) <= ra]
  ra = ra[ra <= qnorm(Pbox$tOp,rm,rs)]
  ra = c(ra, runif(many,ru,rv))
  edf(ra)
  Pbox$steps <- 10
  a = mixture.list(list(uniform(ru,rv),normal(rm,rs)));  plot(a)
  #write(a,'c:/jerry.prn')
  edf(ra)
  lines(a)
  par(old.par)
  Pbox$plotting.every <- everysafe
  Pbox$tOp <- topsafe
  Pbox$bOt <- botsafe
  Pbox$steps <- stepssafe
  }
#mixtureexamples()


##########################################
# Histogram functions
##########################################

# Make an (approximate) p-box from a large random sample
pbox.samples <- function(values) return(mix.equal.numeric(values))     # approximate, not rigorous

fatten <- function(a, dm=0, leftbound=left(a), rightbound=right(a)) {
  A = a
  A@u = c(rep(leftbound,sum(ii()>=(1-dm))),a@u[ii()<(1-dm)])
  A@d = c(a@d[jj()>(dm)],rep(rightbound,sum(jj()<=dm)))
  A@ml = mean(A@u)
  A@mh = mean(A@d)
  v = dwVariance(A)
  A@vl = left(v)
  A@vh = right(v)
  if (Pbox$plotting.every) try(plot.pbox(A))
  return(A)
  }

KSDmax = function(n, conf=0.95) {  
  # Miller, L.H. 1956 Table of percentage points of Kolmogorov statistics. JASA 51: 111-121.
  MillerD = function(n, alpha, A) return(sqrt(log(1.0 / alpha) / (2*n)) - 0.16693 / n - A * (n ^ -1.5)) # Miller's alpha is half of (1 - confidence level); the first term is equal to Smirnov(n, alpha)
  ks80 = c(1.0, 0.90000, 0.68377, 0.56481, 0.49265, 0.44698, 0.41037, 0.38148, 0.35831, 0.33910, 0.32260, 0.30829, 0.29577, 0.28470, 0.27481, 0.26588, 0.25778, 0.25039, 0.24360, 0.23735, 0.23156)
  ks90 = c(1.0, 0.95000, 0.77639, 0.63604, 0.56522, 0.50945, 0.46799, 0.43607, 0.40962, 0.38746, 0.36866, 0.35242, 0.33815, 0.32549, 0.31417, 0.30397, 0.29472, 0.28627, 0.27851, 0.27136, 0.26473)
  ks95 = c(1.0, 0.97500, 0.84189, 0.70760, 0.62394, 0.56328, 0.51926, 0.48342, 0.45427, 0.43001, 0.40925, 0.39122, 0.37543, 0.36143, 0.34890, 0.33760, 0.32733, 0.31796, 0.30936, 0.30143, 0.29408)
  ks98 = c(1.0, 0.99000, 0.90000, 0.78456, 0.68887, 0.62718, 0.57741, 0.53844, 0.50654, 0.47960, 0.45662, 0.43670, 0.41918, 0.40362, 0.38970, 0.37713, 0.36571, 0.35528, 0.34569, 0.33685, 0.32866)
  ks99 = c(1.0, 0.99500, 0.92929, 0.82900, 0.73424, 0.66853, 0.61661, 0.57581, 0.54179, 0.51332, 0.48893, 0.46770, 0.44905, 0.43247, 0.41762, 0.40420, 0.39201, 0.38086, 0.37062, 0.36117, 0.35241)
  if (conf==0) ksD = 0 else
  if (conf==0.80) 
                        if (n > 20) ksD = MillerD(n, 0.10, 0.00256) else  
                        ksD = ks80[n] else
  if (conf==0.90)
                        if (n > 20) ksD = MillerD(n, 0.05, 0.0526) else  
                        ksD = ks90[n] else
  if (conf==0.98) 
                        if (n > 20) ksD = MillerD(n, 0.01, 0.20562) else  
                        ksD = ks98[n] else 
  if (conf==0.99) 
                        if (n > 20) ksD = MillerD(n, 0.005, 0.28464) else  
                        ksD = ks99[n] else 
  #if (conf==0.95)                
                        if (n > 20) ksD = MillerD(n, 0.025, 0.11282) else  
            ksD = ks95[n] 
  return(ksD)
  }

histogram = function(x,y=NULL,mn=min(c(x,y)),mx=max(c(x,y)),conf=0.95) { #sample values are in an array x of scalars, or if they're intervals, in two arrays x,y
  n <- length(x)
  sx <- sort.list(x)
  u <- x[sx[1+0:(Pbox$steps-1)/((Pbox$steps)/n)]]
  d <- x[sx[1+1:Pbox$steps/((Pbox$steps)/(n))]]; d <- c(head(d,n=-1),max(x))
  if (isTRUE(all.equal(0, Pbox$steps %% n))) d <- u
  fatten(if (missing(y)) pbox(u,d,shape='histogram') else env(pbox(u,d), histogram(y)), KSDmax(n,conf),leftbound=mn,rightbound=mx)
  }


###########################
# Joint probability curve #
###########################

# essentially, a convolutive form of "greater than"
 
jpc.pbox <- function(x,y,name='') {
  n <- length(x@d)
  Zu <- Zd <- rep(1,n)
  for (i in 1:n) {
    Zu[[i]] <- left(prob.pbox(y,x@u[[i]]))  #@lo #[[1]]
    Zd[[i]] <- right(prob.pbox(y,x@d[[i]]))  #@hi #[[2]]
    }
  pbox(Zu,Zd,name=name,dids=paste(x@dids,y@dids))
  }

#jpc.pbox <- function(x,y,name='') frechetconv.pbox(x,y,'>')


################################
# Mass reassignments functions #
################################

lowest <- function(x, p) {   # exclude all but the lowest p% of x, useful for Will Powley's rejection rescaling
  if (!is.pbox(x)) stop('The argument to the lowest truncation must be a p-box')
  i <- round(seq(from=1,to=Pbox$steps*(p/100),length.out=Pbox$steps))
  zu <- unlist(x@u)[i]
  zd <- unlist(x@d)[i]
  pbox(u = zu, d = zd)
  }

highest <- function(x, p) {   # exclude all but the highest p% of x, useful for Will Powley's rejection rescaling
  if (!is.pbox(x)) stop('The argument to the highest truncation must be a p-box')
  i <- round(seq(from=1,to=Pbox$steps*(p/100),length.out=Pbox$steps))
  zu <- rev(rev(unlist(x@u))[i])
  zd <- rev(rev(unlist(x@d))[i])
  pbox(u = zu, d = zd)
  }

below <- function(x, s) {   # exclude all values from x but those below s
  if (!is.pbox(x)) stop('The argument to the below truncation must be a p-box')
  p <- right(prob.pbox(x, s))
  i <- round(seq(from=1,to=Pbox$steps*p,length.out=Pbox$steps))
  zu <- pmin(s,unlist(x@u)[i])
  zd <- pmin(s,unlist(x@d)[i])
  pbox(u = zu, d = zd)
  }

above <- function(x, s){   # exclude all values from x but those above s
  if (!is.pbox(x)) stop('The argument to the above truncation must be a p-box')
  p <- 1-left(prob.pbox(x, s))
  i <- round(seq(from=1,to=Pbox$steps*p,length.out=Pbox$steps))
  zu <- pmax(s,rev(rev(unlist(x@u))[i]))
  zd <- pmax(s,rev(rev(unlist(x@d))[i]))
  pbox(u = zu, d = zd)
  }

between <- function(x, m, M) below(above(x, m), M)   # exclude all values from x except those between m and M

rescale <- function(x, m, M)  m + (M-m) * (x - left(x))/ width.interval(range(x))  # linearly rescale x to the specified range [m,M]

censor <- function(x, m, M) {   # remove detail from x between m and M
  zu = x@u
  zu[(m < zu) & (zu < M)] = m
  zd = x@d
  zd[(m < zd) & (zd < M)] = M
  pbox(zu,zd)
  }


#####################################
# Replicate and sequence operations #
#####################################

rep.pbox <- function(x, ...) {
  r = NULL
  for (i in 1:list(...)[[1]]) r = c(r,x)
  return(r) 
  }

seq.pbox <- function(from = NULL, to = NULL,             # by = ((to - from)/(length.out - 1)),
    length.out = NULL, along.with = NULL, ...) {
  if (missing(from)) from <- pbox(1)
  if (missing(to)) to <- pbox(1)
  u1 <- from@u
  d1 <- from@d
  u2 <- pbox(to)@u   
  d2 <- pbox(to)@d
  if (!missing(along.with)) 
    m <- length(along.with)-1 else 
      if (!missing(length.out)) 
        m <- ceiling(length.out)-1 else 
          m <- ceiling(left(to) - left(from))
  bunch <- NULL
  for (i in 0:m) {
    uu <- u1 + i * ((u2-u1)/m)
    dd <- d1 + i * ((d2-d1)/m)
    bunch <- c(bunch, pbox(uu,dd))
    }
  bunch
  }


###########################
# Convolutions operations #
###########################

conv.pbox <- FLEXconv.pbox <- function(x,y,op='+') {
    if (op=='-') return(FLEXconv.pbox(x,negate.pbox(y),'+'))
    if (op=='/') return(FLEXconv.pbox(x,reciprocate.pbox(y),'*'))
    x <- makepbox(x)
    y <- makepbox(y)
    m <- x@n
    p <- y@n
    n <- min(Pbox$steps,m*p)
    L <- m * p / n
    c <- rep(0,m*p)
    Zu <- rep(1,n)
    Zd <- rep(1,n)
    k <- 1:n
#    for (i in 1:m) for (j in 1:p) c[[(i-1)*p+j]] <- x@d[[i]] + y@d[[j]]
#    cc <- sort(c)
    Y <- rep(y@d, rep.int(m,p))
    c <- sort(do.call(op,list(x@d,Y)))         
    Zd <- c[(k-1)*L + L] + 0
#    for (i in 1:m) for (j in 1:p) c[[(i-1)*p+j]] <- x@u[[i]] + y@u[[j]]
#    c <- sort(c)
    Y <- rep(y@u, rep.int(m,p))
    c <- sort(do.call(op,list(x@u,Y)))         
    Zu <- c[(k-1)*L + 1] + 0
    # mean
    ml <- -Inf
    mh <- Inf
    if (op %in% c('+','-','*')) {
      ml <- do.call(op, list(x@ml, y@ml))
      mh <- do.call(op, list(x@mh, y@mh))
      }
    # variance
    vl <- 0
    vh <- Inf
    if (op %in% c('+','-')) {
      vl <- x@vl + y@vl
      vh <- x@vh + y@vh
      }
    pbox(u = Zu, d = Zd, ml = ml, mh = mh, vl=vl, vh=vh, dids=paste(x@dids,y@dids))
    }

perfectconv.pbox <- function(a,b,op='+') {  # prolly doesn't work for ^ in interesting cases
  if (op %in% c('-', '/')) {
    cu = do.call(op, list(a@u, b@d))
    cd = do.call(op, list(a@d, b@u))
    } else {
    cu = do.call(op, list(a@u, b@u))
    cd = do.call(op, list(a@d, b@d))
    }
  scu = sort(cu + 0)
  scd = sort(cd + 0)
  if (all(cu == scu) && all(cd == scd)) pbox(u=scu, d=scd,  dids=paste(a@dids,b@dids), bob=a@bob) else pbox(u=scu, d=scd,  dids=paste(a@dids,b@dids)) 
  }

oppositeconv.pbox <- function(a,b,op='+') {  # prolly doesn't work for ^ in interesting cases
  if (op %in% c('-', '/')) {
    cu = do.call(op, list(a@u, rev(b@d)))
    cd = do.call(op, list(a@d, rev(b@u)))
    } else {
    cu = do.call(op, list(a@u, rev(b@u)))
    cd = do.call(op, list(a@d, rev(b@d)))
    }
  cu = sort(cu + 0)
  cd = sort(cd + 0)
  pbox(u=cu, d=cd,  dids=paste(a@dids,b@dids)) # neither bob nor not-bob
  }

straddles <- function(x) return((left(x)<=0) && (0<=right(x)))   # includes zero
straddlingzero <- function(x) return((left(x)<0) && (0<right(x)))   # neglects zero as an endpoint

frechetconv.pbox <- frechetconv.pbox <- function(x,y,op='+') {
  if (op=='-') return(frechetconv.pbox(x,negate.pbox(y),'+'))
  if (op=='/') return(frechetconv.pbox(x,reciprocate.pbox(y),'*'))
  if (op=='*') if (straddlingzero(x) | straddlingzero(y)) return(imp(balchprod(x,y),naivefrechetconv.pbox(x,y,'*')))
  x <- makepbox(x)
  y <- makepbox(y)
  zu <- zd <- rep(0,Pbox$steps)
  for (i in 1:Pbox$steps)
        {
          j <- i:Pbox$steps
          k <- Pbox$steps:i
          zd[[i]]  <- min(do.call(op,list(x@d[j],y@d[k])))  #zd[[i]] <- min(x@d[j] + y@d[k])
          j <- 1:i
          k <- i:1
          zu[[i]]  <- max(do.call(op,list(x@u[j],y@u[k])))  #zu[[i]] <- max(x@u[j] + y@u[k])
        }
  # mean
  ml <- -Inf
  mh <- Inf
  if (op %in% c('+','-')) {
    ml <- do.call(op, list(x@ml, y@ml))
    mh <- do.call(op, list(x@mh, y@mh))
    }
  # variance
  vl <- 0
  vh <- Inf
  if (op %in% c('+','-')) {
    #zv = env(xv+yv-2* sqrt(xv*yv), xv+yv+2* sqrt(xv*yv))
    # vh <- x@v+y@v - 2*sqrt(x@v*y@v)
    # vl <- x@v+y@v + 2*sqrt(x@v*y@v)
    }
  pbox(u=zu + 0, d=zd + 0, ml = ml, mh = mh, vl=vl, vh=vh, dids=paste(x@dids,y@dids))
  }

# THE FOLLOWING VLADIK MOMENT ROUTINES SUPPORT NAIVEFRECHETCONV.PBOX

#///////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////
#// Vladik's mean formulations
#//  
#// Ferson, S. L. Ginzburg, V. Kreinovich and J. Lopex. 2002. Absolute bounds on the mean of sum, 
#// product, max, and min: a probabilistic extension of interval arithmetic.
#//
#// Vladik:  On page 19, I don't understand the nature of the two kinds of conditions:  1 contained in
#// the sum p1+p2 (which I call pa+pb), and p1 (pa) overlapping p2 (pb).  Are the implementations ok?
#// Also, I believe that the minuends in the denominators of p_i at the top of page 19 should be 
#// right(x_i) rather than right(E_i). On page 21, what is the function $\underbar{f}^u_{min}(p_1,p_2)$ ?
#///////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////

VKmeanlo = function(p,q,k1,k2,k3,k4)      # double p, double q, double k1, double k2, double k3, double k4)
  return(max(p + q - 1, 0.0) * k1 + min(p, 1 - q) * k2 + min(1 - p, q) * k3 + max(1 - p - q, 0.0) * k4)

VKmeanup = function(p,q,k1,k2,k3,k4)      # double p, double q, double k1, double k2, double k3, double k4)
  return(min(p, q) * k1 + max(p - q, 0.0) * k2 + max(q - p, 0.0) * k3 + min(1 - p, 1 - q) * k4)

touching = function(a, b)       # const Interval& a, const Interval& b )
{
    if (is.scalar(a) && is.scalar(b)) return(left(a) == left(b))
    if (straddles(a - b)) return(TRUE)          
    return(FALSE);
}

VKmeanlower = function(pa,pb,k1,k2,k3,k4)     # Interval pa, Interval pb, double k1, double k2, double k3, double k4)
{
  #double p1, p2, ec1;
  lpa = left(pa)
  rpa = right(pa)
  lpb = left(pb)
  rpb = right(pb)
  touch = touching(pa + pb, 1.0)
  p1 = lpa;               p2 = lpb;               ec1 =          VKmeanlo(p1,p2,k1,k2,k3,k4);
  p1 = lpa;               p2 = rpb;               ec1 = min(ec1, VKmeanlo(p1,p2,k1,k2,k3,k4));
  p1 = rpa;               p2 = lpb;               ec1 = min(ec1, VKmeanlo(p1,p2,k1,k2,k3,k4));
  p1 = rpa;               p2 = rpb;               ec1 = min(ec1, VKmeanlo(p1,p2,k1,k2,k3,k4));
  p1 = max(lpa, 1 - rpb); p2 = 1 - p1; if (touch) ec1 = min(ec1, VKmeanlo(p1,p2,k1,k2,k3,k4));
  p1 = min(rpa, 1 - lpb); p2 = 1 - p1; if (touch) ec1 = min(ec1, VKmeanlo(p1,p2,k1,k2,k3,k4));
  return(ec1)
}

VKmeanupper = function(pa,pb,k1,k2,k3,k4)      # Interval pa, Interval pb, double k1, double k2, double k3, double k4)
{
  #double p1, p2, ec2;
  lpa = left(pa)
  rpa = right(pa)
  lpb = left(pb)
  rpb = right(pb)
  touch = touching(pa,pb)
  p1 = lpa;               p2 = lpb;              ec2 =          VKmeanup(p1,p2,k1,k2,k3,k4);
  p1 = lpa;               p2 = rpb;              ec2 = max(ec2, VKmeanup(p1,p2,k1,k2,k3,k4));
  p1 = rpa;               p2 = lpb;              ec2 = max(ec2, VKmeanup(p1,p2,k1,k2,k3,k4));
  p1 = rpa;               p2 = rpb;              ec2 = max(ec2, VKmeanup(p1,p2,k1,k2,k3,k4));
  p1 = max(lpa, 1 - rpb); p2 = 1-p1;  if (touch) ec2 = max(ec2, VKmeanup(p1,p2,k1,k2,k3,k4));
  p1 = min(rpa, 1 - lpb); p2 = 1-p1;  if (touch) ec2 = max(ec2, VKmeanup(p1,p2,k1,k2,k3,k4));
  return(ec2)
}

VKmeanproduct = function(a, b) {
  # Interval ea,eb,ec,pa,pb;
  # double la,ra,lb,rb,k1,k2,k3,k4,ec1,ec2;
  ec = interval(-Inf,Inf)
  ea = mean(a)
  eb = mean(b)
  la = left(a)
  ra = right(a)
  lb = left(b)
  rb = right(b)
  k1 = ra * rb
  k2 = ra * lb
  k3 = la * rb
  k4 = la * lb
  pa = interval( (left(ea) - la) / (ra - la), (right(ea) - la) / (ra - la) )
  pb = interval( (left(eb) - lb) / (rb - lb), (right(eb) - lb) / (rb - lb) )
  ec = env(VKmeanlower(pa,pb,k1,k2,k3,k4), VKmeanupper(pa,pb,k1,k2,k3,k4))
  return(ec)
}

##################################################################################
#
# This (naive) Frechet convolution will work for multiplication of distributions 
# that straddle zero.  Note, however, that it is NOT optimal. It can probably be
# improved considerably.  It does use the Frechet moment propagation formulas.
# Unfortunately, moment propagation has not be implemented yet in the R library.
# To get OPTIMAL bounds for the envelope, we probably must use Berleant's linear 
# programming solution for this problem.
#
##################################################################################

naivefrechetconv.pbox <- naivefrechetconv.pbox <- function(x,y,op='*') {
  if (op=='+') return(frechetconv.pbox(x,y,'+'))
  if (op=='-') return(frechetconv.pbox(x,negate.pbox(y),'+'))
  if (op=='/') return(naivefrechetconv.pbox(x,reciprocate.pbox(y),'*'))
  x <- makepbox(x)
  y <- makepbox(y)
  n = length(x@d)
  Y <- rep(y@d, rep.int(n, n))
  c <- sort(do.call(op,list(x@d,Y)))        
  Zd <- c[(n*n-n+1):(n*n)]
  Y <- rep(y@u, rep.int(n, n))
  c <- sort(do.call(op,list(x@u,Y)))        
  Zu <- c[1:n]
  # mean
  m <- mean(x) * mean(y)
  a <- sqrt(var(x) * var(y))
  ml <- m - a  
  mh <- m + a
  VK = VKmeanproduct(x,y)
  m <- imp(interval(ml,mh), VK)
  # variance
  vl <- 0
  vh <- Inf
  pbox(u = Zu, d = Zd, ml = left(m), mh = right(m), vl=vl, vh=vh, dids=paste(x@dids,y@dids))
  }

balchprod <- function(x,y) {
  if (straddles(x) && straddles(y)) {
    x0 = left(x)
    y0 = left(y)
    xx0 = x - x0
    yy0 = y - y0
    a = frechetconv.pbox(xx0, yy0, '*') 
    b = frechetconv.pbox(y0*xx0, x0*yy0, '+')
    return(frechetconv.pbox(a,b,'+') + x0*y0)
    }
  if (straddles(x)) {
    x0 = left(x)
    xx0 = x - x0
    a = frechetconv.pbox(xx0, y, '*') 
    b = x0 * y
    return(frechetconv.pbox(a,b,'+'))
    }
  if (straddles(y)) {
    y0 = left(y)
    yy0 = y - y0
    a = frechetconv.pbox(x, yy0, '*') 
    b = x * y0
    return(frechetconv.pbox(a,b,'+'))
    }
  return(frechetconv.pbox(x,y,'*'))
  }

SLOWconv.pbox <- function(x,y) {
    x <- makepbox(x)
    y <- makepbox(y)
    n = length(x@d)
    c <- rep(0,n^2)
    Zu <- rep(1,n)
    Zd <- rep(1,n)
    for (i in 1:n) for (j in 1:n) c[[(i-1)*n+j]] <- x@d[[i]] + y@d[[j]]
    c <- sort(c)
    for (k in 1:n) Zd[[k]] <- c[[(k-1)*n + n]]  
    for (i in 1:n) for (j in 1:n) c[[(i-1)*n+j]] <- x@u[[i]] + y@u[[j]]
    c <- sort(c)
    for (k in 1:n) Zu[[k]] <- c[[(k-1)*n + 1]]  
    pbox(u = Zu, d = Zd)
    }

SLOWfrechetconv.pbox <- function(x,y) {
  x <- makepbox(x)
  y <- makepbox(y)
  zu <- zd <- rep(0,Pbox$steps)
  for (i in 1:Pbox$steps)
        {
          outlier <- Inf
          for (j in i:Pbox$steps)
          {
            #cat(j,i-j+Pbox$steps,' ')
            here <- x@d[[j]] + y@d[[i - j + Pbox$steps]]     
            if (here<outlier) outlier <- here
          }
          #cat('\n')
          zd[[i]] <- outlier

          outlier <- -Inf
          for (j in 1:i)
          {
            #cat(j,i-j+1,' ')
            here <- x@u[[j]] + y@u[[i - j + 1]]
            if (here>outlier) outlier <- here
          }
          #cat('\n')
          zu[[i]] <- outlier
        }
  pbox(u=zu, d=zd)
  }

SAME.n.conv.pbox <- function(x,y,op='+') {
  if (op=='-') return(conv.pbox(x,negate.pbox(y),'+'))
  if (op=='/') return(conv.pbox(x,reciprocate.pbox(y),'*'))
  x <- makepbox(x)
  y <- makepbox(y)
  n = length(x@d)
  Zu <- rep(1,n)
  Zd <- rep(1,n)
  Y <- rep(y@d, rep.int(n, n))
  c <- sort(do.call(op,list(x@d,Y)))          #c <- sort(x@d + Y)
  k <- 1:n
  Zd <- c[(k-1)*n + n]
  Y <- rep(y@u, rep.int(n, n))
  c <- sort(do.call(op,list(x@u,Y)))          #c <- sort(x@u + Y)
  Zu <- c[(k-1)*n + 1]  
  # mean
  ml <- -Inf
  mh <- Inf
  if (op %in% c('+','-','*')) {
    ml <- do.call(op, list(x@ml, y@ml))
    mh <- do.call(op, list(x@mh, y@mh))
    }
  # variance
  vl <- 0
  vh <- Inf
  if (op %in% c('+','-')) {
    vl <- x@vl + y@vl
    vh <- x@vh + y@vh
    }
  pbox(u = Zu, d = Zd, ml = ml, mh = mh, vl=vl, vh=vh, dids=paste(x@dids,y@dids))
  }

convOLD.pbox <- function(x,y,op='+') {
  if (op=='-') return(conv.pbox(x,negate.pbox(y),'+'))
  if (op=='/') return(conv.pbox(x,reciprocate.pbox(y),'*'))
  x <- makepbox(x)
  y <- makepbox(y)
  n = length(x@d)
  Zu <- rep(1,n)
  Zd <- rep(1,n)
  Y <- rep(y@d, rep.int(n, n))
  c <- sort(do.call(op,list(x@d,Y)))          #c <- sort(x@d + Y)
  for (k in 1:n) Zd[[k]] <- c[[(k-1)*n + n]] 
  Y <- rep(y@u, rep.int(n, n))
  c <- sort(do.call(op,list(x@u,Y)))          #c <- sort(x@u + Y)
  for (k in 1:n) Zu[[k]] <- c[[(k-1)*n + 1]]  
  # mean
  ml <- -Inf
  mh <- Inf
  if (op %in% c('+','-','*')) {
    ml <- do.call(op, list(x@ml, y@ml))
    mh <- do.call(op, list(x@mh, y@mh))
    }
  # variance
  vl <- 0
  vh <- Inf
  if (op %in% c('+','-')) {
    vl <- x@vl + y@vl
    vh <- x@vh + y@vh
    }
  pbox(u = Zu, d = Zd, ml = ml, mh = mh, vl=vl, vh=vh, dids=paste(x@dids,y@dids))
  }

#####################
# Logical functions #
#####################

are.logicals.pbox <- function(a,b) {
  a <- makepbox(a)
  b <- makepbox(b)
  # must be dimensionless too, but we cannot check that
  ((0 <= left(a)) && (right(a) <= 1) && (0 <= left(b)) && (right(b) <= 1))
  }

# complement.pbox (already defined) is logical negation

andI.pbox <- function(a,b) conv.pbox(a,b,'*');

orI.pbox <- function(a,b) complement.pbox(conv.pbox(complement.pbox(a), complement.pbox(b),'*'))

and.pbox <- function(a,b) env.pbox(pmax.pbox(shift.pbox(-1,frechetconv.pbox(a,b)),0),pmin.pbox(a,b))

or.pbox <- function(a,b) env.pbox(pmax.pbox(a,b),pmin.pbox(1,frechetconv.pbox(a,b)) )


####################
# In-fix Operators #
####################

#####################################################################################################################
#
# The operator %*% is reassigned to Frechet multiplication, which clobbers its use for matrix multiplication.
# The operator %/% is reassigned to Frechet division, which clobbers its use for integer division.
#
# We can distinguish the overlapping uses, but do not seem to be able to access the standard R functions. 
# Can someone suggest a fix to the following two lines that might allow both uses simultaneously?

"%*%" <- function(x,y) if (is.uncertain(x) || is.uncertain(y)) frechetconv.pbox(x,y,'*') else .Primitive("%*%")
"%/%" <- function(x,y) if (is.uncertain(x) || is.uncertain(y)) frechetconv.pbox(x,y,'/') else .Primitive("%/%")

#####################################################################################################################

"%+%" <- function(x,y) frechetconv.pbox(x,y,'+');                   "%-%" <- function(x,y) frechetconv.pbox(x,negate(y),'+')
"%x%" <- function(x,y) frechetconv.pbox(x,y,'*');                   "%div%" <- function(x,y) frechetconv.pbox(x,reciprocate(y),'*')
"%m%" <- function(x,y) frechetconv.pbox(x,y,'pmin');                "%M%" <- function(x,y) frechetconv.pbox(x,y,'pmax')
"%^%" <- function(x,y) exp.pbox(frechetconv.pbox(log.pbox(x),y,'*')) # what restrictions are there on the arguments?
"%<%" <- lt <- function(x,y) prob.pbox(frechetconv.pbox(x,negate(y),'+'),0);   "%>%" <- gt <- function(x,y) xprob.pbox(frechetconv.pbox(y,negate(x),'+'),0)
"%<=%" <- lte <- function(x,y) xprob.pbox(frechetconv.pbox(x,negate(y),'+'),0);   "%>=%" <- gte <- function(x,y) prob.pbox(frechetconv.pbox(y,negate(x),'+'),0)
"%&%" <- function(x,y) and.pbox(x,y);                               "%|%" <- function(x,y) or.pbox(x,y)
# %&% and %|% assume nothing about dependence at EITHER level

"%|+|%" <- function(x,y) conv.pbox(x,y,'+');                        "%|-|%" <- function(x,y) conv.pbox(x,negate.pbox(y),'+')
"%|*|%" <- "%|x|%" <- function(x,y) conv.pbox(x,y,'*');             "%|/|%" <- "%|div|%" <- function(x,y) conv.pbox(x,reciprocate.pbox(y),'*')
"%|m|%" <- function(x,y) conv.pbox(x,y,'pmin');                     "%|M|%" <- function(x,y) conv.pbox(x,y,'pmax')
"%|^|%" <- function(x,y) exp.pbox(conv.pbox(log.pbox(x),y,'*')) # what restrictions are there on the arguments?
"%|<|%" <- function(x,y) prob.pbox(conv.pbox(x,negate(y),'+'),0);   "%|>|%" <- function(x,y) xprob.pbox(conv.pbox(y,negate.pbox(x),'+'),0)
"%|<=|%" <- function(x,y) xprob.pbox(conv.pbox(x,negate(y),'+'),0);   "%|>=|%" <- function(x,y) prob.pbox(conv.pbox(y,negate.pbox(x),'+'),0)
"%|&|%" <- function(x,y) andI.pbox(x,y);                            "%|||%" <- function(x,y) orI.pbox(x,y)
# %|&|% and %|||% assume independence at BOTH levels

"%/+/%" <- function(x,y) perfectconv.pbox(x,y,'+');                 "%/-/%" <- function(x,y) perfectconv.pbox(x,y,'-')
"%/*/%" <- "%/x/%" <- function(x,y) perfectconv.pbox(x,y,'*');      "%///%" <- "%/div/%" <- function(x,y) perfectconv.pbox(x,y,'/')
"%/m/%" <- function(x,y) perfectconv.pbox(x,y,'pmin');              "%/M/%" <- function(x,y) perfectconv.pbox(x,y,'pmax')
"%/^/%" <- function(x,y) perfectexp.pbox(x,y,'^') # what restrictions are there on the arguments?
"%/</%" <- function(x,y) prob.pbox(oppositeconv.pbox(x,negate(y),'+'),0);   "%/>/%" <- function(x,y) xprob.pbox(oppositeconv.pbox(y,negate.pbox(x),'+'),0)
"%/<=/%" <- function(x,y) xprob.pbox(oppositeconv.pbox(x,negate(y),'+'),0);   "%/>=/%" <- function(x,y) prob.pbox(oppositeconv.pbox(y,negate.pbox(x),'+'),0)
# "%/&/%" <- function(x,y) perfectand.pbox(x,y);                     "%/|/%" <- function(x,y) perfector.pbox(x,y)
# what should %/&/% and %/|/% assume about dependence at the two levels?

# backslash creates an escape character, so we use o to denote opposite

"%o+o%" <- function(x,y) oppositeconv.pbox(x,y,'+');                "%o-o%" <- function(x,y) oppositeconv.pbox(x,y,'-')
"%o*o%" <- "%oxo%" <- function(x,y) oppositeconv.pbox(x,y,'*');     "%o/o%" <- "%odivo%" <- function(x,y) oppositeconv.pbox(x,y,'/')
"%omo%" <- function(x,y) oppositeconv.pbox(x,y,'pmin');             "%oMo%" <- function(x,y) oppositeconv.pbox(x,y,'pmax')
"%o^o%" <- function(x,y) oppositeconv.pbox(x,y,'^') # what restrictions are there on the arguments?
"%o<o%" <- function(x,y) prob.pbox(perfectconv.pbox(x,negate(y),'+'),0);   "%o>o%" <- function(x,y) xprob.pbox(perfectconv.pbox(y,negate.pbox(x),'+'),0)
"%o<=o%" <- function(x,y) xprob.pbox(perfectconv.pbox(x,negate(y),'+'),0);   "%o>=o%" <- function(x,y) prob.pbox(perfectconv.pbox(y,negate.pbox(x),'+'),0)
# "%o&o%" <- function(x,y) oppositeand.pbox(x,y);                     "%o|o%" <- function(x,y) oppositeor.pbox(x,y)
# what should %o&o% and %o|o% assume about dependence at the two levels?


# default addition (used by automatic dependency tracking)

quiet <- setMethod('+', c('pbox','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){ shift.pbox(e2, e1) })

quiet <- setMethod('+', c('numeric','pbox'),
  function(e1, e2){ shift.pbox(e1, e2) })

quiet <- setMethod('+', c('pbox','pbox'),function(e1,e2){
  return(  autoselect(e1,e2,'+')  )})   

quiet <- setMethod('+', c('pbox','interval'), 
  function(e1, e2){ e1 + pbox(e2) } )

quiet <- setMethod('+', c('interval','pbox'), 
  function(e1, e2){ pbox(e1) + e2 } )

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('+', c('pbox','Distribution'),function(e1,e2){
  return(  autoselect(e1,distr2pbox(e2),'+')  )})                     #not clear that autoselect = conv is the right behavior here

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('+', c('Distribution','pbox'),function(e1,e2){
  return(  autoselect(distr2pbox(e1),e2,'+')  )})                     #not clear that autoselect = conv is the right behavior here


# default multiplication

quiet <- setMethod('*', c('pbox','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){ mult.pbox(e2, e1) })

quiet <- setMethod('*', c('numeric','pbox'),
  function(e1, e2){ mult.pbox(e1, e2) })

quiet <- setMethod('*', c('pbox','pbox'),function(e1,e2){
  return(  autoselect(e1,e2,'*')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('*', c('pbox','Distribution'),function(e1,e2){
  return(  autoselect(e1,distr2pbox(e2),'*')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('*', c('Distribution','pbox'),function(e1,e2){
  return(  autoselect(distr2pbox(e1),e2,'*')  )})   


# default subtraction

quiet <- setMethod('-', c('pbox','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){pbox(u=e1@u - e2, d=e1@d - e2, ml=e1@ml - e2, mh=e1@mh - e2, vl=e1@vl, vh=e1@vh, bob=e1@bob) })

quiet <- setMethod('-', c('numeric','pbox'),
  function(e1, e2){ pbox(e1 + negate.pbox(e2), opposite=e2) })

quiet <- setMethod('-', c('pbox','pbox'),function(e1,e2){
  return(  autoselect(e1,negate.pbox(e2),'+')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('-', c('pbox','Distribution'),function(e1,e2){
  return(  autoselect(e1,negate.pbox(distr2pbox(e2)),'+')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('-', c('Distribution','pbox'),function(e1,e2){
  return(  autoselect(distr2pbox(e1),negate.pbox(e2),'+')  )})   


# default division

quiet <- setMethod('/', c('pbox','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){ mult.pbox(1/e2, e1) })

quiet <- setMethod('/', c('numeric','pbox'),
  function(e1, e2){ mult.pbox(e1, reciprocate.pbox(e2)) })

quiet <- setMethod('/', c('pbox','pbox'),function(e1,e2){
  return(  autoselect(e1,reciprocate.pbox(e2),'*')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('/', c('pbox','Distribution'),function(e1,e2){
  return(  autoselect(e1,reciprocate.pbox(distr2pbox(e2)),'*')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('/', c('Distribution','pbox'),function(e1,e2){
  return(  autoselect(distr2pbox(e1),reciprocate.pbox(e2),'*')  )})   


# default minimization

if(!isGeneric("Min")) quiet <- setGeneric("Min", function(e1, e2, ...) standardGeneric("Min"))

quiet <- setMethod('Min', c('pbox','numeric'),                    # what happens if e2 is a vector??
  function(e1, e2)  pbox(u=pmin(e1@u,e2), d=pmin(e1@d,e2), ml=min(e1@ml,e2), mh=min(e1@mh,e2))   )  

quiet <- setMethod('Min', c('numeric','pbox'),
  function(e1, e2){ Min(e2, e1)})

quiet <- setMethod('Min', c('pbox','pbox'),function(e1,e2){
  return(  autoselect(e1,e2,'pmin')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('Min', c('pbox','Distribution'),function(e1,e2){
  return(  autoselect(e1,distr2pbox(e2),'pmin')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('Min', c('Distribution','pbox'),function(e1,e2){
  return(  autoselect(distr2pbox(e1),e2,'pmin')  )})   


# default maximization

if(!isGeneric("Max")) quiet <- setGeneric("Max", function(e1, e2, ...) standardGeneric("Max"))

quiet <- setMethod('Max', c('pbox','numeric'),                    # what happens if e2 is a vector??
  function(e1, e2)  pbox(u=pmax(e1@u,e2), d=pmax(e1@d,e2), ml=max(e1@ml,e2), mh=max(e1@mh,e2))   )  

quiet <- setMethod('Max', c('numeric','pbox'),
  function(e1, e2){ Max(e2, e1)})

quiet <- setMethod('Max', c('pbox','pbox'),function(e1,e2){
  return(  autoselect(e1,e2,'pmax')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('Max', c('pbox','Distribution'),function(e1,e2){
  return(  autoselect(e1,distr2pbox(e2),'pmax')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('Max', c('Distribution','pbox'),function(e1,e2){
  return(  autoselect(distr2pbox(e1),e2,'pmax')  )})   


# default raising to a power

quiet <- setMethod('^', c('pbox','numeric'),   # what happens if e2 is a vector??
  function(e1, e2){pbox(u=e1@u ^ e2, d=e1@d ^ e2) })    # what about moments??   #, ml=e1@ml + e2, mh=e1@mh + e2, vl=e1@vl, vh=e1@vh) 

quiet <- setMethod('^', c('numeric','pbox'),
  function(e1, e2){e2 ^ e1})

quiet <- setMethod('^', c('pbox','pbox'),function(e1,e2){
  return(  autoselect(e1,e2,'^')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('^', c('pbox','Distribution'),function(e1,e2){
  return(  autoselect(e1,distr2pbox(e2),'^')  )})   

if (distr.loaded)  # if distr package has been loaded
quiet <- setMethod('^', c('Distribution','pbox'),function(e1,e2){
  return(  autoselect(distr2pbox(e1),e2,'^')  )})   

ilt <- function(x,y) if (right(x) < left(y)) return(1) else if (right(y) < left(x)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(x)<left(y)) else return(interval(0,1))
igt <- function(x,y) if (right(y) < left(x)) return(1) else if (right(x) < left(y)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(y)<left(x)) else return(interval(0,1))
ilte <- function(x,y) if (right(x) <= left(y)) return(1) else if (right(y) < left(x)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(x)<=left(y)) else return(interval(0,1))
igte <- function(x,y) if (right(y) <= left(x)) return(1) else if (right(x) < left(y)) return(0) else if (is.scalar(x) && is.scalar(y)) return(left(y)<=left(x)) else return(interval(0,1))
quiet <- setMethod('<', c('interval','numeric'), function(e1, e2){ ilt(e1,e2) })    
quiet <- setMethod('<', c('numeric','interval'), function(e1, e2){ ilt(e1,e2) })
quiet <- setMethod('<', c('interval','interval'), function(e1, e2){ ilt(e1,e2) })
quiet <- setMethod('>', c('interval','numeric'),   function(e1, e2){ igt(e1,e2) }) 
quiet <- setMethod('>', c('numeric','interval'),  function(e1, e2){ igt(e1,e2) })
quiet <- setMethod('>', c('interval','interval'),  function(e1, e2){ igt(e1,e2) })
quiet <- setMethod('<=', c('interval','numeric'), function(e1, e2){ ilte(e1,e2) })   
quiet <- setMethod('<=', c('numeric','interval'), function(e1, e2){ ilte(e1,e2) })
quiet <- setMethod('<=', c('interval','interval'), function(e1, e2){ ilte(e1,e2) })
quiet <- setMethod('>=', c('interval','numeric'),   function(e1, e2){ igte(e1,e2) }) 
quiet <- setMethod('>=', c('numeric','interval'),  function(e1, e2){ igte(e1,e2) })
quiet <- setMethod('>=', c('interval','interval'),  function(e1, e2){ igte(e1,e2) })

# default less-than comparison (used by automatic dependency tracking)
quiet <- setMethod('<', c('pbox','numeric'), function(e1, e2){ lt(e1,e2) })     # what happens if e2 is a vector??
quiet <- setMethod('<', c('numeric','pbox'), function(e1, e2){ lt(e1,e2) })
quiet <- setMethod('<', c('pbox','interval'), function(e1, e2){ lt(e1,e2) })
quiet <- setMethod('<', c('interval','pbox'), function(e1, e2){ lt(e1,e2) })
quiet <- setMethod('<', c('pbox','pbox'), function(e1, e2){ prob.pbox(autoselect(e1,negate(e2),'+'),0) })
if (distr.loaded) quiet <- setMethod('<', c('pbox','Distribution'),function(e1,e2){  return( prob.pbox(autoselect(e1,negate(distr2pbox(e2)),'+'),0)) })    # if distr package has been loaded
if (distr.loaded) quiet <- setMethod('<', c('Distribution','pbox'),function(e1,e2){  return( prob.pbox(autoselect(distr2pbox(e1),negate(e2),'+'),0)) })    # if distr package has been loaded

# default greater-than comparison (used by automatic dependency tracking)
quiet <- setMethod('>', c('pbox','numeric'),   function(e1, e2){ gt(e1,e2) })   # what happens if e2 is a vector??
quiet <- setMethod('>', c('numeric','pbox'),  function(e1, e2){ gt(e1,e2) })
quiet <- setMethod('>', c('pbox','interval'),  function(e1, e2){ gt(e1,e2) })
quiet <- setMethod('>', c('interval','pbox'),  function(e1, e2){ gt(e1,e2) })
quiet <- setMethod('>', c('pbox','pbox'),  function(e1, e2){ xprob.pbox(autoselect(e2,negate(e1),'+'),0) })
if (distr.loaded)  quiet <- setMethod('>', c('pbox','Distribution'),function(e1,e2){  return( xprob.pbox(autoselect(distr2pbox(e2),negate(e1),'+'),0)) })   # if distr package has been loaded
if (distr.loaded)  quiet <- setMethod('>', c('Distribution','pbox'),function(e1,e2){  return( xprob.pbox(autoselect(e2,negate(distr2pbox(e1)),'+'),0)) })   # if distr package has been loaded

# default less-than-or-equal-to comparison (used by automatic dependency tracking)
quiet <- setMethod('<=', c('pbox','numeric'), function(e1, e2){ lte(e1,e2) })     # what happens if e2 is a vector??
quiet <- setMethod('<=', c('numeric','pbox'), function(e1, e2){ lte(e1,e2) })
quiet <- setMethod('<=', c('pbox','interval'), function(e1, e2){ lte(e1,e2) })
quiet <- setMethod('<=', c('interval','pbox'), function(e1, e2){ lte(e1,e2) })
quiet <- setMethod('<=', c('pbox','pbox'), function(e1, e2){ xprob.pbox(autoselect(e1,negate(e2),'+'),0) })
if (distr.loaded) quiet <- setMethod('<=', c('pbox','Distribution'),function(e1,e2){  return( xprob.pbox(autoselect(e1,negate(distr2pbox(e2)),'+'),0)) })    # if distr package has been loaded
if (distr.loaded) quiet <- setMethod('<=', c('Distribution','pbox'),function(e1,e2){  return( xprob.pbox(autoselect(distr2pbox(e1),negate(e2),'+'),0)) })    # if distr package has been loaded

# default greater-than-or-equal-to comparison (used by automatic dependency tracking)
quiet <- setMethod('>=', c('pbox','numeric'),   function(e1, e2){ gte(e1,e2) })   # what happens if e2 is a vector??
quiet <- setMethod('>=', c('numeric','pbox'),  function(e1, e2){ gte(e1,e2) })
quiet <- setMethod('>=', c('pbox','interval'),  function(e1, e2){ gte(e1,e2) })
quiet <- setMethod('>=', c('interval','pbox'),  function(e1, e2){ gte(e1,e2) })
quiet <- setMethod('>=', c('pbox','pbox'),  function(e1, e2){ prob.pbox(autoselect(e2,negate(e1),'+'),0) })
if (distr.loaded)  quiet <- setMethod('>=', c('pbox','Distribution'),function(e1,e2){  return( prob.pbox(autoselect(distr2pbox(e2),negate(e1),'+'),0)) })   # if distr package has been loaded
if (distr.loaded)  quiet <- setMethod('>=', c('Distribution','pbox'),function(e1,e2){  return( prob.pbox(autoselect(e2,negate(distr2pbox(e1)),'+'),0)) })   # if distr package has been loaded


# We don't support &, &&, |, || as infix operators for p-boxes because 
# we cannot be comprehensive in doing so.  The first problem is that && 
# and || (which would be the natural operators to use) are sealed and 
# can't be changed.  The second problem is that & and I cannot be applied
# when the left argument is an atomic numeric for similar reasons.  Finally,
# & and | won't work on vectors of p-boxes, or rather, we cannot invoke 
# them that way, because an array of p-boxes does not have the class pbox.
# Instead, we define the ugly infix operators %&%, %|&|%, %|%, %|||%, and 
# the functions and.pbox, andI.pbox, or.pbox, orI.pbox.


#######################################################################
# Some inverse probability distributions not already implemented in R #
#######################################################################

qarcsin <- function(p) return(1/2 - cos(p*base::pi) /2)

qarctan <- function(p, alpha, phi) return(phi + tan(-atan(alpha*phi) + p * atan(alpha*phi)+ p*base::pi/2) / alpha)

qbenford <- function(p) {
  l5 = log(5)
  l2 = log(2)
  l3 = log(3)
  q = rep(9,length(p))
  P = (p - 1) * (l2 + l5)
  #q = ifelse(P < 0, 9, q)
  q = ifelse(P < -l2-l5+2*l3, 8, q)
  q = ifelse(P < -l5+2*l2, 7, q)
  q = ifelse(P < -l2-l5+log(7), 6, q)
  q = ifelse(P < -l5+l3, 5, q)
  q = ifelse(P < -l2, 4, q)
  q = ifelse(P < l2-l5, 3, q)
  q = ifelse(P < -l2-l5+l3, 2, q)
  q = ifelse(P < -l5, 1, q)
  q
  }

qexponentialpower <- function(p, lambda, kappa) return(exp(-(log(lambda) - log(log(1-log(1-p)))) / kappa))

qfrechet <- function(p, b, c) b*exp((-1/c)*log(log(1/p)))               # Castillo, page 207

qgammaexponential <- function(p, shape, scale=1, rate=1/scale) rate * ((1-p)^(-1/shape) - 1)

qgev <- function(p,a,b,c) if (c==0) qgumbel(p,a,b) else a + b * (exp(-c*log(-log(p))) - 1) / c   # c must be a scalar

qgumbel <- function(p, a, b) a - b * log(log(1.0/p))                    # Evans et al., page 65

qhypoexponential <- function(p,lambda) return(-log(1-p)/lambda)

qlaplace <- function(p, a, b) ifelse(p<=0.5, a + b * log(2.0 * p),a - b * log(2.0 * (1.0 - p))) # Evans et al., page 92

qloglogistic <- function(p, lambda, kappa) return(exp(-(log(lambda) - log(-p/(p-1))/ kappa)))

qlogtriangular <- function(p, i_min, i_mode, i_max){
  a = log(i_min)
  b = log(i_mode)       ########## could this really be correct?
  c = log(i_max)
  exp(qtriangular(p, a, b, c))
  }

qloguniform <- function(p, one, two) {
  m = log(one)
  exp((log(two) - m) * p + m);
  }

qlomax <- function(p, lambda, kappa) return(((1-p)^(-1/kappa)-1)/lambda)

qmuth <- function(p, a) return(-(lambertW(-exp(log(1-p)-1/a)/a)*a+1-log(1-p)*a)/(a^2))

qreciprocal <- function(p, a=10.0) exp(p * log(a))

qpareto <- function(p, mode, c) mode * exp((-1.0/c) * log(1.0 - p))     # Evans et al., page 119

qpowerfunction <- function(p, b, c) b * exp((1.0/c) * log(p))           # Evans et al., page 128

qquadratic <- function(p,m,a){
  # June 2009 Draft NASA Report "Measurement Uncertainty Analysis: Principles and Methods". Appendix B, page 151
  unitqquad = function(P) {
    d = 4 * P - 2   
    h = d^2 / 4 + -1
    i = sqrt(d^2 / 4 - h)
    j = ifelse(i < 0, -(-i)^(1/3), i^(1/3))
    k = acos(-(d / (2 * i)))
    m = cos(k / 3);
    n = 1.73205080756888 * sin(k / 3);
    return(-j * (m - n))
    }
  return(unitqquad(p)*(a-m)+m)
  }

qrayleigh <- function(p, b) sqrt(-2.0 * b * b * log(1.0 - p))           # Evans et al., page 134

qshiftedloglogistic <- function(p, a,b,c) a + b * (exp(c*log(1/(1/p-1))) - 1) / c

qtrapezoidal <- function(p, a, b, c, d){
  if (nothing(d-a)) return(rep(a,length.out=length(p)))
  if (nothing(c-b)) return(qtriangular(p,a,b,d))
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

ququadratic <- function(p,a,b){
  # http://en.wikipedia.org/wiki/U-quadratic_distribution
  cuberoot <- function(z) return(ifelse(0<z,z^(1/3),-(abs(z)^(1/3))))
  alpha = 12 / (b-a)^3
  beta = (a + b) / 2
  return(beta + cuberoot(3*p / alpha - (beta - a)^3))   
  }

#############################
# Distribution constructors #
#############################

ii  <- function() c(         0, 1:(Pbox$steps-1) / Pbox$steps)
iii <- function() c(  Pbox$bOt, 1:(Pbox$steps-1) / Pbox$steps)
jj  <- function() c(            1:(Pbox$steps-1) / Pbox$steps, 1)
jjj <- function() c(            1:(Pbox$steps-1) / Pbox$steps, Pbox$tOp)

# Use the quantiles( ) constructor to bound all distributions 
# that have specified quantiles (or percentiles or fractiles).
# Or use pointlist( ) for connecting the dots for a distribution
# specified by quantiles.  See also the interpolation schemes 
# used in the generic constructor pbox( ).

qleftquantiles <- function(pp,x,p) {  # if first p is not zero, the left tail will be -Inf
  u = NULL
  for (P in pp) u = c(u,max(left.list(x)[right.list(p)<=P]))   # <?
  u
  }

qrightquantiles <- function(pp,x,p) {  # if last p is not one, the right tail will be Inf 
  d = NULL
  for (P in pp) d = c(d,min(right.list(x)[P<=left.list(p)]))
  d
  }

quantiles <- function(x,p) pbox(u=qleftquantiles(ii(),x,p), d=qrightquantiles(jj(),x,p))  # quantiles are in x and the associated cumulative probabilities are in p

quantilesexamples <- function() {
  do <- function(x,p) {
    q <- quantiles(x,p)
    plot(NULL,xlim=range(c(left(x),right(x))),ylim=c(0,1),xlab='',ylab='Cumulative probability')
    for (i in 1:length(x)) 
      if (is.scalar(x[[i]]) && is.scalar(p[[i]])) points(x[[i]],p[[i]], cex=1.5, col='gray',pch=19) else
        if (is.scalar(p[[i]])) lines(range.interval(x[[i]]),rep(p[[i]],2),lwd=7,col='gray') else
          if (is.scalar(x[[i]])) lines(rep(x[[i]],2),range.interval(p[[i]]),lwd=7,col='gray') else
            rect(left(x[[i]]),left(p[[i]]),right(x[[i]]),right(p[[i]]),border='gray',col='gray',lwd=0)
    lines(q)
    }
  save = Pbox$plotting.every 
  Pbox$plotting.every <- FALSE
  old.par <- par(mfrow=c(2,4)) #,mar=c(2,4,3,1))
  # basic example
  x = c(3, 6,   10,  16,  25,  40)
  p = c(0, 0.2, 0.4, 0.5, 0.7, 1)
  do(x,p)
  # p doesn't start at zero or end at one
  x = c(3,   6,   10,  16,  25,  40)
  p = c(0.1, 0.2, 0.4, 0.5, 0.7, 0.9)
  do(x,p)
  # x has intervals
  x = c(3, interval(4,7), 10, interval(12,18), 25, 40)
  p = c(0, 0.2, 0.4, 0.5, 0.7, 1)
  do(x,p)
  # x has overlapping intervals
  x = c(3, interval(4,7), interval(6,14), interval(12,18), 25, interval(30,40))
  p = c(0, 0.2, 0.4, 0.5, 0.7, 1)
  do(x,p)
  # x has intervals overlappling in a non-sortable way
  x = c(3, interval(4,20), interval(6,14), interval(5,18), 25, interval(20,40))
  p = c(0, 0.2, 0.4, 0.5, 0.7, 1)
  do(x,p) # this result is correct (although it looks strange) because the percentiles constrain each other
  # p has intervals
  x = c(3, 6, 10, 16, 25, 40)
  p = c(0, interval(0.1, 0.2), 0.4, interval(0.5,0.6), 0.7, 1)
  do(x,p)
  # p has intervals that can't be sorted
  x = c(3, 6,                      10,  16,                    25, 40)
  p = c(0, interval(0.1, 0.5), 0.4, interval(0.3,0.6), 0.7, 1)
  do(x,p) # this result is correct (although it looks strange) because the percentiles constrain each other
  # all complexities
  x = c(3, interval(4,20),     interval(6,14), interval(5,18),    25,  interval(20,40))
  p = c(0, interval(0.1, 0.5), 0.4,            interval(0.3,0.6), 0.7, 0.9)
  do(x,p)
  par(old.par)
  Pbox$plotting.every <- save
  }

#quantilesexamples()

pointlist <- function(V, P, name='') {  # connect the dots, quantiles are in V and the associated cumulative probabilities are in P
  if (length(V) != length(P)) stop('Inconsistent lengths')
  if ((min(P) < 0) || (1 < max(P))) stop('Improper probability') # ensure 0 <= p <= 1
  c <- NULL
  for (i in 1:(length(V)-1)) {
    v <- V[[i]]
    p <- P[[i]]
    w <- V[[i+1]]
    q <- P[[i+1]]
    many <- round((q - p) * Pbox$steps * 20)
    if (0 < many) c <- c(c, seq(from=v, to=w, length.out=many))
    }
  u <- d <- rep(0,Pbox$steps)
  # maybe I can parallelize the following lines
  for (k in 1:Pbox$steps) u[[k]] <-c[[1+round((length(c)-1)*(k-1)/(Pbox$steps-1))]]
  for (k in 1:Pbox$steps) d[[k]] <-c[[1+round((length(c)-1)*(k-1)/(Pbox$steps-1))]]
  pbox(u=u, d=d, shape='', name=name, ml=-Inf, mh=Inf, vl=0, vh=Inf)
  }

#Sbernoulli <- function(p, name='') {
#  some = trunc((1-p) * Pbox$steps)
#  rest = Pbox$steps - some
#  u <- c(rep(0,some),rep(1,rest))
#  d <- c(rep(0,some),rep(1,rest))
#  pbox(u=u, d=d, shape='bernoulli', name=name, ml=p, mh=p, vl=p*(1-p), vh=p*(1-p))
#  }

bernoulli = function(p, name='') {
  u <- ifelse(ii() < 1-left(p),0,1)  
  d <- ifelse(jj() < 1-right(p),0,1) 
  pbox(u=u, d=d, shape='bernoulli', name=name, ml=left(p), mh=right(p), vl=0.25-(right(p)-0.5)^2, vh=0.25-(left(p)-0.5)^2)
  }

#Sbeta <- function(shape1, shape2, name=''){
#  m <- shape1/(shape1+shape2)
#  v <- shape1*shape2/((shape1+shape2)^2*(shape1+shape2+1))
#  pbox(u=qbeta(ii(), shape1, shape2), d=qbeta(jj(), shape1, shape2), shape='beta', name=name, ml=m, mh=m, vl=v, vh=v)
#  }

Sbeta  <- function(shape1, shape2, name=''){
  if ((shape1==0) && (shape2==0)) return(pbox(0,1,shape='beta',name=name))  # could be interval(0,1)
  if (shape1==0) return(pbox(0,shape='beta',name=name))
  if (shape2==0) return(pbox(1,shape='beta',name=name))
  m <- shape1/(shape1+shape2)
  v <- shape1*shape2/((shape1+shape2)^2*(shape1+shape2+1))
  pbox(u=qbeta(ii(), shape1, shape2), d=qbeta(jj(), shape1, shape2), shape='beta', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Sbetabinomial <- function(a,b,n) {
  k <- 0:n
  p <- cumsum(choose(n,k) * .Internal(beta(k+a,n-k+b)) / .Internal(beta(a,b)))
  m <- n*a/(a+b)
  v <- n*a*b*(a+b+n)/((a+b)^2*(a+b+1))
  u <- rep(0:n,diff(ceiling(c(0,p)*Pbox$steps)))[1:Pbox$steps]
  d <- c(rep(0:n,diff(floor(c(0,p)*Pbox$steps))),n)[1:Pbox$steps]
  pbox(u=u,d=d,ml=m,mh=m,vl=v,vh=v,shape='beta-binomial')
  }

Sbinomial <- function(size=NULL, prob=NULL, mean=NULL, std=NULL, name=''){
  if (is.null(size) & !is.null(mean) & !is.null(std)) size <- mean/(1-std^2/mean)
  if (is.null(prob) & !is.null(mean) & !is.null(std)) prob <- 1-std^2/mean
  m <- size*prob
  v <- size*prob*(1-prob)
  pbox(u=qbinom(ii(), size, prob), d=qbinom(jj(), size, prob), shape='binomial', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Sbradford <- function(location, scale, shape, name=''){
  k <- log(shape + 1)
  m <- (shape * (scale - location) + k * (location * (shape + 1) - scale) ) / (shape * k)
  v <- ((scale - location)^2 * (shape * (k - 2) + 2 * k)) / (2 * shape * k^2)
  u <- qbradford(iii(), location, scale, shape)
  d <- qbradford(jjj(), location, scale, shape)
  pbox(u=u, d=d, shape='Bradford', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Scauchy <- function(location, scale, name=''){
  pbox(u=qcauchy(iii(), location, scale), d=qcauchy(jjj(), location, scale), shape='Cauchy', name=name, ml=-Inf, mh=Inf, vl=0, vh=Inf)
  }

Schisquared <- function(df, name=''){
  pbox(u=qchisq(ii(),df), d=qchisq(jjj(),df), shape='chi-squared', name=name, ml=df, mh=df, vl=2*df, vh=2*df)
  }

Sdelta <- Sdirac <- function(x,name='') pbox(x,x,shape='delta',name=name)

Sdiscreteuniform0 <- function(max) pbox(Min(max,int(uniform(0, max+1))), ml=max/2, mh=max/2, vl=max*(max+2)/12, vh=max*(max+2)/12)  

Sdiscreteuniform <- function(max=NULL, mean=NULL) {
  if (is.null(max) & !is.null(mean)) max <- 2 * mean
  discreteuniform0(max)
  }

Sexponential <- function(mean, name=''){
  pbox(u=qexp(ii(),1/mean), d=qexp(jjj(),1/mean), shape='exponential', name=name, ml=mean, mh=mean, vl=mean^2, vh=mean^2)
  }

SF <- Sf <- Sfishersnedecor <- function(df1, df2, name=''){
  m <- df2/(df2-2)
  v <- 2*df2^2*(df1+df2-2)/(df1*(df2-2)^2*(df2-4))
  pbox(u=qf(ii(), df1, df2), d=qf(jjj(), df1, df2), shape='F', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Sfrechet <- function(b, c, name=''){
  ml <- -Inf
  mh <- Inf
  if (1 < c) ml <- mh <- b * gammafunc(1 - 1 / c)
  vl <- 0
  vh <- Inf
  if (2 < c){
             e = gammafunc(1 - 1 / c)
             vl <- vh <- b * b * (gammafunc(1 - 2/c) -  e*e)
            } 
  pbox(u=qfrechet(ii(), b, c),  d=qfrechet(jjj(), b, c), shape='Frechet', name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

Sgamma <- function(b, c, name=''){    # N.B. the parameters are b (scale) and c (shape), which is different from rgamma's parameters which are shape and rate (1/scale)
  m <- b*c 
  v <- b^2*c 
  pbox(u=qgamma(ii(), shape=c, scale=b), d=qgamma(jjj(), shape=c, scale=b), shape='gamma', name=name, ml=m, mh=m, vl=v, vh=v) 
  } 

Sgamma1 <- function(mu, sigma, name='') return(gamma(sigma^2/mu, (mu/sigma)^2, name='')) 

Sgamma2 <- function(shape, scale, name=''){ 
  m <- shape*scale 
  v <- shape*scale^2 
  pbox(u=qgamma(iii(), shape=shape, scale=scale), d=qgamma(jjj(), shape=shape, scale=scale), shape='gamma', name=name, ml=m, mh=m, vl=v, vh=v) 
  } 

# N.B. gammaexponential has a DIFFERENT order of arguments (so that it can be integrated with env2.4...it's stupid)
Sgammaexponential <- function(shape, scale=1, rate=1/scale, name='') {
  ml <- -Inf
  mh <- Inf
  vl <- 0
  vh <- Inf
  pbox(u=qgammaexponential(ii(),shape,scale,rate), d=qgammaexponential(jjj(),shape,scale,rate), name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

Sinversegamma <- function(a, b, name=''){ 
  m <- b/(a-1)
  v <- b^2/((a-1)^2*(a-2))
  pbox(u=rev(1/qgamma(jj(), shape=a, scale=1/b)), d=rev(1/qgamma(iii(), shape=a, scale=1/b)), shape='inverse gamma', name=name, ml=m, mh=m, vl=v, vh=v) 
  } 

Sgeometric <- Spascal <- function(prob=NULL, mean=NULL, name=''){
  if (is.null(prob) & !is.null(mean)) prob <- 1/(1+ mean)
  m <- (1-prob)/prob
  v <- (1-prob)/prob^2
  pbox(u=qgeom(ii(),prob), d=qgeom(jjj(),prob), shape='geometric', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Sgev <- Sgeneralizedextremevalue <- function(a=0,b=1,c=0, name='') { # http://en.wikipedia.org/wiki/Generalized_extreme_value_distribution
  if (same(c,0)) return(Sgumbel(a,b,name=''))
  g1 <- gammafunc(1 - c)
  g2 <- gammafunc(1 - 2 * c)
  if (c == 0) m <- a + b * 0.57721566490153 else if (1 <= c) m <- Inf else if (c < 1)
  m <- a + (g1 - 1) * (b/c)
  if (c == 0) v <- (b*base::pi)^2/6 else if (0.5 <= c) v <- Inf else if (c < 1)
  v <- (b/c)^2 * (g2 - g1^2)
  if (0<c) {u = qgev(ii(),a,b,c); d = qgev(jjj(),a,b,c) }
  if (c<0) {u = qgev(iii(),a,b,c); d = qgev(jj(),a,b,c) }
  pbox(u=u, d=d, shape='generalized extreme value', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Sgumbel <- Sextremevalue <- function(a=NULL, b=NULL, mean=NULL, std=NULL, var=NULL, name=''){  
  em <- 0.577215665
  if (missing(std) && !missing(var)) std <- sqrt(var)
  if (missing(a) && missing(b)) {a <- mean-std*em*sqrt(6)/base::pi; b <- std*sqrt(6)/base::pi}
  if (missing(mean)) mean <- a + b * em
  if (missing(var)) var <- ((b * base::pi)^2 / 6)
  pbox(u=qgumbel(iii(), a, b), d=qgumbel(jjj(), a, b), shape='Gumbel', name=name, ml=mean, mh=mean, vl=var, vh=var)
  }

Shypergeometric0 <- function( m, n, k, name=''){
  N <- m + n
  # mean <- k * m / N
  mean <- k / (1+n/m)
  v <- (k*m/N) * (1-m/N) * (N-k) / (N-1)   ########### suboptimal?
  pbox(u=qhyper(iii(), m, n, k), d=qhyper(jjj(), m, n, k), shape='hypergeometric', name=name, ml=mean, mh=mean, vl=v, vh=v)
  }

Shypergeometric <- function(whites=NULL, blacks=NULL, draws=NULL, balls=NULL, name=''){
  # what if whites+black != balls ?
  if (is.null(blacks) & !is.null(balls) & !is.null(whites)) blacks <- balls - whites
  if (is.null(whites) & !is.null(balls) & !is.null(blacks)) whites <- balls - blacks
  if (whites+blacks<draws) stop('too many draws to specify the hypergeometric distribution')
  if (!is.null(blacks) & !is.null(whites) & !is.null(draws)) Shypergeometric0(whites,blacks,draws,name) else stop('not enough information to specify the hypergeometric distribution')
  }

Skumaraswamy <- function(a, b, name=''){
  # Pbox$bOth parameters must be larger than zero
  moment <- function(n) (b*gammafunc(1+n/a)*gammafunc(b)) / gammafunc(1+b+n/a)
  i <- c(  1:(Pbox$steps-1) / Pbox$steps)              
  j <- c(  1:(Pbox$steps-1) / Pbox$steps   )
  kumar <- function(p) exp( (1/a) * log(1-exp((1/b)*log(1-p))))
  u <- c(0, kumar(i))
  d <- c(   kumar(j), 1)
  m <- moment(1)
  v <- moment(2) - m^2
  pbox(u=u, d=d, shape='kumaraswamy', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Slaplace <- function(a, b, name=''){
  m = a
  v = 2 * b * b
  pbox(u=qlaplace(iii(), a, b), d=qlaplace(jjj(), a, b), shape='Laplace', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Slogistic <- function(location, scale, name=''){
  m <- location
  v <- (base::pi*scale)^2/3
  pbox(u=qlogis(iii(),location, scale), d=qlogis(jjj(),location, scale), shape='logistic', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Slognormal0 <- function(meanlog, stdlog, name=''){
  m <- (exp(meanlog + 0.5 * stdlog * stdlog));
  v <- (exp(2.0 * meanlog + stdlog * stdlog) * (exp(stdlog * stdlog)-1.0));
  pbox(u=qlnorm(iii(),meanlog,stdlog), d=qlnorm(jjj(),meanlog,stdlog), shape='lognormal', name=name, ml=m, mh=m, vl=v, vh=v)  ### moments
  }

SL <- Slognormal <- function(mean=NULL, std=NULL, meanlog=NULL, stdlog=NULL, median=NULL, cv=NULL, name='', ...){
  if (is.null(meanlog) & !is.null(median)) meanlog = log(median)
  if (is.null(stdlog) & !is.null(cv)) stdlog = sqrt(log(cv^2 + 1))
  # lognormal(a, b) ~ lognormal2(log(a^2/sqrt(a^2+b^2)),sqrt(log((a^2+b^2)/a^2)))
  if (is.null(meanlog) & (!is.null(mean)) & (!is.null(std))) meanlog = log(mean^2/sqrt(mean^2+std^2))
  if (is.null(stdlog) & !is.null(mean) & !is.null(std)) stdlog = sqrt(log((mean^2+std^2)/mean^2))
  if (!is.null(meanlog) & !is.null(stdlog)) Slognormal0(meanlog,stdlog,name) else stop('not enough information to specify the lognormal distribution')
  }

Slogtriangular <- function(min=NULL, mode=NULL, max=NULL, minlog=NULL, midlog=NULL, maxlog=NULL, name=''){
  if (is.null(min) & !is.null(minlog)) min = exp(minlog)  ###place in arglist
  if (is.null(max) & !is.null(maxlog)) max = exp(maxlog)  ###place in arglist
  lsd <- function(a, b) if (nothing(a-b)) (a+b)/2.0 else (a-b)/log(a/b)
  lsd2 <- function(a, b) if (nothing(a-b)) -2*((a+b)/2)^2 else (a^2-b^2)/log(b/a)
  m <- (2.0/log(max/min)) * (lsd(max,mode) - lsd(mode,min))
  v <- (lsd2(min,mode) - lsd2(mode,max)) / (2 * log(max/min)) - (m*m)
  pbox(u=qlogtriangular(ii(), min, mode, max), d=qlogtriangular(jj(), min, mode, max), shape='logtriangular', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Sloguniform <- function(min=NULL, max=NULL, minlog=NULL, maxlog=NULL, mean=NULL, std=NULL, name=''){
  if (is.null(min) & !is.null(minlog)) min <- exp(minlog)
  if (is.null(max) & !is.null(maxlog)) max <- exp(maxlog)
  if (is.null(max) &  !is.null(mean) & !is.null(std) & !is.null(min)) max = 2.0 * (mean^2 +std^2)/mean - min
  mean = (max - min)/(log(max) - log(min))
  z = log(max/min)
  v = (mean - (max - min)/z)^2 + (max^2 - min^2) / (2*z) - ((max - min) / z)^2
  pbox(u=qloguniform(ii(), min, max), d=qloguniform(jj(), min, max), shape='loguniform', name=name, ml=mean, mh=mean, vl=v, vh=v)
  }

Snegativebinomial <- function(size, prob, name=''){
  m <- size * (1/prob - 1) 
  v <- size * (1 - prob) / (prob^2)
  pbox(u=qnbinom(ii(), size, prob), d=qnbinom(jjj(), size, prob), shape='negative binomial', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Snormal0 <- function(normmean, normstd, name=''){ 
  pbox(u=qnorm(iii(),normmean,normstd), d=qnorm(jjj(),normmean,normstd), shape='normal', name=name, ml=normmean, mh=normmean, vl=normstd^2, vh=normstd^2)
  }

SNormal <- Snormal <- Sgaussian <- function(mean=NULL, std=NULL, median=NULL, mode=NULL, cv=NULL, iqr=NULL, var=NULL, name='', ...){
  if (is.null(mean) & !is.null(median)) mean = median
  if (is.null(mean) & !is.null(mode)) mean = mode
  if (is.null(std) & !is.null(cv) & !is.null(mean)) std = mean * cv
  if (!is.null(mean) & !is.null(std)) Snormal0(mean,std,name) else stop('not enough information to specify the normal distribution')
  }

SSN <- Sskewnormal <- function(location, scale, skew, name=''){ 
  library('sn')
  d = (skew/sqrt(1+skew^2))
  m = location + scale * d * sqrt(2/base::pi)    # skew is repeated !!
  v = scale^2 * (1 - 2*d^2/base::pi)
  pbox(u=qsn(iii(),location,scale,skew), d=qsn(jjj(),location,scale,skew), shape='skew-normal', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Spareto <- function(mode, c, name=''){
  ml <- -Inf
  mh <- Inf
  if (1<c) ml <- mh <- mode * c / (c - 1)
  vl <- 0
  vh <- Inf
  if (2<c) vl <- vh <- mode * mode * c / ((c-1)*(c-1)*(c-2))
  pbox(u=qpareto(iii(), mode, c), d=qpareto(jjj(), mode, c), shape='Pareto', name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

Spowerfunction <- function(b, c, name=''){
  m <- b * c / (c + 1)
  v <- b * b * c / ((c+2)*(c+1)*(c+1))
  pbox(u=qpowerfunction(iii(), b, c), d=qpowerfunction(jjj(), b, c), shape='power function', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Spoisson <- function(lambda, name=''){
  pbox(u=qpois(ii(),lambda), d=qpois(jjj(),lambda), shape='Poisson', name=name, ml=lambda, mh=lambda, vl=lambda, vh=lambda)
  }

Squadratic <- function(mean=0, max=1, name=''){ 
  # June 2009 Draft NASA Report "Measurement Uncertainty Analysis: Principles and Methods". Appendix B, page 151
  if (mean==max) return(pbox(mean))
  # would like to replace the next two lines with a call to 'contextstopifnot' which mentions the name of the constructor in which the errant parameters were detected
     if (max<mean) warning('')
     stopifnot(mean<=max)
  m <- mean
  v <- (max-mean)^2/5
  pbox(u=qquadratic(ii(),mean,max), d=qquadratic(jj(),mean,max), shape='quadratic', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Squadratic1 <- function(mean=0, std=1, name='') quadratic(mean, sqrt(5)*std+mean, name)

Suquadratic <- function(a=0, b=1, name=''){ 
  # http://en.wikipedia.org/wiki/U-quadratic_distribution
  if (a==b) return(pbox(a))
  # would like to replace the next two lines with a call to 'contextstopifnot' which mentions the name of the constructor in which the errant parameters were detected
     if (b<a) warning('')
     stopifnot(a<=b)
  m <- (a+b)/2
  v <- 3*(b-a)^2/20
  pbox(u=ququadratic(ii(),a,b), d=ququadratic(jj(),a,b), shape='uquadratic', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Suquadratic1 <- function(mean=0, std=1, name='') uquadratic(mean-std*sqrt(5/3),mean+std*sqrt(5/3), name)

Srayleigh <- function(b, name=''){
  m <- b * sqrt(base::pi/2)
  v <- (2 - base::pi/2) * b * b
  pbox(u=qrayleigh(ii(), b), d=qrayleigh(jjj(), b), shape='rayleigh', name=name, ml=m, mh=m, vl=v, vh=v) 
  }

Sreciprocal <- function(a=10.0, name=''){
 m <- (a - 1) / log(a)
 pbox(u=qreciprocal(ii(), a), d=qreciprocal(jj(), a), shape='reciprocal', name=name, ml=m, mh=m, vl=0, vh=Inf)
 }

Sshiftedloglogistic <- function(a=0,b=1,c=0,name='')  {
  if (same(c,0)) return(Slogistic(a,b,name=''))
  csc <- function(x) 1/sin(x)
  m <- a + b * (base::pi*c*csc(base::pi*c)) / c
  v <- b^2  * (2*base::pi*c*csc(2*base::pi*c)-(base::pi*c*csc(base::pi*c))^2) / (c^2)
  if (0<c) {u = qshiftedloglogistic(ii(),a,b,c); d = qshiftedloglogistic(jjj(),a,b,c) }
  if (c<0) {u = qshiftedloglogistic(iii(),a,b,c); d = qshiftedloglogistic(jj(),a,b,c) }
  pbox(u=u, d=d, shape='shifted loglogistic', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Strapezoidal <- function(a, b, c, d, name=''){
  ab <- a + b
  cd <- c + d
  if (nothing(cd-ab)) h <- 1 else h <- 1.0 / (3.0 * (cd - ab))
  m <- h * (c * cd + d*d - (a * ab + b*b))
  if (nothing(d - a)) {
                  m <- a   
                  v <- 0.0
           } else v <- 0.5 * h * (cd * (c*c + d*d) -  ab * (a*a + b*b)) - m*m
  pbox(u=qtrapezoidal(ii(), a, b, c, d), d=qtrapezoidal(jj(), a, b, c, d), shape='trapezoidal', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Striangular <- function(min, mode, max, name=''){
  m <- (min + mode + max) / 3
  v <- (min*min + mode*mode + max*max - min*mode - min*max - mode*max) / 18
  pbox(u=qtriangular(ii(), min, mode, max), d=qtriangular(jj(), min, mode, max), shape='triangular', name=name, ml=m, mh=m, vl=v, vh=v)
  }

SU <- Suniform <- Srectangular <- function(min, max, name=''){
  m <- (min+max)/2
  v <- (min-max)^2/12
  pbox(u=qunif(ii(),min,max), d=qunif(jj(),min,max), shape='uniform', name=name, ml=m, mh=m, vl=v, vh=v)
  }   

Sskellam <- function(m1, m2, name=''){
  pbox(Spoisson(m1) %|-|% Spoisson(m2), name=name)
  }

Sstudent <- function(df, name=''){
  m <- 0
  v <- 1/(1-2/df)
  pbox(u=qt(iii(),df), d=qt(jjj(),df), shape="Student's t", name=name, ml=m, mh=m, vl=v, vh=v)
  }

Strapezoidal <- function(a, b, c, d, name=''){
  ab <- a + b
  cd <- c + d
  if (nothing(cd-ab)) h <- 1 else h <- 1.0 / (3.0 * (cd - ab))
  m <- h * (c * cd + d*d - (a * ab + b*b))
  if (nothing(d - a)) {
                  m <- a   
                  v <- 0.0
           } else v <- 0.5 * h * (cd * (c*c + d*d) -  ab * (a*a + b*b)) - m*m
  pbox(u=qtrapezoidal(ii(), a, b, c, d), d=qtrapezoidal(jj(), a, b, c, d), shape='trapezoidal', name=name, ml=m, mh=m, vl=v, vh=v)
  }

Svoigt <- function(sigma, gamma, name=''){
  p <- pbox(normal(0,sigma) %|+|% cauchy(0,gamma), name=name, shape='Voigt')
  p@ml <- -Inf
  p@mh <- Inf
  p@vl <- 0
  p@vh <- Inf
  p
  }

Swakeby <- function(zeta, theta, beta, delta, gamma, name=''){
  m = (zeta+theta/(beta+1)+delta/(1-gamma))
  pbox(u=qwakeby(iii(), zeta, theta, beta, delta, gamma), d=qwakeby(jjj(), zeta, theta, beta, delta, gamma), shape='Wakeby', name=name, ml=m, mh=m, vl=0, vh=Inf)
  }

Swilcoxon <- function(m, n, name=''){ # distribution of the Wilcoxon rank sum statistic (see R's qwilcox)
  mn = m * n / 2
  vr = m * n * (m + n + 1) / 12
  pbox(u=qwilcox(ii(), m, n), d=qwilcox(jj(), m, n), shape='Wilcoxon', name=name, ml=mn, mh=mn, vl=vr, vh=vr)
  }

Sweibull <- function(scale, shape, name=''){  # argument order disagrees with R's qweibull function, but agrees with Wikipedia (in November 2013)
  m <- scale * gammafunc(1+1/shape)
  v <- scale^2*(gammafunc(1+2/shape)-(gammafunc(1+1/shape))^2)
  pbox(u=qweibull(ii(), shape, scale), d=qweibull(jjj(), shape, scale), shape='Weibull', name=name, ml=m, mh=m, vl=v, vh=v)
  }



#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@








arcsin <- function(name=''){ # support = [0,1], mean = 1/2
  #vl <- 0           #!!
  #vh <- Inf        #!!
  pbox(u=qarcsin(ii()), d=qarcsin(jj()), shape='arc sine', name=name, ml=1/2, mh=1/2)
  }

arctan <- function(alpha, phi, name='', sc=TRUE){ #    0 < alpha;      support = [0,infinity)
  if (sc) return(env2.4(arctan,alpha,phi, name=name,sc=FALSE))
  #ml <- -Inf      #!!
  #mh <- Inf      #!!
  #vl <- 0           #!!
  #vh <- Inf        #!!
  pbox(u=qarctan(ii(),alpha, phi), d=qarctan(jjj(),alpha, phi), shape='arc tangent', name=name)
  }

benford <- function(name=''){ # support = {1,2,...,9}, mean = 3.4402, var = 6.0565
  pbox(u=qbenford(ii()), d=qbenford(jj()), shape='Benford', name=name, ml=3.440236967123, mh=3.440236967123, vl=6.056512631376, vh=6.056512631376)
  }

chi <- function(n, name=''){
  pbox(sqrt(chisquared(n)), shape='chi', name=name)
  }

exponentialpower <- function(lambda, kappa, name='', sc=TRUE) { # support = [0,infinity)      (scale) lambda > 0, (shape) kappa > 0
  if (sc) return(env2.4(exponentialpower,lambda,kappa, name=name,sc=FALSE))
  #ml <- -Inf      #!!
  #mh <- Inf      #!!
  #vl <- 0           #!!
  #vh <- Inf        #!!
  pbox(u=qexponentialpower(ii(),lambda, kappa), d=qexponentialpower(jjj(),lambda, kappa), shape='exponential-power', name=name)
  }
  
  
  
  
  
  
  
  
GEV <- generalizedextremevalue <- function(a=0,b=1,c=0, name='', ...) env3.8(Sgev, a, b, c, name, ...)  # if c==0 Gumbel;  if 0<c Frechet;  if c<0 Weibull  # http://en.wikipedia.org/wiki/Generalized_extreme_value_distribution






#GEV <- generalizedextremevalue <- function(a=0,b=1,c=0, name='', sc=TRUE) { # http://en.wikipedia.org/wiki/Generalized_extreme_value_distribution
#  if (same(c,0)) return(gumbel(a,b,name=name))
#  if (sc) return(env3.8(gev,a,b,c, name=name,sc=FALSE))
#  g1 <- gammafunc(1 - c)
#  g2 <- gammafunc(1 - 2 * c)
#  m <- a + (g1 - 1) * (b/c)
#  v <- (b/c)^2 * (g2 - g1^2)
#  wgev <- function(p) a + b * ((1/(-log(p)))^c - 1) / c
#  pbox(u=wgev(ii()), d=wgev(jjj()), shape='generalized extreme value', ml=m, mh=m, vl=v, vh=v, name=name)
#  }
#
#gev <- generalizedextremevalue <- function(m, s, z, name=''){   # this is the GENERALIZED extreme value distribution
#   genextrval <- function(p) m + s * (1/((-log(p))^(1/z))-1) / z
#   pbox(u=genextrval(iii()), d=genextrval(jjj()), shape='generalized extreme value', name=name, ml=m, mh=m, vl=s^2, vh=s^2)
#   }
#
#extremevalue <- function(m, s, z, name=''){   # this is the GENERALIZED extreme value distribution
#  genextrval <- function(p) m + s * (1/((-log(p))^(1/z))-1) / z
#  pbox(u=genextrval(iii()), d=genextrval(jjj()), shape='generalized extreme value', name=name, ml=m, mh=m, vl=s^2, vh=s^2)
#  }














#gumbel <- extremevalue <- fishertippett <- function(a=NULL, b=NULL, mean=NULL, std=NULL, var=NULL, name='', sc=TRUE){  
#  em <- 0.577215665
#  if (missing(std) && !missing(var)) std <- sqrt(var)
#  if (missing(a) && missing(b)) {a <- mean-std*em*sqrt(6)/base::pi; b <- std*sqrt(6)/base::pi}
#  if (missing(mean)) mean <- a + b * em
#  if (missing(var)) var <- ((b * base::pi)^2 / 6)
#  if (sc) return(env2.4(gumbel,a,b, name=name,sc=FALSE))
#  pbox(u=qgumbel(iii(), a, b), d=qgumbel(jjj(), a, b), shape='Gumbel', name=name, ml=mean, mh=mean, vl=var, vh=var)
#  }
#
#hypergeometric0 <- function( m, n, k, name='', sc=TRUE){
#  if (sc) return(env3.8(hypergeometric,m,n,k, name=name,sc=FALSE))
#  N <- m + n
#  mean <- k * m / N
#  v <- (k*m/N) * (1-m/N) * (N-k) / (N-1)
#  pbox(u=qhyper(iii(), m, n, k), d=qhyper(jjj(), m, n, k), shape='hypergeometric', name=name, ml=mean, mh=mean, vl=v, vh=v)
#  }
#
#hypergeometric <- function(whites=NULL, blacks=NULL, draws=NULL, balls=NULL, name=''){
#  # what if whites+black != balls ?
#  if (is.null(blacks) & !is.null(balls) & !is.null(whites)) blacks <- balls - whites
#  if (is.null(whites) & !is.null(balls) & !is.null(blacks)) whites <- balls - blacks
#  if (!is.null(blacks) & !is.null(whites) & !is.null(draws)) hypergeometric0(whites,blacks,draws,name) else stop('not enough information to specify the hypergeometric distribution')
#  }

hyperbolicsecant <- function(name=''){
  pbox(u=(2/base::pi)*log(tan(iii()*base::pi/2)), d=(2/base::pi)*log(tan(jjj()*base::pi/2)), shape='hyperbolic secant', name=name, ml=0, mh=0, vl=1, vh=1)
##############
# Does
# a=hyperbolicsecant()
#     P-box:  ~ hyperbolic secant( range=[-4.110127,4.110127], mean=0, var=1) 
# give the same result as would 
# qhyperbolicsecant <- function(p) return(-asinh(cot(base::pi*p))/base::pi)
# b=pbox(qhyperbolicsecant(p))
##############
  }

hypoexponential <- function(lambda, name='',sc=TRUE){
  if (sc) return(env1.2(hypoexponential,lambda, name=name,sc=FALSE))
  pbox(u=qhypoexponential(ii(),lambda), d=qhypoexponential(jjj(),lambda), shape='hypoexponential', name=name)
  }

#kumaraswamy <- function(a, b, name='',sc=TRUE){ # both parameters must be larger than zero
#  if (sc) return(env2.4(kumaraswamy,a,b, name=name,sc=FALSE))
#  i <- c(  1:(Pbox$steps-1) / Pbox$steps)              
#  j <- c(  1:(Pbox$steps-1) / Pbox$steps   )
#  kumar <- function(p) exp( (1/a) * log(1-exp((1/b)*log(1-p))))
#  moment <- function(n) (b*gammafunc(1+n/a)*gammafunc(b)) / gammafunc(1+b+n/a)
#  m <- moment(1)
#  v <- moment(2) - m^2
#  pbox(u=c(0,kumar(i)), d=c(kumar(j),1), shape='kumaraswamy', name=name, ml=m, mh=m, vl=v, vh=v)
#  }

loglogistic <- function(lambda, kappa, name='',sc=TRUE) { # support = [0,infinity)      (scale) lambda > 0, (shape) kappa > 0
  if (sc) return(env2.4(loglogistic,lambda,kappa, name=name,sc=FALSE))
  #ml <- -Inf      #!!
  #mh <- Inf      #!!
  #vl <- 0           #!!
  #vh <- Inf        #!!
  pbox(u=qloglogistic(ii(),lambda, kappa), d=qloglogistic(jjj(),lambda, kappa), shape='loglogistic', name=name)
  }

lomax <- function(lambda, kappa, name='',sc=TRUE) { # support = (0,infinity)      (scale) lambda > 0, (shape) kappa > 0
  if (sc) return(env2.4(lomax,lambda,kappa, name=name,sc=FALSE))
  #ml <- -Inf      #!!
  #mh <- Inf      #!!
  #vl <- 0           #!!
  #vh <- Inf        #!!
  pbox(u=qlomax(ii(),lambda, kappa), d=qlomax(jjj(),lambda, kappa), shape='Lomax', name=name)
  }

muth <- function(kappa, name='', sc=TRUE) { # support = [0,infinity)      0 < kappa <= 1
  if (sc) return(env1.2(muth,kappa, name=name,sc=FALSE))
  #ml <- -Inf      #!!
  #mh <- Inf      #!!
  #vl <- 0           #!!
  #vh <- Inf        #!!
  pbox(u=qmuth(ii(),kappa), d=qmuth(jjj(),kappa), shape='Muth', name=name)
  }


wilcoxon <- function(m, n, name='', sc=TRUE){
  if (sc) return(env2.4(wilcoxon,m,n, name=name,sc=FALSE))
  pbox(u=qwilcox(ii(), m, n), d=qwilcox(jj(), m, n), shape='Wilcoxon', name=name, ml=-Inf, mh=Inf, vl=0, vh=Inf)
  }













#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

 
env1.2 <- function(dname, i, ...) {
 safe = Pbox$plotting.every
 Pbox$plotting.every <- FALSE
 a = env(
   do.call(dname,list(left(i), ...)),
   do.call(dname,list(right(i), ...)))
 Pbox$plotting.every <- safe
 a@dids = paste('PB',uniquepbox(),sep='')
 if (Pbox$plotting.every) try(plot.pbox(a))
 return(a)
 }

env2.4 <- function(dname, i, j, ...) {
 safe = Pbox$plotting.every
 Pbox$plotting.every <- FALSE
 a = env(
   do.call(dname,list(left(i), left(j), ...)),
   do.call(dname,list(right(i), left(j), ...)),
   do.call(dname,list(left(i), right(j), ...)),
   do.call(dname,list(right(i), right(j), ...)))
 Pbox$plotting.every <- safe
 a@dids = paste('PB',uniquepbox(),sep='')
 if (Pbox$plotting.every) try(plot.pbox(a))
 return(a)
 }

env2.2 <- function(dname, i, j, ...) {
 safe = Pbox$plotting.every
 Pbox$plotting.every <- FALSE
#a = env(
#  do.call(dname,list(left(i), left(j), ...)),
#  do.call(dname,list(right(i), right(j), ...)))
 U_ <- function() {
    if (right(i)<left(j)) return(env(dname(left(i),left(j)),dname(left(i),right(j)),dname(right(i),left(j)),dname(right(i),right(j)))) else
    if ((left(i)<left(j)) & (right(i)<right(j))) return(env(dname(left(i),left(j)),left(j),dname(left(i),right(j)),dname(right(i),right(j)))) else
    if ((left(j)<=left(i)) & (right(i)<=right(j))) return(env(left(i),dname(left(i),right(j)),dname(right(i),right(j)))) else
    if ((left(i)<=left(j)) & (right(j)<=right(i))) return(env(dname(left(i),left(j)),dname(left(i),right(j)),right(j))) else
    if (right(j)>=left(i)) return(env(left(i),right(j),dname(left(i),right(j)))) else stop('Minimum must be smaller than maximum')
    }
 a = U_()
 Pbox$plotting.every <- safe
 a@dids = paste('PB',uniquepbox(),sep='')
 if (Pbox$plotting.every) try(plot.pbox(a))
 if (identical(dname,Sloguniform)) a@shape = 'loguniform' else a@shape = 'uniform'
 return(a)
 }
 
env3.8 <- function(dname, i,j,k, ...) {   # improve by not duplicating if an argument is scalar
 safe = Pbox$plotting.every 
 Pbox$plotting.every <- FALSE
 a = env(
   do.call(dname,list(left(i),left(j), left(k), ...)),
   do.call(dname,list(left(i),right(j), left(k), ...)),
   do.call(dname,list(left(i),left(j), right(k), ...)),
   do.call(dname,list(left(i),right(j), right(k), ...)),
   do.call(dname,list(right(i),left(j), left(k), ...)),
   do.call(dname,list(right(i),right(j), left(k), ...)),
   do.call(dname,list(right(i),left(j), right(k), ...)),
   do.call(dname,list(right(i),right(j), right(k), ...)))
  Pbox$plotting.every <- safe
 a@dids = paste('PB',uniquepbox(),sep='')
 if (Pbox$plotting.every) try(plot.pbox(a))
 return(a)
  }

# bernoulli <- function(p, ...) env1.2(Sbernoulli,p, ...)
Be <- beta <- function(shape1, shape2, ...) env2.4(Sbeta,shape1,shape2,...)
BB <- betabinomial <- function(a, b, n, ...) env3.8(Sbetabinomial, a, b, n, ...)
B <- binomial <- function(size=NULL, prob=NULL, ...) env2.4(Sbinomial,size,prob,...)
bradford <- function(location, scale, shape, ...) env3.8(Sbradford, location, scale, shape, ...)
cantor <- function(...){ fnp1 <- function(fn) {fa <- fn[k %% 2 == 0] / 3; fnext <- c(fa, fa + 2/3); fnext }; k <- 1:(Pbox$steps+2); fn <- k / (Pbox$steps+2); for (kk in 1:20) fn <- fnp1(fn); i <- 1:Pbox$steps; j <- 2:(Pbox$steps+1); pbox(u=fn[i], d=fn[j], shape='Cantor', ml=0.5, mh=0.5, vl=1/8, vh=1/8, ...) }
cauchy <- function(location, scale, ...) env2.4(Scauchy,location,scale,...)
chisquared <- function(df, ...) env1.2(Schisquared,df, ...)
delta <- dirac <- function(x,...)  env1.2(Sdelta,x, ...)
discreteuniform <- function(max, ...)  env1.2(Sdiscreteuniform0,max, ...)
exponential <- function(mean, ...) env1.2(Sexponential,mean, ...)
F <- f <- fishersnedecor <- function(df1, df2, ...) env2.4(SF,df1,df2,...)
frechet <- function(b, c, ...) env2.4(Sfrechet,b,c, ...)
gamma <- erlang <- function(shape, scale, ...) env2.4(Sgamma,shape,scale, ...) 
gamma1 <- function(mu, sigma, ...) return(gamma(sigma^2/mu, (mu/sigma)^2, ...))
gamma2 <- function(shape, scale, ...) env2.4(Sgamma2,shape, scale, ...) 
inversegamma <- function(a, b, ...) env2.4(Sinversegamma,a,b, ...)

# notice that gammaexponential and Sgammaexponential have different argument orders
# Sgammaexponential <- function(shape, scale=1, rate=1/scale, name='') 
gammaexponential <- function(shape, rate=1, scale=1/rate, ...) env2.4(Sgammaexponential, shape, scale, ...)

geometric <- pascal <- function(prob, ...) env1.2(Sgeometric,prob, ...)
gumbel <- extremevalue <- function(a, b, ...) env2.4(Sgumbel, a, b, ...)  
hyperbolicsecant <- function(...){ u <- (2/base::pi)*log(tan(iii()*base::pi/2)); d <- (2/base::pi)*log(tan(jjj()*base::pi/2)); pbox(u=u, d=d, shape='hyperbolic secant', ml=0, mh=0, vl=1, vh=1, ...) }
hypergeometric <- function(whites=NULL, blacks=NULL, draws=NULL, balls=NULL, ...) env3.8(Shypergeometric, whites, blacks, draws, balls, ...)
kumaraswamy <- function(a, b, ...) env2.4(Skumaraswamy, a, b, ...)
laplace <- function(a, b, ...) env2.4(Slaplace, a, b, ...)
logistic <- function(location, scale, ...) env2.4(Slogistic, location, scale, ...)
L <- lognormal <- function(mean, std, ...) env2.4(SL, mean, std, ...)
negativebinomial <- function(size, prob, ...) env2.4(Snegativebinomial, size, prob, ...)
N <- normal <- gaussian <- function(mean, std, ...) env2.4(SNormal, mean, std, ...)
SN <- skewnormal <- function(location, scale, skew, ...) env3.8(SSN, location, scale, skew, ...)
pareto <- function(mode, c, ...) env2.4(Spareto, mode, c, ...)
powerfunction <- function(b, c, ...) env2.4(Spowerfunction, b,c, ...)
poisson <- function(lambda, ...) env1.2(Spoisson,lambda, ...)

# poissonbinomial

quadratic <- function(mean=0, max=1, ...) env2.4(Squadratic, mean, max, ...)
quadratic1 <- function(mean=0, std=1, ...) env2.4(Squadratic1, mean, std, ...)
uquadratic <- function(a=0, b=1, ...) env2.4(Suquadratic, a, b, ...)
uquadratic1 <- function(mean=0, std=1, ...) env2.4(Suquadratic1, mean, std, ...)
rayleigh <- function(b, ...) env1.2(Srayleigh,b, ...)
reciprocal <- function(a=10, ...) env1.2(Sreciprocal,a, ...)
shiftedloglogistic <- function(a=0,b=1,c=0, ...) env3.8(Sshiftedloglogistic, a, b, c, ...)
skellam <- function(m1, m2, ...) env2.4(Sskellam, m1, m2, ...)
t <- student <- function(df, ...) env1.2(Sstudent,df, ...)
#####trapezoidal <- function(a, b, c, d, ...) env4.16(Strapezoidal, a, b, c, d, ...)
voigt <- function(sigma, gamma, ...) env2.4(Svoigt, sigma,gamma, ...)
wakeby <- function(zeta, theta, beta, delta, gamma, ...) env5.32(Swakeby, zeta, theta, beta, delta, gamma,  ...)
wilcoxon <- function(m, n, ...) env2.4(Swilcoxon, m, n, ...)
weibull <- function(scale, shape, ...) env2.4(Sweibull, scale, shape, ...)

U <- uniform <- rectangular <- function(min,max, ...) env2.2(SU,min,max, ...)
loguniform <- function(min,max, ...) env2.2(Sloguniform,min,max, ...)

#####T <- triangular <- function(min, mode, max, ...) env3.8(Striangular, min, mode, max, ...)
logtriangular <- function(min, mode, max, ...) env3.8(Slogtriangular, min, mode, max, ...)


poissonbinomial <- function(p, name='') {  # p is an array of (possibly different) probability values, which can be scalars or intervals
  # the distribution of the sum of independent Bernoulli trials, with possibly different probabilities of success p
  # support = 0:(length(p)), mean = sum(p), variance = sum(p(1-p))
  # poissonbinomial(p[1],p[2],p[3],...,p[n]) ~ binomial(n, p*) iff p[i]=p*, i=1,...n
  # http://en.wikipedia.org/wiki/Poisson_binomial_distribution, 8 May 2012
  # Wang, Y. H. (1993). "On the number of successes in independent trials". Statistica Sinica 3 (2): 295-312.
  if (class(p) != 'numeric') return(env(poissonbinomial(left(p)), poissonbinomial(right(p))))
  n = length(p)
  m = sum(p)
  v = sum(p*(1-p))
  Prk = rep(0,n+1)
  Prk[0+1] = prod(1-p)
  T <- function(i) sum((1/(1/p-1))^i)    #sum((p[j]/(1-p[j]))^i)
  Ti = rep(0,n)
  for (i in 1:n) Ti[i] = T(i)
  for (k in 1:n) {
    i = 1:k
    Prk[k +1] = (1/k) * sum((-1)^(i-1) * Prk[k-i +1] * Ti[i])
    }
  C = cumsum(Prk)
  u = d = rep(0,Pbox$steps)
  i = ii()
  j = jj()
  for (k in 1:n) u[C[k] <= i] = k
  for (k in 1:n) d[C[k] <= j] = k
  pbox(u, d, shape='Poisson Binomial', name=name, ml=left(m), mh=right(m), vl=left(v), vh=right(v))
  }

## testing poissonbinomial
#p = c(0.1, 0.2, 0.3, 0.4, 0.5)
#a = poissonbinomial(p)
#many = 10000
#s = rep(0,many)
#for (i in 1:length(p)) s = s + (runif(many) <= p[i])
#edf(s)
#
#p = rep(0.2, 20)
#a = poissonbinomial(p)
#b = binomial(20, 0.2)
#lines(a,col='blue')
#
#p = c(0.1, interval(0.2, 0.3), interval(0.4, 0.5))
#p1 = left(p)
#p2 = right(p)
#a = poissonbinomial(p)
#many = 10000
#s = rep(0,many)
#for (i in 1:length(p)) s = s + (runif(many) <= p1[i])
#s = rep(0,many)
#edf(s,col='tan')
#for (i in 1:length(p)) s = s + (runif(many) <= p2[i])
#edf(s,col='tan')




distr2pbox <- function(d, name=''){
  # we cannot WRITE p-boxes to the R-package "distr", because a single distribution cannot contain a p-box
  # I don't know how to check whether the class of d is a distr::Distribution (Norm, Pois, AbscontDistribution, etc.)
  if (!is.distr(d)) stop('distribution must be a "distr" object')
  ml <- -Inf
  mh <- Inf
  vl <- 0
  vh <- Inf
  try(ml <- mh <- E(d))
#  try(vl <- vh <- V(d))
  first <- 0;    if (q(d)(first) == -Inf) first <- Pbox$bOt
  last  <- 1;    if (q(d)(last)  == Inf)  last  <- Pbox$tOp
  i <- c(first, 1:(Pbox$steps-1) / Pbox$steps)                 # see distr::TruncQuantile
  j <- c(       1:(Pbox$steps-1) / Pbox$steps, last)
  pbox(u=q(d)(i), d=q(d)(j), shape='"distr"', name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

closest <- function(r, s) if (s<left(r)) return(left(r)) else if (right(r)<s) return(right(r)) else return(s)  # returns the value in the interval r that is closest to the scalar s

T <- triangular <- function(min, mode, max, ...){
  a <- left(min);   b <- right(min)
  c <- left(mode);  d <- right(mode)
  e <- left(max);   f <- right(max)
  if (c<a) c <- a   # implicit constraints
  if (e<c) e <- c
  if (f<d) d <- f
  if (d<b) b <- d
  # moments
  ml <- (a+c+e)/3 
  mh <- (b+d+f)/3 
  m <- closest(interval(c,d),(b+e)/2)
  if (e<=b) vl <- 0 else vl <- (b^2+m^2+e^2-(b*m+b*e+m*e))/18
  vh <- (a^2+f^2+max(c^2-(c*(a+f)+a*f), d^2-(d*(a+f)+a*f)))/18
  pbox(u=qtriangular(ii(), a, c, e), d=qtriangular(jj(), b, d, f), shape='triangular', ml=ml, mh=mh, vl=vl, vh=vh, ...)
  }

trapezoidal <- function(min, lmode, rmode, max, ...){
  a <- left(min);   b <- right(min)
  c <- left(lmode); d <- right(lmode)
  e <- left(rmode); f <- right(rmode)
  g <- left(max);   h <- right(max)
  if (c<a) c <- a   # implicit constraints
  if (e<c) e <- c
  if (g<e) g <- e
  if (h<f) f <- h
  if (f<d) d <- f
  if (d<b) b <- d
  # moments
  Strapezoidalmean <- function(a, b, c, d){
    ab <- a + b
    cd <- c + d
    if (nothing(cd-ab)) h <- 1 else h <- 1.0 / (3.0 * (cd - ab))
    return(h * (c * cd + d*d - (a * ab + b*b)))
    }
  Strapezoidalvar <- function(a, b, c, d){
    ab <- a + b
    cd <- c + d
    if (nothing(cd-ab)) h <- 1 else h <- 1.0 / (3.0 * (cd - ab))
    m <- h * (c * cd + d*d - (a * ab + b*b))
    if (nothing(d - a)) {
                  m <- a   
                  v <- 0.0
           } else v <- 0.5 * h * (cd * (c*c + d*d) -  ab * (a*a + b*b)) - m*m
    return(v)
    }
  ml <- Strapezoidalmean(a,c,e,g)
  mh <- Strapezoidalmean(b,d,f,h)
  if (g<=b) vl <- 0 else vl <- Strapezoidalvar(b,closest(lmode,(b+g)/2),closest(rmode,(b+g)/2),g)
  vh <- Strapezoidalvar(a,closest(interval(c,d),a),closest(interval(e,f),h),h)
  pbox(u=qtrapezoidal(ii(), a, c, e, g), d=qtrapezoidal(jj(), b, d, f, h), shape='trapezoidal', ml=ml, mh=mh, vl=vl, vh=vh, ...)
  }


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

MEquantiles <- pointlist

MEdiscreteminmax <- function(min,max) return(pmin(trunc(uniform(min,max+1)),max))

MEmeanvar <- function(mean, var) return(MEmeansd(mean,sqrt(var)))

MEminmaxmeansd <- function(min, max, mean, sd) return(beta1((mean- min) / (max - min),  sd/(max - min) ) * (max - min) + min)

MEmmms <- MEminmaxmeansd

MEminmaxmeanvar <- function(min, max, mean, var) return(MEminmaxmeansd(min,max,mean,sqrt(var)))


##########################################################################
# Method-of-Moment distribution constructors (match moments of the data x)
# N.B., these functions do not yet support intervals in the data x
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
# N.B., these functions do not yet support intervals in the data x
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


########################################
# Confidence boxes (c-boxes)
########################################

# x[i] ~ Bernoulli(CB), x[i] is either 0 or 1

NVbernoulli <- function(x) {n <- length(x); k <- sum(x); return(env(bernoulli(k/(n+1)), bernoulli((k+1)/(n+1))))}
CBbernoulli <- function(x) {n <- length(x); k <- sum(x); return(env(beta(k, n-k+1), beta(k+1, n-k)))}

# x[i] ~ binomial(N, p), for known N, x[i] is a nonnegative integer less than or equal to N

NVbinomial <- function(x,N) {n <- length(x); k<-sum(x); return(env(betabinomial(N,k,n*N-k+1),betabinomial(N,k+1, n*N-k)))}
CBbinomial <- function(x,N) {n <- length(x); k <- sum(x); return(env(beta(k, n*N-k+1), beta(k+1, n*N-k)))}

# x[i] ~ binomial(N, p), for unknown N, x[i] is a nonnegative integer

# see https://sites.google.com/site/cboxbinomialnp/
NVbinomialnp <- function(x) {stop('see https://sites.google.com/site/cboxbinomialnp/')}
CBbinomialnp.n <- function(x) {stop('see https://sites.google.com/site/cboxbinomialnp/')}
CBbinomialnp.p <- function(x) {stop('see https://sites.google.com/site/cboxbinomialnp/')}

# x[i] ~ Poisson(parameter), x[i] is a nonnegative integer

NVpoisson <- function(x) {n <- length(x); k = sum(x); return(env(negativebinomial(size=k, prob=1-1/(n+1)),negativebinomial(size=k+1, prob=1-1/(n+1))))}
CBpoisson <- function(x) {n <- length(x); k = sum(x); return(env(gamma(shape=k, rate=n),gamma(shape=k+1, rate=n)))}

# x[i] ~ exponential(parameter), x[i] is a nonnegative integer

NVexponential <- function(x) {n <- length(x); k = sum(x); return(gammaexponential(shape=n, rate=k))}
CBexponential <- function(x) {n <- length(x); k = sum(x); return(gamma(shape=n, rate=k))}

# x[i] ~ normal(mu, sigma)

NVnormal <- function(x) {n <- length(x); return(mean(x) + sd(x) * student(n - 1) * sqrt(1 + 1 / n))}
CBnormal.mu <- function(x) {n <- length(x); return(mean(x) + sd(x) * student(n - 1) / sqrt(n))}
CBnormal.sigma <- function(x) {n <- length(x); return(sqrt(var(x)*(n-1)/chisquared(n-1)))}

# x[i] ~ lognormal(mu, sigma), x[i] is a positive value whose logarithm is distributed as normal(mu, sigma)

NVlognormal <- function(x) {n <- length(x); return(exp(mean(log(x)) + sd(log(x)) * student(n - 1) * sqrt(1+1/n)))}
CBlognormal.mu <- function(x) {n <- length(x); return(mean(log(x)) + sd(log(x)) * student(n - 1) / sqrt(n))}
CBlognormal.sigma <- function(x) {n <- length(x); return(sqrt(var(log(x))*(n-1)/chisquared(n-1)))}

# x[i] ~ uniform(minimum, maximum), or
# x[i] ~ uniform(midpoint, width)

#NVuniform <- function(x) {n=length(x); w=(max(x)-min(x))/beta(length(x)-1,2); m=(max(x)-w/2)+(w-(max(x)-min(x)))*uniform(0,1); return(uniform(m-w/2, m+w/2))}
NVuniform <- function(x) {n=length(x); r=max(x)-min(x); w=(r/rbeta(1e4,length(x)-1,2))/2; m=(max(x)-w)+(2*w-r)*runif(1e4,0,1); return(histogram(runif(1e4,m-w, m+w),conf=0))}

CBuniform.minimum <- function(x) {n=length(x); w=(max(x)-min(x))/(1e-8+beta(length(x)-1,2)); m=(max(x)-w/2)+(w-(max(x)-min(x)))*uniform(0,1); return(m %|-|% w/2)}
CBuniform.maximum <- function(x) {n=length(x); w=(max(x)-min(x))/(1e-8+beta(length(x)-1,2)); m=(max(x)-w/2)+(w-(max(x)-min(x)))*uniform(0,1); return(m %|+|% w/2)}
CBuniform.width <- function(x) return((max(x)-min(x))/(1e-8+beta(length(x)-1,2)))
CBuniform.midpoint <- function(x) {w=(max(x)-min(x))/(1e-8+beta(length(x)-1,2)); return((max(x)-w/2)+(w-(max(x)-min(x)))*uniform(0,1))}

CBuniform.minimum <- function(x) {n=length(x); w=(max(x)-min(x))/((1/(2*max(x)))+beta(length(x)-1,2)); m=(max(x)-w/2)+(w-(max(x)-min(x)))*uniform(0,1); return(m %|-|% w/2)}
CBuniform.maximum <- function(x) {n=length(x); w=(max(x)-min(x))/((1/(2*max(x)))+beta(length(x)-1,2)); m=(max(x)-w/2)+(w-(max(x)-min(x)))*uniform(0,1); return(m %|+|% w/2)}
CBuniform.midpoint <- function(x) {w=(max(x)-min(x))/((1/(2*max(x)))+beta(length(x)-1,2)); return((max(x)-w/2)+(w-(max(x)-min(x)))*uniform(0,1))}
CBuniform.width <- function(x) return((max(x)-min(x))/((1/(2*max(x)))+beta(length(x)-1,2)))

# in progress testing
#x = runif(200, 15,30)
#a = CBuniform.minimum(x)
#b = CBuniform.maximum(x) 
#c = CBuniform.midpoint(x)
#d = CBuniform.width(x) 
#edf(x,new=TRUE,xlim=c(5,40))
#black(a)
#black(b)
#red(c)
#blue(d)


# x[i] ~ F, a continuous but unknown distribution

NVnonparametric <- function(x) return(env(histogram(c(x, Inf), conf=0), histogram(c(x, -Inf), conf=0)))

# x[i] ~ normal(mu1, sigma1), y[j] ~ normal(mu2, sigma2), x and y are independent

CBnormal.meandifference <- function(x, y) CB.normal.mu(x) - CB.normal.mu(y)

# x[i] = Y + error[i],  error[j] ~ F,  F unknown,  Y fixed,  x[i] and error[j] are independent

CBnonparametric <- function(x, error) {# i.e., the c-box for Y
    z = NULL
    for(jj in 1:length(error)) z = c(z, y - error[jj])
    z = sort(z)
    Q = Get_Q(length(y), length(error))
    w = Q / sum( Q )
    env(mixture(z,w), mixture(c(z[-1],Inf),w))
    }    


########################################
# Distribution-free p-box constructors #
########################################

# must be able to accept interval arguments

minmax <- function(min, max, name=''){
  pbox(u=rep(min,Pbox$steps), d=rep(max,Pbox$steps), shape='{min, max}', name=name, ml=min, mh=max, vl=0, vh=(max-min)^2/4)
  }

# must be able to accept interval arguments

#minmaxmean <- function(a,b,c) return(mmms(a,b,c,(b-a)^2/4))

minmaxmean <- function(min, max, mean, name=''){
  mid = (max - mean) / (max - min)
  p <- ii()           
  u = ifelse(p <= mid, min, (mean - max) / p + max)
  p <- jj()
  d <- ifelse(mid <= p, max, (mean - min * p) / (1 - p))
  pbox(u=u, d=d, shape='{min, max, mean}', name=name, ml=mean, mh=mean, vl=0, vh=(max-min)*(max-mean)-(max-mean)*(max-mean))
  }

# must be able to accept interval arguments

minmean <- function(min, mean, name=''){
  p <- jjj()
  d <- ((mean - min) / (1-p)) + min
  pbox(u=rep(min,Pbox$steps), d=d, shape='{min, mean}', name=name, ml=mean, mh=mean, vl=0, vh=Inf)
  }

# must be able to accept interval arguments

meanstd <- function(mean, std, name=''){
  p <- iii()         
  u <- mean - std * sqrt(1/p - 1) 
  p <- jjj()
  d <- mean + std * sqrt(p / (1 - p))
  pbox(u=u, d=d, shape='{mean, std}', name=name, ml=mean, mh=mean, vl=std^2, vh=std^2)
  }

meanvar <- meanvariance <- function(mean, var, name='') meanstd(mean, sqrt(var), name)

# must be able to accept interval arguments

posmeanstd <- function(mean, std, name=''){
  p <- ii()          
  u <- pmax(0,mean - std * sqrt(1/p - 1))
  p <- jjj()
  d <- pmin(mean / (1 - p), mean + std * sqrt(p / (1 - p)))
  pbox(u=u, d=d, shape='{positive, mean, std}', name=name, ml=mean, mh=mean, vl=std^2, vh=std^2)
  }

# must be able to accept interval arguments

minmaxmode <- function(min, max, mode, name=''){
  p <- ii()
  u <- p * (mode - min) + min;
  p <- jjj()
  d <- p * (max - mode) + mode
  ml <- (min+mode)/2
  mh <- (mode+max)/2
  vl <- 0
  vh <- (max-min)*(max-min)/12
  pbox(u=u, d=d, shape='{min, max, mode}', name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

# must be able to accept interval arguments

minmaxmedian <- function(min, max, median, name=''){
  p <- ii()       
  u <- rep(median, Pbox$steps)
  u[p <= 0.5] <- min
  p <- jjj()
  d <- rep(median, Pbox$steps)
  d[0.5 < p] <- max
  ml <- (min + median)/2
  mh <- (median + max)/2
  vl <- 0
  vh <- (max - min) * (max - min) / 4
  pbox(u=u, d=d, shape='{min, max, median}', name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

# must be able to accept interval arguments

minmaxmedianismode <- function(min, max, m, name=''){
  p <- ii()
  u <- rep(m, Pbox$steps)
  u[p <= 0.5] <- p[p <= 0.5] * 2.0 * (m - min) + min
  p <- jjj()
  d <- rep(m, Pbox$steps)
  d[0.5 < p] <- (p[0.5 < p] - 0.5) * 2.0 * (max - m) + m
  ml <- (min + 3 * m) / 4
  mh <- (3 * m + max) / 4
  vl <- 0
  vh <- (max - min) * (max - min) / 4
  pbox(u=u, d=d, shape='{min, max, median=mode}', name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

# must be able to accept interval arguments

minmaxpercentile <- function(min, max, fraction, percentile, name=''){
  p <- ii()
  u <- rep(percentile, Pbox$steps)
  u[p <= fraction] <- min
  p <- jjj()
  d <- rep(percentile, Pbox$steps)
  d[fraction < p] <- max
  ml <- fraction * min + (1 - fraction) * percentile
  mh <- fraction * percentile + (1 - fraction) * max
  vl <- 0
  vh <- (max - min) * (max - min) / 4
  pbox(u=u, d=d, shape='{min, max, percentile}', name=name, ml=ml, mh=mh, vl=vl, vh=vh)
  }

# must be able to accept interval arguments

symmeanstd <- function(mean, std, name=''){
  p <- iii()
  u <- rep(mean,Pbox$steps)
  u[p <= 0.5] <- mean - std / sqrt(2 * p[p <= 0.5])
  p <- jjj()
  d <- rep(mean, Pbox$steps)
  d[0.5 < p] <- mean + std / sqrt(2 * (1 - p[0.5 < p]))
  pbox(u=u, d=d, shape='{symmetric, mean, std}', name=name, ml=mean, mh=mean, vl=std^2, vh=std^2)
  }

# must be able to accept interval arguments

maxmean <- function(max, mean, name='') pbox(negate.pbox(minmean(-(max),-(mean))),name=name)

# this mmms function is not correct (it's missing the Berleant-Myers correction); it's also not intervalized...which should be env of (left mean, RIGHT sd) and (right mean, RIGHT sd)
mmms <- function(min,max,mean,std, name='') pbox(imp.pbox(meanstd(mean,std),imp.pbox(minmean(min,mean), maxmean(max,mean))),ml=left(mean), mh=right(mean), vl=left(std)^2,vh=right(std)^2,name=name)

mmmv <- function(a,b,c,d) return(mmms(a,b,c,sqrt(d)))

uniminmax <- function(min,max,mode, name='') pbox(mode + conv.pbox(U(0,1), minmax(min-mode,max-mode), '*'),name=name)

# the following version should be used when interval parameters are supported
unimmmv <- function(min, max, mean, var, mode, name='') {
  pbox(
    imp.pbox(
        mmms(min,max,mean,sqrt(bigger.interval(0, var))),
        mode+conv.pbox(
                        U(0,1),
                        mmms(min-mode,max-mode,2*(mean-mode),sqrt(bigger.interval(0, 3*var-(mean-mode)^2)))
                       )
        )
    ,name=name
    )
  }

unimmmv <- function(min, max, mean, var, mode, name='') {
  #cat('entering unimmmv\nmin:',min,'\nmax:',max,'\nmean:',mean,'\nvar:',var,'\nmode:',mode,'\n')
  #A <- mmms(min,max,mean,sqrt(var))
  #show(A)
  #B <- U(0,1)
  #E <- mmms(min-mode,max-mode,2*(mean-mode),sqrt(3*var-(mean-mode)^2)) 
  #cat('conv.pbox(B,E):')
  #F <- conv.pbox(B,E,'*')
  #show(F)
  #cat('mode+conv.pbox:')
  #G <- mode+F
  #show(G)
  #cat('imp.pbox:')
  #H <- imp.pbox(A,G)
  #show(H)
  pbox(
           imp.pbox(
                     mmms(min,max,mean,sqrt(var)),
                     mode+conv.pbox(
                                    U(0,1),
                                    mmms(min-mode,max-mode,2*(mean-mode),sqrt(3*var-(mean-mode)^2)) 
                                   , '*')
                   )
           ,name=name
          )
  }

# must be able to accept interval arguments

unimmms <- function(min, max, mean, std, mode, name='') unimmmv(min, max, mean, std^2, mode, name=name)

# must be able to accept interval arguments

unimodal <- unimodal.pbox <- function(pb,mode) imp.pbox(pb, unimmms(left(pb),right.pbox(pb),mean.pbox(pb),sd.pbox(pb), mode))

# must be able to accept interval arguments

minmaxmeanismedian <- function(min, max, m, name='') pbox(imp.pbox(minmaxmean(min,max,m), minmaxmedian(min,max,m)),name=name)

# must be able to accept interval arguments

minmaxmeanismode <- function(min, max, m, name='')  pbox(unimodal.pbox(minmaxmean(min,max,m),m),name=name)

whatIknow <- function(    # NOT BEST POSSIBLE 
  min=NULL,
  max=NULL,
  mean=NULL,
  median=NULL,
  mode=NULL,              # implies unimodality too
  std=NULL,
  var=NULL,
  cv=NULL,
  percentiles=NULL,       # array of pairs (percentage, percentile)
  coverages=NULL,
  shape=NULL,             # array of strings that might include 'unimodal', 'symmetric', 'positive' (implies min), 'nonnegative' (implies min), 'concave', 'convex', 'increasinghazard', 'decreasinghazard', 'discrete', 'integervalued', 'continuous', '', '', '', '', 'normal', 'lognormal', etc.
  data=NULL,              # data alone evokes KS confidence bands, data with a named shape evokes the Chen & Iles confidence bands 
  confidence=0.95,
  dependencies=NULL,
  #units=NULL,
  ..., debug=FALSE) {
  #pb <- pbox(dep=dependencies) #, units=units)
  pb <- pbox(dids=dependencies) #, units=units)
  plotting <- c(Pbox$plotting, Pbox$plotting.every)
  Pbox$plotting <- FALSE
  Pbox$plotting.every <- FALSE
  tryCatch( {
  if ('positive' %in% shape)     if (missing(min)) min <- 0 else min <- pmax(min,0)     # should be 0+ (zeroplus) if we had infinitessimals
  if ('nonnegative' %in% shape)  if (missing(min)) min <- 0 else min <- pmax(min,0)
  if (debug) cat('1 ')
  if (present(mode))             shape <- c(shape, 'unimodal')
  if (debug) cat('2 ')
  if (present(min,max))          try(pb <- c(pb,minmax(min,max)))
  if (debug) cat('3 ')
  if (present(min,mean))         try(pb <- c(pb,minmean(min,mean)))
  if (debug) cat('4 ')
  if (present(max,mean))         try(pb <- c(pb,negate(minmean(-max,-mean))))
  if (debug) cat('5 ')
  if (present(min,max,mean))     try(pb <- c(pb,minmaxmean(min,max,mean)))
  if (debug) cat('6 ')
  if (present(min,max,mode))     try(pb <- c(pb,minmaxmode(min,max,mode)))
  if (debug) cat('7 ')
  if (present(min,max,median))   try(pb <- c(pb,minmaxmedian(min,max,median)))
  if (debug) cat('8 ')
  if (present(min,mean,std))     try(pb <- c(pb,min+posmeanstd(mean-min,std)))
  if (debug) cat('9 ')
  if (present(max,mean,std))     try(pb <- c(pb,negate(-max+posmeanstd(-mean+max,std))))
  if (debug) cat('10 ')
  if (present(min,max,mean,std)) try(pb <- c(pb,mmms(min,max,mean,std)))
  if (debug) cat('11 ')
  if (present(min,max,mean,var)) try(pb <- c(pb,mmms(min,max,mean,sqrt(var))))
  if (debug) cat('12 ')
  if (present(mean,std))         try(pb <- c(pb,meanstd(mean,std)))
  if (debug) cat('13 ')
  if (present(mean,cv))          try(pb <- c(pb,meanstd(mean,mean*cv)))
  if (debug) cat('14 ')
  
  if (debug) cat('15 ')
  #minmaxpercentile
  if (debug) cat('16 ')
  
  if (debug) cat('17 ')
# if ('unimodal' %in% shape) { if (!present(mode)) mode <- interval()
  if (debug) cat('18 ')
  if ('unimodal' %in% shape && present(mode)) {
  if (debug) cat('19 ')
    if (present(min,max))          try(pb <- c(pb, uniminmax(min,max,mode)))
  if (debug) cat('20 ')
    if (present(min,max,mean,std)) try(pb <- c(pb, unimmms(min,max,mean,std,mode)))
  if (debug) cat('21 ')
    if (present(min,max,mean,var)) try(pb <- c(pb, unimmmv(min,max,mean,var,mode)))
  if (debug) cat('22 ')
    # can I not otherwise use naked unimodality?
  if (debug) cat('23 ')
    }
  if (debug) cat('24 ')

  if (debug) cat('25 ')
  if ('symmetric' %in% shape && present(mean,std))                     try(pb <- imp(pb,symmeanstd(mean,std)))
  if (debug) cat('26 ')

  if (debug) cat('27 ')
  if (present(min,max,mean,median) && isTRUE(all.equal(mean,median))) try(pb <- c(pb, minmaxmeanismedian(min,max,mean)))
  if (debug) cat('28 ')
  if (present(min,max,mean,mode)   && isTRUE(all.equal(mean,mode)))   try(pb <- c(pb, minmaxmeanismedian(min,max,mean)))
  if (debug) cat('29 ')
  if (present(min,max,median,mode) && isTRUE(all.equal(median,mode))) try(pb <- c(pb, minmaxmedianismode(min,max,median)))
  if (debug) cat('30 ')
  
  if (debug) cat('31 ')
  if ('normal' %in% shape)       try(pb <- c(pb,normal(mean=mean,std=std,var=var,cv=cv,median=median,mode=mode,...)))
  if (debug) cat('32 ')
  if ('lognormal' %in% shape)    try(pb <- c(pb,lognormal(mean=mean,std=std,var=var,cv=cv,median=median,mode=mode...)))
  if (debug) cat('33 ')
    }, finally = {
                  Pbox$plotting <- plotting[[1]]
                  Pbox$plotting.every <- plotting[[2]]
                  if (Pbox$plotting) try(plot.pboxlist(pb))
                 })
  pb
  }

known <- function(...) imp.pbox(whatIknow(...))

###############################
# Functions to import p-boxes #
###############################

scanint <- function(s) {
  m <- unlist(strsplit(s, "\\,"))
  c(as.numeric(substr(m[1],2,100)),   as.numeric(substr(m[2],1,nchar(m[2])-1)))
  }

read <- read.pbox <- function(fn, many=100, multiple=FALSE) {
  headers <- 3
  t <- scan(fn, what='', nlines=3, sep ='\n', quiet=TRUE)
  # units follow the string '; Units: ' in t[[2]]
  if ((t[[1]] != '; Risk Calc version 4.0') || (t[[3]] != '; Type: RANDOM')) stop('file does not contain a p-box')
  s <- scan(fn,what = list(0,0,0), skip=headers, nlines =100, quiet=TRUE)
  z <- scan(fn, what='', skip=many+headers, quiet=TRUE)
  m <- scanint(z[[2]])
  v <- scanint(z[[3]])
  if (multiple) {
                  if (Pbox$steps %% many != 0) stop('eek')
                  dup <- Pbox$steps %/% many 
                  u <- rep(unlist(s[2]),rep(dup,many))
                  d <- rep(unlist(s[3]),rep(dup,many))
                } else {
                  i <- round(seq(from=1,to=many,length.out=Pbox$steps))
                  u <- unlist(s[2])[i]
                  d <- unlist(s[3])[i]
                }
  shape <- RCdistributionName(as.integer(z[[1]]))  
  pbox(u=u, d=d, shape=shape, name=fn, ml=m[1], mh=m[2], vl=v[1], vh=v[2]) 
  }

# numeric codes for distribution shapes used in Risk Calc export files
RCdistribcodenames <- c(
  c(0, 'beta'),
  c(1, 'Cauchy'),
  c(2, 'chi-squared'),
  c(2, 'X2'),
  c(3, 'delta'),
  c(3, 'Dirac'),
  c(4, 'exponential'),
  c(5, 'F'),
  c(5, 'Fisher-Snedecor'),
  c(6, 'Frechet'),
  c(6, 'Frechet'),
  c(7, 'gamma'),
  c(7, 'Erlang'),
  c(8, 'geometric'),
  c(8, 'Pascal'),
  c(9, 'Gumbel'),
  c(9, 'Fisher-Tippett'),
  c(10, 'histogram'),
  c(10, 'empirical'),
  c(10, 'custom'),
  c(11, 'Laplace'),
  c(11, 'double exponential'),
  c(12, 'logistic'),
  c(13, 'lognormal'),
  c(14, 'logtriangular'),
  c(15, 'loguniform'),
  c(16, 'loguniform'),
  c(17, 'normal'),
  c(17, 'Gaussian'),
  c(18, 'Pareto'),
  c(19, 'power function'),
  c(20, 'Rayleigh'),
  c(21, 'reciprocal'),
  c(22, 'Student t'),
  c(22, 't'),
  c(23, 'triangular'),
  c(23, 'Simpson'),
  c(24, 'trapezoidal'),
  c(25, 'uniform'),
  c(25, 'rectangular'),
  c(26, 'Wakeby'),
  c(27, 'Weibull'),
  c(28, 'Bernoulli'),
  c(29, 'binomial'),
  c(30, 'Poisson'),
  c(31, 'discrete uniform'),
  c(32, 'hypergeometric'),
  c(33, 'negative hypergeometric'),
  c(34, 'logarithmic series'),
  c(35, 'negative binomial'),
  c(36, '{min, max}'),
  c(37, '{min, max, mean}'),
  c(38, '{min, mean}'),
  c(39, '{mean, stddev}'),
  c(40, '{min, max, median}'),
  c(41, '{min, max, mode}'),
  c(42, '{min, max, mean is median}'),
  c(43, '{min, max, mean is mode}'),
  c(44, '{min, max, median is mode}'),
  c(45, '{min, max, percentile}'),
  c(46, '{min, max, pos, mean, stddev}'),
  c(47, '{sym, mean, stddev}'),
  c(48, ''),
  c(49, 'UNKNOWN1'),
  c(50, 'UNKNOWN2'),
  c(51, 'UNKNOWN3'),
  c(52, ''),
  c(53, ''),
  c(54, 'ERROR'),
  c(55, 'quadratic'),
  c(56, 'U-quadratic'),
  c(57, 'inverse gamma'),
  c(58, 'Wilcoxon'),
  c(59, 'beta-binomial'),
  c(60, 'generalized extreme value'),
  c(61, 'Kumaraswamy'),
  c(62, 'Skellam'),
  c(63, 'Voigt'),
  c(64, 'hyperbolic secant'),
  c(65, 'Cantor'),

  c(66, 'Bradford'),
  c(67, 'Burr'),
  c(68, 'Fisk'),
  c(69, 'loglogistic'),

  c(70, 'skew-normal'),
  c(71, 'arc sine'),
  c(72, 'arc tangent'),
  c(73, 'Benford'),
  c(74, 'chi'),
  c(75, 'exponential-power'),
  c(76, 'shifted loglogistic'),
  c(77, 'Lomax'),
  c(78, 'Muth'),
  c(79, 'Dagum'),
  c(80, ''),
  c(81, ''),
  c(82, ''),
  c(83, ''),
  c(84, ''),
  c(85, ''),
  c(86, ''),
  c(87, ''),
  c(88, ''),
  c(89, ''),
  c(90, ''),
  c(91, ''),
  c(92, ''),
  c(93, ''),
  c(94, ''),
  c(95, ''),
  c(96, ''),
  c(97, ''),
  c(98, ''),
  c(99, ''),
  c(100, '{pbox}'))

RCdistribdirectory <- matrix(RCdistribcodenames,nrow=2)

RCdistributionCode <- function(distribname)
  RCdistribdirectory[[1,match(distribname,RCdistribdirectory)/2]]

RCdistributionName <- function(distribcode)
  RCdistribdirectory[[2,match(distribcode,RCdistribdirectory)/2+1]]


##########################################################################################################
# P-box for the confidence distribution on a proportion given k successes out of n trials;  error if n<k #
##########################################################################################################

balchbox.0 = function(trials, successes, name='') {               # original formulation
  if ((successes==0) && (trials==0)) return(pbox(0,1,shape='beta',name=name)) else
  if (successes==trials) return(pbox(u=qbeta(ii(), successes, trials-successes+1),d=1,shape='beta',name=name)) else
  if (successes==0) return(pbox(u=0,d=qbeta(jj(), successes+1,trials-successes),shape='beta',name=name)) else
  pbox(u=qbeta(ii(), successes, trials-successes+1),d=qbeta(jj(), successes+1,trials-successes),shape='beta',name=name)
  }

balchbox <- function(n, k, name='') {                             # better moments
  if ((k==0) && (n==0)) return(pbox(0,1,shape='beta',name=name))  # could be interval(0,1)
  if (k==n) return(pbox(env(beta(k, n-k+1),1),name=name))
  if (k==0) return(pbox(env(0,beta(k+1,n-k)),name=name))
  return(pbox(env(beta(k, n-k+1),beta(k+1,n-k)),name=name))
  }

balchbox = function(n, k, name='') {                              # slightly faster
  if (n<k) stop('The value of n (',n,') must be larger than or equal to k (',k,') in balchbox')
  uu = function() qbeta(ii(), k, n-k+1)
  dd = function() qbeta(jj(), k+1,n-k)
  if ((k==0) && (n==0)) {u=0;    d=1 }   else
  if (k==n)             {u=uu(); d=1}    else
  if (k==0)             {u=0;    d=dd()} else 
                        {u=uu(); d=dd()}
  pbox(u=u,d=d,shape='beta',name=name)
  }

balch.ci <- function(b,p1=0.025,p2=1-p1) interval(left(cut(b,p1)), right(cut(b,p2)))

nk <- function(n, k, name='') {   # beta-binomial p-box implied by k successes out of n trials                         
  if ((k==0) && (n==0)) return(pbox(0,1,shape='beta-binomial',name=name))  # could be interval(0,1)
  if (k==n) return(pbox(env(BB(k, n-k+1, n), n),name=name))
  if (k==0) return(pbox(env(0,BB(k+1, n-k, n)),name=name))
  return(pbox(env(BB(k, n-k+1, n),BB(k+1, n-k, n)),name=name))
  }

################################################################################## 
# Subinterval Reconstitution 
################################################################################## 

partition <- function(m,A) {
  i = 1:m
  w = width.interval(A)
  lA = left(A)
  a = NULL
  for (i in 1:m) a = c(a, interval((i - 1)*w/m + lA,  i*w/m + lA))
  a
  }

sir <- function(m,f,A) {
  i = 1:m
  w = width.interval(A)
  lA = left(A)
  lo = Inf
  hi = -Inf
  for (i in 1:m) {
    a = interval((i - 1)*w/m + lA,  i*w/m + lA)
    e = f(a)
    lo = base::min(lo, left(e))
    hi = base::max(hi, right(e))
    }
  interval(lo,hi)
  }


################################################################################## 
# Backcalculation 
################################################################################## 

backcalc <- function(A, C) return(interval(left(C) - left(A), right(C) - right(A)))

factor <- function(A, C) return(interval(left(C) / left(A), right(C) / right(A)))


################################################################################## 
# Cauchy deviate simulation 
################################################################################## 

cds = function(n,f,a) { #  a is a concatenation of intervals
  x1 = x2 = NULL
  for (i in 1:length(a)) {
    x1 = c(x1, left(a[[i]]))
    x2 = c(x2, right(a[[i]]))
    }
  xtilda = (x1 + x2) / 2
  Delta = (x2 - x1) / 2
  del = NULL
  ytilda = f(xtilda)
  for (k in 1:n) {
    r = runif(length(a),0,1)
    c = tan(base::pi*(r-0.5))
    K = max(c)
    delta = Delta * c / K
    x = xtilda - delta
    del = c(del, K * (ytilda - f(x)))
    }
  Z = function(Del) return( n/2 - sum(1/(1 + (del / Del)^2 )))
  Del = uniroot(Z,c(0,max(del)))
  return(list(Del$root, ytilda-Del$root, ytilda+Del$root, Del$f.root, Del$iter, Del$estim.prec))
  }


######################################################################
# Exporting, writing, printing, plotting, summary, and str functions #
######################################################################

sayint <- function(l,h=NULL,...) { # print(l); print(h) ; if (missing(l)) stop('no args')
  #print('111111111111')
  #print(l)
  #print('222222222222')
  #print(h)
  #print('333333333333')
  if (is.null(h) & length(l)==2) {h <- l[[2]]; l <- l[[1]] }
  if (l==h) h else paste('[',format(l,...),',',format(h,...),']',sep='')
  }

sayint <- function(i,...) { 
  l <- i@lo
  h <- i@hi
  if (isTRUE(all.equal(l,h))) h else paste('[',format(l,...),',',format(h,...),']',sep='')
  }

#width.interval <- function(x) x[[2]] - x[[1]] #obsolete

if(!isGeneric("edf")) quiet <- setGeneric("edf", function(x, ...) standardGeneric("edf"))
quiet <- setMethod('edf', 'pbox', function(x, ...) edf.pbox(x,...))
quiet <- setMethod('edf', 'numeric', function(x, ...) edf.numeric(x,...))

summary.pbox <- function (object, ...) {
  if (!is.pbox(object)) stop('object is not a p-box')
  ans <- list(name='', shape='', mean='', variance='', sd='', iqr='', iqr.width=0, range='', left=0, 
   percentile.01='', percentile.05='', percentile.25='', median='',
   percentile.75='', percentile.95='', percentile.99='', right=0, discretizations=0)
  N <- object@n
  ans$name             <- object@name
  ans$shape            <- object@shape
  ans$mean             <- mean.pbox(object)
  ans$variance         <- var.pbox(object)
  ans$sd               <- sd.pbox(object)
  ans$iqr              <- iqr.pbox(object)
  ans$iqr.width        <- width.interval(iqr.pbox(object))
  ans$range            <- range.pbox(object)
  ans$left             <- object@u[[1]]
  ans$percentile.01    <- cut(object, 0.01)
  ans$percentile.05    <- cut(object, 0.05)
  ans$percentile.25    <- cut(object, 0.25)
  ans$median           <- cut(object, 0.50)
  ans$percentile.75    <- cut(object, 0.75)
  ans$percentile.95    <- cut(object, 0.95)
  ans$percentile.99    <- cut(object, 0.99)
  ans$right            <- object@d[[N]]
  ans$discretizations  <- N
  class(ans)           <- "summary.pbox"
  ans
  }

# specify other args by calling this DIRECTLY. as "print.summary.pbox(summary.pbox(x), digits=4)"
# how do I get the generic(?) function "summary(x)" to pass along the extra args?
print.summary.pbox <- function(x, ...) {  
  replaceempty <- function(s,r) if (s=='') r else s
  cat('\nP-box summary',
      '\n  Name: ',replaceempty(x$name,'<none>'),
      '\n  Shape: ',replaceempty(x$shape,'<unknown>'),
      '\n  Mean: ',sayint(x$mean,...),
      '\n  Variance: ',sayint(x$variance,...),
      '\n  Std Deviation: ',sayint(x$sd,...),
      '\n  Interquartile range: ',sayint(x$iqr,...),
      '\n  Interquartile width: ',format(x$iqr.width,...),
      '\n  Support range: ',sayint(x$range,...),
      '\n  Order statistics',
      '\n    Left (min) value: ',format(x$left,...),
      '\n    1st percentile: ', sayint(x$percentile.01,...),
      '\n    5th percentile: ', sayint(x$percentile.05,...),
      '\n    25th percentile: ', sayint(x$percentile.25,...),
      '\n    Median (50th%ile): ', sayint(x$median,...),
      '\n    75th percentile: ', sayint(x$percentile.75,...),
      '\n    95th percentile: ', sayint(x$percentile.95,...),
      '\n    99th percentile: ', sayint(x$percentile.99,...),
      '\n    Right (max) value: ', format(x$right,...),
      '\n  Discretization Pbox$steps: ', x$discretizations,
      '\n',sep = '')
  invisible(x)
  }

write.pbox <- function(x, filename, many=100, confirm=FALSE) {
  w <- rep('',3+100+1)
  w[[1]] <- '; Risk Calc version 4.0'
  w[[2]] <- '; Units: '
  w[[3]] <- '; Type: RANDOM'
  j <- seq(from=1,to=length(x@u),length.out=many)
  for (i in 1:many) 
  w[[3+i]] <- paste(i-1, x@u[j[i]], x@d[j[i]], sep=' ')
  # Risk Calc requires the interval brackets, so don't use the sayint function in the next line
  w[[3+many+1]] <- paste(RCdistributionCode(x@shape), ' [',x@ml, ',', x@mh,'] [',x@vl, ',', x@vh,']', sep='')
  write(w, file=filename, sep='\n')
  if (confirm) cat("Writing p-box to",filename,'\n')
  }

if(!isGeneric("write")) quiet <- setGeneric("write", function (x, file = "data", ncolumns = if (is.character(x)) 1 else 5, 
    append = FALSE, sep = " ") standardGeneric("write"))
quiet <- setMethod('write', 'pbox', function(x, file = 'data', ncolumns = if (is.character(x)) 1 else 5, 
    append = FALSE, sep = " ") write.pbox(x, file))

print.mean <- function(x) cat(sayint(mean(x)), '\n')    #x@ml, x@mh),'\n')

print.var <- function(x) cat(sayint(var.pbox(x)), '\n')    #x@vl, x@vh),'\n')

print.sd <- function(x) cat(sayint(sd(x)), '\n')    #sqrt(x@vl), sqrt(x@vh)),'\n')

as.character.pbox <- function(x, ...) {
  paste(sep='','P-box: ',x@name,' ~ ',x@shape,'( range=',sayint(range(x)),', mean=',sayint(mean(x)),', var=',sayint(var.pbox(x)),')')
  }

print.pbox <- function(x, ...) cat(as.character.pbox(x, ...),'\n')

show.pbox <- function(x, ...) {
  try(plot.pbox(x, ...))
  print.pbox(x)
  }
 
quiet <- setMethod("show", "pbox", function(object)show.pbox(object))
 
updown <- function(cumulative, x) if (cumulative) x else 1-x

cumulative <- function(yes=TRUE) Pbox$cumulative <- yes

plot.pbox <- function(s,name=NULL,cumulative=Pbox$cumulative, col=NULL, ...) {
  if (!is.vacuous(s)) {
    if (missing(name)) name <- s@name
    i = 0:(s@n-1) / s@n
    if (cumulative) ylab = 'Cumulative probability' else ylab = 'Exceedance probability'
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
    if (.Platform$OS.type=='windows') if(!RStudio) bringToTop(-1) # return focus to R console
    }}

lines.pbox <- points.pbox <- superplot.pbox <- function(s,name='',cumulative=Pbox$cumulative, col=NULL,...) {
  i = 0:(s@n-1) / s@n
  if (is.null(col)) color <- 'red' else color <- col
  lines(c(s@u,s@u[[s@n]],s@d[[s@n]]),updown(cumulative,c(i,1,1)),type="S", col=color, ...)
  i = 1:(s@n) / s@n
  if (is.null(col)) color <- 'black'
  lines(c(s@u[1],s@d[1],s@d),updown(cumulative,c(0,0,i)),type="s", col=color, ...)
  if (.Platform$OS.type=='windows') if(!RStudio) bringToTop(-1) # return focus to R console
  }

plot.pbox.scale <- function(min, max, name='',cumulative=Pbox$cumulative, col=NULL, ...) {
  if (cumulative) ylab = 'Cumulative probability' else ylab = 'Exceedance probability'
  plot(c(min,max),c(0,1),xlab=name, ylab=ylab, col='white', ...)
  }

plot.pboxlist <- function(A,...) {
  rm <-  Inf; for (i in 1:length(A)) {r <-  left(A[[i]]); if (is.finite(r)) rm <- base::min(r,rm) }
  rM <- -Inf; for (i in 1:length(A)) {r <- right(A[[i]]); if (is.finite(r)) rM <- base::max(r,rM) }
  if ("xlim" %in% attributes(list(...))$names) plot.pbox.scale(list(...)$xlim[1],list(...)$xlim[2],...) else plot.pbox.scale(rm, rM, ...)    
  for (i in 1:length(A)) lines(A[[i]], ...)
  }

################################################################################## 
# Plotting intervals
################################################################################## 

# width <- function(x) return(right(x)-left(x))

# range.interval <- function(x, na.rm = FALSE) return(c(left(x), right(x)))

plot.interval <- function(x, new=TRUE, shape='R', xlim=range.interval(x), ylim=c(0,1), xlab=substitute(x), ylab='', ...) {
  if (new) plot(NULL,NULL, xlim=xlim, ylim=ylim, xlab=xlab, ylab=ylab, ...)
  lx = left(x)
  rx = right(x)
  if (shape=='A') {
    x = seq(lx,rx,length.out=50)
    m = (lx+rx)/2
    y = sqrt(max(x-m)^2-(x-m)^2)
    y = y / max(y)
    lines(x,y, ...)
    } else if (shape=='T') lines(c(seq(lx,rx,length.out=3),lx), c(0,1,0,0), ...) else lines(c(lx,rx,rx,lx,lx), c(0,0,1,1,0), ...)
  }

lines.interval <- function(x, shape='R', ...) {
  lx = left(x)
  rx = right(x)
  if (shape=='A') {
    x = seq(lx,rx,length.out=50)
    m = (lx+rx)/2
    y = sqrt(max(x-m)^2-(x-m)^2)
    y = y / max(y)
    lines(x,y, ...)
    } else if (shape=='T') lines(c(seq(lx,rx,length.out=3),lx), c(0,1,0,0), ...) else lines(c(lx,rx,rx,lx,lx), c(0,0,1,1,0), ...)
  }

# plot array of intervals
plotem <- function(..., xlab='',ylab='',xlim=NULL,ylim=c(0,1),shape='A',col='black') {
  a = c(...)
  if (is.null(xlim)) {
    m = left(a[[1]])
    M = right(a[[1]])
    for (i in 2:length(a)) {
      m = base::min(m, left(a[[i]]))
      M = base::max(M, right(a[[i]]))
      }
    xlim=c(m,M)
    }
  plot(NULL,NULL, xlim=xlim,ylim=ylim,xlab=xlab,ylab=ylab)
  for (i in 1:length(a)) plot.interval(interval(a[[i]]),new=FALSE,shape=shape,col=col)
  }


##########################################
# Validation functions
##########################################

disagree.numeric <- function(a,b) abs(a-b)
disagree.sinterval <- function(a,b,c,d) pmax(c-b, a-d, 0)
disagree.interval <- function(a,b) disagree.sinterval(a@lo,a@hi, b@lo,b@hi)
disagree.pbox <- function(a,b) sum(disagree.sinterval(a@u,a@d,b@u,b@d))/Pbox$steps


##########################################
# Make a p-box from Michael's Dempster-Shafer format
##########################################

pbox.ds <- function(ds) {   # convert from Michael's Dempster-Shafer format
  k <- length(ds)/3
  w <- ds[,3]
  if (k != length(w)) stop('Need same number of weights as focal elements')
  w = w / sum(w)
  u <- d <- NULL
  for (i in 1:k) {
    u <- c(u,ds[[i,1]])
    d <- c(d,ds[[i,2]])
    }
  su = sort(u); su = c(su[[1]],su)
  pu = c(0,cumsum(w[order(u)]))
  sd = sort(d); sd = c(sd,sd[[length(sd)]])
  pd = c(cumsum(w[order(d)]),1)
  u = d = NULL
  j = length(pu)
  for (p in rev(ii())) {
    repeat {if (pu[[j]] <= p) break; j = j - 1}
    u = c(su[[j]],u)
    }
  j = 1
  for (p in jj()) {
    repeat {if (p <= pd[[j]]) break; j = j + 1}
    d = c(d,sd[[j]])
    }
  pbox(u,d)
  }


##########################################################################################################
# Balch's routines to create a Dempster-Shafer structure for the nonparametric difference
##########################################################################################################

m_Q_glbl = 10  # stub of the memoized table of pre-computed coefficients

Q_size_GLBL <- function( m ){ 1 + m + m*(m+1)/2 + m*(m+1)*(m+2)*(3*m+1)/24 }
Q_size_LoCL <- function( m , c ){ 1 + c + m*c*(c+1)/2 }

Grb_Q <- function( m_in , c_in , Q_list ){
    #    Under-the-hood function for grabbing Q-values from Q_list handed as argumment
    #    (rather than the global Q_list)
    m = max( m_in , c_in )
    c = min( m_in , c_in )
    i_min = Q_size_GLBL( m - 1 ) + Q_size_LoCL( m , c-1 ) + 1
    i_max = i_min + m*c
    I_ndx = i_min:i_max
    Q_list[I_ndx]
    }

Add_Q_at_m <- function( m , Q_list ){
    # Calculates the Q_terms for a given value of m for all values of c from 0 to m.
    if( m <= 0 ){ stop("Parameter m must be greater than zero in the Add_Q_at_m function.\n") }    # m == 0 is a problem because of how R handles the 1:m convention
    # first taking care of c = 0
    I_ndx = Q_size_GLBL( m - 1 ) + 1
    Q_list[ I_ndx ] = 1       
    for( c in 1:m ){
        i_min = Q_size_GLBL( m - 1 ) + Q_size_LoCL( m , c-1 ) + 1
        i_max = i_min + m*c
        I_ndx = i_min:i_max
        Q1 = c( Grb_Q( m-1 , c , Q_list ) , (1:c)*0  )
        Q2 = c(  (1:m)*0 , Grb_Q( m , c-1 , Q_list )  )
        Q_list[ I_ndx ] = Q1 + Q2
        }
    i_min = Q_size_GLBL( m-1 ) + 1
    i_max = Q_size_GLBL( m )
    I_ndx = i_min:i_max
    Q_list[ I_ndx ]
    }

Bld_Q <- function( m_top ){
    # NOT APPROVED FOR USER ACCESS!!  USE AT YOUR OWN PERIL
    N_tot = Q_size_GLBL( m_top )
    Q_out = (1:N_tot)*0
    # first taking care of m = 0
    Q_out[1] = 1
    for( m in 1:m_top ){
        i_min = Q_size_GLBL( m - 1 ) + 1
        i_max = Q_size_GLBL( m )
        I_ndx = i_min:i_max
        Q_out[ I_ndx ] = Add_Q_at_m( m , Q_out )
        }
    Q_out
    }

Add_Q <- function( m_old , m_new , Q_in ){
    # must have m_new > m_old, strictly greater
    # need to add some intput checks   
    N_tot = Q_size_GLBL( m_new )
    Q_out = (1:N_tot)*0
    i_max = Q_size_GLBL( m_old )
    Q_out[1:i_max] = Q_in[1:i_max]
    for( m in ((m_old+1):m_new) ){
        i_min = Q_size_GLBL( m - 1 ) + 1
        i_max = Q_size_GLBL( m )
        I_ndx = i_min:i_max
        Q_out[ I_ndx ] = Add_Q_at_m( m , Q_out )
        }
    Q_out   
    }

Get_Q <- function( m_in , c_in , k = ( 0:(m_in*c_in) ) ){
    # INPUT:
    #    m_in    single integer12211
    #    c_in    single integer
    #    k    single integer or integer array
    # OUTPUT:
    #    unnamed
    #    integer or integer array
    #    Number of ways to partition k into m_in pieces such that each piece is less than or equal to c_in
    m = max( m_in , c_in )
    c = min( m_in , c_in )
    if( m > m_Q_glbl ){
        Q_list_GLBL <<- Add_Q( m_Q_glbl , m , Q_list_GLBL )
         m_Q_glbl <<- m
        }
    Grb_Q( m , c , Q_list_GLBL )[k+1]
    }

npdiff <- function( y_M , err_c ){
    # INPUT:
    #    y_M     (1D array)     the measurement data of interest
    #    err_c (1D array)    are the n_c calibration data
    # OUTPUT:
    #    DS_yT (DS structure) confidence structure on the true value of the measurand
    n_M = length( y_M ); n_C = length( err_c );
    # Input check
    if( n_M*n_C == 0 ) stop("ERROR:  Must have at least one measurand datum and one calibration datum.\n")
    #    Input fix, just want lists
    y_M = c( y_M )
    err_c = c( err_c )
    DD = (1:(n_M*n_C))*0
    dim( DD ) <- c( n_M , n_C )
    for( jj in 1:n_C ) DD[,jj] = y_M - err_c[jj]
    yT = sort( DD[] )
    DS_yT = (1:(3*n_M*n_C+3))*0       
    dim( DS_yT ) <- c( n_M*n_C+1 , 3 )
    DS_yT[,1] = c( -Inf , yT )
    DS_yT[,2] = c( yT , Inf )
    Q = Get_Q( length( y_M ) , length( err_c ) )
    DS_yT[,3] = Q / sum( Q )
    pbox.ds(DS_yT)
    }



pl <- function(...) plot(NULL,ylim=c(0,1),xlim=as.vector(range(...)),xlab='',ylab='Cumulative probability')

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

if ("Pbox$scott.used.to.be.quiet" %in% ls()) {quiet <- Pbox$scott.used.to.be.quiet; rm("Pbox$scott.used.to.be.quiet")} else rm("quiet")

units = function(s) {warning("pba.r library doesn't support units or units checking like RAMAS Risk Calc does"); return(1) }

cat(':pbox> library loaded\n')






####################################################
# End of Probability Bounds Analysis library for R #
####################################################





################# testing
test.pbox <- function() {
bernoulli(.3);
Be(2,3)
beta(2,3)
B(10,.2)
binomial(10,.2)
cauchy(10,1)
chisquared(14)
delta(3)
dirac(3)
discreteuniform(20)
exponential(2)
F(4,5)
f(4,5)
frechet(9,1)
gamma(2,3)
erlang(2,3)
gamma1(5,1)
gamma2(3,2)
geometric(.3)
pascal(.3)
gumbel(2,3)
extremevalue(2,3)
laplace(2,3)
logistic(2,3)
L(5,1) 
lognormal(5,1) 
negativebinomial(10,.2)
N(5,1) 
normal(5,1)
gaussian(5,1)
pareto(5,1)
powerfunction(5,1)
poisson(4)
rayleigh(4)
reciprocal(12)
reciprocal()
weibull(5,2)
U(2,4)
uniform(2,4)
rectangular(2,4) 
loguniform(2,4)
triangular(.2, .6, 1.2)
logtriangular(.2, .6, 1.2)


bernoulli(interval(0.3, 0.5))
Be(interval(2,3),interval(4,5))
beta(interval(2,3),interval(4,5))
B(interval(10,12),interval(.2,.3))
binomial(interval(10,12),interval(.2,.3))
cauchy(interval(10,12),interval(2,3))
chisquared(interval(10,14))
delta(interval(3,5))
dirac(interval(3,5))
discreteuniform(interval(20,23))
exponential(interval(2,3))
F(interval(3,4),interval(4,5))
f(interval(3,4),interval(4,5))
frechet(interval(8,9),interval(1,2))
gamma(interval(8,9),interval(1,2))
erlang(interval(8,9),interval(1,2))
gamma1(interval(8,9),interval(1,2))
gamma2(interval(8,9),interval(1,2))
geometric(interval(.2,.3))
pascal(interval(.2,.3))
gumbel(interval(3,4),interval(4,5))
extremevalue(interval(3,4),interval(4,5))
laplace(interval(3,4),interval(4,5))
logistic(interval(3,4),interval(4,5))
L(interval(3,4),interval(.4,.5))
lognormal(interval(3,4),interval(.4,.5))
negativebinomial(interval(13,14),interval(.4,.5))
N(interval(3,4),interval(.4,.5))
normal(interval(3,4),interval(.4,.5))
gaussian(interval(3,4),interval(.4,.5))
pareto(interval(3,4),interval(4,5))
powerfunction(interval(3,4),interval(4,5))
poisson(interval(3,4))
rayleigh(interval(3,4))
reciprocal(interval(13,14))
weibull(interval(3,4),interval(4,5))
U(interval(.2,.3), interval(.6,.6))
uniform(interval(.2,.3), interval(.6,.6))
rectangular(interval(.2,.3), interval(.6,.6))
loguniform(interval(.2,.3), interval(.6,.6))
triangular(interval(.2,.3), .6, interval(1,1.2))
triangular(interval(.2,.3), interval(.6,.6), interval(1,1.2))
triangular(interval(.2,.3), interval(.2,.6), interval(1,1.2))
logtriangular(interval(.2,.3), .6, interval(1,1.2))
logtriangular(interval(.2,.3), interval(.6,.6), interval(1,1.2))
logtriangular(interval(.2,.3), interval(.2,.6), interval(1,1.2))
return(TRUE)
}


                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           