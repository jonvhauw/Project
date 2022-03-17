
from operator import index
import pyqtgraph as pg
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import LineCollection
import PyQt5 as qt
import Colors as Col

globalEventList = []

plotTrace = True
plotAOD = True
plotPixelNumber = True
plotAODSync = True
plotDiscont = True

plotExtField =True
plotExtFieldKymo = True

plotSPCM = True
plotSPCMSync = True
plotSPCMSampleRatio = 1
normalize = True

kymoStyle = "straight"
plotKymo = True
plotCentroidKymo = True

def on_right_click_plot_time(event):
    global globalEventList
    
    if(event.button == 3):
        globalEventList.append(event.xdata)
        if(len(globalEventList) == 1):
            print("Added time: {} s".format(event.xdata))
        elif(len(globalEventList) == 2):
            print("Added time: {} s".format(event.xdata))
            print("Time difference = {} s".format(globalEventList[0]-globalEventList[1]))
            globalEventList = []
    

def plot_trace_segment(AODTimeArray=np.array([]),pixelNumberArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),AOD1DataArray=np.array([]),AOD2DataArray=np.array([]),
                      eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),discontTimeArray=np.array([]),discontDataArray=np.array([]),AODSyncTimeArray=np.array([]),AODSyncDataArray=np.array([]),
                      SPCMSyncDataArray=np.array([]),SPCMSyncTimeArray=np.array([]),yLabel="Normalized Trace (a.u.)"):
    global plotTrace
    if(plotTrace == True):
        plot_trace2(AODTimeArray=AODTimeArray, pixelNumberArray=pixelNumberArray, SPCMTimeArray=SPCMTimeArray, SPCMDataArray=SPCMDataArray, AOD1DataArray=AOD1DataArray, 
                          AOD2DataArray=AOD2DataArray, eFieldTimeArray=eFieldTimeArray, eFieldDataArray=eFieldDataArray, discontTimeArray=discontTimeArray, discontDataArray=discontDataArray, 
                          AODSyncTimeArray=AODSyncTimeArray, AODSyncDataArray=AODSyncDataArray, SPCMSyncDataArray=SPCMSyncDataArray, SPCMSyncTimeArray=SPCMSyncTimeArray,yLabel=yLabel)

