import numpy as np
import scipy.signal as ss
import os
from datetime import datetime

filterSPCM = True
windowSize = 50
offsetOn = True
offsetExtFieldTime = 0.0
offsetSPCMTime = 0.0
   

def write_offset_times_to_txt(offsetFilePath=""):
    #stores SPCM and Extern field offset
    global offsetSPCMTime
    global offsetExtFieldTime
    
    offsetFile = open(offsetFilePath,'w')
    
    offsetFile.write("offsetSPCMTime:{}\n".format(offsetSPCMTime))
    offsetFile.write("offsetExtFieldTime:{}\n".format(offsetExtFieldTime))
    offsetFile.close()
    
def read_offset_times_from_txt(offsetFilePath=""):
    #reads offset from given file
    global offsetSPCMTime
    global offsetExtFieldTime
    
    offsetFile = open(offsetFilePath,'r') 
    
    offsetSPCMTime = float(offsetFile.readline().split(":")[1])
    offsetExtFieldTime = float(offsetFile.readline().split(":")[1])
    offsetFile.close()
 
def return_arrays_from_tdms_hierarchy(AODLoopTicksArray=np.array([]), SPCMDataArray=np.array([]), SPCMLoopTicksArray=np.array([]), 
                                      eFieldDataArray=np.array([]), eFieldLoopTicksArray=np.array([]), FPGAClockPeriod=25e-9,tdmsFolderPath="",experimentName=""):
    #input: raw data from tdms files
    #output: ticks are converted to time + sync signals generated + offset is applied if true
    global filterSPCM
    global windowSize
    global offsetOn
    global offsetExtFieldTime
    global offsetSPCMTime
    
    AODTimeArray = np.cumsum(np.abs(AODLoopTicksArray.astype('float'))) * FPGAClockPeriod
    AODSyncTimeArray, AODSyncDataArray = generate_sync_array(rawTicksArray=AODLoopTicksArray.astype('float'), rawTimeArray=AODTimeArray)
    
    eFieldTimeArray = np.cumsum(eFieldLoopTicksArray.astype('float')) * FPGAClockPeriod
    
    if(filterSPCM == True):
        SPCMDataArray = noise_filter_counts_array(countsArray=SPCMDataArray,windowSize=windowSize,filterType="gauss")
    SPCMTimeArray = np.cumsum(np.abs(SPCMLoopTicksArray.astype('float'))) * FPGAClockPeriod 
    SPCMSyncTimeArray, SPCMSyncDataArray = generate_sync_array(rawTicksArray=SPCMLoopTicksArray.astype('float'), rawTimeArray=SPCMTimeArray)
    
    if(offsetOn == True):
        offsetFilePath = os.path.join(tdmsFolderPath,"{}_time_offset.txt".format(experimentName))
        
        if(os.path.isfile(offsetFilePath) == True):
            read_offset_times_from_txt(offsetFilePath=offsetFilePath)
        else:
            write_offset_times_to_txt(offsetFilePath=offsetFilePath)
            
            
        eFieldTimeArray = eFieldTimeArray + offsetExtFieldTime
        SPCMSyncTimeArray = SPCMSyncTimeArray + offsetSPCMTime
        SPCMTimeArray = SPCMTimeArray + offsetSPCMTime
    
    return AODTimeArray, AODSyncTimeArray, AODSyncDataArray, SPCMDataArray, SPCMTimeArray, SPCMSyncTimeArray, SPCMSyncDataArray,eFieldDataArray, eFieldTimeArray
    
def noise_filter_counts_array(countsArray=np.array([]),filterType="mean"):
    global windowSize
    
    if(filterType == "mean"):
        kernelArray = np.ones(windowSize) * float(1.0/windowSize) 
        filtCountsArray = np.convolve(countsArray,kernelArray,mode="same")
    elif(filterType == "gauss"):
        kernelArray = ss.windows.gaussian(windowSize, int(windowSize/5))
        kernelArray = kernelArray/sum(kernelArray)
        filtCountsArray = np.convolve(countsArray,kernelArray,mode="same")
        
    return filtCountsArray

def locate_AOD_discontinuities(pixelNumberArray=np.array([])):
    discontIndexArray = np.array([])
    
    pixelNumberJumpArray = abs(np.diff(pixelNumberArray.astype(int)))
    
    aboveMinIndexArray = np.where(pixelNumberJumpArray > 1)[0]
    noMinPixelJumpArray = pixelNumberJumpArray[aboveMinIndexArray]
    belowMaxIndexArray = np.where(noMinPixelJumpArray < max(noMinPixelJumpArray))[0]
    
    discontIndexArray = aboveMinIndexArray[belowMaxIndexArray]
    
    
    return discontIndexArray

