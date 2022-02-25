import numpy as np
import scipy.signal as ss
import os

filterSPCM = True
windowSize = 50
offsetOn = True
offsetExtFieldTime = 0.0
offsetSPCMTime = 0.0
   

def write_offset_times_to_txt(offsetFilePath=""):
    global offsetSPCMTime
    global offsetExtFieldTime
    
    offsetFile = open(offsetFilePath,'w')
    
    offsetFile.write("offsetSPCMTime:{}\n".format(offsetSPCMTime))
    offsetFile.write("offsetExtFieldTime:{}\n".format(offsetExtFieldTime))
    offsetFile.close()
    
def read_offset_times_from_txt(offsetFilePath=""):
    global offsetSPCMTime
    global offsetExtFieldTime
    
    offsetFile = open(offsetFilePath,'r') 
    
    offsetSPCMTime = float(offsetFile.readline().split(":")[1])
    offsetExtFieldTime = float(offsetFile.readline().split(":")[1])
    offsetFile.close()
 
def return_arrays_from_tdms_hierarchy(pixelNumberArray=np.array([]), AODLoopTicksArray=np.array([]), SPCMDataArray=np.array([]), SPCMLoopTicksArray=np.array([]), 
                                      eFieldDataArray=np.array([]), eFieldLoopTicksArray=np.array([]), FPGAClockPeriod=25e-9,tdmsFolderPath="",experimentName=""):
    global filterSPCM
    global windowSize
    global offsetOn
    global offsetExtFieldTime
    global offsetSPCMTime
    
    AODTimeArray = np.cumsum(np.abs(AODLoopTicksArray.astype('float'))) * FPGAClockPeriod
    AODSyncTimeArray, AODSyncDataArray = generate_sync_array(rawTicksArray=AODLoopTicksArray.astype('float'),FPGAClockPeriod=FPGAClockPeriod)
    
    eFieldTimeArray = np.cumsum(eFieldLoopTicksArray.astype('float')) * FPGAClockPeriod
    
    if(filterSPCM == True):
        SPCMDataArray = noise_filter_counts_array(countsArray=SPCMDataArray,windowSize=windowSize,filterType="gauss")
    SPCMTimeArray = np.cumsum(np.abs(SPCMLoopTicksArray.astype('float'))) * FPGAClockPeriod 
    SPCMSyncTimeArray, SPCMSyncDataArray = generate_sync_array(rawTicksArray=SPCMLoopTicksArray.astype('float'),FPGAClockPeriod=FPGAClockPeriod)
    
    if(offsetOn == True):
        offsetFilePath = os.path.join(tdmsFolderPath,"{}_time_offset.txt".format(experimentName))
        
        if(os.path.isfile(offsetFilePath) == True):
            read_offset_times_from_txt(offsetFilePath=offsetFilePath)
        else:
            write_offset_times_to_txt(offsetFilePath=offsetFilePath)
            
            
        eFieldTimeArray = eFieldTimeArray + offsetExtFieldTime
        SPCMSyncTimeArray = SPCMSyncTimeArray + offsetSPCMTime
        SPCMTimeArray = SPCMTimeArray + offsetSPCMTime
    
    return pixelNumberArray, AODTimeArray, AODSyncTimeArray, AODSyncDataArray, SPCMDataArray, SPCMTimeArray, SPCMSyncTimeArray, SPCMSyncDataArray,eFieldDataArray, eFieldTimeArray
    
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

def generate_sync_array(rawTicksArray=np.array([]),FPGAClockPeriod=25e-9):
    syncTimeArray = np.array([])
    syncDataArray = np.array([])
    
    rawTimeArray = np.cumsum(np.abs(rawTicksArray)) * FPGAClockPeriod
    
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
    AODTimeArray = np.copy(AODTimeArray[startIndex:stopIndex])
    pixelNumberArray = np.copy(pixelNumberArray[startIndex:stopIndex])
    AOD1DataArray = np.copy(AOD1DataArray[startIndex:stopIndex])
    AOD2DataArray = np.copy(AOD2DataArray[startIndex:stopIndex])
    
    startIndex = len(np.where(discontTimeArray < startTime)[0]) 
    stopIndex = len(np.where(discontTimeArray < stopTime)[0])
    discontTimeArray = np.copy(discontTimeArray[startIndex:stopIndex])
    discontDataArray = np.copy(discontDataArray[startIndex:stopIndex])  
    
    startIndex = len(np.where(SPCMSyncTimeArray < startTime)[0]) 
    stopIndex = len(np.where(SPCMSyncTimeArray < stopTime)[0])
    SPCMSyncTimeArray = np.copy(SPCMSyncTimeArray[startIndex:stopIndex])
    SPCMSyncDataArray = np.copy(SPCMSyncDataArray[startIndex:stopIndex])     
    
    startIndex = len(np.where(AODSyncTimeArray < startTime)[0]) 
    stopIndex = len(np.where(AODSyncTimeArray < stopTime)[0])
    AODSyncTimeArray = np.copy(AODSyncTimeArray[startIndex:stopIndex])
    AODSyncDataArray = np.copy(AODSyncDataArray[startIndex:stopIndex])    
    
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

    