def plot_trace2(AODTimeArray=np.array([]),pixelNumberArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),AOD1DataArray=np.array([]),AOD2DataArray=np.array([]),
                      eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),discontTimeArray=np.array([]),discontDataArray=np.array([]),AODSyncTimeArray=np.array([]),AODSyncDataArray=np.array([]),
                      SPCMSyncDataArray=np.array([]),SPCMSyncTimeArray=np.array([]),yLabel="Normalized Trace (a.u.)", AOD1_c='dark green', AOD1_s = 'solid', AOD2_c = 'dark blue', AOD2_s = 'solid', Pix_c = 'light green', Pix_s='solid',
                      SPCM_c = 'red', SPCM_s = 'solid', EF_c = 'blue', EF_s = 'solid', SPCM_sync_c = 'dark red', SPCM_sync_s= 'dashed', AOD_sync_c = 'dark green', AOD_sync_s = 'dashed', Disc_c = 'gold', Disc_s = 'solid'):
    
    global plotAOD
    global plotPixelNumber
    global plotAODSync
    global plotDiscont
    global plotSPCM
    global plotSPCMSync
    global plotSPCMSampleRatio
    global normalize
    global plotExtField

    #qt.QTCore.Qt.DashLine
    #pen = pg.mkPen('r', style=qt.QtCore.Qt.DashLine)
    #win = pg.GraphicsWindow(title="test")
    #pg.setConfigOptions(antialias=True)
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    ax = pg.plot()
    #pw = pg.plot(AODTimeArray, AOD1DataArray/max(AOD1DataArray), pen=pen )  # plot x vs y in red
    #pw.plot(AODTimeArray,AOD2DataArray/max(AOD2DataArray), pen='b' )
    #fig, ax = plt.subplots()
    #cid = fig.canvas.mpl_connect('button_press_event', on_right_click_plot_time)
    
    if(plotAOD == True):
        if(normalize == True):
            if(plotPixelNumber == True):
                ax.plot(AODTimeArray,pixelNumberArray/max(pixelNumberArray), pen=Col.make_pen(color=Pix_c, style=Pix_s))
            else:
                ax.plot(AODTimeArray,AOD1DataArray/max(AOD1DataArray), pen=Col.make_pen(color=AOD1_c, style=AOD1_s))
                ax.plot(AODTimeArray,AOD2DataArray/max(AOD2DataArray), pen=Col.make_pen(color=AOD2_c, style=AOD2_s))
        else:
            if(plotPixelNumber == True):
                ax.plot(AODTimeArray,pixelNumberArray,pen=Col.make_pen(color=Pix_c, style=Pix_s))
            else:
                ax.plot(AODTimeArray,AOD1DataArray, pen=Col.make_pen(color=AOD1_c, style=AOD1_s))
                ax.plot(AODTimeArray,AOD2DataArray, pen=Col.make_pen(color=AOD2_c, style=AOD2_s))
            
    if(plotSPCM == True):
        if(normalize == True):
            if(plotSPCMSampleRatio >= 1):
                ax.plot(SPCMTimeArray,SPCMDataArray/max(SPCMDataArray), pen=Col.make_pen(color=SPCM_c, style=SPCM_s))
            else:
                sampleArray = np.arange(0,len(SPCMTimeArray),int(1.0/plotSPCMSampleRatio))
                ax.plot(SPCMTimeArray[sampleArray],SPCMDataArray[sampleArray]/max(SPCMDataArray[sampleArray]), pen=Col.make_pen(color=SPCM_c, style=SPCM_s))
        else:
            if(plotSPCMSampleRatio >= 1):
                ax.plot(SPCMTimeArray,SPCMDataArray, pen='c')
            else:
                sampleArray = np.arange(0,len(SPCMTimeArray),int(1.0/plotSPCMSampleRatio))
                ax.plot(SPCMTimeArray[sampleArray],SPCMDataArray[sampleArray], pen=Col.make_pen(color=SPCM_c, style=SPCM_s))
                
    if(plotExtField == True):       
        if(normalize == True):
            ax.plot(eFieldTimeArray,eFieldDataArray/max(eFieldDataArray), pen=Col.make_pen(color=EF_c, style=EF_s))
        else:
            ax.plot(eFieldTimeArray,eFieldDataArray,linestyle='-', pen=Col.make_pen(color=EF_c, style=EF_s))

    #from here: dashed lines standard 
    if(plotSPCMSync == True):      
        ax.plot(SPCMSyncTimeArray,SPCMSyncDataArray, pen=Col.make_pen(color=SPCM_sync_c, style=SPCM_sync_s))  
        
    if(plotAODSync == True):
        ax.plot(AODSyncTimeArray,AODSyncDataArray, pen=Col.make_pen(color=AOD_sync_c, style=AOD_sync_s))  
            
    if(plotDiscont == True):
        ax.plot(discontTimeArray,discontDataArray, pen=Col.make_pen(color=Disc_c, style=Disc_s))    
         
        
    ax.setTitle('Time traces',fontsize=20)
    ax.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
    #ax.tick_params(labelsize=15)
    #pg.setLabel('left', 'y')
    #pg.setLabem('bottom', 'time(s)')
    #plt.xlabel("time (s)", fontsize = 15)
    #plt.ylabel(yLabel, fontsize = 15)
    #ax.legend(fontsize=15,loc="upper right") 
    #ax.grid()
    #plt.show()

