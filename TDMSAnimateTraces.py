import numpy as np
import os
import easygui
from nptdms import TdmsFile
import TDMSPlotTraces as tdmsPlot
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy.signal as ss
from PIL import Image
import cv2
import skvideo.io
from moviepy.editor import VideoFileClip, concatenate_videoclips
from matplotlib import animation
from matplotlib import cm
from matplotlib.collections import LineCollection
import moviepy.editor as mp
from scipy.optimize import curve_fit

#global variables used to exchange data between functions in/outside of TDMSAnimateTraces 
globalArrayList1 = []
globalArrayList2 = []
globalArrayList3 = []
globalSigmaArray = np.array([])
globalAmplitudeArray = np.array([])
globalCentroidArray = np.array([])
globalEfieldArray = np.array([])
globalPlotLine1 = None
globalPlotLine2 = None
globalPlotArray = None
globalPlotText = None
globalFrameTimeStampArray = np.array([])

globalCounter = None
globalMaxSum1 = 0
globalMaxSum2 = 0

animationFigure = None
animationAxes = None
animationArrow = None
animationArrowCenter = None
animationCentroidLine1 = None
animationCentroidLine2 = None

addCentroidLine = False
displayTimeStamp = True
onlyImage = False
singleAxisSum = False
liveAnimation = False
saveVideo = False
combineVideos = True
animate = True
centroidCalculation = "gaussian fit"
darkCount = 1

maxFramesPerFragment = 300
dpi = 72
fps = 30
pitchX = 0.4e-6
pitchY = 0.4e-6
pixelsPerFrame = 16*16

# Generates the figures and axes references, based on the type of animation to be generated (based on global boolean values, the axes will change)

# Output: - animationFigure: Reference to the figure to be used for frame per frame animation
#         - animationAxes: Reference to the axes of the animation figure

def generate_figure_and_axes():
    global animationFigure
    global animationAxes
    global onlyImage
    
    if(onlyImage == True):
        animationFigure, animationAxes = plt.subplots()
    else:
        if(singleAxisSum == True):
            animationFigure, animationAxes = plt.subplots(nrows=2,ncols=1)
        else:
            animationFigure, animationAxes = plt.subplots(nrows=2,ncols=2)
            animationAxes[0,1].remove()            
    
    return animationFigure, animationAxes
   
def animate_image(i):
    global globalArrayList3
    global animationFigure
    global animationAxes
    global globalFrameTimeStampArray
    global displayTimeStamp    
    global maxFramesPerFragment
    global globalCounter    
    global animationArrow
    global animationArrowCenter    
    global globalEfieldArray
    
    frameArray = globalArrayList3[i]
    timeStamp = globalFrameTimeStampArray[i]
    globalCounter = globalCounter + 1
    sineAmplitude = globalEfieldArray[i] 
    
    frame2DArray = np.zeros((len(frameArray),len(frameArray[0])))
    for i in range(len(frameArray)):
        for j in range(len(frameArray[i])):
            frame2DArray[i][j] = frameArray[i][j][0]
        
    globalPlotArray.set_array(frame2DArray[:-1,:-1].ravel())
    
    
    animationArrow.xy = (animationArrowCenter[0]+sineAmplitude,animationArrowCenter[1])
    
    if(displayTimeStamp == True):
        animationAxes.set_title("T={0:.6f}s".format(timeStamp),fontsize=20)
    
    animationFigure.canvas.draw()
    
    if(globalCounter == maxFramesPerFragment):
        plt.close()
    
def init_animate_image():
    global globalArrayList3
    global animationFigure
    global animationAxes
    global globalPlotArray
    global globalPlotText
    global displayTimeStamp
    global globalCounter
    global pitchX
    global pitchY
    global animationArrow
    global animationArrowCenter  
    
    
    globalCounter = 0

    frameArray = globalArrayList3[0]

    x = np.arange(len(frameArray))*pitchX*1e6
    y = np.arange(len(frameArray[0]))*pitchY*1e6
    frame2DArray = np.zeros((len(x),len(y)))
    for i in range(len(frameArray)):
        for j in range(len(frameArray[i])):
            frame2DArray[i][j] = frameArray[i][j][0]

    globalPlotArray = animationAxes.pcolormesh(y,x,frame2DArray)   
    
    animationAxes.set_xlabel('x-position (um)',fontsize=20)
    animationAxes.set_ylabel('y-position (um)',fontsize=20) 
    animationAxes.tick_params(axis='both',labelsize=12)
    
    
    
    arrowPositionIndexX = int(len(x)*0.5)
    arrowPositionIndexY = int(len(y)*0.1)
    
    animationArrowCenter = (x[arrowPositionIndexX],y[arrowPositionIndexY])
    animationArrow = animationAxes.annotate("", xy=animationArrowCenter, xytext=animationArrowCenter,arrowprops={"facecolor": "white"}) 
    animationAxes.text(animationArrowCenter[0]-1.3,(animationArrowCenter[1]+max(y)*0.05),s="E-Field",color="white",weight="bold",fontsize=12)    
    
    if(displayTimeStamp == True):
        animationAxes.set_title(" ",fontsize=20)    
    
    animationAxes.set_aspect('equal')
    animationFigure.tight_layout()

