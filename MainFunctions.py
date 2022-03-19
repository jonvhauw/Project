import numpy as np
import TDMS as tdms                             #test
import TDMSDataProcessing as tdmsData
import TDMSPlotTraces as tdmsPlot
import TDMSAnimateTraces as tdmsAnimate
import TDMSDataAnalysis as tdmsAnalysis
import TDMSEKModel as tdmsEKModel
import TDMSSaveData as tdmsSave
import time

class Data():

    comsolFieldFactor =  (23e3)*(6.5e-3)/10 # Conversion factor based on comsol simulation V/m/m/V
    electrodeSpacing = 6.5e-3 # Spacing between electrodes in m
    AODSpacialFactor = 8.2e-6/10  # AOD voltage to distance in focal plane m/V
    FPGAClockPeriod = 25e-9
    electrodePolarity = "Negative"  # Positive voltage means E-Field is in the opposite direction of positive displacement

    eFieldAmp = 0.0
    eFieldFreq = 0.0
    pitchX = 0.0
    pitchY = 0.0
    binSize = 0
    dotsPerLine = 0
    numberOfLines = 0

    scanPattern = "S-shape"

    def __init__(self, pixelNumberArray=np.array([]), AODLoopTicksArray=np.array([]), SPCMDataArray=np.array([]), 
                    SPCMLoopTicksArray=np.array([]), eFieldDataArray=np.array([]), eFieldLoopTicksArray=np.array([]), 
                    tdmsPathList="", tdmsFolderPath="", experimentName=""):
        self.pixelNumberArray = pixelNumberArray
        self.AODLoopTicksArray = AODLoopTicksArray
        self.SPCMDataArray = SPCMDataArray
        self.SPCMLoopTicksArray = SPCMLoopTicksArray
        self.eFieldDataArray = eFieldDataArray
        self.eFieldLoopTicksArray = eFieldLoopTicksArray

        self.AOD1DataArray = np.array([])
        self.AOD2DataArray = np.array([])
        self.AODTimeArray = np.array([])
        self.AODSyncTimeArray = np.array([])
        self.AODSyncDataArray = np.array([])

        self.SPCMTimeArray = np.array([])
        self.SPCMSyncTimeArray = np.array([])
        self.SPCMSyncDataArray = np.array([])

        self.eFieldTimeArray = np.array([])
        self.eFieldStrengthDataArray = np.array([])

        self.discontTimeArray = np.array([])
        self.discontDataArray = np.array([])

        self.tdmsPathList = tdmsPathList
        self.tdmsFolderPath = tdmsFolderPath
        self.experimentName = experimentName

    def read_raw_data_from_files(self):
        tdmsPathList,tdmsFolderPath,experimentName = tdms.get_tdms_file_path(rootPath="C:\\Users\\Lucas\\Documents\\Phd\\Experiments\\Scanning laser electrophoresis\\Experimental Data\\POC experiments")
        self.tdmsPathList = tdmsPathList
        self.tdmsFolderPath = tdmsFolderPath
        self.experimentName = experimentName

        tdmsFileList,txtDataFilePath = tdms.read_tdms_file_list(tdmsFilePathList=tdmsPathList)
        tdmsHierarchyDictList = tdms.return_tdms_hierarchy_list(tdmsFileList=tdmsFileList)
        tdmsHierarchyDict = tdms.combine_tdms_hierarchy_list(tdmsHierarchyDictList=tdmsHierarchyDictList)
        tdms.print_tdms_hierarchy(tdmsHierarchyDict)
        pixelNumberArray, AODLoopTicksArray, SPCMDataArray, SPCMLoopTicksArray, eFieldDataArray, eFieldLoopTicksArray=tdms.return_raw_arrays_from_tdms_hierarchy(tdmsHierarchyDict=tdmsHierarchyDict)
        eFieldAmp,eFieldFreq,pitchX,pitchY,binSize,dotsPerLine, numberOfLines=tdms.return_parameters_from_tdms_hierarchy(tdmsHierarchyDict=tdmsHierarchyDict,comsolFieldFactor=self.comsolFieldFactor,electrodeSpacing=self.electrodeSpacing,AODSpacialFactor=self.AODSpacialFactor)
        
        self.pixelNumberArray = np.append(self.pixelNumberArray, pixelNumberArray)
        self.AODLoopTicksArray = np.append(self.AODLoopTicksArray, AODLoopTicksArray)
        self.SPCMDataArray = np.append(self.SPCMDataArray, SPCMDataArray)
        self.SPCMLoopTicksArray = np.append(self.SPCMLoopTicksArray, SPCMLoopTicksArray)
        self.eFieldDataArray = np.append(self.eFieldDataArray, eFieldDataArray)
        self.eFieldLoopTicksArray = np.append(self.eFieldLoopTicksArray, eFieldLoopTicksArray)

        self.eFieldAmp = eFieldAmp
        self.eFieldFreq = eFieldFreq
        self.pitchX = pitchX
        self.pitchY = pitchY
        self.binSize = binSize
        self.dotsPerLine = dotsPerLine
        self.numberOfLines = numberOfLines

    def generate_time_arrays(self):
        tdmsData.windowSize = 50
        tdmsData.filterSPCM = False
        pixelNumberArray, AODTimeArray, AODSyncTimeArray, AODSyncDataArray, SPCMDataArray, SPCMTimeArray, SPCMSyncTimeArray, SPCMSyncDataArray,eFieldDataArray, eFieldTimeArray = tdmsData.return_arrays_from_tdms_hierarchy(pixelNumberArray=self.pixelNumberArray, AODLoopTicksArray=self.AODLoopTicksArray, SPCMDataArray=self.SPCMDataArray,
                                                                                                                                                                                                                         SPCMLoopTicksArray=self.SPCMLoopTicksArray, eFieldDataArray=self.eFieldDataArray, eFieldLoopTicksArray=self.eFieldLoopTicksArray,
                                                                                                                                                                                                                        FPGAClockPeriod=self.FPGAClockPeriod,tdmsFolderPath=self.tdmsFolderPath,experimentName=self.experimentName)
        self.AODTimeArray = np.append(self.AODTimeArray, AODTimeArray)
        self.AODSyncTimeArray = np.append(self.AODSyncTimeArray, AODSyncTimeArray)
        self.AODSyncDataArray = np.append(self.AODSyncDataArray, AODSyncDataArray)
        self.SPCMTimeArray = np.append(self.SPCMTimeArray, SPCMTimeArray)
        self.SPCMSyncTimeArray = np.append(self.SPCMSyncTimeArray, SPCMSyncTimeArray)
        self.SPCMSyncDataArray = np.append(self.SPCMSyncDataArray, SPCMSyncDataArray)
        self.eFieldDataArray = np.append(self.eFieldDataArray, eFieldDataArray)
        self.eFieldTimeArray = np.append(self.eFieldTimeArray, eFieldTimeArray)

        discontIndexArray = tdmsData.locate_AOD_discontinuities(pixelNumberArray=self.pixelNumberArray)
        discontTimeArray,discontDataArray = tdmsData.discont_index_to_time_and_data_array(discontIndexArray=discontIndexArray, AODTimeArray=self.AODTimeArray)
        AOD1DataArray, AOD2DataArray   = tdmsData.pixel_number_array_to_AOD_grid_index_arrays(pixelNumberArray=self.pixelNumberArray,amountOfLines=int(self.numberOfLines),pixelsPerLine=int(self.dotsPerLine),lineAxis=0,scanningPattern=self.scanPattern)
        
        self.discontTimeArray = np.append(self.discontTimeArray, discontTimeArray)
        self.discontDataArray = np.append(self.discontDataArray, discontDataArray)

        self.AOD1DataArray = np.append(self.AOD1DataArray, AOD1DataArray)
        self.AOD2DataArray = np.append(self.AOD2DataArray, AOD2DataArray)
    
    def plot_trace_segment(self, timeSegment):
        print("segmenting")
        AODTimeArray,AOD1DataArray,AOD2DataArray,pixelNumberArray,SPCMTimeArray,SPCMDataArray,eFieldTimeArray,eFieldDataArray,discontTimeArray,discontDataArray,AODSyncTimeArray,AODSyncDataArray,SPCMSyncTimeArray,SPCMSyncDataArray= tdmsData.data_to_segment(timeSegment=timeSegment,AOD1DataArray=self.AOD1DataArray,AOD2DataArray=self.AOD2DataArray,
                                                                                                                                                                                                                       AODTimeArray=self.AODTimeArray,SPCMTimeArray=self.SPCMTimeArray,SPCMDataArray=self.SPCMDataArray,
                                                                                                                                                                                                                       eFieldTimeArray=self.eFieldTimeArray,eFieldDataArray=self.eFieldDataArray,pixelNumberArray=self.pixelNumberArray,
                                                                                                                                                                                                                       discontTimeArray=self.discontTimeArray,discontDataArray=self.discontDataArray,AODSyncTimeArray=self.AODSyncTimeArray,
                                                                                                                                                                                                                       AODSyncDataArray=self.AODSyncDataArray,SPCMSyncDataArray=self.SPCMSyncDataArray,SPCMSyncTimeArray=self.SPCMSyncTimeArray)


        tdmsPlot.plot_trace2(AODTimeArray=AODTimeArray,AOD1DataArray=AOD1DataArray,AOD2DataArray=AOD2DataArray,
                      pixelNumberArray=pixelNumberArray,SPCMTimeArray=SPCMTimeArray,SPCMDataArray=SPCMDataArray,
                      eFieldTimeArray=eFieldTimeArray,eFieldDataArray=eFieldDataArray,discontTimeArray=discontTimeArray,discontDataArray=discontDataArray,AODSyncTimeArray=AODSyncTimeArray,AODSyncDataArray=AODSyncDataArray,
                      SPCMSyncDataArray=SPCMSyncDataArray,SPCMSyncTimeArray=SPCMSyncTimeArray, AOD1_c='dg', AOD1_s = 'solid', AOD2_c = 'db', AOD2_s = 'solid', Pix_c = 'lg', Pix_s='solid',
                      SPCM_c = 're', SPCM_s = 'solid', EF_c = 'bl', EF_s = 'solid', SPCM_sync_c = 'dr', SPCM_sync_s= 'dashed', AOD_sync_c = 'dg', AOD_sync_s = 'dashed', Disc_c = 'go', Disc_s = 'solid')   
    
    def generate_pictures(self, timestamp=0):
        print("start")
        #start = time.time.now()
        rollImage = False
        rollPixels = 0
        rollAxis = 0
        eFieldStrengthDataArray = tdmsAnalysis.scale_eField_data_to_eField_strength(eFieldDataArray=self.eFieldDataArray,eFieldAmp=self.eFieldAmp,electrodePolarity=self.electrodePolarity)
        self.eFieldStrengthDataArray = eFieldStrengthDataArray
        tdmsAnimate.generate_picture_from_segment(pixelNumberArray=self.pixelNumberArray,AODTimeArray=self.AODTimeArray,AOD1DataArray=self.AOD1DataArray,
                                        AOD2DataArray=self.AOD2DataArray,SPCMTimeArray=self.SPCMTimeArray,SPCMDataArray=self.SPCMDataArray,eFieldTimeArray=self.eFieldTimeArray,eFieldDataArray=eFieldStrengthDataArray,
                                        rollImage=rollImage,rollAxis=rollAxis,rollPixels=rollPixels,tdmsFolderPath=self.tdmsFolderPath,experimentName=self.experimentName, time=timestamp)
        #print(time.time.now()-start)



test = Data()
test.read_raw_data_from_files()
test.generate_time_arrays()
#test.plot_trace_segment([43.1,43.85])
test.generate_pictures(timestamp=43.15)