'''
def plot_trace1(AODTimeArray=np.array([]),pixelNumberArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),AOD1DataArray=np.array([]),AOD2DataArray=np.array([]),
                      eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),discontTimeArray=np.array([]),discontDataArray=np.array([]),AODSyncTimeArray=np.array([]),AODSyncDataArray=np.array([]),
                      SPCMSyncDataArray=np.array([]),SPCMSyncTimeArray=np.array([]),yLabel="Normalized Trace (a.u.)"):
    
    global plotAOD
    global plotPixelNumber
    global plotAODSync
    global plotDiscont
    global plotSPCM
    global plotSPCMSync
    global plotSPCMSampleRatio
    global normalize
    global plotExtField
    
    
    fig, ax = plt.subplots()
    cid = fig.canvas.mpl_connect('button_press_event', on_right_click_plot_time)
    
    if(plotAOD == True):
        if(normalize == True):
            if(plotPixelNumber == True):
                ax.plot(AODTimeArray,pixelNumberArray/max(pixelNumberArray),linestyle='-',color="lightgreen",label="pixelNumber")
            else:
                ax.plot(AODTimeArray,AOD1DataArray/max(AOD1DataArray),linestyle='-',color="darkgreen",label="AOD x")
                ax.plot(AODTimeArray,AOD2DataArray/max(AOD2DataArray),linestyle='-',color="darkblue",label="AOD y")
        else:
            if(plotPixelNumber == True):
                ax.plot(AODTimeArray,pixelNumberArray,linestyle='-',color="lightgreen",label="pixelNumber")
            else:
                ax.plot(AODTimeArray,AOD1DataArray,linestyle='-',color="lightgreen",label="AOD1")
                ax.plot(AODTimeArray,AOD2DataArray,linestyle='-',color="turquoise",label="AOD2")
            
    if(plotSPCM == True):
        if(normalize == True):
            if(plotSPCMSampleRatio >= 1):
                ax.plot(SPCMTimeArray,SPCMDataArray/max(SPCMDataArray),linestyle='-',color="red",label="SPCM")
            else:
                sampleArray = np.arange(0,len(SPCMTimeArray),int(1.0/plotSPCMSampleRatio))
                ax.plot(SPCMTimeArray[sampleArray],SPCMDataArray[sampleArray]/max(SPCMDataArray[sampleArray]),linestyle='-',color="red",label="SPCM")
        else:
            if(plotSPCMSampleRatio >= 1):
                ax.plot(SPCMTimeArray,SPCMDataArray,linestyle='-',color="red",label="SPCM")
            else:
                sampleArray = np.arange(0,len(SPCMTimeArray),int(1.0/plotSPCMSampleRatio))
                ax.plot(SPCMTimeArray[sampleArray],SPCMDataArray[sampleArray],linestyle='-',color="red",label="SPCM")
                
    if(plotExtField == True):       
        if(normalize == True):
            ax.plot(eFieldTimeArray,eFieldDataArray/max(eFieldDataArray),linestyle='-',color="blue",label="E-Field")
        else:
            ax.plot(eFieldTimeArray,eFieldDataArray,linestyle='-',color="blue",label="E-Field")
                
    if(plotSPCMSync == True):      
        ax.plot(SPCMSyncTimeArray,SPCMSyncDataArray,linestyle='--',linewidth=2.0,color="darkred",label="SPCM Sync")  
        
    if(plotAODSync == True):
        ax.plot(AODSyncTimeArray,AODSyncDataArray,linestyle='--',linewidth=2.0,color="darkgreen",label="AOD Sync")  
            
    if(plotDiscont == True):
        ax.plot(discontTimeArray,discontDataArray,linestyle='-',color="gold",label="Discontinuity")    
         
        
    ax.set_title('Time traces',fontsize=20)
    ax.tick_params(labelsize=15)
    plt.xlabel("time (s)", fontsize = 15)
    plt.ylabel(yLabel, fontsize = 15)
    ax.legend(fontsize=15,loc="upper right") 
    ax.grid()
    plt.show()
'''  
 
    
def plot_position_and_velocity_trace(frameTimeStampArray=np.array([]),widthPositionArray=np.array([]),heightPositionArray=np.array([]),
                                     positionTimeArray=np.array([]),filteredHeightPositionArray=np.array([]),filteredWidthPositionArray=np.array([]),
                                     velocityTimeArray=np.array([]),heightVelocityArray=np.array([]),widthVelocityArray=np.array([]),
                                     eFieldTimeArray=np.array([]),eFieldDataArray=np.array([])):
    
    plotHeight = False
    plotWidth = False
    global plotExtField
    
    
    if(len(widthPositionArray)>0):
        plotWidth = True
    
    if(len(heightPositionArray)>0):
        plotHeight = True
        
    
    positionVelocityFig, positionVelocityAxes = plt.subplots(nrows=2,ncols=1,sharex=True)
        
    positionAx1 = positionVelocityAxes[0]
    positionAx2 = positionAx1.twinx()
    lineListPosition = []    
    
    velocityAx1 = positionVelocityAxes[1]
    velocityAx2 = velocityAx1.twinx()
    lineListVelocity = []    
    
    if(plotExtField == True):
        stopIndexEField = np.where(eFieldTimeArray <= positionTimeArray[-1])[0][-1]
            
        
        line = positionAx2.plot(eFieldTimeArray[:stopIndexEField],eFieldDataArray[:stopIndexEField]/max(eFieldDataArray[:stopIndexEField]),lw=2,linestyle="-",color="green",label="E/Emax")
        lineListPosition = lineListPosition + line
        positionAx2.set_ylabel('E-Field/max(E-Field)',fontsize=15)
        positionAx2.tick_params(axis="y",labelsize=10)
        positionAx2.yaxis.label.set_color("green")
        
        line = velocityAx2.plot(eFieldTimeArray[:stopIndexEField],eFieldDataArray[:stopIndexEField]/max(eFieldDataArray[:stopIndexEField]),lw=2,linestyle="-",color="green",label="E/Emax")
        lineListVelocity = lineListVelocity + line
        velocityAx2.set_ylabel('E-Field/max(E-Field)',fontsize=15)
        velocityAx2.tick_params(axis="y",labelsize=10)
        velocityAx2.yaxis.label.set_color("green")
        
    if(plotHeight == True):
        line = positionAx1.plot(frameTimeStampArray,heightPositionArray*1e6,linestyle='',marker='o',color="salmon",label="y-position")
        lineListPosition = lineListPosition + line
        line = positionAx1.plot(positionTimeArray,filteredHeightPositionArray*1e6,lw=2,color="darkred",label="y-position (filter)")
        lineListPosition = lineListPosition + line
        
        line = velocityAx1.plot(velocityTimeArray,heightVelocityArray*1e3,color="red",lw=2,label="y-velocity")
        lineListVelocity = lineListVelocity + line
        
        
    
    if(plotWidth == True):
        line = positionAx1.plot(frameTimeStampArray,widthPositionArray*1e6,linestyle='',marker='o',lw=2,color="lightblue",label="x-position")
        lineListPosition = lineListPosition + line
        line = positionAx1.plot(positionTimeArray,filteredWidthPositionArray*1e6,color="darkblue",lw=2,label="x-position (filter)")
        lineListPosition = lineListPosition + line
        
        line = velocityAx1.plot(velocityTimeArray,widthVelocityArray*1e3,color="blue",lw=2,label="x-velocity")   
        lineListVelocity = lineListVelocity + line
        
    
    labels = [line.get_label() for line in lineListPosition]
    positionAx2.legend(lineListPosition,labels,fontsize=15,loc="upper right")
    positionAx1.set_title('Particle position trace',fontsize=20)
    positionAx1.set_ylabel('Particle position (um)',fontsize=15)
    positionAx1.tick_params(axis='both',labelsize=10)
    positionAx1.yaxis.label.set_color("red")
    positionAx1.set_xlabel('Time (s)',fontsize=15)
    positionAx1.grid()
    
    labels = [line.get_label() for line in lineListVelocity]
    velocityAx2.legend(lineListVelocity,labels,fontsize=15,loc="upper right")    
    velocityAx1.set_title('Particle velocity trace',fontsize=20)
    velocityAx1.set_ylabel('Particle velocity (mm/s)',fontsize=15)
    velocityAx1.tick_params(axis="both",labelsize=10)
    velocityAx1.yaxis.label.set_color("red")
    velocityAx1.set_xlabel('Time (s)',fontsize=15)
    velocityAx1.grid()
    
    
    
    plt.show()    
    


