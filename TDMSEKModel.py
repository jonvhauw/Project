import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


"""
Constants and independent variables
"""

h = 100e-6 #Height of the cell
w = 1000e-6 #Width of the cell 
zv = 1  #charge of the ions
e = 1.60217662e-19 #elementary charge
I = 0.6e-4 #ionic strength  
rho = 1000 #density of medium
T = 297 #absolute temperature
mu = 8.9e-4 #viscosity
kb = 1.38064852e-23 #boltzmann constant
NA = 6.02214076e23 #avogadro
E = 18.4e3 # Efield strength
eps0 = 8.85418782e-12 #permitivity 
epsR = 80 #relative permitivity 
f = 1000
zetaW = -100e-3 #wall zeta potential
zetaP = -30e-3  #particle zeta potential

"""
Dependent variables
"""
nu = 0
Dh = 0
uEO = 0
Re = 0
n0 = 0
EBar = 0 
GBar = 0

kappa = 0 
kappaBar = 0

zetaWBar = 0

omega = 0

def init_dependent_variables():
    global h  
    global w  
    global zv 
    global e 
    global I 
    global rho 
    global T 
    global mu 
    global kb 
    global NA 
    global E 
    global eps0 
    global epsR 
    global f 
    global zetaW
    global zetaP
    
    global nu
    global Dh
    global uEO
    global Re
    global n0
    global EBar
    global GBar
    global kappa
    global kappaBar
    global zetaWBar
    global omega
    
    nu = mu/rho
    Dh = 2*h*w/(h+w)
    uEO = -E*eps0*epsR*zetaW/mu
    Re = rho*Dh*uEO/mu
    n0 = I/(1e-3) * NA #ion concentration 
    EBar = E*Dh*Re/zetaW
    GBar = 2*zv*e*n0*zetaW/(rho*uEO**2)
    
    kappa = math.sqrt((2* zv**2 * e**2 * n0)/(eps0*epsR*kb*T))
    kappaBar = kappa*Dh
    
    zetaWBar = zv*e*zetaW/(kb*T)
    
    omega = 2* np.pi * f
    
    print("Dh: {}".format(Dh))
    print("nu: {}".format(nu))
    print("Re: {}".format(Re))
    print("zetaWBar: {}".format(zetaWBar))
    print("Kappa: {}".format(kappaBar))
    print("GBar: {}".format(GBar))
    print("EBar: {}".format(EBar))
    print("uEO: {}".format(uEO))
    
    


def calc_Cmn(m=0,n=0):
    global kappaBar
    global omega
    global h
    global w
    global zetaWBar
    global Dh
    
    term1 = 1+(2*m-1)*(2*m-1)*np.pi*np.pi*Dh*Dh/(kappaBar*kappaBar*w*w)
    term1 = term1 * kappaBar*kappaBar
    term1 = term1/((2*n-1) *Dh*np.pi/h)
    term1 = term1 + (2*n-1)*Dh*np.pi/h
    term1 = term1*(2*m-1)*np.pi*Dh
    term1 = ((-1)**(int(m)+int(n)) * w)/term1
    
    
    
    term2 = (1+ ((2*n - 1)**2 * np.pi**2 * Dh**2)/(kappaBar**2 * h**2))*kappaBar**2
    term2 = term2/((2*m - 1)*Dh*np.pi/w)
    term2 = term2 + (2*m - 1)*Dh*np.pi/w
    term2 = term2 * (2*n - 1)*np.pi*Dh 
    term2 = (-1)**(int(m)+int(n)) * h/term2
    
    Cmn = (term1 + term2)*zetaWBar
    
    
    return Cmn


def calc_CmnBar(m=0,n=0):
    global kappaBar
    global omega
    global h
    global w
    global zetaWBar
    global Dh
    
    term1 = 1+(2*m-1)*(2*m-1)*np.pi*np.pi*Dh*Dh/(kappaBar*kappaBar*w*w)
    term1 = term1 * kappaBar*kappaBar
    term1 = term1/((2*n-1) *Dh*np.pi/h)
    term1 = term1 + (2*n-1)*Dh*np.pi/h
    term1 = term1*(2*m-1)*np.pi*Dh
    term1 = ((-1)**(int(m)+int(n)) * w)/term1
    
    
    
    term2 = (1+ ((2*n - 1)**2 * np.pi**2 * Dh**2)/(kappaBar**2 * h**2))*kappaBar**2
    term2 = term2/((2*m - 1)*Dh*np.pi/w)
    term2 = term2 + (2*m - 1)*Dh*np.pi/w
    term2 = term2 * (2*n - 1)*np.pi*Dh 
    term2 = (-1)**(int(m)+int(n)) * h/term2
    
    Cmn = (term1 + term2)
    
    
    return Cmn