def generate_sync_array(rawTicksArray=np.array([]), rawTimeArray=np.array([])):
    
    syncTimeArray = np.array([])
    syncDataArray = np.array([])

    negativeIndexArray = np.where(rawTicksArray <= 0)[0]
    negativeIndexJumpArray = np.diff(negativeIndexArray)
    negativeSignChangeIndexArray = np.where(negativeIndexJumpArray > 1)[0]
    
    positiveIndexArray = np.where(rawTicksArray >= 0)[0]
    positiveIndexJumpArray = np.diff(positiveIndexArray)
    positiveSignChangeIndexArray = np.where(positiveIndexJumpArray > 1)[0] 

    if(rawTicksArray[0] > 0):
        syncDataArray = np.append(syncDataArray, 1.0)
    elif(rawTicksArray[0] < 0):
        syncDataArray = np.append(syncDataArray, 0.0)
    
    syncTimeArray = np.append(syncTimeArray,rawTimeArray[0])    
 
    allSignChangeIndexArray = np.array([])
    allSignChangeIndexArray = np.append(allSignChangeIndexArray,negativeIndexArray[negativeSignChangeIndexArray])
    allSignChangeIndexArray = np.append(allSignChangeIndexArray,positiveIndexArray[positiveSignChangeIndexArray])
    allSignChangeIndexArray = np.sort(allSignChangeIndexArray).astype(int)
    
    for rawTimeSignChangeIndex in allSignChangeIndexArray:
        syncTimeArray = np.append(syncTimeArray,rawTimeArray[rawTimeSignChangeIndex])
        syncTimeArray = np.append(syncTimeArray,rawTimeArray[rawTimeSignChangeIndex+1])
        
        if(rawTicksArray[rawTimeSignChangeIndex] < rawTicksArray[rawTimeSignChangeIndex+1]):
            syncDataArray = np.append(syncDataArray,[0.0,1.0])
            
        elif(rawTicksArray[rawTimeSignChangeIndex] > rawTicksArray[rawTimeSignChangeIndex+1]):
            syncDataArray = np.append(syncDataArray,[1.0,0.0])
            
    
    return syncTimeArray, syncDataArray

def data_to_segment(timeSegment=[],AODTimeArray=np.array([]),AOD1DataArray=np.array([]),AOD2DataArray=np.array([]),SPCMTimeArray=np.array([]),SPCMDataArray=np.array([]),eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),
                    pixelNumberArray=np.array([]),discontTimeArray=np.array([]),discontDataArray=np.array([]),AODSyncTimeArray=np.array([]),AODSyncDataArray=np.array([]),
                      SPCMSyncDataArray=np.array([]),SPCMSyncTimeArray=np.array([])):
    
    if(len(timeSegment) != 2):
        return 0
    
    startTime = timeSegment[0]
    stopTime = timeSegment[1]
    
    startIndex = len(np.where(AODTimeArray < startTime)[0]) 
    stopIndex = len(np.where(AODTimeArray < stopTime)[0])
    AODTimeArray = AODTimeArray[startIndex:stopIndex]
    pixelNumberArray = pixelNumberArray[startIndex:stopIndex]
    AOD1DataArray = AOD1DataArray[startIndex:stopIndex]
    AOD2DataArray = AOD2DataArray[startIndex:stopIndex]
    
    startIndex = len(np.where(discontTimeArray < startTime)[0]) 
    stopIndex = len(np.where(discontTimeArray < stopTime)[0])
    discontTimeArray = discontTimeArray[startIndex:stopIndex]
    discontDataArray = discontDataArray[startIndex:stopIndex]  
    
    startIndex = len(np.where(SPCMSyncTimeArray < startTime)[0]) 
    stopIndex = len(np.where(SPCMSyncTimeArray < stopTime)[0])
    SPCMSyncTimeArray = SPCMSyncTimeArray[startIndex:stopIndex]
    SPCMSyncDataArray = SPCMSyncDataArray[startIndex:stopIndex]
    
    startIndex = len(np.where(AODSyncTimeArray < startTime)[0]) 
    stopIndex = len(np.where(AODSyncTimeArray < stopTime)[0])
    AODSyncTimeArray = AODSyncTimeArray[startIndex:stopIndex]
    AODSyncDataArray = AODSyncDataArray[startIndex:stopIndex]   

    startIndex = len(np.where(SPCMTimeArray < startTime)[0]) 
    stopIndex = len(np.where(SPCMTimeArray < stopTime)[0])
    SPCMTimeArray = SPCMTimeArray[startIndex:stopIndex]
    SPCMDataArray = SPCMDataArray[startIndex:stopIndex]

    startIndex = len(np.where(eFieldTimeArray < startTime)[0]) 
    stopIndex = len(np.where(eFieldTimeArray < stopTime)[0])
    eFieldTimeArray = eFieldTimeArray[startIndex:stopIndex]
    eFieldDataArray = eFieldDataArray[startIndex:stopIndex]     
    
    return AODTimeArray, AOD1DataArray, AOD2DataArray, pixelNumberArray, SPCMTimeArray, SPCMDataArray, eFieldTimeArray, eFieldDataArray, discontTimeArray, discontDataArray, AODSyncTimeArray, AODSyncDataArray, SPCMSyncTimeArray, SPCMSyncDataArray