def plot_overlapping_periods(timeArrayList=[],dataArrayList=[],averageVelocityTimeArray=np.array([]),averageVelocityArray=np.array([]),eFieldFreq=100):
    global plotExtField
    
    maxPeriodDuration = 0
    labelList = []
    lineList = []
    periodOverlapFig, periodOverlapAxes = plt.subplots()
    eFieldPeriodAxes = periodOverlapAxes.twinx()
    
    
    for period in timeArrayList:
        periodDuration = period[-1] - period[0]
        if( periodDuration > maxPeriodDuration):
            maxPeriodDuration = periodDuration
    
    for i in range(len(timeArrayList)):
        
        tempTimeArray = timeArrayList[i] - timeArrayList[i][0] 
        tempTimeArray = tempTimeArray/maxPeriodDuration
        
        line = periodOverlapAxes.plot(tempTimeArray,dataArrayList[i]*1e3,color="red",alpha=0.25,label="Velocity")
        
    lineList.append(line[0])
    labelList = [line[0].get_label()]
    
    if(plotExtField == True):
        eFieldTimeArray = np.linspace(0,1,100)
        eFieldDataArray = np.sin(2*np.pi*eFieldTimeArray)
        
        eLine = eFieldPeriodAxes.plot(eFieldTimeArray,eFieldDataArray,linestyle="dashed",lw=2,color="green",label="E/Emax")
        
        lineList.append(eLine[0])
        labelList.append(eLine[0].get_label())
        
        eFieldPeriodAxes.set_ylabel('E-Field/max(E-Field)',color="green",fontsize=15)
        eFieldPeriodAxes.tick_params(axis="y",labelsize=10)
        
    if(len(averageVelocityArray) > 0):
        avgLine = periodOverlapAxes.plot(averageVelocityTimeArray,averageVelocityArray*1e3,lw=2,color='black',label="Average")
        lineList.append(avgLine[0])
        labelList.append(avgLine[0].get_label())
        
        
    
    periodOverlapAxes.legend(lineList,labelList,fontsize=15,loc="upper right")
    periodOverlapAxes.set_title('Particle velocity at centerline',fontsize=20)
    periodOverlapAxes.set_ylabel('Particle velocity (mm/s)',color="red",fontsize=15)
    periodOverlapAxes.set_xlabel('Normalized time (time/period) (a.u.)',fontsize=15)   
    periodOverlapAxes.tick_params(axis="both",labelsize=10)
    periodOverlapAxes.grid()
    plt.show()
    
    
