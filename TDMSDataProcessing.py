import numpy as np
import scipy.signal as ss
import os

filterSPCM = True
windowSize = 50
offsetOn = True
offsetExtFieldTime = 0.0
offsetSPCMTime = 0.0
   
# Writes a file with the time offsets between the different raw data signals

# Input:  - offsetFilePath: Path to the time offset file, values of the offset times are defined by globals 

def write_offset_times_to_txt(offsetFilePath=""):
    global offsetSPCMTime
    global offsetExtFieldTime
    
    offsetFile = open(offsetFilePath,'w')
    
    offsetFile.write("offsetSPCMTime:{}\n".format(offsetSPCMTime))
    offsetFile.write("offsetExtFieldTime:{}\n".format(offsetExtFieldTime))
    offsetFile.close()
    
# Reads the time offsets that need to be applied to the raw data signals

# Input:  - offsetFilePath: Path to the time offset file, values of the offset times are defined by globals 

# Output: No return values, the values are used by multiple modules and are transfered using globals
    
def read_offset_times_from_txt(offsetFilePath=""):
    global offsetSPCMTime
    global offsetExtFieldTime
    
    offsetFile = open(offsetFilePath,'r') 
    
    offsetSPCMTime = float(offsetFile.readline().split(":")[1])
    offsetExtFieldTime = float(offsetFile.readline().split(":")[1])
    offsetFile.close()
    
# Returns arrays of filled with combination of raw and processed data from the tdms hierarchy dictionary

# Input:  - pixelNumberArray: Array containing the index number of the current pixel being scanned by the AODs, these numbers represent a X and Y value encoded in the pixelmapping LUT
#         - AODLoopTicksArray: Array containing the amount of clock ticks it took the FPGA to scan respective pixel
#         - SPCMDataArray: Array containing the photons counted by the SPCM given a certain binsize
#         - SPCMLoopTicksArray: Array containing the amount of clock ticks it took the FPGA to bin the photon count
#         - eFieldDataArray: Array containing the applied voltage to the voltage amplifier which applies this voltage across the microfluidic channel
#         - eFieldLoopTicksArray: Array containing the amount of clock ticks it took the FPGA to apply respective voltage
#         - FPGAClockPeriod: The time of a single clock cycle, for our FPGA this is assumed to be 25 ns
#         - tdmsFolderPath: Path of the folder containing the tdms files
#         - experimentName: Name of the experiment also the EPxx number 

# Output: - pixelNumberArray: Array containing the index number of the current pixel being scanned by the AODs, these numbers represent a X and Y value encoded in the pixelmapping LUT
#         - AODTimeArray: Array containing the time stamps of each pixel, this is calculated using CumSum(AODLoopTicksArray*FPGAClockPeriod)
#         - AODSyncTimeArray: Array containing the timestamps of the AOD synchronisation signal created from the sign of the  AODLoopTicksArray values 
#         - AODSyncDataArray: Array containing a 1 or 0 for respective positive and negative AODLoopTicksArray values
#         - SPCMDataArray: Array containing the photons counted by the SPCM given a certain binsize
#         - SPCMTimeArray: Array containing the time stamps of photoncount bin, this is calculated using CumSum(SPCMLoopTicksArray*FPGAClockPeriod)
#         - SPCMSyncTimeArray: Array containing the timestamps of the SPCM synchronisation signal created from the sign of SPCMLoopTicksArray values
#         - SPCMSyncDataArray: Array containing a 1 or 0 for respective positive and negative SPCMLoopTicksArray values
#         - eFieldDataArray: Array containing the applied voltage to the voltage amplifier which applies this voltage across the microfluidic channel
#         - eFieldTimeArray: Array containing the time stamps of each applied voltage value, this is calculated using CumSum(eFieldLoopTicksArray*FPGAClockPeriod)
 
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
 
# Returns a running average filtered array of photoncounts array

# Input:  - countsArray: Array containing the photon counts that need to be filtered
#         - filterType: string containing the name of the filtertype to be used "mean" is a 1/N kernal, "gauss" is a gaussian kernel

# Output: - pixelNumberArray: Array containing the filtered version of countsArray

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

# Returns the synchornisation time and data array of a given raw ticks array 

# Input:  - rawTicksArray: Array containing raw ticks data directly from the FPGA 
#         - FPGAClockPeriod: The time of a single clock cycle, for our FPGA this is assumed to be 25 ns

# Output: - syncTimeArray: Array containing the timestamps of the synchronisation signal created from the sign of the rawTicksArray values 
#         - syncDataArray: Array containing a 1 or 0 for respective positive and negative rawTicksArray values 

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


# Returns the segmented data (between start and stop time in timeSegment list) of the origanal data arrays