def animate_image_and_single_sum(i):
    global globalArrayList1
    global globalArrayList3
    global animationFigure
    global animationAxes
    global globalPlotArray
    global globalPlotLine1
    global globalPlotLine2    
    global globalFrameTimeStampArray
    global displayTimeStamp
    global maxFramesPerFragment
    global globalCounter
    global globalAmplitudeArray
    global globalSigmaArray
    global globalCentroidArray
    global animationArrow
    global animationArrowCenter    
    global globalEfieldArray  
    global animationCentroidLine1
    global animationCentroidLine2   
    global pitchX
    global pitchY
    global addCentroidLine
    
    
    
    
    sumArray1 = globalArrayList1[i]
    frameArray = globalArrayList3[i]
    timeStamp = globalFrameTimeStampArray[i]
    globalCounter = globalCounter + 1
    sineAmplitude = globalEfieldArray[i]
    
    amplitude = globalAmplitudeArray[i]
    sigma = globalSigmaArray[i]
    mu = globalCentroidArray[i]
    fitArray = np.array([])
    
    pixelNumberArray = np.arange(len(sumArray1))
    fitArray = amplitude*np.exp(-0.5*np.square(pixelNumberArray-mu)/sigma)    
    
    frame2DArray = np.zeros((len(frameArray),len(frameArray[0])))
    for i in range(len(frameArray)):
        for j in range(len(frameArray[i])):
            frame2DArray[i][j] = frameArray[i][j][0]
        
    globalPlotLine2.set_ydata(fitArray)
    globalPlotLine1.set_ydata(sumArray1)
    globalPlotArray.set_array(frame2DArray[:-1,:-1].ravel())
    
    animationAxes[0].set_xlim([0,max(pixelNumberArray*pitchX*1e6)])
    animationAxes[1].set_xlim([0,max(pixelNumberArray*pitchX*1e6)])
    
    animationArrow.xy = (animationArrowCenter[0]+sineAmplitude,animationArrowCenter[1])
    if(addCentroidLine == True):
        animationCentroidLine1.remove()
        animationCentroidLine2.remove()
        animationCentroidLine1 = animationAxes[0].axvline(x=mu*pitchX*1e6,color="red")
        animationCentroidLine2 = animationAxes[1].axvline(x=mu*pitchX*1e6,color="red")    
    """
    if(displayTimeStamp == True):
        globalPlotText.set_text("T={0:.3f}s".format(timeStamp))
    
    """
    if(displayTimeStamp == True):
        animationAxes[0].set_title("T={0:.3f}s".format(timeStamp),fontsize=15)    
    
    
    animationFigure.canvas.draw()
    
    
    if(globalCounter == maxFramesPerFragment):
        plt.close()

def init_animate_image_and_single_sum():
    global globalArrayList1
    global globalArrayList2
    global globalArrayList3
    global globalSigmaArray
    global globalAmplitudeArray   
    global globalCentroidArray
    global animationFigure
    global animationAxes
    global globalPlotArray
    global globalPlotLine1
    global globalPlotLine2
    global globalPlotText
    global displayTimeStamp
    global globalCounter
    global globalMaxSum1
    global pitchX
    global pitchY
    global animationArrow
    global animationArrowCenter  
    global animationCentroidLine1
    global animationCentroidLine2 
    global addCentroidLine
    
    globalCounter = 0
    
    sumArray1 = globalArrayList1[0]
    indexArray1 = np.arange(len(sumArray1))
    
    
    amplitude = globalAmplitudeArray[0]
    sigma = globalSigmaArray[0]
    mu = globalCentroidArray[0]
    fitArray = np.array([])
    
    fitArray = amplitude*np.exp(-0.5*np.square(indexArray1-mu)/sigma)

    frameArray = globalArrayList3[0]

    x = np.arange(len(frameArray))*pitchX*1e6
    y = np.arange(len(frameArray[0]))*pitchY*1e6
    frame2DArray = np.zeros((len(x),len(y)))
    for i in range(len(frameArray)):
        for j in range(len(frameArray[i])):
            frame2DArray[i][j] = frameArray[i][j][0]
    


    
    globalPlotArray = animationAxes[1].pcolormesh(y,x,frame2DArray)   
    
    animationAxes[1].set_xlabel('x-position (um)',fontsize=15)
    animationAxes[1].set_ylabel('y-position (um)',fontsize=15)    
    animationAxes[1].tick_params(axis='both',labelsize=10)
    """
    if(displayTimeStamp == True):
        globalPlotText = animationAxes[1].text(1,(max(y)-1),str(""),color='white')
    """
    
    globalPlotLine1 = animationAxes[0].plot(y,sumArray1,color='blue')[0]  
    globalPlotLine2 = animationAxes[0].plot(y,fitArray,color="red")[0]
    if(addCentroidLine == True):
        animationCentroidLine1 = animationAxes[0].axvline(x=mu*pitchX*1e6,color="red")
        animationCentroidLine2 = animationAxes[1].axvline(x=mu*pitchX*1e6,color="red")
    
    animationAxes[0].set_xlim([0,max(y)])
    animationAxes[0].set_ylim([0,1.1*max(globalAmplitudeArray)]) 
    
    animationAxes[0].set_ylabel('Pixel sum (a.u.)',fontsize=15)    
    animationAxes[0].tick_params(axis='both',labelsize=10)    
    
    arrowPositionIndexX = int(len(x)*0.5)
    arrowPositionIndexY = int(len(y)*0.1)
    
    animationArrowCenter = (x[arrowPositionIndexX],y[arrowPositionIndexY])
    animationArrow = animationAxes[1].annotate("", xy=animationArrowCenter, xytext=animationArrowCenter,arrowprops={"facecolor": "white"}) 
    animationAxes[1].text(animationArrowCenter[0]-1.3,(animationArrowCenter[1]+max(y)*0.05),s="E-Field",color="white",weight="bold",fontsize=12)     
    
    if(displayTimeStamp == True):
        animationAxes[0].set_title(" ",fontsize=20)
        
    ratio = max(y)/(1.1*max(globalAmplitudeArray))
    
    animationAxes[0].set_aspect(ratio)
    animationAxes[0].grid()
    animationAxes[1].set_aspect('equal')
    animationFigure.tight_layout()
    
    