def plot_fitted_velocity_scatter_plot(fittedVelocityList=[],fittedCovVelocityList=[]):
    fitteduEPArray = np.array([])
    fitteduEOArray = np.array([])
    
    for i in range(len(fittedVelocityList)):
        fitteduEPArray = np.append(fitteduEPArray,fittedVelocityList[i][0])
        fitteduEOArray = np.append(fitteduEOArray,fittedVelocityList[i][1])
        
    averageuEP = np.average(fitteduEPArray)
    averageuEO = np.average(fitteduEOArray)
    
    fig, ax = plt.subplots()
    
    ax.plot(fitteduEOArray*1e3,fitteduEPArray*1e3,color="red",marker="o",linestyle="",label="Fitted Data")
    ax.plot(averageuEO*1e3,averageuEP*1e3,color="black",marker="X",linestyle="",label="Average", markersize=20)
    
    ax.grid()
    ax.legend(fontsize=15,loc="upper right")
    ax.set_title('Electrophoretic vs Electroosmotic velocity',fontsize=20)
    ax.set_ylabel('Electrophoretic velocity (mm/s)',fontsize=15)
    ax.set_xlabel('Electroosmotic velocity (mm/s)',fontsize=15)
    plt.show()
    
def plot_fitted_velocity_fixed_uEO(fitteduEPArray=np.array([]),uEO=0.001):
    fitteduEOArray = np.array([])
    
    for i in range(len(fitteduEPArray)):
        fitteduEOArray = np.append(fitteduEOArray,uEO)
        
    averageuEP = np.average(fitteduEPArray)
    
    fig, ax = plt.subplots()
    
    ax.plot(fitteduEOArray*1e3,fitteduEPArray*1e3,color="red",marker="o",linestyle="",label="Fitted Data")
    ax.plot(uEO*1e3,averageuEP*1e3,color="black",marker="X",linestyle="",label="Average", markersize=20)
    
    ax.grid()
    ax.legend(fontsize=15,loc="upper right")
    ax.set_title('Electrophoretic vs Electroosmotic velocity',fontsize=20)
    ax.set_ylabel('Electrophoretic velocity (mm/s)',fontsize=15)
    ax.set_xlabel('Electroosmotic velocity (mm/s)',fontsize=15)
    plt.show()    


