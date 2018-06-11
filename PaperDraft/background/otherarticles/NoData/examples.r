###############################################
# Invoke R by double clicking its desktop icon
# Enter rm(list = ls()) to clear R’s memory
# Click File / Source R code on the main menu
# Locate and Open the file sra.r
###############################################


# slide 22
normal(3,1)
uniform(0,6)
exponential(1)
N(3,1)


# 23
binomial(7,.4)


# 30
a = N(50,13)
a
cut.mc(a, 0.67)     # cut <- function(x,s,...) {UseMethod("fractile")}; cut(a, 0.67)


# 35
X = N(5,1)
Y = T(1,2,4)
plot.mclist(X, Y, X + Y)


# 39
L = U(80, 120) 		    
i = U(0.0003, 0.0008)	
K = L(1000, 750)	    
n = L(0.25, 0.05)  	    
BD = L(1650, 100)
foc = U(0.0001, 0.005)
Koc = N(10, 3)
T = (n + BD * foc * Koc) * L / (K * i) 
summary(T)


# 40
L = uniform(80, 120) 	
i = uniform(0.0003, 0.0008)
K = lognormal(1000, 750)
K = truncate(K, 300, 3000)
n = lognormal(0.25, 0.05)
n = truncate(n, 0.2, 0.35)
BD = lognormal(1650, 100)
BD = truncate(BD, 1500, 1750)
foc = uniform(0.0001, 0.005)
Koc = normal(10, 3)
Koc = truncate(Koc, 5, 20)
T = (n + BD * foc * Koc) * L / (K * i) 
summary(T)


# 41
par(mfrow=c(2,4))
plot(L)
plot(i)
plot(K)
plot(n)
plot(BD)
plot(foc)
plot(Koc)
par(mfrow=c(1,1))


# 42
plot(T)


# 44
plot(T, xlim=c(0,500))


# 51
Data = c(
0.653,    
0.178 ,
0.263 ,    
0.424 ,
0.284 ,    
0.438 ,
0.471 ,    
0.852 ,
0.480 ,    
0.375 ,
0.148 ,    
0.185 , 
0.320 ,     
0.642 , 
0.247 ,    
0.784 ,
0.643 ,    
0.261 ,
0.636 ,    
0.487)
normal(mean(Data), sd(Data))


# 52 
MLnormal(Data)


# 57
histogram(Data)                    # the figure doesn't match the data


# 61
par(mfrow=c(3,4))
betapert(1,12, 1)
betapert(1,12, 2)
betapert(1,12, 3)
betapert(1,12, 4)
betapert(1,12, 5)
betapert(1,12, 6)
betapert(1,12, 7)
betapert(1,12, 8)
betapert(1,12, 9)
betapert(1,12, 10)
betapert(1,12, 11) 
betapert(1,12, 12)
par(mfrow=c(1,1))


# 70
L   = MEmmms(80,120,100,11.55)  		# source-receptor distance
i   = MEmmms(0.0003,0.0008,0.00055,0.0001443)	# hydraulic gradient
K   = MEmmms(300,3000,1000,750)  		# hydraulic conductivity
n   = MEmmms(0.2,0.35,0.25,0.05)  		# effective soil porosity
BD  = MEmmms(1500,1750,1650,100) 		# soil bulk density
foc = MEmmms(0.0001,0.005,0.00255,0.001415)   	# fraction organic carbon
Koc = MEmmms(5,20,10,3)    			# organic partition coefficient 
Tind  = (n + BD * foc* Koc) * L / (K * i) 
summary(Tind)


# 71
par(mfrow=c(2,4))
plot(L,col='red')
plot(i,col='red')
plot(K,col='red')
plot(n,col='red')
plot(BD,col='red')
plot(foc,col='red')
plot(Koc,col='red')
par(mfrow=c(1,1))


# 72
Maxent = Tind
pert = function(x) betapert(left(x), right(x), mean(x))     # notice use of "mean"
L   = pert(L)
i   = pert(i)
K   = pert(K)
n   = pert(n)
BD  = pert(BD)
foc = pert(foc)
Koc = pert(Koc)
PERT  = (n + BD * foc* Koc) * L / (K * i) 
plot(NULL, xlim=c(0,100000), ylim=c(0,1))
lines(PERT, col='lightblue')
lines(Maxent, col='red')


# 76 
BW = normal( 608, 66.9) 
A = uniform(0.354,0.47)
B = uniform(0.836,0.888) 
FMR = A * BW ^ B 
AEfish = MEminmaxmean(0.77, 0.98, 0.91)   
AEinverts = MEminmaxmean(0.72, 0.96, 0.87)   
GEfish = normal(1200, 240) 
GEinverts = normal(1050, 225) 
Cfish = uniform(0.1,0.3)
Cinverts = uniform(0.02, 0.06) 
Pfish = 0.9  
Pinverts = 0.1 
TDI = FMR * (Cfish * Pfish / (AEfish * GEfish) + Cinverts * Pinverts / (AEinverts * GEinverts))


# 78
plot(TDI, cumulative=FALSE)
mean(TDI)
median(TDI)
cut(TDI, 0.95)
sd(TDI)


###############################################
# Invoke R by double clicking its desktop icon
# Enter rm(list = ls()) to clear R’s memory
# Click File / Source R code on the main menu
# Locate and Open the file pba.r
###############################################