def animate_image_and_sums(i):
    global globalArrayList3
    global animationFigure
    global animationAxes
    global globalPlotArray
    global globalPlotLine1
    global globalPlotLine2    
    global globalFrameTimeStampArray
    global displayTimeStamp
    global maxFramesPerFragment
    global globalCounter
    global globalMaxSum1
    global globalMaxSum2
    
    
    sumArray1 = globalArrayList1[i]
    sumArray2 = globalArrayList2[i]
    frameArray = globalArrayList3[i]
    timeStamp = globalFrameTimeStampArray[i]
    globalCounter = globalCounter + 1
    
    frame2DArray = np.zeros((len(frameArray),len(frameArray[0])))
    for i in range(len(frameArray)):
        for j in range(len(frameArray[i])):
            frame2DArray[i][j] = frameArray[i][j][0]
        
    globalPlotLine2.set_xdata(sumArray2)
    globalPlotLine1.set_ydata(sumArray1)
    globalPlotArray.set_array(frame2DArray[:-1,:-1].ravel())
    
    if(displayTimeStamp == True):
        globalPlotText.set_text("T={0:.3f}s".format(timeStamp))
    
    
    
    
    animationFigure.canvas.draw()
    
    
    
    if(globalCounter == maxFramesPerFragment):
        plt.close()

def init_animate_image_and_sums():
    global globalArrayList1
    global globalArrayList2
    global globalArrayList3
    global animationFigure
    global animationAxes
    global globalPlotArray
    global globalPlotLine1
    global globalPlotLine2
    global globalPlotText
    global displayTimeStamp
    global globalCounter
    global globalMaxSum1
    global globalMaxSum2
    global pitchX
    global pitchY
    
    globalCounter = 0
    
    sumArray1 = globalArrayList1[0]
    indexArray1 = np.arange(len(sumArray1))

    sumArray2 = globalArrayList2[0]
    indexArray2 = np.arange(len(sumArray2))    

    frameArray = globalArrayList3[0]

    x = np.arange(len(frameArray))*pitchX
    y = np.arange(len(frameArray[0]))*pitchY
    frame2DArray = np.zeros((len(x),len(y)))
    for i in range(len(frameArray)):
        for j in range(len(frameArray[i])):
            frame2DArray[i][j] = frameArray[i][j][0]
    


    globalPlotLine2 = animationAxes[1,1].plot(sumArray2,indexArray2)[0]
    animationAxes[1,1].set_ylim([0,max(indexArray2)])
    #animationAxes[1,1].set_yticks(indexArray2,minor=True)
    #animationAxes[1,1].grid(b=True,which='minor',axis='y',markevery=1)
    
    globalPlotArray = animationAxes[1,0].pcolormesh(y,x,frame2DArray,vmin=150,vmax=255,cmap="Greens")   
    
    animationAxes[1,0].set_xlabel('x-position (um)',fontsize=20)
    animationAxes[1,0].set_ylabel('y-position (um)',fontsize=20)    
    
    if(displayTimeStamp == True):
        globalPlotText = animationAxes[1,0].text(1,(max(y)-1),str(""),color='white')
    
    
    globalPlotLine1 = animationAxes[0,0].plot(indexArray1,sumArray1)[0]    
    animationAxes[0,0].set_xlim([0,max(indexArray1)])
    #animationAxes[0,0].grid(b=True,axis='x',markevery=0.1)
    
    animationAxes[1,1].set_xlim([100,50000])
    animationAxes[0,0].set_ylim([100,50000]) 
    
    
def init_animation():
    global onlyImage
    
    if(onlyImage == True):
        init_animate_image()
    else:
        if(singleAxisSum == True):
            init_animate_image_and_single_sum()
        else:
            init_animate_image_and_sums()
 