def plot_kymograph(xDataArrayList=[],yDataArrayList=[],frameTimeStampArray=np.array([]),eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),positionTimeArray=np.array([]),
                   frameSumWidthCentroidArray=np.array([]),frameSumHeightCentroidArray=np.array([]),pitchX=0.4e-6,pitchY=0.4e-6,offsetFactor=1.0,saveFig=True,figurePath=""):
    
    if(len(xDataArrayList) == 0 or len(yDataArrayList) == 0):
        if(len(xDataArrayList) > 0 ):
            positionDataArrayList = xDataArrayList
            centroidArray = frameSumWidthCentroidArray
        else:
            positionDataArrayList = yDataArrayList
            centroidArray = frameSumHeightCentroidArray
            
        plot_single_kymograph(positionDataArrayList=positionDataArrayList,frameTimeStampArray=frameTimeStampArray,eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldDataArray,positionTimeArray=positionTimeArray,
                   centroidArray=centroidArray,pitchX=pitchX,pitchY=pitchY)
        
    else:
        plot_double_kymograph(xDataArrayList=xDataArrayList, yDataArrayList=yDataArrayList, frameTimeStampArray=frameTimeStampArray, eFieldTimeArray=eFieldTimeArray, eFieldDataArray=eFieldDataArray, positionTimeArray=positionTimeArray,
                              frameSumWidthCentroidArray=frameSumWidthCentroidArray, frameSumHeightCentroidArray=frameSumHeightCentroidArray, pitchX=pitchX,pitchY=pitchY,saveFig=saveFig,figurePath=figurePath)
        


def plot_single_kymograph(positionDataArrayList=[],frameTimeStampArray=np.array([]),eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),positionTimeArray=np.array([]),
                   centroidArray=np.array([]),pitchX=0.4,pitchY=0.4):
    
    global plotExtFieldKymo
    global plotCentroidKymo
    
    maxSumValue = max(np.ravel(positionDataArrayList))
    minSumValue = min(np.ravel(positionDataArrayList))
    
    
    startTime = frameTimeStampArray[0]
    stopTime = frameTimeStampArray[-1]
    
    averageFrameTime = frameTimeStampArray[-1]-frameTimeStampArray[1]
    averageFrameTime = averageFrameTime/(len(frameTimeStampArray)-1)
    
    
    fig, positionAxes = plt.subplots()
    eFieldAxes = positionAxes.twinx()
    positionArray = np.arange(len(positionDataArrayList[0]))*pitchX
    norm = plt.Normalize((minSumValue/maxSumValue), 0.8)
    for i in range(len(positionDataArrayList)):    
        
        #sumArray = np.ones(len(positionDataArrayList[i]))*frameTimeStampArray[i]-0.5*averageFrameTime
        sumArray = np.ones(len(positionDataArrayList[i]))*frameTimeStampArray[i]
                
        
        points = np.array([sumArray,positionArray]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-1],points[1:]],axis=1)
        lc = LineCollection(segments,cmap='viridis',lw=2,norm=norm)
        lc.set_array(positionDataArrayList[i][1:]/maxSumValue)
        yLine = positionAxes.add_collection(lc)

        
    positionAxes.set_title('Image profile kymograph',fontsize=20)
    positionAxes.set_ylabel('Particle position (um)',fontsize=15)
    positionAxes.set_xlabel('Time (s)',fontsize=15)  
    positionAxes.set_xlim(startTime, stopTime)
    positionAxes.set_ylim(0, positionArray[-1])    
    positionAxes.tick_params(labelsize=15)
    positionAxes.set_facecolor(cm.viridis(0))
    #fig.colorbar(yLine, ax=positionAxes)
    
    if(plotExtFieldKymo == True):
        eFieldAxes.plot(eFieldTimeArray,(eFieldDataArray/max(eFieldDataArray)),linestyle='-',color="Red",label="E-Field")
    if(plotCentroidKymo == True):
        positionAxes.plot(positionTimeArray,centroidArray,linestyle='-',lw=1.5,color="red",label="Centroid")
        
    
    plt.show()     
    
    
