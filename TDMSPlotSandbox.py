
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import LineCollection

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
        plot_trace(AODTimeArray=AODTimeArray, pixelNumberArray=pixelNumberArray, SPCMTimeArray=SPCMTimeArray, SPCMDataArray=SPCMDataArray, AOD1DataArray=AOD1DataArray, 
                          AOD2DataArray=AOD2DataArray, eFieldTimeArray=eFieldTimeArray, eFieldDataArray=eFieldDataArray, discontTimeArray=discontTimeArray, discontDataArray=discontDataArray, 
                          AODSyncTimeArray=AODSyncTimeArray, AODSyncDataArray=AODSyncDataArray, SPCMSyncDataArray=SPCMSyncDataArray, SPCMSyncTimeArray=SPCMSyncTimeArray,yLabel=yLabel)


def plot_trace(AODTimeArray=np.array([]),pixelNumberArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),AOD1DataArray=np.array([]),AOD2DataArray=np.array([]),
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
                ax.plot(AODTimeArray,AOD1DataArray/max(AOD1DataArray),linestyle='-',color="lightgreen",label="AOD1")
                ax.plot(AODTimeArray,AOD2DataArray/max(AOD2DataArray),linestyle='-',color="turquoise",label="AOD2")
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
         
        
    ax.set(title='Time traces')
    ax.tick_params(labelsize=15)
    plt.xlabel("time (s)", fontsize = 15)
    plt.ylabel(yLabel, fontsize = 15)
    ax.legend()
    ax.grid()
    plt.show()
    

    
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
        
    
    positionVelocityFig, positionVelocityAxes = plt.subplots(nrows=2,ncols=1)
        
    positionAx1 = positionVelocityAxes[0]
    positionAx2 = positionAx1.twinx()
    lineListPosition = []    
    
    velocityAx1 = positionVelocityAxes[1]
    velocityAx2 = velocityAx1.twinx()
    lineListVelocity = []    
    
    if(plotExtField == True):
        stopIndexEField = np.where(eFieldTimeArray <= positionTimeArray[-1])[0][-1]
            
        
        line = positionAx2.plot(eFieldTimeArray[:stopIndexEField],eFieldDataArray[:stopIndexEField]/max(eFieldDataArray[:stopIndexEField]),color="green",label="E/Emax")
        lineListPosition = lineListPosition + line
        positionAx2.set_ylabel('E-Field/max(E-Field)')
        positionAx2.yaxis.label.set_color("green")
        
        line = velocityAx2.plot(eFieldTimeArray[:stopIndexEField],eFieldDataArray[:stopIndexEField]/max(eFieldDataArray[:stopIndexEField]),color="green",label="E/Emax")
        lineListVelocity = lineListVelocity + line
        velocityAx2.set_ylabel('E-Field/max(E-Field)')
        velocityAx2.yaxis.label.set_color("green")
        
    if(plotHeight == True):
        line = positionAx1.plot(frameTimeStampArray,heightPositionArray*1e6,linestyle='',marker='o',color="salmon",label="y-position")
        lineListPosition = lineListPosition + line
        line = positionAx1.plot(positionTimeArray,filteredHeightPositionArray*1e6,color="darkred",label="y-position (filter)")
        lineListPosition = lineListPosition + line
        
        line = velocityAx1.plot(velocityTimeArray,heightVelocityArray*1e3,color="red",label="y-velocity")
        lineListVelocity = lineListVelocity + line
        
        
    
    if(plotWidth == True):
        line = positionAx1.plot(frameTimeStampArray,widthPositionArray*1e6,linestyle='',marker='o',color="lightblue",label="x-position")
        lineListPosition = lineListPosition + line
        line = positionAx1.plot(positionTimeArray,filteredWidthPositionArray*1e6,color="darkblue",label="x-position (filter)")
        lineListPosition = lineListPosition + line
        
        line = velocityAx1.plot(velocityTimeArray,widthVelocityArray*1e3,color="blue",label="x-velocity")   
        lineListVelocity = lineListVelocity + line
        
    
    labels = [line.get_label() for line in lineListPosition]
    positionAx2.legend(lineListPosition,labels)
    positionAx1.set_title('Particle position trace')
    positionAx1.set_ylabel('Particle position (um)')
    positionAx1.set_xlabel('Time (s)')
    
    labels = [line.get_label() for line in lineListVelocity]
    velocityAx2.legend(lineListVelocity,labels)    
    velocityAx1.set_title('Particle velocity trace')
    velocityAx1.set_ylabel('Particle velocity (mm/s)')
    velocityAx1.set_xlabel('Time (s)')
    
    
    return positionAx1, velocityAx1   
    


def plot_overlapping_periods(timeArrayList=[],dataArrayList=[],eFieldFreq=100):
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
        
        eLine = eFieldPeriodAxes.plot(eFieldTimeArray,eFieldDataArray,color="green",label="E/Emax")
        
        lineList.append(eLine[0])
        labelList.append(eLine[0].get_label())
        
        eFieldPeriodAxes.set_ylabel('E-Field/max(E-Field)')
        eFieldPeriodAxes.yaxis.label.set_color("green")    
        
        
    periodOverlapAxes.legend(lineList,labelList)
    periodOverlapAxes.set_title('Particle velocity at centerline')
    periodOverlapAxes.set_ylabel('Particle velocity (mm/s)')
    periodOverlapAxes.set_xlabel('Normalized time (time/period) (a.u.)')    
    plt.show()
    
    