# Input:  - timeSegment: List containing two values, the start and stop time of the segment
#         - AODTimeArray: Array containing the time stamps of each pixel
#         - AOD1DataArray: Array containing the pixel value of the first AOD
#         - AOD2DataArray: Array containing the pixel value of the second AOD
#         - SPCMTimeArray: Array containing the time stamps of photoncount bin
#         - SPCMDataArray: Array containing the photons counted by the SPCM given a certain binsize
#         - eFieldTimeArray: Array containing the time stamps of each applied voltage value
#         - eFieldDataArray: Array containing the applied voltage to the voltage amplifier which applies this voltage across the microfluidic channel
#         - pixelNumberArray: Array containing the index number of the current pixel being scanned by the AODs, these numbers represent a X and Y value encoded in the pixelmapping LUT
#         - discontTimeArray: Array containing the time stamps where a discontinuity is found (not used anymore)
#         - discontDataArray: Array containing 1's where a discontinuity is found (not used anymore)
#         - AODSyncTimeArray: Array containing the timestamps of the AOD synchronisation signal created from the sign of the  AODLoopTicksArray values 
#         - AODSyncDataArray: Array containing a 1 or 0 for respective positive and negative AODLoopTicksArray values
#         - SPCMSyncDataArray: Array containing a 1 or 0 for respective positive and negative SPCMLoopTicksArray values
#         - SPCMSyncTimeArray: Array containing the timestamps of the SPCM synchronisation signal created from the sign of SPCMLoopTicksArray values

# Output: - AODTimeArray:  All arrays contain the same data but limited in size to the start and stop times from timeSegment
#         - AOD1DataArray:
#         - pixelNumberArray:
#         - SPCMTimeArray:
#         - SPCMDataArray:
#         - eFieldTimeArray:
#         - eFieldDataArray:
#         - discontTimeArray:
#         - discontDataArray:
#         - AODSyncTimeArray:
#         - AODSyncDataArray:
#         - SPCMSyncTimeArray:
#         - SPCMSyncDataArray:

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


# Returns a pixel mapping dictionary to link the pixel number to a AOD1 and AOD2 pixelnumber respectively
# The shape of this scanning pattern is E

# Input:  - amountOfLines: The amount of lines scanned by FPGA program
#         - pixelsPerLine: The amount of pixel per line scanned by the FPGA program
#         - lineAxis: Integer (1 or 0) encoding the line axis 

# Output: - pixelMappingDict:  Dictionary containing the x and y pixel values for every pixel number=> {pixelNumber:[AOD1,AOD2]}

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

# Returns a pixel mapping dictionary to link the pixel number to a AOD1 and AOD2 pixelnumber respectively
# The shape of this scanning pattern is S with double exposure per pixel

# Input:  - amountOfLines: The amount of lines scanned by FPGA program
#         - pixelsPerLine: The amount of pixel per line scanned by the FPGA program
#         - lineAxis: Integer (1 or 0) encoding the line axis 

# Output: - pixelMappingDict:  Dictionary containing the x and y pixel values for every pixel number=> {pixelNumber:[AOD1,AOD2]}

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

# Returns a pixel mapping dictionary to link the pixel number to a AOD1 and AOD2 pixelnumber respectively
# The shape of this scanning pattern is S with quadruple exposure per pixel

# Input:  - amountOfLines: The amount of lines scanned by FPGA program
#         - pixelsPerLine: The amount of pixel per line scanned by the FPGA program
#         - lineAxis: Integer (1 or 0) encoding the line axis 

# Output: - pixelMappingDict:  Dictionary containing the x and y pixel values for every pixel number=> {pixelNumber:[AOD1,AOD2]}

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

# Returns a pixel mapping dictionary to link the pixel number to a AOD1 and AOD2 pixelnumber respectively
# The shape of this scanning pattern is S with single exposure per pixel

# Input:  - amountOfLines: The amount of lines scanned by FPGA program
#         - pixelsPerLine: The amount of pixel per line scanned by the FPGA program
#         - lineAxis: Integer (1 or 0) encoding the line axis 

# Output: - pixelMappingDict:  Dictionary containing the x and y pixel values for every pixel number=> {pixelNumber:[AOD1,AOD2]}

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

# Selects the correct pixel mapping function and returns respective AOD1 and AOD2 value arrays from the pixelNumberArray

# Input:  - pixelNumberArray:  Array containing the index number of the current pixel being scanned by the AODs, these numbers represent a X and Y value encoded in the pixelmapping LUT
#         - amountOfLines: The amount of lines scanned by FPGA program
#         - pixelsPerLine: The amount of pixel per line scanned by the FPGA program
#         - lineAxis: Integer (1 or 0) encoding the line axis 
#         - scanningPattern: String containing the name of the scanning pattern of the FPGA program

# Output: - AOD1DataArray: Array containing the pixel value of the first AOD
#         - AOD2DataArray: Array containing the pixel value of the second AOD

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