def calc_Rmn(m=0,n=0):
    global w
    global h
    
    
    Rmn = 4*np.pi**2
    Rmn = Rmn*(((2*m-1)**2)/w**2 + ((2*n-1)**2)/h**2)
    
    return Rmn

def calc_AB(order=100,y=0,z=0):
    global omega
    global Dh
    global w
    global h
    global nu
    global kappaBar
    
    mArray = np.arange(1,int(order),dtype=int)
    nArray = np.arange(1,int(order),dtype=int)
    
    yBar = y/Dh
    zBar = z/Dh
    A = 0
    B = 0
    for m in mArray:
        for n in nArray:
            CmnBar = calc_CmnBar(m=m,n=n)
            Rmn = calc_Rmn(m=m, n=n)
            
            factor1 = Rmn**2 + (16*omega**2)/(nu**2)
            factor2 = math.cos((2*m - 1)*Dh*np.pi*yBar/w)
            factor3 = math.cos((2*n - 1)*Dh*np.pi*zBar/h)   
            
            A = A + CmnBar * (factor2*factor3/factor1) * Rmn
            B = B - CmnBar * (factor2*factor3/factor1) * (4*omega/nu)
            
    return A,B

def calc_alpha_beta(order=100,y=0,z=0):
    global Dh
    global w
    global h
    global kappaBar
    
    A,B = calc_AB(order=order, y=y, z=z)
    
    beta = (64/(h*w)) * (kappaBar**2) * math.sqrt(A**2 + B**2) 
    alpha = math.atan(B/A)
    
    print("beta: {}, alpha:{}".format(beta,alpha))
    return alpha,beta

def calc_uEOBar_without_zetaw(order=100,timeArray=np.array([]),y=0,z=0):
    global omega
    global Dh
    global w
    global h
    global nu
    global kappaBar
    
    mArray = np.arange(1,int(order),dtype=int)
    nArray = np.arange(1,int(order),dtype=int)
    uEOBarArray = np.array([])
    
    yBar = y/Dh
    zBar = z/Dh
    
    
    for t in timeArray:
        
        uEOBar = 0
        for m in mArray:
            for n in nArray:
                CmnBar = calc_CmnBar(m=m, n=n)
                Rmn = calc_Rmn(m=m, n=n)
                
                factor1 = Rmn**2 + (16*omega**2)/(nu**2)
                factor2 = math.cos((2*m - 1)*Dh*np.pi*yBar/w)
                factor3 = math.cos((2*n - 1)*Dh*np.pi*zBar/h)
                
                term1 = Rmn*math.sin(omega*t)*factor2*factor3/factor1
                term2 = (4*omega/nu)*math.cos(omega * t)*factor2*factor3/factor1
                
                uEOBar = uEOBar + CmnBar*(term1 - term2)
                
        uEOBar = (64/(h*w)) * (kappaBar**2) * uEOBar
        uEOBarArray = np.append(uEOBarArray, uEOBar)
        
    return uEOBarArray

def calc_uEOBar(order=100,timeArray=np.array([]),y=0,z=0):
    global omega
    global Dh
    global GBar
    global EBar
    global w
    global h
    global nu
    
    
    mArray = np.arange(1,int(order),dtype=int)
    nArray = np.arange(1,int(order),dtype=int)
    uEOBarArray = np.array([])
    
    yBar = y/Dh
    zBar = z/Dh
    
    
    for t in timeArray:
        
        uEOBar = 0
        for m in mArray:
            for n in nArray:
                Cmn = calc_Cmn(m=m, n=n)
                Rmn = calc_Rmn(m=m, n=n)
                
                factor1 = Rmn**2 + (16*omega**2)/(nu**2)
                factor2 = math.cos((2*m - 1)*Dh*np.pi*yBar/w)
                factor3 = math.cos((2*n - 1)*Dh*np.pi*zBar/h)
                
                term1 = Rmn*math.sin(omega*t)*factor2*factor3/factor1
                term2 = (4*omega/nu)*math.cos(omega * t)*factor2*factor3/factor1
                
                uEOBar = uEOBar + Cmn*(term1 - term2)
                
        uEOBar = (-64/(h*w)) * GBar * EBar * uEOBar
        uEOBarArray = np.append(uEOBarArray, uEOBar)
        
    return uEOBarArray