def split_segment_into_fragments(pixelNumberArray=np.array([]),AODTimeArray=np.array([]),AOD1DataArray=np.array([]),AOD2DataArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([])):
    global pixelsPerFrame
    global maxFramesPerFragment
    
    SPCMTimeFragmentArrayList = []
    SPCMDataFragmentArrayList = []
    AODTimeFragmentArrayList = []
    AOD1DataFragmentArrayList = []
    AOD2DataFragmentArrayList = []
    pixelNumberFragmentArrayList = []
    
    maxPixelNumberIndexArray = np.where(pixelNumberArray == max(pixelNumberArray))[0]
    minPixelNumberIndexArray = np.where(pixelNumberArray == min(pixelNumberArray))[0]
    
    if(maxPixelNumberIndexArray[0] < minPixelNumberIndexArray[0]):
        maxPixelNumberIndexArray = maxPixelNumberIndexArray[1:]
    
    startIndexArray = np.array([])
    stopIndexArray = np.array([])
    
    
    numberOfFragments = min(int(len(minPixelNumberIndexArray)/maxFramesPerFragment),int(len(maxPixelNumberIndexArray)/maxFramesPerFragment))    
    
    
    for i in range(numberOfFragments+1):
        startIndexArray = np.append(startIndexArray, minPixelNumberIndexArray[i*maxFramesPerFragment])
        
        
    for i in range(len(startIndexArray)-1):
        startIndex = startIndexArray[i]
        stopIndex = startIndexArray[i+1] + 1
        
        AODTimeFragmentArrayList.append(AODTimeArray[int(startIndex):int(stopIndex)])
        AOD1DataFragmentArrayList.append(AOD1DataArray[int(startIndex):int(stopIndex)])
        AOD2DataFragmentArrayList.append(AOD2DataArray[int(startIndex):int(stopIndex)])
        pixelNumberFragmentArrayList.append(pixelNumberArray[int(startIndex):int(stopIndex)])
        
        startTime = AODTimeArray[int(startIndex):int(stopIndex)][0]
        stopTime = AODTimeArray[int(startIndex):int(stopIndex)][-1]
        
        startIndex = len(np.where(SPCMTimeArray < startTime)[0]) 
        stopIndex = len(np.where(SPCMTimeArray < stopTime)[0]) 
        
        SPCMTimeFragmentArrayList.append(SPCMTimeArray[int(startIndex):int(stopIndex)])
        SPCMDataFragmentArrayList.append(SPCMDataArray[int(startIndex):int(stopIndex)])       
        
    
    
    
    return SPCMTimeFragmentArrayList, SPCMDataFragmentArrayList, AODTimeFragmentArrayList, AOD1DataFragmentArrayList, AOD2DataFragmentArrayList,pixelNumberFragmentArrayList