def discont_index_to_time_and_data_array(discontIndexArray=np.array([]), AODTimeArray=np.array([])):
    discontTimeArray = np.array([AODTimeArray[0]])
    discontDataArray = np.array([0.0])
    
    for i in range(len(discontIndexArray)):
        index = discontIndexArray[i]
        preIndex = int(index - 1)
        postIndex = int(index + 1)            
        
        discontTimeArray = np.append(discontTimeArray, AODTimeArray[preIndex])
        discontDataArray = np.append(discontDataArray, 0.0)
        
        discontTimeArray = np.append(discontTimeArray, AODTimeArray[index])
        discontDataArray = np.append(discontDataArray, 1.0)
        
        discontTimeArray = np.append(discontTimeArray, AODTimeArray[postIndex])
        discontDataArray = np.append(discontDataArray, 1.0) 
        
        discontTimeArray = np.append(discontTimeArray, AODTimeArray[postIndex+1])
        discontDataArray = np.append(discontDataArray, 0.0)     
    
    return discontTimeArray, discontDataArray

def generate_E_grid_pixel_mapping_dict(amountOfLines=10,pixelsPerLine=10,lineAxis=0):
    amountOfPixels = int(amountOfLines * (pixelsPerLine + 1))
    pixelMappingDict = {}
    y = 0
    for index in range(amountOfPixels):
        x = index % (pixelsPerLine + 1)
        if((index != 0) and (x == 0)):
            y = y + 1
        if(x == pixelsPerLine):
            x = 0
        
        if(lineAxis == 0):
            pixelMappingDict[index] = [x,y]
        else:
            pixelMappingDict[index] = [y,x]
        
    return pixelMappingDict

def generate_S_grid_x2_pixel_mapping_dict(amountOfLines=10,pixelsPerLine=10,lineAxis=0):
    amountOfPixels = int(amountOfLines*pixelsPerLine)
    pixelMappingDict = {}
    countUp = True
    xCounter = 0
    for index in range(amountOfPixels):
        y = int(index/( pixelsPerLine))
        
        if((index%pixelsPerLine) == 0 and (index > 0)):
            countUp = not countUp
            xCounter = 0        
        
        if(countUp == True):
            x = xCounter
        elif(countUp == False):
            x = pixelsPerLine - 1 - xCounter
            
        xCounter = xCounter + 1
        
            
        if(lineAxis == 0):
            pixelMappingDict[int(index*2)] = [x,y]
            pixelMappingDict[int(index*2 + 1)] = [x,y]
        else:
            pixelMappingDict[int(index*2)] = [y,x]
            pixelMappingDict[int(index*2 + 1)] = [y,x]
            
    if(lineAxis == 0):
        pixelMappingDict[index*2+2] = [0,y]
        pixelMappingDict[index*2+3] = [0,0]
    else:
        pixelMappingDict[index*2+2] = [y,0]
        pixelMappingDict[index*2+3] = [0,0]
        
    return pixelMappingDict

def generate_S_grid_x4_pixel_mapping_dict(amountOfLines=10,pixelsPerLine=10,lineAxis=0):
    amountOfPixels = int(amountOfLines*pixelsPerLine)
    pixelMappingDict = {}
    countUp = True
    xCounter = 0
    for index in range(amountOfPixels):
        y = int(index/(pixelsPerLine))
        
        if((index%pixelsPerLine) == 0 and (index > 0)):
            countUp = not countUp
            xCounter = 0        
        
        if(countUp == True):
            x = xCounter
        elif(countUp == False):
            x = pixelsPerLine - 1 - xCounter
            
        xCounter = xCounter + 1
        
            
        if(lineAxis == 0):
            pixelMappingDict[int(index*4)] = [x,y]
            pixelMappingDict[int(index*4 + 1)] = [x,y]
            pixelMappingDict[int(index*4 + 2)] = [x,y]
            pixelMappingDict[int(index*4 + 3)] = [x,y]
        else:
            pixelMappingDict[int(index*4)] = [y,x]
            pixelMappingDict[int(index*4 + 1)] = [y,x]
            pixelMappingDict[int(index*4 + 2)] = [y,x]
            pixelMappingDict[int(index*4 + 3)] = [y,x]
            
    if(lineAxis == 0):
        pixelMappingDict[index*4+4] = [0,y]
        pixelMappingDict[index*4+5] = [0,0]
    else:
        pixelMappingDict[index*4+4] = [y,0]
        pixelMappingDict[index*4+5] = [0,0]
        
    return pixelMappingDict

