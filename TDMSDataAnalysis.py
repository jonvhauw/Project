import numpy as np
import scipy.signal as ss


filterCutoff = 100
filterType = 'Butter'
filterOrder = 4


def locate_particle_in_image():
    
    
    return 0


def calc_filter_phase_offset(sos=np.array([]),fs=1000):
    w,h = ss.sosfreqz(sos,worN=int(fs/2))
    
    normalizedFreqArray = w/np.pi
    phaseArray = np.angle(h)
    
    return normalizedFreqArray, phaseArray


def compensate_filter_phase_offset(timeArray=np.array([]),sos=np.array([]),fs=3000,eFieldFreq=100):
    compensatedTimeArray = np.array([])
    
    normalizedFreqArray, phaseArray = calc_filter_phase_offset(sos=sos,fs=fs)
    
    fNyquist = fs/2
    normalizedeFieldFreq= eFieldFreq/fNyquist
    
    
    phaseOffset = phaseArray[np.where(normalizedFreqArray < normalizedeFieldFreq)[0][-1] + 1]
    phaseOffsetTime = 1/eFieldFreq * phaseOffset/(2*np.pi)
    
    compensatedTimeArray = timeArray + phaseOffsetTime
    
    return compensatedTimeArray


def low_pass_filter(timeArray=np.array([]),dataArray=np.array([]),eFieldFreq=100,compensateOutliers=True,thresholdFactor=0.5):
    global filterCutoff
    global filterType
    global filterOrder
    
    averageSamplePeriod = np.mean(np.diff(timeArray))
    fs = int(1/averageSamplePeriod)
    
    if(compensateOutliers == True):
        dataArray = compensate_outliers(dataArray=dataArray, thresholdFactor=thresholdFactor)
    
    sos = ss.butter(filterOrder,filterCutoff,'low', fs=fs,output='sos')
    filteredDataArray = ss.sosfilt(sos,dataArray)
    
    compensatedTimeArray = compensate_filter_phase_offset(timeArray=timeArray,sos=sos,fs=fs,eFieldFreq=eFieldFreq)
    
    
    return compensatedTimeArray, filteredDataArray

def compensate_outliers(dataArray=np.array([]),thresholdFactor=3.0,times=2):
    
    for i in range(times):
        averageStep = np.average(abs(np.diff(dataArray)))
        
        outlierIndexArray = np.where(abs(np.diff(dataArray)) > averageStep*thresholdFactor)[0]
        
        try:
            if(outlierIndexArray[0] == 0):
                outlierIndexArray = outlierIndexArray[1:]
                
            if(outlierIndexArray[-1] == (len(dataArray)-2)):
                outlierIndexArray = outlierIndexArray[:len(outlierIndexArray)-1]
                
            for outlierIndex in outlierIndexArray:
                dataArray[outlierIndex] = np.average([dataArray[outlierIndex-1],dataArray[outlierIndex+1]])
                #dataArray[outlierIndex] = dataArray[outlierIndex-1]               
                #
        except:
            print("")
    return dataArray
    


def split_trace_per_efield_period(eFieldTimeArray=np.array([]),eFieldDataArray=np.array([]),dataArray=np.array([]),timeArray=np.array([]),compensateAverage=False):
    dataArrayList = []
    timeArrayList = []
    periodStartIndexArray = np.array([])
    periodStartStopTimeArrayList = []
    
    
    stopIndexEField = np.where(eFieldTimeArray <= timeArray[-1])[0][-1]
    periodStartIndexArray = locate_period_start_indices(eFieldDataArray=eFieldDataArray[:stopIndexEField])
    
    
    
    for i in range(len(periodStartIndexArray)-1):
        startIndex = periodStartIndexArray[i]
        stopIndex = periodStartIndexArray[i+1]-1
        
        startTime = eFieldTimeArray[startIndex]
        stopTime = eFieldTimeArray[stopIndex]
        
        periodStartStopTimeArrayList.append([startTime,stopTime])
    
    for startStopTimeArray in periodStartStopTimeArrayList:
        try:
            startIndex = np.where(timeArray < startStopTimeArray[0])[0][-1]
        except:
            startIndex = 0
        stopIndex = np.where(timeArray < startStopTimeArray[1])[0][-1]
        
        tempDataArray = np.copy(dataArray[startIndex:stopIndex])
        tempTimeArray = np.copy(timeArray[startIndex:stopIndex])
        
        timeArrayList.append(tempTimeArray)
        dataArrayList.append(tempDataArray)
        
    if(compensateAverage == True):
        for i in range(len(dataArrayList)):
            dataArrayList[i] = dataArrayList[i] - np.average(dataArrayList[i]) 
        
    
    return timeArrayList, dataArrayList

def locate_period_start_indices(eFieldDataArray=np.array([])):
    periodStartIndexArray = np.array([])
    
    positiveSignIndexArray = np.where(eFieldDataArray < 0)[0]
    tempIndexArray = np.where(np.diff(positiveSignIndexArray)>1)[0]
    
    periodStartIndexArray = positiveSignIndexArray[tempIndexArray]
    
    
    return periodStartIndexArray

def differentiate_signal(dataArray=np.array([]),timeArray=np.array([])):
    derivativeDataArray = np.array([])
    derivativeTimeArray = np.array([])
    
    
    derivativeDataArray = np.diff(dataArray)/np.diff(timeArray)
    
    timeStepArray = np.diff(timeArray)
    timeStepArray = timeStepArray/2
    
    derivativeTimeArray = timeStepArray + timeArray[:-1]
    
    
    return derivativeDataArray, derivativeTimeArray

def scale_to_dimensions(frameSumWidthCentroidArray=np.array([]),frameSumHeightCentroidArray=np.array([]),pitchX=0.4e-6,pitchY=0.4e-6):
    
    widthPositionArray = frameSumWidthCentroidArray*pitchX
    heightPositionArray = frameSumHeightCentroidArray*pitchY
    
    return widthPositionArray, heightPositionArray

def scale_eField_data_to_eField_strength(eFieldDataArray=np.array([]),eFieldAmp=10e3,electrodePolarity="Negative"):
    electrodePolarity = electrodePolarity.lower()
    polarityFactor = 1.0
    if(electrodePolarity == "negative"):
        polarityFactor = -1.0
        
    eFieldStrengthDataArray = polarityFactor*(eFieldAmp/max(eFieldDataArray))*eFieldDataArray
    
    return eFieldStrengthDataArray