def generate_video_from_segment(pixelNumberArray=np.array([]),AODTimeArray=np.array([]),AOD1DataArray=np.array([]),
                                AOD2DataArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),eFieldTimeArray=np.array([]),
                                eFieldDataArray=np.array([]),
                                rollImage=False,rollAxis=0,rollPixels=1,
                                tdmsFolderPath="",experimentName=""):
   
    
    global globalArrayList1
    global globalArrayList2
    global globalArrayList3
    global globalFrameTimeStampArray
    global animationFigure
    global animationAxes
    global onlyImage
    global liveAnimation
    global combineVideos
    global globalCounter
    global maxFramesPerFragment
    global saveVideo
    global animate
    global fps
    global dpi
    global globalEfieldArray
    global globalSigmaArray
    global globalAmplitudeArray
    global globalCentroidArray
    global pitchX
    global pitchY
    
    videoPathList = []
    frameTimeStampArray = np.array([])
    frameArrayListList = []
    frameTimeStampArrayList = []
    frameSumHeightArrayListList = []
    frameSumWidthArrayListList = []
    frameSumHeightCentroidArrayList = []
    frameSumWidthCentroidArrayList = []
    globalEfieldArray = np.array([])
    
    SPCMTimeFragmentArrayList, SPCMDataFragmentArrayList, AODTimeFragmentArrayList, AOD1DataFragmentArrayList, AOD2DataFragmentArrayList,pixelNumberFragmentArrayList = split_segment_into_fragments(pixelNumberArray=pixelNumberArray,AODTimeArray=AODTimeArray,
                                 AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray)
    """
    pixelsPerFrame = max(pixelNumberArray) + 1
    pixelsInFragment = int(pixelsPerFrame * maxFramesPerFragment)
    numberOfFragments = int(min(len(AODTimeArray),len(SPCMTimeArray))/pixelsInFragment)
    """
    for i in range(len(SPCMTimeFragmentArrayList)):
        """
        AODTimeFragmentArray = AODTimeArray[int(i*pixelsInFragment):int((i+1)*pixelsInFragment)]
        AOD1DataFragmentArray = AOD1DataArray[int(i*pixelsInFragment):int((i+1)*pixelsInFragment)]
        AOD2DataFragmentArray = AOD2DataArray[int(i*pixelsInFragment):int((i+1)*pixelsInFragment)]
        
        startTime = AODTimeArray[int(i*pixelsInFragment)]
        stopTime = AODTimeArray[int((i+1)*pixelsInFragment)]  
        startIndex = len(np.where(SPCMTimeArray < startTime)[0]) 
        stopIndex = len(np.where(SPCMTimeArray < stopTime)[0])   
        
        SPCMTimeFragmentArray = SPCMTimeArray[startIndex:stopIndex]
        SPCMDataFragmentArray = SPCMDataArray[startIndex:stopIndex]
        """
        
        AODTimeFragmentArray = AODTimeFragmentArrayList[i]
        AOD1DataFragmentArray = AOD1DataFragmentArrayList[i]
        AOD2DataFragmentArray = AOD2DataFragmentArrayList[i]
        SPCMTimeFragmentArray = SPCMTimeFragmentArrayList[i]
        SPCMDataFragmentArray = SPCMDataFragmentArrayList[i]
        pixelNumberFragmentArray = pixelNumberFragmentArrayList[i]
      
    
        frameArrayList, frameSumWidthArrayList, frameSumHeightArrayList, frameSumWidthCentroidArray ,frameSumHeightCentroidArray, frameTimeStampArray,frameSumHeightAmplitudeArray,frameSumHeightSigmaArray,frameSumWidthAmplitudeArray,frameSumWidthSigmaArray  = generate_frame_list_from_fragment(AODTimeArray=AODTimeFragmentArray,AOD1DataArray=AOD1DataFragmentArray,
                                                          AOD2DataArray=AOD2DataFragmentArray,pixelNumberArray=pixelNumberFragmentArray,SPCMTimeArray=SPCMTimeFragmentArray,SPCMDataArray=SPCMDataFragmentArray,
                                                          rollImage=rollImage,rollAxis=rollAxis,rollPixels=rollPixels)
        
        eFieldFrameTimeArray = np.array([])
        globalEfieldArray = np.array([])
        eFieldAmp = max(eFieldDataArray)
        for frameTimeStamp in frameTimeStampArray:
            timeIndex = int(len(np.where(eFieldTimeArray < frameTimeStamp)[0]))
            value = eFieldDataArray[timeIndex]/eFieldAmp
            eFieldFrameTimeArray = np.append(eFieldFrameTimeArray,eFieldTimeArray[timeIndex])
            globalEfieldArray = np.append(globalEfieldArray,value)
            
        
        
        
        
        globalArrayList1 = frameSumHeightArrayList
        globalArrayList2 = frameSumWidthArrayList
        globalArrayList3 = frameArrayList
        globalFrameTimeStampArray = frameTimeStampArray
        
        globalAmplitudeArray = frameSumHeightAmplitudeArray
        globalSigmaArray = frameSumHeightSigmaArray
        globalCentroidArray = frameSumHeightCentroidArray
        
      
        frameTimeStampArrayList.append(frameTimeStampArray)
        frameArrayListList.append(frameArrayList)
        frameSumWidthCentroidArrayList.append(frameSumWidthCentroidArray)
        frameSumWidthArrayListList.append(frameSumWidthArrayList)
        frameSumHeightCentroidArrayList.append(frameSumHeightCentroidArray)
        frameSumHeightArrayListList.append(frameSumHeightArrayList)
        
        
        
        if(animate == True):
            animationFigure, animationAxes = generate_figure_and_axes()
            init_animation()
            writer = animation.writers['ffmpeg'](fps=fps)
        
            if(onlyImage == True):
                ani = animation.FuncAnimation(animationFigure, animate_image,frames=len(globalArrayList3),interval=100)
            else:
                if(singleAxisSum == True):
                    ani = animation.FuncAnimation(animationFigure, animate_image_and_single_sum,frames=len(globalArrayList3),repeat=False,interval = 100)
                else:
                    ani = animation.FuncAnimation(animationFigure, animate_image_and_sums,frames=len(globalArrayList3),repeat=False,interval=100)
                    
            if(saveVideo == True):
                print('Writing frames to: {}_{}.mp4'.format(experimentName,i))
                videoPath = os.path.join(tdmsFolderPath,"{}_{}.mp4".format(experimentName,i))
                videoPathList.append(videoPath)
                ani.save(videoPath,writer=writer,dpi=dpi)
        
        if(liveAnimation == True):
            print('Displaying frames')      
            for i in range(len(frameArrayList)):
                tdmsPlot.plot_frame_image_and_sums(frameArray=frameArrayList[i],sumHeightArray=frameSumHeightArrayList[i],sumWidthArray=frameSumWidthArrayList[i],time=frameTimeStampArray[i],pitchX=pitchX,pitchY=pitchY)
                    
                 
            
            
                
    
    if((saveVideo == True) and (combineVideos == True) and (animate == True)):
        concatenate_videos(videoPathList=videoPathList,experimentName=experimentName)
        #for i in range(len(videoPathList)):
         #   os.remove(videoPathList[i])
        
    
    return frameTimeStampArrayList,frameArrayListList,frameSumWidthArrayListList,frameSumHeightArrayListList, frameSumWidthCentroidArrayList, frameSumHeightCentroidArrayList

def search_time_index(AODTimeFragmentArrayList=np.array([]), time=0):
    AODTimeFragmentArray = np.concatenate(AODTimeFragmentArrayList).ravel()
    Index = np.abs(AODTimeFragmentArray - time).argmin()
    AODTime = AODTimeFragmentArray[Index]
    for i, e in enumerate(AODTimeFragmentArrayList):
        if AODTime in e:
            return i