def pixel_number_array_to_AOD_grid_index_arrays(pixelNumberArray=np.array([]),amountOfLines=10,pixelsPerLine=10,lineAxis=0,scanningPattern="E-shape"):
    AOD1DataArray = np.copy(pixelNumberArray)
    AOD2DataArray = np.copy(pixelNumberArray)
    pixelMappingDict = {}
    
    if(scanningPattern == "E-shape"):
        pixelMappingDict = generate_E_grid_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)
    elif(scanningPattern == "S-shape"):
        pixelMappingDict = generate_S_grid_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)
    elif(scanningPattern == "S-shape-x2"):
        pixelMappingDict = generate_S_grid_x2_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)
    elif(scanningPattern == "S-shape-x4"):
        pixelMappingDict = generate_S_grid_x4_pixel_mapping_dict(amountOfLines=amountOfLines, pixelsPerLine=pixelsPerLine, lineAxis=lineAxis)        
        
        
    
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
    
    frameTimeStampArray = np.array([])
    frameTimeStampArray = ravel_list_of_arrays(arrayList=frameTimeStampArrayList)
    
    #averageFrameTime = np.average(np.diff(frameTimeStampArray))
    
    frameSumHeightCentroidArray = np.array([])
    frameSumWidthCentroidArray = np.array([])
    frameSumWidthArrayList = []
    frameSumHeightArrayList = []
    
    #tempList = []
    
    #gapsBetweenSegments = False
    """
    
    for i in range(len(frameTimeStampArrayList)-1):
        if((frameTimeStampArrayList[i+1][0]-frameTimeStampArrayList[i][-1]) >= 1.3*averageFrameTime):
            gapsBetweenSegments = True
            
            
    if(gapsBetweenSegments == True):
        for i in range(len(frameTimeStampArrayList)-1):
            newTime = frameTimeStampArrayList[i+1][0] + frameTimeStampArrayList[i][-1]
            newTime = newTime/2
            frameTimeStampArray = np.append(frameTimeStampArray,frameTimeStampArrayList[i])
            frameTimeStampArray = np.append(frameTimeStampArray, newTime)
            
            
            newWidthCentroid = frameSumWidthCentroidArrayList[i+1][0] + frameSumWidthCentroidArrayList[i][-1]
            newWidthCentroid = newWidthCentroid/2
            frameSumWidthCentroidArray = np.append(frameSumWidthCentroidArray,frameSumWidthCentroidArrayList[i])
            frameSumWidthCentroidArray = np.append(frameSumWidthCentroidArray,newWidthCentroid)
            
            newHeightCentroid = frameSumHeightCentroidArrayList[i+1][0] + frameSumHeightCentroidArrayList[i][-1]
            newHeightCentroid = newHeightCentroid/2
            frameSumHeightCentroidArray = np.append(frameSumHeightCentroidArray,frameSumHeightCentroidArrayList[i])
            frameSumHeightCentroidArray = np.append(frameSumHeightCentroidArray,newHeightCentroid)            
            
            
            newSumWidthArray = frameSumWidthArrayListList[i+1][0] + frameSumWidthArrayListList[i][-1]
            newSumWidthArray = newSumWidthArray/2
            tempList = frameSumWidthArrayListList[i]
            tempList.append(newSumWidthArray)
            frameSumWidthArrayList = frameSumWidthArrayList + tempList
            
            newSumHeightArray = frameSumHeightArrayListList[i+1][0] + frameSumHeightArrayListList[i][-1]
            newSumHeightArray = newSumHeightArray/2
            tempList = frameSumHeightArrayListList[i]
            tempList.append(newSumHeightArray)
            frameSumHeightArrayList = frameSumHeightArrayList + tempList 
            
            
        frameTimeStampArray = np.append(frameTimeStampArray,frameTimeStampArrayList[len(frameTimeStampArrayList)-1])
        frameSumWidthCentroidArray = np.append(frameSumWidthCentroidArray,frameSumWidthCentroidArrayList[len(frameSumWidthCentroidArrayList)-1])
        frameSumHeightCentroidArray = np.append(frameSumHeightCentroidArray,frameSumHeightCentroidArrayList[len(frameSumHeightCentroidArrayList)-1])
        frameSumWidthArrayList = frameSumWidthArrayList + frameSumWidthArrayListList[-1]
        frameSumHeightArrayList = frameSumHeightArrayList + frameSumHeightArrayListList[-1]
        
        
    else:
    
        frameTimeStampArray = np.ravel(np.array(frameTimeStampArrayList))
        frameSumWidthCentroidArray = np.ravel(np.array(frameSumWidthCentroidArrayList))
        frameSumHeightCentroidArray = np.ravel(np.array(frameSumHeightCentroidArrayList))
    
        frameSumWidthArrayList = np.array(frameSumWidthArrayListList).reshape(-1, np.array(frameSumWidthArrayListList).shape[-1]).tolist()
        frameSumHeightArrayList = np.array(frameSumHeightArrayListList).reshape(-1, np.array(frameSumHeightArrayListList).shape[-1]).tolist()
    
"""
    
    
    frameSumWidthCentroidArray = ravel_list_of_arrays(arrayList=frameSumWidthCentroidArrayList)
    frameSumHeightCentroidArray = ravel_list_of_arrays(arrayList=frameSumHeightCentroidArrayList)
    
    frameSumHeightArrayList = ravel_list_of_list_of_array(arrayListList=frameSumHeightArrayListList)
    frameSumWidthArrayList = ravel_list_of_list_of_array(arrayListList=frameSumWidthArrayListList) 
    
    
    return frameTimeStampArray,frameSumWidthArrayList,frameSumHeightArrayList, frameSumWidthCentroidArray, frameSumHeightCentroidArray