def calc_period_from_uEO_and_uEP(normalizedTimeArray=np.array([]),uEO=1.0,uEP=1.0,y=0,z=0,order=100):
    velocityPeriodArray = np.array([])
    alpha,beta = calc_alpha_beta(order=order,y=y,z=z)
    
    uObsFunction = fitting_function(alpha=alpha,beta=beta)
    
    for normalizedTime in normalizedTimeArray:
        uObs = uObsFunction(normalizedTime=normalizedTime, uEP=uEP, uEO=uEO)
        velocityPeriodArray = np.append(velocityPeriodArray,uObs)
        
    return velocityPeriodArray

def fitting_function_fixed_uEO(alpha,beta,uEO):
    def function(normalizedTime,uEP):
        
        normalizedAngle = 2*normalizedTime*np.pi
        a = uEP + uEO*beta*math.cos(alpha)
        b = uEO*beta*math.sin(alpha)
        
        amplitude = math.sqrt(a**2 + b**2)
        phase = math.atan(b/a)
        
        if(a < 0 and b < 0 and b/a >= 0):
            phase = phase - np.pi
        
        
        uObs = amplitude*np.sin(normalizedAngle + phase)
        
        
        return uObs
    return function    

def fitting_function(alpha,beta):
    def function(normalizedTime,uEP,uEO):
        
        normalizedAngle = 2*normalizedTime*np.pi
        a = uEP + uEO*beta*math.cos(alpha)
        b = uEO*beta*math.sin(alpha)
        
        amplitude = math.sqrt(a**2 + b**2)
        phase = math.atan(b/a)
        
        if(a < 0 and b < 0 and b/a >= 0):
            phase = phase - np.pi
        
        
        uObs = amplitude*np.sin(normalizedAngle + phase)
        
        
        return uObs
    return function

def calc_initial_guess():
    global zetaP
    global zetaW
    global eps0
    global epsR
    global E
    global mu
    
    uEOInit = - (eps0*epsR*E*zetaW)/mu
    uEPInit = (eps0*epsR*E*zetaP)/mu
    
    p0 = [uEPInit,uEOInit]
    
    return p0

def calc_initial_guess_fixed_uEO():
    global zetaP
    global zetaW
    global eps0
    global epsR
    global E
    global mu
    
    uEPInit = (eps0*epsR*E*zetaP)/mu
    
    p0 = [uEPInit]
    
    return p0

def fit_model_to_period(normalizedTimeArray=np.array([]),velocityArray=np.array([]),alpha=np.pi/2,beta=1.0):
    p0 = calc_initial_guess()
    try:
        
        popt, pcov = curve_fit(fitting_function(alpha=alpha,beta=beta),xdata=normalizedTimeArray,ydata=velocityArray,p0=p0) 
    except:
        popt = p0
        pcov = np.array([[0.0,0.0],[0.0,0.0]])
    velocityFitArray = np.array([])
    
    for normalizedTime in normalizedTimeArray:
        velocity = fitting_function(alpha=alpha,beta=beta)(normalizedTime=normalizedTime,uEP=popt[0],uEO=popt[1])
        velocityFitArray = np.append(velocityFitArray,velocity)
    
    return p0, popt,pcov, velocityFitArray

def fit_model_to_period_fixed_uEO(normalizedTimeArray=np.array([]),velocityArray=np.array([]),alpha=np.pi/2,beta=1.0,uEO=0.001):
    p0 = calc_initial_guess_fixed_uEO()
    try:
        
        popt, pcov = curve_fit(fitting_function_fixed_uEO(alpha=alpha,beta=beta,uEO=uEO),xdata=normalizedTimeArray,ydata=velocityArray,p0=p0) 
    except:
        popt = p0
        pcov = np.array([0.0])
    velocityFitArray = np.array([])
    
    for normalizedTime in normalizedTimeArray:
        velocity = fitting_function_fixed_uEO(alpha=alpha,beta=beta,uEO=uEO)(normalizedTime=normalizedTime,uEP=popt[0])
        velocityFitArray = np.append(velocityFitArray,velocity)
    
    return p0, popt,pcov, velocityFitArray
    
