import numpy as np
import scipy.signal as ss


filterCutoff = 100
filterType = 'Butter'
filterOrder = 4


# Returns the phase array of the low-pass filter transferfunction. This filter  
# is applied to the raw position signal of the tracked particle

# Input:  - sos: Array containing the second order sections (a representation of the polynomial transferfunction used by scipy)
#         - fs: Sampling frequency of particle tracking 

# Output: - normalizedFreqArray: Normalized frequency array normalized to Nyquist frequency or fs/2
#         - phaseArray: Phase response of the filter with second order section = sos 

def calc_filter_phase_offset(sos=np.array([]),fs=1000):
    w,h = ss.sosfreqz(sos,worN=int(fs/2))
    
    normalizedFreqArray = w/np.pi
    phaseArray = np.angle(h)
    
    return normalizedFreqArray, phaseArray

# Given a time array and external oscillating field frequency it will compensate
# the time shift based on the phase response of the filter and return a timearray
# with phase compensation

# Input:  - timeArray: Array containing the timestamps of all frames
#         - sos: Array containing the second order sections (a representation of the polynomial transferfunction used by scipy)
#         - fs: Sampling frequency of particle tracking
#         - eFieldFreq: Frequency of the applied external electric field

# Output: - compensatedTimeArray: Array containing the timestamps of all frames, compensated for the phase shift of the low-pass filter

def compensate_filter_phase_offset(timeArray=np.array([]),sos=np.array([]),fs=3000,eFieldFreq=100):
    compensatedTimeArray = np.array([])
    
    normalizedFreqArray, phaseArray = calc_filter_phase_offset(sos=sos,fs=fs)
    
    fNyquist = fs/2
    normalizedeFieldFreq= eFieldFreq/fNyquist
    
    
    phaseOffset = phaseArray[np.where(normalizedFreqArray < normalizedeFieldFreq)[0][-1] + 1]
    phaseOffsetTime = 1/eFieldFreq * phaseOffset/(2*np.pi)
    
    compensatedTimeArray = timeArray + phaseOffsetTime
    
    return compensatedTimeArray

# Applies a low pass filter to data array with a cut-off at filterCutoff, after filtering
# the phase shift is compensated and the outliers are compensated if compensateOutliers == True

# Input:  - timeArray: Array containing the timestamps of all frames
#         - dataArray: 
#         - eFieldFreq: Frequency of the applied external electric field
#         - compensateOutliers: Boolean to allow function to compensate outliers
#         - thresholdFactor: Threshold for compensating outliers if jump between subsequent position is tresholdFactor*averagejump => compensate outlier

# Output: - compensatedTimeArray: Array containing the timestamps of all frames, compensated for the phase shift of the low-pass filter
#         - filteredDataArray: Array containing the particle trace after low-pass filtering and possible outlier removal

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

# Returns an array with the outliers removed. Outliers are seen as jump between subsequent position is greater than tresholdFactor*averagejump => compensate outlier

# Input:  - dataArray: Array containing data where outliers need to be removed, this is usually the low-pass filtered position data of particle
#         - thresholdFactor: Threshold for compensating outliers if jump between subsequent position is tresholdFactor*averagejump => compensate outlier
#         - times: The amount of repetitions of the oulier removal, additional repetitions will gradually remove less extreme ouliers 

# Output: - dataArray: Array containing the data with outliers removed

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
    

# Splits data array into a list of arrays for every period of the eFieldDataArray

# Input:  - eFieldTimeArray: Array containing the timestamps of the applied external electric field
#         - eFieldDataArray: Array containing the applied external electric field for respective timestamp
#         - dataArray: Array containing data to be split up for every period of eFieldDataArray
#         - timeArray: Array containing respective timestamp to be split up for every period of eFieldDataArray 
#         - compensateAverage: Boolean that allows the function to subtract the average value of the period from respective period in dataArrayList 

# Output: - timeArrayList: List of timestamp arrays for every period of eFieldDataArray
#         - dataArrayList: List of data arrays for every period of eFieldDataArray

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

# Returns an array of indices where eFieldDataArray starts a new period

# Input:  - eFieldDataArray: Array containing the applied external electric field data

# Output: - periodStartIndexArray: Array containing indices in eFieldDataArray where period starts

def locate_period_start_indices(eFieldDataArray=np.array([])):
    periodStartIndexArray = np.array([])
    
    positiveSignIndexArray = np.where(eFieldDataArray < 0)[0]
    tempIndexArray = np.where(np.diff(positiveSignIndexArray)>1)[0]
    
    periodStartIndexArray = positiveSignIndexArray[tempIndexArray]
    
    
    return periodStartIndexArray

# Returns the derivative of the data and the respective timestamps

# Input:  - dataArray: Array containing data to be derivated
#         - timeArray: Array containing timestamp array of respective dataArray

# Output: - derivativeDataArray: Array containing differentiated data
#         - derivativeTimeArray: Array containing timestamps of respective differentiated data

def differentiate_signal(dataArray=np.array([]),timeArray=np.array([])):
    derivativeDataArray = np.array([])
    derivativeTimeArray = np.array([])
    
    
    derivativeDataArray = np.diff(dataArray)/np.diff(timeArray)
    
    timeStepArray = np.diff(timeArray)
    timeStepArray = timeStepArray/2
    
    derivativeTimeArray = timeStepArray + timeArray[:-1]
    
    
    return derivativeDataArray, derivativeTimeArray

# Returns scaled versions of the frameSumWidthCentroidArray and frameSumHeightCentroidArray

# Input:  - frameSumWidthCentroidArray: Array containing the centroid of particle in units of pixel number along width direction 
#         - frameSumHeightCentroidArray: Array containing the centroid of particle in units of pixel number along height direction 
#         - pitchX: distance per voltage of the AODx signal in units of m/V
#         - pitchY: distance per voltage of the AODy signal in units of m/V

# Output: - widthPositionArray: Array containing the centroid of particle in units of m along width direction 
#         - heightPositionArray: Array containing the centroid of particle in units of m along height direction 

def scale_to_dimensions(frameSumWidthCentroidArray=np.array([]),frameSumHeightCentroidArray=np.array([]),pitchX=0.4e-6,pitchY=0.4e-6):
    
    widthPositionArray = frameSumWidthCentroidArray*pitchX
    heightPositionArray = frameSumHeightCentroidArray*pitchY
    
    return widthPositionArray, heightPositionArray


# Returns scaled versions of the eFieldData Array, scaled to units of V/m

# Input:  - eFieldDataArray: Array containing raw data of applied external electric field
#         - eFieldAmp: External electric field amplitude calculated through simulation in comsol
#         - electrodePolarity: Determines the polarity of the electrodes during experiment 

# Output: - eFieldStrengthDataArray: Array containing the scaled external electric field data in units of V/m

def scale_eField_data_to_eField_strength(eFieldDataArray=np.array([]),eFieldAmp=10e3,electrodePolarity="Negative"):
    electrodePolarity = electrodePolarity.lower()
    polarityFactor = 1.0
    if(electrodePolarity == "negative"):
        polarityFactor = -1.0
        
    eFieldStrengthDataArray = polarityFactor*(eFieldAmp/max(eFieldDataArray))*eFieldDataArray
    
    return eFieldStrengthDataArray