def plot_fitted_velocity_scatter_plot(fittedVelocityList=[],fittedCovVelocityList=[]):
    fitteduEPArray = np.array([])
    fitteduEOArray = np.array([])
    
    for i in range(len(fittedVelocityList)):
        fitteduEPArray = np.append(fitteduEPArray,fittedVelocityList[i][0])
        fitteduEOArray = np.append(fitteduEOArray,fittedVelocityList[i][1])
        
    
    fig, ax = plt.subplots()
    
    ax.plot(fitteduEOArray,fitteduEPArray,color="red",marker="o",linestyle="",label="Fitted Data")
    
    ax.legend()
    ax.set_title('Electrophoretic vs Electroosmotic velocity')
    ax.set_ylabel('Electrophoretic velocity (mm/s)')
    ax.set_xlabel('Electroosmotic velocity (mm/s)')
    plt.show()
    
    
def plot_kymograph(xDataArrayList=[],yDataArrayList=[],frameTimeStampArray=np.array([]),eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),positionTimeArray=np.array([]),
                   frameSumWidthCentroidArray=np.array([]),frameSumHeightCentroidArray=np.array([]),pitch=0.4e-6,offsetFactor=1.0):
    global plotExtFieldKymo
    global plotCentroidKymo
    
    xMaxSumValue = max(np.ravel(xDataArrayList))
    xMinSumValue = min(np.ravel(xDataArrayList))
    
    yMaxSumValue = max(np.ravel(yDataArrayList))
    yMinSumValue = min(np.ravel(yDataArrayList))
    yOffset = 0
    
    startTime = frameTimeStampArray[0]
    stopTime = frameTimeStampArray[-1]
    
    averageFrameTime = frameTimeStampArray[-1]-frameTimeStampArray[1]
    averageFrameTime = averageFrameTime/(len(frameTimeStampArray)-1)
    
    
    fig, (ax1,ax2) = plt.subplots(2,1,sharex=True)
    yPositionArray = np.arange(len(yDataArrayList[0]))*pitch
    norm = plt.Normalize((yMinSumValue/yMaxSumValue), 0.8)
    for i in range(len(yDataArrayList)):    
        
        sumArray = np.ones(len(yDataArrayList[i]))*frameTimeStampArray[i]-0.5*averageFrameTime
        
        
        points = np.array([sumArray,yPositionArray]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-1],points[1:]],axis=1)
        lc = LineCollection(segments,cmap='viridis',lw=2,norm=norm)
        lc.set_array(yDataArrayList[i][1:]/yMaxSumValue)
        yLine = ax1.add_collection(lc)

        
    ax1.set(title='Time traces of SPCM')
    ax1.set_xlim(startTime, stopTime)
    ax1.set_ylim(0, yPositionArray[-1])    
    ax1.tick_params(labelsize=15)
    ax1.set_facecolor(cm.viridis(0))
    fig.colorbar(yLine, ax=ax1)
    
    
    xPositionArray = np.arange(len(xDataArrayList[0]))*pitch
    norm = plt.Normalize((xMinSumValue/xMaxSumValue), 0.8)
    for i in range(len(xDataArrayList)):    
       
        sumArray = 3*averageFrameTime*((xDataArrayList[i])/(xMaxSumValue)) + frameTimeStampArray[i]
        
        points = np.array([sumArray,xPositionArray]).T.reshape(-1,1,2)
        segments = np.concatenate([points[:-1],points[1:]],axis=1)
        lc = LineCollection(segments,cmap='viridis',lw=2,norm=norm)
        lc.set_array(xDataArrayList[i][1:]/xMaxSumValue)
        xLine = ax2.add_collection(lc)
        
        
        
        
        
    ax2.set(title='')
    ax2.set_xlim(startTime, stopTime)
    ax2.set_ylim(0, yPositionArray[-1])    
    ax2.tick_params(labelsize=15)
    ax2.set_facecolor(cm.viridis(0))
    fig.colorbar(xLine, ax=ax2)    
    
 
    if(plotExtFieldKymo == True):
        
        ax1.plot(eFieldTimeArray,(eFieldDataArray/max(eFieldDataArray))*6,linestyle='-',color="Red",label="E-Field")
        ax2.plot(eFieldTimeArray,(eFieldDataArray/max(eFieldDataArray))*6,linestyle='-',color="Red",label="E-Field")
    
    if(plotCentroidKymo == True):
        ax1.plot(positionTimeArray,frameSumHeightCentroidArray,linestyle='-',color="Green",label="Centroid")
        ax2.plot(frameTimeStampArray,frameSumWidthCentroidArray,linestyle='-',color="Green",label="Centroid")        
        
        
    
    return ax1