def generate_S_grid_pixel_mapping_dict(amountOfLines=10,pixelsPerLine=10,lineAxis=0):
    amountOfPixels = int(amountOfLines*pixelsPerLine)
    pixelMappingDict = {}
    countUp = True
    xCounter = 0
    for index in range(amountOfPixels):
        y = int(index/( pixelsPerLine))
        
        if((index%pixelsPerLine) == 0 and (index > 0)):
            countUp = not countUp
            xCounter = 0        
        
        if(countUp == True):
            x = xCounter
        elif(countUp == False):
            x = pixelsPerLine - 1 - xCounter
            
        xCounter = xCounter + 1
        
            
        if(lineAxis == 0):
            pixelMappingDict[index] = [x,y]
        else:
            pixelMappingDict[index] = [y,x]
            
    if(lineAxis == 0):
        pixelMappingDict[index+1] = [0,y]
        pixelMappingDict[index+2] = [0,0]
    else:
        pixelMappingDict[index+1] = [y,0]
        pixelMappingDict[index+2] = [0,0]
        
    return pixelMappingDict


def generate_pixel_mapping_dict(scanningPattern="S-shape", amountOfLines=10, pixelsPerLine=10, lineAxis=0):
    if(scanningPattern == "E-shape"):
        pixelMappingDict = generate_E_grid_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)
    elif(scanningPattern == "S-shape"):
        pixelMappingDict = generate_S_grid_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)
    elif(scanningPattern == "S-shape-x2"):
        pixelMappingDict = generate_S_grid_x2_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)
    elif(scanningPattern == "S-shape-x4"):
        pixelMappingDict = generate_S_grid_x4_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis) 
    return pixelMappingDict


def pixel_number_array_to_AOD_grid_index_arrays(pixelNumberArray=np.array([]),amountOfLines=10,pixelsPerLine=10,lineAxis=0,scanningPattern="E-shape"):
    AOD1DataArray = np.copy(pixelNumberArray)
    AOD2DataArray = np.copy(pixelNumberArray)
    pixelMappingDict = generate_pixel_mapping_dict(scanningPattern=scanningPattern, amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)
    

    amountOfPixels = len(pixelMappingDict.keys())
    for i in range(amountOfPixels):
        AOD1DataArray[np.where(AOD1DataArray == i)[0]] = pixelMappingDict[i][0]
        AOD2DataArray[np.where(AOD2DataArray == i)[0]] = pixelMappingDict[i][1]
        
    
        
    return AOD1DataArray, AOD2DataArray

def ravel_list_of_arrays(arrayList=[]):
    array = np.array([])
    l = []
    for a in arrayList:
        l = l + a.tolist()
        
    array = np.array(l)
    
    return array

def ravel_list_of_list_of_array(arrayListList=[]):
    arrayList = []
    
    for l in arrayListList:
        for a in l:
            arrayList.append(a)
    
    return arrayList

def flatten_fragments_to_segment(frameTimeStampArrayList=[],frameSumWidthArrayListList=[],frameSumHeightArrayListList=[],frameSumWidthCentroidArrayList=[],frameSumHeightCentroidArrayList=[]):
    
    frameTimeStampArray = ravel_list_of_arrays(arrayList=frameTimeStampArrayList)
       
    frameSumHeightCentroidArray = np.array([])
    frameSumWidthCentroidArray = np.array([])
    frameSumWidthArrayList = []
    frameSumHeightArrayList = []
    
    frameSumWidthCentroidArray = ravel_list_of_arrays(arrayList=frameSumWidthCentroidArrayList)
    frameSumHeightCentroidArray = ravel_list_of_arrays(arrayList=frameSumHeightCentroidArrayList)
    
    frameSumHeightArrayList = ravel_list_of_list_of_array(arrayListList=frameSumHeightArrayListList)
    frameSumWidthArrayList = ravel_list_of_list_of_array(arrayListList=frameSumWidthArrayListList) 
    
    
    return frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList, frameSumWidthCentroidArray, frameSumHeightCentroidArray