def plot_double_kymograph(xDataArrayList=[],yDataArrayList=[],frameTimeStampArray=np.array([]),eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),positionTimeArray=np.array([]),
                   frameSumWidthCentroidArray=np.array([]),frameSumHeightCentroidArray=np.array([]),pitchX=0.4e-6,pitchY=0.4e-6,saveFig=True,figurePath=""):
    global plotExtFieldKymo
    global plotCentroidKymo
    
    xMaxSumValue = max(np.ravel(xDataArrayList))
    xMinSumValue = min(np.ravel(xDataArrayList))
    
    yMaxSumValue = max(np.ravel(yDataArrayList))
    yMinSumValue = min(np.ravel(yDataArrayList))
    
    startTime = frameTimeStampArray[0]
    stopTime = frameTimeStampArray[-1]
    
    averageFrameTime = frameTimeStampArray[-1]-frameTimeStampArray[1]
    averageFrameTime = averageFrameTime/(len(frameTimeStampArray)-1)
    
    
    fig, (axPosition1,axPosition2) = plt.subplots(2,1,sharex=True,figsize=(15,3),dpi=200)
    eFieldAxes1 = axPosition1.twinx()
    eFieldAxes2 = axPosition2.twinx()
    
    yPositionArray = np.arange(len(yDataArrayList[0]))*pitchY
    norm = plt.Normalize((yMinSumValue/yMaxSumValue), 0.8)
    for i in range(len(yDataArrayList)):    
        
        #sumArray = np.ones(len(yDataArrayList[i]))*frameTimeStampArray[i]-0.5*averageFrameTime
        sumArray = np.ones(len(yDataArrayList[i]))*frameTimeStampArray[i]
        
              
        points = np.array([sumArray,yPositionArray]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-1],points[1:]],axis=1)
        lc = LineCollection(segments,cmap='Greens',lw=2,norm=norm)
        lc.set_array(yDataArrayList[i][1:]/yMaxSumValue)
        yLine = axPosition1.add_collection(lc)

        
    axPosition1.set(title='Image profile kymograph')
    axPosition1.set_xlim(startTime, stopTime)
    axPosition1.set_ylim(0, yPositionArray[-1])    
    axPosition1.tick_params(labelsize=15)
    axPosition1.set_facecolor(cm.Greens(0))
    fig.colorbar(yLine, ax=axPosition1)
    
    
    xPositionArray = np.arange(len(xDataArrayList[0]))*pitchX
    norm = plt.Normalize((xMinSumValue/xMaxSumValue), 0.8)
    for i in range(len(xDataArrayList)):    
        
        sumArray = np.ones(len(xDataArrayList[i]))*frameTimeStampArray[i]
        points = np.array([sumArray,xPositionArray]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-1],points[1:]],axis=1)
        lc = LineCollection(segments,cmap='Greens',lw=2,norm=norm)
        lc.set_array(xDataArrayList[i][1:]/xMaxSumValue)
        xLine = axPosition2.add_collection(lc)        
                           
        
        
    axPosition2.set(title='')
    axPosition2.set_xlim(startTime, stopTime)
    axPosition2.set_ylim(0, yPositionArray[-1])    
    axPosition2.tick_params(labelsize=15)
    axPosition2.set_facecolor(cm.Greens(0))
    fig.colorbar(xLine, ax=axPosition2)    
    
 
    if(plotExtFieldKymo == True):
        
        eFieldAxes1.plot(eFieldTimeArray,(eFieldDataArray/max(eFieldDataArray)),linestyle='-',color="cyan",label="E-Field")
        eFieldAxes2.plot(eFieldTimeArray,(eFieldDataArray/max(eFieldDataArray)),linestyle='-',color="cyan",label="E-Field")
    
    if(plotCentroidKymo == True):
        axPosition1.plot(positionTimeArray,frameSumHeightCentroidArray,linestyle='-',lw=1.5,color="red",label="Centroid")
        axPosition2.plot(positionTimeArray,frameSumWidthCentroidArray,linestyle='-',lw=1.5,color="red",label="Centroid")        
        
        
    if(saveFig == True):
        plt.savefig(figurePath, dpi=200)
        
        
    
    
    plt.show() 
    
    