def generate_picture_from_segment(pixelNumberArray=np.array([]),AODTimeArray=np.array([]),AOD1DataArray=np.array([]),
                                AOD2DataArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),eFieldTimeArray=np.array([]),
                                eFieldDataArray=np.array([]),
                                rollImage=False,rollAxis=0,rollPixels=1,
                                tdmsFolderPath="",experimentName="", time=0):
   
    
    global globalArrayList1
    global globalArrayList2
    global globalArrayList3
    global globalFrameTimeStampArray
    global animationFigure
    global animationAxes
    global onlyImage
    global liveAnimation
    global combineVideos
    global globalCounter
    global maxFramesPerFragment
    global saveVideo
    global animate
    global fps
    global dpi
    global globalSigmaArray
    global globalAmplitudeArray
    global globalCentroidArray
    global pitchX
    global pitchY

    frameTimeStampArray = np.array([])
    
    SPCMTimeFragmentArrayList, SPCMDataFragmentArrayList, AODTimeFragmentArrayList, AOD1DataFragmentArrayList, AOD2DataFragmentArrayList,pixelNumberFragmentArrayList = split_segment_into_fragments(pixelNumberArray=pixelNumberArray,AODTimeArray=AODTimeArray,
                                 AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray)

    i = search_time_index(AODTimeFragmentArrayList=AODTimeFragmentArrayList, time=time)

        
    AODTimeFragmentArray = AODTimeFragmentArrayList[i]
    AOD1DataFragmentArray = AOD1DataFragmentArrayList[i]
    AOD2DataFragmentArray = AOD2DataFragmentArrayList[i]
    SPCMTimeFragmentArray = SPCMTimeFragmentArrayList[i]
    SPCMDataFragmentArray = SPCMDataFragmentArrayList[i]
    pixelNumberFragmentArray = pixelNumberFragmentArrayList[i]
      
    
    frameArrayList, frameSumWidthArrayList, frameSumHeightArrayList, frameSumWidthCentroidArray ,frameSumHeightCentroidArray, frameTimeStampArray,frameSumHeightAmplitudeArray,frameSumHeightSigmaArray,frameSumWidthAmplitudeArray,frameSumWidthSigmaArray  = generate_frame_list_from_fragment(AODTimeArray=AODTimeFragmentArray,AOD1DataArray=AOD1DataFragmentArray,
                                                          AOD2DataArray=AOD2DataFragmentArray,pixelNumberArray=pixelNumberFragmentArray,SPCMTimeArray=SPCMTimeFragmentArray,SPCMDataArray=SPCMDataFragmentArray,
                                                          rollImage=rollImage,rollAxis=rollAxis,rollPixels=rollPixels)
        
         
    print('Displaying frames')    
    tdmsPlot.plot_frame_video_and_sums(frameArray=np.array(frameArrayList),sumHeightArray=frameSumHeightArrayList[i],sumWidthArray=frameSumWidthArrayList[i],time=frameTimeStampArray[i],pitchX=pitchX,pitchY=pitchY)


def AOD_calibration_curve(pitch=0.5,numberOfPixels=16):
    voltageArray = np.arange(0,numberOfPixels)*pitch
    calibrationArray = np.array([])
    
    for voltage in voltageArray:
        if(voltage <= 6.0):
            calibrationFactor = 1.0 - 0.3*(voltage-6)**2/6**2
        else:
            calibrationFactor = 1.0 - (0.3 * (voltage-6.0)/4.0)
            
        
        calibrationFactor = 1.0/calibrationFactor
        calibrationArray = np.append(calibrationArray,calibrationFactor)
    
    return calibrationArray


def AOD_calibration_dict(pitch=0.5,numberOfPixels=16):
    calibrationDict1 = {}
    calibrationDict2 = {}
    
    
    return calibrationDict1, calibrationDict2


def calc_centroid_weight_of_intensity_profile(frameSumArray=np.array([])):
    indexArray = np.arange(len(frameSumArray))
    if(sum(frameSumArray) > 0):
        frameCentroid = np.trapz(np.multiply(indexArray,frameSumArray),indexArray)/np.trapz(frameSumArray,indexArray)
    else:
        frameCentroid = 0
    
    return frameCentroid 

def calc_centroid_correlation_of_intensity_profile(frameSumArray=np.array([]),spotSize=3):
    gaussWindowArray = ss.windows.gaussian(len(frameSumArray),spotSize)
    crossCorrelationArray = ss.correlate(frameSumArray,gaussWindowArray,mode='same')
    frameCentroid = np.where(crossCorrelationArray == max(crossCorrelationArray))[0]
    
    return frameCentroid

def intensity_profile_function(amplitude=200):
    def function(pixelNumber, mu, sigma):
        exponent = -0.5 * np.square((pixelNumber - mu)/sigma)
        value = amplitude
        value = value * np.exp(exponent)
        return value    
    return function

def intensity_profile_function_fixed_sigma(amplitude=200,sigma=5):
    def function(pixelNumber, mu):
        exponent = -0.5 * np.square((pixelNumber - mu)/sigma)
        value = amplitude
        value = value * np.exp(exponent)
        return value    
    return function

def calc_sigma(frameSumArray=np.array([])):
    indexArray = np.arange(len(frameSumArray))
    frameSumArray = frameSumArray.astype('float')
    probabilityArray = frameSumArray/np.trapz(frameSumArray,indexArray)
    
    variance = sum(probabilityArray*np.multiply(indexArray,indexArray)) - sum(probabilityArray*indexArray)**2
    std = np.sqrt(variance)
    return std