# Return an array consisting of all elements of a list of arrays, concatinates all arrays

# Input:  - arrayList: List containing arrays to be concatinated

# Output: - array: Concatinated array

def ravel_list_of_arrays(arrayList=[]):
    array = np.array([])
    l = []
    for a in arrayList:
        l = l + a.tolist()
        
    array = np.array(l)
    
    return array

# Returns an array consisting of all elements of a list of a list of arrays, concatinates all arrays

# Input:  - arrayList: List containing a list of arrays to be concatinated

# Output: - array: Concatinated array

def ravel_list_of_list_of_array(arrayListList=[]):
    arrayList = []
    
    for l in arrayListList:
        for a in l:
            arrayList.append(a)
    
    return arrayList

# Returns flattened arrays of all array lists or array list lists using the two function above. 
# A single trace is called a segment and a segment is split up in fragments for every 300 frames or so

# Input:  - frameTimeStampArrayList: A list containing arrays of timestamps from the fragments within the segment 
#         - frameSumWidthArrayListList: A list containing a list of arrays, the arrays are the integrated profiles of every frame in the width direction and are grouped in a list fro every fragment in a segment
#         - frameSumHeightArrayListList: A list containing a list of arrays, the arrays are the integrated profiles of every frame in the height direction and are grouped in a list fro every fragment in a segment
#         - frameSumWidthCentroidArrayList: A list containing arrays of the particle centroid width pixel for every frame, grouped together per fragment 
#         - frameSumHeightCentroidArrayList: A list containing arrays of the particle centroid height pixel for every frame, grouped together per fragment 


# Output: - frameTimeStampArray: flattened versions of the inputs
#         - frameSumWidthArrayList: 
#         - frameSumHeightArrayList: 
#         - frameSumWidthCentroidArray: 
#         - frameSumHeightCentroidArray: 

def flatten_fragments_to_segment(frameTimeStampArrayList=[],frameSumWidthArrayListList=[],frameSumHeightArrayListList=[],frameSumWidthCentroidArrayList=[],frameSumHeightCentroidArrayList=[]):
    
    frameTimeStampArray = np.array([])
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


"""
These functions are not used anymore, but were important during the development of the FPGA code, they look for possible discontinuities in the 
data which happend often during the first versions of the FPGA code
"""

def locate_AOD_discontinuities(pixelNumberArray=np.array([])):
    discontIndexArray = np.array([])
    
    pixelNumberJumpArray = abs(np.diff(pixelNumberArray.astype(int)))
    
    aboveMinIndexArray = np.where(pixelNumberJumpArray > 1)[0]
    noMinPixelJumpArray = pixelNumberJumpArray[aboveMinIndexArray]
    belowMaxIndexArray = np.where(noMinPixelJumpArray < max(noMinPixelJumpArray))[0]
    
    discontIndexArray = aboveMinIndexArray[belowMaxIndexArray]
    
    
    return discontIndexArray


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

def find_auto_offset(AODSyncTimeArray=np.array([]),AODSyncDataArray=np.array([]),SPCMSyncTimeArray=np.array([]),
                        SPCMSyncDataArray=np.array([]),eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]), cutoff = 100000):

    AODSyncDataArray = AODSyncDataArray[1:cutoff]
    SPCMSyncDataArray = SPCMSyncDataArray[1: cutoff]
    eFieldDataArray = eFieldDataArray[1: cutoff]

    AODSyncDiff = np.diff(AODSyncDataArray)
    AODIndex = np.where(AODSyncDiff == 1)[0][0]
    AODTime = (AODSyncTimeArray[AODIndex]+AODSyncTimeArray[AODIndex+1])/2

    SPCMSyncDiff = np.diff(SPCMSyncDataArray)
    SPCMIndex = np.where(SPCMSyncDiff == 1)[0][0]
    SPCMTime = (SPCMSyncTimeArray[SPCMIndex]+SPCMSyncTimeArray[SPCMIndex+1])/2

    eFieldSyncArray = np.where(eFieldDataArray >= 0, 1, 0)
    eFieldsyncDiff = np.diff(eFieldSyncArray)
    eFieldIndex = np.where(eFieldsyncDiff == 1)[0][0]
    eFieldTime = (eFieldTimeArray[eFieldIndex]+eFieldTimeArray[eFieldIndex+1])/2


    period = eFieldTimeArray[np.where(eFieldsyncDiff == 1)[0][1]]-eFieldTimeArray[eFieldIndex]

    print(SPCMTime-AODTime)
    offsetSPCMTime = mod((SPCMTime-AODTime), period)
    offsetExtFieldTime = mod((eFieldTime-AODTime), period)

    return offsetSPCMTime, offsetExtFieldTime, period

def mod(x, y):
    while x >= y:
        x -= y
    if x >= y/2:
        x -= y
    return x