def plot_frame_image_and_sums(frameArray=np.array([]),sumHeightArray=np.array([]),sumWidthArray=np.array([]),time=0,pitchX=0.4e-6,pitchY=0.4e-6):
    figure, axes = plt.subplots(nrows=2,ncols=2)
    axes[0,1].remove()    
    
    heightIndexArray = np.arange(len(sumHeightArray))

    widthIndexArray = np.arange(len(sumWidthArray))  
    
    maxFrameValue = 10
    maxWidthSumValue = 30
    maxHeightSumValue = 30

    x = np.arange(len(frameArray))*pitchX
    y = np.arange(len(frameArray[0]))*pitchY
    frame2DArray = np.zeros((len(x),len(y)))
    for i in range(len(frameArray)):
        for j in range(len(frameArray[i])):
            frame2DArray[i][j] = frameArray[i][j][0]
    
    

    axes[1,1].plot(sumWidthArray,widthIndexArray,lw=2,color=cm.Greens(255))
    axes[1,1].set_ylim([0,max(widthIndexArray)])
    
    axes[1,0].pcolormesh(y,x,frame2DArray,vmin=0,vmax=maxFrameValue,cmap="Greens")   
    
    axes[1,0].set_xlabel('x-position (um)',fontsize=20)
    axes[1,0].set_ylabel('y-position (um)',fontsize=20) 
    
    timeStampString = "T={0:.3f}s".format(time)
    
    axes[1,0].set_title(timeStampString,fontsize=10) 
    
    #axes[1,0].text(1,(max(y)-1),timeStampString,color='black')
    

    
    axes[0,0].plot(heightIndexArray,sumHeightArray,lw=2,color=cm.Greens(255))  
    axes[0,0].set_xlim([0,max(heightIndexArray)])
    
    axes[1,1].set_xlim([0,maxWidthSumValue])
    axes[0,0].set_ylim([0,maxHeightSumValue])
    
    plt.show()

from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui

def plot_frame_video_and_sums(frameArray=np.array([]), pitchX=0.4e-6,pitchY=0.4e-6, timeArray=np.array([])):
      
    frameArray = np.swapaxes(frameArray, 0, 3)
    frameArray = frameArray[:][:][:][0]

    frameArray = np.swapaxes(frameArray, 0, 2)

    app = pg.QtGui.QApplication([])

    #x = np.random.rand(500,50,50)

    pg.setConfigOptions(antialias=True)

    # main graphics window
    #view = pg.GraphicsView()

    # show the window
    #view.show()
    imv = pg.ImageView()
    imv.show()


    # add the plotItem to the graphicsWindow and set it as central

    # create an image object
    img = pg.ImageItem(border='w', levels=(frameArray.min(),frameArray.max()))
    tr = QtGui.QTransform()  # prepare ImageItem transformation:
    tr.scale(pitchX, pitchY)

    img.setTransform(tr)
    imv.setImage(frameArray, xvals=timeArray)
    app.exec_()
'''
    #can be used for video demonstration
    norm = mpl.colors.Normalize(vmin=0, vmax=frameArray.max())
    cmap = cm.jet
    m = cm.ScalarMappable(norm=norm, cmap=cmap)



    # data generator
    def animLoop():
        global cnt
        if cnt < frameArray.shape[0]:
            imv.setImage(m.to_rgba(frameArray[cnt]))
        else:
            cnt = 0
        cnt+=1
    #start = interval and interval = start
    timer = QtCore.QTimer()
    timer.setInterval(200)
    timer.timeout.connect(animLoop)
    timer.start(500)

    app.exec_()
'''
cnt=0