def calc_centroid_fit_to_intensity_profile_fixed_sigma(frameSumArray=np.array([])):
    indexArray = np.arange(len(frameSumArray))
    amplitude = max(frameSumArray)
    initCentroid = calc_centroid_weight_of_intensity_profile(frameSumArray=frameSumArray)
    spotSize = calc_sigma(frameSumArray=frameSumArray)
    try:
        
        popt,pcov = curve_fit(intensity_profile_function_fixed_sigma(amplitude=amplitude,sigma=spotSize),xdata=indexArray,ydata=frameSumArray,p0=[initCentroid])
    except:
        
        popt = np.array([0.0,0.0])
        pcov = np.array([[0.0,0.0],[0.0,0.0]])
        
    frameCentroid = popt[0]
    """
    fitArray = np.array([])
    for i in indexArray:
        value = intensity_profile_function_fixed_sigma(amplitude=amplitude,sigma=spotSize)(pixelNumber=i,mu=popt[0])
        fitArray = np.append(fitArray,value)
        
    fig, ax = plt.subplots()
    
    ax.plot(frameSumArray,color="red",linestyle="-",label="Data")
    ax.plot(fitArray,color='blue',label='Fitted Data')
    ax.legend()
    ax.set_title('Electrophoretic vs Electroosmotic velocity')
    ax.set_ylabel('Electrophoretic velocity (mm/s)')
    ax.set_xlabel('Electroosmotic velocity (mm/s)')
    plt.show()    
    """
    return frameCentroid
    

def calc_centroid_fit_to_intensity_profile(frameSumArray=np.array([]),spotSize=5):
    indexArray = np.arange(len(frameSumArray))
    amplitude = max(frameSumArray)
    initCentroid = calc_centroid_weight_of_intensity_profile(frameSumArray=frameSumArray)
    try:
        
        popt,pcov = curve_fit(intensity_profile_function(amplitude=amplitude),xdata=indexArray,ydata=frameSumArray,p0=[initCentroid,spotSize])
    except:
        
        popt = np.array([0.0,0.0])
        pcov = np.array([[0.0,0.0],[0.0,0.0]])
        
    frameCentroid = popt[0]
    sigma = popt[0]
    """
    fitArray = np.array([])
    for i in indexArray:
        value = intensity_profile_function(amplitude=amplitude)(pixelNumber=i,mu=popt[0],sigma=popt[1])
        fitArray = np.append(fitArray,value)
        
    fig, ax = plt.subplots()
    
    ax.plot(frameSumArray,color="red",linestyle="-",label="Data")
    ax.plot(fitArray,color='blue',label='Fitted Data')
    ax.legend()
    ax.set_title('Electrophoretic vs Electroosmotic velocity')
    ax.set_ylabel('Electrophoretic velocity (mm/s)')
    ax.set_xlabel('Electroosmotic velocity (mm/s)')
    plt.show()    
    """
    return frameCentroid, amplitude, sigma

def calc_centroid_max_of_intensity_profile(frameSumArray=np.array([])):
    frameCentroid = 0
    if(sum(frameSumArray) > 0):
        frameCentroid = np.where(frameSumArray == max(frameSumArray))[0][0]
    
    return frameCentroid

def calc_centroid(frameSumArray=np.array([]),spotSize=3):
    global centroidCalculation
    
    frameCentroid = 0
    amplitude = 0
    sigma = 0
    
    if(centroidCalculation == "gaussian fit"):
        frameCentroid, amplitude, sigma = calc_centroid_fit_to_intensity_profile(frameSumArray=frameSumArray,spotSize=spotSize)
    elif(centroidCalculation == "weight"):
        frameCentroid = calc_centroid_weight_of_intensity_profile(frameSumArray=frameSumArray)
    elif(centroidCalculation == "cross correlatioin"):
        frameCentroid = calc_centroid_correlation_of_intensity_profile(frameSumArray=frameSumArray, spotSize=spotSize)
    elif(centroidCalculation == "gaussian fit fixed sigma"):
        frameCentroid = calc_centroid_fit_to_intensity_profile_fixed_sigma(frameSumArray=frameSumArray)
    elif(centroidCalculation == "maximum"):
        frameCentroid = calc_centroid_max_of_intensity_profile(frameSumArray=frameSumArray)
        
        
    
    return frameCentroid, amplitude, sigma
    
   