def fit_model_to_segment(timeArrayList=[],velocityArrayList=[],y=0,z=0):
    velocityFitArrayList = []
    poptList = []
    pcovList = []
    
    alpha,beta = calc_alpha_beta(y=y,z=z)
    normalizedVelocityTimeArrayList = normalize_time_array_list(timeArrayList=timeArrayList)
    
    for i in range(len(normalizedVelocityTimeArrayList)):
        p0, popt, pcov, velocityFitArray= fit_model_to_period(normalizedTimeArray=normalizedVelocityTimeArrayList[i], velocityArray=velocityArrayList[i], alpha=alpha, beta=beta)
        
        poptList.append(popt)
        pcovList.append(pcov)
        velocityFitArrayList.append(velocityFitArray)
        
    return p0, poptList, pcovList, velocityFitArrayList

def fit_model_to_segment_fixed_uEO(timeArrayList=[],velocityArrayList=[],uEO=0.001,y=0,z=0):
    velocityFitArrayList = []
    poptList = []
    pcovList = []
    
    alpha,beta = calc_alpha_beta(y=y,z=z)
    normalizedVelocityTimeArrayList = normalize_time_array_list(timeArrayList=timeArrayList)
    
    for i in range(len(normalizedVelocityTimeArrayList)):
        p0, popt, pcov, velocityFitArray= fit_model_to_period_fixed_uEO(normalizedTimeArray=normalizedVelocityTimeArrayList[i], velocityArray=velocityArrayList[i], alpha=alpha, beta=beta,uEO=uEO)
        
        poptList.append(popt)
        pcovList.append(pcov)
        velocityFitArrayList.append(velocityFitArray)
        
    return p0, poptList, pcovList, velocityFitArrayList


def normalize_time_array(timeArray=np.array([]),maxPeriodDuration=0):
    normalizedTimeArray = np.array([])
    
    if(maxPeriodDuration == 0):
        maxPeriodDuration = timeArray[-1] - timeArray[0]
        
    normalizedTimeArray = timeArray - timeArray[0]
    normalizedTimeArray = normalizedTimeArray/maxPeriodDuration
    
    return normalizedTimeArray
"""
def normalize_time_array_list(timeArrayList=[]):
    normalizedTimeArrayList = []
    
        
    for i in range(len(timeArrayList)):
        periodDuration = timeArrayList[i][-1] - timeArrayList[i][0]
        tempTimeArray = timeArrayList[i] - timeArrayList[i][0]
        tempTimeArray = tempTimeArray/periodDuration
        
        normalizedTimeArrayList.append(tempTimeArray)
        
    
    return normalizedTimeArrayList
"""

def normalize_time_array_list(timeArrayList=[]):
    maxPeriodDuration = 0
    normalizedTimeArrayList = []
    
    for period in timeArrayList:
        periodDuration = period[-1]-period[0]
        if(periodDuration > maxPeriodDuration):
            maxPeriodDuration = periodDuration
        
    for i in range(len(timeArrayList)):
        tempTimeArray = timeArrayList[i] - timeArrayList[i][0]
        tempTimeArray = tempTimeArray/maxPeriodDuration
        
        normalizedTimeArrayList.append(tempTimeArray)
        
    
    return normalizedTimeArrayList
   
    
if (__name__ == "__main__"):
    print("Done")
    
    init_dependent_variables()
    calc_alpha_beta(order=25,y=0,z=0)
    timeArray = np.linspace(0,0.01,200)
    
    uEOBarArray = calc_uEOBar(timeArray=timeArray)
    
    noZetauEOBarArray = calc_uEOBar_without_zetaw(timeArray=timeArray)
    
    alpha,beta = calc_alpha_beta()
    tempArray = timeArray*omega + alpha
    
    print("alpha: {}".format(alpha*180/np.pi))
    print("beta: {}".format(beta))
    
    normalizedTimeArray = normalize_time_array(timeArray=timeArray,maxPeriodDuration=0.01)
    velocityFitArray = np.array([])
    
    for normalizedTime in normalizedTimeArray:
        velocity = fitting_function(alpha=alpha,beta=beta)(normalizedTime=normalizedTime,uEP=-0.0008,uEO=0.001)
        velocityFitArray = np.append(velocityFitArray,velocity)    
    
    
    fig1, ax1 = plt.subplots()
    """
    ax1.plot(timeArray,uEOBarArray,color="red")
    ax1.plot(timeArray,noZetauEOBarArray,linestyle='--',color="blue")
    ax1.plot(timeArray,beta*np.sin(tempArray),linestyle=' ',marker='o',color='green')
    """
    ax1.plot(normalizedTimeArray,velocityFitArray,linestyle='-',color='green')
    
    plt.show()