# 121
A = lognormal(interval(.05,.06), sqrt(interval(0.0001,0.001)))
B = minmaxmode(0, 0.05, 0.03)
C = histogram(c(0.2, 0.5, 0.6, 0.7, 0.75, 0.8), mn=0, mx=1)
D = uniform(0, 1)
par(mfrow=c(2,2))
plot(A, col='blue')
plot(B, col='pink')
plot(C, col='black')
plot(D, col='green')


# 122
par(mfrow=c(1,1))
fi = A %|&|% B %|&|% C %|&|% D
f = A %&% B %&% C %&% D
plot(f, col='orange')
lines(fi, col='black')


# 123
range(fi)
median(fi)
mean(fi)
var(fi)
sd(fi)
range(f)
median(f)
mean(f)
var(f)
sd(f)


# 126
A = env(mix.equal.numeric(c(10,20,30,40)), mix.equal.numeric(c(30,50,60,70)))
prob(A, 15)
cut(A, 0.95)          # cut.pbox(A, 0.95)


# 129-130
A = mixture(i(1,3), i(2,4), i(3,5))
B = mixture(i(2,8), i(6,10), i(8,12))
A + B


# 134
par(mfrow=c(3,3))
plot(minmax(5,7))
plot(minmaxmedian(5,7,6))
plot(minmaxmode(5,7,6))
plot(minmaxmean(5,7,6))
plot(unimmms(5,7,6,1,6))          # plot(minmaxmeanismode(5,7,6))  # minmaxmeanismode has a bug
plot(minmaxmedianismode(5,7,6))
plot(meanstd(5,1))
plot(symmeanstd(5,1))
plot(mmms(5,7,6,0.5))
par(mfrow=c(1,1))


# 142
a.1=i(1.00, 2.00) 
a.2=i(2.68, 2.98) 
a.3=i(7.52, 7.67) 
a.4=i(7.73, 8.35) 
a.5=i(9.44, 9.99) 
a.6=i(3.66, 4.58)
b.1=i(3.5, 6.4)
b.2=i(6.9, 8.8)
b.3=i(6.1, 8.4)
b.4=i(2.8, 6.7)
b.5=i(3.5, 9.7)
b.6=i(6.5, 9.9)
b.7=i(0.15, 3.8)
b.8=i(4.5, 4.9)
b.9=i(7.1, 7.9)
a = mixture(a.1,a.2,a.3,a.4,a.5,a.6)
b = mixture(b.1,b.2,b.3,b.4,b.5,b.6,b.7,b.8,b.9)


# 144
# it's not easy to compute the fitted normals in pba.r


# 146
data = runif(30,340,460)  # not the correct data for the graph on the slide
histogram(data)


# 147
# needs RAMAS Risk Calc
#setdefault(confidence,3) // 95%
#H = histogram(0.001,9.99,a.1,a.2,a.3,a.4,a.5,a.6, b.1,b.2,b.3,b.4,b.5,b.6,b.7,b.8,b.9)
#setdefault(confidence,0) // 0%
#h = histogram(0.001,9.99,a.1,a.2,a.3,a.4,a.5,a.6, b.1,b.2,b.3,b.4,b.5,b.6,b.7,b.8,b.9)
#plot(h,col='black')
#plot(H,col='green')
# the green graph on the slide is in error; the confidence levels seems to be less than 95%


# 156
plot(CBbinomial(2,10))  # equivalent to CBbernoulli(c(0,0,1,0,1,0,0,0,0,0))


# 160
# the mmms function is not optimal in pba.r
L   = mmms(80,120,100,11.55)  			# source-receptor distance
i   = mmms(0.0003,0.0008,0.00055,0.0001443)	# hydraulic gradient
K   = mmms(300,3000,1000,750)  			# hydraulic conductivity
n   = mmms(0.2,0.35,0.25,0.05)  		# effective soil porosity
BD  = mmms(1500,1750,1650,100) 			# soil bulk density
foc = mmms(0.0001,0.005,0.00255,0.001415)   	# fraction organic carbon
Koc = mmms(5,20,10,3)    			# organic partition coefficient 
par(mfrow=c(2,4))
plot(L)
plot(i)
plot(K)
plot(n)
plot(BD)
plot(foc)
plot(Koc)
par(mfrow=c(1,1))


# 161
T  = (n %+% BD %*% foc %*% Koc) %*% L %/% (K %*% i) 


# 162
plot(T, xlim=c(0,500))
 

# 166
BW = normal( 608, 66.9)   
FMR = i(0.412 + c(-1,1)*0.058) * BW ^ i(0.862 + c(-1,1)*0.026)
AEfish = minmaxmean(0.77, 0.98, 0.91)   
AEinverts = minmaxmean(0.72, 0.96, 0.87)   
GEfish = normal(1200, 240)   
GEinverts = normal(1050, 225)   
Cfish = i(0.1,0.3)  
Cinverts = i(0.02, 0.06)
Pfish = 0.9  
Pinverts = 0.1  

# 167
par(mfrow=c(2,4))
plot(BW)
plot(FMR)
plot(AEfish)
plot(AEinverts)
plot(GEfish)
plot(GEinverts)
plot(Cfish)
plot(Cinverts)
plot(Pfish)
plot(Pinverts)
par(mfrow=c(1,1))


# 168
TDI = FMR %|*|% (Cfish %*% Pfish %/% (AEfish %|*|% GEfish) %+% Cinverts %*% Pinverts %/% (AEinverts %|*|% GEinverts))