def generate_frame_list_from_fragment(AODTimeArray=np.array([]),AOD1DataArray=np.array([]),AOD2DataArray=np.array([]),pixelNumberArray=np.array([]),
                                     SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),rollImage=False,rollAxis=0,rollPixels=1):
    global pixelsPerFrame
    global centroidCalculation
    global pitchX
    global pitchY
    global darkCount
    
    frameArrayList = []
    frameSumWidthArrayList = []
    frameSumHeightArrayList = []
    frameSumHeightCentroidArray = np.array([])
    frameSumHeightAmplitudeArray = np.array([])
    frameSumHeightSigmaArray = np.array([])
    frameSumWidthCentroidArray = np.array([])
    frameSumWidthAmplitudeArray = np.array([])
    frameSumWidthSigmaArray = np.array([])
    
    
    width = int(max(AOD1DataArray)+1)
    height = int(max(AOD2DataArray)+1)
    frameArray = np.zeros((width,height,3),dtype=np.uint8)
    counter = 1
    frameStartTime = AODTimeArray[0]
    frameTimeStampArray = np.array([])
    
    frameSumWidthArray = np.zeros(width,dtype=int)
    frameSumHeightArray = np.zeros(height,dtype=int)
    
    startTime = AODTimeArray[0]
    stopTime = AODTimeArray[-1]
    progresCounter = 0
    progresPercentage = 0
    progresString = ""
    
    AODXCalibrationArray = AOD_calibration_curve(pitch=pitchX,numberOfPixels=16)
    AODYCalibrationArray = AOD_calibration_curve(pitch=pitchY,numberOfPixels=4)
    
    print("Generating frames between {}s and {}s".format(startTime, stopTime))
    for i in range(len(AODTimeArray)):
        AOD1Index = AOD1DataArray[i]
        AOD2Index = AOD2DataArray[i]
        pixelNumber = pixelNumberArray[i]
        
        if(pixelNumber == 0):
            frameStartTime = AODTimeArray[i]        
        
        if(pixelNumber == pixelsPerFrame):
            frameArrayList.append(frameArray)
            #print(frameArray)
            
            #indexArray = frameSumHeightArray < 0.6*np.average(frameSumHeightArray)
            #frameSumHeightArray[indexArray] = 0.0
            """
            frameSumHeightArray = frameSumHeightArray - 0.6*np.average(frameSumHeightArray)
            indexArray = frameSumHeightArray < 0
            frameSumHeightArray[indexArray] = 0.0                    
            """
            #indexArray = frameSumHeightArray > 0
            #frameSumHeightArray[indexArray] = 1                    
    
            #frameSumHeightArray = np.multiply(frameSumHeightArray, AODXCalibrationArray)
            #indexArray = np.where(frameSumHeightArray < 1.2*np.average(frameSumHeightArray))[0]
            #frameSumHeightArray[indexArray] = 0.0
            
            frameSumHeightCentroid,amplitude,sigma = calc_centroid(frameSumArray=frameSumHeightArray,spotSize=3)
            frameSumHeightCentroidArray = np.append(frameSumHeightCentroidArray,frameSumHeightCentroid)
            frameSumHeightAmplitudeArray = np.append(frameSumHeightAmplitudeArray, amplitude)
            frameSumHeightSigmaArray = np.append(frameSumHeightSigmaArray,sigma)
    
            frameSumWidthCentroid,amplitude,sigma = calc_centroid(frameSumArray=frameSumWidthArray,spotSize=3)
            frameSumWidthCentroidArray = np.append(frameSumWidthCentroidArray,frameSumWidthCentroid)    
            frameSumWidthAmplitudeArray = np.append(frameSumWidthAmplitudeArray,amplitude)
            frameSumWidthSigmaArray = np.append(frameSumWidthSigmaArray,sigma)
            
            frameSumHeightArrayList.append(frameSumHeightArray)
            frameSumWidthArrayList.append(frameSumWidthArray)
    
              
            frameSumWidthArray = np.zeros(width,dtype=int)
            frameSumHeightArray = np.zeros(height,dtype=int)
            frameArray = np.zeros((width,height,3),dtype=np.uint8)
    
            frameStopTime = AODTimeArray[i]
            frameTimeStamp = (frameStopTime+frameStartTime)/2
            frameTimeStampArray = np.append(frameTimeStampArray,frameTimeStamp)
            
        progresPercentage = (AODTimeArray[i] - startTime)/(stopTime - startTime)
        if(progresPercentage > progresCounter):
            print("{} {:.0f}%".format(progresString,(progresPercentage*100)))
            progresString = progresString + "#"
            progresCounter = progresCounter + 0.1
            
            
        SPCMDataArrayIndex = len(np.where(SPCMTimeArray < AODTimeArray[i])[0])
        if(SPCMDataArrayIndex == len(SPCMTimeArray)):
            SPCMDataArrayIndex = SPCMDataArrayIndex - 1
        #pixelValue = int(SPCMDataArray[SPCMDataArrayIndex]*255)
        if(SPCMDataArray[SPCMDataArrayIndex] > darkCount):
            pixelValue = int(SPCMDataArray[SPCMDataArrayIndex])
        else:
            pixelValue = 0
            
        frameSumWidthArray[AOD1Index] = frameSumWidthArray[AOD1Index] + pixelValue
        frameSumHeightArray[AOD2Index] = frameSumHeightArray[AOD2Index] + pixelValue
        pixelArray = np.ones(3,dtype=np.uint8) * pixelValue
        frameArray[AOD1Index][AOD2Index] = frameArray[AOD1Index][AOD2Index] + pixelArray
        
    return frameArrayList, frameSumWidthArrayList, frameSumHeightArrayList, frameSumWidthCentroidArray ,frameSumHeightCentroidArray, frameTimeStampArray,frameSumHeightAmplitudeArray,frameSumHeightSigmaArray,frameSumWidthAmplitudeArray,frameSumWidthSigmaArray      

def concatenate_videos(videoPathList=[],experimentName=""):
    videoFileList = []
    for videoPath in videoPathList:
        videoFileList.append(VideoFileClip(videoPath))
        
    concatenatedVideo = concatenate_videoclips(videoFileList)
    extension = videoPathList[0].split('.')[1]
    concatenatedVideoPath = os.path.join(os.path.dirname(videoPathList[0]),"{}_concatenated.{}".format(experimentName,extension))
    concatenatedVideo.write_videofile(concatenatedVideoPath)    
    


